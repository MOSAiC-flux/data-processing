#!/usr/bin/python3
# ############################################################################################
# AUTHOR: Michael Gallagher (CIRES/NOAA)
# EMAIL:  michael.r.gallagher@noaa.gov
# 
# PURPOSE:
#
# A quick example on pulling in ATMOS flux team data for analysis
# 
# ############################################################################################
from   datetime import datetime, timedelta
import os, inspect, argparse

import numpy  as np
import pandas as pd
import xarray as xr
import netCDF4 

station = 'asfs30'
site = 'L2'
data_dir = './processed_data/level2/{}/'.format(station) # point this program to your data
head_str = 'level2_preliminary_1min_{}.{}.'.format(station,site)        # plot 10min data
tail_str = '.nc'           # leading data file string 

parser = argparse.ArgumentParser()                                
parser.add_argument('-s', '--start_time', metavar='str',   help='beginning of processing period, Ymd syntax')
parser.add_argument('-e', '--end_time',   metavar='str',   help='end  of processing period, Ymd syntax')

# start at first day of available data if a start isn't provided, end at the end of leg 2
args         = parser.parse_args()                                        
start_time = datetime(2020,2,28,0,0) # the first day of MOSAiC tower data
#start_time = datetime(2019,10,15,0,0) # the first day of MOSAiC tower data

if args.start_time:
    start_time = datetime.strptime(args.start_time, '%Y%m%d') 

if args.end_time:
    end_time = datetime.strptime(args.end_time, '%Y%m%d')   
else: 
    end_time = datetime(2020,3,1,0,0) # end of leg 2 

print('---------------------------------------------------------------------------------------')
print('')
print('Looking at data days between {} -----> {}'.format(start_time,end_time))
print('')
print('---------------------------------------------------------------------------------------')

# ###############################################################################################
# pull in the data from every daily file in the time range asked for and concatenate it into 
# a single data frame. this means you can look at data across the full range without array syntax
# ###############################################################################################
print(' ... pulling in data from the following files:')
day_series = pd.date_range(start_time, end_time) # we're going to get data for these days between start->end
file_list  = [] 
for today in day_series: # loop over the days in the processing range and get a list of files
    date_str  = today.strftime('%Y%m%d') # get date string for file name
    curr_file = data_dir+head_str+'{}'.format(date_str)+tail_str # name of file from today
    if os.path.isfile(curr_file): 
        file_list.append(curr_file) 
    else:
        print(' !!! file {} not found !!!'.format(curr_file))
        continue
#for name in file_list: print('    {}'.format(name)); print('') # uncomment to see every file used

# do it the hard way??
manual_labor_is_my_style = False

if manual_labor_is_my_style:
    # open the entire list of data files from these days as one netcdf dataset
    dataset = netCDF4.MFDataset(files=file_list, aggdim='time') 

    # now put that dataset into a dataframe because dataframes are so much more useful, use timestamps as index
    print(' ... making dataframe')
    time_data     = dataset.variables['time']
    time_to_dates = netCDF4.num2date(time_data[:], time_data.units, \
                                     only_use_cftime_datetimes=False,only_use_python_datetimes=True)
    # only_use declarations might only be required/available in the newest netcdf version...??

    df = pd.DataFrame(index=time_to_dates) # put netcdf dataset into a pandas dataframe to be easily plotted

    # loop over all variables
    for var in dataset.variables.keys():
        values = dataset.variables[var][:]
        df[var] = values

        try: fill_val = np.float(values.ncattrs()['fill_value'])
        except: print("no fill value for {}".format(var))

    df['time'] = time_to_dates # duplicates index... but it can be convenient
    df = df.sort_index()       # or (inplace=True)

    # there it is! you can make plots, compare, etc etc etc
    print('\n---------------------------------------------------------------------------------------\n')
    print('netcdf file attributes:')
    for name in dataset.ncattrs():
        print("{} = {}".format(name, getattr(dataset, name)))

else: # or let someone else write the code for me.
    xarr_ds = xr.open_mfdataset(file_list)
    df = xarr_ds.to_dataframe() # pandas dataframes are really useful

print('\n---------------------------------------------------------------------------------------\n')
print('dataframe header and footer:')
print(df.info(verbose=True))
print('\n---------------------------------------------------------------------------------------\n')
print(df['radiation_SWu'])
print(df['radiation_net'])
    


