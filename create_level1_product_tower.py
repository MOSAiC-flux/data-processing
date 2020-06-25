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
#       CR!000X at the base of the tower. 
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
# python3 create_level1_product_tower.py -v -s 20191015 -e 20200231
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

import os, inspect, argparse, time, gc
import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from datetime  import datetime, timedelta
from numpy     import sqrt
from netCDF4   import Dataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

version_msg = '\n\nPS-122 MOSAiC Met Tower processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

def main(): # the main data crunching program

    # the date on which the first MOSAiC data was taken... there will be a "seconds_since" variable 
    global beginning_of_time
    beginning_of_time    = datetime(2019,10,15,0,0) # the first day of MOSAiC tower data
    integ_time_turb_flux = 30 # [minutes] the integration time for the turbulent flux calculation
    process_fast_data    = True
    calc_stats           = False # If False, stats are read from NOAA Services. If True calculated here.
    # should set to True normally because recalculating here accounts for coordinate rotations, QC, and the like

    global data_dir      # make available to the functions at bottom
    global level1_dir
    global printline     # prints a line out of dashes, pretty boring
    global verboseprint  # defines a function that prints only if -v is used when running

    # where do we get the data from
    data_dir   = './data/tower/0_level_raw/'
    level1_dir = './processed_data/tower/level1/'  # where does level1 data go

    # QC params:
    apogee_switch_date = datetime(2019,11,12,10,21,29) # Nov. 12th, 10:21::29

    # these are subdirs of the data_dir
    metek_bottom_dir = 'Metek02m/'
    metek_middle_dir = 'Metek06m/'
    metek_top_dir    = 'Metek10m/'
    metek_mast_dir   = 'Metek30m/'
    licor_dir        = 'Licor02m/'
    tower_logger_dir = 'CR1000X/daily_files/'

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

    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')

    args         = parser.parse_args()
    v_print      = print if args.verbose else lambda *a, **k: None
    verboseprint = v_print

    def printline(startline='',endline=''): # make for pretty printing
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
        if start_time == end_time: # processing current days data, pull out of the dump dir
            tower_logger_dir = '/CR1000X/'

    print('The first day of the experiment is:    %s' % beginning_of_time)
    print('The first day we process data is:      %s' % start_time)
    print('The last day we will process data is:  %s' % end_time)
    print('---------------------------------------------------------------------------------------------')

    # get the and fast raw data day by day, a little different than the stations, but the data is a bit different
    # heavy lifting is in "get_logger_data()" and "get_fast_data()" at the bottom of this code
    # ###########################################################################################################
    day_series = pd.date_range(start_time, end_time)    # we're going to loop over these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    for today in day_series: # loop over the days in the processing range
        tomorrow  = today+day_delta
        seconds_today = pd.date_range(today, tomorrow, freq='S')         

        slow_data = get_slow_data(today)

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
        slow_data = slow_data.sort_index()
        slow_data = slow_data[:][today:tomorrow] 

        # this fills the entries that didn't exist in the ascii files with nans
        slow_data = slow_data.reindex(labels=seconds_today, copy=False)

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

    print('---------------------------------------------------------------------------------------------')
    print('All done! Netcdf output files can be found in: {}'.format(level1_dir))
    print(version_msg)
    print('---------------------------------------------------------------------------------------------')

def get_slow_data(date):
    tower_subdir = 'CR1000X/daily_files/'
    slow_data  = pd.DataFrame()
    fuzzy_window = timedelta(2) # we look for files 2 days before and after because we didn't save even days...(?!)
    # fuzzy_window>=2 required for the earlier days of MOSAiC where logger info is spread out across 'daily-ish' files

    slow_atts, slow_vars = define_level1_slow()
    print('... getting slow logger data from: %s' % data_dir+tower_subdir)

    for data_file in os.listdir(data_dir+tower_subdir):

        if data_file.endswith('.dat'):

            file_words = data_file.split(sep='_')
            if data_file == 'cr1000x_tower.dat':
                use_file = True
                verboseprint('... using the daily file {}'.format(data_file))
            elif len(file_words) > 2:
                file_date  = datetime.strptime(file_words[2]+file_words[3].strip('.dat'),'%m%d%Y%H%M') # (!)
                if file_date >= (date-fuzzy_window) and file_date <= (date+fuzzy_window): # weirdness
                    use_file = True
                    verboseprint('... using the file {} from the day: {}'.format(data_file,file_date))
                else:
                    use_file = False
            else: 
                use_file = False 
            if use_file:
                path  = data_dir+tower_subdir+'/'+data_file
                with open(path) as f:
                    firstline = f.readlines()[1].rsplit(',')
                    num_cols = len(firstline)
                if num_cols != len(slow_vars): # should never happen
                    print("{} ---- {}".format(num_cols,len(slow_vars)))
                    printline()
                    print("{} ---- {}".format(slow_vars,firstline))
                    fl.fatal("# columns in data file doesn't match expected columns, cant work")

                na_vals = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"']
                frame = pd.read_csv(path,parse_dates=[0],sep=',',na_values=na_vals,\
                                    index_col=0,header=[1],skiprows=[2,3],engine='c',\
                                    converters={'gps_alt':convert_sci, 'gps_hdop':convert_sci})#,\
                                    #dtype=dtype_dict)
                slow_data = pd.concat([slow_data,frame]) # is concat computationally efficient?
        else:
            fl.warn('There is a logger file I cant use, this makes no sense... {}'.format(data_file))

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

    frame_list = []
    first_file = True
    for data_file in os.listdir(data_dir+subdir):
        if data_file.startswith('msc') and data_file.endswith('_raw.txt'):
            file_words  = data_file.split(sep='_')
            date_string = file_words[0].strip('msc') # YYYJJJHH

            metek_file_date = datetime.strptime('2'+date_string,'%Y%j%H')

            if metek_file_date >= (date) and metek_file_date < (date+day_delta):
                nfiles += 1
                if first_file:
                    verboseprint('... using the file {} from the day: {}'.format(data_file, metek_file_date))
                    first_file = False
                path        = data_dir+subdir+data_file
                header_list = None

                # read in data finally, then assign colunm names and convert timestamps after
                frame = pd.read_csv(path, parse_dates=False, sep='\s+', na_values=['nan','NaN'],
                                     header=header_list, skiprows=[0], engine='c')

                frame.columns = cols

                # convert timestamp into useable datetime array and then set index to timestamps
                mmssuuu_strs = frame[cols[0]].values.astype('str')
                noaadate     = np.char.zfill(mmssuuu_strs, 7).tolist()
                date_now     = ' {}-{}-{}-{}'.format(metek_file_date.year, metek_file_date.month,
                                                    metek_file_date.day,  metek_file_date.hour)
                time_now     = np.array([nd+date_now for nd in noaadate])
                timestamps   = pd.to_datetime(time_now, format='%M%S%f %Y-%m-%d-%H').rename('TIMESTAMP')
                frame        = frame.set_index(timestamps)
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

# do the stuff to write out level1 fast files, we're going to write these out in a group for each instrument
# I'm not sure if this is the best way, but it seems the most obvious right now.
def write_level1_fast(metek_bottom, metek_middle, metek_top, metek_mast, licor_bottom, date):

    # these keys are the names of the groups in the netcdf files and the
    # strings in the tuple on the right will be the strings that we search for
    # in fast_atts to know which atts to apply to which group/variable, the
    # data is the value of the search string, a dict of dicts...
    inst_dict = {}
    inst_dict['2m_metek']   = ('2m'    , metek_bottom)
    inst_dict['6m_metek']   = ('6m'    , metek_middle)
    inst_dict['10m_metek']  = ('10m'   , metek_top)
    inst_dict['mast_metek'] = ('mast'  , metek_mast)
    inst_dict['2m_licor']   = ('licor' , licor_bottom)

    fast_atts, fast_vars = define_level1_fast() 

    print("... writing level1 fast data {}".format(date))

    # if there's no data, bale (had to look up how to spell bale)
    if metek_bottom.empty and metek_middle.empty and metek_top.empty and metek_mast.empty and licor_bottom.empty:
        print("!!! no data on day {}, returning from write without writing".format(date))
        return False

    out_dir       = level1_dir
    file_str_fast = 'fast_preliminary_tower.{}.nc'.format(date.strftime('%Y%m%d'))

    lev1_fast_name  = '{}/{}'.format(out_dir, file_str_fast)

    global_atts_fast = define_global_atts("fast") # global atts for level 1 and level 2

    netcdf_lev1_fast  = Dataset(lev1_fast_name, 'w')

    for att_name, att_val in global_atts_fast.items(): # write the global attributes to fast
        netcdf_lev1_fast.setncattr(att_name, att_val)

    # loop through the 4 instruments and set vars in each group based on the strings contained in those vars.
    # a bit sketchy but better than hardcoding things... probably. can at least be done in loop
    # and provides some flexibility for var name changes and such.
    for inst in inst_dict: # for instrument in instrument list create a group and stuff it with data/vars

        inst_str  = inst_dict[inst][0]
        inst_data = inst_dict[inst][1]

        curr_group = netcdf_lev1_fast.createGroup(inst) 

        # create time variable for this group with appropriate attributes, etc etc,
        time_name = 'time'
        curr_group.createDimension(time_name, None)

        time_atts_fast   = {'units'     : 'milliseconds since {}'.format(beginning_of_time),
                            'delta_t'   : '0000-00-00 00:01:00',
                            'long_name' : 'milliseconds since the first day of MOSAiC',
                            'calendar'  : 'standard'}
        bot             = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files
        fast_dti        = pd.DatetimeIndex(inst_data.index.values)
        fast_delta_ints = np.floor((fast_dti - bot).total_seconds()*1000) # ms 
        t_fast_ind      = pd.Int64Index(fast_delta_ints)
        t_fast          = curr_group.createVariable(time_name, 'i8',time_name) # seconds since
        t_fast[:]       = t_fast_ind.values
        
        for att_name, att_val in time_atts_fast.items(): curr_group[time_name].setncattr(att_name,att_val)
        
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
                var_fast = curr_group.createVariable(var_name, var_dtype, time_name, zlib=True)
                var_fast[:] = var_tmp # compress fast data via zlib=True

            except Exception as e:
                print("!!! something wrong with variable {} on date {} !!!".format(var_name, date))
                print(inst_data[var_name])
                print("!!! {} !!!".format(e))
                continue

            for att_name, att_desc in var_atts.items(): # write atts to the var now
                curr_group[var_name].setncattr(att_name, att_desc)

            # add a percent_missing attribute to give a first look at "data quality"
            perc_miss = fl.perc_missing(var_fast)
            curr_group[var_name].setncattr('percent_missing', perc_miss)
            curr_group[var_name].setncattr('missing_value'  , fill_val)
            used_vars.append(var_name)  # all done, move on to next variable


    netcdf_lev1_fast.close()
    gc.collect() # manually call garbage collector after all that data shuffling
    return True

def write_level1_slow(slow_data, date): 
    
    # some user feedback into the output
    slow_atts, slow_vars = define_level1_slow() 
    time_name = list(slow_atts.keys())[0] # are slow atts and fast atts always going to be the same?

    all_missing_slow = True 
    first_loop       = True
    n_missing_denom  = 0

    # count missing percs for each var and print useful infow
    for var_name, var_atts in slow_atts.items():
        if var_name == time_name: continue
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
        print("!!! no data on day {}, returning from write without writing".format(date))
        return False

    print("... writing level1 slow data {}, ~{}% of slow data is present".format(date, 100-avg_missing_slow))

    out_dir       = level1_dir
    file_str_slow = 'slow_preliminary_tower.{}.nc'.format(date.strftime('%Y%m%d'))
    lev1_slow_name  = '{}/{}'.format(out_dir, file_str_slow)

    global_atts_slow = define_global_atts("slow") # global atts for level 1 and level 2

    netcdf_lev1_slow  = Dataset(lev1_slow_name, 'w', format='NETCDF4_CLASSIC')

    for att_name, att_val in global_atts_slow.items(): # write the global attributes to slow
        netcdf_lev1_slow.setncattr(att_name, att_val)

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_lev1_slow.createDimension('time', None)
    time_atts_slow   = {'units'     : 'seconds since {}'.format(beginning_of_time),
                        'delta_t'   : '0000-00-00 00:01:00',
                        'long_name' : 'seconds since the first day of MOSAiC',
                        'calendar'  : 'standard'}
    bot = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files

    # create the arrays that are integer intervals from  'time since beginning of mosaic' for indexing netcdf files
    bot = np.datetime64(beginning_of_time)
    slow_dti = pd.DatetimeIndex(slow_data.index.values)
    slow_delta_ints = np.floor((slow_dti - bot).total_seconds())      # seconds
    t_slow_ind = pd.Int64Index(slow_delta_ints)
    t_slow = netcdf_lev1_slow.createVariable('time', 'i','time') # seconds since
    t_slow[:] = t_slow_ind.values

    for att_name, att_val in time_atts_slow.items(): netcdf_lev1_slow['time'].setncattr(att_name,att_val)

    for var_name, var_atts in slow_atts.items():
        if var_name == time_name: continue # already did that

        var_dtype = slow_data[var_name].dtype

        if fl.column_is_ints(slow_data[var_name]):
        # if issubclass(var_dtype.type, np.integer): # netcdf4 classic doesnt like 64 bit integers
            var_dtype = np.int32
            fill_val  = def_fill_int
            slow_data[var_name].fillna(fill_val, inplace=True)
            var_tmp = slow_data[var_name].values.astype(np.int32)

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

    gc.collect() # maybe this helps with the random (rare) memory access crashes in the netcdf/hdf5 libs?
    netcdf_lev1_slow.close() # close and write files for today
    return True

# annoying, convert E to e so that python recognizes scientific notation in logger files...
def convert_sci(array_like_thing):
    return np.float64(array_like_thing.replace('E','e'))

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
