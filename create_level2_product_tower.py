#!/usr/bin/env python3
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

# import our code modules.... lots of definitions
from tower_data_definitions import define_global_atts, define_level2_variables
from tower_data_definitions import define_turb_variables, define_qc_variables
from tower_data_definitions import define_10hz_variables, define_level1_slow, define_level1_fast

from get_data_functions     import get_flux_data, get_arm_radiation_data, get_ship_df
from site_metadata          import metcity_metadata
from qc_level2              import qc_tower, qc_tower_winds, qc_tower_turb_data

import functions_library as fl # includes a bunch of helper functions that we wrote

# Ephemeris
# SPA is NREL's (Ibrahim Reda's) emphemeris calculator that all those BSRN/ARM radiometer geeks use ;
# pvlib is NREL's photovoltaic library
from pvlib import spa 
    # .. [1] I. Reda and A. Andreas, Solar position algorithm for solar radiation
    #    applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.

    # .. [2] I. Reda and A. Andreas, Corrigendum to Solar position algorithm for
    #    solar radiation applications. Solar Energy, vol. 81, no. 6, p. 838,
    #    2007.

import os, inspect, argparse, time, gc

import socket 

global nthreads 

hostname = socket.gethostname()
if '.psd.' in hostname:
    if hostname.split('.')[0] in ['linux1024', 'linux512']:
        nthreads = 25  # the twins have 32 cores/64 threads, won't hurt if we use <30 threads
    elif hostname.split('.')[0] in ['linux64', 'linux128', 'linux256']:
        nthreads = 12  # 
    else:
        nthreads = 90  # the new compute is hefty.... real hefty

else: nthreads = 8     # laptops don't tend to have 12  cores... yet

from multiprocessing import Process as P
from multiprocessing import Queue   as Q

# need to debug something? kills multithreading to step through function calls
we_want_to_debug = False
if we_want_to_debug:
    from multiprocessing.dummy import Process as P
    from multiprocessing.dummy import Queue   as Q
    nthreads = 1
    try: from debug_functions import drop_me as dm
    except: you_dont_care=True
 
import numpy  as np
import pandas as pd
import xarray as xr

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from datetime  import datetime, timedelta
from numpy     import sqrt
from scipy     import stats
from netCDF4   import Dataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

# just in case... avoids some netcdf nonsense involving the default file locking across mounts
os.environ['HDF5_USE_FILE_LOCKING']='FALSE' # just in case
os.environ['HDF5_MPI_OPT_TYPES']='TRUE'     # just in case

version_msg = '\n\nPS-122 MOSAiC Met Tower processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

def main(): # the main data crunching program

    # the UNIX epoch... provides a common reference, used with base_time
    global epoch_time
    epoch_time        = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers

    global integ_time_step, win_len

    integ_time_step = [10]# [minutes] integration time for the turb flux calculation and average window for mosseb files

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
    sb       = 5.67e-8 # stefan-boltzmann
    emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over OPall the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')

    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')
    
    # pass the base path to make it more mobile
    parser.add_argument('-p', '--path', metavar='str', help='fulll path to data, including /data/ andtrailing slash')
    parser.add_argument('-pd', '--pickledir', metavar='str',help='want to store a pickle of the data for debugging?')

    args         = parser.parse_args()
    if args.verbose: verbose = True
    else: verbose = False
    v_print      = print if args.verbose else lambda *a, **k: None
    verboseprint = v_print
    
    # paths
    global data_dir, level1_dir, level2_dir, turb_dir, date_twr_raised

    if args.path: data_dir = args.path
    else: data_dir = '/Projects/MOSAiC/'

    if args.pickledir: pickle_dir=args.pickledir
    else: pickle_dir=False
    level1_dir = data_dir+'/tower/1_level_ingest/'                                  # where does level1 data live?
    level2_dir = data_dir+'/tower/2_level_product/version2/'                        # where does level2 data go
    level2_dir = '/Projects/MOSAiC_internal/flux_data_tests/tower/2_level_product/' # where does level2 data go
    turb_dir   = data_dir+'/tower/2_level_product/version2/'                        # where does level2 data go
    #turb_dir   = '/Projects/MOSAiC_internal/flux_data_tests/tower/2_level_product/' # where does level2 data go
    arm_dir    = '/Projects/MOSAiC_internal/partner_data/' 
    leica_dir  = '/Projects/MOSAiC_internal/partner_data/AWI/polarstern/WXstation/'

    def printline(startline='',endline=''):
        print('{}--------------------------------------------------------------------------------------------{}'
              .format(startline, endline))

    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y%m%d')
    else:
        # make the data processing start yesterday! i.e. process only most recent full day of data
        start_time = epoch_time.today() # any datetime object can provide current time
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0, day=start_time.day)

    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y%m%d')
    else:
        end_time = epoch_time.today() # any datetime object can provide current time
        end_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0, day=start_time.day)
    
    # expand the load by 1 day to facilite gps processing    
    start_time = start_time-timedelta(1)
    end_time = end_time+timedelta(1)

    print('The first day we  process data is:     %s' % str(start_time+timedelta(1)))
    print('The last day we will process data is:  %s' % str(end_time-timedelta(1)))
    printline()

    global mc_site_metadata
    mc_site_metadata = metcity_metadata()

    # thresholds! limits that can warn you about bad data!
    # these aren't used yet but should be used to warn about spurious data
    irt_targ          = (-80  ,5)    # IRT surface brightness temperature limits [Celsius]
    sr50d             = (1    ,3)    # distance limits from SR50 to surface [m]; install height -1 m or +0.5
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
    cd_lim            = (-2.3e-3,1.5e-2)  # drag coefficinet sanity check. really it can't be < 0, but a small negative
                                          # threshold allows for empiracally defined (from EC) 3 sigma noise distributed about 0
    
    # various calibration params
    # ##########################
    # initial distance measurement for sr50 to snow (187.9cm) corrected
    # by 2-m Tvais (-25.7 C) at 0430 UTC Oct 27, 2019
    #sr50_init_dist  = sqrt((-25.7+K_offset)/K_offset)*187.9
    #sr50_init_depth = 2.3 #snow depth (cm) measured under SR50 at 0430 UTC Oct 27, 2019
    
    init_twr = pd.DataFrame()
    
    init_twr['init_date']  = [
                                datetime(2019,10,24,5,30),             # Tower initial raise, Leg 1
                                datetime(2020,6,27,9,30),              # Tower initial raise, Leg 4
                                datetime(2020,7,2,13,50),              # Tower insutments on boom moved our away from ablation shield, reset
                                datetime(2020,7,5,13,37),              # Tower settles: reset
                                datetime(2020,7,8,11,46),              # Tower settles: reset
                                datetime(2020,7,11,11,26),             # Tower settles: reset
                                datetime(2020,7,24,8,24),              # Tower settles: reset
                                datetime(2020,7,29,8,41),              # back on board
                                datetime(2020,8,27,11,4),              # Tower initial raise, Leg 5. Date estiamte from level 1 as notes say tower begins 8/25 before sr50 comes online
                                datetime(2020,8,31,11,31,35),          # Tower settles by ~1deg. Need reset of sr50 range
                                datetime(2020,9,8,15,52),              # Tower settles: reset
                                datetime(2020,9,18,5,45)               # end
                             ]
        
    init_twr['init_dist']  = [
                                sqrt((-25.7+K_offset)/K_offset)*187.9, # by 2-m Tvais (-25.7 C) at 0430 UTC Oct 27, 2019
                                sqrt((0.3+K_offset)/K_offset)*207.5,   # from level 1 data
                                sqrt((-1.6+K_offset)/K_offset)*228.9,  # from level 2 data
                                sqrt((-0.4+K_offset)/K_offset)*232,    # Tower settles: reset
                                sqrt((0.1+K_offset)/K_offset)*236.6,   # Tower settles: reset
                                sqrt((1+K_offset)/K_offset)*237.7,     # Tower settles: reset
                                sqrt((0.2+K_offset)/K_offset)*256.4,   # Tower settles: reset
                                nan,                                   # back on board
                                sqrt((0.5+K_offset)/K_offset)*221.5,   # Leg 5
                                sqrt((-0.5+K_offset)/K_offset)*226.7,  # Tower settles by ~1deg. Need reset of sr50 range                               
                                sqrt((-4.3+K_offset)/K_offset)*226.8,  # Tower settles: reset
                                nan                                    # end
                             ]
        
    init_twr['init_depth'] = [
                                2.3,                                   # snow depth (cm) measured under SR50 at 0430 UTC Oct 27, 2019
                                7,                                     # Tower initial raise, Leg 4 Current snow depth is hard to determine because of ambiguity between snow and the surface scattering layer. Interface between solid ice and non-solid ice was 7-9cm down." 
                                7,                                     # adjustment to boom 
                                1.63,                                  # Tower settles: reset
                                -4.4,                                  # Tower settles: reset
                                -9.1,                                  # Tower settles: reset
                                -29.2,                                 # Tower settles: reset
                                nan,                                   # back on board
                                0,                                     # no snow according to Ola's notes
                                -2.195,                                # Tower settles by ~1deg. Need reset of sr50 range. This is last measurement before shift. 
                                -0.33,                                 # Tower settles: reset
                                nan                                    # end
                             ]    
        
    init_twr['init_loc']   = [
                                'CO1',                                 # Original CO
                                'CO2',                                 # Leg 4 CO
                                'CO2',                                 # Leg 4 CO adjustment
                                'CO2',                                 # Tower settles: reset
                                'CO2',                                 # Tower settles: reset
                                'CO2',                                 # Tower settles: reset
                                'CO2',                                 # Tower settles: reset
                                'PS',                                  # back on board
                                'CO3',                                 # Leg 5 CO
                                'CO3',                                 # Tower settles by ~1deg. Need reset of sr50 range
                                'CO3',                                 # Tower settles: reset
                                'PS'                                   # back on board
                             ] 

    # Set the index
    init_twr.set_index(init_twr['init_date'],inplace=True)    


    # the following is currently N/A, we don't have the ARM data yet to read in
    #sr30      = (-4,1000) # SWD & SWU [Wm^2]
    #ir20      = (50,400)  # LWD & LWU [Wm^2] (FYI, 315 W/m2 ~ 0 C)
    #ir20_case = (-80,10)  # IR20 instrument case temperature [C]

    # Ola says he's guessed at some of these... ... ...
    mast_params = {}
    mast_dates  = []
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
 
    # Some other dates
    fpA_bury_date = datetime(2019,10,24,5,48) 
    fpB_bury_date = datetime(2019,10,25,1,35) 

    # mast dates and headings w.r.t. tower from available notes and a deductions, assumptions
    # mast_hdg_dates map to mast_hdg_vals 1 to 1        
    # ccox made an effort, but without heights and with so many changes to the mast between 12/1 and 12/9, without notes the adjustments are arbitrarily set to match the 10 m data, which has not benefits. We can revisit later. I 'll leave it where I left off, a combination of my guesses adn Ola's notes.            
    
    # mast_hdg:
    # These are the manual readings at the mast. The final position could be replaced with 99.1 from
    # 3/17 (first obs since Dec), but this was after teh 3/11 lead.
      
    # gps_hdg:
    # These are the manual readings at the tower when the mast obs were made. The final position could
    # be replaced with 199.6 from 3/17 (first obs since Dec), but this was after teh 3/11 lead. Cox
    # adjusted some using the values from thee filtered tower gps when the date of the reading (NOT
    # the date of the change from mast_hdg_dates!) was recorded
    mast_hdg_df = pd.DataFrame(np.array([
        # date         mast_hdg  gps_hdg
        [datetime(2019,10,15,0,0),   nan,      nan  ], # Beginning of time; just a placeholder. Sonic not mounted
        [datetime(2019,10,19,5,49),  10,       291.0], # Sonic mounted on low mast
        [datetime(2019,10,26,7,0),   40.7,     291.2], # Tower raised to 30 m; Ola's notes based on manual heading reading on 00:56:55 Oct 30, 2019. I have two versions of the second column: 290.7 & 291.2
        [datetime(2019,11,18,12,50), 205.1,    290.7], # Tower falls down; Ola's notes
        [datetime(2019,11,28,4,30),  200.0,    291.0], # Mast sonic mounted on 2m boom after repair from fall
        [datetime(2019,12,1,9,50),   268.8,    281.7], # ccox
        [datetime(2019,12,1,23,58),  286.0,    291.0], # Mast sonic mounted on repaired 2m boom after repair from fall .chris thinks first colums is 268.6 & second sol is 282.1
        #[datetime(2019,12,6,6,27),   104.1,    291.9], # ccox
        #[datetime(2019,12,8,0,0),    214.7,    292.9], # ccox
        #[datetime(2019,12,8,12,42),  291.2,    290.0], # ccox
        [datetime(2019,12,8,14,0),   215.0,    290.0], # Mast raised as far as possible
        [datetime(2019,12,9,0,0),    193.9,    290.0], # ccox
        [datetime(2019,12,9,7,30),   228.0,    291.5], # Mast raised with remaining useable tubes
        [datetime(2020,3,17,12,0),   228.0,    291.3], # Chris took a reading here. However, note that the tower and mast had ben seperated on 3/11 so this is difficult to interpret.
        ]),columns=['date','mast_hdg','gps_hdg'])
    
    mast_hdg_df.set_index(mast_hdg_df['date'],inplace=True)
   
    
    # recording some information on the manual alignments and azimuth readings for the tower-down data from 10/15 - 10/24.
    # we will use this later in the wind calcs to make the adjustments
    twr_hdg_dates_10m = pd.DataFrame(np.array([                  
                                        # date  hdg 
                                        [datetime(2019,10,15,0,0), nan], # sonic not mounted
                                        [datetime(2019,10,24,5,3), nan],
                                        ]),columns=['date', 'tower_heading'])
    twr_hdg_dates_10m.set_index(twr_hdg_dates_10m['date'],inplace=True)
    
    twr_hdg_dates_6m = pd.DataFrame(np.array([                  
                                        # date  hdg 
                                        [datetime(2019,10,15,0,0), 27], # tower lying down, sonic upright
                                        [datetime(2019,10,24,1,13), nan], # sonic/tower lying down
                                        ]),columns=['date', 'tower_heading'])
    twr_hdg_dates_6m.set_index(twr_hdg_dates_6m['date'],inplace=True)
    
    twr_hdg_dates_2m = pd.DataFrame(np.array([                  
                                        # date  hdg 
                                        [datetime(2019,10,15,0,0), 27], # tower lying down, sonic upright
                                        [datetime(2019,10,22,3,37), 293.1], # spare sonic switched on, sonic north aligned
                                        [datetime(2019,10,24,1,13), nan], # sonic/tower lying down
                                        ]),columns=['date', 'tower_heading'])
    twr_hdg_dates_2m.set_index(twr_hdg_dates_2m['date'],inplace=True)
    
    global twr_manual_hdg_data
    twr_manual_hdg_data = {}
    twr_manual_hdg_data['metek_10m'] = twr_hdg_dates_10m
    twr_manual_hdg_data['metek_6m'] = twr_hdg_dates_6m
    twr_manual_hdg_data['metek_2m'] = twr_hdg_dates_2m
    

    # #####################################################################################################
    # Now that everything is defined, we read in the logger data for the date range requested and then
    # do vector operations for data QC, as well as any processing to derive output variables (i.e. no loops)

    # read *all* of the tower logger data...? this could be too much. but why have so much RAM if you don't use it?
    curr_station = "tower" # be compatible with asfs notation 
    slow_data, code_version = get_flux_data(curr_station, start_time, end_time, 1,
                                            data_dir, 'slow', verbose, nthreads, False, pickle_dir)

    slow_data = slow_data[start_time:end_time] # in case we pickled the larger dataset

    arm_data, arm_version = get_arm_radiation_data(start_time, end_time, arm_dir, verbose, nthreads, pickle_dir)

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
    print("\n A small sample of ARM data:\n")
    print(arm_data)
    printline(startline="\n")

    # #############################################################################################
    # a small amount of pre-processing before the loop over each day. the band-pass filtering
    # is done on an envelope the day before and after and therefore must be done as a whole 

    # The heading/alt from the v102 is "noisey" at regular frequencies, about ~1, 2.1, 6.4, and 12.8
    # hours. I've considered several approaches: wavelet frequency rejection, various band-pass filters,
    # Kalman filter, tower->ais bearing baseline. Median filter works the best. J. Hutchings results indicate
    # that the 12 hour signal is tidal - throughout the year! - so it shuld be retained. So, we implement 
    # a 6 hour running median filter. I have implemented a 1 day buffer on the start_time, end_time for
    # this. For missing data we forward pad to reduce edge effects but report nan in the padded space.
    print('\n... band-pass median filter applied to heading... unthreaded and a bit slow.... must be done') 

    # mast gps height for ice alt calc
    twr_GPS_height_raised_precise = [(1.985)] # estimate of height above ice surface on 10/25:
                                              # = 2.3 cm snow + 179 cm SR50 + 9 cm SR50 sensor len + 1.25 cm pipe rad + 6.9 cm gps height

    mst_GPS_height_raised_precise = [(0.799)] # 27 cm snow depth + 46 cm Hardigg box height + 6.9 cm gps height. the
                                              # snow depth is and average of the two nearby (~5 m) obs, 17 and 37
                                              # cm; it was in a transiton into a drifted ridge

    # The heading is in degree x 100 so convert. also we will do something simlar for the altitude
    slow_data['tower_heading'] = slow_data['gps_hdg']/100.0  # convert to degrees
    slow_data['tower_ice_alt'] = slow_data['gps_alt'] - twr_GPS_height_raised_precise     

    # The filter needs to be carried out in vector space. the filter is 6 hrs = 21600 sec
    unitv1 = np.cos(np.radians(slow_data['tower_heading'])) # degrees -> unit vector
    unitv2 = np.sin(np.radians(slow_data['tower_heading'])) # degrees -> unit vector
    unitv1 = unitv1.interpolate(method='pad').rolling(21600,min_periods=1,center=True).median() # filter the unit vector
    unitv2 = unitv2.interpolate(method='pad').rolling(21600,min_periods=1,center=True).median() # filter the unit vector
    tmph = np.degrees(np.arctan2(-unitv2,-unitv1))+180 # back to degrees

    tmpa = slow_data['tower_ice_alt'].interpolate(method='pad').rolling(21600,min_periods=1,center=True).median()

    tmph.mask(slow_data['tower_heading'].isna(),inplace=True)
    tmpa.mask(slow_data['tower_ice_alt'].isna(),inplace=True)

    slow_data['tower_heading'] = tmph
    slow_data['tower_ice_alt'] = tmpa

    # naive merge was *extremely***** slow and innefecient.
    # slow_data = pd.concat([slow_data, arm_data], index=1) # the naive merge
    # so instead we create nan columns and only fill them where there is data 
    print('... finished filtering heading, now copying ARM data')
    rad_vars = ['down_long_hemisp', 'down_short_hemisp', 'up_long_hemisp', 'up_short_hemisp']
    #'skin_temp_surface', 'radiation_LWnet', 'radiation_SWnet', 'net_radiation']   

    arm_data.rename(columns={
        'LWdn'  : 'down_long_hemisp',
        'SWdn'  : 'down_short_hemisp',
        'LWup'  : 'up_long_hemisp',
        'SWup'  : 'up_short_hemisp',
    }, inplace=True) 
 
 
    arm_data = arm_data.sort_index(); 
    prev_len = len(arm_data)
    arm_data = arm_data.drop_duplicates(); 
    drop_len = len(arm_data)
    print(f"... for some reason there were {prev_len-drop_len} duplicates in ARM data, if this number is 0, that's good")
    arm_inds = arm_data.index
    slow_data = slow_data.sort_index(); 
    slow_inds = slow_data.index


    # now we have to match the ARM timestamps up to the flux timestamps, the naive
    # pd.concat([slow_data, arm_data], axis=1) is so absurdly slow that we wrote a
    # custom function that does this in a more clever way
    not_present, index_map = compare_indexes(arm_inds, slow_inds)
    slow_map = np.array(index_map[0]) # these just say which index in ARM data relates to which
    arm_map  = np.array(index_map[1]) # index in the slow data

    verboseprint(f"\n... there were {len(not_present)} datapoints present in ARM but not in flux ")
    verboseprint(f"... data for the requested timeframe!!! \n")

    # now we have to actually *put* the ARM data into the slow_data dataframe at the mapped indices
    for iv, rv in enumerate(rad_vars):
        val_arr = np.array([nan]*len(slow_inds))
        val_arr[slow_map] = arm_data[rv].values[arm_map]
        slow_data[rv] = val_arr
        slow_data[rv] = slow_data[rv].interpolate(limit=59) # fill in the NaNs that should not be but leave
                                                            # the ones that should be... one mins worth

    print('... finished with ARM data, processing mast heading for full time series')

    if 'mast_RECORD' in slow_data: # same thing for the mast if it was up
        slow_data['mast_gps_alt'] = slow_data['gps_alt']/1000.0 # convert to meters
        slow_data['mast_heading'] = slow_data['mast_gps_hdg_Avg']/100.0  # convert to degrees
        slow_data['mast_ice_alt'] = slow_data['mast_gps_alt'] - mst_GPS_height_raised_precise 



        tmph = slow_data['mast_heading'].rolling(86400,min_periods=1,center=True).median()
        tmpa = slow_data['mast_ice_alt'].interpolate(method='pad').rolling(86400,min_periods=1,center=True).median()
        tmph.mask(slow_data['mast_heading'].isna(), inplace=True)
        tmpa.mask(slow_data['mast_ice_alt'].isna(), inplace=True)

        slow_data['mast_heading'] = tmph
        slow_data['mast_heading'] = np.mod(slow_data['mast_heading'], 360)
        slow_data['mast_ice_alt'] = tmpa


    verboseprint("... creating qc flags... takes a minute and some RAM")

    if we_want_to_debug:
        with open(f'./tests/{datetime(2022,10,10).today().strftime("%Y%m%d")}_qc_debug_before.pkl', 'wb') as pkl_file:
            import pickle
            pickle.dump(slow_data, pkl_file)

    slow_data = qc_tower(slow_data)

    if we_want_to_debug:
        with open(f'./tests/{datetime(2022,10,10).today().strftime("%Y%m%d")}_qc_debug_after.pkl', 'wb') as pkl_file:
            import pickle
            pickle.dump(slow_data, pkl_file)

    # where arm data is missing, mark qc var as bad 
    arm_vars = ['down_long_hemisp', 'down_short_hemisp', 'up_long_hemisp', 'up_short_hemisp']
    for av in arm_vars: slow_data.loc[slow_data[av].isnull(), av+'_qc'] = 2

    ship_df = get_ship_df(leica_dir).reindex(slow_data.index).interpolate() # ship location used in daily calcs

    print('... done with the slow stuff, moving into parallelized daily processing') 
    verboseprint("\n We've retreived and QCed all slow data, now processing each day...\n")

    def process_day(today, tomorrow, slow_data_today, day_q):

        slow_data = slow_data_today
        today_str = today.strftime('%Y-%m-%d') # used for prints
        # where are we in our indices for tracking data?
        
        # SR50 initialization info
        idt = init_twr.reindex(method='pad',index=slow_data.index)
        idt = idt[today:tomorrow]

        if slow_data.empty:
            verboseprint(f"!!! No data available today at all... {today_str}!!! ")
            day_q.put(False); return
        else: verboseprint(f"... processing all data for {today_str}!!! ")

        # have the instruments moved today?
        licor_z = mc_site_metadata.get_instr_metadata('licor', 'height', today, True)[0]
        wxt_z   = mc_site_metadata.get_instr_metadata('sensor_P_mast', 'height', today, True)[0]

        # has the mast moved today?
        mast_index = 0 
        for mi, md in enumerate(mast_dates) :
            if today >= md:
                mast_index = mi-1
                break

        mast_hdg           = mast_params['mast_hdg'][mast_index]
        gps_hdg_mast_setup = mast_params['gps_hdg_mast_setup'][mast_index]
        mast_sonic_height  = mast_params['mast_sonic_heights'][mast_index]

        verboseprint(f"... automated, thresholds/despiking/etc, data QC {mast_index}")

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


        # begin slow_data QC, including automated boundary and hand groomed 
        verboseprint("... automated data QC")
        
        sd = slow_data # shorthand notation to make things a little clearer, maybe... because pandas uses
                       # the name as a pointer to the DataFrame in memory, we can now use both names to
                       # refer to the dataframe and operations on either variable will modify our slow data
                       # data frame in memory. 
        sd['vaisala_P_2m']   .mask( (sd['vaisala_P_2m']     <p_thresh[0])    \
                                    | (sd['vaisala_P_2m']   >p_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_T_2m']   .mask( (sd['vaisala_T_2m']     <T_thresh[0])    \
                                    | (sd['vaisala_T_2m']   >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_T_6m']   .mask( (sd['vaisala_T_6m']     <T_thresh[0])    \
                                    | (sd['vaisala_T_6m']   >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_T_10m']  .mask( (sd['vaisala_T_10m']    <T_thresh[0])    \
                                    | (sd['vaisala_T_10m']  >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_Td_2m']  .mask( (sd['vaisala_Td_2m']    <T_thresh[0])    \
                                    | (sd['vaisala_Td_2m']  >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_Td_6m']  .mask( (sd['vaisala_Td_6m']    <T_thresh[0])    \
                                    | (sd['vaisala_Td_6m']  >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_Td_10m'] .mask( (sd['vaisala_Td_10m']   <T_thresh[0])    \
                                    | (sd['vaisala_Td_10m'] >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['vaisala_RH_2m']  .mask( (sd['vaisala_RH_2m']    <rh_thresh[0])   \
                                    | (sd['vaisala_RH_2m']  >rh_thresh[1]) , \
                                    inplace=True) # ppl

        sd['vaisala_RH_6m']  .mask( (sd['vaisala_RH_6m']    <rh_thresh[0])   \
                                    | (sd['vaisala_RH_6m']  >rh_thresh[1]) , \
                                    inplace=True) # ppl

        sd['vaisala_RH_10m'] .mask( (sd['vaisala_RH_10m']   <rh_thresh[0])   \
                                    | (sd['vaisala_RH_10m'] >rh_thresh[1]) , \
                                    inplace=True) # ppl

        sd['mast_T']         .mask( (sd['mast_T']           <T_thresh[0])    \
                                    | (sd['mast_T']         >T_thresh[1]) ,  \
                                    inplace=True) # ppl

        sd['mast_RH']        .mask( (sd['mast_RH']          <rh_thresh[0])   \
                                    | (sd['mast_RH']        >rh_thresh[1]) , \
                                    inplace=True) # ppl

    #    sd['vaisala_RH_2m']  = fl.despike(sd['vaisala_RH_2m'],0.4,30,'yes') # replace spikes outside 0.4% over 30s median
    #    sd['vaisala_RH_6m']  = fl.despike(sd['vaisala_RH_6m'],0.4,30,'yes') # replace spikes outside 0.4% over 30s median
    #    sd['vaisala_RH_10m'] = fl.despike(sd['vaisala_RH_10m'],0.4,30,'yes') # replace spikes outside 0.4% over 30s median

        verboseprint("... met corrections and calculations...")
        # Vaisala relative corrections
        #   Tower was lowered from 2019,10,19,7,19,0 to 2019,10,24,5,30,0 (n=425459 sec)
        #   The precised heights were within 20 cm above the surface a little more than a meter high
        #   (see vasaila_T_height_on_ground)
        #   
        #   This is a slight correction (inside measurement uncertainty) to the measured temperatures that make them
        #   more intercomparable for making profiles. The bias correction forces the three sensors to the mean of
        #   the sensors during the comparison period. It is based on the mean differences. Temperature dependencies
        #   are not (qualitatively) conclusive enough, nor are any dependencies easily parameterized, nor does the
        #   comparison period span a large enough range in temperature to justify either intrpolation or
        #   extrapolation of correction factors.

        # here we derive useful parameters computed from logger data that we want to write to the output file
        # ###################################################################################################
        # compute RH wrt ice -- compute RHice(%) from RHw(%), Temperature(deg C), and pressure(mb)
        Td2, h2, a2, x2, Pw2, Pws2, rhi2 = fl.calc_humidity_ptu300(slow_data['vaisala_RH_2m'],\
                                                                   slow_data['vaisala_T_2m']+K_offset,
                                                                   slow_data['vaisala_P_2m'],
                                                                   0)
        slow_data['rhi_2m']                  = rhi2
        slow_data['enthalpy_vaisala_2m']     = h2
        slow_data['abs_humidity_vaisala_2m'] = a2
        slow_data['vapor_pressure_2m']       = Pw2
        slow_data['mixing_ratio_2m']         = x2

        # atm pressure adjusted assuming 1 hPa per 10 m (1[hPA]*ht[m]/10[m]), except for mast, which has a direct meas.
        # 3/14/22 imrproved precision of heights using actual humidity sensor height reported in attributes
        p6    = slow_data['vaisala_P_2m']-1*(5.24-1.45)/10
        p10   = slow_data['vaisala_P_2m']-1*(9.14-1.45)/10    

        # we are missing a lot of the mast pressures so I will fill in with an approximation    
        pmast = slow_data['mast_P'] 
        pmast.fillna(slow_data['vaisala_P_2m']-1*mast_params['mast_sonic_heights'][mast_index]/10)

        Td6, h6, a6, x6, Pw6, Pws6, rhi6 = fl.calc_humidity_ptu300(slow_data['vaisala_RH_6m'],\
                                                                   slow_data['vaisala_T_6m']+K_offset,
                                                                   p6,
                                                                   0)
        slow_data['rhi_6m']                  = rhi6
        slow_data['enthalpy_vaisala_6m']     = h6
        slow_data['abs_humidity_vaisala_6m'] = a6
        slow_data['vapor_pressure_6m']       = Pw6
        slow_data['mixing_ratio_6m']         = x6

        Td10, h10, a10, x10, Pw10, Pws10, rhi10 = fl.calc_humidity_ptu300(slow_data['vaisala_RH_10m'],\
                                                                          slow_data['vaisala_T_10m']+K_offset,
                                                                          p10,
                                                                          0)
        slow_data['rhi_10m']                  = rhi10
        slow_data['enthalpy_vaisala_10m']     = h10
        slow_data['abs_humidity_vaisala_10m'] = a10
        slow_data['vapor_pressure_10m']       = Pw10
        slow_data['mixing_ratio_10m']         = x10

        Tdm, hm, am, xm, Pwm, Pwsm, rhim = fl.calc_humidity_ptu300(slow_data['mast_RH'],\
                                                                   slow_data['mast_T']+K_offset,
                                                                   pmast,
                                                                   -1)
        slow_data['dew_point_mast']            = Tdm
        slow_data['rhi_mast']                  = rhim
        slow_data['enthalpy_vaisala_mast']     = hm
        slow_data['abs_humidity_vaisala_mast'] = am
        slow_data['vapor_pressure_mast']       = Pwm
        slow_data['mixing_ratio_mast']         = xm


        # #####################################################################################
        # air temperature offsets from Ola Persson's "Met_Tower_Intercomparison_Results.docx"
        # further augmented to be time dependent in an email discussion titled: "temperaturex 
        # offsets" from Oct 6th 2021
        
        # R218 (2m): no offset
        # P917 (P197) (6m after Dec 2019): dT = 7.5e-5 x YD - 0.13
        # R217  (6m before Dec 2019): dT = 0.0972
        # R428 (10 m throughout MOSAiC): dT = -0.000302 x YD + 0.17
        # mast (30 m & 22 m): dT = 0.338

        year_day = today.timetuple().tm_yday
        if today.year == 2020: year_day += 365

        # year_day is the continuous 2019 Year Day (e. g., 2019 is <=365 while days in 2020 are >= than
        # 366.0; 00Z Jan 31, 2020 is YD396.00, etc). a. la. ola 
        sd['vaisala_T_2m']         .loc[today:tomorrow] = \
            sd['vaisala_T_2m']     .loc[today:tomorrow] - 0.00   # no offset 

        if today < datetime(2019,12,4): # P917 (P197) (6m after Dec 2019):
            sd['vaisala_T_6m']     .loc[today:tomorrow] = \
                sd['vaisala_T_6m'] .loc[today:tomorrow] - 0.0972 
        else:
            sd['vaisala_T_6m']     .loc[today:tomorrow] = \
                sd['vaisala_T_6m'] .loc[today:tomorrow] - ((7.5e-5*year_day) - 0.13)

        sd['vaisala_T_10m']        .loc[today:tomorrow] = \
             sd['vaisala_T_10m']   .loc[today:tomorrow]  - (-1*(0.000302*year_day) + 0.17)

        sd['mast_T']               .loc[today:tomorrow] = \
            sd['mast_T']           .loc[today:tomorrow] - 0.3380
 
        # now re-calculate RH with the corrected temperatures and the not-corrected q, as requested by Ola 
        # coefficients from calc_humidity_ptu300 to re-derive RH after correcting temp
        c0 = 0.4931358; c1 = -0.46094296*1e-2; c2 = 0.13746454*1e-4; c3 = -0.12743214*1e-7
        bm1 = -0.58002206*1e4; b0 = 0.13914993*1e1; b1 = -0.48640239*1e-1; b2 = 0.41764768*1e-4;     
        b3  = -0.14452093*1e-7;     b4  = 6.5459673

        t2m  = sd['vaisala_T_2m']+K_offset;  t6m = sd['vaisala_T_6m']+K_offset; 
        t10m = sd['vaisala_T_10m']+K_offset; tmm = sd['mast_T']+K_offset

        o2m = t2m - ( c0*t2m**0 + c1*t2m**1 + c2*t2m**2 + c3*t2m**3 )
        Pws2 = np.exp( ( bm1*o2m**-1 + b0*o2m**0 + b1*o2m**1 + b2*o2m**2 + b3*o2m**3 ) + b4*np.log(o2m) ) # [Pa]
        sd['vaisala_RH_2m'] = 100*(Pw2/Pws2) 

        o6m = t6m - ( c0*t6m**0 + c1*t6m**1 + c2*t6m**2 + c3*t6m**3 )
        Pws6 = np.exp( ( bm1*o6m**-1 + b0*o6m**0 + b1*o6m**1 + b2*o6m**2 + b3*o6m**3 ) + b4*np.log(o6m) ) # [Pa]
        sd['vaisala_RH_6m'] = 100*(Pw6/Pws6) 

        o10m = t10m - ( c0*t10m**0 + c1*t10m**1 + c2*t10m**2 + c3*t10m**3 )
        Pws10 = np.exp( ( bm1*o10m**-1 + b0*o10m**0 + b1*o10m**1 + b2*o10m**2 + b3*o10m**3 ) + b4*np.log(o10m) ) # [Pa]
        sd['vaisala_RH_10m'] = 100*(Pw10/Pws10) 

        # now actually apply the offsets
        sd['vaisala_RH_2m']       .loc[datetime(2019,10,19) : datetime(2020,9,21)] = \
            sd['vaisala_RH_2m']   .loc[datetime(2019,10,19) : datetime(2020,9,21)] + 1.04   

        sd['vaisala_RH_6m']       .loc[datetime(2019,10,19) : datetime(2019,12,4)] = \
            sd['vaisala_RH_6m']   .loc[datetime(2019,10,19) : datetime(2019,12,4)] + 0.05

        sd['vaisala_RH_6m']       .loc[datetime(2019,12,4) : datetime(2020,9,21)] = \
            sd['vaisala_RH_6m']   .loc[datetime(2019,12,4) : datetime(2020,9,21)] - 0.11

        sd['vaisala_RH_10m']      .loc[datetime(2019,10,19) : datetime(2020,9,21)] = \
             sd['vaisala_RH_10m'] .loc[datetime(2019,10,19) : datetime(2020,9,21)] +0.06

        sd['mast_RH']             .loc[datetime(2019,10,19) : datetime(2020,9,21)] = \
            sd['mast_RH']         .loc[datetime(2019,10,19) : datetime(2020,9,21)] + 0.86

        # sr50 dist QC then in m & snow depth in cm, both corrected for
        # temperature, snwdpth_meas is height in cm on oct 27 2019
        sd['sr50_dist'].mask( (sd['sr50_dist']<sr50d[0])  | (sd['sr50_dist']>sr50d[1]) , inplace=True) # ppl
        # make adjustment to the alternating detections of multi-surfaces at the beginning of Leg 4
        sd['sr50_dist'].loc[datetime(2020,6,27,9,15,0):datetime(2020,7,2,8,8,0)].mask( ((sd['sr50_dist']>2.15) | (sd['sr50_dist']<1.9)), inplace=True) 
        sd['sr50_dist'].loc[(sd.index > datetime(2020,6,27,9,15,0)) & (sd.index < datetime(2020,7,2,8,8,0)) &  (sd['sr50_dist']<2.04)] += 0.1 
        sd['sr50_dist'].loc[datetime(2020,2,19,9,21,0):datetime(2020,2,20,14,52,0)].mask( ((sd['sr50_dist']>2) | (sd['sr50_dist']<1)), inplace=True) 
        sd['sr50_dist'].loc[(sd.index > datetime(2020,2,19,9,21,0)) & (sd.index < datetime(2020,2,20,14,52,0)) &  (sd['sr50_dist']>1.45)] += -0.16
        sd['sr50_dist'].loc[datetime(2020,2,20,14,52,0):datetime(2020,2,21,23,31,0)].mask( ((sd['sr50_dist']>2) | (sd['sr50_dist']<1)), inplace=True) 
        sd['sr50_dist'].loc[(sd.index > datetime(2020,2,20,14,52,0)) & (sd.index < datetime(2020,2,21,23,31,0)) &  (sd['sr50_dist']>1.45)] += -0.13
        # replace spikes outside 2 cm over 5 min sec with 5 min median
  #      sd['sr50_dist']  = fl.despike(sd['sr50_dist'],0.05,300,"yes") 
        sd['sr50_dist']  = sd['sr50_dist']*sqrt((sd['vaisala_T_2m']+K_offset)/K_offset)
        # now calculate snow depth
        sd['snow_depth'] = idt['init_dist'] + (idt['init_depth']-sd['sr50_dist']*100)

        # Flux Plate QC

        # Fix the flux plates that were insalled upside down, why is this here... it doesn't have to be... vestigial
        sd['fp_A_Wm2'] = sd['fp_A_Wm2'] * -1
        sd['fp_B_Wm2'] = sd['fp_B_Wm2'] * -1

        sd['fp_A_Wm2'].mask( (sd['fp_A_Wm2']<flxp[1]) & (abs(sd['fp_A_Wm2'])>flxp[1]) , inplace=True) # ppl
        sd['fp_B_Wm2'].mask( (sd['fp_B_Wm2']<flxp[1]) & (abs(sd['fp_B_Wm2'])>flxp[1]) , inplace=True) # ppl
        sd['fp_A_Wm2'].loc[:fpA_bury_date] = nan # data is garbage before being buried
        sd['fp_B_Wm2'].loc[:fpB_bury_date] = nan # data is garbage before being buried

        # IRT QC
        sd['apogee_body_T'].mask( (sd['apogee_body_T']<irt_targ[0])
                                  | (sd['apogee_body_T']>irt_targ[1]), 
                                  inplace=True) # ppl

        sd['apogee_targ_T'].mask( (sd['apogee_targ_T']<irt_targ[0])
                                  | (sd['apogee_targ_T']>irt_targ[1]),
                                  inplace=True) # ppl

        sd['apogee_body_T'].mask( (sd['vaisala_T_2m']<-1)
                                  & (abs(sd['apogee_body_T'])==0),
                                  inplace=True) # reports spurious 0s sometimes

        sd['apogee_targ_T'].mask( (sd['vaisala_T_2m']<-1)
                                  & (abs(sd['apogee_targ_T'])==0),
                                  inplace=True) # reports spurious 0s sometimes

        # replace spikes outside 2C over 60 sec with 60 s median
    #    sd['apogee_body_T']  = fl.despike(sd['apogee_body_T'],2,60,'yes') 
    #    sd['apogee_targ_T']  = fl.despike(sd['apogee_targ_T'],2,60,'yes') 

        # GPS QC etc.
        sd['lat_tower']     = sd['gps_lat_deg']+sd['gps_lat_min']/60.0 # add decimal values
        sd['lon_tower']     = sd['gps_lon_deg']+sd['gps_lon_min']/60.0
        sd['gps_alt']       = sd['gps_alt']/1000.0 # convert to meters

        sd['gps_alt'].mask( (sd['gps_alt']   < twr_alt_lim[0])
                            | (sd['gps_alt'] > twr_alt_lim[1]),
                            inplace=True) # stat lims

        sd['lat_tower']     .mask( (sd['gps_qc']==0) | (sd['gps_hdop']>4), inplace=True) 
        sd['lon_tower']     .mask( (sd['gps_qc']==0) | (sd['gps_hdop']>4), inplace=True) 
        sd['gps_alt']       .mask( (sd['gps_qc']==0) | (sd['gps_hdop']>4), inplace=True) 
        sd['tower_heading'] .mask( (sd['gps_qc']==0) | (sd['gps_hdop']>4), inplace=True) 

        if 'mast_RECORD' in sd:
            sd['lat_mast']     = sd['mast_gps_lat_deg_Avg']+sd['mast_gps_lat_min_Avg']/60.0 # add decimal values
            sd['lon_mast']     = sd['mast_gps_lon_deg_Avg']+sd['mast_gps_lon_min_Avg']/60.0

            sd['mast_gps_alt'].mask( (sd['mast_gps_alt']   < mst_alt_lim[0])
                                     | (sd['mast_gps_alt'] > mst_alt_lim[1]),
                                     inplace=True) # stat lims

            sd['lat_mast']     .mask( (sd['mast_gps_qc']==0) | (sd['mast_gps_hdop_Avg']>4), inplace=True) 
            sd['lon_mast']     .mask( (sd['mast_gps_qc']==0) | (sd['mast_gps_hdop_Avg']>4), inplace=True) 
            sd['mast_gps_alt'] .mask( (sd['mast_gps_qc']==0) | (sd['mast_gps_hdop_Avg']>4), inplace=True) 
            sd['mast_heading'] .mask( (sd['mast_gps_qc']==0) | (sd['mast_gps_hdop_Avg']>4), inplace=True) 


        # Get the bearing on the ship... load the ship track and reindex to slow_data, calculate distance
        # [m] and bearing [deg from tower rel to true north, as wind direction]
        sdf = ship_df[today:tomorrow]
        sd['ship_distance'] = fl.distance_wgs84(sd['lat_tower'],sd['lon_tower'], sdf['lat'],sdf['lon'])
        sd['ship_bearing']  = fl.calculate_initial_angle_wgs84(sd['lat_tower'], sd['lon_tower'], sdf['lat'], sdf['lon']) 
        sd['ship_distance'].mask( (sd['ship_distance']>700), inplace=True)

        # something breaks in the trig model briefly. its weird. i'll just screen it out
        sd['ship_bearing'] .loc[datetime(2020,3,9,0,0,0):datetime(2020,3,10,0,0,0)].mask( (sd['ship_bearing']>326), inplace=True) 
        sd['ship_distance'].loc[datetime(2020,3,9,0,0,0):datetime(2020,3,10,0,0,0)].mask( (sd['ship_distance']>370), inplace=True) 

        # Ephemeris, set it up
        utime_in = np.array(slow_data.index.astype(np.int64)/10**9) # unix time. sec since 1/1/70
        lat_in   = slow_data['lat_tower']                           # latitude
        lon_in   = slow_data['lon_tower']                           # latitude
        elv_in   = np.zeros(slow_data.index.size)+2                 # the elevation shall be 2 m...details are negligible
        pr_in    = slow_data['vaisala_P_2m'].fillna(slow_data['vaisala_P_2m'].median()) # mb 
        t_in     = slow_data['vaisala_T_2m'].fillna(slow_data['vaisala_T_2m'].median()) # degC

        # est of atm ref at sunrise/set following U. S. Naval Observatory's Vector Astrometry Software @
        # wikipedia https://en.wikipedia.org/wiki/Atmospheric_refraction. This really just sets a flag for
        # when to apply the refraction adjustment.
        atm_ref  = ( 1.02 * 1/np.tan(np.deg2rad(0+(10.3/(0+5.11)))) ) * pr_in/1010 * (283/(273.15+t_in))/60

        # seconds. delta_t between terrestrial and UT1 time
        delt_in  = spa.calculate_deltat(slow_data.index.year, slow_data.index.month) 
        # do the thing
        app_zenith, zenith, app_elevation, elevation, azimuth, eot = spa.solar_position(utime_in,lat_in,lon_in,elv_in,pr_in,t_in,delt_in,atm_ref)

        # write it out
        slow_data['zenith_true']     = zenith
        slow_data['zenith_apparent'] = app_zenith 
        slow_data['azimuth']         = azimuth 

        # in matlab, there were rare instabilities in the Reda and Andreas algorithm that resulted in spikes
        # (a few per year). no idea if this is a problem in the python version, but lets make sure
    #    slow_data['zenith_true']     = fl.despike(slow_data['zenith_true'],2,5,'no')
    #    slow_data['zenith_apparent'] = fl.despike(slow_data['zenith_apparent'],2,5,'no')
    #    slow_data['azimuth']         = fl.despike(slow_data['azimuth'],2,5,'no')

        # Laura's product currently has NaNs in shortwave for winter, we want zeros until we get the "real" measurements
        sd_copy = slow_data.copy()

        slow_data['up_short_hemisp']   .where( sd['zenith_true']<93, 0, inplace=True)
        slow_data['down_short_hemisp'] .where( sd['zenith_true']<93, 0, inplace=True)
        slow_data['up_short_hemisp']   .where( ~sd['down_long_hemisp'].isna(), nan, inplace=True)
        slow_data['down_short_hemisp'] .where( ~sd['down_long_hemisp'].isna(), nan, inplace=True)

        # calculate budget
        slow_data['radiation_LWnet'] = slow_data['down_long_hemisp']-slow_data['up_long_hemisp']
        slow_data['radiation_SWnet'] = slow_data['down_short_hemisp']-slow_data['up_short_hemisp']
        slow_data['net_radiation']   = slow_data['radiation_LWnet'] + slow_data['radiation_SWnet'] 

        # arm data corrections, via Matt Shupe, citing "Correcting_LWandIRT.pptx" received in
        # email titled "LWD, LWU, IRT corrections" to be referenced
        slow_data['down_long_hemisp'] = slow_data['down_long_hemisp'] -(2.005 - 0.029*slow_data['radiation_LWnet'])
        slow_data['up_long_hemisp']   = slow_data['up_long_hemisp']   -(0.619 + 0.003*slow_data['radiation_LWnet'])
        slow_data['radiation_LWnet']  = slow_data['down_long_hemisp'] -slow_data['up_long_hemisp']

        # surface skin temperature Persson et al. (2002) https://www.doi.org/10.1029/2000JC000705
        slow_data['skin_temp_surface'] = (((slow_data['up_long_hemisp']-(1-emis)*slow_data['down_long_hemisp'])/(emis*sb))**0.25)-K_offset

        # rename columns to match expected level2 names from data_definitions
        # there's probably a more clever way to do this
        slow_data.rename(inplace=True, columns =\
                         {
                             'vaisala_T_2m'    : 'temp_2m',
                             'vaisala_T_6m'    : 'temp_6m',
                             'vaisala_T_10m'   : 'temp_10m',
                             'mast_T'          : 'temp_mast',
                             'vaisala_Td_2m'   : 'dew_point_2m',
                             'vaisala_Td_6m'   : 'dew_point_6m',
                             'vaisala_Td_10m'  : 'dew_point_10m',
                             'vaisala_RH_2m'   : 'rh_2m',
                             'vaisala_RH_6m'   : 'rh_6m',
                             'vaisala_RH_10m'  : 'rh_10m',
                             'mast_RH'         : 'rh_mast',
                             'vaisala_P_2m'    : 'atmos_pressure_2m',
                             'mast_P'          : 'atmos_pressure_mast',    
                             'apogee_body_T'   : 'body_T_IRT',       
                             'apogee_targ_T'   : 'brightness_temp_surface',    
                             'fp_A_mV'         : 'flux_plate_A_mv',  
                             'fp_B_mV'         : 'flux_plate_B_mv',  
                             'fp_A_Wm2'        : 'subsurface_heat_flux_A', 
                             'fp_B_Wm2'        : 'subsurface_heat_flux_B',
        }, errors="raise")

        # ###################################################################################################
        # OK, all is done with the logger data, now get the 20hz data and put it into its own netcdf file
        # done in a loop because I only have 32GB of RAM in my laptop and there's no sense doing otherwise
        printline(startline='\n')
        verboseprint(f"\n.. now processing {today}...\n")
        printline(endline='\n')

        # all the 0.1 seconds today, for obs. we buffer by 1 hr for easy of po2 in turbulent fluxes below
        Hz10_today        = pd.date_range(today-pd.Timedelta(1,'hour'), tomorrow+pd.Timedelta(1,'hour'), freq='0.1S') 
        seconds_today     = pd.date_range(today, tomorrow, freq='S')   # all the seconds today, for obs
        minutes_today     = pd.date_range(today, tomorrow, freq='T')   # all the minutes today, for obs
        ten_minutes_today = pd.date_range(today, tomorrow, freq='10T') # all the 10 minutes today, for obs

        # before putting the data in, make sure it's indexed for the full time range (i.e. times without obs
        # become NaNs) and select only the data from today to keep in the output file
        logger_today = slow_data
        logger_today = logger_today.reindex(labels=seconds_today, copy=False)

        # Nothing bad happened...  this probably doesn't really need to be a loop
        # get the right instrument heights for this day... goes in the day loop
        height_list = ['2m', '6m', '10m']
        sonic_z = []; Tvais_z = []; RHvais_z = []

        for ih, h in enumerate(height_list):
            sonic_z.append  (mc_site_metadata.get_instr_metadata('sonic_'+h,     'height', today, True)[0])
            Tvais_z.append  (mc_site_metadata.get_instr_metadata('sensor_T_'+h,  'height', today, True)[0])
            RHvais_z.append (mc_site_metadata.get_instr_metadata('sensor_Rh_'+h, 'height', today, True)[0]) 

        Pvais_z  = mc_site_metadata.get_instr_metadata('sensor_P_2m', 'height', today, True)[0]
        SR50_z   = mc_site_metadata.get_instr_metadata('SR50', 'height', today, True)[0]

        # raw data... ~20 Hz data, 5Mb files each hour...
        #                              !! Important !!
        #   to calculate turbulent params, the data is first resampled to 10 Hz by averaging then reindexed to a
        #   continuous 10 Hz time grid (NaN at blackouts) of Lenth 60 min x 60 sec x 10 Hz = 36000
        #   Later on (below) we will fill all missing times with the median of the (30 min?) flux sample.

        # ~~~~~~~~~~~~~~~~~~~~ (1) Read the raw data ~~~~~~~~~~~~~~~~~~~~~~~
        #   The data are nominally 20 Hz for MOSAiC, but irregular time stamping
        #   because NOAA Services timestamped to the ~ms at time of processing by Windows OS

        # this contrived loop is vestigial. this code was originally written with fast variables in their own
        # group and now they're mashed with a prefix into the same standard netcdf. this converts to the old structure
        metek_inst_keys = ['metek_2m', 'metek_6m', 'metek_10m', 'metek_mast']
        fast_data = get_fast_data(today, data_dir) # dictionary of dataframes with keys above
        
        # #######################################################################################################

        # Add empiraclly-calculated offsets to the Metek inclinometer/tilt to make it plumb 
        fast_data['metek_2m']['metek_2m_incx']       .loc[datetime(2019,10,15) : datetime(2019,12,19)] = \
            fast_data['metek_2m']['metek_2m_incx']   .loc[datetime(2019,10,15) : datetime(2019,12,19)] + 1.75   

        fast_data['metek_2m']['metek_2m_incy']       .loc[datetime(2019,10,15) : datetime(2019,12,19)] = \
            fast_data['metek_2m']['metek_2m_incy']   .loc[datetime(2019,10,15) : datetime(2019,12,19)] + -1.25 

        fast_data['metek_2m']['metek_2m_incx']       .loc[datetime(2019,12,19) : datetime(2020,3,10)] = \
            fast_data['metek_2m']['metek_2m_incx']   .loc[datetime(2019,12,19) : datetime(2020,3,10)] + 0.5   
        fast_data['metek_2m']['metek_2m_incy']       .loc[datetime(2019,12,19) : datetime(2020,3,10)] = \
            fast_data['metek_2m']['metek_2m_incy']   .loc[datetime(2019,12,19) : datetime(2020,3,10)] + -0.75
            
        fast_data['metek_2m']['metek_2m_incx']       .loc[datetime(2020,3,10) : datetime(2020,5,10)] = \
            fast_data['metek_2m']['metek_2m_incx']   .loc[datetime(2020,3,10) : datetime(2020,5,10)] + 1.   
        fast_data['metek_2m']['metek_2m_incy']       .loc[datetime(2020,3,10) : datetime(2020,5,10)] = \
            fast_data['metek_2m']['metek_2m_incy']   .loc[datetime(2020,3,10) : datetime(2020,5,10)] + -1.75 
            
        fast_data['metek_2m']['metek_2m_incx']       .loc[datetime(2020,6,24) : datetime(2020,7,29)] = \
            fast_data['metek_2m']['metek_2m_incx']   .loc[datetime(2020,6,24) : datetime(2020,7,29)] + -1.75   
        fast_data['metek_2m']['metek_2m_incy']       .loc[datetime(2020,6,24) : datetime(2020,7,29)] = \
            fast_data['metek_2m']['metek_2m_incy']   .loc[datetime(2020,6,24) : datetime(2020,7,29)] + -0.5 
            
        fast_data['metek_2m']['metek_2m_incx']       .loc[datetime(2020,8,25) : datetime(2020,9,18)] = \
            fast_data['metek_2m']['metek_2m_incx']   .loc[datetime(2020,8,25) : datetime(2020,9,18)] + -2.   
        fast_data['metek_2m']['metek_2m_incy']       .loc[datetime(2020,8,25) : datetime(2020,9,18)] = \
            fast_data['metek_2m']['metek_2m_incy']   .loc[datetime(2020,8,25) : datetime(2020,9,18)] + -0.5
            
        fast_data['metek_6m']['metek_6m_incx']       .loc[datetime(2019,10,15) : datetime(2019,12,19)] = \
            fast_data['metek_6m']['metek_6m_incx']   .loc[datetime(2019,10,15) : datetime(2019,12,19)] + 2.75   
        fast_data['metek_6m']['metek_6m_incy']       .loc[datetime(2019,10,15) : datetime(2019,12,19)] = \
            fast_data['metek_6m']['metek_6m_incy']   .loc[datetime(2019,10,15) : datetime(2019,12,19)] + 1.25            
            
        fast_data['metek_6m']['metek_6m_incx']       .loc[datetime(2019,12,19) : datetime(2020,3,10)] = \
            fast_data['metek_6m']['metek_6m_incx']   .loc[datetime(2019,12,19) : datetime(2020,3,10)] + 3.25   
        fast_data['metek_6m']['metek_6m_incy']       .loc[datetime(2019,12,19) : datetime(2020,3,10)] = \
            fast_data['metek_6m']['metek_6m_incy']   .loc[datetime(2019,12,19) : datetime(2020,3,10)] + 2.5
            
        fast_data['metek_6m']['metek_6m_incx']       .loc[datetime(2020,3,10) : datetime(2020,5,10)] = \
            fast_data['metek_6m']['metek_6m_incx']   .loc[datetime(2020,3,10) : datetime(2020,5,10)] + 3.25   
        fast_data['metek_6m']['metek_6m_incy']       .loc[datetime(2020,3,10) : datetime(2020,5,10)] = \
            fast_data['metek_6m']['metek_6m_incy']   .loc[datetime(2020,3,10) : datetime(2020,5,10)] + 1.75            
            
        fast_data['metek_6m']['metek_6m_incx']       .loc[datetime(2020,6,24) : datetime(2020,7,29)] = \
            fast_data['metek_6m']['metek_6m_incx']   .loc[datetime(2020,6,24) : datetime(2020,7,29)] + -2.   
        fast_data['metek_6m']['metek_6m_incy']       .loc[datetime(2020,6,24) : datetime(2020,7,29)] = \
            fast_data['metek_6m']['metek_6m_incy']   .loc[datetime(2020,6,24) : datetime(2020,7,29)] + -3.5 

        fast_data['metek_6m']['metek_6m_incx']       .loc[datetime(2020,8,25) : datetime(2020,9,18)] = \
            fast_data['metek_6m']['metek_6m_incx']   .loc[datetime(2020,8,25) : datetime(2020,9,18)] + -0.75   
        fast_data['metek_6m']['metek_6m_incy']       .loc[datetime(2020,8,25) : datetime(2020,9,18)] = \
            fast_data['metek_6m']['metek_6m_incy']   .loc[datetime(2020,8,25) : datetime(2020,9,18)] + 3
            
        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2019,10,15) : datetime(2019,11,17)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2019,10,15) : datetime(2019,11,17)] + 2.5   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2019,10,15) : datetime(2019,11,17)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2019,10,15) : datetime(2019,11,17)] + 1.75            

        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2019,11,17) : datetime(2019,12,19)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2019,11,17) : datetime(2019,12,19)] + 2.5   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2019,11,17) : datetime(2019,12,19)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2019,11,17) : datetime(2019,12,19)] + 1 
            
        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2019,12,19) : datetime(2020,2,7)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2019,12,19) : datetime(2020,2,7)] + 2.5   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2019,12,19) : datetime(2020,2,7)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2019,12,19) : datetime(2020,2,7)] + 1.25 
            
        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2020,2,7) : datetime(2020,4,13)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2020,2,7) : datetime(2020,4,13)] + 2.   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2020,2,7) : datetime(2020,4,13)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2020,2,7) : datetime(2020,4,13)] + 0.25 
            
        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2020,4,13) : datetime(2020,5,10)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2020,4,13) : datetime(2020,5,10)] + 2.   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2020,4,13) : datetime(2020,5,10)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2020,4,13) : datetime(2020,5,10)] + 0.75
        
        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2020,6,24) : datetime(2020,7,29)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2020,6,24) : datetime(2020,7,29)] + 0.75   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2020,6,24) : datetime(2020,7,29)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2020,6,24) : datetime(2020,7,29)] + -2.75
            
        fast_data['metek_10m']['metek_10m_incx']       .loc[datetime(2020,8,25) : datetime(2020,9,18)] = \
            fast_data['metek_10m']['metek_10m_incx']   .loc[datetime(2020,8,25) : datetime(2020,9,18)] + -1.75   
        fast_data['metek_10m']['metek_10m_incy']       .loc[datetime(2020,8,25) : datetime(2020,9,18)] = \
            fast_data['metek_10m']['metek_10m_incy']   .loc[datetime(2020,8,25) : datetime(2020,9,18)] + 2.
           
             
        if all([fast_data[k].empty for k in metek_inst_keys]):
            verboseprint(f"!!! No fast data available today... {today_str}!!! ")
        else:
            
            licor_data = fast_data['licor']
            licor_data['licor_pr'] = licor_data['licor_pr']*10 # [to hPa]

            # ~~~~~~~~~~~~~~~~~~~~~ (2) Quality control ~~~~~~~~~~~~~~~~~~~~~~~~
            print('... quality controlling the fast data now.')

            # I'm being a bit lazy here: no accouting for reasons data was rejected. For another day.
            # must use bitwise operators for boolean array declarations and the parenthesis around each
            # comparison are required this is a point where the python syntax gets a bit ridiculous IMO
            for inst in metek_inst_keys:
                # physically-possible limits
                met_T = fast_data[inst][inst+'_T']
                met_X = fast_data[inst][inst+'_x']
                met_Y = fast_data[inst][inst+'_y']
                met_Z = fast_data[inst][inst+'_z']

                fast_data[inst][inst+'_T'].mask( (met_T<T_thresh[0]) | (met_T>T_thresh[1]) , inplace=True)
                fast_data[inst][inst+'_x'].mask( np.abs(met_X) > ws_thresh[1]              , inplace=True)
                fast_data[inst][inst+'_y'].mask( np.abs(met_Y) > ws_thresh[1]              , inplace=True)
                fast_data[inst][inst+'_z'].mask( np.abs(met_Z) > ws_thresh[1]              , inplace=True)

                if inst != 'metek_mast': #mast, no inc dat
                    met_incx = fast_data[inst][inst+'_incx']
                    met_incy = fast_data[inst][inst+'_incy']
                    fast_data[inst][inst+'_incx'].mask(np.abs(met_incx) > incl_range[1], inplace=True)
                    fast_data[inst][inst+'_incy'].mask(np.abs(met_incy) > incl_range[1], inplace=True)


                # Some time periods have to be removed. In particular, the first week of Dec. It is a mess. 
                # The sonic was rotated over and over and I don't have any notes. I will also remove the set up in April
                if 'mast' in inst:
                    # The April setup
                    fast_data[inst][inst+'_T'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                    fast_data[inst][inst+'_x'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                    fast_data[inst][inst+'_y'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                    fast_data[inst][inst+'_z'].loc[datetime(2020,4,13,12,0,0):datetime(2020,4,14,10,0,0)] = nan
                    # The Dec re-setup
                    #fast_data[inst][inst+'_T'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                    #fast_data[inst][inst+'_x'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                    #fast_data[inst][inst+'_y'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan
                    #fast_data[inst][inst+'_z'].loc[datetime(2019,12,1,9,51,0):datetime(2019,12,9,7,29,0)] = nan



                # Diagnostic: break up the diagnostic and search for bad paths. the diagnostic
                # is as follows:
                # 1234567890123
                # 1000096313033
                #
                # char 1-2   = protocol stuff. 10 is actualy 010 and saying we receive instantaneous
                #              data from network. ignore
                # char 3-7   = data format. we use 96 = 00096
                # char 8     = heating operation mode. we set it to 3 = on but control internally for temp
                #              and data quality (ie dont operate the heater if you dont really have to)
                # char 9     = heating state, 0 = off, 1 = on, 2 = on but faulty
                # char 10    = number of unusable radial paths (max 9). we want this to be 0 and it is
                #              redundant with the next...
                # char 11-13 = percent of unusuable paths. in the example above, 3033 = 3 of 9 or 33% bad paths
                #
                # We want to strip off the last 3 digits here and remove data that are not all 0s.
                # To do this fast I will do it by subtracting off the top sig figs like below.
                # The minumum value is 1/9 so I will set the threhsold a little > 0 for slop in precision
                # We could set this higher. Perhaps 1 or 2 bad paths is not so bad? Not sure.
                if inst != 'metek_mast': 
                    bad_data = (fast_data[inst][inst+'_heatstatus']/1000\
                                -np.floor(fast_data[inst][inst+'_heatstatus']/1000)) >  max_bad_paths[0]
                    fast_data[inst][inst+'_x'].mask(bad_data, inplace=True)
                    fast_data[inst][inst+'_y'].mask(bad_data, inplace=True)
                    fast_data[inst][inst+'_z'].mask(bad_data, inplace=True)
                    fast_data[inst][inst+'_T'].mask(bad_data, inplace=True)
                elif inst == 'metek_mast':
                    # not sure what happened here, but I'm guessing icing following the melt
                    fast_data[inst][inst+'_x'].loc[datetime(2020,4,20,4,0,0):datetime(2020,4,22,0,0,0)] = nan 
                    fast_data[inst][inst+'_y'].loc[datetime(2020,4,20,4,0,0):datetime(2020,4,22,0,0,0)] = nan
                    fast_data[inst][inst+'_z'].loc[datetime(2020,4,20,4,0,0):datetime(2020,4,22,0,0,0)] = nan

            #
            # And now Licor ####################################################
            # Physically-possible limits
            T       = licor_data['licor_T']
            pr      = licor_data['licor_pr']
            h2o     = licor_data['licor_h2o']
            co2     = licor_data['licor_co2']
            co2_str = licor_data['licor_co2_str']

            licor_data['licor_T']  .mask( (T<T_thresh[0])  | (T>T_thresh[1]) , inplace=True) 
            licor_data['licor_pr'] .mask( (pr<p_thresh[0]) | (pr>p_thresh[1]), inplace=True)
            licor_data['licor_h2o'].mask( (h2o<lic_h2o[0]) | (h2o>lic_h2o[1]), inplace=True)
            licor_data['licor_co2'].mask( (co2<lic_co2[0]) | (co2>lic_co2[1]), inplace=True)

            # CO2 signal strength is a measure of window cleanliness applicable to CO2 and H2O vars
            licor_data['licor_co2'].mask( (co2_str<lic_co2sig_thresh[0]),  inplace=True)
            licor_data['licor_h2o'].mask( (co2_str<lic_co2sig_thresh[0]),  inplace=True)

            # The diagnostics are boolean and were decoded in level1
            pll           = licor_data['licor_pll']
            detector_temp = licor_data['licor_dt']
            chopper_temp  = licor_data['licor_ct']
            # Phase Lock Loop. Optical filter wheel rotating normally if 1, else "abnormal"
            bad_pll = pll == 0
            # If 0, detector temp has drifted too far from set point. Should yield a bad calibration, I think
            bad_dt = detector_temp == 0
            # Ditto for the chopper housing temp
            bad_ct = chopper_temp == 0

            # Get rid of diag QC failures
            licor_data['licor_h2o'][bad_pll] = nan
            licor_data['licor_co2'][bad_pll] = nan
            licor_data['licor_h2o'][bad_dt]  = nan
            licor_data['licor_co2'][bad_dt]  = nan
            licor_data['licor_h2o'][bad_ct]  = nan
            licor_data['licor_co2'][bad_ct]  = nan

            # Despike: looking for big spikes right now for the slow data but will use Fairall et al. despik.m on 10 min intervals in turbulence code
            #   Here screens +/-5 m/s outliers relative to a running 1 min median
            #   args go like return = despike(input,oulier_threshold_in_m/s,window_length_in_n_samples)
            #   !!!! Replaces failures with the median of the window !!!!
            for inst in metek_inst_keys:
                fast_data[inst][inst+'_x'] = fl.despike(fast_data[inst][inst+'_x'],5,1200,'yes')
                fast_data[inst][inst+'_y'] = fl.despike(fast_data[inst][inst+'_y'],5,1200,'yes')
                fast_data[inst][inst+'_z'] = fl.despike(fast_data[inst][inst+'_z'],5,1200,'yes')
                fast_data[inst][inst+'_T'] = fl.despike(fast_data[inst][inst+'_T'],5,1200,'yes')

            # There are bad measurements right on the edge of radpidly changing co2_str where co2_str is
            # high enough not to be screen out, but is still changeing, e.g., after cleaning. This is an attempt
            # to screen that out and hopefully it doesn't overdo it. The threshold translates to 1% per 30 min. 
            bad_licor = fl.despike(licor_data['licor_co2_str'],1,36000,'ret')        
            licor_data['licor_co2'][bad_licor==True] = nan
            licor_data['licor_h2o'][bad_licor==True] = nan
            licor_data['licor_T'][bad_licor==True] = nan
            licor_data['licor_pr'][bad_licor==True] = nan

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
                metek_10hz = fast_data[inst].resample('100ms').mean()
                fast_data_10hz[inst] = metek_10hz.reindex(index=Hz10_today, method='nearest', tolerance='50ms')


            licor_10hz = licor_data.resample('100ms').mean()
            licor_10hz = licor_10hz.reindex(index=Hz10_today)

            # ~~~~~~~~~~~~~~~~~ (4) Do the Tilt Rotation  ~~~~~~~~~~~~~~~~~~~~~~
            print("... cartesian tilt rotation. Translating body -> earth coordinates.")
            # This really only affects the slow interpretation of the data.  When we do the fluxes it will be
            # a double rotation into the streamline that implicitly accounts for deviations between body and earth
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
            #             psi     =  azimuth        is about the z axis. the inclinometer does not measure this
            #                                       despite what the manual may say (it's "aspirational").
            #             metek y -> earth u, +North
            #             metek x -> earth v, +West
            #             Have a look also at pg 21-23 of NEW_MANUAL_20190624_uSonic-3_Cage_MP_Manual for
            #             metek conventions. Pg 21 seems to have errors in the diagram?
            for inst in metek_inst_keys:

                # Tower.
                # If we are working with the tower sonics, the calculation is straightforward. 
                # Inclinomters and heading used to rotate from body to earth coordinates
                # Heading uses a filtered value to reduce noise, which was calculated earlier in this code
                if 'mast' not in inst:
                    th = logger_today['tower_heading'].reindex(index=fast_data_10hz[inst].index).interpolate()  
                    
                    # if prior to raise day, we need to use some manual offsets from the tower heading
                    date_twr_raised = datetime(2019, 10, 24, 5, 30)  # instrument heights after tower raised
                    if today < ( date_twr_raised - timedelta(hours=date_twr_raised.hour, minutes=date_twr_raised.minute, seconds=date_twr_raised.second) ) + timedelta(days=1):
                        th2 = twr_manual_hdg_data[inst]['tower_heading'].reindex(index=th.index,method='pad').interpolate()
                        th = th.fillna(value=th2)
                        logger_today['tower_heading'].fillna(value=291.3) # the tower frame of reference will be persisted back from when it was first raised

                    if (datetime(2020,6,27,9,20) < today < datetime(2020,7,29,8,30)) and inst == 'metek_6m': 
                        th = th + 7.4 # adjust tower heading for only six meter metek on leg 4
                        th = np.mod(th, 360) # ? necessary? or tilt_rotation() take care of this?

                    ct_u, ct_v, ct_w = fl.tilt_rotation(fast_data_10hz[inst] [inst+'_incy'],
                                                        fast_data_10hz[inst] [inst+'_incx'],
                                                        th, 
                                                        fast_data_10hz[inst] [inst+'_y'], # y -> u on uSonic!
                                                        fast_data_10hz[inst] [inst+'_x'], # x -> v on uSonic!
                                                        fast_data_10hz[inst] [inst+'_z'])

                # Mast, three eras: ~ Leg 1, Leg 2 and Leg 3 with some additional complexities in Leg 1.        
                elif 'mast' in inst:

                    # This is Leg 1 and 2.  We use information available and interpolate between.
                    if today < datetime(2020,3,12,0,0):   
                        # interpolate the mast alignment metadata for today
                        most_recent_gps = mast_hdg_df['gps_hdg'].reindex(index=fast_data_10hz[inst].index,method='pad')
                        most_recent_mast = mast_hdg_df['mast_hdg'].reindex(index=fast_data_10hz[inst].index,method='pad')
                        mast_align = most_recent_gps - most_recent_mast   
                        if today >  mast_hdg_df.index[-2]: # if we are in leg 1 pad, but lineraly interp thru leg 2
                            meth = 'linear'
                        else:
                            meth = 'pad' 

                        mast_hdg_series = np.mod(logger_today['tower_heading'].reindex(index=fast_data_10hz[inst].index).interpolate()-mast_align,360).astype('float')                    

                        # if we are working on the mast but we don't have a v102 we have to set to missing
                        # values, although we can report our estiamte of the heading
                        logger_today['lat_mast']=np.zeros(len(logger_today['lat_tower']))+def_fill_flt 
                        logger_today['lon_mast']=np.zeros(len(logger_today['lon_tower']))+def_fill_flt 
                        logger_today['mast_ice_alt']=np.zeros(len(logger_today['tower_ice_alt']))+def_fill_flt 
                        logger_today['mast_heading']=mast_hdg_series.reindex(index=seconds_today)

                    # This is the Newdle in Leg 3. 
                    #   A "spare" v102 was used so the heading is tracked directly. 
                    #   The mast and tower are not on the same piece of ice, so that tower cannot be
                    #   used as reference for the mast at all.    
                    elif today > datetime(2020,4,14,0,0) and today < datetime(2020,5,12,0,0):             
                        # set to 68.5 from calcs416.py 
                        mast_align = 68.5
                        mast_hdg_series = np.mod(logger_today['mast_heading'].reindex(index=fast_data_10hz[inst].index).interpolate()-mast_align,360) 
                        # also, set the heading for the file
                        logger_today['mast_heading'] = np.mod(logger_today['mast_heading']-mast_align,360)

                    # part of leg 3, leg 4 and 5 the mast stays packed away safely in cold storage
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

                # reassign corrected vals in meteorological convention
                fast_data_10hz[inst][inst+'_x'] = ct_v  # met v = postivie northward
                fast_data_10hz[inst][inst+'_y'] = ct_u  # met u = positive eastward
                fast_data_10hz[inst][inst+'_z'] = ct_w

                # start referring to xyz as uvw now
                fast_data_10hz[inst].rename(columns={inst+'_y' : inst+'_v',
                                                     inst+'_x' : inst+'_u',
                                                     inst+'_z' : inst+'_w',
                                                     }, errors="raise", inplace=True) 
    
                # ######################################################################################
                # corrections to the high frequency component of the turbulence spectrum... the metek
                # sonics used seem to have correlated cross talk between T and w that results in biased
                # flux values with a dependency on frequency...
                #
                # this correction fixes that and is documented in the data paper, see comments in
                # functions_library
                fast_data_10hz[inst] = fl.fix_high_frequency(fast_data_10hz[inst], inst+'_')

            # now we recalculate the 1 min average wind direction and speed from the
            # u and v velocities in meteorological  convention
            print("... calculating a corrected set of slow wind speed and direction.")
            metek_ws = {}
            metek_wd = {}
            for inst in metek_inst_keys:
                u_min = fast_data_10hz[inst] [inst+'_u'].resample('1T',label='left').apply(fl.take_average)
                v_min = fast_data_10hz[inst] [inst+'_v'].resample('1T',label='left').apply(fl.take_average)
                ws = np.sqrt(u_min**2+v_min**2)
                wd = np.mod((np.arctan2(-u_min,-v_min)*180/np.pi),360)
                metek_ws[inst] = ws
                metek_wd[inst] = wd

            # ~~~~~~~~~~~~~~~~~~ (5) Recalculate Stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # !!  Sorry... This is a little messed up. The original stats are read from the NOAA Services stats
            # files, contents calculated from the raw data. But we have QC'd the data and changed the raw
            # values, so we need to update the stats. I do that here. But then was there ever any point in
            # reading the stats data in the first place? nope! and now we don't
            metek_stats = {}
            print('... recalculating the NOAA Services style stats data; corrected, rotated, and quality controlled')

            inst_dict = {}
            inst_dict['metek_2m']   = '2m'   
            inst_dict['metek_6m']   = '6m'   
            inst_dict['metek_10m']  = '10m'  
            inst_dict['metek_mast'] = 'mast' 

            for inst in metek_inst_keys:
                height = inst_dict[inst]
                
                metek_stats[inst] = pd.DataFrame()
                metek_stats[inst]['wspd_vec_mean_'+height] = metek_ws[inst]
                metek_stats[inst]['wdir_vec_mean_'+height] = metek_wd[inst]

                metek_stats[inst]['wspd_u_mean_'+height] = \
                    fast_data_10hz[inst][inst+'_u'].resample('1T',label ='left').mean()

                metek_stats[inst]['wspd_v_mean_'+height] = \
                    fast_data_10hz[inst][inst+'_v'].resample('1T',label ='left').mean()

                metek_stats[inst]['wspd_w_mean_'+height] = \
                    fast_data_10hz[inst][inst+'_w'].resample('1T',label ='left').mean()

                metek_stats[inst]['temp_acoustic_mean_'+height] = \
                    fast_data_10hz[inst][inst+'_T'].resample('1T',label ='left').mean()

                metek_stats[inst]['wspd_u_std_'+height] = \
                    fast_data_10hz[inst][inst+'_u'].resample('1T',label ='left').std()

                metek_stats[inst]['wspd_v_std_'+height] = \
                    fast_data_10hz[inst][inst+'_v'].resample('1T',label ='left').std()

                metek_stats[inst]['wspd_w_std_'+height] = \
                    fast_data_10hz[inst][inst+'_w'].resample('1T',label ='left').std()

                metek_stats[inst]['temp_acoustic_std_'+height] = \
                    fast_data_10hz[inst][inst+'_T'].resample('1T',label ='left').std()

            # Each mean is followed by a screeening that rejects mean containing < 50% (300/600 10Hz samples
            # per minute) of valid (non nan) data. I do this for licor but not for metek (above) because in
            # licor this is associated with time when optics and sensor temepratures are at the edge of
            # acceptable limits but are still recording spurious data, perhaps becausse there is a change
            # undeerway (eg, signal strength changing after cleaning as ethanol evaporates). This causes a
            # bias in licor. In metek it probably just means noise and most <50% valid samples are casued by
            # attenutation from blowing snow where the samples that do appear in the window are still "good".
            licor_stats                     = pd.DataFrame()
            licor_stats['h2o_licor']        = licor_10hz['licor_h2o']     .resample('1T',label='left').mean()
            licor_stats['co2_licor']        = licor_10hz['licor_co2']     .resample('1T',label='left').mean()
            licor_stats['temp_licor']       = licor_10hz['licor_T']       .resample('1T',label='left').mean()
            licor_stats['pressure_licor']         = licor_10hz['licor_pr']      .resample('1T',label='left').mean()
            licor_stats['co2_signal_licor'] = licor_10hz['licor_co2_str'] .resample('1T',label='left').mean()

            licor_stats['co2_licor'][(licor_10hz['licor_co2']*0+1) .resample('1T',label='left').sum() < 300] = nan         
            licor_stats['h2o_licor'][(licor_10hz['licor_h2o']*0+1) .resample('1T',label='left').sum() < 300] = nan  
            licor_stats['temp_licor'][(licor_10hz['licor_T']*0+1)  .resample('1T',label='left').sum() < 300] = nan        
            licor_stats['pressure_licor'][(licor_10hz['licor_pr']*0+1)   .resample('1T',label='left').sum() < 300] = nan        
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
            # turbulence_data = fl.grachev_fluxcapacitor(sz, sonic_data, licor_data,
            #                                            h2o_units, co2_units, p, t, q, verbose=v)
            #       sz = instrument height
            #       sonic_data = dataframe of u,v,w winds
            #       licor_data = dataframe of h2o adn co2
            #       h2o_units = units of licor h2o, e.g., 'mmol/m3'
            #       co2_units = units of licor co2, e.g., 'mmol/m3'
            #       p = pressure in hPa, scaler
            #       t = air temperature in C, scaler
            #       q = vapor mixing ratio, scaler
            turb_data_dict = {}

            # calculate before loop, used to modify height offsets below to be 'more correct'
            # snow depth calculation shouldn't/doesn't fail but catch the exception just in case
            try: 
                snow_depth = slow_data['snow_depth'][seconds_today].copy()  # get snow_depth, heights evolve in time
                snow_depth[(np.abs(stats.zscore(snow_depth.values)) < 3)]   # remove weird outliers
                snow_depth = snow_depth*0.01                                # convert to meters
                snow_depth = snow_depth.rolling(600, min_periods=10).mean() # fill nans for bulk calc only
            except Exception as ex: 
                print(f"... calculating snow depth for {today} failed for some reason... ")
                snow_depth = pd.Series(0, index=slow_data[seconds_today].index)

            for win_len in range(0,len(integ_time_step)):
                turb_data       = pd.DataFrame()    
                flux_freq       = '{}T'.format(integ_time_step[win_len])
                flux_time_today = pd.date_range(today, today+timedelta(1), freq=flux_freq)
                suffix_list     = ['_2m','_6m','_10m','_mast'] # suffix for vars in turb file

                # a DatetimeIndex based on integ_time_step, the integration window
                # for the calculations that is defined at the top  of the code

                turb_winds = {}

                for i_inst, inst in enumerate(metek_inst_keys):
                    verboseprint("... processing turbulence data for {}".format(inst))

                    # recalculate wind vectors to be saved with turbulence data  later
                    height = inst_dict[inst]
                    u_min  = fast_data_10hz[inst] [inst+'_u'].resample(flux_freq,label='left').apply(fl.take_average)
                    v_min  = fast_data_10hz[inst] [inst+'_v'].resample(flux_freq,label='left').apply(fl.take_average)
                    ws     = np.sqrt(u_min**2+v_min**2)
                    wd     = np.mod((np.arctan2(-u_min,-v_min)*180/np.pi),360)

                    turb_winds[inst] = pd.DataFrame()
                    turb_winds[inst]['wspd_vec_mean_'+height] = ws
                    turb_winds[inst]['wdir_vec_mean_'+height] = wd

                    for time_i in range(0,len(flux_time_today)-1): # flux_time_today = 
                        # Get the index, ind, of the metek frame that pertains to the present calculation 
                        # indswrite = (fast_data_10hz[inst].index >= flux_time_today[time_i]) \
                        #        & \
                        #        (fast_data_10hz[inst].index < flux_time_today[time_i+1]) 

                        # Get the index, ind, of the metek frame that pertains to the present calculation A
                        # little tricky. We need to make sure we give it enough data to encompass the nearest
                        # power of 2: for 30 min fluxes this is ~27 min so you are good, but for 10 min
                        # fluxes it is 13.6 min so you need to give it more.
                        # 
                        # We buffered the 10 Hz so that we can go outside the edge of "today" by up to an
                        # hour. It's a bit of a formality, but for general cleanliness we are going to center
                        # all fluxes to the nearest min so that e.g,
                        # 
                        # 12:00-12:10 is actually 11:58 through 12:12
                        # 12:00-12:30 is actually 12:01 through 12:28   

                        # @10Hz, min needed to cover the nearet po2 [minutes]
                        po2_len = np.ceil(2**round(np.log2(integ_time_step[win_len]*60*10))/10/60) 
                        t_win = pd.Timedelta((po2_len-integ_time_step[win_len])/2,'minutes')
                        calc_data = fast_data_10hz[inst].loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].copy()

                        # get the licor data. we will just pass it through for every height as a placeholder,
                        # but only save the output for the right height. the decision doesnt need to be in
                        # the loop, but at least it is findable
                        licor_data = licor_10hz.loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].copy()  
                        if licor_z > 8: 
                            use_this_licor = suffix_list[2]
                        elif licor_z > 4 and licor_z < 8: 
                            use_this_licor = suffix_list[1] 
                        elif licor_z < 4:
                            use_this_licor = suffix_list[0]
                        else: # nan
                            use_this_licor = '_2m'

                        # we need pressure and temperature these are just for calculation of constants so the
                        # 2m data should be close enough...the original code assumed a nominal pressure and
                        # used sonic temperature...
                        Pr_time_i = logger_today['atmos_pressure_2m'].loc[flux_time_today[time_i]\
                                                                           -t_win:flux_time_today[time_i+1]+t_win].mean()
                        T_time_i = logger_today['temp_2m'].loc[flux_time_today[time_i]\
                                                                      -t_win:flux_time_today[time_i+1]+t_win].mean()
                        Q_time_i = logger_today['mixing_ratio_2m'].loc[flux_time_today[time_i]\
                                                                    -t_win:flux_time_today[time_i+1]+t_win].mean()/1000

                        # make the turbulent flux calculations via Grachev module
                        if args.verbose: v = True;
                        else: v = False

                        # give generic names for calculations and select the desired indexes
                        calc_data.rename(columns={inst+'_u' : 'u',
                                            inst+'_v' : 'v',
                                            inst+'_w' : 'w',
                                            inst+'_T' : 'T',
                                            }, errors="raise", inplace=True)
                        if 'mast' not in inst: sz = sonic_z[i_inst]
                        else: sz = mast_sonic_height
                        data = fl.grachev_fluxcapacitor(sz, calc_data, licor_data, 'mmol/m3', 'mmol/m3',
                                                        Pr_time_i, T_time_i, Q_time_i, verbose=v)

                        # Sanity check on Cd. Ditch the whole run if it fails
                        #data[:].mask( (data['Cd'] < cd_lim[0])  | (data['Cd'] > cd_lim[1]) , inplace=True)
                        data = data.add_suffix(suffix_list[i_inst])                                        

                        # doubtless there is a better way to initialize this
                        if time_i == 0: inst_data = data
                        else: inst_data = inst_data.append(data)


                        # now add the indexer datetime doohicky

                    verboseprint("... concatting turbulence calculations to one dataframe")
                    inst_data.index = flux_time_today[0:-1]
                    turb_data = pd.concat( [turb_data, inst_data, turb_winds[inst]], axis=1) # concat columns alongside each other 

                    # ugh. there are 2 dimensions to the spectral variables, but the spectra are
                    # smoothed. The smoothing routine is a bit strange in that is is dependent on the length
                    # of the window (to which it should be orthogonal!) and worse, is not obviously
                    # predictable...it grows in a for loop nested in a while loop that is seeded by a counter
                    # and limited by half the length of the window, but the growth is not entirely
                    # predictable and neither is the result so I can't preallocate the frequency vector. I
                    # need to talk to Andrey about this and I need a programatic solution to assigning a
                    # frequency dimension when pandas actually treats that dimension indpendently along the
                    # time dimension. I will search the data frame for instances of a frequency dim then
                    # assign times without it nan of that length. for days without a frequency dim I will
                    # assign it to be length of 2 arbitrarily so that the netcdf can be written. This is
                    # ugly.

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

                    # (2) if missing times were found, fill with nans of the freq length you discovered. this
                    # happens on days when the instruents are turned on and also perhaps runs when missing
                    # data meant the flux_capacitor returned for lack of inputs 
                    if f_dim_len > 0 and any(missing_f_dim_ind):
                        
                        # case we have no data we need to remake a nominal fs as a filler
                        if 'fs' not in locals(): 
                            fs = pd.DataFrame(np.zeros((60,1)),columns=['fs'])
                            fs = fs['fs']*nan
                        
                        
                        for ii in range(0,len(missing_f_dim_ind)):
                            # these are the array with multiple dims...  im filling the ones that are missing
                            # with nan (of fs in the case of fs...) such that they can form a proper and
                            # square array for the netcdf
                            turb_data['fs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]   = fs
                            turb_data['sUs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]  = fs*nan
                            turb_data['sVs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]  = fs*nan
                            turb_data['sWs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]  = fs*nan
                            turb_data['sTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]  = fs*nan
                            turb_data['sqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]  = fs*nan
                            turb_data['scs'+suffix_list[i_inst]][missing_f_dim_ind[ii]]  = fs*nan
                            turb_data['cWUs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cWVs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cWTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cUTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cVTs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cWqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cUqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cVqs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cWcs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cUcs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cVcs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan
                            turb_data['cUVs'+suffix_list[i_inst]][missing_f_dim_ind[ii]] = fs*nan

                # now reassign the naming convention for the licor stuff
                turb_data['Hl']            = turb_data['Hl'            +use_this_licor]
                turb_data['Hl_Webb']       = turb_data['Hl_Webb'       +use_this_licor]
                turb_data['CO2_flux']      = turb_data['CO2_flux'      +use_this_licor]
                turb_data['CO2_flux_Webb'] = turb_data['CO2_flux_Webb' +use_this_licor]
                turb_data['nSq']           = turb_data['nSq'           +use_this_licor]
                turb_data['nSc']           = turb_data['nSc'           +use_this_licor]
                turb_data['Wq_csp']        = turb_data['Wq_csp'        +use_this_licor]
                turb_data['Uq_csp']        = turb_data['Uq_csp'        +use_this_licor]
                turb_data['Vq_csp']        = turb_data['Vq_csp'        +use_this_licor]
                turb_data['Wc_csp']        = turb_data['Wc_csp'        +use_this_licor]
                turb_data['Uc_csp']        = turb_data['Uc_csp'        +use_this_licor]
                turb_data['Vc_csp']        = turb_data['Vc_csp'        +use_this_licor]
                turb_data['sqs']           = turb_data['sqs'           +use_this_licor]
                turb_data['scs']           = turb_data['scs'           +use_this_licor]
                turb_data['cWqs']          = turb_data['cWqs'          +use_this_licor]
                turb_data['cUqs']          = turb_data['cUqs'          +use_this_licor]
                turb_data['cVqs']          = turb_data['cVqs'          +use_this_licor]
                turb_data['cWcs']          = turb_data['cWcs'          +use_this_licor]
                turb_data['cUcs']          = turb_data['cUcs'          +use_this_licor]
                turb_data['cVcs']          = turb_data['cVcs'          +use_this_licor]
                turb_data['Deltaq']        = turb_data['Deltaq'        +use_this_licor]           
                turb_data['Deltac']        = turb_data['Deltac'        +use_this_licor]

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
                empty_data = np.zeros(np.size(slow_data['mixing_ratio_10m'][seconds_today]))
                bulk_input = pd.DataFrame()
                bulk_input['u']  = ws[seconds_today]                                 # wind speed                (m/s)
                bulk_input['t']  = slow_data['temp_10m'][seconds_today]              # air temperature           (degC) 
                bulk_input['Q']  = slow_data['mixing_ratio_10m'][seconds_today]/1000 # air moisture mixing ratio (kg/kg)
                bulk_input['zi'] = empty_data+600                                    # inversion height          (m) guess!
                bulk_input['P']  = slow_data['atmos_pressure_2m'][seconds_today]     # surface pressure          (mb)


                bulk_input['zu'] = 10.54-snow_depth # height of anemometer      (m)
                bulk_input['zt'] = 9.34-snow_depth  # height of thermometer     (m)
                bulk_input['zq'] = 9.14-snow_depth  # height of hygrometer      (m)      
                
                bulk_input['ts'] = slow_data['skin_temp_surface'][seconds_today]     # bulk water/ice surface temp (degC) 

                bulk_input = bulk_input.resample(str(integ_time_step[win_len])+'min',label='left').apply(fl.take_average)

                # output dataframe
                empty_data = np.zeros(len(bulk_input))
                bulk = pd.DataFrame() 
                bulk['bulk_Hs_10m']      = empty_data*nan # hsb: sensible heat flux             (Wm-2)
                bulk['bulk_Hl_10m']      = empty_data*nan # hlb: latent heat flux               (Wm-2)
                bulk['bulk_tau']         = empty_data*nan # tau: stress                         (Pa)
                bulk['bulk_z0']          = empty_data*nan # zo: roughness length, veolicity     (m)
                bulk['bulk_z0t']         = empty_data*nan # zot:roughness length, temperature   (m)
                bulk['bulk_z0q']         = empty_data*nan # zoq: roughness length, humidity     (m)
                bulk['bulk_L']           = empty_data*nan # L: Obukhov length                   (m)       
                bulk['bulk_ustar']       = empty_data*nan # usr: friction velocity              (sqrt(momentum flux)), ustar (m/s)
                bulk['bulk_tstar']       = empty_data*nan # tsr: temperature scale, tstar       (K)
                bulk['bulk_qstar']       = empty_data*nan # qsr: specific humidity scale, qstar (kg/kg?)
                bulk['bulk_dter']        = empty_data*nan # dter
                bulk['bulk_dqer']        = empty_data*nan # dqer
                bulk['bulk_Hl_Webb_10m'] = empty_data*nan # hl_webb: Webb density-corrected Hl  (Wm-2)
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
                    tmp = [bulk_input['u'][ii],bulk_input['ts'][ii],bulk_input['t'][ii],bulk_input['Q'][ii],
                           bulk_input['zi'][ii],bulk_input['P'][ii],bulk_input['zu'][ii],bulk_input['zt'][ii],bulk_input['zq'][ii]] 
                    if not any(np.isnan(tmp)):
                        bulkout = fl.cor_ice_A10(tmp)
                        for hh in range(len(bulkout)):
                            if bulkout[13] < cd_lim[0] or bulkout[13] > cd_lim[1]:  # Sanity check on Cd. Ditch the whole run if it fails
                                bulk[bulk.columns[hh]][ii]=nan  # for some reason this needs to be in a loop
                            else:
                                bulk[bulk.columns[hh]][ii]=bulkout[hh]

                # qc/flagging algorithm for turbulence calculations, this should likely be ripped out and put into
                # functions_library once the qc-ing is satisfactorily performed....  similar to a despiker but based on
                # derivatives and flags these values as -1 in case we want to use them in an algorithmic approach if you list
                # a variable here, the associated *_qc var will created and then flagged according to the algorithm
                def flag_swings(vals, threshold=5):  
                    # put in by Michael, takes into account variance (invariant iqr) and flags large swings away
                    # from that variance at a certain threshold. right now as -1
                    def get_iqr(arr):
                        q75, q25 = np.nanpercentile(arr, [75 ,25])
                        iqr = q75 - q25; return iqr

                    window_size = 24; sym = int(window_size/2) # window to calculate variance/iqr over
                    mean_vals = vals.rolling(sym, win_type='gaussian', center=True, min_periods=1).mean(std=3)
                    new_vals = vals-mean_vals
                    try: 
                        iqr  = get_iqr(new_vals)
                        iqrs  = vals*np.nan
                        means = vals*np.nan
                        for i,v in enumerate(new_vals) : 
                            if i < sym:
                                iqrs[i] = get_iqr(new_vals[0:i+sym])
                            elif i > len(new_vals)-sym :
                                iqrs[i] = get_iqr(new_vals[i-sym:len(new_vals)-1])
                            else:
                                iqrs[i] = get_iqr(new_vals[i-sym:i+sym])

                    except: return vals*0
                    diffs     = vals*np.nan
                    diffs[1:] = np.diff(new_vals)
                    qc_vals   = np.array([-1 if d > iqr*threshold else 0 for i,d in enumerate(diffs)])

                    return qc_vals, iqrs, diffs, new_vals

                print("... running turbulence qc algorithm...")
                height_list = ['2m', '6m', '10m', 'mast']
                vars_to_flag = ['sigU', 'sigV', 'sigW', 'ustar']
                for h in height_list: 
                    for v in vars_to_flag: 
                        var_name = f'{v}_{h}'
                        turb_data[f'{var_name}_qc'] = flag_swings(turb_data[var_name], 6)[0]
                print("... FINISHED turbulence qc algorithm...")

                # add this to the EC data
                turb_data = pd.concat( [turb_data, bulk], axis=1) # concat columns alongside each other without adding indexes
                turb_data_dict[win_len] = turb_data.copy()
                
        verboseprint('... writing to level2 netcdf files and calcuating averages for day: {}'.format(today))

        # for level2 we are only writing out 1minute+ files so we
        vector_vars = [] # these come from metek stats, leaving but vestigial
        angle_vars  = ['tower_heading', 'ship_bearing', 'mast_heading']

        l2_atts, l2_cols = define_level2_variables(); qc_atts, qc_cols = define_qc_variables(include_turb=True)
        l2_cols = l2_cols+qc_cols

        logger_list = []
        for ivar, var_name in enumerate(logger_today.columns):
            fstr = f'1T' # pandas notation for timestep

            # this was copied from the 10min debugging, not all these
            # vars are actually in the 1 second logger_today dataframe
            try: 
                if var_name.split('_')[-1] == 'qc':
                    logger_list.append(fl.average_mosaic_flags(logger_today[var_name], fstr))
                elif any(substr in var_name for substr in angle_vars):
                    logger_list.append(logger_today[var_name].resample(fstr, label='left').apply(fl.take_average, is_angle=True))
                else:
                    logger_list.append(logger_today[var_name].resample(fstr, label='left').apply(fl.take_average))

            except Exception as e: 
                print("... this should never happen, why did it?\n {e}\n\n")
                import traceback
                import sys
                print(traceback.format_exc())
                raise

        logger_1min = pd.concat(logger_list, axis=1)

        try: l2_data = pd.concat([logger_1min, stats_data], axis=1)
        except UnboundLocalError: l2_data = logger_1min # there was no fast data, rare

        # run qc on wind sector for 1 minute data
        onemin_data = qc_tower_winds(l2_data.copy(), ship_df[today:tomorrow]) # ship_df necessary for calculating ship->mast vector

        # write out all the hard work that we've done at native resolution
        write_level2_10hz(fast_data_10hz.copy(), licor_10hz.copy(), today)
        write_level2_netcdf(onemin_data, today, "1min")

        # now resample variables at specified turbulence integration timestep, currently only 10 minutes
        for win_len in range(0,len(integ_time_step)):

            data_list = []


            for ivar, var_name in enumerate(l2_cols):
                fstr = f'{integ_time_step[win_len]}T' # pandas notation for timestep
                
                try: 
                    if var_name.split('_')[-1] == 'qc':
                        data_list.append(fl.average_mosaic_flags(l2_data[var_name], fstr))
                    elif any(substr in var_name for substr in vector_vars):
                        data_list.append(turb_data[var_name]) 
                    elif any(substr in var_name for substr in angle_vars):
                        data_list.append(l2_data[var_name].resample(fstr, label='left').apply(fl.take_average, is_angle=True))
                    else:
                        data_list.append(l2_data[var_name].resample(fstr, label='left').apply(fl.take_average))
                except Exception as e: 
                    # this is a little silly, data didn't exist for var fill with nans
                    print(f"... wait what/why/huh??? {var_name} {e}")
                    data_list.append(pd.Series([np.nan]*len(l2_data), index=l2_data.index, name=var_name)\
                                     .resample(fstr, label='left').apply(fl.take_average))

            avged_data = pd.concat(data_list, axis=1)
            avged_data = avged_data[today:tomorrow]

            # run qc on wind sector for 10 minute data 
            try: 
                

                avged_data = qc_tower_winds(avged_data, ship_df[today:tomorrow].resample(fstr,label='left').apply(fl.take_average))
                # for debugging the write function.... ugh
                if we_want_to_debug:
                    import pickle
                    pickle_args = [avged_data.copy(), turb_data_dict[win_len], today, f"{integ_time_step[win_len]}min"]
                    pkl_file = open(f'./tests/{today.strftime("%Y%m%d")}_pre-qc_data.pkl', 'wb')
                    pickle.dump(pickle_args, pkl_file)
                    pkl_file.close()

                avged_data, turb_data = qc_tower_turb_data(avged_data, turb_data_dict[win_len].copy())

                write_level2_netcdf(avged_data.copy(), today, f"{integ_time_step[win_len]}min", turb_data[today:tomorrow])

            except: 
                print(f"!!! failed to qc and write turbulence data for {win_len} on {today} !!!")
                print("==========================================================================================")
                print("Python traceback: \n\n")
                import traceback
                import sys
                print(traceback.format_exc())
                print("==========================================================================================")
                #print(sys.exc_info()[2])

        print(f"... finally finished with day {today_str}, returning worker process to parent")
        day_q.put(True); return
            
    # #########################################################################################
    # here's where we actually call the data crunching function, processing days sequentially
    day_series = pd.date_range(start_time, end_time)
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    q_list = []  # setup queue storage
    for i_day, today in enumerate(day_series): # loop over the days in the processing range and crunch away
        tomorrow        = today+day_delta
        slow_data_today = slow_data[today:tomorrow]

        q_today = Q()
        P(target=process_day, args=(today, tomorrow, slow_data_today, q_today)).start()
        q_list.append(q_today)

        if (i_day+1) % nthreads == 0 or today == day_series[-1]:
            for qq in q_list: qq.get()
            q_list = []

    printline()
    print('All done! Netcdf output files can be found in: {}'.format(level2_dir))
    print(version_msg)
    printline()

def compare_indexes(inds_sparse, inds_lush, guess_jump = 50):
    inds_not_present = [] 
    map_between = ([],[]) # tuple of matching indexes

    sl = len(inds_sparse)

    # we assume monotonicity
    if not inds_sparse.is_monotonic_increasing or not inds_lush.is_monotonic_increasing:
        raise Exception("indexes not sorted")

    sparse_i = 0; old_perc = 0 


    print("")
    n_missed_but_not_really = 0 
    range_inds = iter(range(len(inds_sparse)))
    #for lush_i in range_inds:
    for sparse_i in range_inds:
        
        if sparse_i % 1000 == 0: print(f"... aligning {round((sparse_i/sl)*100,4)}% of ARM/flux data", end='\r')

        sparse_date = inds_sparse[sparse_i] # get the actual timestamp to compare
        try: 
            lush_i = inds_lush.get_loc(sparse_date)
            map_between[0].append(lush_i)
            map_between[1].append(sparse_i)
        except Exception:
            inds_not_present.append(sparse_date)

    print(f"...  aligned 100.000% of ARM/flux \n", end='\r')

    #print(f"!!!!!! there were these indexes weirdly skipped {n_missed_but_not_really} !!!!!!!!!")
    return inds_not_present, map_between

def fast_concat_dfs(df_list):
    from pandas.core.indexes.api import union_indexes
    all_cols = union_indexes([df.columns for df in df_list])
    dfs = (df.reindex(columns=all_cols) for df in df_list)
    print("... concatting large DFs, will take some time")
    combined = pd.concat(dfs)

    # now we have to have a function that merges the duplicated indexes:
    def ind_agg(group_series):
        if(len(group_series)>1):
            if (group_series.notna().sum() > 1):
                print("!!!! this should never happen!!!!")
            else:
                return group_series.sum()
        else:
            return group_series.sum()

    print("... combining large DF indexes")
    combined.groupby(combined.index).agg(ind_agg)
    print("... done large DFs!!!")
    return 
    

def get_fast_data(date, data_dir):

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

    data_atts, data_cols = define_level1_fast()

    level1_dir = data_dir+'/tower/1_level_ingest/'                                  # where does level1 data live?
    file_dir   = level1_dir

    date_str = date.strftime('%Y%m%d.%H%M%S')
    file_name = f'mosflxtowerfast.level1.{date_str}.nc'
    file_str = '{}/{}'.format(file_dir,file_name)

    if not os.path.isfile(file_str): 
        print('... no fast data on {}, file {} not found !!!'.format(date, file_name))
        return pd.DataFrame()

    # sometimes xarray throws exceptions on first try, had no time to debug it yet:
    try:
        xarr_ds = xr.open_dataset(file_str)

    except Exception as e:
        print("!!! xarray exception: {}".format(e))
        print("!!! file: {}".format(file_str))
        print("!!! this means there was no data in this file^^^^")
        nan_row   = np.ndarray((1,len(data_cols)))*nan
        nan_frame = pd.DataFrame(nan_row, columns=data_cols, index=pd.DatetimeIndex([date]))
        return nan_frame

    print("... converting level1 fast data to dataframe, takes a second")
    
    # we can't call to_dataframe on full dataset, numpy doesn't like creating insanely large arrays:
    # https://github.com/pydata/xarray/issues/838
    df_dict = {}
    for inst_name, search_str in inst_dict.items():
        tmp_ds = xarr_ds.copy()
        vars_to_drop = [k for k in xarr_ds.variables.keys() if (search_str not in k)]
        tmp_ds  = tmp_ds.drop(vars_to_drop)    
        try: df_dict[inst_name] = tmp_ds.to_dataframe()
        except ValueError: df_dict[inst_name] = pd.DataFrame()
        if search_str == '2m': n_entries = len(df_dict[inst_name].index)
            
    print("... {}/1728000 fast entries on {}, representing {}% data coverage"
                 .format(n_entries, date, round((n_entries/1728000)*100.,2)))

    del tmp_ds, xarr_ds

    return df_dict

#@profile
def write_level2_netcdf(l2_data, date, timestep, turb_data=None):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta
 
    l2_atts, l2_cols = define_level2_variables()

    short_name = "met"
    if timestep != "1min":
        short_name = 'seb'


    # THIS ALL NEEDS TO BE DELETED!!!!!!!!!!!!!!!!!!!! replace global vars so you can run in isolation
    if we_want_to_debug:
        level2_dir  =  './tests/'
        epoch_time = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers
        def_fill_flt = -9999.0
        def_fill_int = -9999
        nan = np.NaN

    out_dir  =  level2_dir
    if not os.path.exists(out_dir):
        print("!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! !!!")
        print("!!! making directory: {out_dir}, did you mean to do this or... !!!")
        print("!!! did you accidentally specify the wrong path??              !!!")
        print("!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! !!!")
        os.makedirs(out_dir)

    file_str = 'mos{}.metcity.level2.4.{}.{}.nc'.format(short_name, timestep,date.strftime('%Y%m%d.%H%M%S'))

    lev2_name  = '{}{}'.format(out_dir, file_str)

    if type(turb_data) == type(pd.DataFrame()):
        global_atts = define_global_atts("seb") # global atts for level 1 and level 2
    else:
        global_atts = define_global_atts("level2") # global atts for level 1 and level 2
    netcdf_lev2 = Dataset(lev2_name, 'w', zlib=True, clobber=True)

    if isinstance(turb_data, type(pd.DataFrame())):
        turb_atts, turb_cols = define_turb_variables()
        qc_atts, qc_cols = define_qc_variables(include_turb=True)
    else:
        qc_atts, qc_cols = define_qc_variables()
        turb_atts = {}

    l2_atts.update(qc_atts) # combine qc atts/vars now
    l2_cols = l2_cols+qc_cols

    fstr = '{}T'.format(timestep.rstrip("min"))

    if timestep != "1min":

        # we also need freq. dim for some turbulence vars and fix some object-oriented confusion
        # this loop effectively exists to normalize data in a way that the netcdf4 library 
        # can easily write them out, clean up weird dtypes==object, multi dimensional
        # missing data (time, freq) for turbulence calcultations, etc etc etc   
        first_exception = True
        for var_name, var_atts in turb_atts.items(): 
            try: turb_data[var_name]
            except KeyError as ke: 
                if var_name.split("_")[-1] == 'qc': continue; do_nothing = True # we don't fill in all qc variables yet
                else: raise 
                
            chosen_index = 0 # pick first time point to find the number of frequency datapoints written

            if turb_data[var_name].isna().all() or type(turb_data[var_name][chosen_index]) == type(float()):
                turb_data[var_name] = np.float64(turb_data[var_name])

            # this is weird and should only every happen if there was all nans in the fast data
            elif turb_data[var_name][chosen_index].dtype != np.dtype('float64') and turb_data[var_name][chosen_index].len > 1:

                if first_exception:
                    print(f"... something was strange about the fast data on {date} {ae}"); first_exception = False

                max_size = 0 
                for i in turb_data.index: 
                    try:
                        this_size = turb_data[var_name][i].size
                        if this_size > max_size:
                            max_size = this_size
                            chosen_index = i
                    except: do_nothing = True

                for i in turb_data.index: 
                    try: this_size = turb_data[var_name][i].size
                    except: 
                        turb_data[var_name][i] = pd.Series([nan]*max_size)

            # create variable, # dtype inferred from data file via pandas
            if 'fs' in var_name:
                netcdf_lev2.createDimension('freq', turb_data[var_name][chosen_index].size)   

    else:
        l2_data = l2_data #no turbulence data


    all_missing     = True 
    first_loop      = True
    n_missing_denom = 0

    if l2_data.empty:
        print("... there was no data to write today {} for {}" .format(date,timestep))
        print(l2_data)
        return False

    # get some useful missing data information for today and print it for the user
    for var_name, var_atts in l2_atts.items():
        try: dt = l2_data[var_name].dtype
        except KeyError as e: 
            print(" !!! no {} in data on {} ... does this make sense??".format(var_name, date))
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

    if 100-avg_missing < 0.001: 
        print("!!!  not writing {} level2 on {}, because ~{}% of data is present !!!".format(timestep, date, 100-avg_missing))
        return False

    print("... writing {} level2 on {}, ~{}% of data is present".format(timestep, date, 100-avg_missing))

    for att_name, att_val in global_atts.items(): # write global attributes 
        netcdf_lev2.setncattr(att_name, att_val)
        

    try: 
        event_today, event_time = mc_site_metadata.get_site_metadata('events', date)
        if event_today is not None:
            netcdf_lev2.setncattr('event', f'{event_time.strftime("%Y-%m-%d %H:%M:%S")} -- {event_today}')
    except Exception as e:
        do_nothing = True#print(e)

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_lev2.createDimension('time', None)

    dti = pd.DatetimeIndex(l2_data.index.values)
    if timestep != "1min":
        dti = pd.date_range(date, tomorrow, freq=fstr)

    try:
        fms = l2_data.index[0]
    except Exception as e:
        print("... something went really wrong with the indexing")
        print("... the code doesn't handle that currently")
        raise e

    # base_time, ARM spec, the difference between the time of the first data point and the BOT
    today_midnight = datetime(fms.year, fms.month, fms.day)
    beginning_of_time = fms 

    # create the three 'bases' that serve for calculating the time arrays
    et = np.datetime64(epoch_time)
    bot = np.datetime64(beginning_of_time)
    tm =  np.datetime64(today_midnight)

    # first write the int base_time, the temporal distance from the UNIX epoch
    base = netcdf_lev2.createVariable('base_time', 'i') # seconds since
    base[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])      # seconds

    base_atts = {'string'     : '{}'.format(bot),
                 'long_name' : 'Base time in Epoch',
                 'units'     : 'seconds since {}'.format(et),
                 'ancillary_variables'  : 'time_offset',}
    for att_name, att_val in base_atts.items(): netcdf_lev2['base_time'].setncattr(att_name,att_val)

    time_int = int(timestep.rstrip("min"))
    if time_int < 10:
        delt_str = f"0000-00-00 00:0{time_int}:00"
    else:
        delt_str = f"0000-00-00 00:{time_int}:00"

    # here we create the array and attributes for 'time'
    t_atts   = {'units'     : 'seconds since {}'.format(tm),
                'delta_t'   : delt_str,
                'long_name' : 'Time offset from midnight',
                'calendar'  : 'standard',}


    bt_atts   = {'units'     : 'seconds since {}'.format(bot),
                 'delta_t'   : delt_str,
                 'long_name' : 'Time offset from base_time',
                 'ancillary_variables'  : 'base_time',
                 'calendar'  : 'standard',}

    delta_ints = np.floor((dti - tm).total_seconds())      # seconds

    t_ind = pd.Int64Index(delta_ints)

    # now we create the array and attributes for 'time_offset'
    bt_delta_ints = np.floor((dti - bot).total_seconds())      # seconds

    bt_ind = pd.Int64Index(bt_delta_ints)

    # set the time dimension and variable attributes to what's defined above
    bt = netcdf_lev2.createVariable('time_offset', 'd','time') # seconds since

    # set the time dimension and variable attributes to what's defined above
    t = netcdf_lev2.createVariable('time', 'd','time') # seconds since

    # this try/except is vestigial, this bug should be fixed
    bt[:] = bt_ind.values
    t[:]  = t_ind.values

    for att_name, att_val in t_atts.items(): netcdf_lev2['time'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts.items(): netcdf_lev2['time_offset'].setncattr(att_name,att_val)


    for var_name, var_atts in l2_atts.items():

        try:
            var_dtype = l2_data[var_name].dtype
        except KeyError as e:
            var = netcdf_lev2.createVariable(var_name, var_dtype, 'time')
            var[:] = t_ind.values*nan
            for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name].setncattr(att_name, att_desc)
            continue

        perc_miss = fl.perc_missing(l2_data[var_name])

        var  = netcdf_lev2.createVariable(var_name, var_dtype, 'time')

        # all qc flags set to -01 for when corresponding variables are missing data, except for these vars 
        # exception_cols = ['bulk_qc', 'turbulence_2m_qc', 'turbulence_6m_qc', 'turbulence_10m_qc', 
        #                   'turbulence_mast_qc', 'Hl_qc', 'down_long_hemisp', 'down_short_hemisp',
        #                   'up_long_hemisp', 'up_short_hemisp']

        exception_cols = {'bulk_qc': 'bulk_Hs_10m', 'turbulence_2m_qc': 'Hs_2m',
                          'turbulence_6m_qc': 'Hs_6m', 'turbulence_10m_qc': 'Hs_10m', 
                          'turbulence_mast_qc': 'Hs_mast', 'Hl_qc': 'Hl',
                          'down_long_hemisp': False, 'down_short_hemisp': False,
                          'up_long_hemisp': False, 'up_short_hemisp': False}

        if var_name.split('_')[-1] == 'qc':
            fill_val = np.int32(-1)

            if not any(var_name in c for c in list(exception_cols.keys())): 
                 l2_data.loc[l2_data[var_name.rstrip('_qc')].isnull(), var_name] = fill_val

            else: 
                if exception_cols[var_name] != False: 

                    try:
                        l2_data.loc[l2_data[exception_cols[var_name]].isnull(), var_name] = fill_val
                    except:
                        l2_data.loc[turb_data[exception_cols[var_name]].isnull(), var_name] = fill_val
                        
                    l2_data.loc[l2_data[var_name].isnull(), var_name] = fill_val

        if fl.column_is_ints(l2_data[var_name]):
            var_dtype = np.int32
            fill_val  = def_fill_int
            l2_data[var_name] = l2_data[var_name].values.astype(np.int32)
        else:
            fill_val  = def_fill_flt

        vtmp = l2_data[var_name].copy()

        # write atts to the var now
        for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name].setncattr(att_name, att_desc)
        netcdf_lev2[var_name].setncattr('missing_value', float(fill_val))

        max_val = np.nanmax(vtmp.values) # masked array max/min/etc
        min_val = np.nanmin(vtmp.values)
        avg_val = np.nanmean(vtmp.values)

        if var_name.split('_')[-1] != 'qc' or var_name.split('_')[-1] != 'info':
        
            netcdf_lev2[var_name].setncattr('max_val', max_val)
            netcdf_lev2[var_name].setncattr('min_val', min_val)
            netcdf_lev2[var_name].setncattr('avg_val', avg_val)

        vtmp.fillna(fill_val, inplace=True)
        var[:] = vtmp

        try:
            height_today, height_change_time = mc_site_metadata.get_var_metadata(var_name, 'height', date)

            if height_today is None: 
                curr_height, height_change_time = mc_site_metadata.get_var_metadata(var_name, 'height', date, True)
                height_start = curr_height
                height_end   = curr_height
            else:
                prev_height, prev_time = mc_site_metadata.get_var_metadata(var_name, 'height', date, True)
                height_start = prev_height
                height_end   = height_today

            netcdf_lev2[var_name].setncattr('height_start', height_start)
            netcdf_lev2[var_name].setncattr('height_end', height_end)
            netcdf_lev2[var_name].setncattr('height_change_time', height_change_time.strftime('%Y-%m-%d %H:%M:%S'))

            event_today, event_time = mc_site_metadata.get_var_metadata(var_name, 'events', date)
            if event_today is not None:
                netcdf_lev2[var_name].setncattr('event', f'{event_time.strftime("%Y-%m-%d %H:%M:%S")} -- {event_today}')

        except Exception as e:
            do_nothing = True # no height values found in mc_site_metadata for variable

        # add a percent_missing attribute to give a first look at "data quality"
        netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)


    # loop over all the data_out variables and save them to the netcdf along with their atts, etc
    for var_name, var_atts in turb_atts.items():

        try:

            try: turb_data[var_name]
            except keyerror as ke: 
                if var_name.split("_")[-1] == 'qc':
                    continue; do_nothing = true # we don't fill in all qc variables yet
                else: raise 

            # create variable, # dtype inferred from data file via pandas
            var_dtype = turb_data[var_name][0].dtype

            if turb_data[var_name][0].size == 1:
                var_turb  = netcdf_lev2.createVariable(var_name, var_dtype, 'time')

                # convert dataframe to np.ndarray and pass data into netcdf (netcdf can't handle pandas data)
                td = turb_data[var_name].copy()
                td.fillna(def_fill_flt, inplace=True)
                var_turb[:] = td.values

            else:

                if 'fs' in var_name:  
                    var_turb  = netcdf_lev2.createVariable(var_name, var_dtype, ('freq'))
                    # convert dataframe to np.ndarray and pass data into netcdf (netcdf can't handle pandas data). this is even stupider in multipple dimensions
                    td = turb_data[var_name][0].copy()

                    # this fixes the rare case that *one* column is filled entirely with nans
                    # and therefore "col" is a numpy array and not a DataFrame
                    try: 
                        td.fillna(def_fill_flt, inplace=True)
                    except AttributeError: 
                        td = pd.DataFrame(td)
                        td.fillna(def_fill_flt, inplace=True)

                    var_turb[:] = td.values
                else:   

                    var_turb  = netcdf_lev2.createVariable(var_name, var_dtype, ('time','freq'))

                    # replaced some sketchy code loops with functional OO calls and list comprehensions
                    # put the timeseries into a temporary DF that's a simple timeseries, not an array of 'freq'
                    try:
                        tmp_list = [col.values for col in turb_data[var_name].values]

                    # this *also* fixes the rare case that *one* column is filled entirely with
                    # nans and therefor "col" is a numpy array and not a DataFrame
                    except AttributeError:
                        tmp_list = [col for col in turb_data[var_name].values]

                    tmp_df      = pd.DataFrame(tmp_list, index=turb_data.index).fillna(def_fill_flt)
                    tmp         = tmp_df.to_numpy()
                    var_turb[:] = tmp         

            # add variable descriptions from above to each file
            for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name] .setncattr(att_name, att_desc)

            try:
                height_today, height_change_time = mc_site_metadata.get_var_metadata(var_name, 'height', date)

                if height_today is None: 
                    curr_height, height_change_time = mc_site_metadata.get_var_metadata(var_name, 'height', date, True)
                    height_start = curr_height
                    height_end   = curr_height
                else:
                    prev_height, prev_time = mc_site_metadata.get_var_metadata(var_name, 'height', date, True)
                    height_start = prev_height
                    height_end   = height_today

                netcdf_lev2[var_name].setncattr('height_start', height_start)
                netcdf_lev2[var_name].setncattr('height_end', height_end)
                netcdf_lev2[var_name].setncattr('height_change_time', height_change_time.strftime('%Y-%m-%d %H:%M:%S'))

                event_today, event_time = mc_site_metadata.get_var_metadata(var_name, 'events', date)
                if event_today is not None:
                    netcdf_lev2[var_name].setncattr('event', f'{event_time.strftime("%Y-%m-%d %H:%M:%S")} -- {event_today}')

            except Exception as e:
                do_nothing = True # no height values found in mc_site_metadata for variable

            # add a percent_missing attribute to give a first look at "data quality"
            netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)


            # add a percent_missing attribute to give a first look at "data quality"
            perc_miss = fl.perc_missing(var_turb)
            netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)
            netcdf_lev2[var_name].setncattr('missing_value', def_fill_flt)

        except:
            import traceback
            import sys
            print(traceback.format_exc())


    try: turb_data.index; print(f"... wrote out {date} with turbulence data at {timestep}")
    except: do_nothing = True

    netcdf_lev2.close() # close and write files for today

def write_level2_10hz(sonic_data, licor_data, date):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    # these keys are the names of the groups in the netcdf files and the
    # strings in the tuple on the right will be the strings that we search for
    # in fast_atts to know which atts to apply to which group/variable, the
    # data is the value of the search string, a dict of dicts...
    inst_dict = {}
    inst_dict['metek_2m']   = ('2m'    , sonic_data['metek_2m'][date:tomorrow]  )
    inst_dict['metek_6m']   = ('6m'    , sonic_data['metek_6m'][date:tomorrow]  )
    inst_dict['metek_10m']  = ('10m'   , sonic_data['metek_10m'][date:tomorrow] )
    inst_dict['metek_mast'] = ('mast'  , sonic_data['metek_mast'][date:tomorrow])
    inst_dict['licor']      = ('licor' , licor_data[date:tomorrow])

    fast_atts, fast_vars = define_10hz_variables()

    print("... writing level1 fast data {}".format(date))

    # if there's no data, bale (had to look up how to spell bale)
    num_empty=0; 
    for inst in inst_dict:
        if inst_dict[inst][1].empty: num_empty+=1

    if num_empty == len(inst_dict): 
        print("!!! no data on day {}, returning from fast write without writing".format(date))
        return False

    out_dir = level2_dir
    if not os.path.exists(out_dir):
        print("!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! !!!")
        print("!!! making directory: {out_dir}, did you mean to do this or... !!!")
        print("!!! did you accidentally specify the wrong path??              !!!")
        print("!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! !!!")
        os.makedirs(out_dir)

    file_str_fast = 'moswind10hz.metcity.level2.4.{}.nc'.format(date.strftime('%Y%m%d.%H%M%S'))
    
    lev1_fast_name  = '{}/{}'.format(out_dir, file_str_fast)

    global_atts_fast = define_global_atts("10hz") # global atts for level 1 and level 2

    netcdf_lev1_fast  = Dataset(lev1_fast_name, 'w', clobber=True, zlib=True)

    for att_name, att_val in global_atts_fast.items(): # write the global attributes to fast
        netcdf_lev1_fast.setncattr(att_name, att_val)

    # create standardized time dimension for file
    netcdf_lev1_fast.createDimension(f'time', None)

    fms = sonic_data['metek_2m'][date:tomorrow].index[0]
    beginning_of_time = fms 

    # base_time, ARM spec, the difference between the time of the first data point and the BOT
    today_midnight = datetime(fms.year, fms.month, fms.day)
    beginning_of_time = fms 

    # create the three 'bases' that serve for calculating the time arrays
    et  = np.datetime64(epoch_time)
    bot = np.datetime64(beginning_of_time)
    tm  = np.datetime64(today_midnight)

    # first write the int base_time, the temporal distance from the UNIX epoch
    base_fast = netcdf_lev1_fast.createVariable(f'base_time', 'i') # seconds since
    base_fast[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])

    base_atts = {'string'              : '{}'.format(bot),
                 'long_name'           : 'Base time since Epoch',
                 'units'               : 'seconds since {}'.format(et),
                 'ancillary_variables' : 'time_offset',}

    t_atts_fast   = {'units'     : 'milliseconds since {}'.format(tm),
                     'delta_t'   : '0000-00-00 00:00:00.001',
                     'long_name' : 'Time offset from midnight',
                     'calendar'  : 'standard',}

    bt_atts_fast   = {'units'    : 'milliseconds since {}'.format(bot),
                      'delta_t'   : '0000-00-00 00:00:00.001',
                      'long_name' : 'Time offset from base_time',
                      'calendar'  : 'standard',}

    bt_fast_dti = pd.DatetimeIndex(sonic_data['metek_2m'][date:tomorrow].index.values)   
    fast_dti    = pd.DatetimeIndex(sonic_data['metek_2m'][date:tomorrow].index.values)

    # set the time dimension and variable attributes to what's defined above
    t_fast      = netcdf_lev1_fast.createVariable(f'time', 'd',f'time') 
    bt_fast     = netcdf_lev1_fast.createVariable(f'time_offset', 'd',f'time') 

    bt_fast_delta_ints = np.floor((bt_fast_dti - bot).total_seconds()*1000)      # milliseconds
    fast_delta_ints    = np.floor((fast_dti - tm).total_seconds()*1000)      # milliseconds

    bt_fast_ind = pd.Int64Index(bt_fast_delta_ints)
    t_fast_ind  = pd.Int64Index(fast_delta_ints)

    t_fast[:]   = t_fast_ind.values
    bt_fast[:]  = bt_fast_ind.values

    for att_name, att_val in t_atts_fast.items():
        netcdf_lev1_fast[f'time'].setncattr(att_name,att_val)
    for att_name, att_val in base_atts.items():
        netcdf_lev1_fast[f'base_time'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts_fast.items():
        netcdf_lev1_fast[f'time_offset'].setncattr(att_name,att_val)

    # loop through the 4 instruments and set vars in each group based on the strings contained in those vars.
    # a bit sketchy but better than hardcoding things... probably. can at least be done in loop
    # and provides some flexibility for var name changes and such.
    for inst in inst_dict: # for instrument in instrument list create a group and stuff it with data/vars

        inst_str  = inst_dict[inst][0]
        inst_data = inst_dict[inst][1][date:tomorrow]

        #curr_group = netcdf_lev1_fast.createGroup(inst) 

            
        used_vars = [] # used to sanity check and make sure no vars get left out of the file by using string ids
        for var_name, var_atts in fast_atts.items():
            if inst_str not in var_name: continue # check if this variable belongs to this instrument/group
            # if 'TIMESTAMP' in var_name:
            #     used_vars.append(var_name)
            #     continue # already did time stuff
            # actually, commenting out because maybe we should preserve the original timestamp integers???

            try: 
                var_dtype = inst_data[var_name].dtype
            except: 
                print(f" !!! variable {var_name} didn't exist in 10hz data, not writing any 10hz !!!")
                return False

            if fl.column_is_ints(inst_data[var_name]):
                var_dtype = np.int32
                fill_val  = def_fill_int
                inst_data[var_name].fillna(fill_val, inplace=True)
                var_tmp   = inst_data[var_name].values.astype(np.int32)

            else:
                fill_val  = def_fill_flt
                inst_data[var_name].fillna(fill_val, inplace=True)
                var_tmp   = inst_data[var_name].values
        
            try:
                var_fast = netcdf_lev1_fast.createVariable(var_name, var_dtype, f'time', zlib=True)
                var_fast[:] = var_tmp # compress fast data via zlib=True

            except Exception as e:
                print("!!! something wrong with variable {} on date {} !!!".format(var_name, date))
                print(inst_data[var_name])
                print("!!! {} !!!".format(e))
                continue

            for att_name, att_desc in var_atts.items(): # write atts to the var now
                netcdf_lev1_fast[var_name].setncattr(att_name, att_desc)

            # add a percent_missing attribute to give a first look at "data quality"
            perc_miss = fl.perc_missing(var_fast)
            netcdf_lev1_fast[var_name].setncattr('percent_missing', perc_miss)
            netcdf_lev1_fast[var_name].setncattr('missing_value'  , fill_val)
            used_vars.append(var_name)  # all done, move on to next variable


    netcdf_lev1_fast.close()
    return True

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
