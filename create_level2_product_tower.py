#!/usr/local/bin/python3
# -*- coding: utf-8 -*-   
from tower_data_definitions import code_version
code_version = code_version()

# ######################################################################################################
# AUTHORS:
#
#   Michael Gallagher (CIRES/NOAA)  michael.r.gallagher@noaa.gov
#   Christopher Cox (NOAA) christopher.j.cox@noaa.gov
#
#   Many sections based on Matlab code written by O. Persson (CIRES), A. Grachev (CIRES/NOAA), and
#   C. Fairall (NOAA); We thank them for their many contributions.
#
# PURPOSE:
#
# Takes in various MOSAiC data files and outputs a sane NetCDF file that is usable by
# all... should save duplication of effort on the part of multiple scientists and ensure that
# we don't waste time getting to the science. Here raw data files are cleaned up and packaged
# nicely, some new parameters are calculated. This work follows on Ola's first looks at MOSAiC
# observations. This code aims to be clear. If something is unclear, please talk to us about it 
#
# Right now, the read routines for the 20hz fast data (licor/sonic) are written... but the
# data processing component is not... this is the next thing on the list.
#
# HOWTO:
#
# To run this package with verbose printing over the data from Dec 1st:
# python3 create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201
#
# To profile the code and see what's taking so long:
# python -m cProfile -s cumulative ./create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201 -f
#
# RELEASE-NOTES:
#
# Please look at CHANGELOG-tower.md for notes on changes/improvements with each version.
#
# ######################################################################################################

from tower_data_definitions import define_global_atts, define_level2_variables, define_turb_variables 
from tower_data_definitions import define_level1_slow, define_level1_fast

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
from netCDF4   import Dataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

# just in case... avoids some netcdf nonsense involving the default file locking across mounts
os.environ['HDF5_USE_FILE_LOCKING']='FALSE' # just in case

# some mobility details to do this from the linux trio
import sys
trio_lib_path =  /psd3data/arctic/MOSAiC/python_libs/'
if path.exists(trio_lib_path):
    sys.path.insert(0,trio_lib_path)
else: computing_on_trio=False # placeholder
import xarray as xr
print(xr.__file__) # should show it was picked up from trio_lib_path

version_msg = '\n\nPS-122 MOSAiC Met Tower processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

def main(): # the main data crunching program

    # the date on which the first MOSAiC data was taken... there will be a "seconds_since" variable 
    global beginning_of_time, integ_time_turb_flux
    beginning_of_time    = datetime(2019,10,15,0,0) # the first day of MOSAiC tower data
    integ_time_turb_flux = 30 # [minutes] the integration time for the turbulent flux calculation

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring

    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0

    # constants for calculations
    Rd       = 287     # gas constant for dry air
    K_offset = 273.15  # convert C to K
    h2o_mass = 18      # are the obvious things...
    co2_mass = 44      # ... ever obvious?

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over all the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')

    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')
    
    # pass the base path to make it more mobile
    parser.add_argument('-p', '--path', metavar='str', help='base path to data up to, including /data/, include trailing slash')


    args         = parser.parse_args()
    v_print      = print if args.verbose else lambda *a, **k: None
    verboseprint = v_print
    
    # paths
    global data_dir, level1_dir, level2_dir, turb_dir # make data available
    data_dir   = args.path #'/Volumes/RESOLUTE/data/' #'/data/'
    level1_dir = data_dir+'MOSAiC/tower/1_level_ingest/'  # where does level1 data go
    level2_dir = data_dir+'MOSAiC/tower/2_level_product/' # where does level2 data go
    turb_dir   = data_dir+'MOSAiC/tower/2_level_product/' # where does level2 data go
    ais_dir    = data_dir+'MOSAiC_dump/ais/'              # this is where ais data lives
    
    def printline(startline='',endline=''):
        print('{}--------------------------------------------------------------------------------------------{}'
              .format(startline, endline))

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

    print('The first day of the experiment is:    %s' % beginning_of_time)
    print('The first day we  process data is:     %s' % start_time)
    print('The last day we will process data is:  %s' % end_time)
    printline()

    # thresholds! limits that can warn you about bad data!
    # these aren't used yet but should be used to warn about spurious data
    irt_targ          = (-80  ,5)    # IRT surface brightness temperature limits [Celsius]
    sr50d             = (1    ,2.5)  # distance limits from SR50 to surface [m]; install height -1 m or +0.5
    flxp              = (-120 ,120)  # minimum and maximum conductive heat flux (W/m2)
    T_thresh          = (-70  ,20)   # minimum & maximum air temperatures (C)
    rh_thresh         = (5    ,130)  # relative humidity (#)
    p_thresh          = (850  ,1100) # air pressure
    ws_thresh         = (0    ,40)   # wind speed from sonics (m/s)
    lic_co2sig_thresh = (94   ,100)  # rough estimate of minimum CO2 signal value corresponding to optically-clean window
    lic_h2o           = (0    ,500)  # Licor h2o [mol/m3]
    lic_co2           = (0    ,25)   # Licor co2 [mmol/m3]
    max_bad_paths     = (0.01 ,1)    # METEK: maximum [fraction] of bad paths allowed. (0.01 = 1%), but is
                                     # actually in 1/9 increments. This just says we require all paths to be usable.
    incl_range        = (-90  ,90)   # The inclinometer on the metek

    # various calibration params
    # ##########################
    # initial distance measurement for sr50 to snow (187.9cm) corrected
    # by 2-m Tvais (-25.7 C) at 0430 UTC Oct 27, 2019
    sr50_init_dist  = sqrt((-25.7+K_offset)/K_offset)*187.9
    sr50_init_depth = 2.3 #snow depth (cm) measured under SR50 at 0430 UTC Oct 27, 2019

    # the following is currently N/A, we don't have the ARM data yet to read in
    #sr30      = (-4,1000) # SWD & SWU [Wm^2]
    #ir20      = (50,400)  # LWD & LWU [Wm^2] (FYI, 315 W/m2 ~ 0 C)
    #ir20_case = (-80,10)  # IR20 instrument case temperature [C]

    # from Ola's original code... these are events that are important/relevant to data processing
    # here they are stored as a list of tuple pairs, (date, event_description)...
    # ... I would like to do this in a more clever way but haven't had the time to get to it
    raise_day = datetime(2019,10,25,5,30) # used elsewhere
    events = []
    events.append( (datetime(2019,10,22,1,0),   'move WXT away from lowest boom') )
    events.append( (datetime(2019,10,22,5,0),   'replace 2m sonic w spare (S/N 7255)') )
    events.append( (datetime(2019,10,24,1,0),   'rotate & calibrate GPS') )
    events.append( (datetime(2019,10,25,1,25),  'put in second flux plate - under Apogee') )
    events.append( (raise_day,                  'raised met tower; sonics N oriented to GPS N') )
    events.append( (datetime(2019,10,26,1,0),   'move WXT to mast') )
    events.append( (datetime(2019,10,26,8,0),   '30-m mast raised') )
    events.append( (datetime(2019,10,29,0,47),  'adjusted orientation of 2-m sonic slightly clockwise') )
    events.append( (datetime(2019,11,1,5,20),   'lowered Licor from 6 m to 2 m') )

    # these are important instrument parameters stored as a list of tuple pairs, (datetime, param_value)
    # #################################################################################################
    # tower instrument heights before tower was raised-estimates, i.e. while laying down... why keep?
    sonic_height_on_ground      = [(1.15,1.25,1.3)] # height from tower base plate (m)
    vasaila_T_height_on_ground  = [(1.05,1.2,1.25)] # height from tower base plate (m)
    vasaila_Rh_height_on_ground = [(1.05,1.2,1.25)] # height from tower base plate (m)
    vasaila_P_height_on_ground  = [(1.2)]
    GPS_height_on_ground        = [(1)]
    SR50_height_on_ground       = [(1)]

    # instrument heights after tower raised
    date_twr_raised = datetime(2019, 10, 24, 5, 30)

    sonic_height_raised      = [(2.66, 5.68, 10.54)] # height from tower base plate (m)
    vasaila_T_height_raised  = [(1.65, 5.44, 9.34)]  # height from tower base plate (m)
    vasaila_Rh_height_raised = [(1.45, 5.24, 9.14)]  # height from tower base plate (m)
    vasaila_P_height_raised  = [(1.65)]
    GPS_height_raised        = [(2)]
    SR50_height_raised       = [(2)]
    
    # Some other dates
    fpA_bury_date = datetime(2019,10,24,5,48) 
    fpB_bury_date = datetime(2019,10,25,1,35) 

    # these are the parameters associated with these dates, also stored in a list of tuples
    mast_params = {}
    mast_dates  = []
    mast_index  = 0
    mast_params['mast_hdg'] = []
    mast_params['gps_hdg_mast_setup'] = []
    mast_params['mast_sonic_heights'] = []

    # mast sonic transitions, dates/times, & heights:
    mast_dates.append(datetime(2019,10,19,5,49))  # 1) sonic on tripod
    mast_dates.append(datetime(2019,10,26,7,0))   # 2) raising mast to 30 m
    mast_dates.append(datetime(2019,11,18,12,50)) # 3) mast collapse
    mast_dates.append(datetime(2019,11,28,4,30))  # 4) sonic on stand close to 2-m tower sonic
    mast_dates.append(datetime(2019,12,1,9,50))   # 5) sonic on tripod ~14 m from tower
    mast_dates.append(datetime(2019,12,8,14,00))  # 6) raising mast to 23 m, a pause?
    mast_dates.append(datetime(2019,12,9,7,30))   # 7) reached 23 m

    # Ola says he's guessed at some of these... ... ...
    mast_params['mast_hdg'].append(nan)
    mast_params['mast_hdg'].append(40.7)
    mast_params['mast_hdg'].append(40.7)
    mast_params['mast_hdg'].append(291.2)
    mast_params['mast_hdg'].append(291.2)
    mast_params['mast_hdg'].append(215)
    mast_params['mast_hdg'].append(228)

    mast_params['gps_hdg_mast_setup'].append(nan)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(290)
    mast_params['gps_hdg_mast_setup'].append(291.2)

    mast_params['mast_sonic_heights'].append(3.1)
    mast_params['mast_sonic_heights'].append(31.72)
    mast_params['mast_sonic_heights'].append(nan)
    mast_params['mast_sonic_heights'].append(1.6)
    mast_params['mast_sonic_heights'].append(3.78)
    mast_params['mast_sonic_heights'].append(18.4)
    mast_params['mast_sonic_heights'].append(23.28)

    # sanity check, prolly not necessary
    if len(mast_params['mast_hdg']) != len(mast_dates)\
    or len(mast_params['gps_hdg_mast_setup']) != len(mast_dates)\
    or len(mast_params['mast_sonic_heights']) != len(mast_dates):
        fatal('something went awry... this is not good')

    # make sure we're at the right index for the day we're starting on, where
    if start_time > mast_dates[mast_index]:
        for date in mast_dates:
            if start_time > date and date!= mast_dates[0]:
                mast_index += 1

    # WXT transitions, dates/times, & heights:
    wxt_index   = 0
    wxt_dates   = []
    wxt_heights = []
    wxt_dates.append(datetime(2019,10,19,6,0))   # 1) WXT on 2-m level on unraised tower
    wxt_dates.append(datetime(2019,10,22,1,0))   # 2) WXT put more upright near 8m level on unraised tower
    wxt_dates.append(datetime(2019,10,24,5,30))  # 3) tower raised WXT at 2 m height
    wxt_dates.append(datetime(2019,10,26,1,0))   # 4) WXT moved to mast tripod
    wxt_dates.append(datetime(2019,10,26,7,0))   # 5) mast raised to 30 m
    wxt_dates.append(datetime(2019,11,18,12,50)) # 6) mast collapses (WXT still running)
    wxt_dates.append(datetime(2019,11,19,10,30)) # 7) WXT removed and brought onboard
    wxt_dates.append(datetime(2019,11,28,5,0))   # 8) WXT mounted on 2-mtower boom
    wxt_dates.append(datetime(2019,12,8,14,0))   # 9) WXT moved to mast and raised to 23 m
    wxt_dates.append(datetime(2019,12,9,7,30))   # 10) reached 23m
    wxt_heights.append(1.1)
    wxt_heights.append(1.5)
    wxt_heights.append(2)
    wxt_heights.append(3.2)
    wxt_heights.append(30.76)
    wxt_heights.append(0)
    wxt_heights.append(nan)
    wxt_heights.append(2)
    wxt_heights.append(17.5)
    wxt_heights.append(22.37)
    if len(wxt_heights) != len(wxt_dates):
        fatal('something went awry... this is bad')

    # make sure we're at the right index for the day we're starting on
    if start_time > wxt_dates[wxt_index]:
        for date in wxt_dates:
            if start_time > date and date!= wxt_dates[0]:
                wxt_index += 1

    # licor transitions, dates/times, & heights:
    licor_index   = 0 # used to keep track of where you are in the dates, this is ugly, can't you get the index
    licor_dates   = []
    licor_heights = []
    licor_dates.append(datetime(2019,10,19,6,0))  # 1) on unraised tower at 6-m height
    licor_dates.append(datetime(2019,10,24,5,30)) # 2) on raised tower at 6-m height
    licor_dates.append(datetime(2019,11,1,5,0))   # 3) moved to two meters... cause it doesn't stay clean
    licor_heights.append(1.5)
    licor_heights.append(5.18)
    licor_heights.append(2.35)

    if len(licor_heights) != len(licor_dates):
        fatal('something went awry... this is ... not the best')

    # make sure we're at the right index for the day we're starting on
    if start_time > licor_dates[licor_index]:
        for date in licor_dates:
            if start_time > date and date!= licor_dates[0]:
                licor_index += 1

    # mast dates and headings w.r.t. tower from Ola's notes
    mast_hdg_dates   = [datetime(2019,10,15,0,0) , datetime(2019,10,26,7,0) , datetime(2019,11,18,12,50),\
                       datetime(2019,11,28,4,30) , datetime(2019,12,1,9,50) , datetime(2019,12,8,14,00),\
                       datetime(2019,12,9,7,30)]
    mast_hdg_vals    = {'mast_hdg' : [nan, 40.7, 40.7, 291.2, 291.2, 215, 228],
                        'gps_hdg'  : [nan, 291.2, 291.2, 291.2, 291.2, 290, 291.5], # 'gps_hdg_mast_setup'??
                        'date'     : mast_hdg_dates,}
    mast_hdg_df = pd.DataFrame(mast_hdg_vals, index=mast_hdg_dates)


    # ################################################################################################# 
    # Now that everything is defined, we read in the logger data for the date range requested and then do vector
    # operations for data QC, as well as any processing to derive output variables from these data. i.e. no loops

    # read *all* of the tower logger data...? this could be too much. but why have so much RAM if you don't use it?
    # this doesn't need to be threaded but it was in the asfs code and you want the chance to abstract it later
    q = Queue()
    Thread(target=get_slow_netcdf_data, 
           args=(start_time, end_time, 
                 q)).start()
    slow_data = q.get()
    

    n_entries   = slow_data.size
    if slow_data.empty: # 'fatal' is a print function defined at the bottom of this script that exits
        fl.fatal('No slow data for time range {} ---> {} ?'.format(start_time,end_time))
        
    verboseprint('===================================================')
    verboseprint('Data and observations provided by the slow data:')
    verboseprint('===================================================')
    if args.verbose: slow_data.info(verbose=True) # must be contained
    verboseprint('===================================================')
    print("\n A small sample of slow data:\n")
    print(slow_data)
    printline(startline="\n")
    # now clean and QC the logger data 'subtleties'. any and all fixing of logger data is done here
    # ###################################################################################################
    # correct apogee_body and apogee_target data, body & targ temperatures were reversed before this time
    verboseprint("... cleaning up slow data")
    # missing met data comes as '0' instead of NaN... good stuff
    zeros_list = ['vaisala_RH_2m','vaisala_RH_6m','vaisala_RH_10m', 'mast_RH','vaisala_P_2m','mast_P','sr50_dist']
    for param in zeros_list: # make the zeros nans
        slow_data[param].mask(slow_data[param]==0.0, inplace=True)

    RH_list = ['vaisala_RH_2m','vaisala_RH_6m','vaisala_RH_10m', 'mast_RH']
    for param in RH_list: # make the zeros nans
        RH_vals = slow_data[param]
        slow_data[param].mask( (RH_vals<rh_thresh[0]) | (RH_vals>rh_thresh[1]) , inplace=True)

    press_list = ['vaisala_P_2m','mast_P']
    for param in press_list: # make the zeros nans
        P_vals = slow_data[param]
        slow_data[param].mask( (P_vals<p_thresh[0]) | (P_vals>p_thresh[1]) , inplace=True)

    temps_list = ['vaisala_T_2m','vaisala_T_6m','vaisala_T_10m','mast_T','apogee_targ_T','apogee_body_T']
    for param in temps_list: # identify when T==0 is actually missing data, this takes some logic
        T_vals = slow_data[param]
        slow_data[param].mask( (T_vals<T_thresh[0]) | (T_vals>T_thresh[1]) , inplace=True)
        
        potential_inds  = np.where(slow_data[param]==0.0)
        if potential_inds[0].size==0: continue # if empty, do nothing, this is unnecessary
        ind = 0 
        while ind < len(potential_inds[0]):
            curr_ind = potential_inds[0][ind]
            lo = ind
            hi = ind+60
            T_nearby = slow_data[param].iloc[lo:hi]
            if np.any(T_nearby < -5) or np.any(T_nearby > 5):    # temps cant go from 0 to +/-5C in 1 minute
                slow_data[param].iloc[ind] = nan
            if (slow_data[param].iloc[lo:hi] == 0).all(): # no way all values for a minute are *exactly* 0
                ind = ind + 60
                slow_data[param].iloc[lo:hi] = nan
            else:
                ind = ind+1

    # Vaisala QC
    slow_data['mast_P']         .loc[datetime(2020,3,13,0,0,0):datetime(2020,5,13,0,0,0)] = nan # something went horribly wrong with the pressure sensor during the leg 3 newdle reboot           
    slow_data['vaisala_T_2m']   .loc[datetime(2020,1,17,17,21,32):datetime(2020,1,19,11,45,54)] = nan # something unexplained here, need to remove it manually
    slow_data['vaisala_RH_2m']  .loc[datetime(2020,1,17,17,21,32):datetime(2020,1,19,11,45,54)] = nan # ditto
    slow_data['vaisala_T_2m']   .loc[:datetime(2019,10,19,7,19,37)] = nan # right at the beginning bogus T values
    slow_data['vaisala_T_6m']   .loc[:datetime(2019,10,19,5,57,56)] = nan # ditto
    slow_data['vaisala_T_10m']  .loc[:datetime(2019,10,15,7,31,29)] = nan # ditto    
    slow_data['vaisala_RH_2m']  .loc[:datetime(2019,10,15,8,55,0)] = nan # ditto
    slow_data['vaisala_RH_6m']  .loc[:datetime(2019,10,15,8,55,0)] = nan # ditto
    slow_data['vaisala_RH_10m'] .loc[:datetime(2019,10,15,8,55,0)] = nan # ditto   
    slow_data['vaisala_Td_2m']  .loc[:datetime(2019,10,15,8,55,0)] = nan # ditto
    slow_data['vaisala_Td_6m']  .loc[:datetime(2019,10,15,8,55,0)] = nan # ditto
    slow_data['vaisala_Td_10m'] .loc[:datetime(2019,10,15,8,55,0)] = nan # ditto  
    slow_data['vaisala_P_2m']   .mask( (slow_data['vaisala_P_2m']<p_thresh[0])     | (slow_data['vaisala_P_2m']>p_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_T_2m']   .mask( (slow_data['vaisala_T_2m']<T_thresh[0])     | (slow_data['vaisala_T_2m']>T_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_T_6m']   .mask( (slow_data['vaisala_T_6m']<T_thresh[0])     | (slow_data['vaisala_T_6m']>T_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_T_10m']  .mask( (slow_data['vaisala_T_10m']<T_thresh[0])    | (slow_data['vaisala_T_10m']>T_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_Td_2m']  .mask( (slow_data['vaisala_Td_2m']<T_thresh[0])    | (slow_data['vaisala_Td_2m']>T_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_Td_6m']  .mask( (slow_data['vaisala_Td_6m']<T_thresh[0])    | (slow_data['vaisala_Td_6m']>T_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_Td_10m'] .mask( (slow_data['vaisala_Td_10m']<T_thresh[0])   | (slow_data['vaisala_Td_10m']>T_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_RH_2m']  .mask( (slow_data['vaisala_RH_2m']<rh_thresh[0])   | (slow_data['vaisala_RH_2m']>rh_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_RH_6m']  .mask( (slow_data['vaisala_RH_6m']<rh_thresh[0])   | (slow_data['vaisala_RH_6m']>rh_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_RH_10m'] .mask( (slow_data['vaisala_RH_10m']<rh_thresh[0])  | (slow_data['vaisala_RH_10m']>rh_thresh[1]) , inplace=True) # ppl
    slow_data['mast_T']         .mask( (slow_data['mast_T']<T_thresh[0])           | (slow_data['mast_T']>T_thresh[1]) , inplace=True) # ppl
    slow_data['mast_T']         .mask( (slow_data['vaisala_T_2m']<-1) & (abs(slow_data['mast_T'])==0) , inplace=True)    

    # Vaisala relative corrections
    #   Tower was lowered from 2019,10,19,7,19,0 to 2019,10,24,5,30,0 (n=425459 sec)
    #   The precised heights were within 20 cm above the surface a little more than a meter high (see vasaila_T_height_on_ground)
    #   This is a slight correction (inside measurement uncertainty) to the measured temperatures that make them more 
    #   intercomparable for making profiles. The bias correction forces the three sensors to the mean of the sensors 
    #   during the comparison period. It is based on the mean differences. Temperature dependencies are not (qualitatively) conclusive 
    #   enough, nor are any dependencies easily parameterized, nor does the comparison period span a large enough range in
    #   temperature to justify either intrpolation or extrapolation of correction factors.
    slow_data['vaisala_T_2m'] = slow_data['vaisala_T_2m']+0.0643
    slow_data['vaisala_T_6m'] = slow_data['vaisala_T_6m']-0.0513
    slow_data['vaisala_T_10m'] = slow_data['vaisala_T_10m']-0.0130      
       
    # here we derive useful parameters computed from logger data that we want to write to the output file
    # ###################################################################################################
    # compute RH wrt ice -- compute RHice(%) from RHw(%), Temperature(deg C), and pressure(mb)
    Td2, h2, a2, x2, Pw2, Pws2, rhi2 = fl.calc_humidity_ptu300(slow_data['vaisala_RH_2m'],\
                                                               slow_data['vaisala_T_2m']+K_offset,
                                                               slow_data['vaisala_P_2m'],
                                                               0)
    slow_data['RHi_vaisala_2m']          = rhi2
    slow_data['enthalpy_vaisala_2m']     = h2
    slow_data['abs_humidity_vaisala_2m'] = a2
    slow_data['pw_vaisala_2m']           = Pw2
    slow_data['MR_vaisala_2m']           = x2
    

    # atm pressure adjusted assuming 1 hPa per 10 m (1[hPA]*ht[m]/10[m]), except for mast, which has a direct meas.
    p6    = slow_data['vaisala_P_2m']-1*6/10
    p10   = slow_data['vaisala_P_2m']-1*10/10    
        # we are missing a lot of the mast pressures so I will fill in with an approximation    
    pmast = slow_data['mast_P'] 
    pmast.fillna(slow_data['vaisala_P_2m']-1*mast_params['mast_sonic_heights'][mast_index]/10, inplace=True)

    Td6, h6, a6, x6, Pw6, Pws6, rhi6 = fl.calc_humidity_ptu300(slow_data['vaisala_RH_6m'],\
                                                               slow_data['vaisala_T_6m']+K_offset,
                                                               p6,
                                                               0)
    slow_data['RHi_vaisala_6m']          = rhi6
    slow_data['enthalpy_vaisala_6m']     = h6
    slow_data['abs_humidity_vaisala_6m'] = a6
    slow_data['pw_vaisala_6m']           = Pw6
    slow_data['MR_vaisala_6m']           = x6

    Td10, h10, a10, x10, Pw10, Pws10, rhi10 = fl.calc_humidity_ptu300(slow_data['vaisala_RH_10m'],\
                                                                      slow_data['vaisala_T_10m']+K_offset,
                                                                      p10,
                                                                      0)
    slow_data['RHi_vaisala_10m']          = rhi10
    slow_data['enthalpy_vaisala_10m']     = h10
    slow_data['abs_humidity_vaisala_10m'] = a10
    slow_data['pw_vaisala_10m']           = Pw10
    slow_data['MR_vaisala_10m']           = x10

    Tdm, hm, am, xm, Pwm, Pwsm, rhim = fl.calc_humidity_ptu300(slow_data['mast_RH'],\
                                                               slow_data['mast_T']+K_offset,
                                                               pmast,
                                                               -1)
    slow_data['dewpoint_vaisala_mast']     = Tdm
    slow_data['RHi_vaisala_mast']          = rhim
    slow_data['enthalpy_vaisala_mast']     = hm
    slow_data['abs_humidity_vaisala_mast'] = am
    slow_data['pw_vaisala_mast']           = Pwm
    slow_data['MR_vaisala_mast']           = xm

    # QC GPS and add useful data columns, these were sprinkled throughout Ola's code, like information nuggets
    slow_data['tower_lat']     = slow_data['gps_lat_deg']+slow_data['gps_lat_min']/60.0 # add decimal values
    slow_data['tower_lon']     = slow_data['gps_lon_deg']+slow_data['gps_lon_min']/60.0
    slow_data['tower_heading'] = slow_data['gps_hdg']/100.0  # convert to degrees
    slow_data['tower_heading'] = slow_data['tower_heading'].where(~np.isinf(slow_data['tower_heading'])) # infinities->nan
    slow_data['gps_alt']       = slow_data['gps_alt']/1000.0 # convert to meters
    slow_data['tower_lat'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4) , inplace=True) 
    slow_data['tower_lon'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4), inplace=True) 
    slow_data['gps_alt'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4), inplace=True) 
    slow_data['tower_heading'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4), inplace=True) 

    # sr50 dist QC then in m & snow depth in cm, both corrected for temperature, snwdpth_meas is height in cm on oct 27 2019
    slow_data['sr50_dist'].loc[:raise_day] = nan # sr50 data is garbage when the tower is down (it's pointed at the horizon or something)
    slow_data['sr50_dist'].mask( (slow_data['sr50_dist']<sr50d[0])  | (slow_data['sr50_dist']>sr50d[1]) , inplace=True) # ppl
    slow_data['sr50_dist']  = fl.despike(slow_data['sr50_dist'],0.05,300,"yes") # replace spikes outside 2 cm over 5 min sec with 5 min median
    slow_data['sr50_dist']  = slow_data['sr50_dist']*sqrt((slow_data['vaisala_T_2m']+K_offset)/K_offset)
    slow_data['snow_depth'] = sr50_init_depth + (sr50_init_dist-slow_data['sr50_dist']*100)

    # Flux Plate QC
    slow_data['fp_A_Wm2'].mask( (slow_data['fp_A_Wm2']<flxp[1]) & (abs(slow_data['fp_A_Wm2'])>flxp[1]) , inplace=True) # ppl
    slow_data['fp_B_Wm2'].mask( (slow_data['fp_B_Wm2']<flxp[1]) & (abs(slow_data['fp_B_Wm2'])>flxp[1]) , inplace=True) # ppl
    slow_data['fp_A_Wm2'].loc[:fpA_bury_date] = nan # data is garbage before being buried
    slow_data['fp_B_Wm2'].loc[:fpB_bury_date] = nan # data is garbage before being buried

    # IRT QC
    slow_data['apogee_body_T'].mask( (slow_data['apogee_body_T']<irt_targ[0]) | slow_data['apogee_body_T']>irt_targ[1] , inplace=True) # ppl
    slow_data['apogee_targ_T'].mask( (slow_data['apogee_targ_T']<irt_targ[0]) | slow_data['apogee_targ_T']>irt_targ[1] , inplace=True) # ppl
    slow_data['apogee_body_T'].mask( (slow_data['vaisala_T_2m']<-1) & (abs(slow_data['apogee_body_T'])==0) , inplace=True) # reports spurious 0s sometimes
    slow_data['apogee_targ_T'].mask( (slow_data['vaisala_T_2m']<-1) & (abs(slow_data['apogee_targ_T'])==0) , inplace=True) # reports spurious 0s sometimes
    slow_data['apogee_body_T']  = fl.despike(slow_data['apogee_body_T'],2,60,'yes') # replace spikes outside 2C over 60 sec with 60 s median
    slow_data['apogee_targ_T']  = fl.despike(slow_data['apogee_targ_T'],2,60,'yes') # replace spikes outside 2C over 60 sec with 60 s median

    # Calculate bearings and adjust heading
    # Read today's Met City AIS 
    print('...finding bearing, adjusting heading') 
    # Load it
    ais_df = pd.DataFrame()  
    for i in range(-1,(end_time-start_time).days+2,1):
       path  = ais_dir+'floenavi-ais_211003823-'+(start_time+timedelta(i)).strftime('%Y%m%d')+'.dat'       
       if  os.path.isfile(path) and os.stat(path).st_size > 0:           
           df = pd.read_csv(path,sep='\s+',parse_dates={'date': [0,1]}).set_index('date')
           df.columns = ["lat","lon"]
           ais_df = pd.concat([ais_df,df]) 
    
    if ais_df.empty == False:       
        ais_df=ais_df.resample('1s').interpolate().reindex(slow_data.index)
        lat1 = np.array(ais_df['lat'])
        lon1 = np.array(ais_df['lon'])
        lat2 = np.array(slow_data['tower_lat'])
        lon2 = np.array(slow_data['tower_lat'])
        dd=fl.distance(lat1,lon1,lat2,lon2) # just a sanity check... distance from AIS to tower is 22.9 m
        br=fl.calculate_initial_angle(lat1,lon1,lat2,lon2) 
        ais_df['br']=br
        ais_df['br']=ais_df['br']#-(ais_df['br'].mean()-slow_data['tower_heading'].mean())
        slow_data['tower_heading']=ais_df['br']

    # rename columns to match expected level2 names from data_definitions, there's probably a more clever way to do this
    slow_data.rename(inplace=True, columns =\
                     {
                         'call_time_mainscan' : 'logger_scantime'           ,
                         'vaisala_T_2m'       : 'temp_vaisala_2m'           ,
                         'vaisala_T_6m'       : 'temp_vaisala_6m'           ,
                         'vaisala_T_10m'      : 'temp_vaisala_10m'          ,
                         'mast_T'             : 'temp_vaisala_mast'         ,
                         'vaisala_Td_2m'      : 'dewpoint_vaisala_2m'       ,
                         'vaisala_Td_6m'      : 'dewpoint_vaisala_6m'       ,
                         'vaisala_Td_10m'     : 'dewpoint_vaisala_10m'      ,
                         'vaisala_RH_2m'      : 'rel_humidity_vaisala_2m'   ,
                         'vaisala_RH_6m'      : 'rel_humidity_vaisala_6m'   ,
                         'vaisala_RH_10m'     : 'rel_humidity_vaisala_10m'  ,
                         'mast_RH'            : 'rel_humidity_vaisala_mast' ,
                         'vaisala_P_2m'       : 'pressure_vaisala_2m'       ,
                         'mast_P'             : 'mast_pressure'             ,    
                         'apogee_body_T'      : 'body_T_IRT'                ,       
                         'apogee_targ_T'      : 'surface_T_IRT'             ,    
                         'fp_A_mV'            : 'flux_plate_A_mv'           ,  
                         'fp_B_mV'            : 'flux_plate_B_mv'           ,  
                         'fp_A_Wm2'           : 'flux_plate_A_Wm2'          , 
                         'fp_B_Wm2'           : 'flux_plate_B_Wm2'          , 
    }, errors="raise")

    # ###################################################################################################
    # OK, all is done with the logger data, now get the 20hz data and put it into its own netcdf file
    # done in a loop because I only have 32GB of RAM in my laptop and there's no sense doing otherwise
    day_series = pd.date_range(start_time, end_time)    # we're going to loop over these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    for today in day_series: # loop over the days in the processing range
        tomorrow  = today+day_delta
        Hz10_today        = pd.date_range(today, tomorrow, freq='0.1S')           # all the 0.1 seconds today, for obs
        seconds_today     = pd.date_range(today, tomorrow, freq='S')              # all the seconds today, for obs
        minutes_today     = pd.date_range(today, tomorrow, freq='T')              # all the minutes today, for obs
        ten_minutes_today = pd.date_range(today, tomorrow, freq='10T')            # all the 10 minutes today, for obs


        # Chris moved this block to the top of the day_series loop because he needed some of the output
        # earlier. Nothing bad happened...  this probably doesn't really need to be a loop
        for this_second in seconds_today:
            # get the right instrument heights for this day... goes in the day loop
            if today < raise_day:
                sonic_z  = sonic_height_on_ground
                Tvais_z  = vasaila_T_height_on_ground
                RHvais_z = vasaila_Rh_height_on_ground
                GPS_z    = vasaila_P_height_on_ground
                Pvais_z  = GPS_height_on_ground
                SR50_z   = SR50_height_on_ground
            else:
                sonic_z  = sonic_height_raised
                Tvais_z  = vasaila_T_height_raised
                RHvais_z = vasaila_Rh_height_raised
                GPS_z    = vasaila_P_height_raised
                Pvais_z  = GPS_height_raised
                SR50_z   = SR50_height_raised

            # has the licor moved today?
            if licor_index+1 < len(licor_dates): # make sure we aren't past the last event
                if today >= licor_dates[licor_index+1]:
                    licor_index +=1
            licor_z = licor_heights[licor_index]

            # has the mast moved today?
            if mast_index+1 < len(mast_dates): # make sure we aren't past the last event
                if today >= mast_dates[mast_index+1]:
                    mast_index += 1
            mast_hdg           = mast_params['mast_hdg'][mast_index]
            gps_hdg_mast_setup = mast_params['gps_hdg_mast_setup'][mast_index]
            mast_sonic_height  = mast_params['mast_sonic_heights'][mast_index]

            # has the wxt moved today?
            if wxt_index+1 < len(wxt_dates): # make sure we aren't past the last event
                if today > wxt_dates[wxt_index+1]:
                    wxt_index += 1
            wxt_z = wxt_heights[wxt_index]

        # before putting the data in, make sure it's indexed for the full time range (i.e. times without obs
        # become NaNs) and select only the data from today to keep in the output file
        logger_today = slow_data[:][today:tomorrow] # does this do what you think?
        logger_today = logger_today.reindex(labels=seconds_today, copy=False)

        # raw data... ~20 Hz data, 5Mb files each hour...
        #                              !! Important !!
        #   to calculate turbulent params, the data is first resampled to 10 Hz by averaging then reindexed to a
        #   continuous 10 Hz time grid (NaN at blackouts) of Lenth 60 min x 60 sec x 10 Hz = 36000
        #   Later on (below) we will fill all missing times with the median of the (30 min?) flux sample.

        # ~~~~~~~~~~~~~~~~~~~~ (1) Read the raw data ~~~~~~~~~~~~~~~~~~~~~~~
        #   The data are nominally 20 Hz for MOSAiC, but irregular time stamping
        #   because NOAA Services timestamped to the ~ms at time of processing by Windows OS
        #
        raw_fast_data = {}
        metek_inst_keys = ['metek_2m', 'metek_6m', 'metek_10m', 'metek_mast']
        for inst in metek_inst_keys:
            raw_fast_data[inst] = get_fast_netcdf_data(inst, today)
        raw_licor_data = get_fast_netcdf_data('licor', today)

        # ~~~~~~~~~~~~~~~~~~~~~ (2) Quality control ~~~~~~~~~~~~~~~~~~~~~~~~
        print('... quality controlling the fast data now.')

        # I'm being a bit lazy here: no accouting for reasons data was rejected. For another day.
        # must use bitwise operators for boolean array declarations and the parenthesis around each comparison
        # are required this is a point where the python syntax gets a bit ridiculous IMO
        for inst in metek_inst_keys:
            # physically-possible limits
            met_T = raw_fast_data[inst][inst+'_T']
            met_X = raw_fast_data[inst][inst+'_x']
            met_Y = raw_fast_data[inst][inst+'_y']
            met_Z = raw_fast_data[inst][inst+'_z']

            raw_fast_data[inst][inst+'_T'].mask( (met_T<T_thresh[0]) | (met_T>T_thresh[1]) , inplace=True)
            raw_fast_data[inst][inst+'_x'].mask( np.abs(met_X) > ws_thresh[1]              , inplace=True)
            raw_fast_data[inst][inst+'_y'].mask( np.abs(met_Y) > ws_thresh[1]              , inplace=True)
            raw_fast_data[inst][inst+'_z'].mask( np.abs(met_Z) > ws_thresh[1]              , inplace=True)

            if inst != 'metek_mast': #mast, no inc dat
                met_incx = raw_fast_data[inst][inst+'_incx']
                met_incy = raw_fast_data[inst][inst+'_incy']
                raw_fast_data[inst][inst+'_incx'].mask(np.abs(met_incx) > incl_range[1], inplace=True)
                raw_fast_data[inst][inst+'_incy'].mask(np.abs(met_incy) > incl_range[1], inplace=True)


            # Diagnostic: break up the diagnostic and search for bad paths. the diagnostic
            # is as follows:
            # 1234567890123
            # 1000096313033
            #
            # char 1-2   = protocol stuff. 10 is actualy 010 and saying we receive instantaneous data from network. ignore
            # char 3-7   = data format. we use 96 = 00096
            # char 8     = heating operation mode. we set it to 3 = on but control internally for temp
            #              and data quality (ie dont operate the heater if you dont really have to)
            # char 9     = heating state, 0 = off, 1 = on, 2 = on but faulty
            # char 10    = number of unusable radial paths (max 9). we want this to be 0 and it is redundant with the next...
            # char 11-13 = percent of unusuable paths. in the example above, 3033 = 3 of 9 or 33% bad paths
            #
            # We want to strip off the last 3 digits here and remove data that are not all 0s.
            # To do this fast I will do it by subtracting off the top sig figs like below.
            # The minumum value is 1/9 so I will set the threhsold a little > 0 for slop in precision
            # We could set this higher. Perhaps 1 or 2 bad paths is not so bad? Not sure.
            if inst != 'metek_mast': #mast, no heat data?
                bad_data = (raw_fast_data[inst][inst+'_heatstatus']/1000\
                            -np.floor(raw_fast_data[inst][inst+'_heatstatus']/1000)) >  max_bad_paths[0]
                raw_fast_data[inst][inst+'_x'].mask(bad_data, inplace=True)
                raw_fast_data[inst][inst+'_y'].mask(bad_data, inplace=True)
                raw_fast_data[inst][inst+'_z'].mask(bad_data, inplace=True)
                raw_fast_data[inst][inst+'_T'].mask(bad_data, inplace=True)

        #
        # And now Licor ####################################################
        # Physically-possible limits, python is not happy with conventions in ambiguity of "or"
        # im accustomed to in matlab so i split it into two lines
        T       = raw_licor_data['licor_T']
        pr      = raw_licor_data['licor_pr']
        h2o     = raw_licor_data['licor_h2o']
        co2     = raw_licor_data['licor_co2']
        co2_str = raw_licor_data['licor_co2_str']

        raw_licor_data['licor_T']  .mask( (T<T_thresh[0])  | (T>T_thresh[1]) , inplace=True) 
        raw_licor_data['licor_pr'] .mask( (pr<p_thresh[0]) | (pr>p_thresh[1]), inplace=True)
        raw_licor_data['licor_h2o'].mask( (h2o<lic_h2o[0]) | (h2o>lic_h2o[1]), inplace=True)
        raw_licor_data['licor_co2'].mask( (co2<lic_co2[0]) | (co2>lic_co2[1]), inplace=True)

        # CO2 signal strength is a measure of window cleanliness applicable to CO2 and H2O vars
        raw_licor_data['licor_co2'].mask( (co2_str<lic_co2sig_thresh[0]) | (co2_str>lic_co2sig_thresh[1]),  inplace=True)
        raw_licor_data['licor_h2o'].mask( (co2_str<lic_co2sig_thresh[0]) | (co2_str>lic_co2sig_thresh[1]),  inplace=True)

        # The diagnostics are boolean and were decoded in level1
        pll           = raw_licor_data['licor_pll']
        detector_temp = raw_licor_data['licor_dt']
        chopper_temp  = raw_licor_data['licor_ct']
        # Phase Lock Loop. Optical filter wheel rotating normally if 1, else "abnormal"
        bad_pll = pll == 0
        # If 0, detector temp has drifted too far from set point. Should yield a bad calibration, I think
        bad_dt = detector_temp == 0
        # Ditto for the chopper housing temp
        bad_ct = chopper_temp == 0

        # Get rid of diag QC failures
        raw_licor_data['licor_h2o'][bad_pll] = nan
        raw_licor_data['licor_co2'][bad_pll] = nan
        raw_licor_data['licor_h2o'][bad_dt]  = nan
        raw_licor_data['licor_co2'][bad_dt]  = nan
        raw_licor_data['licor_h2o'][bad_ct]  = nan
        raw_licor_data['licor_co2'][bad_ct]  = nan

        # Despike: meant to replace despik.m by Fairall. Works a little different tho
        #   Here screens +/-5 m/s outliers relative to a running 1 min median
        #   args go like return = despike(input,oulier_threshold_in_m/s,window_length_in_n_samples)
        #   !!!! Replaces failures with the median of the window !!!!
        for inst in metek_inst_keys:
            raw_fast_data[inst][inst+'_x'] = fl.despike(raw_fast_data[inst][inst+'_x'],5,1200,'yes')
            raw_fast_data[inst][inst+'_y'] = fl.despike(raw_fast_data[inst][inst+'_y'],5,1200,'yes')
            raw_fast_data[inst][inst+'_z'] = fl.despike(raw_fast_data[inst][inst+'_z'],5,1200,'yes')
            raw_fast_data[inst][inst+'_T'] = fl.despike(raw_fast_data[inst][inst+'_T'],5,1200,'yes')
            
        # There are bad measurements right on the edge of radpidly changing co2_str where co2_str is
        # high enough not to be screen out, but is still changeing, e.g., after cleaning. This is an attempt
        # to screen that out and hopefully it doesn't overdo it. The threshold translates to 1% per 30 min. 
        bad_licor = fl.despike(raw_licor_data['licor_co2_str'],1,36000,'ret')        
        raw_licor_data['licor_co2'][bad_licor==True] = nan
        raw_licor_data['licor_h2o'][bad_licor==True] = nan
        raw_licor_data['licor_T'][bad_licor==True] = nan
        raw_licor_data['licor_pr'][bad_licor==True] = nan

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
        fast_data_10hz = {}
        for inst in metek_inst_keys:
            metek_10hz = raw_fast_data[inst].resample('100ms').mean()
            fast_data_10hz[inst] = metek_10hz.reindex(index=Hz10_today)

        licor_10hz = raw_licor_data.resample('100ms').mean()
        licor_10hz = licor_10hz.reindex(index=Hz10_today)

        # ~~~~~~~~~~~~~~~~~ (4) Do the Tilt Rotation  ~~~~~~~~~~~~~~~~~~~~~~
        print("... cartesian tilt rotation. Translating body -> earth coordinates. Caveats!!!")
        print("... please read in-line comments ! Solution being developed with J. Hutchings.")

        # This really only affects the slow interpretation of the data.
        # When we do the fluxes it will be a double rotation into the streamline that implicitly accounts for deviations between body and earth
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
        #               slow_data['gps_hdg'].reindex(index=Hz10_today, copy=False).interpolate('linear')

        #           However, there is low-frequency variability in the heading information recevied at the gps. The period is roughly
        #           1-2 hours and the standard deviation is 1-1.5 deg. This variability is NOT movement of the ice floe! We saw this in
        #           the GPS when stationary in Boulder and it looks similar at MOSAiC. Jenny H. says it is normal and calls it "noise".
        #           Probably somehow related to the satellite constellation, though it was uncorrelated with GPS qc vars in Colorado.
        #           It is not noise in the conventional sense, but appears very systematic, which makes it something we need to take into account.
        #
        #           In order to avoid propogating the error into the reported wind directions, we need some sort of low-pass filter having an averaging period that is shorter than significant deviations in the actual heading of the floe but at
        #           least ~3 hours.
        #                           For now, I will use the DAILY AVERAGE HEADING!
        #                           Working with J Hutchings to analyze the times scales of floe rotation vs the time scales of GPS HEHDT errors.
        #                           Planning to develop of floe-scale hdg by using multiple GPS acroess the floe to beat down the error

        for inst in metek_inst_keys:
            if 'mast' not in inst:
                ct_u, ct_v, ct_w = fl.tilt_rotation(fast_data_10hz[inst] [inst+'_incy'],
                                                    fast_data_10hz[inst] [inst+'_incx'],
                                                    np.zeros(len(fast_data_10hz[inst] ))+logger_today['gps_hdg'].mean(),
                                                    fast_data_10hz[inst] [inst+'_y'],
                                                    fast_data_10hz[inst] [inst+'_x'],
                                                    fast_data_10hz[inst] [inst+'_z'])
                fast_data_10hz[inst][inst+'_y'] = ct_u # y -> u on uSonic!
                fast_data_10hz[inst][inst+'_x'] = ct_v # x -> v on uSonic!
                fast_data_10hz[inst][inst+'_z'] = ct_w

            else:
                # !! The mast wind vectors/directions need work.
                # Byron has  v*-1 after swapping x/y, which is the left-hand to right-hand coordinate swap
                # which I think is correct, but it isn't working well or consistently
                # No inclinometer up here. For now we are assuming it is plum
                nmastvals = len(fast_data_10hz[inst])
                ct_u, ct_v, ct_w = fl.tilt_rotation(np.zeros(nmastvals),
                                                    np.zeros(nmastvals),
                                                    np.zeros(nmastvals)+logger_today['gps_hdg'].mean(),
                                                    fast_data_10hz[inst][inst+'_x']*(-1),
                                                    fast_data_10hz[inst][inst+'_y'],
                                                    fast_data_10hz[inst][inst+'_z'])
                                                    # not sure this ^ is correct: It should be on y

                fast_data_10hz[inst][inst+'_x'] = ct_u # x -> u on USA-1!
                fast_data_10hz[inst][inst+'_y'] = ct_v # y -> v on USA-1!
                fast_data_10hz[inst][inst+'_z'] = ct_w

            # start referring to xyz as uvw now (maybe we should keep both?)
            fast_data_10hz[inst].rename(columns={inst+'_y' : inst+'_u',
                                                 inst+'_x' : inst+'_v',
                                                 inst+'_z' : inst+'_w',
                                                 }, errors="raise", inplace=True) 

        # !!
        # Now we recalculate the 1 min average wind direction and speed from the u and v velocities.
        # These values differ from the stats calcs (*_ws and *_wd) in two ways:
        #   (1) The underlying data has been quality controlled
        #   (2) We have rotated that sonic y,x,z into earth u,v,w
        #
        print("... calculating a corrected set of slow wind speed and direction.")
        metek_ws = {}
        metek_wd = {}
        for inst in metek_inst_keys:
            u_min = fast_data_10hz[inst] [inst+'_u'].resample('1T',label='left').apply(fl.take_average)
            v_min = fast_data_10hz[inst] [inst+'_v'].resample('1T',label='left').apply(fl.take_average)
            if 'mast' not in inst:
                ws_corr, wd_corr = fl.calculate_metek_ws_wd(u_min.index,
                                                         u_min,
                                                         v_min,
                                                         logger_today['gps_hdg']*0) 
            else:
                # correct for mast heading by comparing obs of mast orientation wrt tower, a bit more complicated
                # From Ola's code, Ola says he's guessed at some of these... ... ...
                most_recent_ind  = mast_hdg_df.index.get_loc(today, method='ffill') # get most recent manual mast heading obs
                most_recent_time = mast_hdg_df.index[most_recent_ind]
                most_recent_gps  = mast_hdg_df['gps_hdg'][most_recent_ind]
                most_recent_mast = mast_hdg_df['mast_hdg'][most_recent_ind]
                if most_recent_ind < len(mast_hdg_df.index)-1:
                    if mast_hdg_df.index[most_recent_ind+1].normalize() == today.normalize(): # heading was observed today
                        most_recent_gps  = mast_hdg_df['gps_hdg'][most_recent_ind+1]
                        most_recent_mast = mast_hdg_df['mast_hdg'][most_recent_ind+1]

                # Ola's code: wd_mtk30(igdmtk30(i))=mod(sd(2)+(mast_hdg+(gps_hdg_twr(igdmtk30(i))-gps_hdg_mast_setup)),360);
                mast_hdg_series = most_recent_mast-most_recent_gps+(logger_today['gps_hdg']*0+logger_today['gps_hdg'].mean())
                ws_corr, wd_corr = fl.calculate_metek_ws_wd(u_min.index,
                                                            u_min,
                                                            v_min,
                                                            mast_hdg_series) 

            metek_ws[inst] = ws_corr
            metek_wd[inst] = wd_corr

        # ~~~~~~~~~~~~~~~~~~ (5) Recalculate Stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # !!  Sorry... This is a little messed up. The original stats are read from the NOAA Services stats
        # files, contents calculated from the raw data. But we have QC'd the data and changed the raw
        # values, so we need to update the stats. I do that here. But then was there ever any point in
        # reading the stats data in the first place? nope! and now we don't
        metek_stats = {}
        print('... recalculating the NOAA Services style stats data; corrected, rotated, and quality controlled')
        for inst in metek_inst_keys:

            metek_stats[inst] = pd.DataFrame()
            metek_stats[inst]['wind_speed_'+inst]     = metek_ws[inst]
            metek_stats[inst]['wind_direction_'+inst] = metek_wd[inst]
            metek_stats[inst]['temp_variance_'+inst]  = fast_data_10hz[inst][inst+'_T'].resample('1T',label='left').var()
            metek_stats[inst]['u_'+inst]              = fast_data_10hz[inst][inst+'_u'].resample('1T',label='left').mean()
            metek_stats[inst]['v_'+inst]              = fast_data_10hz[inst][inst+'_v'].resample('1T',label='left').mean()
            metek_stats[inst]['w_'+inst]              = fast_data_10hz[inst][inst+'_w'].resample('1T',label='left').mean()
            metek_stats[inst]['temp_'+inst]           = fast_data_10hz[inst][inst+'_T'].resample('1T',label='left').mean()
            metek_stats[inst]['stddev_u_'+inst]       = fast_data_10hz[inst][inst+'_u'].resample('1T',label='left').std()
            metek_stats[inst]['stddev_v_'+inst]       = fast_data_10hz[inst][inst+'_v'].resample('1T',label='left').std()
            metek_stats[inst]['stddev_w_'+inst]       = fast_data_10hz[inst][inst+'_w'].resample('1T',label='left').std()
            metek_stats[inst]['stddev_T_'+inst]       = fast_data_10hz[inst][inst+'_T'].resample('1T',label='left').std()

        # Each mean is followed by a screeening that rejects mean containing < 50% (300/600 10Hz samples per minute) of valid
        # (non nan) data. I do this for licor but not for metek (above) because in licor this is associated with time when
        # optics and sensor temepratures are at the edge of acceptable limits but are still recording spurious data, perhaps
        # becausse there is a change undeerway (eg, signal strength changing after cleaning as ethanol evaporates). This causes
        # a bias in licor. In metek it probably just means noise and most <50% valid samples are casued by attenutation from
        # blowing snow where the samples that do appear in the window are still "good".    
        licor_stats                     = pd.DataFrame()
        licor_stats['H2O_licor']        = licor_10hz['licor_h2o']     .resample('1T',label='left').mean()
        licor_stats['H2O_licor'][(licor_10hz['licor_h2o']*0+1).resample('1T',label='left').sum() < 300] = nan  
        licor_stats['CO2_licor']        = licor_10hz['licor_co2']     .resample('1T',label='left').mean()
        licor_stats['CO2_licor'][(licor_10hz['licor_co2']*0+1).resample('1T',label='left').sum() < 300] = nan         
        licor_stats['temp_licor']       = licor_10hz['licor_T']       .resample('1T',label='left').mean()
        licor_stats['temp_licor'][(licor_10hz['licor_T']*0+1).resample('1T',label='left').sum() < 300] = nan        
        licor_stats['pr_licor']         = licor_10hz['licor_pr']      .resample('1T',label='left').mean()*10 # [to hPa]
        licor_stats['pr_licor'][(licor_10hz['licor_pr']*0+1).resample('1T',label='left').sum() < 300] = nan        
        licor_stats['co2_signal_licor'] = licor_10hz['licor_co2_str'] .resample('1T',label='left').mean()
        licor_stats['co2_signal_licor'][(licor_10hz['licor_co2_str']*0+1).resample('1T',label='left').sum() < 300] = nan 

        # now put it all together
        stats_data = pd.DataFrame()
        for inst in metek_inst_keys:
            stats_data = pd.concat(  [stats_data, metek_stats[inst]], axis=1)
        stats_data = pd.concat(  [stats_data, licor_stats], axis=1 )
        print(stats_data)
        # ~~~~~~~~~~~~~~~~~~~~ (6) Flux Capacitor  ~~~~~~~~~~~~~~~~~~~~~~~~~
        verboseprint('... calculating turbulent fluxes and associated MO parameter s')

        # Rotation to the streamline, FFT window segmentation, detrending,
        # hamming, and computation of power [welch] & cross spectral densities,
        # covariances and associated diagnostics, as well as derived
        # variables (fluxes and stress parameters) are performed within a
        # sub-function called below.
        #
        # turbulence_data = grachev_fluxcapacitor(z_level_nominal,z_level_n,sonic_dir,metek,licor,clasp)
        #       z_level_nominal = nomoinal height nomenclature as a string: '2m', '6m', '10m', or 'mast' so that we can reference unique column names later
        #       z_level_n = Height of measurements in m, being precise because it affects the calculation
        #       sonic_dir = Orientation (azimuth) of the sonic anemoneter relative to true North
        #       metek = the metek DataFrame
        #       licor = the licor DataFrame - currently unused until we get that coded up
        #       clasp = the clasp data frame - currently unused until we get that coded up
        #
        turb_data = pd.DataFrame()    
        flux_freq = '{}T'.format(integ_time_turb_flux)
        flux_time_today = pd.date_range(today, today+timedelta(1), freq=flux_freq)
        suffix_list = ['_2m','_6m','_10m','_mast'] # suffix for vars in turb file
        # a DatetimeIndex based on integ_time_turb_flux, the integration window
        # for the calculations that is defined at the top  of the code
        for i_inst, inst in enumerate(metek_inst_keys):
            verboseprint("... processing turbulence data for {}".format(inst))
            for time_i in range(0,len(flux_time_today)-1): # flux_time_today = 
                # Get the index, ind, of the metek frame that pertains to the present calculation 
                inds = (fast_data_10hz[inst].index >= flux_time_today[time_i]) \
                       & \
                       (fast_data_10hz[inst].index < flux_time_today[time_i+1]) 

                # !! tower heading...is this meant to be oriented with the sonic North? like, does this
                # equal "sonic north"? hdg = np.float64(logger_today['gps_hdg'][logger_today['gps_hdg'].index ==
                # flux_time_today[time_i]])
                hdg = logger_today['gps_hdg'].mean()

                # make the turbulent flux calculations via Grachev module
                v = False
                if args.verbose: v = True;

                # give generic names for calculations and select the desired indexes
                calc_data = fast_data_10hz[inst][inds]
                calc_data.rename(columns={inst+'_u' : 'u',
                                    inst+'_v' : 'v',
                                    inst+'_w' : 'w',
                                    inst+'_T' : 'T',
                                    }, errors="raise", inplace=True)
                if 'mast' not in inst: sz = sonic_z[0][i_inst]
                else: sz = mast_sonic_height

                data = fl.grachev_fluxcapacitor(sz, hdg, calc_data, [], [], verbose=v)
                data = data.add_suffix(suffix_list[i_inst])
                if time_i == 0: # doubtless there is a better way to initialize this
                    inst_data = data
                else:
                    inst_data = inst_data.append(data)

            # now add the indexer datetime doohicky
            verboseprint("... concatting turbulence calculations to one dataframe")
            inst_data.index = flux_time_today[0:-1]
            turb_data = pd.concat( [turb_data, inst_data], axis=1) # concat columns alongside each other without adding indexes
            
        # calculate the bulk every 30 min
        print('... calculating bulk fluxes for day: {}'.format(today))
        # Input dataframe
            # first get 1 s wind speed. i dont care about direction. 
        ws = (fast_data_10hz['metek_10m']['metek_10m_u']**2 + fast_data_10hz['metek_10m']['metek_10m_v']**2)**0.5
        ws = ws.resample('1s',label='left').apply(fl.take_average)
            # make a better surface temperature
        tsfc = (((slow_data['surface_T_IRT']+273.15)**4 / 0.985)**0.25)-273.15
        empty_data = np.zeros(np.size(slow_data['MR_vaisala_10m'][seconds_today]))
        bulk_input = pd.DataFrame()
        bulk_input['u']  = ws                                               # wind speed                         (m/s)
        bulk_input['ts'] = tsfc                                             # bulk water/ice surface tempetature (degC) this needs to be corrected for reflected
        bulk_input['t']  = slow_data['temp_vaisala_10m'][seconds_today]     # air temperature                    (degC) 
        bulk_input['Q']  = slow_data['MR_vaisala_10m'][seconds_today]/1000  # air moisture mixing ratio          (fraction)
        bulk_input['zi'] = empty_data+600                                   # inversion height                   (m) wild guess
        bulk_input['P']  = slow_data['pressure_vaisala_2m'][seconds_today]  # surface pressure                   (mb)
        bulk_input['zu'] = empty_data+10                                    # height of anemometer               (m)
        bulk_input['zt'] = empty_data+10                                    # height of thermometer              (m)
        bulk_input['zq'] = empty_data+10                                    # height of hygrometer               (m)      
        bulk_input = bulk_input.resample('30min',label='left').apply(fl.take_average)
   
        # output dataframe
        empty_data = np.zeros(len(bulk_input))
        bulk = pd.DataFrame() 
        bulk['bulk_Hs_10m']      = empty_data*nan # hsb: sensible heat flux (Wm-2)
        bulk['bulk_Hl_10m']      = empty_data*nan # hlb: latent heat flux (Wm-2)
        bulk['bulk_tau']         = empty_data*nan # tau: stress                             (Pa)
        bulk['bulk_z0']          = empty_data*nan # zo: roughness length, veolicity              (m)
        bulk['bulk_z0t']         = empty_data*nan # zot:roughness length, temperature (m)
        bulk['bulk_z0q']         = empty_data*nan # zoq: roughness length, humidity (m)
        bulk['bulk_L']           = empty_data*nan # L: Obukhov length (m)       
        bulk['bulk_ustar']       = empty_data*nan # usr: friction velocity (sqrt(momentum flux)), ustar (m/s)
        bulk['bulk_tstar']       = empty_data*nan # tsr: temperature scale, tstar (K)
        bulk['bulk_qstar']       = empty_data*nan # qsr: specific humidity scale, qstar (kg/kg?)
        bulk['bulk_dter']        = empty_data*nan # dter
        bulk['bulk_dqer']        = empty_data*nan # dqer
        bulk['bulk_Hl_Webb_10m'] = empty_data*nan # hl_webb: Webb density-corrected Hl (Wm-2)
        bulk['bulk_Cd_10m']      = empty_data*nan # Cd: transfer coefficient for stress
        bulk['bulk_Ch_10m']      = empty_data*nan # Ch: transfer coefficient for Hs
        bulk['bulk_Ce_10m']      = empty_data*nan # Ce: transfer coefficient for Hl
        bulk['bulk_Cdn_10m']     = empty_data*nan # Cdn_10: 10 m neutral transfer coefficient for stress
        bulk['bulk_Chn_10m']     = empty_data*nan # Chn_10: 10 m neutral transfer coefficient for Hs
        bulk['bulk_Cen_10m']     = empty_data*nan # Cen_10: 10 m neutral transfer coefficient for Hl
        bulk['bulk_Rr']          = empty_data*nan # Reynolds number
        bulk['bulk_Rt']          = empty_data*nan # 
        bulk['bulk_Rq']          = empty_data*nan # 
        bulk=bulk.reindex(index=bulk_input.index)
       
        for ii in range(len(bulk)):
            tmp = [bulk_input['u'][ii],bulk_input['ts'][ii],bulk_input['t'][ii],bulk_input['Q'][ii],bulk_input['zi'][ii],bulk_input['P'][ii],bulk_input['zu'][ii],bulk_input['zt'][ii],bulk_input['zq'][ii]] 
            if not any(np.isnan(tmp)):
                bulkout = fl.cor_ice_A10(tmp)
                for hh in range(len(bulkout)):
                    bulk[bulk.columns[hh]][ii]=bulkout[hh]
     
        # add this to the EC data
        turb_data = pd.concat( [turb_data, bulk], axis=1) # concat columns alongside each other without adding indexes

        print('... writing to level2 netcdf files and calcuating averages for day: {}'.format(today))

        # for level2 we are only writing out 1minute+ files so we
        logger_1min = logger_today.resample('1T', label='left').apply(fl.take_average)
        l2_data = pd.concat([logger_1min, stats_data], axis=1)

        # write out in threads the files separately to save some time... which would be great... but HDF5
        # borks if you try to do it... ? really annoying and I can't find any reason why
        onemin_q = Queue()
        Thread(target=write_level2_netcdf,\
               args=(l2_data.copy(), today, "1min", onemin_q)).start()
        onemin_q.get()

        turb_q = Queue()
        Thread(target=write_turb_netcdf,\
               args=(turb_data.copy(), today, turb_q)).start()
        turb_q  .get()

        tenmin_q = Queue()
        Thread(target=write_level2_netcdf,\
               args=(l2_data.copy(), today, "10min", tenmin_q)).start()
        tenmin_q.get()

    printline()
    print('All done! Netcdf output files can be found in: {}'.format(level2_dir))
    print(version_msg)
    printline()


def get_slow_netcdf_data(start_time, end_time, q): 

    data_atts, data_cols = define_level1_slow()
    time_var = 'time'

    in_dir = level1_dir

    day_series = pd.date_range(start_time, end_time) # get data for these days
    file_list  = [] 
    missing_days = [] 
    for today in day_series: # loop over the days in the processing range and get a list of files
        file_str = '{}/slow_preliminary_tower.{}.nc'.format(in_dir,
                                                            today.strftime('%Y%m%d'))
        if os.path.isfile(file_str): 
            file_list.append(file_str) 
        else:
            missing_days.append(today.strftime('%m-%d-%Y'))
            continue
    if len(missing_days)==0: print("... pulling slow data, there were zero missing days of data")
    else: print("... pulling in slow data, it was missing days:")

    for i, day in enumerate(missing_days): 
        if i%5 == 0: print("\n  ---> ", end =" ")
        if i==len(missing_days)-1: 
            print("{}\n".format(day))
            break
        print("{},  ".format(day), end =" ")

    print("... compiling all days of slow level1 data into single dataframe, takes a second")
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

def get_fast_netcdf_data(inst_group, date):

    # these keys are the names of the groups in the netcdf files and the
    # strings in the tuple on the right will be the strings that we search for
    # in fast_atts to know which atts to apply to which group/variable, the
    # data is the value of the search string, a dict of dicts...
    inst_dict = {}
    inst_dict['metek_2m']   = '2m'   
    inst_dict['metek_6m']   = '6m'   
    inst_dict['metek_10m']  = '10m'  
    inst_dict['metek_mast'] = 'mast' 
    inst_dict['licor']      = 'licor'

    try: search_str = inst_dict[inst_group]
    except:
        fl.fatal("YOU TRIED TO GET A GROUP OF FAST DATA THAT DOESN'T EXIST, TYPO PROBABLY")
        
    data_atts, data_cols = define_level1_fast()
    group_cols = [i for i in data_cols if search_str in i]

    file_dir = level1_dir
    file_name = 'fast_preliminary_tower.{}.nc'.format(date.strftime('%Y%m%d'))
    file_str = '{}/{}'.format(file_dir,file_name)

    if not os.path.isfile(file_str): 
        print('... no fast data on {}, file {} not found !!!'.format(date, file_name))
        nan_row   = np.ndarray((1,len(data_cols)))*nan
        nan_frame = pd.DataFrame(nan_row, columns=data_cols, index=pd.DatetimeIndex([date]))
        return nan_frame

    print("... converting level1 {} data to dataframe, takes a second".format(inst_group))
    # sometimes xarray throws exceptions on first try, had no time to debug it yet:

    try:
        xarr_ds = xr.open_dataset(file_str, group=inst_group)
    except Exception as e:
        print("!!! xarray exception: {}".format(e))
        print("!!! file: {}".format(file_str))
        print("!!! this means there was no data in this file^^^^")
        nan_row   = np.ndarray((1,len(data_cols)))*nan
        nan_frame = pd.DataFrame(nan_row, columns=data_cols, index=pd.DatetimeIndex([date]))
        return nan_frame
    
    data_frame = xarr_ds.to_dataframe()
    n_entries = len(data_frame)
    verboseprint("... {}/1728000 fast entries on {}, representing {}% data coverage"
                 .format(n_entries, date, round((n_entries/1728000)*100.,2)))

    return data_frame

def write_level2_netcdf(l2_data, date, timestep, q):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    l2_atts, l2_cols = define_level2_variables()

    all_missing     = True 
    first_loop      = True
    n_missing_denom = 0

    if l2_data.empty:
        print("... there was no data to write today {} for {}" .format(date,timestep))
        print(l2_data)
        q.put(False)
        return

    # get some useful missing data information for today and print it for the user
    for var_name, var_atts in l2_atts.items():
        try: dt = l2_data[var_name].dtype
        except KeyError as e: 
            print(" !!! no {} in data ... does this make sense??".format(var_name))
            continue
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

    print("... writing {} level2 on {}, ~{}% of data is present".format(timestep, date, 100-avg_missing))

    out_dir  = level2_dir
    file_str = '/mosflxtowermet.level2.{}.{}.nc'.format(timestep,date.strftime('%Y%m%d.%H%M%S'))

    lev2_name  = '{}/{}'.format(out_dir, file_str)

    global_atts = define_global_atts("level2") # global atts for level 1 and level 2
    netcdf_lev2 = Dataset(lev2_name, 'w')

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
    t = netcdf_lev2.createVariable('time', 'i8','time') # seconds since
    t[:] = t_ind.values

    for att_name, att_val in time_atts.items(): netcdf_lev2['time'].setncattr(att_name,att_val)

    for var_name, var_atts in l2_atts.items():

        try:
            var_dtype = l2_data[var_name].dtype
        except KeyError as e:
            var = netcdf_lev2.createVariable(var_name, var_dtype, 'time')
            var[:] = t_ind.values*nan
            for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name].setncattr(att_name, att_desc)
            continue

        perc_miss = fl.perc_missing(l2_data[var_name])

        if fl.column_is_ints(l2_data[var_name]):
            var_dtype = np.int32
            fill_val  = def_fill_int
            l2_data[var_name] = l2_data[var_name].values.astype(np.int32)
        else:
            fill_val  = def_fill_flt

        if timestep != "1min":
            vtmp = l2_data[var_name].resample(fstr, label='left').apply(fl.take_average)
        else: vtmp = l2_data[var_name]
        vtmp.fillna(fill_val, inplace=True)

        var  = netcdf_lev2.createVariable(var_name, var_dtype, 'time')
        var[:] = vtmp

        # write atts to the var now
        for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name].setncattr(att_name, att_desc)
        netcdf_lev2[var_name].setncattr('missing_value', fill_val)

        max_val = np.nanmax(vtmp.values) # masked array max/min/etc
        min_val = np.nanmin(vtmp.values)
        avg_val = np.nanmean(vtmp.values)
        
        netcdf_lev2[var_name].setncattr('max_val', max_val)
        netcdf_lev2[var_name].setncattr('min_val', min_val)
        netcdf_lev2[var_name].setncattr('avg_val', avg_val)
        
        # add a percent_missing attribute to give a first look at "data quality"
        netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)

    netcdf_lev2.close() # close and write files for today
    q.put(True)

def write_turb_netcdf(turb_data, date, q):
    
    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    turb_atts, turb_cols = define_turb_variables()

    if turb_data.empty:
        print("... there was no turbulence data to write today {}".format(date))
        q.put(False)
        return

    # get some useful missing data information for today and print it for the user
    if not turb_data.empty: avg_missing = (1-turb_data.iloc[:,0].notnull().count()/len(turb_data.iloc[:,1]))*100.
    #fl.perc_missing(turb_data.iloc[:,0].values)
    else: avg_missing = 100.

    print("... writing turbulence data for on {}, ~{}% of data is present".format(date, 100-avg_missing))

    out_dir  = turb_dir
    file_str = '/mosflxtowerturb.level2.{}.{}.nc'.format(integ_time_turb_flux, date.strftime('%Y%m%d.%H%M%S'))

    turb_name  = '{}/{}'.format(out_dir, file_str)

    global_atts = define_global_atts("turb") # global atts for level 1 and level 2
    netcdf_turb = Dataset(turb_name, 'w') 

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
        netcdf_turb[var_name].setncattr('percent_missing', perc_miss)
        netcdf_turb[var_name].setncattr('missing_value', def_fill_flt)

    netcdf_turb.close() # close and write files for today
    q.put(True)
    
 
# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
