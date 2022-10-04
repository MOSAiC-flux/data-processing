#!/usr/bin/env python3
# -*- coding: utf-8 -*-   
from tower_data_definitions import code_version
code_version = code_version()

# ######################################################################################################
# AUTHORS:
#
#   Michael Gallagher (CIRES/NOAA)  michael.r.gallagher@noaa.gov
#
# PURPOSE:
#
#
#
# HOWTO:
#
#
# RELEASE-NOTES:
#
# Please look at CHANGELOG-tower.md for notes on changes/improvements with each version.
#
# ######################################################################################################

# import our code modules
from tower_data_definitions import define_global_atts as define_global_atts_tower 
from tower_data_definitions import define_turb_variables as define_turb_variables_tower 

from asfs_data_definitions import define_global_atts as define_global_atts_asfs 
from asfs_data_definitions import define_turb_variables as define_turb_variables_asfs 

from get_data_functions     import get_flux_data

import functions_library as fl # includes a bunch of helper functions that we wrote

import os, inspect, argparse, time, gc
import socket 

global nthreads 
if '.psd.' in socket.gethostname():
    nthreads = 32  # the twins have 64 cores, it won't hurt if we use <20
else: nthreads = 8  # laptops don't tend to have 64 cores

from multiprocessing import Pool as pool
from multiprocessing import Process as P
from multiprocessing import Queue   as Q

# need to debug something? kills multithreading to step through function calls
we_want_to_debug = False
if we_want_to_debug:
    from multiprocessing.dummy import Process as P
    from multiprocessing.dummy import Queue   as Q
    nthreads = 1
    from debug_functions import drop_me as dm
 
import numpy  as np
import pandas as pd
import xarray as xr

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from datetime  import datetime, timedelta
from numpy     import sqrt
from netCDF4   import Dataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

# just in case... avoids some netcdf nonsense involving the default file locking across mounts
os.environ['HDF5_USE_FILE_LOCKING']='FALSE' # just in case
os.environ['HDF5_MPI_OPT_TYPES']='TRUE'     # just in case

version_msg = '\n\nPS-122 MOSAiC Met "FLUX" processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

# argparse is defined at bottom in __main__ and this function takes those as arguments
# which makes debugging at the REPL via "import main" much easier
def main(station_name, start_time=datetime(2019,10,1), end_time=datetime(2020,10,1),
         data_dir='/Projects/MOSAiC/', verbose=True, pickle_dir=None):

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring
    def printline(startline='',endline=''):
        print('{}--------------------------------------------------------------------------------------------{}'
              .format(startline, endline))
    v_print      = print if verbose else lambda *a, **k: None
    verboseprint = v_print

    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0

    print('The first day we process data is:      %s' % str(start_time))
    print('The last day we will process data is:  %s' % str(end_time))
    printline()

    ds, code_version = get_flux_data(station_name, start_time, end_time, 2, data_dir, 'seb', True, 60, True, './')
 
    # a wrapper that does some accounting for filling in nans, etc, gets called below
    def fill_var_nans(ds, var_name, qc_var):
        notnan_count_before = ds[var_name].notnull().sum().values # some accounting of what has been pulled out
        ds[var_name][ds[qc_var]!=0] = np.nan
        ndropped = notnan_count_before - ds[var_name].notnull().sum().values
        drop_dict = { 'name': var,
                      'tot_dropped': ndropped,
                      'percent_dropped': np.round((ndropped/len(ds[var_name]))*100,2)
                     }
        return drop_dict, ds

    # the do-er part of it all, loop over the variables and fill in all
    # the data with nans for each variable as mapped to the variables respective qc var  

    if station_name == 'tower':
        turb_vars_allheights = ['Hs',]
        turb_vars_10m        = ['Hl', 'bulk_Hs_10m', 'bulk_Hl_10m']
        turb_vars_to_keep    = ['Hs', 'Hl', 'bulk_Hs_10m', 'bulk_Hl_10m']

    else:
        turb_vars_allheights = []
        turb_vars_10m        = ['Hl', 'bulk_Hs', 'bulk_Hl']
        turb_vars_to_keep = ['Hs', 'Hl', 'bulk_Hs', 'bulk_Hl']

    dropped_df           = pd.DataFrame()
    qc_vars = [] # keep track and drop
    for var in ds.variables:

        if '_qc' in var: 
            qc_var = var
            qc_vars.append(qc_var)
            var_name = qc_var.rstrip('_qc')
            if var_name!=qc_var: # the rstrip actually worked, *_qc are 1:1 mappings
                try: 
                    dd, ds = fill_var_nans(ds, var_name, qc_var)
                    dropped_df = dropped_df.append(dd, ignore_index=True)

                except Exception as e: 
                    print(e)
                    print(var_name)

            else: 

                if 'turbulence_qc' in qc_var:
                    height = qc_var.split('_')[-1]
                    for tv in turb_vars_allheights: 
                        try:
                            dd, ds = fill_var_nans(ds, tv+f"_{height}", qc_var)
                            dropped_df = dropped_df.append(dd, ignore_index=True)

                        except Exception as e: 
                            print(e)
                            print("-----")
                if qc_var == 'turbulence_qc_10m':
                    for v in turb_vars_10m: 
                        dd, ds = fill_var_nans(ds, v, qc_var)
                        dropped_df = dropped_df.append(dd, ignore_index=True)
                        
    dropped_df.index = dropped_df['name']
    dropped_df       = dropped_df.drop('name', axis=1)
    dropped_df       = dropped_df.sort_values(by=['percent_dropped'], ascending=False)

    printline()
    print('The most dropped variables by percentage for')
    print(f'    {start_time} -----> {end_time}\n')
    print(dropped_df.iloc[0:20])

    # this call to global/turb atts is hacky
    if station_name!='tower': short_name = 'asfs'
    else: short_name = 'tower'

    vars_to_drop = []
    for v in eval(f'define_turb_variables_{short_name}()')[1]: 
        if not any(tv in v for tv in turb_vars_to_keep): vars_to_drop.append(v)
    
    # drop qc, turbulence, and other listed variables
    vars_to_drop.extend(qc_vars)
    ds = ds.drop_vars(vars_to_drop)

    # set new global atts 
    if station_name == 'tower': global_args = f'file_type="level3"'
    else: global_args = f'station_name="{station_name}", file_type="level3"'
    for att in ds.copy().attrs: del ds.attrs[att] # copy cause loop, delete old global atts
    for att, val in eval(f'define_global_atts_{short_name}({global_args})').items():
        ds.attrs[att] = val
    data_provenance = "Based on data from the mosseb.level2 datastream with : https://doi.org/XXXXXXXXXX"

    #ds = ds.convert_calendar("standard", use_cftime=True) # move to standard calendar
    time_vars = ['time', 'base_time', 'time_offset']
    for timev in time_vars:
        ds[timev].convert_calendar("standard", use_cftime=True) # move to standard calendar

    encoding = {}
    for v in ds.variables:
        if 'time' not in v: ds[v].attrs['data_provenance'] = data_provenance
        if 'time' in v: fillval = None
        else: fillval = def_fill_int
        encoding[v] = {'zlib': True, "complevel": 9, '_FillValue': fillval}

    printline('\n', '\n')
    print(f"Writing out level3 files by splitting up days, threaded with {nthreads} threads...")

    level3_dir = f'{data_dir}/{station_name}/3_level_archive/'
    os.makedirs(level3_dir, exist_ok=True)

    days_to_write = pd.date_range(start_time, end_time, freq='D')   # all the minutes today, for obs
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    write_arg_list = []

    if station_name == 'tower': fun_name = 'metcity'
    else: fun_name = station_name

    for today in days_to_write:
        tomorrow = today+day_delta
        write_arg_list.append((fun_name, ds.sel(time=slice(today,tomorrow)), level3_dir, encoding, today))

    print("\n    ... now actually calling write out\n")
    printline()
    call_function_threaded(write_level3, write_arg_list)

    return ds, dropped_df, vars_to_drop, write_arg_list

# this takes advantage of the xarray netcdf write function, since
# we're just leaving most attributes the same from the level2 files
def write_level3(station_name, ds, data_dir, encoding, data_date):

    file_name = f'{data_dir}/{station_name}.level3.4.10min.{data_date.strftime("%Y%m%d.%H%M%S")}.nc'
    if data_date.day==1: print(f"... processing day {data_date}\n... {file_name}")

    dti = pd.DatetimeIndex(ds['time'].values)

    # this is stolen from the level2 stuff, xarray is doing weird things to the attributes/encoding of these
    # vars so we'll just write them over from scratch
    epoch_time = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers
    et         = np.datetime64(epoch_time)
    bot        = np.datetime64(data_date)
    tm         = np.datetime64(data_date)

    base_atts = {'string'     : '{}'.format(bot),
                 'long_name' : 'Base time in Epoch',
                 'units'     : 'seconds since {}'.format(et),
                 'ancillary_variables'  : 'time_offset',}

    delt_str = f"0000-00-00 00:10:00"

    # here we create the array and attributes for 'time'
    t_atts   = {'units'     : 'seconds since {}'.format(tm),
                'delta_t'   : delt_str,
                'long_name' : 'Time offset from midnight',
                'calendar'  : 'standard',}


    to_atts   = {'units'     : 'seconds since {}'.format(bot),
                 'delta_t'   : delt_str,
                 'long_name' : 'Time offset from base_time',
                 'ancillary_variables'  : 'base_time',
                 'calendar'  : 'standard',}

    to_delta_ints = np.floor((dti - bot).total_seconds())      # seconds
    to_ind = pd.Int64Index(to_delta_ints)

    delta_ints = np.floor((dti - tm).total_seconds())      # seconds
    t_ind = pd.Int64Index(delta_ints)

    ds = ds.drop(['base_time', 'time', 'time_offset'])
    ds['base_time'] = np.int32((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])
    ds['time'] = np.int32(t_ind.values)
    ds['time_offset'] = np.int32(to_ind.values)

    # this is annoying
    for att_name, att_val in base_atts.items(): 
        ds['base_time'].encoding[att_name] = att_val
        ds['base_time'].attrs[att_name] = att_val

    for att_name, att_val in t_atts.items():
        ds['time'].encoding[att_name] = att_val
        ds['time'].attrs[att_name] = att_val

    for att_name, att_val in to_atts.items():
        ds['time_offset'].encoding[att_name] = att_val
        ds['time_offset'].attrs[att_name] = att_val
    
    for v in ds.variables:
        if 'time' not in v:
            ds[v].attrs['percent_missing'] = np.round(((len(ds[v])-ds[v].notnull().sum().values)/len(ds[v]))*100, 2)

    ds.to_netcdf(file_name, 'w', encoding=encoding) # besides the time enoding, this being one line is convenient

def call_function_threaded(func, arg_list, timeout=None):
    with pool(processes=nthreads) as p:
        p.starmap(func, arg_list)

    # this was a custom function that allows for interrupts (.gets) and printing and other fun things
    # but it's pretty unnecessary for most use cases
    # q_list = []
    # p_list = []
    # ret_list = [] 
    # for i_call, arg_tuple in enumerate(arg_list):
    #     q = Q(); q_list.append(q)
    #     p = P(target=func, args=arg_tuple+(q,))
    #     p_list.append(p); p.start()
    #     if (i_call+1) % nthreads == 0 or arg_tuple is arg_list[-1]:
    #         for iq, fq in enumerate(q_list):
    #             rval = fq.get()
    #             p_list[iq].join(timeout=1.0)
    #             ret_list.append(rval)
    #         q_list = []
    #         p_list = []

    # return ret_list


# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over OPall the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')

    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')
    
    # pass the base path to make it more mobile
    parser.add_argument('-p', '--path', metavar='str', help='full path to data, including /data/ andtrailing slash')
    parser.add_argument('-pd', '--pickledir', metavar='str',help='want to store a pickle of the data for debugging?')

    parser.add_argument('-a', '--station', metavar='str',help='asfs#0/tower, if omitted all will be procesed')

    args         = parser.parse_args()
    if args.verbose: verbose = True
    else: verbose = False
    
    # paths
    global data_dir 

    if args.path: data_dir = args.path
    else: data_dir = '/Projects/MOSAiC/'

    if args.pickledir: pickle_dir=args.pickledir
    else: pickle_dir=False

    if args.station: station_list = list(args.station.split(','))
    else: station_list = ['asfs30', 'asfs40', 'asfs50', 'tower']
    
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y%m%d')
    else:
        start_time = datetime(2019,10,1)

    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y%m%d')
    else:
        end_time = datetime(2020,10,1)

    for station_name in station_list:
        main(station_name, start_time, end_time, data_dir, verbose, pickle_dir)
    
