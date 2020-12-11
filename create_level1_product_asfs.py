#!/usr/bin/env python3
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
# To create a uniform "level1" data product for the three remote flux stations (aka ASFS')
# at MOSAiC and to document the data processing workflow. At this time, this code only
# uses data from the SD cards. This will change if we're ever receiving data via
# radio/iridium and fail to recover an SD card.
#
# Function calls are parallelized/threaded when possible and thus this software
# occupies 4 cores most of the time it is running. But, it's entirely I/O limited and so
# it runs much faster on my NVME/SSD based comp than it does on the rusty disked server at
# NOAA. 
# 
# This code creates two different *daily* NetCDF files from raw observations by ASFS' at
# MOSAiC. "level1" products are archival files with little to no data QC, intended to be
# packaged binary files of the raw data. There are "slow" and "fast" versions of level1
# files. 
#
# Descriptions of these two different output files and their contents:
# (look at "asfs_data_definitions.py" for detailed product description)
# ############################################################################################
# level1 "slow":
#
#       Observations from all instruments averaged over 1 minute intervals. These include
#       statistics on the one minute intervals as logged at the stations. These level1 files
#       are raw uncalibrated data.
# 
# level1 "fast":
# 
#       Observations from metek sonic anemometers and licor CO2/H2O gas rapid gas
#       analyzer. These observations are taken at 20Hz barring any problems. For more
#       documentation on the timing of these observations and how this was processed, please
#       see the comments in the "get_fast_data()" function. These level1 files are raw
#       uncalibrated data.
#
# HOWTO:
#
# To run this package with verbose printing over all ofthe data:
# python3 create_level1_product_asfs.py -v -s 20191005 -e 20201005 -p /Projects/MOSAiC/
#
# To profile the code and see what's taking so long:
# python3 -m cProfile -s cumulative ./create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201 
#
# RELEASE-NOTES:
#
# Please look at CHANGELOG-asfs.md for notes on changes/improvements with each version.
#
# ###############################################################################################
#
# look at these files for documentation on netcdf vars and nomenclature
# as well as additional information on the syntax used to designate certain variables here
from asfs_data_definitions import define_global_atts, get_level1_col_headers
from asfs_data_definitions import define_level1_slow, define_level1_fast

import functions_library as fl

import os, inspect, argparse, time
 
import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere, inf=nan
 
import socket

global nthreads 
if '.psd.' in socket.gethostname():
    nthreads = 60  # the twins have 64 cores, it won't hurt if we use <20
else: nthreads = 3 # laptops don't tend to have 64 cores
nthreads=1
from multiprocessing import Process as P
from multiprocessing import Queue   as Q

# need to debug something? kills multithreading to step through function calls
# from multiprocessing.dummy import Process as P
# from multiprocessing.dummy import Queue   as Q
# nthreads = 1

from datetime  import datetime, timedelta
from numpy     import sqrt
from netCDF4   import Dataset, MFDataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

# just in case... avoids some netcdf nonsense involving the default file locking across mounts
os.environ['HDF5_USE_FILE_LOCKING']='FALSE' # just in case
os.environ['HDF5_MPI_OPT_TYPES']='TRUE'     # just in case

version_msg = '\n\nPS-122 MOSAiC Flux team ASFS processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)

def main(): # the main data crunching program

    global trial, n_trial_files
    trial = False # FOR TESTING PURPOSES ONLY, takes random xxx files and cuts to save debugging time
    n_trial_files = 2000

    # the UNIX epoch... provides a common reference, used with base_time
    global epoch_time
    epoch_time        = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring
    global verbose       # a useable flag to allow subroutines etc when using -v 

    global data_dir, level1_dir

    flux_stations = ['asfs30']#, 'asfs40', 'asfs50'] # our beauties
    apogee_switch_date = {}
    apogee_switch_date['asfs30'] = datetime(2019,12,13,11,9,0) # 
    apogee_switch_date['asfs40'] = datetime(2019,12,13,11,9,0) # 
    apogee_switch_date['asfs50'] = datetime(2019,11,14,6,11,0) # 

    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over all the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')
    parser.add_argument('-p', '--path', metavar='str', help='base path to data up to, including /data/, include trailing slash')  # pass the base path to make it more mobile
    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    args         = parser.parse_args()
    verbose      = True if args.verbose else False # use this to run segments of code via v/verbose flag
    v_print      = print if verbose else lambda *a, **k: None     # placeholder
    verboseprint = v_print # use this function to print a line if the -v/--verbose flag is provided

    if args.path: data_dir = args.path
    else: data_dir = '/Projects/MOSAiC/'
    
    level1_dir = data_dir #'./processed_data/level1/'  # where does level1 data go

    def printline(startline='',endline=''): # make for pretty printing
        print('{}--------------------------------------------------------------------------------------------{}'
              .format(startline, endline))

    global start_time, end_time
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

    printline(endline="\n")
    print('The first day we  process data is:     %s' % str(start_time+timedelta(1)))
    print('The last day we will process data is:  %s' % str(end_time-timedelta(1)))
    printline("\n")
    
    # program logic starts here, the logic flow goes like this:
    # #########################################################
    # 
    #     1) read in all days of slow data from raw data
    #     2) loop over days requested
    #     3) for that day, pull in fast data from raw data
    #     4) do level1 qc for that day
    #     5) write level 1 files for that day
    #     6) go to next day
    #     -----------------> all done here, go run the level2 code
    # 
    # ... OK, here we go then
    # ##########################################################################################
    # read *all* of the slow data... why have so much RAM if you don't use it?

    print("Getting data from raw DAQ files from stations: {}!!".format(flux_stations))
    print("   ... and doing it in threads, hold onto your britches")
    printline()
    # get the "slow" raw data first, heavy lifting is in "get_slow_data()" the slow
    # dataset is "small", so we load it all at once
    # #####################################################################################
    # dataframes go in dicts with station keys, we parallellize data ingesting to save time.
    slow_data   = {}
    slow_q_dict = {}; slow_p_dict = {}
    
    slow_atts, slow_vars = define_level1_slow()
    for curr_station in flux_stations:
        # try to save some time and multithread the reading
        slow_q_dict[curr_station] = Q()
        # run the threads for retreiving data
        P(target=get_slow_data, \
               args=(curr_station, start_time, end_time, \
                     slow_q_dict[curr_station])).start()

        if nthreads < len(flux_stations):
            slow_data[curr_station] = slow_q_dict[curr_station].get()

    # wait to finish slow first, then get results from thread queue
    if nthreads >= len(flux_stations):
        for curr_station in  flux_stations:
            slow_data[curr_station] = slow_q_dict[curr_station].get()

            verboseprint("\n===================================================")
            verboseprint("Data and observations provided by {}:".format(curr_station))
            verboseprint('===================================================')
            if verbose: slow_data[curr_station].info(verbose=True) # must be contained;

    print("\n... got all slow data from files, exiting for timing")

    # tell user about big data gaps, good sanity check for downtime
    # using batt_volt_Avg because if the battery voltage is missing....
    if verbose: 
        for curr_station in  flux_stations:
            curr_slow_data = slow_data[curr_station]
            printline()
            bv = curr_slow_data["batt_volt_Avg"]

            threshold   = 60 # warn if the station was down for more than 60 minutes
            nan_groups  = bv.isnull().astype(int).groupby(bv.notnull().astype(int).cumsum()).cumsum()
            mins_down   = np.sum( nan_groups > 0 )

            prev_val   = 0 
            if np.sum(nan_groups > threshold) > 0:
                print("\n!! {} was down for at least {} minutes on the following dates: ".format(curr_station, threshold))
                for i,val in enumerate(nan_groups):
                    if val == 1 and prev_val == 0: 
                        down_start = bv.index[i]
                    if val == 0  and prev_val > 0 and prev_val > threshold: 
                        print("---> from {} to {} ".format(down_start, bv.index[i]))
                    prev_val = val

                perc_down = round(((bv.size-mins_down)/bv.size)*100, 3)
                print("\nFor your time range, the station was down for a total of {} minutes...".format(mins_down))
                print("... which gives an uptime of approx {}% over this period".format(perc_down))

            else:
                print("\nStation {} was alive for the entire time range you requested!! Not bad... \n"
                      .format(curr_station, threshold))

    printline()
    print("\nGetting list of fast files for each station and sorting them by date... \n")
    printline()

    # there's too much fast data, we need to read in and write out each
    # day individually if coded like slow above, station "fast" datasets take
    # 32Gb of RAM (I only have 40Gb) and that's only for legs 1 and 2
    # #########################################################################
    fast_atts, fast_cols = define_level1_fast()
    fast_file_list       = {} # a list of fast data files for each station and the
    first_timestamp_list = {} # corresponding first file timestamp, sorted in time
    fast_file_q = {}
    for curr_station in flux_stations: # get station file lists in parallel
        fast_file_q[curr_station] = Q()
        P(target=get_fast_file_list, \
               args=(curr_station, fast_file_q[curr_station])).start()

    for curr_station in flux_stations: # wait for threads and get return values
        first_timestamp_list[curr_station] = fast_file_q[curr_station].get()
        fast_file_list[curr_station]       = fast_file_q[curr_station].get()

    # we have to actually import the fast data on a daily basis for each station, so this
    # is all done in a loop for each day, and then level1 QC/writing for both slow/fast
    # data is done in that loop.... very annoying but seems the best solution
    # ##############################################################################################
    day_series = pd.date_range(start_time+timedelta(1), end_time-timedelta(1)) # data was requested for these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    printline()
    print("\n Got all slow data and have a list of fast files, now processing each day...\n")
    printline()

    nthreads_station = int(np.floor(nthreads/3))
    station_q_dict = {}
    station_p_dict = {} 

    # defined here, called below in loops, this is the code for processing one days data, 
    # done this way so the code can be threaded
    def process_station_day(curr_station, slow_data_today, day_q):

        # queue used to retreive data for today
        if i_day % 1 == 0: print("\nCurrently processing level1 data for {} in {}".format(today, curr_station))

        # run the threads for retreiving data
        fast_data_today = get_fast_data(today, fast_file_list[curr_station],
                                        first_timestamp_list[curr_station], curr_station)

        # ########################################################################
        # level 1 cleaning and QC starts here. this is *only* minimal fixes fit for
        # archiving purposes, no more no less. there should be very little code before
        # level 1 files are written out... and it's all here.
        # ########################################################################
        # switch apogee target & body T if necessary, date apogee switched in CR1000X software

            # correct flux plate sign code from ola
            # jd_flxp_corr(1,1:2)=[modystr(12)-1+31+12/24+00/1440 modystr(10)-1+1+12/24+00/1440]; %ASFS30
            # jd_flxp_corr(2,1:2)=[modystr(12)-1+31+12/24+00/1440 modystr(12)-1+31+12/24+00/1440]; %ASFS40
            # jd_flxp_corr(3,1:2)=[modystr(10)-1+1+12/24+00/1440 modystr(12)-1+31+12/24+00/1440]; %ASFS50
            # ind=[73 77];
            # for ia=1:3
            #   for k=1:2   
            #     irev=find(jd_pldt<jd_flxp_corr(ia,k));
            #     if length(irev)>0
            #       dataday(ia,ind(k),irev)=-dataday(ia,ind(k),irev);
            #     end
            #     flxp(ia,k,1:iz)=dataday(ia,ind(k),1:iz);
            #   end
            # end

        #if not slow_data_today.empty:

        if today == apogee_switch_date[curr_station].replace(hour=0, minute=0, second=0):
            targ_T = slow_data_today['apogee_targ_T_Avg'].copy()
            body_T = slow_data_today['apogee_body_T_Avg'].copy()
            targ_T_std = slow_data_today['apogee_targ_T_Std'].copy()
            body_T_std = slow_data_today['apogee_body_T_Std'].copy()

            slow_data_today['apogee_targ_T_Avg'] = \
                np.where(slow_data_today.index < apogee_switch_date[curr_station],\
                         body_T,\
                         targ_T)
            slow_data_today['apogee_body_T_Avg'] = \
                np.where(slow_data_today.index < apogee_switch_date[curr_station],\
                         targ_T,\
                         body_T)

            slow_data_today['apogee_targ_T_Std'] = \
                np.where(slow_data_today.index < apogee_switch_date[curr_station],\
                         body_T_std,\
                         targ_T_std)
            slow_data_today['apogee_body_T_Std'] = \
                np.where(slow_data_today.index < apogee_switch_date[curr_station],\
                         targ_T_std,\
                         body_T_std)

        elif today < apogee_switch_date[curr_station]:
            cs_targ_avg = slow_data_today['apogee_targ_T_Avg'] 
            cs_body_avg = slow_data_today['apogee_body_T_Avg'] 
            slow_data_today['apogee_targ_T_Avg'] = cs_body_avg
            slow_data_today['apogee_body_T_Avg'] = cs_targ_avg

            cs_targ_std = slow_data_today['apogee_targ_T_Std'] 
            cs_body_std = slow_data_today['apogee_body_T_Std'] 
            slow_data_today['apogee_targ_T_Std'] = cs_body_std
            slow_data_today['apogee_body_T_Std'] = cs_targ_std

        # level1 qc/processing done write out level1 raw/'ingest' files to netcdf today
        today_empty_dict = {} # boolean keeper of if there was no data today

        sdt   = slow_data_today
        fdt   = fast_data_today
        satts = slow_atts
        fatts = fast_atts

        if not sdt.empty or not fdt.empty: 
            # run the threads for retreiving data
            write_level1_netcdfs(sdt, satts, fdt, fatts, curr_station, today)
        else:
            print("... no data available for {} on {}".format(curr_station, today))

        # process_station_days() ends here
        day_q.put(True)
        return 

    nthreads_station = int(np.floor(nthreads/3)) # num of days we can throw into child procs before waiting

    q_dict = {}  # setup queue storage
    for curr_station in flux_stations: q_dict[curr_station] = []

    # call processing by day then station (allows threading for processing a single days data)
    for i_day, today in enumerate(day_series): # loop over the days in the processing range and get a list of files
        tomorrow = today+day_delta
        for curr_station in flux_stations:
            slow_data_today = slow_data[curr_station][today:tomorrow]

            q_today = Q()
            q_dict[curr_station].append(q_today)
            P(target=process_station_day,
              args=(curr_station, slow_data_today, q_today)).start()

            if nthreads < len(flux_stations): 
                q_dict[curr_station][0].get()
                q_dict[curr_station] = []

        if nthreads > 1: 
            if (i_day+1) % nthreads_station == 0 or today == day_series[-1]:
                for curr_station in flux_stations:
                    for qq in q_dict[curr_station]: qq.get()
                    q_dict[curr_station] = []

    printline()
    print('All done! Netcdf output files can be found in: {}'.format(level1_dir))
    printline()
    print(version_msg)
    printline()

# pulls in logger text files from sdcard data and returns a dataframe and a list of data attributes (units, etc)
# qq returns the results from a threaded call and is of Queue class
def get_slow_data(station, start_time, end_time, qq): 

    searchdir = data_dir+station+'/0_level_raw/site_visits/'

    # look through station subdirectories and only take data file if it's an "SDcard" folder... 
    # returns file path list for all files in all sd card data dirs for this station, i.e. a list of every data file
    card_file_list = get_card_file_list('slow', searchdir) 
    print('... found {} slow files in directory {}'.format(len(card_file_list), searchdir))
    frame_list = [] # list of frames from files... to be concatted after loop
    data_atts, data_cols  = define_level1_slow()

    # called in process/queue loop over card_file_list below
    def read_slow_csv(dfile, file_q):
        # 'cause campbell is.... inconsistent
        na_vals = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"','']

        # count the columns in the first line and select the col headers out of asfs_data_definitions.py
        with open(dfile) as ff: 
            topline = ff.readline().rsplit(',')
            num_cols = len(topline)
            if num_cols > 8: # you dont have a header
                first_time = datetime.strptime(topline[0].strip('"'), '%Y-%m-%d %H:%M:%S')
            if num_cols == 8: # then the file has a header
                num_cols = len(ff.readline().rsplit(',')) # so get the right number from the next line
                first_time = ff.readline().rsplit(',')[3].strip('"')              

        if num_cols == 99 and station == 'asfs30' and first_time > datetime(2020,4,12,16,22):
            cver = 1
        elif num_cols == 89 and station == 'asfs30' and first_time > datetime(2020,5,5,0,0):     
            cver = 1
        else: cver = 0

        cols  = get_level1_col_headers(num_cols, cver)
        frame = pd.read_csv(dfile, parse_dates=[0], sep=',', na_values=na_vals,\
                            index_col=0, engine='c', names=cols)
        file_q.put(frame)
        
    # divide the files into pools and call thread_read() on the list of files in parallel
    nthreads_station = int(np.floor(nthreads/3))
    if nthreads_station == 0 : nthreads_station=1
    q_list = []
    for file_i, data_file in enumerate(card_file_list):

        if (file_i % 250 == 0) and file_i != 0:  
            verboseprint("... at {} of {} for {} slow data".format(file_i, len(card_file_list),station))

        file_q = Q()
        q_list.append(file_q)
        P(target=read_slow_csv, args=(data_file, file_q)).start()

        if (file_i+1) % nthreads_station == 0 or data_file == card_file_list[-1]:
            for fq in q_list:
                new_frame = fq.get()
                frame_list.append(new_frame)
            q_list = []
            if trial and n_trial_files<file_i: break
 
    print(f"... got all files read, got all threads back for {station}. now we concat")
    data_frame = pd.concat(frame_list) # is concat computationally efficient?    
    data_frame = data_frame.sort_index() # sort chronologically    
    data_frame.drop_duplicates(inplace=True) # get rid of duplicates
    data_frame = data_frame[start_time:end_time] # done gathering data, now narrow down to requested window

    # some sanity checks
    n_dupes = ~data_frame.duplicated().size
    if data_frame.empty: # 'fatal' is a print function defined at the bottom of this script that exits
        print("No {} data for requested time range {} ---> {} ?\n".format(searchdir,start_time,end_time))
        print("... Im sorry... no data will be created for {}".format(station))
        qq.put(data_frame)
        return

    if n_dupes > 0 : fl.fatal("... there were {} duplicates for {} in this time range!!\n you got duped, dying".format(n_dupes, searchdir))

    # now, reindex for every second in range and fill with nans so that the we commplete record
    mins_range = pd.date_range(start_time, end_time, freq='T') # all the minutes today, for obs
    try:
        data_frame = data_frame.reindex(labels=mins_range, copy=False)
    except Exception as ee:
        printline()
        print("There was an exception reindexing for {}".format(searchdir))
        print(' ---> {}'.format(ee))
        printline()
        print(data_frame.index[data_frame.index.duplicated()])
        print("...dropping these duplicate indexes... ")
        printline()
        data_frame = data_frame.drop(data_frame.index[data_frame.index.duplicated()], axis=0)
        print(" There are now {} duplicates in DF".format(len(data_frame[data_frame.index.duplicated()])))
        print(" There are now {} duplicates in timeseries".format(len(mins_range[mins_range.duplicated()])))
        data_frame = data_frame.reindex(labels=mins_range, copy=False)

    # why doesn't the dataframe constructor use the name from cols for the index name??? silly
    data_frame.index.name = data_cols[0]
    
    # now we subtract 1 min from the index so that the times mark the beginning rather than the end of the 1 min avg time, more conventional-like
    data_frame.index = data_frame.index-pd.Timedelta(1,unit='min')  
    
    # sort data by time index and return data_frame to queue
    qq.put(data_frame)

# finds all files for station, returning a list of the timestamps from
# the first lines of each file and a sorted list of filenames
def get_fast_file_list(station, qq):

    # look through station subdirectories and only take data file if it's an "SDcard" folder... 
    # returns list of every data file path in sdcard subdirs
    searchdir          = data_dir+station+'/0_level_raw/site_visits/'
    entire_file_list   = get_card_file_list('fast', searchdir) 
    first_ts_series    = []  # keep the timestamp from first line to concat in the correct order
    unsorted_file_list = []
    print('... found {} fast files in directory {}'.format(len(entire_file_list), searchdir))

    for file_n, data_file in enumerate(entire_file_list):
        if file_n % 1000 == 0 and file_n != 0:  
            verboseprint("... currently on file {} of {} for fast files in {} "
                         .format(file_n, len(entire_file_list), searchdir))

        # count the columns in the first line, if less than expected, bail
        f = open(data_file)
        try: firstline=f.readline().rsplit(',')
        except Exception as e:
            print("!!! problem with data file {}!!!".format(data_file))
            print("!!! {} !!!".format(e))
            continue
        f.close()

        num_cols  = len(firstline)
        if (num_cols > 11 or num_cols <7): 
            print("!!! The number of columns should be 7 or 11, something's up !!!")
            print("!!! not using {} with cols {}".format(data_file,num_cols))
            continue

        # keep first timestamp for sorting
        try: 
            first_timestamp = np.datetime64(datetime.strptime(firstline[0].strip('"'), '%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            print("!!! something was wrong with the timestamp format in {} !!!".format(data_file))
            print("!!! {} !!!".format(firstline))
            print("!!! {} !!!".format(e))
            continue

        first_ts_series.append(first_timestamp)
        unsorted_file_list.append(data_file)

    # use numpy to sort files by first timestamp
    ftss = np.array(first_ts_series)
    ufl  = np.array(unsorted_file_list)

    sorted_timestamps = ftss[np.argsort(ftss)]
    sorted_file_list  = ufl[np.argsort(ftss)]

    qq.put(sorted_timestamps.tolist())
    qq.put(sorted_file_list.tolist())

# gets data for the 20hz metek sonics, complicated because of nuances grabbing fast data
# via logger this function pulls files into dataframe, sorted based on time of first
# entry in file, then interpolates the timestamps so that each fast obs gets a
# unique/approximate timestamp...
# finally it returns the day of data requested with  the new interpolated timestamps
# ########################################################################################
# sorry Chris, I hope this function isn't too incomprehensible/ugly. and if it is, then I
# hope it just_works(tm) and you don't have to touch it.
def get_fast_data(date, fast_file_list, first_timestamp_list, curr_station): 

    # get data cols/attributes from definitions file
    data_atts, data_cols = define_level1_fast()

    day_delta        = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    # half_day_delta = pd.to_timedelta(43200000000 ,unit='us') # we want to eliminate interpolation boundary conds
    eighth_day_delta = pd.to_timedelta(10800000000 ,unit='us') # we want to eliminate interpolation boundary conds

    na_vals = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"','']

    if len(fast_file_list) != len(first_timestamp_list): # sanity check
        fl.fatal("something went wrong with fast file stuff... weird")

    # we search for data outside of today because we need to interpolate timestamps...
    # ... a quarter day is too much but... too much might be good enough
    ldb = date-eighth_day_delta           # lower_date_bound for data to pull in for today
    udb = date+day_delta+eighth_day_delta # upper_date_bound for data to pull in for today

    inds_to_use = [i for i, tstamp in enumerate(first_timestamp_list) if (tstamp>ldb and tstamp<udb)]

    if len(inds_to_use) == 0 :
        verboseprint("!!! NO FAST DATA FROM {} FOR DAY {} !!!".format(curr_station, date))
        return pd.DataFrame(columns=data_cols)

    frame_list  = [] # all the frames created from files from today
    for file_i in inds_to_use:
        cols      = data_cols.copy()
        data_file = fast_file_list[file_i]

        # count the columns in the first line, if less than expected, bail
        with open(data_file) as f: 
            firstline = f.readline().rsplit(',')
            num_cols  = len(firstline)

        try:  # ingest each csv into own data frame and keep in list
            frame = pd.read_csv(data_file, parse_dates=[0], sep=',', na_values=na_vals,\
                                engine='c', names=cols)
            frame_list.append(frame)   
        except Exception as e:
            printline()
            print(e)
            print("!!! There was an exception reading file {}, skipping!!!".format(data_file))
            printline()

    # reindex each frame to avoid collisions before concatting/interpolating the time column/axis
    reindex_start = 0 
    for curr_frame in frame_list: # reindex each data frame properly to avoid collisions 
        curr_frame.index = range(reindex_start, reindex_start+len(curr_frame.index))
        reindex_start    = reindex_start + len(curr_frame.index) # increment by num data rows for next loop

    full_frame  = pd.concat(frame_list) # is concat computationally efficient?

    # full_frame contains all the data now, in the correct order, but times are wonky and
    # it's indexed by an incremented integer, not so useful. fix it by interpolating timestamps
    # and then reindexing return_frame with interpolated timestamps
    times = pd.DataFrame(full_frame["TIMESTAMP"])
    extra_seconds = times["TIMESTAMP"].iloc[-1]+timedelta(seconds=5) # boundary case, don't lose data at tail
    times = times.append({"TIMESTAMP": extra_seconds}, ignore_index=True)
    times.loc[times["TIMESTAMP"].duplicated(),"TIMESTAMP"] = nan # replace duplicate values with nan

    # to interpolate times, we convert the timestamps to a float timedelta
    # ... interp... then convert interpolated deltas back to complete timestamp series
    t0 = times["TIMESTAMP"].min()
    nn_times = times["TIMESTAMP"].notnull()
    times.loc[nn_times, 'T_DELTA'] = (times.loc[nn_times,"TIMESTAMP"] - t0).dt.total_seconds()
    times_interped = t0 + pd.to_timedelta(times.T_DELTA.interpolate(), unit='s')
    return_times   = times_interped.iloc[0:-1].copy() # pop the boundary case added above

    # all done, put the interpolated time column back into complete dataframe and send back to processing
    full_frame["TIMESTAMP"] = np.where(True, return_times, return_times) # np.where is _much_ faster than pandas.. :\
    full_frame.index        = full_frame["TIMESTAMP"]
    
    # not quite done. now we subtract 5 sec (length of the scan) from the index so that the times mark the beginning rather than the end
    full_frame.index = full_frame.index-pd.Timedelta(5,unit='sec')

    return_frame = full_frame[date:date+day_delta]
    n_entries    = return_frame.index.size

    verboseprint("... {}/1728000 fast entries on {} for {}, representing {}% data coverage"
                 .format(n_entries, date, curr_station, round((n_entries/1728000)*100.,2)))
    return return_frame

# function that searches sitevisit dirs looking for SDcard directory and returns data file paths in a list
def get_card_file_list(filestr, searchdir): # filestr is the name in the data file you want to get slow/fast/etc
    card_file_list = [] 
    for subdir, dirs, files in os.walk(searchdir):
        for curr_dir in dirs:
            if "sdcard" in curr_dir.lower():
                card_dir = subdir+'/'+curr_dir
                card_files_in_dir = []
                for f in os.listdir(card_dir):
                    if filestr in f and f.endswith('.dat') and not f.startswith('._'):
                        card_files_in_dir.append(card_dir+'/'+f)
                card_file_list.extend(card_files_in_dir) # lets not make a list of lists
    return card_file_list

# do the stuff to write out the level1 files, after finishing this it could probably just be one
# function that is called separately for fast and slow... : \ maybe refactor someday.... mhm
def write_level1_netcdfs(slow_data, slow_atts, fast_data, fast_atts, curr_station, date):
    l_site_names = { "asfs30" : "L2", "asfs40" : "L1", "asfs50" : "L3"}

    # some user feedback into the output
    time_name   = list(slow_atts.keys())[0] # are slow atts and fast atts always going to be the same?
    max_str_len = 30 # these lines are for printing prettilly

    slow_atts_iter   = slow_atts.copy() # so we can delete stuff from slow atts and not mess with iterator
    slow_atts_copy   = slow_atts.copy() # so we can delete stuff from slow atts and not mess with iterator
    all_missing_slow = True 
    first_loop       = True
    n_missing_denom  = 0

    for var_name, var_atts in slow_atts_iter.items():
        if var_name == time_name: continue
        try: dt = slow_data[var_name].dtype
        except KeyError as e: 
            ## fixme so that each df always has each column, even if with no data
            #print(" !!! no {} in data for {} ... does this make sense??".format(var_name, curr_station))
            del slow_atts_copy[var_name]
            continue
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

    fast_atts_copy   = fast_atts.copy() # so we can delete stuff from slow atts and not mess with iterator
    all_missing_fast = True
    first_loop       = True
    for var_name, var_atts in fast_atts_copy.items():
        if var_name == time_name: continue
        perc_miss = fl.perc_missing(fast_data[var_name].values)
        if perc_miss < 100: all_missing_fast = False

    # if there's no data, bale
    if all_missing_fast and all_missing_slow:
        print("!!! no data on day {} for {}, returning from write without writing".format(curr_station, date))
        return False

    print("... writing level1 for {} on {}, ~{}% of slow data is present".format(curr_station, date, 100-avg_missing_slow))

    out_dir       = level1_dir+curr_station+"/1_level_ingest_"+curr_station
    file_str_fast = '/mos{}fast.level1.{}.nc'.format(curr_station, date.strftime('%Y%m%d.%H%M%S'))
    file_str_slow = '/mos{}slow.level1.{}.nc'.format(curr_station, date.strftime('%Y%m%d.%H%M%S'))

    lev1_slow_name  = '{}/{}'.format(out_dir, file_str_slow)
    lev1_fast_name  = '{}/{}'.format(out_dir, file_str_fast)

    global_atts_slow = define_global_atts(curr_station, "slow") # global atts for level 1 and level 2
    global_atts_fast = define_global_atts(curr_station, "fast") # global atts for level 1 and level 2

    netcdf_lev1_slow  = Dataset(lev1_slow_name, 'w')#, format='NETCDF4_CLASSIC')
    netcdf_lev1_fast  = Dataset(lev1_fast_name, 'w')#, format='NETCDF4_CLASSIC')

    for att_name, att_val in global_atts_slow.items(): # write the global attributes to slow
        netcdf_lev1_slow.setncattr(att_name, att_val)
        
    for att_name, att_val in global_atts_fast.items(): # write the global attributes to fast
        netcdf_lev1_fast.setncattr(att_name, att_val)

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_lev1_slow.createDimension('time', None)
    netcdf_lev1_fast.createDimension('time', None)

    try:
        fms = slow_data.index[0]
    except Exception as e:
        print("\n\n\n!!! Something went wrong, there's fast data for today but no slow data")
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
    base_slow = netcdf_lev1_slow.createVariable('base_time', 'u4') # seconds since
    base_fast = netcdf_lev1_fast.createVariable('base_time', 'u4') # seconds since
    base_slow[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])      # seconds
    base_fast[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])      # seconds

    base_atts = {'string'     : '{}'.format(bot),
                 'long_name' : 'Base time since Epoch',
                 'units'     : 'seconds since {}'.format(et),
                 'ancillary_variables'  : 'time_offset',}
    for att_name, att_val in base_atts.items(): netcdf_lev1_slow['base_time'].setncattr(att_name,att_val)
    for att_name, att_val in base_atts.items(): netcdf_lev1_fast['base_time'].setncattr(att_name,att_val)

    # here we create the array and attributes for 'time'
    t_atts_slow   = {'units'     : 'seconds since {}'.format(tm),
                     'delta_t'   : '0000-00-00 00:01:00',
                     'long_name' : 'Time offset from midnight',
                     'calendar'  : 'standard',}

    t_atts_fast = t_atts_slow.copy()
    t_atts_fast['units']     = 'milliseconds since {}'.format(tm)
    t_atts_fast['delta_t']   = '0000-00-00 00:01:00.001',

    bt_atts_slow   = {'units'     : 'seconds since {}'.format(bot),
                     'delta_t'   : '0000-00-00 00:01:00',
                     'long_name' : 'Time offset from base_time',
                     'calendar'  : 'standard',}

    bt_atts_fast           = t_atts_slow.copy()
    bt_atts_fast['units']  = 'milliseconds since {}'.format(bot)
    t_atts_fast['delta_t'] = '0000-00-00 00:01:00.001',

    slow_dti = pd.DatetimeIndex(slow_data.index.values)
    fast_dti = pd.DatetimeIndex(fast_data.index.values)

    slow_delta_ints = np.floor((slow_dti - tm).total_seconds())      # seconds
    fast_delta_ints = np.floor((fast_dti - tm).total_seconds()*1000) # ms 

    t_slow_ind = pd.Int64Index(slow_delta_ints)
    t_fast_ind = pd.Int64Index(fast_delta_ints)

    # set the time dimension and variable attributes to what's defined above
    t_slow = netcdf_lev1_slow.createVariable('time', 'u4','time') # seconds since
    t_fast = netcdf_lev1_fast.createVariable('time', 'u8','time') # seconds since

    # now we create the array and attributes for 'time_offset'
    bt_slow_dti = pd.DatetimeIndex(slow_data.index.values)   
    bt_fast_dti = pd.DatetimeIndex(fast_data.index.values)

    bt_slow_delta_ints = np.floor((bt_slow_dti - bot).total_seconds())      # seconds
    bt_fast_delta_ints = np.floor((bt_fast_dti - bot).total_seconds()*1000) # ms 

    bt_slow_ind = pd.Int64Index(bt_slow_delta_ints)
    bt_fast_ind = pd.Int64Index(bt_fast_delta_ints)

    # set the time dimension and variable attributes to what's defined above
    bt_slow = netcdf_lev1_slow.createVariable('time_offset', 'u4','time') # seconds since
    bt_fast = netcdf_lev1_fast.createVariable('time_offset', 'u8','time')

    # this try/except is vestigial, this bug should be fixed
    try:
        t_slow[:] = t_slow_ind.values
        bt_slow[:] = bt_slow_ind.values
    except RuntimeError as re:
        print("!!! there was an error creating slow time variable with netcdf/hd5 I cant debug !!!")
        print("!!! {} !!!".format(re))
        raise re

    try:
        t_fast[:] = t_fast_ind.values
        bt_fast[:] = bt_fast_ind.values
    except RuntimeError as re:
        print("!!! there was an error creating fast time variable with netcdf/hd5 I cant debug !!!")
        print("!!! {} !!!".format(re))
        raise re

    for att_name, att_val in t_atts_slow.items(): netcdf_lev1_slow['time'].setncattr(att_name,att_val)
    for att_name, att_val in t_atts_fast.items(): netcdf_lev1_fast['time'].setncattr(att_name,att_val)

    for att_name, att_val in bt_atts_slow.items(): netcdf_lev1_slow['time_offset'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts_fast.items(): netcdf_lev1_fast['time_offset'].setncattr(att_name,att_val)

    for var_name, var_atts in slow_atts_copy.items():
        if var_name == time_name: continue

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

    for var_name, var_atts in fast_atts.items():
        if var_name == time_name: continue

        var_dtype = fast_data[var_name].dtype

        if var_dtype == object:
            continue 

        elif fl.column_is_ints(fast_data[var_name]):
        # if issubclass(var_dtype.type, np.integer): # netcdf4 classic doesnt like 64 bit integers
            var_dtype = np.int32
            fill_val  = def_fill_int
            fast_data[var_name].fillna(fill_val, inplace=True)
            var_tmp   = fast_data[var_name].values.astype(np.int32)

        else:
            fill_val  = def_fill_flt
            fast_data[var_name].fillna(fill_val, inplace=True)
            var_tmp   = fast_data[var_name].values
        
        try:
            var_fast = netcdf_lev1_fast.createVariable(var_name, var_dtype, 'time', zlib=True)
            var_fast[:] = var_tmp # compress fast data via zlib=True

        except Exception as e:
            print("!!! something wrong with variable {} -- {} on date {} !!!".format(var_name, curr_station, date))
            print(fast_data[var_name])
            print("!!! {} !!!".format(e))
            continue

        for att_name, att_desc in var_atts.items(): # write atts to the var now
            netcdf_lev1_fast[var_name].setncattr(att_name, att_desc)

        # add a percent_missing attribute to give a first look at "data quality"
        perc_miss = fl.perc_missing(var_fast)
        netcdf_lev1_fast[var_name].setncattr('percent_missing', perc_miss)
        netcdf_lev1_fast[var_name].setncattr('missing_value'  , fill_val)

    netcdf_lev1_slow.close() # close and write files for today
    netcdf_lev1_fast.close() 
    if fast_data.empty:
        print(f"... no fast data for today but there was slow?? {curr_station } -- {tm}")
        os.remove(lev1_fast_name)
    return True

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
