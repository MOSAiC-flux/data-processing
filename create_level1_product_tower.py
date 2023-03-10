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
# Takes in various MOSAiC data files and outputs level1 netcdf 'ingest' files
# that are then used to create the level2 files. This work follows on Ola's
# first looks at MOSAiC observations. These level1 output files are raw
# uncalibrated data in a convenient format.
#
# Descriptions of these two different output files and their contents:
# (look at "tower_data_definitions.py" for detailed product description)
# ############################################################################################
# level1 "slow":
#
#       Observations from all instruments averaged over 1 minute intervals, as logged by the
#       CR1000X at the base of the tower. 
# 
# level1 "fast":
# 
#       Observations from metek sonic anemometers and licor CO2/H2O gas rapid gas
#       analyzer at all 4 levels (2m, 6m, 10m, and 30(ish)m mast. These observations are
#       taken at 20Hz barring any problems. 
#
# HOWTO:
#
# To run this package with verbose printing over the data from Dec 1st:
# python3 create_level1_product_tower.py -v -s 20191015 -e 20200231 -p /psd3data/arctic/
#
# To profile the code and see what's taking so long:
# python -m cProfile -s cumulative ./create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201 -f
#
# RELEASE-NOTES:
#
# Please look at CHANGELOG-tower.md for notes on changes/improvements with each version.
#
# UPDATES:
# ######################################################################################################
from tower_data_definitions import define_global_atts
from tower_data_definitions import define_level1_slow, define_level1_fast

import functions_library as fl # functions written by the flux team for processing data

import os, inspect, argparse, time

from multiprocessing import Process as P
from multiprocessing import Queue   as Q

import socket 

global nthreads 
if '.psd.' in socket.gethostname():
    nthreads = 20  # the twins have 64 cores, it won't hurt if we use <20
else: nthreads = 8 # laptops don't tend to have 64 cores, set to 1 to debug

# need to debug something? kills multithreading to step through function calls
# from multiprocessing.dummy import Process as P
# from multiprocessing.dummy import Queue   as Q
# nthreads = 1

import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from datetime  import datetime, timedelta
from numpy     import sqrt
from netCDF4   import Dataset

# just in case... avoids some netcdf nonsense involving the default file locking across mounts
os.environ['HDF5_USE_FILE_LOCKING']='FALSE' # just in case

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

version_msg = '\n\nPS-122 MOSAiC Met Tower processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

def main(): # the main data crunching program

    # the UNIX epoch... provides a common reference, used with base_time
    global epoch_time
    epoch_time        = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers

    process_fast_data    = True
    calc_stats           = False # If False, stats are read from NOAA Services. If True calculated here.
    # should set to True normally because recalculating here accounts for coordinate rotations, QC, and the like

    global data_dir      # make available to the functions at bottom
    global level1_dir
    global printline     # prints a line out of dashes, pretty boring
    global verboseprint  # defines a function that prints only if -v is used when running

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
    
    # where do we get the data from
    if args.path:
        data_dir = args.path #'./data/tower/0_level_raw/'
    else: # assume we are on PSD
        data_dir = '/Projects/MOSAiC/'

    level1_dir = data_dir+'tower/1_level_ingest' #./processed_data/tower/level1/'  # where does level1 data go
    
    # QC params:
    apogee_switch_date = datetime(2019,11,12,10,21,29) # Nov. 12th, 10:21::29

    # these are subdirs of the data_dir
    metek_bottom_dir = 'tower/0_level_raw/Metek02m/'
    metek_middle_dir = 'tower/0_level_raw/Metek06m/'
    metek_top_dir    = 'tower/0_level_raw/Metek10m/'
    metek_mast_dir   = 'tower/0_level_raw/Metek30m/'
    licor_dir        = 'tower/0_level_raw/Licor02m/'
    tower_logger_dir = 'tower/0_level_raw/CR1000X/daily_files/'
    mast_logger_dir  = 'tower/0_level_raw/CR1000_mast/daily_files/'

    # constants for calculations
    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0
    Rd       = 287     # gas constant for dry air
    K_offset = 273.15  # convert C to K
    h2o_mass = 18      # are the obvious things...
    co2_mass = 44      # ... ever obvious?

    def printline(startline='',endline=''): # make for pretty printing
        print('{}--------------------------------------------------------------------------------------------{}'
              .format(startline, endline))

    start_time = epoch_time # initialize
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
        if start_time == end_time: # processing current days data, pull out of the dump dir
            tower_logger_dir = '/CR1000X/'

    print('The first day we process data is:      %s' % start_time)
    print('The last day we will process data is:  %s\n' % end_time)
    print('---------------------------------------------------------------------------------------------')

    # get the and fast raw data day by day, a little different than the stations, but the data is a bit different
    # heavy lifting is in "get_logger_data()" and "get_fast_data()" at the bottom of this code
    # ###########################################################################################################
    day_series = pd.date_range(start_time, end_time)    # we're going to loop over these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    def process_tower_day(today, day_q): 

        tomorrow      = today+day_delta
        seconds_today = pd.date_range(today, tomorrow, freq='S')         
        slow_data     = get_slow_data(today)
        
        n_entries   = slow_data.size
        if slow_data.empty: # 'fatal' is a print function defined at the bottom of this script that exits
            fl.warn('No logger data for date: {} '.format(today))
            
        slow_data.drop_duplicates(inplace=True) # drop any rows that are duplicated between files due to DAQ issues
        n_entries_after = slow_data.size
        n_removed       = n_entries-n_entries_after
        verboseprint('... there were %s duplicates removed from the logger data in this time range!' % n_removed)

        # now clean and QC the logger data 'subtleties'. any and all fixing of logger data is done here
        # this is the *only* QC done to level1 output files, very minimal
        # ###################################################################################################
        # correct apogee_body and apogee_target data, body & targ temperatures were reversed before this time

        # sort things out (this could/should be done in get_data function?)
        if slow_data.empty:
            print(f"!!! no logger today means we're doing nothing for {today}, moving on to next day...")
            day_q.put(False) # we don't do anything with the return codes yet
            return

        slow_data = slow_data.sort_index()
        slow_data = slow_data[:][today:tomorrow] 

        # this fills the entries that didn't exist in the ascii files with nans
        try:
            slow_data = slow_data.reindex(labels=seconds_today, copy=False)
        except Exception as e:
            fl.warn("There were duplicates in your slow data for {}\n ".format(today))
        
        targ_T = slow_data['apogee_targ_T'].copy()
        body_T = slow_data['apogee_body_T'].copy() 
        slow_data['apogee_targ_T'] = np.where(slow_data.index < apogee_switch_date,\
                                              body_T,\
                                              targ_T)
        slow_data['apogee_body_T'] = np.where(slow_data.index < apogee_switch_date,\
                                              targ_T,\
                                              body_T)

        metek_bottom = get_fast_data(metek_bottom_dir, today)
        metek_middle = get_fast_data(metek_middle_dir, today)
        metek_top    = get_fast_data(metek_top_dir,    today)
        metek_mast   = get_fast_data(metek_mast_dir,   today)
        licor_bottom = get_fast_data(licor_dir,        today)

        # now clean and QC the fast data subtleties, here we decode the licor diagnostics so it doesn't have to been done every level2 run
        print("... decoding the Licor diagnostics. it's fast like the Dranitsyn. Gimme a minute...")
        
        pll, detector_temp, chopper_temp = fl.decode_licor_diag(licor_bottom['licor_diag'])
        # Phase Lock Loop. Optical filter wheel rotating normally if 1, else "abnormal"
        # detector temp, if 0 weve drifted too far from set point. should yield a bad calibration, I think
        # ditto for the chopper housing temp
        licor_bottom['licor_pll'] = pll
        licor_bottom['licor_dt']  = detector_temp
        licor_bottom['licor_ct']  = chopper_temp

        # ~~~~~~~~~~~~~~~~~~~~~ (2) Quality control ~~~~~~~~~~~~~~~~~~~~~~~~
        print('... quality controlling the fast data now.')
        # do we want the optionn to put stats values into the "level1" product. probably not... but I'll leave this here for now.
        if calc_stats == True:

            print('... recalculating NOAA Services style stats data with the corrected, rotated, and quality controlled values.')

            metek_bottom_stats  = pd.DataFrame()
            metek_middle_stats  = pd.DataFrame()
            metek_top_stats     = pd.DataFrame()
            metek_mast_stats    = pd.DataFrame()
            licor_bottom_stats  = pd.DataFrame()

            metek_bottom_stats['wind_speed_metek_2m']       = bottom_ws_corr
            metek_middle_stats['wind_speed_metek_6m']       = middle_ws_corr
            metek_top_stats   ['wind_speed_metek_10m']      = top_ws_corr
            metek_mast_stats  ['wind_speed_metek_mast']     = mast_ws_corr

            metek_bottom_stats['wind_direction_metek_2m']   = bottom_wd_corr
            metek_middle_stats['wind_direction_metek_6m']   = middle_wd_corr
            metek_top_stats   ['wind_direction_metek_10m']  = top_wd_corr
            metek_mast_stats  ['wind_direction_metek_mast'] = mast_wd_corr

            metek_bottom_stats['temp_variance_metek_2m']    = metek_bottom_10hz['T'].resample('1T',label='left').var()
            metek_middle_stats['temp_variance_metek_6m']    = metek_middle_10hz['T'].resample('1T',label='left').var()
            metek_top_stats   ['temp_variance_metek_10m']   = metek_top_10hz['T'].resample('1T',label='left').var()
            metek_mast_stats  ['temp_variance_metek_mast']  = metek_mast_10hz['T'].resample('1T',label='left').var()

            licor_bottom_stats['H2O_licor']                 = licor_bottom_10hz['h2o'].resample('1T',label='left').mean()
            licor_bottom_stats['CO2_licor']                 = licor_bottom_10hz['co2'].resample('1T',label='left').mean()
            licor_bottom_stats['temp_licor']                = licor_bottom_10hz['T'].resample('1T',label='left').mean()
            licor_bottom_stats['pr_licor']                  = licor_bottom_10hz['pr'].resample('1T',label='left').mean()*10 # [to hPa]
            licor_bottom_stats['co2_signal_licor']          = licor_bottom_10hz['co2_str'].resample('1T',label='left').mean()

            metek_bottom_stats['u_metek_2m']                = metek_bottom_10hz['u'].resample('1T',label='left').mean()
            metek_middle_stats['u_metek_6m']                = metek_middle_10hz['u'].resample('1T',label='left').mean()
            metek_top_stats['u_metek_10m']                  = metek_top_10hz['u'].resample('1T',label='left').mean()
            metek_mast_stats['u_metek_mast']                = metek_mast_10hz['u'].resample('1T',label='left').mean()

            metek_bottom_stats['v_metek_2m']                = metek_bottom_10hz['v'].resample('1T',label='left').mean()
            metek_middle_stats['v_metek_6m']                = metek_middle_10hz['v'].resample('1T',label='left').mean()
            metek_top_stats['v_metek_10m']                  = metek_top_10hz['v'].resample('1T',label='left').mean()
            metek_mast_stats['v_metek_mast']                = metek_mast_10hz['v'].resample('1T',label='left').mean()

            metek_bottom_stats['w_metek_2m']                = metek_bottom_10hz['w'].resample('1T',label='left').mean()
            metek_middle_stats['w_metek_6m']                = metek_middle_10hz['w'].resample('1T',label='left').mean()
            metek_top_stats['w_metek_10m']                  = metek_top_10hz['w'].resample('1T',label='left').mean()
            metek_mast_stats['w_metek_mast']                = metek_mast_10hz['w'].resample('1T',label='left').mean()

            metek_bottom_stats['temp_metek_2m']             = metek_bottom_10hz['T'].resample('1T',label='left').mean()
            metek_middle_stats['temp_metek_6m']             = metek_middle_10hz['T'].resample('1T',label='left').mean()
            metek_top_stats['temp_metek_10m']               = metek_top_10hz['T'].resample('1T',label='left').mean()
            metek_mast_stats['temp_metek_mast']             = metek_mast_10hz['T'].resample('1T',label='left').mean()

            metek_bottom_stats['stddev_u_metek_2m']         = metek_bottom_10hz['u'].resample('1T',label='left').std()
            metek_middle_stats['stddev_u_metek_6m']         = metek_middle_10hz['u'].resample('1T',label='left').std()
            metek_top_stats['stddev_u_metek_10m']           = metek_top_10hz['u'].resample('1T',label='left').std()
            metek_mast_stats['stddev_u_metek_mast']         = metek_mast_10hz['u'].resample('1T',label='left').std()

            metek_bottom_stats['stddev_v_metek_2m']         = metek_bottom_10hz['v'].resample('1T',label='left').std()
            metek_middle_stats['stddev_v_metek_6m']         = metek_middle_10hz['v'].resample('1T',label='left').std()
            metek_top_stats['stddev_v_metek_10m']           = metek_top_10hz['v'].resample('1T',label='left').std()
            metek_mast_stats['stddev_v_metek_mast']         = metek_mast_10hz['v'].resample('1T',label='left').std()

            metek_bottom_stats['stddev_w_metek_2m']         = metek_bottom_10hz['w'].resample('1T',label='left').std()
            metek_middle_stats['stddev_w_metek_6m']         = metek_middle_10hz['w'].resample('1T',label='left').std()
            metek_top_stats['stddev_w_metek_10m']           = metek_top_10hz['w'].resample('1T',label='left').std()
            metek_mast_stats['stddev_w_metek_mast']         = metek_mast_10hz['w'].resample('1T',label='left').std()

            metek_bottom_stats['stddev_T_metek_2m']         = metek_bottom_10hz['T'].resample('1T',label='left').std()
            metek_middle_stats['stddev_T_metek_6m']         = metek_middle_10hz['T'].resample('1T',label='left').std()
            metek_top_stats['stddev_T_metek_10m']           = metek_top_10hz['T'].resample('1T',label='left').std()
            metek_mast_stats['stddev_T_metek_mast']         = metek_mast_10hz['T'].resample('1T',label='left').std()

        # continue with writing out level1 files:
        # #######################################
        rval_slow = write_level1_slow(slow_data, today)
        rval_fast = write_level1_fast(metek_bottom, metek_middle, metek_top, metek_mast, licor_bottom, today)

        # process_station_days() ends here
        day_q.put(True)
        return 

    q_list = []  # setup queue storage
    day_list = [] # for debugging
    for i_day, today in enumerate(day_series): # loop over the days in the processing range and get a list of files

        q_today = Q()
        q_list.append(q_today)
        day_list.append(today)
        P(target=process_tower_day, args=(today, q_today,)).start()

        if (i_day+1) % nthreads == 0 or today == day_series[-1]:
            for iq, qq in enumerate(q_list):
                qq.get()
            q_list = []
        #import gc; gc.collect() 

    print('---------------------------------------------------------------------------------------------')
    print('All done! Netcdf output files can be found in: {}'.format(level1_dir))
    print(version_msg)
    print('---------------------------------------------------------------------------------------------')

def get_slow_data(date):

    tower_subdir = 'tower/0_level_raw/CR1000X/daily_files/'
    mast_subdir  = 'tower/0_level_raw/CR1000_mast/daily_files/'
    slow_data  = pd.DataFrame()
    fuzzy_window = timedelta(20) # we look for files 2 days before and after because we didn't save even days...(?!)
    # fuzzy_window>=5 required for days of MOSAiC where logger info is spread out across 'daily-ish' files -- "shutdown days"

    slow_atts, slow_vars = define_level1_slow()
    print('... getting slow logger data from: %s' % data_dir+tower_subdir)
    
    logger_file_list   = [] # list of filenames to concat into dataframes
    mast_gps_file_list = [] # list of filenames to concat into mast dataframes

    data_file_list = os.listdir(data_dir+tower_subdir)
    data_file_list.extend(os.listdir(data_dir+mast_subdir))

    for data_file in data_file_list:

        if data_file.endswith('.dat'):

            file_words = data_file.split(sep='_')
            if data_file == 'cr1000x_tower.dat':
                logger_file_list.append(data_file)
                verboseprint('... using the daily file {}'.format(data_file))
            elif data_file == 'CR1000_Noodleville_mast.dat':
                use_file = False
                #verboseprint("... skipping {} ... what is this file? redundant data?".format(data_file))
            elif len(file_words) > 2:
                file_date  = datetime.strptime(file_words[-2]+file_words[-1].strip('.dat'),'%m%d%Y%H%M') # (!)
                
                if file_date >= (date-fuzzy_window) and file_date <= (date+fuzzy_window): # weirdness
                    if file_words[1] == "Noodleville":
                        print(f"!!! Noodle file found {data_file}")
                        mast_gps_file_list.append(data_file)
                    else:
                        logger_file_list.append(data_file)
                    verboseprint('... using the file {} from the day: {}'.format(data_file,file_date))
            else:
                fl.warn('There is a logger file I cant use, this makes no sense... {}'.format(data_file))
                use_file = False

    logger_df_list = [] # logger dataframes to be concatted all at once
    for logger_file in logger_file_list:
        path  = data_dir+tower_subdir+'/'+logger_file
        with open(path) as f:
            firstline = f.readlines()[1].rsplit(',')
            num_cols = len(firstline)
            na_vals = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"']
            frame = pd.read_csv(path,parse_dates=[0],sep=',',na_values=na_vals,\
                                index_col=0,header=[1],skiprows=[2,3],engine='c',\
                                converters={'gps_alt':convert_sci, 'gps_hdop':convert_sci})#,\
                                #dtype=dtype_dict)
            logger_df_list.append(frame)

    try:
        logger_df = pd.concat(logger_df_list, verify_integrity=False) # is concat computationally efficient?
    except: 
        print(f"!!! no logger data in {fuzzy_window} day window around day... is this reasonable?")
        logger_df = pd.DataFrame()

    mast_gps_df_list = [] # mast gps dataframes to be concatted all at once
    for mast_gps_file in mast_gps_file_list:
        path  = data_dir+mast_subdir+'/'+mast_gps_file
        with open(path) as f:

            cols = ["TIMESTAMP","mast_RECORD","mast_gps_lat_deg_Avg","mast_gps_lat_min_Avg","mast_gps_lon_deg_Avg",\
                    "mast_gps_lon_min_Avg","mast_gps_hdg_Avg","mast_gps_alt_Avg","mast_gps_qc","mast_gps_hdop_Avg",\
                    "mast_gps_nsat_Avg","mast_PTemp","mast_batt_volt","mast_call_time_mainscan","mast_T","mast_RH","mast_P"]

            firstline = f.readlines()[1].rsplit(',')
            num_cols = len(firstline)
            na_vals = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"']
            frame = pd.read_csv(path,names=cols,parse_dates=[0],sep=',',na_values=na_vals,\
                                index_col=0,skiprows=[0,1,2,3],engine='c',\
                                converters={'gps_alt':convert_sci, 'gps_hdop':convert_sci})#,\
                                #dtype=dtype_dict)
                                    
            mast_gps_df_list.append(frame)

    if len(mast_gps_df_list)>0:
        mast_gps_df = pd.concat(mast_gps_df_list, verify_integrity=False) # is concat computationally efficient? 
        # need to shift some times because of a drfted clock -ccox notes.txt 20200422         
        # mast_gps_df.loc[datetime(2020,4,13,12,27,49):datetime(2020,4,22,14,51,16)].index=mast_gps_df.loc[datetime(2020,4,13,12,27,49):datetime(2020,4,22,14,51,16)].index.shift(freq='+248s') # this should work, but .loc and .shift or .reindex do not play nicely together
        # however, I cannot find a graceful solution after more hours than I'd like to recall so F$#k it        
       # aa = mast_gps_df[:datetime(2020,4,13,12,27,48)]
       # bb = mast_gps_df[datetime(2020,4,13,12,27,49):datetime(2020,4,22,14,51,16)]
       # cc = mast_gps_df[datetime(2020,4,22,14,51,17):]
       # bb.index=bb.index.shift(freq='+248s') 
       # mast_gps_df = pd.concat([aa,bb,cc])
       # mast_gps_df.drop_duplicates(inplace=True)
        aa = mast_gps_df[(mast_gps_df.index <= datetime(2020,4,13,12,27,49))]  
        bb = mast_gps_df[(mast_gps_df.index > datetime(2020,4,13,12,27,49)) & (mast_gps_df.index <= datetime(2020,4,22,14,51,16))] 
        cc = mast_gps_df[(mast_gps_df.index > datetime(2020,4,22,14,51,16))]  
        bb.index=bb.index.shift(freq='+248s') 
        mast_gps_df = pd.concat([aa,bb,cc])
  
        slow_data = logger_df.combine_first(mast_gps_df) # there's mast_T etc etc in both files, must overwrite
        slow_data = mast_gps_df.combine_first(logger_df) # there's mast_T etc etc in both files, must overwrite
        #slow_data = pd.concat([logger_df, mast_gps_df], axis=1) # is concat computationally efficient?  
    else:
        slow_data = logger_df

    slow_data.index = slow_data.index-pd.Timedelta(1,unit='sec') 
    return slow_data.sort_index() # sort logger data (when copied, you lose the file create ordering...)


# gets data that is in the metek format, either 'raw' or 'stats' can but put in as a data_str
def get_fast_data(subdir, date):
    fast_atts, fast_vars = define_level1_fast() 
    
    metek_data = pd.DataFrame()
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we look for files from date+(1day-1microsecond)

    print('... getting fast data from: %s' % data_dir+subdir)
    nfiles = 0

    # define column names according to instrument 
    inst_strs = ['licor','2m','6m','10m','30m']
    curr_inst = [inst for inst in inst_strs if inst in subdir.lower()][0]
    if curr_inst == '30m': curr_inst='mast' #directory labeled 30m, data vars labeled mast...
    cols = [s for s in fast_vars if curr_inst in s.lower()]
    if curr_inst == 'licor': cols = cols[0:7] # there's 7 columns in the original data but we're decoding the diags and adding vars

    frame_list = []
    first_file = True
    for data_file in os.listdir(data_dir+subdir):
        if data_file.startswith('msc') and data_file.endswith('_raw.txt'):
            file_words  = data_file.split(sep='_')
            date_string = file_words[0].strip('msc') # YYYJJJHH

            metek_file_date = datetime.strptime('2'+date_string,'%Y%j%H')

            if metek_file_date >= (date) and metek_file_date < (date+day_delta):
                nfiles += 1
                #if first_file:
                verboseprint('... using the file {} from the day: {}'.format(data_file, metek_file_date))
                    #first_file = False
                path        = data_dir+subdir+data_file
                header_list = None

                # read in data finally, then assign colunm names and convert timestamps after
                frame = pd.read_csv(path, parse_dates=False, sep='\s+', na_values=['nan','NaN'],
                                     header=header_list, skiprows=[0], engine='c',)

                mmssuuu  = frame[0].values # convert timestamp into useable datetime array and then set index to timestamps

                # rarely, some files have a random amount of "NUL chars" sprinkled at the beginning of lines, must be shutdown periods?
                # it's rare enough that we don't want to run the conversion on *all* files (v. slow), so we just re-read the bad files
                # literally only saves one data point of fast data, worth it? we could just drop that line but it took a while to track down and fix
                # this is written this way because pandas *and* numpy process the nul char in the pipeline before doing conversions and it borks everything
                # and I couldn't find a reasonable workaround. kind of stupid to essentially re-write a slower version of read_csv
                if np.any(np.isnan(mmssuuu)): 
                    bad_inds = np.argwhere(np.isnan(mmssuuu))
                    fl.warn("SOMETHING WRONG WITH TIMESTAMPS (NUL CHAR?) IN FILE {}\n\n SOMEWHERE NEAR LINES {}.. this is gonna be slow".format(data_file, bad_inds))
                    with open(path, 'r') as fin:
                        next(fin)
                        weird_string_lines = fin.read().split("\n")
                    for i, line in enumerate(weird_string_lines):
                        weird_data_line = np.fromstring(line, sep=' ')
                        if i == 0:
                            weird_data = weird_data_line.transpose()
                        if len(weird_data_line) > 0 : weird_data = np.vstack([weird_data, weird_data_line])
                    frame = pd.DataFrame(weird_data)
                    frame[0] = pd.to_numeric(frame[0])
                    mmssuuu  = frame[0].values
                    bad_inds = np.argwhere(np.isnan(mmssuuu))

                frame.columns = cols # rename columns appropriately
                noaadate = np.char.zfill(mmssuuu.astype(int).astype(str), 7)
                date_now = ' {}-{}-{}-{}'.format(metek_file_date.year, metek_file_date.month,
                                                    metek_file_date.day,  metek_file_date.hour)
                time_now = np.array([nd+date_now for nd in noaadate])
                timestamps = pd.to_datetime(time_now, format='%M%S%f %Y-%m-%d-%H').rename('TIMESTAMP')
                frame = frame.set_index(timestamps)
                frame = frame[mmssuuu>=0] # drop bad timestamps
                frame_list.append(frame)


        else: # found a file that is not an 'msc' file...warn user??
            x = 'do nothing' # placeholder, guess we won't warn the user, sorry user!

    if nfiles == 0: 
        fl.warn('NO FAST DATA FOR {} on {} ... MAKE SENSE??\n\n'.format(subdir,date)\
             +'IS THIS A DAY WHEN THE MAST WAS DOWN? NO? UH OH...')  

        # create a fake 20hz data frame that's empty and return it             
        Hz20_today       = pd.date_range(date, date+day_delta, freq="0.05S") 
        frame            = pd.DataFrame(index=Hz20_today, 
                                        columns=cols, 
                                        dtype=np.float64) 
        frame            = frame.set_index(Hz20_today)
        return frame

    elif nfiles != 24:
        fl.warn('{} of 24 {} files available for today {}'.format(nfiles,subdir,date))

    # put the date from all files into one data frame before giving it back
    metek_data = pd.concat(frame_list) # is concat computationally efficient?

    metek_data = metek_data.sort_index()
    return metek_data

def write_level1_fast(metek_bottom, metek_middle, metek_top, metek_mast, licor_bottom, date):

    # these keys are the names of the groups in the netcdf files and the
    # strings in the tuple on the right will be the strings that we search for
    # in fast_atts to know which atts to apply to which group/variable, the
    # data is the value of the search string, a dict of dicts...
    inst_dict = {}
    inst_dict['metek_2m']   = ('2m'    , metek_bottom)
    inst_dict['metek_6m']   = ('6m'    , metek_middle)
    inst_dict['metek_10m']  = ('10m'   , metek_top)
    inst_dict['metek_mast'] = ('mast'  , metek_mast)
    inst_dict['licor']      = ('licor' , licor_bottom)

    fast_atts, fast_vars = define_level1_fast() 

    print("... writing level1 fast data {}".format(date))

    # if there's no data, bale (had to look up how to spell bale)
    if metek_bottom.empty and metek_middle.empty and metek_top.empty and metek_mast.empty and licor_bottom.empty:
        print("!!! no data on day {}, returning from fast write without writing".format(date))
        return False

    out_dir       = level1_dir
    file_str_fast = 'mosflxtowerfast.level1.{}.nc'.format(date.strftime('%Y%m%d.%H%M%S'))
    
    lev1_fast_name  = '{}/{}'.format(out_dir, file_str_fast)

    global_atts_fast = define_global_atts("fast") # global atts for level 1 and level 2

    netcdf_lev1_fast  = Dataset(lev1_fast_name, 'w',zlib=True)

    for att_name, att_val in global_atts_fast.items(): # write the global attributes to fast
        netcdf_lev1_fast.setncattr(att_name, att_val)

    # loop through the 4 instruments and set vars in each group based on the strings contained in those vars.
    # a bit sketchy but better than hardcoding things... probably. can at least be done in loop
    # and provides some flexibility for var name changes and such.
    for inst in inst_dict: # for instrument in instrument list create a group and stuff it with data/vars

        inst_str  = inst_dict[inst][0]
        inst_data = inst_dict[inst][1]

        #curr_group = netcdf_lev1_fast.createGroup(inst) 

        netcdf_lev1_fast.createDimension(f'time_{inst_str}', None)

        fms = inst_data.index[0]
        beginning_of_time = fms 

        # base_time, ARM spec, the difference between the time of the first data point and the BOT
        today_midnight = datetime(fms.year, fms.month, fms.day)
        beginning_of_time = fms 

        # create the three 'bases' that serve for calculating the time arrays
        et  = np.datetime64(epoch_time)
        bot = np.datetime64(beginning_of_time)
        tm  =  np.datetime64(today_midnight)

        # first write the int base_time, the temporal distance from the UNIX epoch
        base_fast = netcdf_lev1_fast.createVariable(f'base_time_{inst_str}', 'i') # seconds since
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

        bt_fast_dti = pd.DatetimeIndex(inst_data.index.values)   
        fast_dti    = pd.DatetimeIndex(inst_data.index.values)

        # set the time dimension and variable attributes to what's defined above
        t_fast      = netcdf_lev1_fast.createVariable(f'time_{inst_str}', 'd',f'time_{inst_str}') 
        bt_fast     = netcdf_lev1_fast.createVariable(f'time_offset_{inst_str}', 'd',f'time_{inst_str}') 

        bt_fast_delta_ints = np.floor((bt_fast_dti - bot).total_seconds()*1000)      # milliseconds
        fast_delta_ints    = np.floor((fast_dti - tm).total_seconds()*1000)      # milliseconds

        bt_fast_ind = pd.Int64Index(bt_fast_delta_ints)
        t_fast_ind  = pd.Int64Index(fast_delta_ints)

        t_fast[:]   = t_fast_ind.values
        bt_fast[:]  = bt_fast_ind.values

        for att_name, att_val in t_atts_fast.items():
            netcdf_lev1_fast[f'time_{inst_str}'].setncattr(att_name,att_val)
        for att_name, att_val in base_atts.items():
            netcdf_lev1_fast[f'base_time_{inst_str}'].setncattr(att_name,att_val)
        for att_name, att_val in bt_atts_fast.items():
            netcdf_lev1_fast[f'time_offset_{inst_str}'].setncattr(att_name,att_val)
            
        used_vars = [] # used to sanity check and make sure no vars get left out of the file by using string ids
        for var_name, var_atts in fast_atts.items():
            if inst_str not in var_name: continue # check if this variable belongs to this instrument/group
            # if 'TIMESTAMP' in var_name:
            #     used_vars.append(var_name)
            #     continue # already did time stuff
            # actually, commenting out because maybe we should preserve the original timestamp integers???

            var_dtype = inst_data[var_name].dtype

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
                var_fast = netcdf_lev1_fast.createVariable(var_name, var_dtype, f'time_{inst_str}', zlib=True)
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

def write_level1_slow(slow_data, date): 
    
    # some user feedback into the output
    slow_atts, slow_vars = define_level1_slow() 

    all_missing_slow = True 
    first_loop       = True
    n_missing_denom  = 0

    # count missing percs for each var and print useful infow
    for var_name, var_atts in slow_atts.items():
        if var_name not in slow_data.columns:
            if not 'mast_' in var_name and date < datetime(2020,4,20): # noodleville was born in april
                verboseprint("... {} not in dataframe but in file, is this a problem?".format(var_name))
            continue
        if var_name == 'time': continue
        perc_miss = fl.perc_missing(slow_data[var_name].values)
        if perc_miss < 100: all_missing_slow = False
        if first_loop: 
            avg_missing_slow = perc_miss
            first_loop=False
        elif perc_miss < 100: 
            avg_missing_slow = avg_missing_slow + perc_miss
            n_missing_denom += 1
    if n_missing_denom > 1: avg_missing_slow = round(avg_missing_slow/n_missing_denom,2)
    else: avg_missing_slow = 100.

    # if there's no data, bale
    if all_missing_slow:
        print("!!! no data on day {}, returning slow from write without writing".format(date))
        return False

    print("... writing level1 slow data {}, ~{}% of slow data is present".format(date, 100-avg_missing_slow))

    out_dir       = level1_dir    
    file_str_slow = 'mosflxtowerslow.level1.{}.nc'.format(date.strftime('%Y%m%d.%H%M%S'))
    
    lev1_slow_name  = '{}/{}'.format(out_dir, file_str_slow)

    global_atts_slow = define_global_atts("slow") # global atts for level 1 and level 2

    netcdf_lev1_slow  = Dataset(lev1_slow_name, 'w', zlib=True)

    for att_name, att_val in global_atts_slow.items(): # write the global attributes to slow
        netcdf_lev1_slow.setncattr(att_name, att_val)

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_lev1_slow.createDimension('time', None)

    fms = slow_data.index[0]
    beginning_of_time = fms 

    # base_time, ARM spec, the difference between the time of the first data point and the BOT
    today_midnight = datetime(fms.year, fms.month, fms.day)
    beginning_of_time = fms 

    # create the three 'bases' that serve for calculating the time arrays
    et  = np.datetime64(epoch_time)
    bot = np.datetime64(beginning_of_time)
    tm  =  np.datetime64(today_midnight)

    # first write the int base_time, the temporal distance from the UNIX epoch
    base_slow = netcdf_lev1_slow.createVariable('base_time', 'i') # seconds since
    base_slow[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0]) # seconds

    base_atts = {'string'     : '{}'.format(bot),
                 'long_name' : 'Base time since Epoch',
                 'units'     : 'seconds since {}'.format(et),
                 'ancillary_variables'  : 'time_offset',}

    t_atts_slow   = {'units'     : 'seconds since {}'.format(tm),
                     'delta_t'   : '0000-00-00 00:01:00',
                     'long_name' : 'Time offset from midnight',
                     'calendar'  : 'standard',}

    bt_atts_slow   = {'units'    : 'seconds since {}'.format(bot),
                      'delta_t'   : '0000-00-00 00:01:00',
                      'long_name' : 'Time offset from base_time',
                      'calendar'  : 'standard',}

    bt_slow_dti        = pd.DatetimeIndex(slow_data.index.values)   
    slow_dti           = pd.DatetimeIndex(slow_data.index.values)

    # set the time dimension and variable attributes to what's defined above
    t_slow             = netcdf_lev1_slow.createVariable('time', 'd','time') 
    bt_slow            = netcdf_lev1_slow.createVariable('time_offset', 'd','time') 

    bt_slow_delta_ints = np.floor((bt_slow_dti - bot).total_seconds())      # seconds
    slow_delta_ints    = np.floor((slow_dti - tm).total_seconds())      # seconds

    bt_slow_ind        = pd.Int64Index(bt_slow_delta_ints)
    t_slow_ind         = pd.Int64Index(slow_delta_ints)

    t_slow[:]  = t_slow_ind.values
    bt_slow[:] = bt_slow_ind.values

    for att_name, att_val in base_atts.items(): netcdf_lev1_slow['base_time'].setncattr(att_name,att_val)
    for att_name, att_val in t_atts_slow.items(): netcdf_lev1_slow['time'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts_slow.items(): netcdf_lev1_slow['time_offset'].setncattr(att_name,att_val)

    for var_name, var_atts in slow_atts.items():
        if var_name not in slow_data.columns:
            continue
        if var_name == 'time': continue # already did that

        if var_name == 'mast_T' or var_name == 'mast_RH' or var_name == 'mast_P':
            print(slow_data[var_name])

        var_dtype = slow_data[var_name].dtype

        if fl.column_is_ints(slow_data[var_name]):
        # if issubclass(var_dtype.type, np.integer): # netcdf4 classic doesnt like 64 bit integers
            var_dtype = np.int32
            fill_val  = def_fill_int
            slow_data[var_name].fillna(fill_val, inplace=True)
            var_tmp = slow_data[var_name].values.astype(np.uint32)

        else:
            fill_val  = def_fill_flt
            slow_data[var_name].fillna(fill_val, inplace=True)
            var_tmp = slow_data[var_name].values

        var_slow  = netcdf_lev1_slow.createVariable(var_name, var_dtype, 'time')
        var_slow[:]  = var_tmp

        for att_name, att_desc in var_atts.items():
            netcdf_lev1_slow[var_name].setncattr(att_name, att_desc)

        # add a percent_missing attribute to give a first look at "data quality"
        perc_miss = fl.perc_missing(var_slow)
        netcdf_lev1_slow[var_name].setncattr('percent_missing', perc_miss)
        netcdf_lev1_slow[var_name].setncattr('missing_value'  , fill_val)

    netcdf_lev1_slow.close() # close and write files for today
    return True

# annoying, convert E to e so that python recognizes scientific notation in logger files...
def convert_sci(array_like_thing):
    return np.float64(array_like_thing.replace('E','e'))

# annoying, get rid of null chars at beginning of lines
def convert_nulchar(array_like_thing):
    nul_char_regex = '[\x00]+'
    valid_data_regex = re.compile(r'^[\.\sa-zA-Z0-9_-]*$')#/^[\sa-zA-Z0-9_-]*$/gm')
    
    #alphanumeric_filter = filter(valid_data_regex.search, array_like_thing)
    #alphanumeric_string = "".join(alphanumeric_filter)  
    alphanumeric_string = re.sub(nul_char_regex, '', array_like_thing)
    if alphanumeric_string != array_like_thing:
        print("not equalssss")
        print("{} ---- {}".format(alphanumeric_string, array_like_thing))
    if '\0' in array_like_thing:
        print("array like thing contains nul charssssss")
        print(alphanumeric_string)
    if '\x00' in array_like_thing:
        print("array like thing contains nulchar")
        print(alphanumeric_string)

    return alphanumeric_string

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
