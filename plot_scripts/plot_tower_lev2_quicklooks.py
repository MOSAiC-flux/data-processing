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

sys.path.insert(0,'..')

import functions_library as fl 

def main(): # the main data crunching program  

    parser = argparse.ArgumentParser()                                
    parser.add_argument('-v', '--verbose',    action ='count', help='print verbose log messages')            
    parser.add_argument('-s', '--start_time', metavar='str',   help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time',   metavar='str',   help='end  of processing period, Ymd syntax')
    
    multiheight_var_list = ['temp_metek', 'wind_direction_metek', 'wind_speed_metek', 'pw_vaisala', 'RHi_vaisala', 'MR_vaisala',
                            'dewpoint_vaisala', 'temp_vaisala', 'rel_humidity_vaisala']

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

    data_dir = '../processed_data/tower/level2/' # point this program to your data
    tail_str = '.nc'    # plot 1 second data
    head_str = 'level2_preliminary_tower_10min.'           # leading data file string 


    out_dir_daily    = '../quicklooks/tower/daily/'           # wher you want to put the png
    out_dir_all_days = '../quicklooks/tower/all_days/'           # wher you want to put the png

    # plot for all of leg 2.
    time_lims  = (start_time, end_time)

    make_plots_pretty() # ... and higher resolution
    max_len_height_str = np.max(len(height_strs[:]))

    day_series = pd.date_range(start_time, end_time) # we're going to get date for these days between start->end

    df_list = []
    print(" Retreiving data from netcdf files...")
    for i_day, today in enumerate(day_series): # loop over the days in the processing range and get a list of files
        if i_day % 10 == 0: print("  ... getting data for day {}".format(today))
        date_str  = today.strftime('%Y%m%d') # get date string for file name
        curr_file = data_dir+head_str+'{}'.format(date_str)+tail_str # name of file from today
        if os.path.isfile(curr_file):
            xarr_ds = xr.open_dataset(curr_file)
            data_frame      = xarr_ds.to_dataframe()
            df_list.append(data_frame)
        else:
            print(' !!! file {} not found for date {}'.format(curr_file,today))
            continue
    df = pd.concat(df_list)
    time_dates = df.index
    df['time'] = time_dates # duplicates index... but it can be convenient

    print('') 
    print(' ... data sample :')
    print('================')
    print(df)

    var_list_dict = {}# put variables to be plotted into tuples
    for var_name in multiheight_var_list: 
        var_list_dict[var_name] = []
        for height in height_strs: var_list_dict[var_name].append(var_name+'_'+height)
    # append some stuff by hand:

    var_list_dict['pressure']   = ['pressure_vaisala_2m','mast_pressure']
    var_list_dict['flux_plate'] = ['flux_plate_A_Wm2','flux_plate_B_Wm2'] 
    var_list_dict['IRT']        = ['body_T_IRT','surface_T_IRT'] 

    print('\n\n')
    print('   Plotting variables:\n')
    for var_name, plot_vars in var_list_dict.items():
        print('       {}'.format(var_name))
    print('\n\n')

    for var_name, plot_vars in var_list_dict.items():
        print("... plotting {} for full time range".format(var_name))
        plot_str = 'MOSAiC_tower_{}'.format(var_name) # what to name the png file

        plot_vars = var_list_dict[var_name]


        #fig = plt.figure(figsize=(35,15))

        legend_additions = [] # uncomment code below to add the percent of missing data to the legend

        fig, ax = plt.subplots(figsize=(35,15))

        i  = 0
        for var in plot_vars:
            perc_miss = fl.perc_missing(df[var])
            df[var].plot(xlim=time_lims, ax=ax)
            legend_additions.append('(missing '+str(perc_miss)+'%)')
            i = i+1

        # add useful data info to legend
        i = 0
        h,l = ax.get_legend_handles_labels()
        for s in plot_vars: l[i] = s + legend_additions[i]; i=i+1;
        ax.legend(l, loc='best',facecolor='white',edgecolor='white')

        ax.set_ylabel('{}'.format(var_name))
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
        # for obj in tl: 
        #     print(obj)
        #     print(dir(obj))
        #ml = ax.xaxis.set_major_locator(hl)


        ax.set_title('MOSAiC flux tower observations')
        fig.text(0.43, 0.005,'(plotted at {})'.format(today.today()))
        fig.tight_layout(pad=3.0) # cut off white-space on edges
        start_str = start_time.strftime('%Y-%m-%d') # get date string for file name
        end_str   = end_time.strftime('%Y-%m-%d')   # get date string for file name
        save_str  ='{}/{}_{}_to_{}.png'.format(out_dir_all_days, plot_str, start_str, end_str)   
        print('... saving to: {}'.format(save_str))
        fig.savefig(save_str)   
    
    plt.close('all') # closes figure before looping again 

    for var_name, plot_vars in var_list_dict.items():
        print("\n Making daily plots for var {}, takes a while...".format(var_name))
        for i_day, today in enumerate(day_series):
            if i_day % 10 == 0:
                print(" ... plotting {}".format(today))
                plt.close('all') # closes figure before looping again 
            plot_str = 'MOSAiC_tower_{}'.format(var_name) # what to name the png file

            #fig = plt.figure(figsize=(35,15))

            legend_additions = [] # uncomment code below to add the percent of missing data to the legend

            fig, ax = plt.subplots(figsize=(35,15))

            i  = 0
            plot_success = False
            for var in plot_vars:
                try: 
                    df[var][today:today+timedelta(1)].plot(ax=ax)
                    perc_miss = fl.perc_missing(df[var])
                    df[var].plot(xlim=time_lims, ax=ax)
                    legend_additions.append('(missing '+str(perc_miss)+'%)')
                    plot_success = True
                except Exception as e:
                    legend_additions.append('(no data)')
                    print(e)
                    continue
                i = i+1
            if plot_success == False:
                print("... no data/plotting for day {}".format(today))
                continue

            # add useful data info to legend
            i = 0
            h,l = ax.get_legend_handles_labels()
            for s in plot_vars: l[i] = s + legend_additions[i]; i=i+1;
            ax.legend(l, loc='best',facecolor='white',edgecolor='white')

            ax.set_ylabel('{}'.format(var_name))
            ax.set_xlim(today, today+timedelta(1)) # fix stupid edges that are wider than data

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
            fig.text(0.43, 0.005,'(plotted at {})'.format(today.today()))
            fig.tight_layout(pad=3.0) # cut off white-space on edges
            today_str = today.strftime('%Y%m%d') # get date string for file name
            if not os.path.exists('{}/{}'.format(out_dir_daily, var_name)):
                print('... making dir: {}/{}'.format(out_dir_daily, var_name))
                os.makedirs('{}/{}'.format(out_dir_daily, var_name))
            save_str  ='{}/{}/{}_{}.png'.format(out_dir_daily,var_name, plot_str, today_str)
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

