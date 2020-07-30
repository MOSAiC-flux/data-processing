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

from asfs_data_definitions import define_level1_slow, define_level1_fast, code_version
code_version = code_version()

import functions_library as fl

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning) 

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

    data_dir = '../processed_data/flux_stations/level1/' # point this program to your data
    tail_str = '.nc'    # plot 1 second data
    head_str_slow = '/slow_preliminary_'           # leading data file string 
    head_str_fast = '/fast_preliminary_'           # leading data file string 

    station_strs = ['asfs30','asfs40','asfs50']
    site_strs    = ['L2','L1','L3']

    # station_strs = ['asfs30']
    # site_strs    = ['L2']

    out_dir    = '../quicklooks/asfs/level1/'           # wher you want to put the png

    # plot for all of leg 2.
    time_lims  = (start_time, end_time)

    make_plots_pretty() # ... and higher resolution

    day_series = pd.date_range(start_time, end_time) # we're going to get date for these days between start->end


    slow_var_list_dict = {}
    fast_var_list_dict = {}

    slow_var_list_dict['metek_inc']                = ['metek_InclX_Avg','metek_InclY_Avg'] 
    slow_var_list_dict['sr30_up_down_DegC_Avg']    = ['sr30_swu_DegC_Avg','sr30_swd_DegC_Avg']
    slow_var_list_dict['sr30_up_down_Irr_Avg']     = ['sr30_swu_Irr_Avg','sr30_swd_Irr_Avg']
    slow_var_list_dict['sr30_up_down_IrrC_Avg']    = ['sr30_swu_IrrC_Avg','sr30_swd_IrrC_Avg']
    slow_var_list_dict['apogee_T_Avg']             = ['apogee_body_T_Avg','apogee_targ_T_Avg']  
    slow_var_list_dict['sr50_dist_Avg']            = ['sr50_dist_Avg']
    slow_var_list_dict['vaisala_RH_Avg']           = ['vaisala_RH_Avg']
    slow_var_list_dict['vaisala_T_Avg']            = ['vaisala_T_Avg']  
    slow_var_list_dict['vaisala_Td_Avg']           = ['vaisala_Td_Avg'] 
    slow_var_list_dict['vaisala_P_Avg']            = ['vaisala_P_Avg']  

    slow_var_list_dict['ir20_up_down_mV_Avg']      = ['ir20_lwu_mV_Avg','ir20_lwd_mV_Avg']
    slow_var_list_dict['ir20_up_down_Wm2_Avg']     = ['ir20_lwu_Wm2_Avg','ir20_lwd_Wm2_Avg']
    slow_var_list_dict['flux_plates_mV_Avg']       = ['fp_A_mV_Avg','fp_B_mV_Avg']
    slow_var_list_dict['flux_plates_Wm2_Avg']      = ['fp_A_Wm2_Avg','fp_B_Wm2_Avg']

    slow_var_list_dict['sr30_up_down_fantach_Avg'] = ['sr30_swu_fantach_Avg','sr30_swd_fantach_Avg']         
    slow_var_list_dict['sr30_up_down_heatA_Avg']   = ['sr30_swu_heatA_Avg','sr30_swd_heatA_Avg']
    slow_var_list_dict['ir20_up_down_fan_Avg']     = ['ir20_lwu_fan_Avg','ir20_lwd_fan_Avg']

    fast_var_list_dict['metek_x']                  = ['metek_x']
    fast_var_list_dict['metek_y']                  = ['metek_y']
    fast_var_list_dict['metek_z']                  = ['metek_z']
    fast_var_list_dict['metek_T']                  = ['metek_T']

    fast_var_list_dict['metek_heatstatus']         = ['metek_heatstatus']    
    fast_var_list_dict['metek_senspathstate']      = ['metek_senspathstate'] 
    fast_var_list_dict['licor_co2']                = ['licor_co2']           
    fast_var_list_dict['licor_h2o']                = ['licor_h2o']           
    fast_var_list_dict['licor_pr']                 = ['licor_pr']            
    fast_var_list_dict['licor_diag']               = ['licor_diag']          
    fast_var_list_dict['licor_co2_str']            = ['licor_co2_str']       
    fast_var_list_dict['licor_T']                  = ['licor_T']             


    for name, var_list in slow_var_list_dict.items():
        for var in var_list:
            if var not in slow_vars:
                print("{} not found in level1 slow definintions, the definition probably changed but you didn't change this code... exiting".format(var))
                exit()

    for name, var_list in fast_var_list_dict.items():
        for var in var_list:
            if var not in fast_vars:
                print("{} not found in fast definintions, the definition probably changed but you didn't change this code... exiting".format(var))
                exit()

    print("\n retreiving data from netcdf files...")
    print("           ... fyi we resample the 20hz fast data to 10 minutessampl because plotting 20hz data is s.l.o.w.\n\n")
    for i_day, today in enumerate(day_series): # loop over the days in the processing range and get a list of files
        if i_day % 1 == 0: print("\n ... getting and plotting data for day {}".format(today))
        date_str  = today.strftime('%Y%m%d') # get date string for file name
        df_all_slow = pd.DataFrame()
        for station_ind,curr_station in enumerate(station_strs):
            
            curr_file_slow = data_dir+curr_station+head_str_slow+curr_station+'.'+site_strs[station_ind]+'.{}'.format(date_str)+tail_str # name of file from today
            if os.path.isfile(curr_file_slow):
                xarr_ds_slow    = xr.open_dataset(curr_file_slow)
                try:
                    df_slow = xarr_ds_slow.to_dataframe()
                except Exception as e:
                    print(e)
                    print("... {} has no data in slow file {}".format(today,curr_file_slow))

                time_dates_slow = df_slow.index
                df_slow['time'] = time_dates_slow # duplicates index... but it can be convenient
                df_slow = df_slow.add_suffix('_{}'.format(curr_station))
                if df_all_slow.empty:
                    df_all_slow = df_slow
                else:
                    df_all_slow  = pd.concat( [df_all_slow,df_slow], axis=1 )
                    
            else:
                print(' !!! {} slow file not found on {}:'.format(curr_station,today))
                print(" !!! {}".format(curr_file_slow))

        try: inds = df_all_slow.index
        except:
            print(" !!! no slow data for any stations on {}".format(today))
            continue
            
        if i_day == 0:
            print('') 
            print(' ... slow data sample :')
            print('================\n')
            print(df_all_slow)
            print("\n")

        print("\n ... plotting:", end =" ",flush=True),
        nchars = 0 
        for var_title, var_names in slow_var_list_dict.items():
            print("{},".format(var_title), end =" ", flush=True); nchars+=len(var_title)
            if nchars >= 75: print("\n              ",end="");  nchars=0
            plot_str = 'mosaic_{}'.format(var_title) # what to name the png file
            today_str = today.strftime('%y-%m-%d') # get date string for file name

            if not os.path.exists('{}/{}'.format(out_dir, var_title)):
                os.makedirs('{}/{}'.format(out_dir, var_title))

            all_station_var_names = []
            for curr_station in station_strs:
                all_station_var_names = all_station_var_names+[name+'_'+curr_station for name in var_names] 

            save_str  ='{}/{}/{}_{}.png'.format(out_dir, var_title, plot_str, today_str)
            plot_vars(df_all_slow, all_station_var_names, var_title, save_str, today, today+timedelta(1)) # plot one day
        print("\n")
        df_all_fast = pd.DataFrame()
        for station_ind,curr_station in enumerate(station_strs):

            curr_file_fast = data_dir+curr_station+head_str_fast+curr_station+'.'+site_strs[station_ind]+'.{}'.format(date_str)+tail_str # name of file from today

            if os.path.isfile(curr_file_fast):

                ds_fast = xr.open_dataset(curr_file_fast)
                try: 
                    df = xarr_ds_fast.to_dataframe()
                    df_fast  = df.resample('10T',label='left').mean() 

                except Exception as e:
                    print("... no data in fast file {}".format(today))
                    print("... {}".format(curr_file_fast))
                    continue

                time_dates_fast = df_fast.index
                df_fast['time'] = time_dates_fast # duplicates index... but it can be convenient
                df_fast = df_fast.add_suffix('_{}'.format(curr_station))

                if df_all_fast.empty:
                    df_all_fast  = df_fast
                else:
                    df_all_fast  = pd.concat( [df_all_fast,df_fast], axis=1 )

            else:
                print(' !!! fast file for {} not found on {}'.format(curr_station,today))
                print(" !!! {}".format(curr_file_fast))
                continue

        try: inds = df_all_fast.index
        except:
            print(" !!! no fast data for any stations on {}".format(today))
            continue

        if i_day == 0:
            print('\n') 
            print(' ... fast data sample :')
            print('================\n')
            print("\n")
            print(df_all_fast)
            print("\n")

        print("\n ... plotting:", end =" ",flush=True),
        nchars = 0 
        for var_title, var_names in fast_var_list_dict.items():
            print("{},".format(var_title), end =" ", flush=True); nchars+=len(var_title)
            if nchars >= 75: print("\n              ",end="");  nchars=0
            plot_str = 'MOSAiC_{}'.format(var_title) # what to name the png file
            today_str = today.strftime('%Y-%m-%d') # get date string for file name

            if not os.path.exists('{}/{}'.format(out_dir, var_title)):
                print('\n !!! making dir: {}/{} !!! \n'.format(out_dir, var_title))
                os.makedirs('{}/{}'.format(out_dir, var_title))

            all_station_var_names = []
            for curr_station in station_strs:
                all_station_var_names = all_station_var_names + [name+curr_station for name in var_names] 

            save_str   ='{}/{}/{}_{}.png'.format(out_dir, var_title, plot_str, today_str)
            plot_vars(df_all_fast, all_station_var_names, var_title, save_str, today, today+timedelta(1)) # plot one day



def plot_vars(df, plot_vars, ylabel, save_str, start_day, end_day):
    time_lims  = (start_day, end_day)

    legend_additions = [] # uncomment code below to add the percent of missing data to the legend

    fig, ax = plt.subplots(figsize=(35,15))

    plot_vars = [plot_vars] if type(plot_vars) is str else plot_vars # lets us plot single or multiple variables

    plot_vars_copy = plot_vars.copy()

    for i_var,var in enumerate(plot_vars_copy):
        i_var += 1
        try:
            perc_miss = fl.perc_missing(df[var])
        except Exception as e:
            df[var] = [np.NaN for i in range(len(df.index))]
            perc_miss = 100.0

        df[var].plot(xlim=time_lims, ax=ax)
        legend_additions.append(' (missing '+str(perc_miss)+'%)')

    # add useful data info to legend
    i = 0
    h,l = ax.get_legend_handles_labels()

    for i,s in enumerate(plot_vars): l[i] = s + legend_additions[i]; 
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

