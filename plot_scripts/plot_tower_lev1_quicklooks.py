#!/usr/local/bin/python3
# -*- coding: utf-8 -*-  
# ############################################################################################
# AUTHOR: Michael Gallagher (CIRES/NOAA)
# EMAIL:  michael.r.gallagher@noaa.gov
# 
# PURPOSE:
#
# Plots variables that are measured at all four heights on the MOSAiC flow for quicklooks
# 
# Date:  
# 
# ############################################################################################
from   datetime import datetime, timedelta
import os, inspect, argparse, sys

import matplotlib as mpl
import matplotlib.pyplot as plt 
import numpy             as np
import pandas            as pd
import xarray            as xr
import netCDF4 

sys.path.insert(0,'..') # add ../ to imports to grab "functions_library" file

from tower_data_definitions import define_level1_slow, define_level1_fast
import functions_library as fl 

def main(): # the main data crunching program  

    parser = argparse.ArgumentParser()                                
    parser.add_argument('-v', '--verbose',    action ='count', help='print verbose log messages')            
    parser.add_argument('-s', '--start_time', metavar='str',   help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time',   metavar='str',   help='end  of processing period, Ymd syntax')
    
    data_atts_slow, slow_vars = define_level1_slow()
    data_atts_fast, fast_vars = define_level1_fast()

    args       = parser.parse_args()                                        
    start_time = datetime.today()
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y%m%d') 
    else: 
        # make the data processing start yesterday! i.e. process only most recent full day of data
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0, day=start_time.day-1) 

    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y%m%d')   
    else: 
        end_time = start_time

    print('---------------------------------------------------------------------------------------')
    print('Plotting data days between {} -----> {}'.format(start_time,end_time))
    print('---------------------------------------------------------------------------------------\n')

    data_dir = '../processed_data/tower/level1/' # point this program to your data
    tail_str = '.nc'    # plot 1 second data
    head_str_slow = 'slow_preliminary_tower.'           # leading data file string 
    head_str_fast = 'fast_preliminary_tower.'           # leading data file string 
    height_strs = ['2m','6m','10m','mast']  # plot at these heights

    out_dir    = '../quicklooks/tower/level1/'           # wher you want to put the png

    # groups in netcdf level1 for fast tower data
    fast_groups = ['metek_2m','metek_6m','metek_10m','metek_mast','licor']

    # plot for all of leg 2.
    time_lims  = (start_time, end_time)

    make_plots_pretty() # ... and higher resolution
    max_len_height_str = np.max(len(height_strs[:]))

    day_series = pd.date_range(start_time, end_time) # we're going to get date for these days between start->end

    height_strs = ['2m','6m','10m']
    multiheight_var_list = ['vaisala_RH', 'vaisala_T']

    slow_var_list_dict = {}# put variables to be plotted into tuples
    for var_name in multiheight_var_list: 
        slow_var_list_dict[var_name] = []
        for height in height_strs: slow_var_list_dict[var_name].append(var_name+'_'+height)

    slow_var_list_dict['vaisala_RH'].append('mast_RH')
    slow_var_list_dict['vaisala_T'].append('mast_T')

    slow_var_list_dict['vaisala_Td']  = ['vaisala_Td_2m','vaisala_Td_6m','vaisala_Td_10m']
    slow_var_list_dict['fp_mV']       = ['fp_A_mV','fp_B_mV']
    slow_var_list_dict['fp_Wm2']      = ['fp_A_Wm2','fp_B_Wm2']
    slow_var_list_dict['apogee_T']    = ['apogee_body_T','apogee_targ_T']
    slow_var_list_dict['sr50_dist']   = ['sr50_dist']
    slow_var_list_dict['pressure']    = ['vaisala_P_2m', 'mast_P']

    multiheight_var_list_fast = ['x','y','z','T']
    height_strs = ['2m','6m','10m','mast']
    fast_var_list_dict = {}# put variables to be plotted into dict
    for var_name in multiheight_var_list_fast: 
        fast_var_list_dict['metek_'+var_name] = []
        for height in height_strs: fast_var_list_dict['metek_'+var_name].append('metek_'+height+'_'+var_name)

    multiheight_var_list_fast = ['hspd','incx','incy']
    height_strs = ['2m','6m','10m'] # no mast for these
    for var_name in multiheight_var_list_fast: 
        fast_var_list_dict['metek_'+var_name] = []
        for height in height_strs: fast_var_list_dict['metek_'+var_name].append('metek_'+height+'_'+var_name)

    fast_var_list_dict['licor_co2'] = ['licor_co2']
    fast_var_list_dict['licor_h2o'] = ['licor_h2o']
    fast_var_list_dict['licor_T']   = ['licor_T']
    fast_var_list_dict['licor_pr']  = ['licor_pr']

    print("\n retreiving data from netcdf files...")
    print("           ... fyi we resample the 20hz fast data to 10 minutessampl because plotting 20hz data is s.l.o.w.\n\n")
    for i_day, today in enumerate(day_series): # loop over the days in the processing range and get a list of files
        if i_day % 1 == 0: print("\n ... getting and plotting data for day {}".format(today))
        date_str  = today.strftime('%Y%m%d') # get date string for file name
        curr_file_slow = data_dir+head_str_slow+'{}'.format(date_str)+tail_str # name of file from today
        if os.path.isfile(curr_file_slow):
            xarr_ds_slow    = xr.open_dataset(curr_file_slow)
            try:
                df_slow = xarr_ds_slow.to_dataframe()
            except exception as e:
                print(e)
                print("... {} has no data in slow file {}".format(today,curr_file_slow))

            time_dates_slow = df_slow.index
            df_slow['time'] = time_dates_slow # duplicates index... but it can be convenient

            if i_day == 0:
                print('') 
                print(' ... slow data sample :')
                print('================\n')
                print(df_slow)
                print("\n")
            
            print("\n ... plotting:", end =" ",flush=True),
            nchars = 0 
            for var_title, var_names in slow_var_list_dict.items():
                print("{},".format(var_title), end =" ", flush=True); nchars+=len(var_title)
                if nchars >= 75: print("\n              ",end="");  nchars=0
                plot_str = 'mosaic_tower_{}'.format(var_title) # what to name the png file
                today_str = today.strftime('%y-%m-%d') # get date string for file name

                if not os.path.exists('{}/{}'.format(out_dir, var_title)):
                    os.makedirs('{}/{}'.format(out_dir, var_title))

                save_str  ='{}/{}/{}_{}.png'.format(out_dir, var_title, plot_str, today_str)
                plot_vars(df_slow, var_names, var_title, save_str, today, today+timedelta(1)) # plot one day

        else:
            print(' !!! slow file {} not found for date {}'.format(curr_file_slow,today))

        curr_file_fast = data_dir+head_str_fast+'{}'.format(date_str)+tail_str # name of file from today
        if os.path.isfile(curr_file_fast):

            df_list_fast = []
            for var_group in fast_groups:
                xarr_ds_fast = xr.open_dataset(curr_file_fast, group=var_group)
                try: 
                    df_group = xarr_ds_fast.to_dataframe()
                    df_group  = df_group.resample('10T',label='left').mean() 
                    df_list_fast.append(df_group)
                except Exception as e:
                    print("... no data in fast file {}".format(today,curr_file_fast))
                    break
            df_fast = pd.concat(df_list_fast, axis=1)
            time_dates_fast = df_fast.index
            df_fast['time'] = time_dates_fast # duplicates index... but it can be convenient

            if i_day == 0:
                print('\n') 
                print(' ... fast data sample :')
                print('================\n')
                print("\n")
                print(df_fast)
                print("\n")

            print("\n ... plotting:", end =" ",flush=True),
            nchars = 0 
            for var_title, var_names in fast_var_list_dict.items():
                print("{},".format(var_title), end =" ", flush=True); nchars+=len(var_title)
                if nchars >= 75: print("\n              ",end="");  nchars=0
                plot_str = 'MOSAiC_tower_{}'.format(var_title) # what to name the png file
                today_str = today.strftime('%Y-%m-%d') # get date string for file name

                if not os.path.exists('{}/{}'.format(out_dir, var_title)):
                    print('\n !!! making dir: {}/{} !!! \n'.format(out_dir, var_title))
                    os.makedirs('{}/{}'.format(out_dir, var_title))

                save_str   ='{}/{}/{}_{}.png'.format(out_dir, var_title, plot_str, today_str)
                plot_vars(df_fast, var_names, var_title, save_str, today, today+timedelta(1)) # plot one day

            print("")
        else:
            print(' !!! fast file {} not found for date {}'.format(curr_file_fast,today))
            continue


def plot_vars(df, plot_vars, ylabel, save_str, start_day, end_day):
    time_lims  = (start_day, end_day)

    legend_additions = [] # uncomment code below to add the percent of missing data to the legend

    fig, ax = plt.subplots(figsize=(35,15))

    i  = 0
    plot_vars = [plot_vars] if type(plot_vars) is str else plot_vars # lets us plot single or multiple variables

    for var in plot_vars:
        try:
            perc_miss = fl.perc_missing(df[var])
        except Exception as e:
            print(e)
            print("no {} data".format(plot_vars))
            this_var_doesnt_exist_so_we_do_nothing = False
            return
            
        df[var].plot(xlim=time_lims, ax=ax)
        legend_additions.append(' (missing '+str(perc_miss)+'%)')
        i = i+1

    # add useful data info to legend
    i = 0
    h,l = ax.get_legend_handles_labels()
    for s in plot_vars: l[i] = s + legend_additions[i]; i=i+1;
    ax.legend(l, loc='best',facecolor='white',edgecolor='white')

    ax.set_ylabel('{}'.format(ylabel))
    #ax.set_xlim(today, today+timedelta(1)) # fix stupid edges that are wider than data

    # get style colors used for lines so that we can match them up for the pressure vars
    i = 0 
    colors = []
    for line in ax.get_lines():
        colors.append(line.get_color())
        i += 1

    ax.set_xlabel('[time - UTC]',labelpad=-0)

    hl = mpl.dates.DayLocator(interval=1)
    ml = ax.xaxis.get_major_locator()
    tl = ax.xaxis.get_ticklabels()
    ml.day = 1

    ax.set_title('MOSAiC flux tower observations')
    #print("... saving at {}".format(save_str))
    fig.text(0.43, 0.005,'(plotted at {})'.format(start_day.today()))
    fig.tight_layout(pad=3.0) # cut off white-space on edges
    fig.savefig(save_str)   
    
    plt.close('all') # closes figure before looping again 


def make_plots_pretty():

    # choose one
    plt.style.use('ggplot')             # grey grid with bolder colors
    #plt.style.use('seaborn-whitegrid') # white grid with softer colors

    mpl.rcParams['lines.linewidth']     = 3
    mpl.rcParams['font.size']           = 22
    mpl.rcParams['legend.fontsize']     = 'medium'
    mpl.rcParams['axes.labelsize']      = 'xx-large'
    mpl.rcParams['axes.titlesize']      = 'xx-large'
    mpl.rcParams['xtick.labelsize']     = 'xx-large'
    mpl.rcParams['ytick.labelsize']     = 'xx-large'
    mpl.rcParams['ytick.labelsize']     = 'xx-large'
    mpl.rcParams['grid.linewidth']      = 4.
    mpl.rcParams['axes.linewidth']      = 6
    mpl.rcParams['axes.grid']           = True
    mpl.rcParams['axes.grid.which']     = 'minor'
    mpl.rcParams['axes.edgecolor']      = 'grey'
    mpl.rcParams['axes.labelpad']       = 20
    mpl.rcParams['axes.titlepad']       = 20
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
    main() 

