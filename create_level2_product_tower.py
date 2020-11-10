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

# Ephemeris
# SPA is NREL's (Ibrahim Reda's) emphemeris calculator that all those BSRN/ARM radiometer geeks use ;) 
# pvlib is NREL's photovoltaic library
from pvlib import spa 
    # .. [1] I. Reda and A. Andreas, Solar position algorithm for solar radiation
    #    applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.

    # .. [2] I. Reda and A. Andreas, Corrigendum to Solar position algorithm for
    #    solar radiation applications. Solar Energy, vol. 81, no. 6, p. 838,
    #    2007.

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


version_msg = '\n\nPS-122 MOSAiC Met Tower processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

def main(): # the main data crunching program

    # the date on which the first MOSAiC data was taken... there will be a "seconds_since" variable 
    global beginning_of_time, integ_time_turb_flux, win_len
    beginning_of_time    = datetime(1970,1,1,0,0,0) # Unix epoch, ARM convention
    integ_time_turb_flux = [10,30] # [minutes] the integration time for the turbulent flux calculation

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring

    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0

    # constants for calculations
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
    global data_dir, level1_dir, level2_dir, turb_dir, sonic_z, mast_sonic_height, licor_z # make data available
    data_dir   = args.path 
    level1_dir = data_dir+'MOSAiC/tower/1_level_ingest/'                  # where does level1 data live?
    level2_dir = data_dir+'MOSAiC_dump/tower/2_level_product_dev/'        # where does level2 data go
    turb_dir   = data_dir+'MOSAiC_dump/tower/2_level_product_dev/'        # where does level2 data go
    leica_dir  = data_dir+'MOSAiC/partner_data/AWI/polarstern/WXstation/' # this is where the ship track lives  
    
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
    
    # expand the load by 1 day to facilite gps processing    
    start_time = start_time-timedelta(1)
    end_time = end_time+timedelta(1)

    print('The first day of the experiment is:    %s' % beginning_of_time)
    print('The first day we  process data is:     %s' % str(start_time+timedelta(1)))
    print('The last day we will process data is:  %s' % str(end_time-timedelta(1)))
    printline()

    # thresholds! limits that can warn you about bad data!
    # these aren't used yet but should be used to warn about spurious data
    irt_targ          = (-80  ,5)    # IRT surface brightness temperature limits [Celsius]
    sr50d             = (1    ,2.5)  # distance limits from SR50 to surface [m]; install height -1 m or +0.5
    flxp              = (-120 ,120)  # minimum and maximum conductive heat flux (W/m2)
    T_thresh          = (-70  ,20)   # minimum & maximum air temperatures (C)
    rh_thresh         = (40   ,130)  # relative humidity (#)
    p_thresh          = (850  ,1100) # air pressure
    ws_thresh         = (0    ,27)   # wind speed from sonics (m/s)
    lic_co2sig_thresh = (94   ,105)  # rough estimate of minimum CO2 signal value corresponding to optically-clean window
    lic_h2o           = (0    ,500)  # Licor h2o [mol/m3]
    lic_co2           = (0    ,25)   # Licor co2 [mmol/m3]
    max_bad_paths     = (0.01 ,1)    # METEK: maximum [fraction] of bad paths allowed. (0.01 = 1%), but is
                                     # actually in 1/9 increments. This just says we require all paths to be usable.
    incl_range        = (-90  ,90)   # The inclinometer on the metek
    twr_alt_lim       = (-3.5,10.2)  # tower +/- 3sigma on the altitude data
    mst_alt_lim       = (-4.5,7.6)   # mast +/- 3sigma on the altitude data
    cd_lim            = (-2.3e-3,1.5e-2) # drag coefficinet sanity check. really it can't be < 0, but a small negative threshold allows for empiracally defined (from EC) 3 sigma noise distributed about 0.
    
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
    
    # mast gps height for ice alt calc
    twr_GPS_height_raised_precise = [(1.985)] # estimate of height above ice surface on 10/25 = 2.3 cm snow + 179 cm SR50 + 9 cm SR50 sensor len + 1.25 cm pipe rad + 6.9 cm gps height
    mst_GPS_height_raised_precise = [(0.799)] # 27 cm snow depth + 46 cm Hardigg box height + 6.9 cm gps height. the snow depth is and average of the two nearby (~5 m) obs, 17 and 37 cm; it was in a transiton into a drifted ridge
    
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

    # mast dates and headings w.r.t. tower from available notes and a deductions, assumptions
    # mast_hdg_dates map to mast_hdg_vals 1 to 1        
    # ccox made an effort, but without heights and with so many changes to the mast between 12/1 and 12/9, without notes the adjustments are arbitrarily set to match the 10 m data, which has not benefits. We can revisit later. I 'll leave it where I left off, a combination of my guesses adn Ola's notes.            
    mast_hdg_dates   = [datetime(2019,10,15,0,0)    , # Beginning of time; just a placeholder
                        datetime(2019,10,26,7,0)    , # Tower raised to 30 m; Ola's notes based on manual heading reading on 00:56:55 Oct 30, 2019
                        datetime(2019,11,18,12,50)  , # Tower falls down; Ola's notes
                        datetime(2019,11,28,4,30)   , # Sonic tests at 2 m; Ola's notes, says he's guessing. The results suggest there is a problem so some adjustments have been made
                        datetime(2019,11,29,0,0)    , # added by ccox based on comparison to early Dec, see above
                        datetime(2019,12,1,9,51),
                        datetime(2019,12,1,23,58),
                        datetime(2019,12,2,23,58),
                        datetime(2019,12,3,23,58),
                        datetime(2019,12,4,23,58),  
                        datetime(2019,12,5,23,58),  
                        datetime(2019,12,6,6,27), 
                        datetime(2019,12,8,0,0)     , # ccox
                        datetime(2019,12,8,12,42)   , # ccox
                        datetime(2019,12,8,14,1)    , # Not sure what is going on on 12/8-12/9, Ola's notes, says he's guessing
                        datetime(2019,12,9,0,0)     , # ccox 
                        datetime(2019,12,9,7,31)    , # Placeholder, see next line
                        datetime(2020,3,17,12,0)]     # Chris took a reading here. However, note that the tower and mast had ben separaated on 3/11 so this is difficult to interpret.
    
    mast_hdg_vals    = {'mast_hdg' : [nan, 40.7,  205.1, 205.1, 196.6, 268.6, 268.6, 276.1, 279.1, 282.6, 286.6, 104.1, 214.7, 291.2, 215, 193.9, 215, 228], # These are the manual readings at the mast. The final position could be replaced with 99.1 from 3/17 (first obs since Dec), but this was after teh 3/11 lead.
                        'gps_hdg'  : [nan, 290.7, 290.7, 291.2, 291.2, 281.7, 282.1, 284.2, 286.5, 288.9, 291.3, 291.9, 292.9, 290,   290, 290,   290, 291.3], # These are the manual readings at the tower when the mast obs were made. The final position could be replaced with 199.6 from 3/17 (first obs since Dec), but this was after teh 3/11 lead. Cox adjusted some using the values from thee filtered tower gps when the date of the reading (NOT the date of the change from mast_hdg_dates!) was recorded
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
    slow_data['mast_RH']        .loc[datetime(2019,11,26,12,14,0):datetime(2019,11,26,12,45,0)] = nan # bad data when turned back on after nov storm        
    slow_data['vaisala_T_2m']   .loc[datetime(2020,1,17,17,21,32):datetime(2020,1,19,11,55,0)] = nan # something unexplained here, need to remove it manually
    slow_data['vaisala_RH_2m']  .loc[datetime(2020,1,17,17,21,32):datetime(2020,1,19,11,55,0)] = nan # ditto
    slow_data['vaisala_P_2m']   .loc[datetime(2020,1,17,17,21,32):datetime(2020,1,19,11,55,0)] = nan # ditto
    slow_data['vaisala_Td_2m']   .loc[datetime(2020,1,17,17,21,32):datetime(2020,1,19,11,55,0)] = nan # ditto
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
    slow_data['mast_T']         .mask( (slow_data['mast_T']<-1) & (abs(slow_data['mast_T'])==0) , inplace=True)    
    slow_data['mast_RH']        .mask( (slow_data['mast_RH']<rh_thresh[0])   | (slow_data['mast_RH']>rh_thresh[1]) , inplace=True) # ppl
    slow_data['vaisala_RH_2m']  = fl.despike(slow_data['vaisala_RH_2m'],0.4,30,'yes') # replace spikes outside 0.4% over 30s median
    slow_data['vaisala_RH_6m']  = fl.despike(slow_data['vaisala_RH_6m'],0.4,30,'yes') # replace spikes outside 0.4% over 30s median
    slow_data['vaisala_RH_10m']  = fl.despike(slow_data['vaisala_RH_10m'],0.4,30,'yes') # replace spikes outside 0.4% over 30s median

    # When the tower was powered back on after being off, the (heated) RH sensor needed to warm and equillibrate. The equillibration period is 15-30 min and has a characteristic shape:
    # when the tower turns on the RH starts ver low, increases very high then falls back to the accurate value. Instead of automating a screening procedure I just mannually screened
    # the RH data. 
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,10,19,5,56,0):datetime(2019,10,19,6,6,0)] = nan

    slow_data['vaisala_RH_2m']   .loc[datetime(2019,10,19,6,52,0):datetime(2019,10,19,6,53,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,18,11,11,0):datetime(2019,11,18,11,13,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,18,11,11,0):datetime(2019,11,18,11,13,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,18,11,11,0):datetime(2019,11,18,11,13,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,19,3,59,0):datetime(2019,11,19,4,26,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,19,3,59,0):datetime(2019,11,19,4,26,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,19,3,59,0):datetime(2019,11,19,4,26,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,19,11,16,0):datetime(2019,11,19,11,20,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,19,11,16,0):datetime(2019,11,19,11,20,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,19,11,16,0):datetime(2019,11,19,11,20,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,20,8,39,0):datetime(2019,11,20,8,55,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,20,8,39,0):datetime(2019,11,20,8,55,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,20,8,39,0):datetime(2019,11,20,8,55,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,20,9,50,0):datetime(2019,11,20,9,56,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,20,9,50,0):datetime(2019,11,20,9,56,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,20,9,50,0):datetime(2019,11,20,9,56,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,21,4,5,0):datetime(2019,11,21,4,16,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,21,4,5,0):datetime(2019,11,21,4,16,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,21,4,5,0):datetime(2019,11,21,4,16,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,21,11,23,0):datetime(2019,11,21,11,34,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,21,11,23,0):datetime(2019,11,21,11,34,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,21,11,23,0):datetime(2019,11,21,11,34,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,23,4,16,0):datetime(2019,11,23,4,30,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,23,4,16,0):datetime(2019,11,23,4,30,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,23,4,16,0):datetime(2019,11,23,4,30,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,23,11,11,0):datetime(2019,11,23,11,33,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,23,11,11,0):datetime(2019,11,23,11,33,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,23,11,11,0):datetime(2019,11,23,11,33,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,25,4,51,0):datetime(2019,11,25,4,59,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,25,4,51,0):datetime(2019,11,25,4,59,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,25,4,51,0):datetime(2019,11,25,4,59,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,25,9,34,0):datetime(2019,11,25,9,54,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,25,9,34,0):datetime(2019,11,25,9,54,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,25,9,34,0):datetime(2019,11,25,9,54,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,26,5,36,0):datetime(2019,11,26,6,0,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,26,5,36,0):datetime(2019,11,26,6,0,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,26,5,36,0):datetime(2019,11,26,6,0,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,27,4,55,0):datetime(2019,11,27,5,44,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,27,4,55,0):datetime(2019,11,27,5,44,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,27,4,55,0):datetime(2019,11,27,5,44,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,28,4,35,0):datetime(2019,11,28,4,48,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,28,4,35,0):datetime(2019,11,28,4,48,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,28,4,35,0):datetime(2019,11,28,4,48,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,11,28,12,11,0):datetime(2019,11,28,12,37,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,11,28,12,11,0):datetime(2019,11,28,12,37,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,11,28,12,11,0):datetime(2019,11,28,12,37,0)] = nan
    
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,12,4,6,0,0):datetime(2019,12,4,11,8,0)] = nan
    
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,12,5,6,5,0):datetime(2019,12,5,6,7,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,12,10,7,17,0):datetime(2019,12,10,7,43,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,12,10,7,17,0):datetime(2019,12,10,7,43,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,12,10,7,17,0):datetime(2019,12,10,7,43,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2019,12,11,8,4,0):datetime(2019,12,11,8,29,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2019,12,11,8,4,0):datetime(2019,12,11,8,29,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2019,12,11,8,4,0):datetime(2019,12,11,8,29,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,1,15,7,53,0):datetime(2020,1,15,8,18,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,1,15,7,53,0):datetime(2020,1,15,8,18,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,1,15,7,53,0):datetime(2020,1,15,8,18,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,2,13,7,59,0):datetime(2020,2,13,8,27,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,2,13,7,59,0):datetime(2020,2,13,8,27,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,2,13,7,59,0):datetime(2020,2,13,8,27,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,3,11,17,33,0):datetime(2020,3,11,18,1,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,3,11,17,33,0):datetime(2020,3,11,18,1,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,3,11,17,33,0):datetime(2020,3,11,18,1,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,3,12,9,50,0):datetime(2020,3,12,12,2,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,3,12,9,50,0):datetime(2020,3,12,10,26,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,3,12,9,50,0):datetime(2020,3,12,10,26,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,3,23,23,57,0):datetime(2020,3,24,0,23,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,3,23,23,57,0):datetime(2020,3,24,0,23,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,3,23,23,57,0):datetime(2020,3,24,0,23,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,4,2,13,58,0):datetime(2020,4,2,14,26,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,4,2,13,58,0):datetime(2020,4,2,14,26,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,4,2,13,58,0):datetime(2020,4,2,14,26,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,4,4,9,13,0):datetime(2020,4,4,9,38,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,4,4,9,13,0):datetime(2020,4,4,9,38,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,4,4,9,13,0):datetime(2020,4,4,9,38,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,4,7,15,42,0):datetime(2020,4,7,16,10,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,4,7,15,42,0):datetime(2020,4,7,16,10,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,4,7,15,42,0):datetime(2020,4,7,16,10,0)] = nan
    
    slow_data['vaisala_RH_2m']   .loc[datetime(2020,4,20,8,43,0):datetime(2020,4,20,8,46,0)] = nan
    slow_data['vaisala_RH_6m']   .loc[datetime(2020,4,20,8,43,0):datetime(2020,4,20,8,46,0)] = nan
    slow_data['vaisala_RH_10m']  .loc[datetime(2020,4,20,8,43,0):datetime(2020,4,20,8,46,0)] = nan
    
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
    pmast.fillna(slow_data['vaisala_P_2m']-1*mast_params['mast_sonic_heights'][mast_index]/10)

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
    slow_data['apogee_body_T'].mask( (slow_data['apogee_body_T']<irt_targ[0]) | (slow_data['apogee_body_T']>irt_targ[1]) , inplace=True) # ppl
    slow_data['apogee_targ_T'].mask( (slow_data['apogee_targ_T']<irt_targ[0]) | (slow_data['apogee_targ_T']>irt_targ[1]) , inplace=True) # ppl
    slow_data['apogee_body_T'].mask( (slow_data['vaisala_T_2m']<-1) & (abs(slow_data['apogee_body_T'])==0) , inplace=True) # reports spurious 0s sometimes
    slow_data['apogee_targ_T'].mask( (slow_data['vaisala_T_2m']<-1) & (abs(slow_data['apogee_targ_T'])==0) , inplace=True) # reports spurious 0s sometimes
    slow_data['apogee_body_T']  = fl.despike(slow_data['apogee_body_T'],2,60,'yes') # replace spikes outside 2C over 60 sec with 60 s median
    slow_data['apogee_targ_T']  = fl.despike(slow_data['apogee_targ_T'],2,60,'yes') # replace spikes outside 2C over 60 sec with 60 s median
    slow_data['apogee_targ_T']  .loc[:datetime(2019,10,15,7,54)] = nan
    slow_data['apogee_body_T']  .loc[:datetime(2019,10,15,7,54)] = nan

    # GPS QC etc.
    slow_data['tower_lat']     = slow_data['gps_lat_deg']+slow_data['gps_lat_min']/60.0 # add decimal values
    slow_data['tower_lon']     = slow_data['gps_lon_deg']+slow_data['gps_lon_min']/60.0
    slow_data['tower_heading'] = slow_data['gps_hdg']/100.0  # convert to degrees
    slow_data['tower_heading'] = slow_data['tower_heading'].where(~np.isinf(slow_data['tower_heading'])) # infinities->nan
    slow_data['gps_alt']       = slow_data['gps_alt']/1000.0 # convert to meters
    slow_data['gps_alt'].mask( (slow_data['gps_alt']<twr_alt_lim[0]) | (slow_data['gps_alt']>twr_alt_lim[1]) , inplace=True) # stat lims
    slow_data['tower_lat'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4) , inplace=True) 
    slow_data['tower_lon'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4), inplace=True) 
    slow_data['gps_alt'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4), inplace=True) 
    slow_data['tower_heading'].mask( (slow_data['gps_qc']==0) | (slow_data['gps_hdop']>4), inplace=True) 
    slow_data['tower_ice_alt'] = slow_data['gps_alt'] - twr_GPS_height_raised_precise 
    
    if 'mast_RECORD' in slow_data:
        slow_data['mast_lat']     = slow_data['mast_gps_lat_deg_Avg']+slow_data['mast_gps_lat_min_Avg']/60.0 # add decimal values
        slow_data['mast_lon']     = slow_data['mast_gps_lon_deg_Avg']+slow_data['mast_gps_lon_min_Avg']/60.0
        slow_data['mast_heading'] = slow_data['mast_gps_hdg_Avg']/100.0  # convert to degrees
        slow_data['mast_gps_alt'] = slow_data['gps_alt']/1000.0 # convert to meters
        slow_data['mast_heading'] = slow_data['mast_heading'].where(~np.isinf(slow_data['mast_heading'])) # infinities->nan
        slow_data['mast_gps_alt'].mask( (slow_data['mast_gps_alt']<mst_alt_lim[0]) | (slow_data['mast_gps_alt']>mst_alt_lim[1]) , inplace=True) # stat lims
        slow_data['mast_lat'].mask( (slow_data['mast_gps_qc']==0) | (slow_data['mast_gps_hdop_Avg']>4) , inplace=True) 
        slow_data['mast_lon'].mask( (slow_data['mast_gps_qc']==0) | (slow_data['mast_gps_hdop_Avg']>4), inplace=True) 
        slow_data['mast_gps_alt'].mask( (slow_data['mast_gps_qc']==0) | (slow_data['mast_gps_hdop_Avg']>4), inplace=True) 
        slow_data['mast_heading'].mask( (slow_data['mast_gps_qc']==0) | (slow_data['mast_gps_hdop_Avg']>4), inplace=True) 
        slow_data['mast_ice_alt'] = slow_data['mast_gps_alt'] - mst_GPS_height_raised_precise 

    # The heading/alt from the v102 is "noisey" at regular frequencies, about ~1, 2.1, 6.4, 12.8 hours. I've considered several approaches: wavelet frequency rejection,
    # various band-pass filters, Kalman filter, tower->ais bearing baseline. Median filter works the best. Because the lowest nosie frequency is near 12 hours, a
    # 24 hour filter is needed. I have implemented a 1 day buffer on the start_time, end_time for this. For missing data we forward pad to reduce edge effects but report
    # nan in the padded space.
    print('... band-pass median filter applied to heading') 
    # 
    tmph =  slow_data['tower_heading'].interpolate(method='pad').rolling(86400,min_periods=1,center=True).median()
    tmph.mask(slow_data['tower_heading'].isna(),inplace=True)
    slow_data['tower_heading'] = tmph
    tmpa = slow_data['tower_ice_alt'].interpolate(method='pad').rolling(86400,min_periods=1,center=True).median()
    tmpa.mask(slow_data['tower_ice_alt'].isna(),inplace=True)
    slow_data['tower_ice_alt'] = tmpa
    slow_data['tower_heading']   .loc[:datetime(2019,10,24,4,59,49)] = nan # this is a couple hours ater the gps was calibrated and mounted and is when the data looks ok
    if 'mast_RECORD' in slow_data:
        tmph = slow_data['mast_heading'].rolling(86400,min_periods=1,center=True).median()
        tmph.mask(slow_data['mast_heading'].isna(),inplace=True)
        slow_data['mast_heading'] = tmph
        slow_data['mast_heading'] = np.mod(slow_data['mast_heading'],360)
        tmpa = slow_data['mast_ice_alt'].interpolate(method='pad').rolling(86400,min_periods=1,center=True).median()
        tmpa.mask(slow_data['mast_ice_alt'].isna(),inplace=True)
        slow_data['mast_ice_alt'] = tmpa
        
    slow_data['tower_ice_alt'].loc[:raise_day] = nan # not very useful before the tower is up
    slow_data['tower_heading'].loc[:raise_day] = nan # ditto

    # Get the bearing on the ship 
    # Load the ship track and reindex to slow_data, calculate distance [m] and bearing [deg from tower rel to true north, as wind direction]
    ship_df = pd.read_csv(leica_dir+'Leica_Sep20_2019_Oct01_2020_clean.dat',sep='\s+',parse_dates={'date': [0,1]}).set_index('date')          
    ship_df.columns = ['u1','lon_ew','latd','latm','lond','lonm','u2','u3','u4','u5','u6','u7']
    ship_df['lat']=ship_df['latd']+ship_df['latm']/60
    ship_df['lat'].mask(ship_df['lat'] == 9+9/60, inplace=True) # 9 is a missing value in the original file. when combined from above line 9+9/60=9.15 is the new missing data
    ship_df['lon']=ship_df['lond']+ship_df['lonm']/60
    ship_df['lon'].mask(ship_df['lon'] == 9+9/60, inplace=True) # 9 is a missing value in the original file. when combined from above line 9+9/60=9.15 is the new missing data 
    ship_df['lon'] = ship_df['lon']*ship_df['lon_ew'] # deg west will be negative now
    ship_df=ship_df.reindex(slow_data.index).interpolate()
    slow_data['ship_distance']=fl.distance(slow_data['tower_lat'],slow_data['tower_lon'],ship_df['lat'],ship_df['lon'])*1000
    slow_data['ship_bearing']=fl.calculate_initial_angle(slow_data['tower_lat'],slow_data['tower_lon'],ship_df['lat'],ship_df['lon']) 
    slow_data['ship_distance'].mask( (slow_data['ship_distance']>700), inplace=True)
    slow_data['ship_bearing'].loc[datetime(2020,3,9,0,0,0):datetime(2020,3,10,0,0,0)].mask( (slow_data['ship_bearing']>326), inplace=True) # something breaks in the trig model briefly. its weird. i'll just screen it out
    slow_data['ship_distance'].loc[datetime(2020,3,9,0,0,0):datetime(2020,3,10,0,0,0)].mask( (slow_data['ship_distance']>370), inplace=True) # something breaks in the trig model briefly. its weird. i'll just screen it out

    # Ephemeris
    # set it up
    utime_in = np.array(slow_data.index.astype(np.int64)/10**9)                                              # unix time. sec since 1/1/70
    lat_in   = slow_data['tower_lat']                                                                        # latitude
    lon_in   = slow_data['tower_lon']                                                                        # latitude
    elv_in   = np.zeros(slow_data.index.size)+2                                                              # the elvation shall be 2 m...the details are negligible
    pr_in    = slow_data['vaisala_P_2m'].fillna(slow_data['vaisala_P_2m'].median())                          # mb 
    t_in     = slow_data['vaisala_T_2m'].fillna(slow_data['vaisala_T_2m'].median())                          # degC
    
    atm_ref  = ( 1.02 * 1/np.tan(np.deg2rad(0+(10.3/(0+5.11)))) ) * pr_in/1010 * (283/(273.15+t_in))/60      # est of atm ref at sunrise/set following U. S. Naval Observatory's Vector Astrometry Software @ wikipedia https://en.wikipedia.org/wiki/Atmospheric_refraction. This really just sets a flag for when to apply the refraction adjustment. 
    delt_in  = spa.calculate_deltat(slow_data.index.year, slow_data.index.month)                             # seconds. delta_t between terrestrial and UT1 time
    # do the thing
    app_zenith, zenith, app_elevation, elevation, azimuth, eot = spa.solar_position(utime_in,lat_in,lon_in,elv_in,pr_in,t_in,delt_in,atm_ref)
    # write it out
    slow_data['sza_true'] = zenith
    slow_data['sza_app']  = app_zenith 
    slow_data['azimuth']  = azimuth 

    # in matlab, there were rare instabilities in the Reda and Andreas algorithm that resulted in spikes (a few per year). no idea if this is a problem in the python version, but lets make sure
    slow_data['sza_true'] = fl.despike(slow_data['sza_true'],2,5,'no')
    slow_data['sza_app'] = fl.despike(slow_data['sza_app'],2,5,'no')
    slow_data['azimuth'] = fl.despike(slow_data['azimuth'],2,5,'no')

    # rename columns to match expected level2 names from data_definitions, there's probably a more clever way to do this
    slow_data.rename(inplace=True, columns =\
                     {
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

    day_series = pd.date_range(start_time+timedelta(1), end_time-timedelta(1))    # we're going to loop over these days. timedelta because the input expanded 11 day on either side to facilitatte smoothing gps
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    for today in day_series: # loop over the days in the processing range
        tomorrow  = today+day_delta
        Hz10_today        = pd.date_range(today-pd.Timedelta(1,'hour'), tomorrow+pd.Timedelta(1,'hour'), freq='0.1S') # all the 0.1 seconds today, for obs. we buffer by 1 hr for easy of po2 in turbulent fluxes below
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
        raw_licor_data['licor_pr'] = raw_licor_data['licor_pr']*10 # [to hPa]

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
                
                
            # Some time periods have to be removed. In particular, the first week of Dec. It is a mess. 
            # The sonic was rotated over and over and I don't have any notes. I will also remove the set up in April
            if 'mast' in inst:
                # The April setup
                raw_fast_data[inst][inst+'_T'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                raw_fast_data[inst][inst+'_x'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                raw_fast_data[inst][inst+'_y'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                raw_fast_data[inst][inst+'_z'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                # The Dec re-setup
                raw_fast_data[inst][inst+'_T'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                raw_fast_data[inst][inst+'_x'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                raw_fast_data[inst][inst+'_y'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                raw_fast_data[inst][inst+'_z'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                


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
            if inst != 'metek_mast': 
                bad_data = (raw_fast_data[inst][inst+'_heatstatus']/1000\
                            -np.floor(raw_fast_data[inst][inst+'_heatstatus']/1000)) >  max_bad_paths[0]
                raw_fast_data[inst][inst+'_x'].mask(bad_data, inplace=True)
                raw_fast_data[inst][inst+'_y'].mask(bad_data, inplace=True)
                raw_fast_data[inst][inst+'_z'].mask(bad_data, inplace=True)
                raw_fast_data[inst][inst+'_T'].mask(bad_data, inplace=True)
            elif inst == 'metek_mast':
                raw_fast_data[inst][inst+'_x'].loc[datetime(2020,4,20,4,0,0):datetime(2020,4,22,0,0,0)] = nan # not sure what happened here, but I'm guessing icing following the melt
                raw_fast_data[inst][inst+'_y'].loc[datetime(2020,4,20,4,0,0):datetime(2020,4,22,0,0,0)] = nan
                raw_fast_data[inst][inst+'_z'].loc[datetime(2020,4,20,4,0,0):datetime(2020,4,22,0,0,0)] = nan

        #
        # And now Licor ####################################################
        # Physically-possible limits
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
        raw_licor_data['licor_co2'].mask( (co2_str<lic_co2sig_thresh[0]),  inplace=True)
        raw_licor_data['licor_h2o'].mask( (co2_str<lic_co2sig_thresh[0]),  inplace=True)
        
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
        print("... cartesian tilt rotation. Translating body -> earth coordinates.")
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

        for inst in metek_inst_keys:
            
            # Tower.
            # If we are working with the tower sonics, the calculation is straightforward. 
            # Inclinomters and heading used to rotate from body to earth coordinates
            # Heading uses a filtered value to reduce noise, which was calculated earlier in this code
            if 'mast' not in inst:
                ct_u, ct_v, ct_w = fl.tilt_rotation(fast_data_10hz[inst] [inst+'_incy'],
                                                    fast_data_10hz[inst] [inst+'_incx'],
                                                    logger_today['tower_heading'].reindex(index=fast_data_10hz[inst].index).interpolate(),
                                                    fast_data_10hz[inst] [inst+'_y'], # y -> u on uSonic!
                                                    fast_data_10hz[inst] [inst+'_x'], # x -> v on uSonic!
                                                    fast_data_10hz[inst] [inst+'_z'])
                
            # Mast.
            # Three eras: ~ Leg 1, Leg 2 and Leg 3 with some additional complexities in Leg 1.        
            elif 'mast' in inst:
                
                # This is Leg 1 and 2.
                #   We use information available and interpolate between.
                if today < datetime(2020,4,14,0,0):   
                    # interpolate the mast alignment metadata for today
                    most_recent_gps = mast_hdg_df['gps_hdg'].reindex(index=fast_data_10hz[inst].index,method='pad')
                    most_recent_mast = mast_hdg_df['mast_hdg'].reindex(index=fast_data_10hz[inst].index,method='pad')
                    mast_align = most_recent_gps - most_recent_mast   
                    if today >  mast_hdg_df.index[-2]: # if we are in leg 1 pad, but lineraly interp thru leg 2
                        meth = 'linear'
                    else:
                        meth = 'pad' 
                           
                    mast_hdg_series = np.mod(logger_today['tower_heading'].reindex(index=fast_data_10hz[inst].index).interpolate()-mast_align,360)                    

                    # if we are working on the mast but we don't have a v102 we have to set to missing values, although we can report our estiamte of the heading
                    logger_today['mast_lat']=np.zeros(len(logger_today['tower_lat']))+def_fill_flt 
                    logger_today['mast_lon']=np.zeros(len(logger_today['tower_lon']))+def_fill_flt 
                    logger_today['mast_ice_alt']=np.zeros(len(logger_today['tower_ice_alt']))+def_fill_flt 
                    logger_today['mast_heading']=mast_hdg_series.reindex(index=seconds_today)
                
                # This is the Newdle in Leg 3. 
                #   A "spare" v102 was used so the heading is tracked directly. 
                #   The mast and tower are not on the same piece of ice, so that tower cannot be used as reference for the mast at all.    
                elif today > datetime(2020,4,14,0,0) and today < datetime(2020,5,12,0,0):             
                    # set to 68.5 from calcs416.py 
                    mast_align = 68.5
                    mast_hdg_series = np.mod(logger_today['mast_heading'].reindex(index=fast_data_10hz[inst].index).interpolate()-mast_align,360) 
                    # also, set the heading for the file
                    logger_today['mast_heading'] = np.mod(logger_today['mast_heading']-mast_align,360)
                
                # leg 4 and 5 the mast stays packed away safely in cold storage
                else:
                     mast_hdg_series = fast_data_10hz[inst]['metek_mast_T']*nan
                    
                # No inclinometer up here. For now we are assuming it is plum
                nmastvals = len(fast_data_10hz[inst])
                ct_u, ct_v, ct_w = fl.tilt_rotation(np.zeros(nmastvals),
                                                    np.zeros(nmastvals),
                                                    mast_hdg_series,
                                                    fast_data_10hz[inst][inst+'_x'], # x -> u on USA-1!
                                                    fast_data_10hz[inst][inst+'_y'], # y -> v on USA-1!
                                                    fast_data_10hz[inst][inst+'_z'])

            # reassign corrected vals
            fast_data_10hz[inst][inst+'_y'] = ct_u
            fast_data_10hz[inst][inst+'_x'] = ct_v
            fast_data_10hz[inst][inst+'_z'] = ct_w

            # start referring to xyz as uvw now (maybe we should keep both?)
            fast_data_10hz[inst].rename(columns={inst+'_y' : inst+'_u',
                                                 inst+'_x' : inst+'_v',
                                                 inst+'_z' : inst+'_w',
                                                 }, errors="raise", inplace=True) 

        # Now we recalculate the 1 min average wind direction and speed from the u and v velocities in meteorological  convention
        print("... calculating a corrected set of slow wind speed and direction.")
        metek_ws = {}
        metek_wd = {}
        for inst in metek_inst_keys:
            u_min = fast_data_10hz[inst] [inst+'_u'].resample('1T',label='left').apply(fl.take_average)
            v_min = fast_data_10hz[inst] [inst+'_v'].resample('1T',label='left').apply(fl.take_average)
            ws = np.sqrt(u_min**2+v_min**2)
            wd = np.mod((np.arctan2(-v_min,-u_min)*180/np.pi),360)
            metek_ws[inst] = ws
            metek_wd[inst] = wd

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
        licor_stats['pr_licor']         = licor_10hz['licor_pr']      .resample('1T',label='left').mean()
        licor_stats['pr_licor'][(licor_10hz['licor_pr']*0+1).resample('1T',label='left').sum() < 300] = nan        
        licor_stats['co2_signal_licor'] = licor_10hz['licor_co2_str'] .resample('1T',label='left').mean()
        licor_stats['co2_signal_licor'][(licor_10hz['licor_co2_str']*0+1).resample('1T',label='left').sum() < 300] = nan 

        # now put it all together
        stats_data = pd.DataFrame()
        for inst in metek_inst_keys:
            stats_data = pd.concat(  [stats_data, metek_stats[inst]], axis=1)
        stats_data = pd.concat(  [stats_data, licor_stats], axis=1 )
        stats_data = stats_data[today:tomorrow]
 
        # ~~~~~~~~~~~~~~~~~~~~ (6) Flux Capacitor  ~~~~~~~~~~~~~~~~~~~~~~~~~
        verboseprint('... calculating turbulent fluxes and associated MO parameters')
        # Rotation to the streamline, FFT window segmentation, detrending,
        # hamming, and computation of power [welch] & cross spectral densities,
        # covariances and associated diagnostics, as well as derived
        # variables (fluxes and stress parameters) are performed within a
        # sub-function called below.
        #
        # turbulence_data = fl.grachev_fluxcapacitor(sz, sonic_data, licor_data, h2o_units, co2_units, p, t, q, verbose=v)
        #       sz = instrument height
        #       sonic_data = dataframe of u,v,w winds
        #       licor_data = dataframe of h2o adn co2
        #       h2o_units = units of licor h2o, e.g., 'mmol/m3'
        #       co2_units = units of licor co2, e.g., 'mmol/m3'
        #       p = pressure in hPa, scaler
        #       t = air temperature in C, scaler
        #       q = vapor mixing ratio, scaler
        for win_len in range(0,len(integ_time_turb_flux)):
            turb_data = pd.DataFrame()    
            flux_freq = '{}T'.format(integ_time_turb_flux[win_len])
            flux_time_today = pd.date_range(today, today+timedelta(1), freq=flux_freq)
            suffix_list = ['_2m','_6m','_10m','_mast'] # suffix for vars in turb file
            # a DatetimeIndex based on integ_time_turb_flux, the integration window
            # for the calculations that is defined at the top  of the code
            for i_inst, inst in enumerate(metek_inst_keys):
                verboseprint("... processing turbulence data for {}".format(inst))
                for time_i in range(0,len(flux_time_today)-1): # flux_time_today = 
                    # Get the index, ind, of the metek frame that pertains to the present calculation 
                   # inds = (fast_data_10hz[inst].index >= flux_time_today[time_i]) \
                   #        & \
                   #        (fast_data_10hz[inst].index < flux_time_today[time_i+1]) 
                           
                    # Get the index, ind, of the metek frame that pertains to the present calculation 
                    # A little tricky. We need to make sure we give it enough data to encompass the nearest power of 2: for 30 min fluxes this is ~27 min so you are good, but for 10 min fluxes it is 13.6 min so you need to give it more. 
                    # We buffered the 10 Hz so that we can go outside the edge of "today" by up to an hour. It's a bit of a formality, but for general cleanliness we are going to center all fluxes to the nearest min so that e.g,
                    # 12:00-12:10 is actually 11:58 through 12:12
                    # 12:00-12:30 is actually 12:01 through 12:28   
                    po2_len = np.ceil(2**round(np.log2(integ_time_turb_flux[win_len]*60*10))/10/60) # @10Hz,# min needed to cover the nearet po2 [minutes]
                    t_win = pd.Timedelta((po2_len-integ_time_turb_flux[win_len])/2,'minutes')
                    calc_data = fast_data_10hz[inst].loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].copy()
                    
                    # get the licor data. we will just pass it through for every height as a placeholder, but only save the output for the right height. the decision doesnt need to be in the loop, but at least it is findable
                    licor_data = licor_10hz.loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].copy()  
                    if licor_z > 8: 
                        use_this_licor = suffix_list[2]
                    if licor_z > 4 and licor_z < 8: 
                        use_this_licor = suffix_list[1] 
                    if licor_z < 4: 
                        use_this_licor = suffix_list[0]

                    # we need pressure and temperature
                    # these are just for calculation of constants so the 2m data should be close enough...the original code assumed a nominal pressure and used sonic temperature...
                    Pr_time_i = slow_data['pressure_vaisala_2m'].loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].mean()
                    T_time_i = slow_data['temp_vaisala_2m'].loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].mean()
                    Q_time_i = slow_data['MR_vaisala_2m'].loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].mean()/1000
                                                  
                    # make the turbulent flux calculations via Grachev module
                    v = False
                    if args.verbose: v = True;
    
                    # give generic names for calculations and select the desired indexes
                    calc_data.rename(columns={inst+'_u' : 'u',
                                        inst+'_v' : 'v',
                                        inst+'_w' : 'w',
                                        inst+'_T' : 'T',
                                        }, errors="raise", inplace=True)
                    if 'mast' not in inst: sz = sonic_z[0][i_inst]
                    else: sz = mast_sonic_height
                    data = fl.grachev_fluxcapacitor(sz, calc_data, licor_data, 'mmol/m3', 'mmol/m3', Pr_time_i, T_time_i, Q_time_i, verbose=v)
                    data[:].mask( (data['Cd'] < cd_lim[0])  | (data['Cd'] > cd_lim[1]) , inplace=True) # # Sanity check on Cd. Ditch the whole run if it fails
                    data = data.add_suffix(suffix_list[i_inst])                                        
                    if time_i == 0: # doubtless there is a better way to initialize this
                        inst_data = data
                    else:
                        inst_data = inst_data.append(data)
    
                # now add the indexer datetime doohicky
                verboseprint("... concatting turbulence calculations to one dataframe")
                inst_data.index = flux_time_today[0:-1]
                turb_data = pd.concat( [turb_data, inst_data], axis=1) # concat columns alongside each other without adding indexes
                
                # ugh. there are 2 dimensions to the spectral variables, but the spectra are smoothed. The smoothing routine is a bit strange in that is is dependent
                # on the length of the window (to which it should be orthogonal!) and worse, is not obviously predictable...it groes in a for loop nested in a while 
                # loop that is seeded by a counter and limited by half the length of the window, but the growth is not entirely predictable and neither is the result
                # so I can't preallocate the frequency vector. I need to talk to Andrey about this and I need a programatic solution to assigning a frequency dimension
                # when pandas actually treats that dimension indpendently along the time dimension. I will search the data frame for instances of a frequency dim then assign
                # times without it nan of that length. for days without a frequency dim I will assign it to be length of 2 arbitrarily so that the netcdf can be written. This
                # is ugly.
    
                # (1) figure out the length of the freq dim and how many times are missing. also, save the frequency itself or you will write that vector as nan later on...
                missing_f_dim_ind = []
                f_dim_len = 1 
                for ii in range(0, np.array(turb_data['fs'+suffix_list[i_inst]]).size):
                    len_var = np.array(turb_data['fs'+suffix_list[i_inst]][ii]).size
                    if len_var == 1:
                        missing_f_dim_ind.append(ii)
                    else:
                        f_dim_len = len_var
                        fs = turb_data['fs'+suffix_list[i_inst]][ii]
                                             
                # (2) if missing times were found, fill with nans of the freq length you discovered. this happens on days when the instruents are turned on and also perhaps runs when missing data meant the flux_capacitor returned for lack of inputs
                if f_dim_len > 1 and not not missing_f_dim_ind: # omg, double negatives...python is so absurd. it didn't understand "is" so missing_f_dim_ind is not not a thing will have to do
                    for ii in range(0,len(missing_f_dim_ind)):
                        # these are the array with multiple dims...
                        # im filling the ones that are missing with nan (of fs in the case of fs...) such that they can form a proper and square array for the netcdf
                        turb_data['fs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs
                        turb_data['sus'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['svs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['sws'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['sTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['sqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['scs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cwus'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cwvs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cwTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cuTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cvTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cwqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cuqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cvqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cwcs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cucs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cvcs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                        turb_data['cuvs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan

            # now reassign the naming convention for the licor stuff
            turb_data['Hl'] = turb_data['Hl'+use_this_licor]
            turb_data['Hl_Webb'] = turb_data['Hl_Webb'+use_this_licor]
            turb_data['CO2_flux'] = turb_data['CO2_flux'+use_this_licor]
            turb_data['CO2_flux_Webb'] = turb_data['CO2_flux_Webb'+use_this_licor]
            turb_data['nSq'] = turb_data['nSq'+use_this_licor]
            turb_data['nSc'] = turb_data['nSc'+use_this_licor]
            turb_data['wq_csp'] = turb_data['wq_csp'+use_this_licor]
            turb_data['uq_csp'] = turb_data['uq_csp'+use_this_licor]
            turb_data['vq_csp'] = turb_data['vq_csp'+use_this_licor]
            turb_data['wc_csp'] = turb_data['wc_csp'+use_this_licor]
            turb_data['uc_csp'] = turb_data['uc_csp'+use_this_licor]
            turb_data['vc_csp'] = turb_data['vc_csp'+use_this_licor]
            turb_data['sqs'] = turb_data['sqs'+use_this_licor]
            turb_data['scs'] = turb_data['scs'+use_this_licor]
            turb_data['cwqs'] = turb_data['cwqs'+use_this_licor]
            turb_data['cuqs'] = turb_data['cuqs'+use_this_licor]
            turb_data['cvqs'] = turb_data['cvqs'+use_this_licor]
            turb_data['cwcs'] = turb_data['cwcs'+use_this_licor]
            turb_data['cucs'] = turb_data['cucs'+use_this_licor]
            turb_data['cvcs'] = turb_data['cvcs'+use_this_licor]
            turb_data['Deltaq'] = turb_data['Deltaq'+use_this_licor]
            turb_data['Kurt_q'] = turb_data['Kurt_q'+use_this_licor]
            turb_data['Kurt_wq'] = turb_data['Kurt_wq'+use_this_licor]
            turb_data['Kurt_uq'] = turb_data['Kurt_uq'+use_this_licor]
            turb_data['Skew_q'] = turb_data['Skew_q'+use_this_licor]
            turb_data['Skew_wq'] = turb_data['Skew_wq'+use_this_licor]
            turb_data['Skew_uq'] = turb_data['Skew_uq'+use_this_licor]
            turb_data['Deltac'] = turb_data['Deltac'+use_this_licor]
            turb_data['Kurt_c'] = turb_data['Kurt_c'+use_this_licor]
            turb_data['Kurt_wc'] = turb_data['Kurt_wc'+use_this_licor]
            turb_data['Kurt_uc'] = turb_data['Kurt_uc'+use_this_licor]
            turb_data['Skew_c'] = turb_data['Skew_c'+use_this_licor]
            turb_data['Skew_wc'] = turb_data['Skew_wc'+use_this_licor]
            turb_data['Skew_uc'] = turb_data['Skew_uc'+use_this_licor] 
            
            # select a freq vector 
            if not turb_data['fs_2m'].isnull().all():
                turb_data['fs'] = turb_data['fs_2m']
            elif not turb_data['fs_6m'].isnull().all():
                turb_data['fs'] = turb_data['fs_6m']
            elif not turb_data['fs_10m'].isnull().all():
                turb_data['fs'] = turb_data['fs_10m']
            else:
                turb_data['fs'] = nan    
                 
    
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
            bulk_input['u']  = ws[seconds_today]                                               # wind speed                         (m/s)
            bulk_input['ts'] = tsfc                                             # bulk water/ice surface tempetature (degC) this needs to be corrected for reflected
            bulk_input['t']  = slow_data['temp_vaisala_10m'][seconds_today]     # air temperature                    (degC) 
            bulk_input['Q']  = slow_data['MR_vaisala_10m'][seconds_today]/1000  # air moisture mixing ratio          (kg/kg)
            bulk_input['zi'] = empty_data+600                                   # inversion height                   (m) wild guess
            bulk_input['P']  = slow_data['pressure_vaisala_2m'][seconds_today]  # surface pressure                   (mb)
            bulk_input['zu'] = empty_data+10                                    # height of anemometer               (m)
            bulk_input['zt'] = empty_data+10                                    # height of thermometer              (m)
            bulk_input['zq'] = empty_data+10                                    # height of hygrometer               (m)      
            bulk_input = bulk_input.resample(str(integ_time_turb_flux[win_len])+'min',label='left').apply(fl.take_average)
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
                        if bulkout[13] < cd_lim[0] or bulkout[13] > cd_lim[1]:  # Sanity check on Cd. Ditch the whole run if it fails
                            bulk[bulk.columns[hh]][ii]=nan  # for some reason this needs to be in a loop
                        else:
                            bulk[bulk.columns[hh]][ii]=bulkout[hh]
 
            # add this to the EC data
            turb_data = pd.concat( [turb_data, bulk], axis=1) # concat columns alongside each other without adding indexes
            print('Outputting {} turbulent fluxes to netcdf files: {}'.format(str(integ_time_turb_flux[win_len])+"min",today))
            turb_q = Queue()
            Thread(target=write_turb_netcdf,\
                args=(turb_data.copy(), today, turb_q)).start()
            turb_q.get()


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

    l2_atts, l2_cols = define_level2_variables(sonic_z, mast_sonic_height, licor_z)

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

    turb_atts, turb_cols = define_turb_variables(sonic_z, mast_sonic_height, licor_z)

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
    file_str = '/mosflxtowerturb.level2.{}min.{}.nc'.format(integ_time_turb_flux[win_len], date.strftime('%Y%m%d.%H%M%S'))

    turb_name  = '{}/{}'.format(out_dir, file_str)

    global_atts = define_global_atts("turb") # global atts for level 1 and level 2
    netcdf_turb = Dataset(turb_name, 'w') 

    for att_name, att_val in global_atts.items(): netcdf_turb.setncattr(att_name, att_val) 
    n_turb_in_day = np.int(24*60/integ_time_turb_flux[win_len])

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_turb.createDimension('time', None)# n_turb_in_day) 
    # we also need freq. dim for some turbulence vars and fix some object-oriented confusion
    for var_name, var_atts in turb_atts.items(): 
        # seriously python, seriously????
        if turb_data[var_name].isnull().all():
            if turb_data[var_name].dtype == object: # happens when all fast data is missing...
                turb_data[var_name] = np.float64(turb_data[var_name])     
            elif turb_data[var_name][0].size > 1:
                if turb_data[var_name][0].dtype == object: # happens when all fast data is missing...
                    turb_data[var_name] = np.float64(turb_data[var_name])
            else:         
                if turb_data[var_name].dtype == object: # happens when all fast data is missing...
                    turb_data[var_name] = np.float64(turb_data[var_name])
                    # create variable, # dtype inferred from data file via pandas
        if 'fs' in var_name:
            netcdf_turb.createDimension('freq', turb_data[var_name][0].size)   
                   
    time_atts_turb = {'units'     : 'seconds since {}'.format(beginning_of_time),
                      'delta_t'   : '0000-00-00 00:00:01',
                      'long_name' : 'seconds since the first day of MOSAiC',
                      'calendar'  : 'standard',}
    # this is a bit klugy
    time_atts_turb['delta_t']   = '0000-00-00 '+np.str(pd.Timedelta(integ_time_turb_flux[win_len],'m')).split(sep=' ')[2] 

    bot = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files
    times_turb = np.floor(((pd.date_range(date, tomorrow, freq=np.str(integ_time_turb_flux[win_len])+'T') - bot).total_seconds()))

    # fix problems with flt rounding errors for high temporal resolution (occasional errant 0.00000001)
    times_turb = pd.Int64Index(times_turb)

    # set the time dimension and variable attributes to what's defined above
    t    = netcdf_turb.createVariable('time', 'i','time') # seconds since
    t[:] = times_turb.values
    for att_name, att_val in time_atts_turb.items() : netcdf_turb['time'].setncattr(att_name,att_val)
    
    # loop over all the data_out variables and save them to the netcdf along with their atts, etc
    for var_name, var_atts in turb_atts.items():

        # create variable, # dtype inferred from data file via pandas
        var_dtype = turb_data[var_name][0].dtype
        if turb_data[var_name][0].size == 1:
            var_turb  = netcdf_turb.createVariable(var_name, var_dtype, 'time')
            turb_data[var_name].fillna(def_fill_flt, inplace=True)
            # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data)
            var_turb[:] = turb_data[var_name].values
        else:
            if 'fs' in var_name:  
                var_turb  = netcdf_turb.createVariable(var_name, var_dtype, ('freq'))
                turb_data[var_name][0].fillna(def_fill_flt, inplace=True)
                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data). this is even stupider in multipple dimensions
                var_turb[:] = turb_data[var_name][0].values      
            else:   
                var_turb  = netcdf_turb.createVariable(var_name, var_dtype, ('time','freq'))
                for jj in range(0,turb_data[var_name].size):
                    turb_data[var_name][jj].fillna(def_fill_flt, inplace=True)
                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data). this is even stupider in multipple dimensions
                tmp = np.empty([turb_data[var_name].size,turb_data[var_name][0].size])
                for jj in range(0,turb_data[var_name].size):
                    tmp[jj,:]=np.array(turb_data[var_name][jj])
                var_turb[:] = tmp         


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
