#!/usr/bin/env python3
# -*- coding: utf-8 -*-  
# ############################################################################################
# AUTHOR: Michael Gallagher (CIRES/NOAA)
# EMAIL:  michael.r.gallagher@noaa.gov
# 
# This script takes in the 'slow' level1 data and makes plots of a suite of variables. Each
# plot is given a general name (e.g. meteorology) and then an associated dictionary controls
# the number of subplots and the variables that go on each subplot. 
#
# The plotting is done in a configurable number of threadsparallel
#
# ./plot_asfs_tower_quicklooks.py -v -s 20191005 -e 20201002 
#
#
# DATES:
#   v1.0: 2020-11-13
# 
# ############################################################################################
from datetime  import datetime, timedelta

from multiprocessing import Process as P
from multiprocessing import Queue   as Q

import os, inspect, argparse, sys, socket
import matplotlib        as mpl
import matplotlib.pyplot as plt
import colorsys

if '.psd.' in socket.gethostname():
    nthreads = 20 # the twins have 64 cores, it won't hurt if we use ~30
else: nthreads = 4 # if nthreads < nplots then plotting will not be threaded

# this is here because for some reason the default matplotlib doesn't
# like running headless...  off with its head
mpl.interactive(False)
#mpl.use('pdf');
plt.switch_backend('svg') 

plt.ioff() # turn off pyplot interactive mode 
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'  # just in case
os.environ['HDF5_MPI_OPT_TYPES']='TRUE'  # just in case

import numpy  as np
import pandas as pd
import xarray as xr

sys.path.insert(0,'../')

import functions_library as fl 
from get_data_functions import get_tower_l1_data

#import warnings
mpl.warnings.filterwarnings("ignore", category=mpl.MatplotlibDeprecationWarning)
mpl.warnings.filterwarnings("ignore", category=UserWarning) 

def main(): # the main data crunching program

    default_data_dir = '/psd3data/arctic/MOSAiC/' # give '-p your_directory' to the script if you don't like this

    threaded_data    = True; nthreads = 16
    make_daily_plots = True
    make_leg_plots   = True # make plots that include data from each leg

    leg1_start = datetime(2019,10,5)
    leg2_start = datetime(2019,12,15) 
    leg3_start = datetime(2020,3,2)
    leg4_start = datetime(2020,6,1)
    leg5_start = datetime(2020,8,15)
    mosaic_end = datetime(2020,10,2)
    leg_list   = [leg1_start,leg2_start,leg3_start,leg4_start,leg5_start,mosaic_end]

    global code_version # code_version is the *production* code and is pulled in from nc files later

    # what are we plotting? dict key is the full plot name, value is another dict...
    # ... of subplot titles and the variables to put on each subplot
    var_dict = {} # code below plots strings with vaisala_T/RH in the name at 3 heights
    var_dict['meteorology']     = {'temperature'      : ['vaisala_T','mast_T','apogee_targ_T'], 
                                   'humidity'         : ['vaisala_RH', 'mast_RH'],
                                   'pressure'         : ['vaisala_P_2m', 'mast_P'],
                                   }
    var_dict['plates_and_sr50'] = {'flux_plates'      : ['fp_A_Wm2','fp_B_Wm2'],
                                   'surface_distance' : ['sr50_dist'],
                                   }
    var_dict['is_alive']        = {'logger_temp'      : ['PTemp'],
                                   'logger_voltage'   : ['batt_volt'],
                                   'gps'              : ['gps_hdop'],
                                   }
    var_dict['lat_lon']         = {'minutes'         : ['gps_lat_min','gps_lon_min'],
                                   'degrees'         : ['gps_lon_deg','gps_lat_deg'],
                                   }

    unit_dict = {}
    unit_dict['meteorology']     = {'temperature'      : 'C',
                                    'humidity'         : '%', 
                                    'pressure'         : 'hPa', 
                                    }
    unit_dict['plates_and_sr50'] = {'flux_plates'      : 'W/m2', 
                                    'surface_distance' : 'm', 
                                    }
    unit_dict['is_alive']        = {'logger_temp'      : 'C', 
                                    'logger_voltage'   : 'V',
                                    'gps'              : 'none', 
                                    }
    unit_dict['lat_lon']        = {'minutes'           : 'minutes',
                                   'degrees'           : 'degrees',
                                   }


    # if you put a color in the list, (rgb or hex) the function below will all lines different luminosities
    # of the same hue. if you put a 3-tuple of colors, it will use the colors provided explicitly for 30/40/50
    color_dict = {}
    color_dict['meteorology']     = ['#E24A33','#348ABD','#988ED5','#777777','#FBC15E','#8EBA42','#FFB5B8']
    color_dict['winds']           = ['#4878CF','#6ACC65','#D65F5F','#B47CC7','#C4AD66','#77BEDB','#4878CF']
    color_dict['radiation']       = ['#001C7F','#017517','#8C0900','#7600A1','#B8860B','#006374','#001C7F']
    color_dict['plates_and_sr50'] = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2']
    color_dict['is_alive']        = [(0.35,0.55,0.55), (0.55,0.55,0.35), (0.2,0.5,0.8)]
    color_dict['lat_lon']  = [(0.8,0.8,0.8),(0.2,0.4,0.2),(0.8,0.6,0.6),(0.2,0.4,0.2),(0.9,0.5,0.9),(0.3,0.1,0.5),(0.1,0.01,0.01)]
    color_dict['licor'] = ['#23001a','#ffe000','#00fdff']

    # gg_colors    = ['#E24A33','#348ABD','#988ED5','#777777','#FBC15E','#8EBA42','#FFB5B8']
    # muted_colors = ['#4878CF','#6ACC65','#D65F5F','#B47CC7','#C4AD66','#77BEDB','#4878CF']
    # dark_colors  = ['#001C7F','#017517','#8C0900','#7600A1','#B8860B','#006374','#001C7F']
    # other_dark   = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2']
    # other_colors = [(0.8,0.8,0.9), (0.85,0.85,0.9), (0.9,0.9,1.0)]

    parser = argparse.ArgumentParser()                                
    parser.add_argument('-v', '--verbose',    action ='count', help='print verbose log messages')            
    parser.add_argument('-s', '--start_time', metavar='str',   help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time',   metavar='str',   help='end  of processing period, Ymd syntax')
    parser.add_argument('-p', '--path', metavar='str', help='base path to data up to, including /data/, include trailing slash')

    args         = parser.parse_args()
    v_print      = print if args.verbose else lambda *a, **k: None
    verboseprint = v_print

    global data_dir, level1_dir # paths
    if args.path: data_dir = args.path
    else: data_dir = default_data_dir

    start_time = datetime.today()
    if args.start_time: start_time = datetime.strptime(args.start_time, '%Y%m%d') 
    else: # make the data processing start yesterday! i.e. process only most recent full day of data
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0, day=start_time.day-1) 
    if args.end_time: end_time = datetime.strptime(args.end_time, '%Y%m%d')   
    else: end_time = start_time

    print('---------------------------------------------------------------------------------------')
    print('Plotting data days between {} -----> {}'.format(start_time,end_time))
    print('---------------------------------------------------------------------------------------\n')

    quicklooks_dir   = '{}/quicklooks/tower/1_level/'.format(data_dir)
    out_dir_daily    = '{}/daily/'.format(quicklooks_dir)    # where you want to put the png
    out_dir_all_days = '{}/all_days/'.format(quicklooks_dir) # where you want to put the png

    # plot for all of leg 2.
    day_series = pd.date_range(start_time, end_time) # we're going to get date for these days between start->end
    df, code_version = get_tower_l1_data(start_time, end_time, nthreads, data_dir)

    make_plots_pretty('seaborn-whitegrid') # ... and higher resolution

    if make_daily_plots:
        day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
        print("~~ making daily plots for all figures ~~")
        print("----------------------------------------")
        nplotthreads = int(np.floor(nthreads/len(var_dict)))
        for i_day, start_day in enumerate(day_series):
            if i_day % nplotthreads!=0 or i_day>len(day_series): continue

            print("  ... plotting data for day {} (and {} days *with {} plots* after in parallel)".format(start_day,nplotthreads,len(var_dict)))

            plot_q_list = []; plot_p_list = []
            for ithread in range(0,nplotthreads):
                today     = start_day+timedelta(ithread)
                tomorrow  = today+day_delta
                start_str = today.strftime('%Y-%m-%d') # get date string for file name
                end_str   = (today+timedelta(1)).strftime('%Y-%m-%d')   # get date string for file name

                plot_q_list.append({}); plot_p_list.append({});
                for plot_name, subplot_dict in var_dict.items():
                    plot_q_list[ithread][plot_name] = Q()
                    save_str  ='{}/{}/MOSAiC_Tower_{}_{}_to_{}.png'.format(out_dir_daily,plot_name,plot_name, start_str, end_str)

                    plot_p_list[ithread][plot_name] =\
                      P(target=make_plot, args=(df[today:tomorrow].copy(),
                                                subplot_dict,
                                                unit_dict[plot_name],
                                                color_dict[plot_name],
                                                save_str,
                                                True,
                                                plot_q_list[ithread][plot_name])).start()

            for ithread in range(0,nplotthreads):
                for plot_name, subplot_dict in var_dict.items():
                    plot_q_list[ithread][plot_name].get()

    make_plots_pretty('ggplot')
    print("\n ... daily plotting done!!!")
    print("-----------------------------------------------")
    print(" ... resampling for non-daily plots, we have to")
    df = df.resample('1T',label='left').mean()

    if make_leg_plots:
        print(" ... making leg plots for ",end='', flush=True)
        leg_names = ["leg1","leg2","leg3","leg4","leg5"]
        for ileg in range(0,len(leg_list)-1):
            print(" {}...".format(leg_names[ileg]),end='', flush=True)
            leg_dir   = "{}/{}_complete".format(quicklooks_dir,leg_names[ileg])
            start_day = leg_list[ileg]; start_str = start_day.strftime('%Y-%m-%d') # get date string for file name
            end_day   = leg_list[ileg+1]; end_str = end_day.strftime('%Y-%m-%d')   # get date string for file name

            plot_q_dict = {}; plot_p_dict = {}
            for plot_name, subplot_dict in var_dict.items():
                plot_q_dict[plot_name] = Q()
                save_str  ='{}/MOSAiC_Tower_{}_{}_to_{}.png'.format(leg_dir, plot_name, start_str, end_str)
                plot_p_dict[plot_name] = P(target=make_plot,
                                           args=(df[start_day:end_day].copy(),subplot_dict,unit_dict[plot_name],
                                                 color_dict[plot_name],save_str, False,plot_q_dict[plot_name])).start()

            for plot_name, subplot_dict in var_dict.items():
                plot_q_dict[plot_name].get()
        print("\n") # end of leg plots
    # make plots for range *actually* requested when calling scripts
    start_str = start_time.strftime('%Y-%m-%d') # get date string for file name
    end_str   = end_time.strftime('%Y-%m-%d')   # get date string for file name

    print(" ... making plots for entire data set")
    plot_q_dict = {}; plot_p_dict = {}
    for plot_name, subplot_dict in var_dict.items():
        plot_q_dict[plot_name] = Q()
        save_str  ='{}/MOSAiC_Tower_{}_{}_to_{}.png'.format(out_dir_all_days, plot_name, start_str, end_str)
        plot_p_dict[plot_name] = P(target=make_plot,
                                   args=(df[start_time:end_time].copy(), subplot_dict, unit_dict[plot_name],
                                         color_dict[plot_name], save_str,False,plot_q_dict[plot_name])).start()

    for plot_name, subplot_dict in var_dict.items():
        plot_q_dict[plot_name].get()

    plt.close('all') # closes figure before looping again 
    exit() # end main()

def get_tower_data(curr_file, curr_station, today, q):

    if os.path.isfile(curr_file):
        xarr_ds = xr.open_dataset(curr_file)
        data_frame = xarr_ds.to_dataframe()
        code_version = xarr_ds.attrs['version']
    else:
        print(' !!! file {} not found for date {}'.format(curr_file,today))
        data_frame   = pd.DataFrame()
        code_version = None
    q.put(data_frame)
    q.put(code_version)
    return # can be implicit

# abstract plotting to function so plots are made iteratively according to the keys and values in subplot_dict and
# the supplied df and df.index.... i.e. this plots the full length of time available in the supplied df
def make_plot(df, subplot_dict, units, colors, save_str, daily, q):

    nsubs = len(subplot_dict)
    if daily: fig, ax = plt.subplots(nsubs,1,figsize=(80,40*nsubs))  # square-ish, for daily detail
    else:     fig, ax = plt.subplots(nsubs,1,figsize=(160,30*nsubs)) # more oblong for long time series

    # loop over subplot list and plot all variables for each subplot
    ivar = -1; isub = -1
    for subplot_name, var_list in subplot_dict.items():
        isub+=1
        legend_additions = [] # uncomment code below to add the percent of missing data to the legend

        for var in var_list:
            ivar+=1

            if 'vaisala_T' in var or 'vaisala_RH' in var:
                if isinstance(colors[ivar],str) or isinstance(colors[ivar][0],float) :
                    color_tuples = get_rgb_trio(colors[ivar])
                else: color_tuples = list(colors[ivar])
                height_strs = ['_2m','_6m','_10m']
                for ihs, hs in enumerate(height_strs):
                    try:
                        obs_var   = var+'{}'.format(hs)
                        var_color = color_tuples[ihs]
                        perc_miss  = fl.perc_missing(df[obs_var])

                        time_lims = (df.index[0], df.index[-1]+(df.index[-1]-df.index[-2])) 
                        df[obs_var].plot(xlim=time_lims, ax=ax[isub], color=var_color)
                        legend_additions.append('{} (missing '.format(obs_var)+str(perc_miss)+'%)')
                        plot_success = True
                    except Exception as e:
                        legend_additions.append('{} (no data)'.format(obs_var))
                        continue
            else:
                color_tuples = get_rgb(colors[ivar])
                try:
                    obs_var   = var
                    var_color = color_tuples
                    perc_miss  = fl.perc_missing(df[obs_var])

                    time_lims = (df.index[0], df.index[-1]+(df.index[-1]-df.index[-2])) 
                    df[obs_var].plot(xlim=time_lims, ax=ax[isub], color=var_color)
                    legend_additions.append('{} (missing '.format(obs_var)+str(perc_miss)+'%)')
                    plot_success = True

                except Exception as e:
                    legend_additions.append('{} (no data)'.format(obs_var))
                    continue

        #add useful data info to legend
        j = 0 
        h,l = ax[isub].get_legend_handles_labels()
        for s in range(0,len(l)):
            l[s] = legend_additions[s]

        #ax[isub].legend(l, loc='upper right',facecolor=(0.3,0.3,0.3,0.5),edgecolor='white')
        ax[isub].legend(l, loc='best',facecolor=(0.3,0.3,0.3,0.5),edgecolor='white')    
        ax[isub].set_ylabel('{} [{}]'.format(subplot_name, units[subplot_name]))
        ax[isub].grid(b=True, which='major', color='grey', linestyle='-')
        #ax[isub].grid(b=False, which='minor')

        if isub==len(subplot_dict)-1:
            ax[isub].set_xlabel('date [UTC]', labelpad=-0)
        else:
            ax[isub].tick_params(which='both',labelbottom=False)
            ax[isub].set_xlabel('', labelpad=-400)

    fig.text(0.5, 0.005,'(plotted on {} from level1 data version {} )'.format(datetime.today(), code_version),
             ha='center')
    fig.tight_layout(pad=3) # cut off white-space on edges

    if not os.path.isdir(os.path.dirname(save_str)):
        print("!!! making directory {}... hope that's what you intended".format(os.path.dirname(save_str)))
        os.makedirs(os.path.dirname(save_str))

    fig.savefig(save_str)
        
    plt.close() # closes figure before exiting
    q.put(True)
    return # not necessary


def get_rgb(color):
    if isinstance(color, str):
        rgb = hex_to_rgb(color)
    else: rgb = color
    return rgb

# returns 3 rgb tuples of varying darkness for a given color, 
def get_rgb_trio(color):
    if isinstance(color, str):
        rgb = hex_to_rgb(color)
    else: rgb = color
    r=rgb[0]; g=rgb[1]; b=rgb[2]
    lume = np.sqrt(0.299*r**22 + 0.587*g**2 + 0.114*b**2)
    h,l,s = colorsys.rgb_to_hls(r,g,b)
    if(lume>0.5): 
        col_one = colorsys.hls_to_rgb(h, l, s)
        col_two = colorsys.hls_to_rgb(h, l-0.2, s)
        col_thr = colorsys.hls_to_rgb(h, l-0.4, s)
    else:
        col_one = colorsys.hls_to_rgb(h, l+0.4, s)
        col_two = colorsys.hls_to_rgb(h, l+0.2, s)
        col_thr = colorsys.hls_to_rgb(h, l, s)
    return [col_one, col_two, col_thr]

def hex_to_rgb(hex_color):
    rgb_tuple = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return tuple(map(lambda x: x/256.0, rgb_tuple))

def make_plots_pretty(style_name):
    # plt.style.use('ggplot')            # grey grid with bolder colors
    # plt.style.use('seaborn-whitegrid') # white grid with softer colors
    plt.style.use(style_name)
    mpl.rcParams['agg.path.chunksize']  = 10000 # big data, big RAM
    mpl.rcParams['lines.linewidth']     = 12
    mpl.rcParams['font.size']           = 80
    mpl.rcParams['legend.fontsize']     = 'medium'
    mpl.rcParams['axes.labelsize']      = 'xx-large'
    mpl.rcParams['axes.titlesize']      = 'xx-large'
    mpl.rcParams['xtick.labelsize']     = 'xx-large'
    mpl.rcParams['ytick.labelsize']     = 'xx-large'
    mpl.rcParams['ytick.labelsize']     = 'xx-large'
    mpl.rcParams['grid.linewidth']      = 2.
    mpl.rcParams['axes.linewidth']      = 6
    mpl.rcParams['axes.grid']           = True
    mpl.rcParams['axes.grid.which']     = 'minor'
    mpl.rcParams['axes.edgecolor']      = 'grey'
    mpl.rcParams['axes.labelpad']       = 100
    mpl.rcParams['axes.titlepad']       = 100
    mpl.rcParams['axes.xmargin']        = 0.3
    mpl.rcParams['axes.ymargin']        = 0.3
    mpl.rcParams['xtick.major.pad']     = 10
    mpl.rcParams['ytick.major.pad']     = 10
    mpl.rcParams['xtick.minor.pad']     = 10
    mpl.rcParams['ytick.minor.pad']     = 10
    mpl.rcParams['xtick.minor.visible'] = True
    mpl.rcParams['axes.spines.right']   = False
    mpl.rcParams['axes.spines.top']     = False
    mpl.rcParams['legend.facecolor']    = 'white'

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way 
if __name__ == '__main__': 
    main_locals = main() 
