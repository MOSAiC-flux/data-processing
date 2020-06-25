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
# python3 create_level1_product_asfs.py -v -s 20191005 -e 20201005
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
from asfs_data_definitions import define_global_atts
from asfs_data_definitions import define_level1_slow, define_level1_fast

import functions_library as fl

import os, inspect, argparse, time, gc 
import numpy  as np
import pandas as pd


from threading import Thread
from queue     import Queue
from datetime  import datetime, timedelta
from numpy     import sqrt
from netCDF4   import Dataset, MFDataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

version_msg = '\n\nPS-122 MOSAiC Flux team ASFS processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)

def main(): # the main data crunching program

    global trial, n_trial_files
    trial = True # FOR TESTING PURPOSES ONLY, takes random xxx files and cuts to save debugging time
    n_trial_files = 1500

    # the date on which the first MOSAiC data was taken... there will be a "seconds_since" variable 
    global beginning_of_time
    beginning_of_time    = datetime(2019,10,5,0,0) # the first day of MOSAiC ASFS data

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring
    global verbose       # a useable flag to allow subroutines etc when using -v 

    global data_dir, level1_dir
    data_dir  = './data/'
    level1_dir = './processed_data/level1/'  # where does level1 data go

    flux_stations = ['asfs30', 'asfs40', 'asfs50'] # our beauties
    apogee_switch_date = {}
    apogee_switch_date[flux_stations[0]] = datetime(2019,12,13,11,9,0) # 
    apogee_switch_date[flux_stations[1]] = datetime(2019,12,13,11,9,0) # 
    apogee_switch_date[flux_stations[2]] = datetime(2019,11,14,6,11,0) # 

    
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
    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    args         = parser.parse_args()
    verbose      = True if args.verbose else False # use this to run segments of code via v/verbose flag
    v_print      = print if verbose else lambda *a, **k: None     # placeholder
    verboseprint = v_print # use this function to print a line if the -v/--verbose flag is provided

    def printline(startline='',endline=''): # make for pretty printing
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
    print("   and doing it in threads, hopefully this doesn't burn your lap")
    printline()

    # get the "slow" raw data first, heavy lifting is in "get_slow_data()" the slow
    # dataset is "small", so we load it all at once
    # #####################################################################################
    # dataframes go in dicts with station keys, we parallellize data ingesting to save time.
    slow_data   = {}
    slow_q_dict = {}
    slow_atts, slow_vars = define_level1_slow()
    for curr_station in flux_stations:
        # try to save some time and multithread the reading
        slow_q_dict[curr_station] = Queue()
        # run the threads for retreiving data
        Thread(target=get_slow_data, \
               args=(curr_station, start_time, end_time, \
                     slow_q_dict[curr_station])).start()

    # wait to finish slow first, then get results from thread queue
    for curr_station in  flux_stations:
        slow_data[curr_station] = slow_q_dict[curr_station].get()

        verboseprint("\n===================================================")
        verboseprint("Data and observations provided by {}:".format(curr_station))
        verboseprint('===================================================')
        if verbose: slow_data[curr_station].info(verbose=True) # must be contained;

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

    # there's a whole history (now) behind why the fast code looks like this
    # but...  there's too much fast data, we need to read in and write out each
    # day individually if coded like slow above, station "fast" datasets take
    # 32Gb of RAM (I only have 40Gb) and that's only for legs 1 and 2
    # #########################################################################
    fast_atts, fast_cols = define_level1_fast()
    fast_file_list       = {} # a list of fast data files for each station and the
    first_timestamp_list = {} # corresponding first file timestamp, sorted in time
    fast_file_q = {}
    for curr_station in flux_stations: # get station file lists in parallel
        fast_file_q[curr_station] = Queue()
        Thread(target=get_fast_file_list, \
               args=(curr_station, fast_file_q[curr_station])).start()

    for curr_station in flux_stations: # wait for threads and get return values
        first_timestamp_list[curr_station] = fast_file_q[curr_station].get()
        fast_file_list[curr_station]       = fast_file_q[curr_station].get()

    # we have to actually import the fast data on a daily basis for each station, so this
    # is all done in a loop for each day, and then level1 QC/writing for both slow/fast
    # data is done in that loop.... very annoying but seems the best solution
    # ##############################################################################################
    day_series = pd.date_range(start_time, end_time)    # data was requested for these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00

    printline()
    print("\n Got all slow data and have a list of fast files, now processing each day...\n")
    printline()

    i_day = -1 
    for today in day_series: # loop over the days in the processing range and get a list of files
        gc.collect()
        i_day+=1
        tomorrow = today+day_delta

        # dictionary of data frames for todays data
        fast_data_today = {}
        slow_data_today = {} 

        # get slow data for today only from full data frame retreived above
        for curr_station in flux_stations:
            slow_data_today[curr_station] = slow_data[curr_station][today:tomorrow]

        # queue used to retreive data for today
        fast_q_dict = {} 
        if i_day % 1 == 0: print("\nCurrently processing level1 data for {}".format(today))

        for curr_station in flux_stations:
            # try to save some time and multithread the reading
            fast_q_dict[curr_station] = Queue()
            # run the threads for retreiving data
            Thread(target=get_fast_data, \
                   args=(today, fast_file_list[curr_station], first_timestamp_list[curr_station], curr_station, \
                         fast_q_dict[curr_station])).start()

        # wait for results from threads and then put dataframes into list
        for curr_station in flux_stations:
            fast_data_today[curr_station] = fast_q_dict[curr_station].get()

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

        for curr_station in flux_stations:
            #if not slow_data_today[curr_station].empty:

            if today == apogee_switch_date[curr_station].replace(hour=0, minute=0, second=0):
                targ_T = slow_data_today[curr_station]['apogee_targ_T_Avg'].copy()
                body_T = slow_data_today[curr_station]['apogee_body_T_Avg'].copy()
                targ_T_std = slow_data_today[curr_station]['apogee_targ_T_Std'].copy()
                body_T_std = slow_data_today[curr_station]['apogee_body_T_Std'].copy()

                slow_data_today[curr_station]['apogee_targ_T_Avg'] = \
                    np.where(slow_data_today[curr_station].index < apogee_switch_date[curr_station],\
                             body_T,\
                             targ_T)
                slow_data_today[curr_station]['apogee_body_T_Avg'] = \
                    np.where(slow_data_today[curr_station].index < apogee_switch_date[curr_station],\
                             targ_T,\
                             body_T)

                slow_data_today[curr_station]['apogee_targ_T_Std'] = \
                    np.where(slow_data_today[curr_station].index < apogee_switch_date[curr_station],\
                             body_T_std,\
                             targ_T_std)
                slow_data_today[curr_station]['apogee_body_T_Std'] = \
                    np.where(slow_data_today[curr_station].index < apogee_switch_date[curr_station],\
                             targ_T_std,\
                             body_T_std)

            elif today < apogee_switch_date[curr_station]:
                cs_targ_avg = slow_data_today[curr_station]['apogee_targ_T_Avg'] 
                cs_body_avg = slow_data_today[curr_station]['apogee_body_T_Avg'] 
                slow_data_today[curr_station]['apogee_targ_T_Avg'] = cs_body_avg
                slow_data_today[curr_station]['apogee_body_T_Avg'] = cs_targ_avg

                cs_targ_std = slow_data_today[curr_station]['apogee_targ_T_Std'] 
                cs_body_std = slow_data_today[curr_station]['apogee_body_T_Std'] 
                slow_data_today[curr_station]['apogee_targ_T_Std'] = cs_body_std
                slow_data_today[curr_station]['apogee_body_T_Std'] = cs_targ_std

        # #############################################################################
        # level1 qc/processing done write out level1 raw/'ingest' files to netcdf today
        # ############################################################################# 
        write_q_dict     = {} # queue used to retreive data for today
        today_empty_dict = {} # boolean keeper of if there was no data today
        for curr_station in flux_stations:
            write_q_dict[curr_station] = Queue()

            sdt   = slow_data_today[curr_station]
            fdt   = fast_data_today[curr_station]
            satts = slow_atts
            fatts = fast_atts

            if not sdt.empty or not fdt.empty: 
                # run the threads for retreiving data
                Thread(target=write_level1_netcdfs, \
                       args=(sdt, satts, fdt, fatts, curr_station, today,\
                             write_q_dict[curr_station])).start()
                today_empty_dict[curr_station] = False
            else:
                today_empty_dict[curr_station] = True
                print("... no data available for {} on {}".format(curr_station, today))

        # apparently writes upsing netcdf/hdf5 aren't thread safe... if you don't wait for the thread to
        # finish before calling write again, you'll get weird and random crashes. otherwise the code runs
        # fine. thus, this loop is commented out and we wait for each write before starting another

        #for curr_station in flux_stations: # wait for write threads to finish before moving on
            if not today_empty_dict[curr_station]:
                write_q_dict[curr_station].get()

        continue

    printline()
    print('All done! Netcdf output files can be found in: {}'.format(level1_dir))
    printline()
    print(version_msg)
    printline()

# pulls in logger text files from sdcard data and returns a dataframe and a list of data attributes (units, etc)
# q returns the results from a threaded call and is of Queue class
def get_slow_data(station, start_time, end_time, q): 
    searchdir = data_dir+station

    # look through station subdirectories and only take data file if it's an "SDcard" folder... 
    # returns file path list for all files in all sd card data dirs for this station, i.e. a list of every data file
    card_file_list = get_card_file_list('slow', searchdir) 
    print('... found {} slow files in directory {}'.format(len(card_file_list), searchdir))

    frame_list = [] # list of frames from files... to be concatted after loop
    data_atts, data_cols  = define_level1_slow()

    # 'cause campbell is.... inconsistent
    na_vals         = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"','']

    licor_columns   = [] # list that will remember the names of licor columns to fill them with nans after pulling in data
    file_i          = -1
    for data_file in card_file_list:
        file_i += 1
        if file_i % 500 == 0 and file_i != 0:  
            verboseprint("... at file {} of {} for slow data in {} ".format(file_i, len(card_file_list), searchdir))

        cols  = list(data_atts.keys()).copy() # stupid python 'pointers'...

        # count the columns in the first line, if less than 89, delete the 8 licor indexes
        with open(data_file) as f: num_cols = len(f.readline().rsplit(','))
        if  num_cols == 89: # should be the majority of data files, licor was off, remove licor columns
            licor_indexes = [int(i) for i, word in enumerate(cols) if word.rfind('licor') >= 0 ]
            for i in licor_indexes:
                licor_columns.append(cols[i])
                del cols[i]

        frame = pd.read_csv(data_file, parse_dates=[0], sep=',', na_values=na_vals,\
                            index_col=0, engine='c', names=cols)

        frame_list.append(frame) 

        if trial and file_i > n_trial_files: # running tests
            break

    data_frame = pd.concat(frame_list) # is concat computationally efficient?

    # done gathering data, now narrow down to requested window
    data_frame = data_frame.sort_index()[start_time:end_time]

    # some sanity checks
    n_dupes = ~data_frame.duplicated().size
    if data_frame.empty: # 'fatal' is a print function defined at the bottom of this script that exits
        fl.fatal("No {} data for requested time range {} ---> {} ?\n I'm sorry, I have to die".format(searchdir,start_time,end_time))
    if n_dupes > 0 : fl.fatal("... there were {} duplicates for {} in this time range!!\n you got duped, dying".format(n_dupes, searchdir))

    # now, reindex for every second in range and fill with nans so that the we commplete record
    mins_range = pd.date_range(start_time, end_time, freq='T') # all the minutes today, for obs
    try:
        data_frame = data_frame.reindex(labels=mins_range, copy=False)
    except Exception as e:
        printline()
        print("There was an exception reindexing for {}".format(searchdir))
        print(' ---> {}'.format(e))
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
    
    # add licor columns with nans so that all files have the same variables:
    for i,var in enumerate(licor_columns):
        data_frame[var] = nan

    # sort data by time index and return data_frame to queue
    q.put(data_frame)

# finds all files for station, returning a list of the timestamps from
# the first lines of each file and a sorted list of filenames
def get_fast_file_list(station, q):

    # look through station subdirectories and only take data file if it's an "SDcard" folder... 
    # returns list of every data file path in sdcard subdirs
    searchdir          = data_dir+station
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

    q.put(sorted_timestamps.tolist())
    q.put(sorted_file_list.tolist())

# gets data for the 20hz metek sonics, complicated because of nuances grabbing fast data
# via logger this function pulls files into dataframe, sorted based on time of first
# entry in file, then interpolates the timestamps so that each fast obs gets a
# unique/approximate timestamp...
# finally it returns the day of data requested with  the new interpolated timestamps
# ########################################################################################
# sorry Chris, I hope this function isn't too incomprehensible/ugly. and if it is, then I
# hope it just_works(tm) and you don't have to touch it.
def get_fast_data(date, fast_file_list, first_timestamp_list, curr_station, q): 

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
        q.put(pd.DataFrame(columns=data_cols))
        return

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

    return_frame = full_frame[date:date+day_delta]
    n_entries    = return_frame.index.size

    verboseprint("... {}/1728000 fast entries on {} for {}, representing {}% data coverage"
                 .format(n_entries, date, curr_station, round((n_entries/1728000)*100.,2)))
    q.put(return_frame)

# function that searches sitevisit dirs looking for SDcard directory and returns data file paths in a list
def get_card_file_list(filestr, searchdir): # filestr is the name in the data file you want to get slow/fast/etc
    card_file_list = [] 
    for subdir, dirs, files in os.walk(searchdir):
        for curr_dir in dirs:
            #if curr_dir.lower() == "20191010_setupcollection/sdcard/": continue
            if "sdcard" in curr_dir.lower(): # nobody ever types the same way twice...
                card_dir = subdir+'/'+curr_dir
                card_files_in_dir = []
                for f in os.listdir(card_dir):
                    if filestr in f and f.endswith('.dat'):
                        card_files_in_dir.append(card_dir+'/'+f)
                card_file_list.extend(card_files_in_dir) # lets not make a list of lists
    return card_file_list

# do the stuff to write out the level1 files, after finishing this it could probably just be one
# function that is called separately for fast and slow... : \
def write_level1_netcdfs(slow_data, slow_atts, fast_data, fast_atts, curr_station, date, q):
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
        q.put(False)
        return 

    print("... writing level1 for {} on {}, ~{}% of slow data is present".format(curr_station, date, 100-avg_missing_slow))

    out_dir       = level1_dir+curr_station+"/"
    file_str_fast = '/fast_preliminary_{}.{}.{}.nc'.format(curr_station,
                                                          l_site_names[curr_station],
                                                          date.strftime('%Y%m%d'))
    file_str_slow = '/slow_preliminary_{}.{}.{}.nc'.format(curr_station,
                                                          l_site_names[curr_station],
                                                          date.strftime('%Y%m%d'))

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

    time_atts_slow   = {'units'     : 'seconds since {}'.format(beginning_of_time),
                        'delta_t'   : '0000-00-00 00:01:00',
                        'long_name' : 'seconds since the first day of MOSAiC',
                        'calendar'  : 'standard',}

    time_atts_fast = time_atts_slow.copy()
    time_atts_fast['units']     = 'milliseconds since {}'.format(beginning_of_time)
    time_atts_fast['long_name'] = 'milliseconds since the first day of MOSAiC'

    bot = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files

    # create the arrays that are integer intervals from  'time since beginning of mosaic' for indexing netcdf files
    bot = np.datetime64(beginning_of_time)
    slow_dti = pd.DatetimeIndex(slow_data.index.values)
    fast_dti = pd.DatetimeIndex(fast_data.index.values)

    slow_delta_ints = np.floor((slow_dti - bot).total_seconds())      # seconds
    fast_delta_ints = np.floor((fast_dti - bot).total_seconds()*1000) # ms 

    t_slow_ind = pd.Int64Index(slow_delta_ints)
    t_fast_ind = pd.Int64Index(fast_delta_ints)

    # set the time dimension and variable attributes to what's defined above
    # ###########################################################################
    # 
    # this is where netcdf/hdf crash with a runtime exception sometimes, and I
    # can't figure out why. it never happens reliably (never at same point in the
    # data) I assume it's a bug in netcdf/hdf5. so why not catch the exception and
    # then try again until it works, lol. saves crashing and restarting
    # this only works for python versions built with debug symbols, fyi. if you
    # have a python version without, it just segfaults... weird things

    t_slow = netcdf_lev1_slow.createVariable('time', 'i8','time') # seconds since
    t_fast = netcdf_lev1_fast.createVariable('time', 'i8','time') # seconds since

    while True:
        try:
            t_slow[:] = t_slow_ind.values
            break # if no exception, continue as normal
        except RuntimeError as re:
            print("!!! there was an error creating slow time variable with netcdf/hd5 I cant debug !!!")
            print("!!! {} !!!".format(re))
            print("!!! sorry, trying again, it's not our fault I swear !!!")
    while True:
        try:
            t_fast[:] = t_fast_ind.values
            break # if no exception, continue as normal
        except RuntimeError as re:
            print("!!! there was an error creating fast time variable with netcdf/hd5 I cant debug !!!")
            print("!!! {} !!!".format(re))
            print("!!! sorry, trying again, it's not our fault I swear !!!")

    for att_name, att_val in time_atts_slow.items(): netcdf_lev1_slow['time'].setncattr(att_name,att_val)
    for att_name, att_val in time_atts_fast.items(): netcdf_lev1_fast['time'].setncattr(att_name,att_val)

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

    gc.collect() # maybe this helps with the random (rare) memory access crashes in the netcdf/hdf5 libs?
    netcdf_lev1_slow.close() # close and write files for today
    netcdf_lev1_fast.close() 
    if fast_data.empty:
        print("... no fast data... deleting file")
        os.remove(lev1_fast_name)
    q.put(True)


# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
