#!/usr/local/bin/python3
# -*- coding: utf-8 -*-  
from asfs_data_definitions import code_version
code_version = code_version()

# ############################################################################################
# AUTHORS:
#
#   Michael Gallagher (CIRES/NOAA)  michael.r.gallagher@noaa.gov
#   Christopher Cox (NOAA) christopher.j.cox@noaa.gov
#
#   Many sections based on Matlab code written by O. Persson (CIRES), A. Grachev (CIRES/NOAA),
#   and C. Fairall (NOAA); We thank them for their many contributions.
#
# PURPOSE:
#
# To create a uniform data product for the three "remote flux stations" (aka ASFS') at MOSAiC
# and to document the data processing workflow. At this time, this code only uses data from
# the SD cards. This will change if we're ever receiving data via radio/iridium and fail to
# recover an SD card.
#
# This code creates three different *daily* NetCDF files from raw observations by ASFS' at
# MOSAiC. "level2" files contain derived and quality controlled data products that are
# created using data from the "level1" product for each flux station. level2 files are
# created for both 1 minute and 10 minute averages. A "turbulent" data product is also
# created, using calculations researched and by a range of NOAA team members (named above)
#
# I've tried to optimize the software as best as possible to not waste your (or my) cpu
# cycles. Function calls are parallelized/threaded when possible and this software occupies
# 4 cores most of the time it is running. But, it's entirely I/O limited and so it runs much
# faster on my NVME based laptop than it does on the rusty disked server at NOAA.
# 
# Descriptions of the three different output files and their contents:
# (look at "asfs_data_definitions.py" for detailed product description)
# #########################################################################
#
# level2 (10 and 1 minute averages): 
#
#       This is the first QCed derived science product to be used in analyses, contains
#       the basic scientific params at specified intervals.
#
# turbulent (calculated over 30 minute configurable window):
#
#       Based on Andrey Grachev's matlab code, the turbulent product includes all
#       relevant parameters created while calculatinghe fluxes, including the final results.
# 
# HOWTO:
#
# To run this package with verbose printing over all of the data:
# python3 create_level2_product_asfs.py -v -s 20191005 -e 20201005
#
# To profile the code and see what's taking so long:
# python3 -m cProfile -s cumulative ./create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201 
#
# ###############################################################################################
#
# look at these files for documentation on netcdf vars and nomenclature
# as well as additional information on the syntax used to designate certain variables here
from asfs_data_definitions import define_global_atts, define_level2_variables, define_turb_variables 
from asfs_data_definitions import define_level1_slow, define_level1_fast

import functions_library as fl # includes a bunch of helper functions that we wrote

import os, inspect, argparse, time, gc

import numpy  as np
import pandas as pd
import xarray as xr

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from threading import Thread
from queue     import Queue
from datetime  import datetime, timedelta
from numpy     import sqrt
from netCDF4   import Dataset, MFDataset, num2date

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

version_msg = '\n\nPS-122 MOSAiC Flux team ASFS processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)

def main(): # the main data crunching program

    # the date on which the first MOSAiC data was taken... there will be a "seconds_since" variable 
    global beginning_of_time, integ_time_turb_flux
    beginning_of_time    = datetime(2019,10,5,0,0) # the first day of MOSAiC ASFS data
    integ_time_turb_flux = 10                      # [minutes] the integration time for the turbulent flux calculation
    calc_fluxes          = True                   # if you want to run turbulent flux calculations and write files

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring
    global verbose       # a useable flag to allow subroutines etc when using -v 

    global data_dir, level1_dir, level2_dir, turb_dir # make data available
    data_dir   = './data/'
    level1_dir = './processed_data/level1/'  # where does level1 data go
    level2_dir = './processed_data/level2/'  # where does level2 data go
    turb_dir    = './processed_data/turb/'    # where does level2 data go

    flux_stations = ['asfs30', 'asfs40', 'asfs50'] # our beauties 
    
    # constants for calculations
    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0

    Rd       = 287     # gas constant for dry air
    K_offset = 273.15  # convert C to K
    h2o_mass = 18      # are the obvious things...
    co2_mass = 44      # ... ever obvious?

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over all the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')
    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want

    args         = parser.parse_args()
    verbose      = True if args.verbose else False # use this to run segments of code via v/verbose flag
    v_print      = print if verbose else lambda *a, **k: None     # placeholder
    verboseprint = v_print # use this function to print a line if the -v/--verbose flag is provided
    def printline(startline='',endline=''):
        print('{}--------------------------------------------------------------------------------------------{}'
              .format(startline, endline))

    global start_time, end_time
    start_time = beginning_of_time
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y%m%d')
    else:
        # make the data processing start yesterday! i.e. process only most recent full day of data
        start_time = beginning_of_time.today() # any datetime object can provide current time
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0, day=start_time.day)
    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y%m%d')
    else:
        end_time = beginning_of_time.today() # any datetime object can provide current time
        end_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0, day=start_time.day)

    printline(endline="\n")
    print('The first day of the experiment is:   %s' % beginning_of_time)
    print('The first day we process data is:     %s' % start_time)
    print('The last day we will process data is: %s' % end_time)
    printline(startline="\n")

    # thresholds! limits that can warn you about bad data!
    # these aren't used yet but should be used to warn about spurious data
    lat_thresh        = (70   ,90)   # limits area where station
    hdg_thresh_lo     = (0    ,360)  # limits on gps heading
    irt_targ_lo       = (-80  ,5)    # IRT surface brightness temperature limits [Celsius]
    sr50d             = (1    ,2.5)  # distance limits from SR50 to surface [m]; install height -1 m or +0.5
    sr50_qc           = (152  ,210)  # reported "quality numbers" 0-151=can't read dist;
                                     # 210-300=reduced signal; 300+=high uncertainty
    flxp              = (-120 ,120)  # minimum and maximum conductive heat flux (W/m2)
    T_thresh          = (-70  ,20)   # minimum & maximum air temperatures (C)
    rh_thresh         = (5    ,130)  # relative humidity (#)
    p_thresh          = (850  ,1100) # air pressure
    ws_thresh         = (0    ,40)   # wind speed from sonics (m/s)
    lic_co2sig_thresh = (85   ,100)  # rough estimate of minimum CO2 signal value corresponding to
                                     # optically-clean window. < 90 = needs cleaned (e.g., salt residue); < ~80?? = ice!
    lic_h2o           = (0    ,100)  # Licor h2o [mg/m3]
    lic_co2           = (0    ,5000) # Licor co2 [g/m3]
    max_bad_paths     = (0.01 ,1)    # METEK: maximum [fraction] of bad paths allowed. (0.01 = 1%), but is
                                     # actually in 1/9 increments. This just says we require all paths to be usable.
    incl_range        = (-90  ,90)   # The inclinometer on the metek
    sw_range          = (-4   ,1000) # SWD & SWU max [Wm^2]
    lw_range          = (50  ,400)   # LWD & LWU max [Wm^2] 
    # FYI, ~315 W/m2@ 0 C and LWD under clear skies can be as low as ~100 Wm2)
    met_t             = T_thresh     # Vaisala air temperature [C]
    met_rh            = rh_thresh    # Vaisala relative humidity [#]
    met_p             = p_thresh     # Vaisala air pressure [hPa or ~mb]

    # various calibration params
    # ###################################################################################################

    # initial distance measurement for sr50 to snow made/noted by Ola for calibration
    sr50_init_dist  = {} # dicts, with station name as key
    sr50_init_depth = {}

    # L2 distance (201.8 cm) and 2-m Tvais (-7.75 C) at 0430 UTC Oct 7, 2019 
    sr50_init_dist[flux_stations[0]]  = sqrt((-7.75+K_offset)/K_offset)*201.8
    sr50_init_depth[flux_stations[0]] = 8.3 # snow depth (cm) measured under SR50 at 0430 UTC Oct 7, 2019

    # L1 distance (214.9 cm) and 2-m Tvais (-13.9 C) at 921 UTC Oct 5, 2019
    sr50_init_dist[flux_stations[1]]  = sqrt((-13.9+K_offset)/K_offset)*214.9
    sr50_init_depth[flux_stations[1]] = 9.1 # snow depth (cm) measured under SR50 at 0921 UTC Oct 5, 2019

    # L3 distance (213.3 cm) and 2-m Tvais (-10.1 C) at 0400 UTC Oct 10, 2019
    sr50_init_dist[flux_stations[2]]  = sqrt((-10.1+K_offset)/K_offset)*213.3
    sr50_init_depth[flux_stations[2]] = 6.5 # snow depth (cm) measured under SR50 at 0400 UTC Oct 10, 2019

    # program logic starts here, the logic flow goes like this:
    # #########################################################
    # 
    #     1) read in all days of slow data from netcdf level 1 files
    #     2) loop over days requested
    #     3) for each day, pull in fast data from netcdf level 1 files
    #     5) for each day, apply strict QC and derive desired products in level2 definitions
    #     6) for each day, write level2 netcdf files
    #     7) if desired, using QCed observations, produce turbulent flux data product
    #     8) all done
    #
    # ... here we go then
    # ##########################################################################################

    print("Getting data from level1 netcdf files for stations: {}!!".format(flux_stations))
    print("   and doing it in threads, hopefully this doesn't burn your lap")
    printline()

    # getting the "slow" raw/level1 data is done here, heavy lifting is in "get_slow_data()" 
    # the slow dataset is small, so we load it all at once, the fast has to be done for each day
    # ##########################################################################################
    # dataframes are in dicts with station name keys, parallellizing data ingesting, saves time.
    slow_data   = {}
    slow_atts   = {}
    slow_vars   = {}

    slow_q_dict = {}
    slow_atts_from_definitions, slow_vars_from_definitions = define_level1_slow()
    # read *all* of the slow data... why have so much RAM if you don't use it?
    for curr_station in flux_stations:
        # try to save some time and multithread the reading
        slow_q_dict[curr_station] = Queue()
        # run the threads for retreiving data
        Thread(target=get_slow_netcdf_data, \
               args=(curr_station, start_time, end_time, \
                     slow_q_dict[curr_station])).start()
        time.sleep(.25) # give a quarter second for printing before launching next thread

    # this for loop is commented about becaus netcdf/hdf5 libs really don't like
    # running in parallel for reasons I don't understand. tried to debug in gdb but :\
    # for curr_station in  flux_stations:
        slow_data[curr_station] = slow_q_dict[curr_station].get()
        printline()
        # verboseprint("\n===================================================")
        # verboseprint("Data and observations provided by {}:".format(curr_station))
        # verboseprint('===================================================')
        # if verbose: slow_data[curr_station].info(verbose=True) # must be contained; 

    print("\n\nRetreived slow data for all stations, moving on to fast data and daily processing.\n\n")
    printline()

    # mention big data gaps, good sanity check, using battvolt, because if battery voltage is missing...
    if verbose: 
        for curr_station in  flux_stations:
            curr_slow_data = slow_data[curr_station]

            bv = curr_slow_data["batt_volt_Avg"]

            threshold   = 60 # warn if the station was down for more than 60 minutes
            nan_groups  = bv.isnull().astype(int).groupby(bv.notnull().astype(int).cumsum()).cumsum()
            mins_down   = np.sum( nan_groups > 0 )

            prev_val   = 0 
            if np.sum(nan_groups > threshold) > 0:
                perc_down = round(((bv.size-mins_down)/bv.size)*100, 3)
                print("\nFor your time range, the station was down for a total of {} minutes...".format(mins_down))
                print("... which gives an uptime of approx {}% over this period".format(perc_down))

            else:
                print("\nStation {} was alive for the entire time range you requested!! Not bad... "
                      .format(curr_station, threshold))

    # OK we have all the slow data, now loop over each day and get fast data for that
    # day and do the QC/processing you want. all calculations are done in this loop
    # ######################################################################
    day_series = pd.date_range(start_time, end_time)    # data was requested for these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    printline(startline='\n')
    print("\n We have retreived all slow data, now processing each day...\n")
    i_day = -1 
    for today in day_series: # loop over the days in the processing range and get a list of files

        gc.collect() # usual beginning of the loop cleaning
        i_day+=1
        tomorrow = today+day_delta
        printline()
        printline(endline="\n")
        print("Retreiving level1 data for {}\n".format(today))

        # #######################################################
        # get fast data from netcdf files for daily processing
        # these dictionaries hold the dataframes for todays data 
        fast_data_today = {}
        slow_data_today = {} 

        # get slow data for today only from full data frame retreived above
        for curr_station in flux_stations:
            slow_data_today[curr_station] = slow_data[curr_station][today:tomorrow]

        # queue used to write data for today
        onemin_q_dict = {} 
        tenmin_q_dict = {} 
        turb_q_dict = {} 

        # queue used to retreive data for today
        fast_q_dict = {} 

        for curr_station in flux_stations:
            # try to save some time and multithread the reading
            fast_q_dict[curr_station] = Queue()
            # run the threads for retreiving data
            Thread(target=get_fast_netcdf_data, \
                   args=(curr_station, today, \
                         fast_q_dict[curr_station])).start()
 
        # wait for results from threads and then put dataframes into list
        # for curr_station in flux_stations:
            fast_data_today[curr_station] = fast_q_dict[curr_station].get()

        # process data for each day, for each individual flux station, here's the meat and potatoes!!!
        # 
        # some variable reminders:
        #    "today" is a datetime object referencing current day being processed, from start_time to end_time
        #    "i_day" is an index iterating over these datetime objects, from start_time to end_time
        #    "curr_station" is the station we are currently analyzing
        #    "fdt/sdt" are dataframes of fast/slow data for the current station for the current day
        # ####################################################################################################
        for curr_station in flux_stations:

            fdt = fast_data_today[curr_station] # shorthand to make upcoming code clean(er)
            sdt = slow_data_today[curr_station]

            if len(fdt.index) == 0: # data warnings and sanity checks
                if len(sdt.index) == 0: 
                    print(" !!! No data available for {} on {} !!!".format(curr_station, fl.dstr(today)))
                    continue
                print("... no fast data available for {} on {}... ".format(curr_station, fl.dstr(today)))
            if len(sdt.index) == 0: print("... no slow data available for {} on {}... ".format(curr_station, fl.dstr(today)))
            printline(startline="\n")

            # now clean and QC data 'subtleties'. any and all fixing of data is done here before the day is written out
            # ########################################################################################################
            # first, we assign some variables we want to keep from level1, in level2, and essentially rename them
            # don't worry, we'll QC these down below after assigning them
            sdt['station_heading']      = sdt['gps_hdg_Avg']
            sdt['gps_alt']              = sdt['gps_alt_Avg']
            sdt['sr50_dist']            = sdt['sr50_dist_Avg']
            sdt['press_vaisala']        = sdt['vaisala_P_Avg']
            sdt['temp_vaisala']         = sdt['vaisala_T_Avg']
            sdt['rel_humidity_vaisala'] = sdt['vaisala_RH_Avg']
            sdt['body_T_IRT']           = sdt['apogee_body_T_Avg']
            sdt['surface_T_IRT']        = sdt['apogee_targ_T_Avg']
            sdt['flux_plate_A_Wm2']     = sdt['fp_A_Wm2_Avg']
            sdt['flux_plate_B_Wm2']     = sdt['fp_B_Wm2_Avg']
            sdt['H2O_licor']            = sdt['licor_h2o_Avg']
            sdt['CO2_licor']            = sdt['licor_co2_Avg']
            sdt['temp_licor']           = sdt['licor_T_Avg']
            sdt['co2_signal_licor']     = sdt['licor_co2_str_out_Avg']
            sdt['radiation_LWd']        = sdt['ir20_lwd_Wm2_Avg']
            sdt['radiation_SWd']        = sdt['sr30_swd_Irr_Avg']
            sdt['radiation_LWu']        = sdt['ir20_lwu_Wm2_Avg']
            sdt['radiation_SWu']        = sdt['sr30_swu_Irr_Avg']

            # next, the following variables are derived and defined below:
            # ###############################################################################################
            # 'station_lat','station_lon','snow_depth','MR_vaisala','abs_humidity_vaisala','enthalpy_vaisala',
            # 'pw_vaisala','RHw_vaisala','RHi_vaisala','wind_speed_metek','wind_direction_metek',
            # 'temp_metek','temp_variance_metek','radiation_net'

            print("\nQuality controlling data for {} on {}".format(curr_station, today))
            # clean up missing met data that comes in as '0' instead of NaN... good stuff
            zeros_list = ['rel_humidity_vaisala', 'press_vaisala', 'sr50_dist']
            for param in zeros_list: # make the zeros nans
                sdt[param] = np.where(sdt[param]==0.0, nan, sdt[param])

            temps_list = ['temp_vaisala', 'surface_T_IRT', 'body_T_IRT']
            for param in temps_list: # identify when T==0 is actually missing data, this takes some logic
                potential_inds  = np.where(sdt[param]==0.0)
                if potential_inds[0].size==0: continue # if empty, do nothing, this is unnecessary
                for ind in potential_inds[0]:
                    #ind = ind.item() # convert to native python type from np.int64, so we can index
                    lo = ind
                    hi = ind+5
                    T_nearby = sdt[param][lo:hi]
                    if np.any(T_nearby < -5) or np.any(T_nearby > 5):    # temps cant go from 0 to +/-5C in 5 minutes
                        sdt[param].iloc[ind] = nan
                    elif (sdt[param].iloc[lo:hi] == 0).all(): # no way all values for a minute are *exactly* 0
                        sdt[param].iloc[lo:hi] = nan


            # derive some useful parameters that we want to write to the output file
            # ###################################################################################################
            # compute RH wrt ice -- compute RHice(%) from RHw(%), Temperature(deg C), and pressure(mb)
            Td2, h2, a2, x2, Pw2, Pws2, rhi2 = fl.calc_humidity_ptu300(sdt['rel_humidity_vaisala'],\
                                                                       sdt['temp_vaisala']+K_offset,
                                                                       sdt['press_vaisala'],
                                                                       0)
            sdt['RHi_vaisala']          = rhi2
            sdt['enthalpy_vaisala']     = h2
            sdt['abs_humidity_vaisala'] = a2
            sdt['pw_vaisala']           = Pw2
            sdt['MR_vaisala']           = x2
            sdt['dewpoint_vaisala']     = Td2

            # add useful data columns, these were sprinkled throughout Ola's code, like information nuggets
            sdt['station_lat']     = sdt['gps_lat_deg_Avg']+sdt['gps_lat_min_Avg']/60.0 # add decimal values
            sdt['station_lon']     = sdt['gps_lon_deg_Avg']+sdt['gps_lon_min_Avg']/60.0
            sdt['station_heading'] = sdt['station_heading']/100.0  # convert to degrees
            sdt['gps_alt']         = sdt['gps_alt']/1000.0 # convert to meters
 
            # snow depth in cm, corrected for temperature
            sdt['sr50_dist']  = sdt['sr50_dist']*sqrt((sdt['temp_vaisala']+K_offset)/K_offset)*100
            sdt['snow_depth'] = sr50_init_dist[curr_station] - sdt['sr50_dist'] + sr50_init_depth[curr_station]

            # is up or down positive in our convention??
            sdt['radiation_net'] = (sdt['radiation_LWd']+sdt['radiation_SWd']) - (sdt['radiation_LWu']+sdt['radiation_SWu'])

            # ###################################################################################################
            flux_freq = '{}T'.format(integ_time_turb_flux)

            Hz10_today        = pd.date_range(today, tomorrow, freq='0.1S') # all the 0.1 seconds today, for obs
            seconds_today     = pd.date_range(today, tomorrow, freq='S')    # all the seconds today, for obs
            minutes_today     = pd.date_range(today, tomorrow, freq='T')    # all the minutes today, for obs
            ten_minutes_today = pd.date_range(today, tomorrow, freq='10T')  # all the 10 minutes today, for obs

            flux_time_today   = pd.date_range(today, today+timedelta(1), freq=flux_freq) # flux calc intervals

            #                              !! Important !!
            #   first resample to 10 Hz by averaging and reindexed to a continuous 10 Hz time grid (NaN at
            #   blackouts) of Lenth 60 min x 60 sec x 10 Hz = 36000 Later on (below) we will fill all missing
            #   times with the median of the (30 min?) flux sample.
            # ~~~~~~~~~~~~~~~~~~~~~ (2) Quality control ~~~~~~~~~~~~~~~~~~~~~~~~
            print("... quality controlling the fast data now")

            metek_list = ['metek_x', 'metek_y','metek_z','metek_T']
            for param in metek_list: # identify when T==0 is actually missing data, this takes some logic
                potential_inds  = np.where(fdt[param]==0.0)
                if potential_inds[0].size==0: continue # if empty, do nothing, this is unnecessary
                if potential_inds[0].size>100000:
                    print("!!! there were a lot of zeros in your fast data, this shouldn't happen often !!!")
                    print("!!! {}% of {} was zero today!!!".format(round((potential_inds[0].size/1728000)*100,4),param))
                    split_val = 10000
                else: split_val=200

                while split_val>199: 
                    ind = 0
                    while ind < len(potential_inds[0]):
                        curr_ind = potential_inds[0][ind]
                        hi = int(curr_ind+(split_val))
                        if hi >= len(fdt[param]): hi=len(fdt[param])-1
                        vals_nearby = fdt[param][curr_ind:hi]
                        if (fdt[param].iloc[curr_ind:hi] == 0).all(): # no way all values are consecutively *exactly* 0
                            fdt[param].iloc[curr_ind:hi] = nan
                            ind = ind+split_val
                            continue
                        else:
                            ind = ind+1

                    potential_inds  = np.where(fdt[param]==0.0)
                    if split_val ==10000:
                        split_val = 200
                    else:
                        split_val = split_val -1
                #print("...ended with {} zeros in the array".format(len(potential_inds[0])))

            # I'm being a bit lazy here: no accouting for reasons data was rejected. For another day.
            # Chris said he was lazy first, now I'm being lazy by not making it up, sorry Chris

            # begin with bounding the Metek data to the physically-possible limits
            fdt ['metek_T']  [fdt['metek_T'] < T_thresh[0]]   = nan
            fdt ['metek_T']  [fdt['metek_T'] > T_thresh[1]]   = nan
            fdt ['metek_x']  [np.abs(fdt['metek_x'])  > ws_thresh[1]]  = nan
            fdt ['metek_y']  [np.abs(fdt['metek_y'])  > ws_thresh[1]]  = nan
            fdt ['metek_z']  [np.abs(fdt['metek_z'])  > ws_thresh[1]]  = nan

            # Diagnostic: break up the diagnostic and search for bad paths. the diagnostic is as follows:
            # 1234567890123
            # 1000096313033
            #
            # char 1-2   = protocol stuff. 10 is actualy 010 and it says we are receiving instantaneous data from network. ignore
            # char 3-7   = data format. we use 96 = 00096
            # char 8     = heating operation mode. we set it to 3 = on but control internally for temp and data quality (ie dont operate the heater if you dont really have to)
            # char 9     = heating state, 0 = off, 1 = on, 2 = on but faulty
            # char 10    = number of unusable radial paths (max 9). we want this to be 0 and it is redundant with the next...
            # char 11-13 = percent of unusuable paths. in the example above, 3033 = 3 of 9 or 33% bad paths
            #
            # We want to strip off the last 3 digits here and remove data that are not all 0s.  To do this
            # fast I will do it by subtracting off the top sig figs like below.  The minumum value is 1/9 so
            # I will set the threhsold a little > 0 for slop in precision. We could set this higher. Perhaps 1
            # or 2 bad paths is not so bad? Not sure.
            status = fdt['metek_heatstatus']
            bad_data = (status/1000-np.floor(status/1000)) >  max_bad_paths[0]
            fdt['metek_x'][bad_data]=nan
            fdt['metek_y'][bad_data]=nan
            fdt['metek_z'][bad_data]=nan
            fdt['metek_T'][bad_data]=nan

            # And now Licor ####################################################
            #
            # Physically-possible limits, python isnt happy with ambiguous "or"s
            # im accustomed to in matlab so i split it into two lines
            fdt['licor_T'  ][fdt['licor_T']   < T_thresh[0]]    = nan 
            fdt['licor_T'  ][fdt['licor_T']   > T_thresh[1]]    = nan
            fdt['licor_pr' ][fdt['licor_pr']  < p_thresh[0]/10] = nan
            fdt['licor_pr' ][fdt['licor_pr']  > p_thresh[1]/10] = nan
            fdt['licor_h2o'][fdt['licor_h2o'] < lic_h2o[0]]     = nan
            fdt['licor_h2o'][fdt['licor_h2o'] > lic_h2o[1]]     = nan
            fdt['licor_co2'][fdt['licor_co2'] < lic_co2[0]]     = nan
            fdt['licor_co2'][fdt['licor_co2'] > lic_co2[1]]     = nan

            # CO2 signal strength is a measure of window cleanliness applicable to CO2 and H2O vars
            fdt['licor_co2'][fdt['licor_co2_str'] < lic_co2sig_thresh[0]] = nan
            fdt['licor_h2o'][fdt['licor_co2_str'] < lic_co2sig_thresh[0]] = nan
            fdt['licor_co2'][fdt['licor_co2_str'] > lic_co2sig_thresh[1]] = nan
            fdt['licor_h2o'][fdt['licor_co2_str'] > lic_co2sig_thresh[1]] = nan
                                                                            
            # The diagnostic is coded                                       
            print("... decoding Licor diagnostics. It's fast like the Dranitsyn, even vectorized. Gimme a minute...")

            pll, detector_temp, chopper_temp = fl.decode_licor_diag(fdt['licor_diag'])
            # Phase Lock Loop. Optical filter wheel rotating normally if 1, else "abnormal"
            bad_pll = pll == 0
            # If 0, detector temp has drifted too far from set point. Should yield a bad calibration, I think
            bad_dt = detector_temp == 0
            # Ditto for the chopper housing temp
            bad_ct = chopper_temp == 0
            # Get rid of diag QC failures
            fdt['licor_h2o'][bad_pll] = nan
            fdt['licor_co2'][bad_pll] = nan
            fdt['licor_h2o'][bad_dt]  = nan
            fdt['licor_co2'][bad_dt]  = nan
            fdt['licor_h2o'][bad_ct]  = nan
            fdt['licor_co2'][bad_ct]  = nan
                                  
            # Despike: meant to replace despik.m by Fairall. Works a little different tho
            #   Here screens +/-5 m/s outliers relative to a running 1 min median
            #
            #   args go like return = despike(input,oulier_threshold_in_m/s,window_length_in_n_samples)
            #
            #   !!!! Replaces failures with the median of the window !!!!
            #
            fdt['metek_x'] = fl.despike(fdt['metek_x'],5,1200)
            fdt['metek_y'] = fl.despike(fdt['metek_y'],5,1200)
            fdt['metek_z'] = fl.despike(fdt['metek_z'],5,1200)
            fdt['metek_T'] = fl.despike(fdt['metek_T'],5,1200)


            # ~~~~~~~~~~~~~~~~~~~~~~~ (3) Resample  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            print('... resampling 20 Hz -> 10 Hz.')
            #
            # 20 Hz irregular grid -> 10 Hz regular grid
            #
            # The method is to first resample the 20 Hz data to a 10 Hz regular
            # grid using the average of the (expect n=2) points at each 0.1s
            # interval. Then the result is indexed onto a complete grid for the
            # whole day, which is nominally 1 hour = 36000 samples at 10 Hz
            # Missing data (like NOAA Services blackouts) are nan
            fdt_10hz = fdt.resample('100ms').mean()
            fdt_10hz = fdt_10hz.reindex(index=Hz10_today)

            # ~~~~~~~~~~~~~~~~~ (4) Do the Tilt Rotation  ~~~~~~~~~~~~~~~~~~~~~~
            print('... cartesian tilt rotation. translating body -> earth coordinates. caveats!')
            print('... read in-line comments please! solution being developed with J. Hutchings.')

            # This really only affects the slow interpretation of the data.
            # When we do the fluxes it will be a double rotation into the streamline that
            # implicitly accounts for deviations between body and earth
            #
            # The rotation is done in subroutine tilt_rotation, which is based on code from Chris Fairall et al.
            #
            # tilt_rotation(ct_phi,ct_theta,ct_psi,ct_up,ct_vp,ct_wp)
            #             ct_phi   = inclinometer roll angle (y)
            #             ct_theta = inclinometer pitchi angle (x)
            #             ct_psi   = yaw/heading/azimuth (z)
            #             ct_up    = y(u) wind
            #             ct_vp    = x(v) wind
            #             ct_zp    = z(w) wind
            #
            # Right-hand coordinate system convention:
            #             phi     =  inclinometer y is about the u axis
            #             theta   =  inclinometer x is about the v axis
            #             psi     =  azimuth        is about the z axis. the inclinometer does not measure this despite what the manual may say (it's "aspirational").
            #             metek y -> earth u, +North
            #             metek x -> earth v, +West
            #             Have a look also at pg 21-23 of NEW_MANUAL_20190624_uSonic-3_Cage_MP_Manual for metek conventions. Pg 21 seems to have errors in the diagram?
            #
            #  !! Azimuth is from a linear interpolation of the gps heading. Two questions:
            #       (1) Were the meteks mounted such that metek north = gps north or if not, what is the offset? offset presently assumed = 0
            #       (2) We could calculate the wind direction based on the 1 Hz data, with some code like this:
            #               sdt['station_heading'].reindex(index=Hz10_today, copy=False).interpolate('linear')
            #           However, there is low-frequency variability in the heading information recevied at the gps. The period is roughly
            #           1-2 hours and the standard deviation is 1-1.5 deg. This variability is NOT movement of the ice floe! We saw this in
            #           the GPS when stationary in Boulder and it looks similar at MOSAiC. Jenny H. says it is normal and calls it "noise".
            #           Probably somehow related to the satellite constellation, though it was uncorrelated with GPS qc vars in Colorado.
            #           It is not noise in the conventional sense, but appears very systematic, which makes it something we need to
            #           take into account. In order to avoid propogating the error into the reported wind directions, we need some sort
            #           of low-pass filter having an averaging period that is shorter than significant deviations in the actual heading
            #           of the floe but at least ~3 hours.
            #               For now, I will use the DAILY AVERAGE HEADING!
            #               Working with J Hutchings to analyze the times scales of floe rotation vs the time scales of GPS HEHDT errors.
            #               Planning to develop of floe-scale hdg by using multiple GPS acroess the floe to beat down the error

            # Michael made this the average tilt for the day when converting the tower code, do we want to be more subtle?

            ct_u, ct_v, ct_w = fl.tilt_rotation(np.zeros(len(fdt_10hz))+sdt['station_heading'].mean(),\
                                                np.zeros(len(fdt_10hz))+sdt['station_heading'].mean(),\
                                                np.zeros(len(fdt_10hz))+sdt['station_heading'].mean(),\
                                                fdt_10hz['metek_y'], fdt_10hz['metek_x'], fdt_10hz['metek_z'])

            fdt_10hz['metek_x'] = ct_v # x -> v on uSonic!
            fdt_10hz['metek_y'] = ct_u # y -> u on uSonic!
            fdt_10hz['metek_z'] = ct_w

            # start referring to xyz as uvw now
            fdt_10hz.rename(columns={'metek_x':'metek_u'}, inplace=True)
            fdt_10hz.rename(columns={'metek_y':'metek_v'}, inplace=True)
            fdt_10hz.rename(columns={'metek_z':'metek_w'}, inplace=True)

            # !!
            # Now we recalculate the 1 min average wind direction and speed from the u and v velocities.
            # These values differ from the stats calcs (*_ws and *_wd) in two ways:
            #   (1) The underlying data has been quality controlled
            #   (2) We have rotated that sonic y,x,z into earth u,v,w
            #
            # I have modified the netCDF build to use *_ws_corr and *_wd_corr but have not removed the
            # original calculation because I think it is a nice opportunity for a sanity check. 
            print('... calculating a corrected set of slow wind speed and direction.')

            u_min = fdt_10hz['metek_u'].resample('1T',label='left').apply(fl.take_average)
            v_min = fdt_10hz['metek_v'].resample('1T',label='left').apply(fl.take_average)
            bottom_ws_corr, bottom_wd_corr = fl.calculate_metek_ws_wd(u_min.index, u_min, v_min, sdt['station_heading']*0) 
            # !! we are already in earth coordinates, so hdg = 0!

            # ~~~~~~~~~~~~~~~~~~ (5) Recalculate Stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # !!  Sorry... This is a little messed up. The original stats are read from the NOAA Services stats
            # files, contents calculated from the raw data. But we have QC'd the data and changed the raw
            # values, so we need to update the stats. I do that here. But then was there ever any point in
            # reading the stats data in the first place?
            print('... recalculating NOAA Services style stats with corrected, rotated, and QCed values.')

            sdt['wind_speed_metek']     = bottom_ws_corr
            sdt['wind_direction_metek'] = bottom_wd_corr
            sdt['temp_variance_metek']  = fdt_10hz['metek_T'].resample('1T',label='left').var()
            sdt['temp_metek']           = fdt_10hz['metek_T'].resample('1T',label='left').mean()

            ## is there any reason to recalculate these licor averages or save the uvw components?
            # sdt['H2O_licor']            = fdt_10hz['h2o'].resample('1T',label='left').mean()
            # sdt['CO2_licor']            = fdt_10hz['co2'].resample('1T',label='left').mean()
            # sdt['temp_licor']           = fdt_10hz['T'].resample('1T',label='left').mean()
            # sdt['pr_licor']             = fdt_10hz['pr'].resample('1T',label='left').mean()*10 # [to hPa]
            # sdt['co2_signal_licor']     = fdt_10hz['co2_str'].resample('1T',label='left').mean()
            # sdt['u_metek']              = fdt_10hz['u'].resample('1T',label='left').mean()
            # sdt['v_metek']              = fdt_10hz['v'].resample('1T',label='left').mean()
            # sdt['w_metek']              = fdt_10hz['w'].resample('1T',label='left').mean()
            # sdt['stddev_u_metek']       = fdt_10hz['u'].resample('1T',label='left').std()
            # sdt['stddev_v_metek']       = fdt_10hz['v'].resample('1T',label='left').std()
            # sdt['stddev_w_metek']       = fdt_10hz['w'].resample('1T',label='left').std()
            # sdt['stddev_T_metek']       = fdt_10hz['T'].resample('1T',label='left').std()

            # ~~~~~~~~~~~~~~~~~~~~ (6) Flux Capacitor  ~~~~~~~~~~~~~~~~~~~~~~~~~
            if calc_fluxes == True:
                verboseprint('\nCalculating turbulent fluxes and associated MO parameters.')
                verboseprint('... turbulent flux code not yet set up for Licor and CLASP :(')

                # Rotation to the streamline, FFT window segmentation, detrending,
                # hamming, and computation of power [welch] & cross spectral densities,
                # covariances and associated diagnostics and plots, as well as derived
                # variables (fluxes and stress parameters) are performed within a
                # sub-function called below.
                #
                # turbulence_data = grachev_fluxcapacitor(z_level_nominal,z_level_n,sonic_dir,metek,licor,clasp)
                #       z_level_nominal = nomoinal height nomenclature as a string: '2m', '6m', '10m', or 'mast' so that
                #       we can reference unique column names later
                #       
                #       z_level_n = Height of measurements in m, being precise because it affects the calculation
                #       sonic_dir = Orientation (azimuth) of the sonic anemoneter relative to true North
                #       flux_time_today = a DatetimeIndex defined earlier and based on integ_time_turb_flux, the integration
                #       window for the calculations that is defined at the top of the code
                #       
                #       metek = the metek DataFrame
                #       licor = the licor DataFrame - currently unused until we get that coded up
                #       clasp = the clasp data frame - currently unused until we get that coded up
                #
                metek_10hz = fdt_10hz[['metek_u', 'metek_v', 'metek_w','metek_T']].copy()
                metek_10hz.rename(columns={\
                                           'metek_u':'u',
                                           'metek_v':'v',
                                           'metek_w':'w',
                                           'metek_T':'T'}, inplace=True)
                print(fdt)
                print(fdt_10hz)
                print(metek_10hz)
                for time_i in range(0,len(flux_time_today)-1): # flux_time_today = a DatetimeIndex defined earlier and based on integ_time_turb_flux, the integration window for the calculations that is defined at the top  of the code

                    if time_i % 12 == 0:
                        verboseprint('... processing turbulence data '+np.str(flux_time_today[time_i])+' to '+np.str(flux_time_today[time_i+1]))

                    # Get the index, ind, of the metek frame that pertains to the present calculation This
                    # statement cannot be evaluated with the "and", only one side or the other. wtf?  i =
                    # metek_10hz.index >= flux_time_today[time_i] and metek_10hz.index <
                    # flux_time_today[time_i+1] so we have to split it up in this wacky way
                    ind = metek_10hz.index >= flux_time_today[time_i]
                    ind[metek_10hz.index > flux_time_today[time_i+1]] = False
                    print(ind)
                    print(metek_10hz)
                    # !! heading...is this meant to be oriented with the sonic North? like, does this
                    # equal "sonic north"?  
                    hdg = sdt['station_heading'].mean()

                    # make th1e turbulent flux calculations via Grachev module
                    v = False
                    if verbose: v = True;
                    sonic_z       = 2.50 # what is sonic_z for the flux stations

                    data = fl.grachev_fluxcapacitor(sonic_z, hdg, metek_10hz[ind], [], [], verbose=v)

                    # doubtless there is a better way to initialize this
                    if time_i == 0: turbulencetom = data
                    else: turbulencetom = turbulencetom.append(data)

                # now add the indexer datetime doohicky
                turbulencetom.index = flux_time_today[0:-1] 

                turb_cols = turbulencetom.keys()

            else:
                turb_cols = []

            print('\nOutputting to netcdf files and calcuating averages for day: {}'.format(today))
            onemin_q_dict[curr_station] = Queue()
            Thread(target=write_level2_netcdf, \
                   args=(sdt.copy(), curr_station, today, \
                         "1min", \
                         onemin_q_dict[curr_station])).start()
 
            # wait for results from threads and then put dataframes into list
            # for curr_station in flux_stations:
            trash_var = onemin_q_dict[curr_station].get()

            tenmin_q_dict[curr_station] = Queue()
            Thread(target=write_level2_netcdf, \
                   args=(sdt.copy(), curr_station, today,\
                         "10min", \
                         tenmin_q_dict[curr_station])).start()

            trash_var = tenmin_q_dict[curr_station].get()

            turb_q_dict[curr_station] = Queue()
            Thread(target=write_turb_netcdf, \
                   args=(turbulencetom.copy(), curr_station, today,\
                         turb_q_dict[curr_station])).start()

            trash_var = turb_q_dict[curr_station].get()

    printline()
    print("All done! Go check out your freshly baked files")
    print(version_msg)
    printline()

# loop over all slow files in time range and return data from for full range of days
def get_slow_netcdf_data(curr_station, start_time, end_time, q): 
    l_site_names = { "asfs30" : "L2", "asfs40" : "L1", "asfs50" : "L3"}

    data_atts, data_cols = define_level1_slow()
    time_var = 'time'

    in_dir = level1_dir+curr_station+"/" # point this program to your data

    day_series = pd.date_range(start_time, end_time) # get data for these days
    file_list  = [] 
    missing_days = [] 
    for today in day_series: # loop over the days in the processing range and get a list of files
        file_str = '{}/slow_preliminary_{}.{}.{}.nc'.format(in_dir,
                                                            curr_station,
                                                            l_site_names[curr_station],
                                                            today.strftime('%Y%m%d'))
        if os.path.isfile(file_str): 
            file_list.append(file_str) 
            #print(' FOUND IT {} !!!'.format(file_str))
        else:
            missing_days.append(today.strftime('%m-%d-%Y'))
            continue
    if len(missing_days)==0: print("... pulling in {} slow data, there were zero missing days of data".format(curr_station))
    else: print("... pulling in {} slow data, it was missing days:".format(curr_station))

    for i, day in enumerate(missing_days): 
        if i%5 == 0: print("\n  ---> ", end =" ")
        if i==len(missing_days)-1: 
            print("{}\n".format(day))
            break
        print("{},  ".format(day), end =" ")

    print("... compiling all days of {} slow level1 data into single dataframe, takes a second".format(curr_station))
    df_list = [] # dataframe
    # this became a for loop because "xr.open_mfdataset" has performance/memory issues when
    # compiling large numbers of files across coordinates into one dataframe, see this discussion:
    # https://github.com/pydata/xarray/issues/1385
    for data_file in file_list:
        xarr_ds = xr.open_dataset(data_file)
        df      = xarr_ds.to_dataframe()
        df_list.append(df)
    data_frame = pd.concat(df_list)
    del df_list
    gc.collect()
    q.put(data_frame)

# get level1 fast data from netcdf for specified day (each day eats RAM)
def get_fast_netcdf_data(curr_station, date, q): 
    l_site_names = { "asfs30" : "L2", "asfs40" : "L1", "asfs50" : "L3"}
    data_atts, data_cols = define_level1_fast()
    time_var = data_cols[0]

    file_dir = level1_dir+curr_station+"/"
    file_name = 'fast_preliminary_{}.{}.{}.nc'.format(curr_station,
                                                      l_site_names[curr_station],
                                                      date.strftime('%Y%m%d'))
    file_str = '{}/{}'.format(file_dir,file_name)

    if not os.path.isfile(file_str): 
        print('... no fast data for {} on {}, file {} not found !!!'.format(curr_station, date, file_name))
        nan_row   = np.ndarray((1,len(data_cols)))*nan
        nan_frame = pd.DataFrame(nan_row, columns=data_cols, index=pd.DatetimeIndex([date]))
        q.put(nan_frame)
        return 

    print("... converting {} level1 fast data to dataframe, takes a second".format(curr_station))
    # sometimes xarray throws exceptions on first try, had no time to debug it yet:

    try:
        xarr_ds = xr.open_dataset(file_str)
    except Exception as e:
        print("!!! xarray exception: {}".format(e))
        print("!!! file: {}".format(file_str))
        print("!!! this means there was no data in this file^^^^")
        nan_row   = np.ndarray((1,len(data_cols)))*nan
        nan_frame = pd.DataFrame(nan_row, columns=data_cols, index=pd.DatetimeIndex([date]))
        q.put(nan_frame)
        return
    
    data_frame = xarr_ds.to_dataframe()
    n_entries = len(data_frame)
    verboseprint("... {}/1728000 fast entries on {} for {}, representing {}% data coverage"
                 .format(n_entries, date, curr_station, round((n_entries/1728000)*100.,2)))

    #return data_frame
    q.put(data_frame)

# do the stuff to write out the level1 files, set timestep equal to anything from "1min" to "XXmin"
# and we will average the native 1min data to that timestep. right now we are writing 1 and 10min files
def write_level2_netcdf(l2_data, curr_station, date, timestep, q):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    l_site_names = { "asfs30" : "L2", "asfs40" : "L1", "asfs50" : "L3"}
    l2_atts, l2_cols = define_level2_variables()

    all_missing     = True 
    first_loop      = True
    n_missing_denom = 0

    if l2_data.empty:
        print("... there was no data to write today {} for {} at station {}".format(date,timestep,curr_station))
        print(l2_data)
        q.put(False)
        return

    # get some useful missing data information for today and print it for the user
    for var_name, var_atts in l2_atts.items():
        try: dt = l2_data[var_name].dtype
        except KeyError as e: 
            print(" !!! no {} in data for {} ... does this make sense??".format(var_name, curr_station))
        perc_miss = fl.perc_missing(l2_data[var_name].values)
        if perc_miss < 100: all_missing = False
        if first_loop: 
            avg_missing = perc_miss
            first_loop=False
        elif perc_miss < 100: 
            avg_missing = avg_missing + perc_miss
            n_missing_denom += 1
    if n_missing_denom > 1: avg_missing = round(avg_missing/n_missing_denom,2)
    else: avg_missing = 100.

    print("... writing {} level2 for {} on {}, ~{}% of data is present".format(timestep, curr_station, date, 100-avg_missing))

    out_dir  = level2_dir+curr_station+"/"
    file_str = '/level2_preliminary_{}_{}.{}.{}.nc'.format(timestep,curr_station,
                                                           l_site_names[curr_station],
                                                           date.strftime('%Y%m%d'))

    lev2_name  = '{}/{}'.format(out_dir, file_str)

    global_atts = define_global_atts(curr_station, "level2") # global atts for level 1 and level 2
    netcdf_lev2 = Dataset(lev2_name, 'w', format='NETCDF4_CLASSIC')

    for att_name, att_val in global_atts.items(): # write global attributes 
        netcdf_lev2.setncattr(att_name, att_val)
        
    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_lev2.createDimension('time', None)

    time_atts   = {'units'     : 'seconds since {}'.format(beginning_of_time),
                   'delta_t'   : '0000-00-00 00:01:00',
                   'long_name' : 'seconds since the first day of MOSAiC',
                   'calendar'  : 'standard',}

    bot = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files

    # create the arrays that are integer intervals from  'time since beginning of mosaic' for indexing netcdf files
    bot = np.datetime64(beginning_of_time)
    dti = pd.DatetimeIndex(l2_data.index.values)
    fstr = '{}T'.format(timestep.rstrip("min"))
    if timestep != "1min":
        dti = pd.date_range(date, tomorrow, freq=fstr)
    delta_ints = np.floor((dti - bot).total_seconds()) # seconds

    t_ind = pd.Int64Index(delta_ints)

    # set the time dimension and variable attributes to what's defined above
    t = netcdf_lev2.createVariable('time', 'i','time') # seconds since
    t[:] = t_ind.values

    for att_name, att_val in time_atts.items(): netcdf_lev2['time'].setncattr(att_name,att_val)

    for var_name, var_atts in l2_atts.items():

        var_dtype = l2_data[var_name].dtype
        perc_miss = fl.perc_missing(l2_data[var_name])

        if fl.column_is_ints(l2_data[var_name]):
            var_dtype = np.int32
            fill_val  = def_fill_int
            l2_data[var_name].fillna(fill_val, inplace=True)
            var_tmp = l2_data[var_name].values.astype(np.int32)
        else:
            fill_val  = def_fill_flt
            l2_data[var_name].fillna(fill_val, inplace=True)
            var_tmp = l2_data[var_name].values.astype(np.int32)

        var  = netcdf_lev2.createVariable(var_name, var_dtype, 'time')
        # write atts to the var now
        for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name].setncattr(att_name, att_desc)
        netcdf_lev2[var_name].setncattr('missing_value', fill_val)

        if timestep != "1min":
            vtmp = l2_data[var_name].resample(fstr, label='left').apply(fl.take_average)
        else: vtmp = l2_data[var_name]
        var[:] = vtmp.values

        # add a percent_missing attribute to give a first look at "data quality"
        netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)

    netcdf_lev2.close() # close and write files for today
    q.put(True)

# do the stuff to write out the level1 files, set timestep equal to anything from "1min" to "XXmin"
# and we will average the native 1min data to that timestep. right now we are writing 1 and 10min files
def write_turb_netcdf(turb_data, curr_station, date, q):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    l_site_names = { "asfs30" : "L2", "asfs40" : "L1", "asfs50" : "L3"}
    turb_atts, turb_cols = define_turb_variables()

    if turb_data.empty:
        print("... there was no turbulence data to write today {} at station {}".format(date,curr_station))
        q.put(False)
        return

    # get some useful missing data information for today and print it for the user
    if not turb_data.empty: avg_missing = (1-turb_data.iloc[:,0].notnull().count()/len(turb_data.iloc[:,1]))*100.
    #fl.perc_missing(turb_data.iloc[:,0].values)
    else: avg_missing = 100.

    print("... writing turbulence data for {} on {}, ~{}% of data is present".format(curr_station, date, 100-avg_missing))

    out_dir  = turb_dir+curr_station+"/"
    file_str = '/turb_preliminary_{}min_{}.{}.{}.nc'.format(integ_time_turb_flux,curr_station,
                                                            l_site_names[curr_station],
                                                            date.strftime('%Y%m%d'))

    turb_name  = '{}/{}'.format(out_dir, file_str)

    global_atts = define_global_atts(curr_station, "turb") # global atts for level 1 and level 2
    netcdf_turb = Dataset(turb_name, 'w', format='NETCDF4_CLASSIC')
    # output netcdf4_classic files, for backwards compatibility... can be changed later but has some useful
    # features when using the data with 'vintage' processing code. it's the netcdf3 api, wrapped in hdf5


    # !! sorry, i have a different set of globals for this file so it isnt in the file list
    for att_name, att_val in global_atts.items(): netcdf_turb.setncattr(att_name, att_val) 
    n_turb_in_day = np.int(24*60/integ_time_turb_flux)

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_turb.createDimension('time', None)# n_turb_in_day)    

    time_atts_turb = {'units'     : 'seconds since {}'.format(beginning_of_time),
                      'delta_t'   : '0000-00-00 00:00:01',
                      'long_name' : 'seconds since the first day of MOSAiC',
                      'calendar'  : 'standard',}
    # this is a bit klugy
    time_atts_turb['delta_t']   = '0000-00-00 '+np.str(pd.Timedelta(integ_time_turb_flux,'m')).split(sep=' ')[2] 

    bot = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files
    times_turb = np.floor(((pd.date_range(date, tomorrow, freq=np.str(integ_time_turb_flux)+'T') - bot).total_seconds()))

    # fix problems with flt rounding errors for high temporal resolution (occasional errant 0.00000001)
    times_turb = pd.Int64Index(times_turb)

    # set the time dimension and variable attributes to what's defined above
    t    = netcdf_turb.createVariable('time', 'i','time') # seconds since
    t[:] = times_turb.values
    for att_name, att_val in time_atts_turb.items() : netcdf_turb['time'].setncattr(att_name,att_val)

    # loop over all the data_out variables and save them to the netcdf along with their atts, etc
    for var_name, var_atts in turb_atts.items():
         
        if turb_data[var_name].dtype == object: # happens when all fast data is missing...
            turb_data[var_name] = np.float64(turb_data[var_name])

        # create variable, # dtype inferred from data file via pandas
        var_dtype = turb_data[var_name].dtype
        var_turb  = netcdf_turb.createVariable(var_name, var_dtype, 'time')

        turb_data[var_name].fillna(def_fill_flt, inplace=True)

        # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data)
        var_turb[:] = turb_data[var_name].values

        # add variable descriptions from above to each file
        for att_name, att_desc in var_atts.items(): netcdf_turb[var_name] .setncattr(att_name, att_desc)

        # add a percent_missing attribute to give a first look at "data quality"
        perc_miss = fl.perc_missing(var_turb)
        max_val = np.nanmax(var_turb) # masked array max/min/etc
        min_val = np.nanmin(var_turb)
        avg_val = np.nanmean(var_turb)
        netcdf_turb[var_name].setncattr('max_val', max_val)
        netcdf_turb[var_name].setncattr('min_val', min_val)
        netcdf_turb[var_name].setncattr('avg_val', avg_val)
        netcdf_turb[var_name].setncattr('percent_missing', perc_miss)
        netcdf_turb[var_name].setncattr('missing_value', def_fill_flt)

    netcdf_turb.close() # close and write files for today
    q.put(True)
    
# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
