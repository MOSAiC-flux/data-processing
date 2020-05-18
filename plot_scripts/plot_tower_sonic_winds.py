#!/usr/bin/python3
# ############################################################################################
# AUTHOR: Michael Gallagher (CIRES/NOAA)
# EMAIL:  michael.r.gallagher@noaa.gov
# 
# PURPOSE:
#
# Plots wind speed/direction and temperature sensors at 2m, 6m, 10m, and 'mast-top'. 
# This takes dates as arguments if you want to plot a range of days, otherwise
# it plots the data from yesterday. It loops over the days you ask for with the flags.
# More or less a 'quicklook' plotting script 
# 
# ############################################################################################
from   datetime import datetime, timedelta
import os, inspect, argparse

import matplotlib as mpl

# this is required because for some reason the default ubuntu matplotlib doesn't
# like running headless... took me a while to figure out without internet
mpl.use('pdf');
mpl.interactive(False)

import matplotlib.pyplot as plt 
import numpy             as np
import pandas            as pd  
import netCDF4 

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

def main(): # the main data crunching program  

    var_name = 'temperature'             # labels the axis
    data_dir = '../tower_data/processed_data/10min/' # point this program to your data
    tail_str = '_10min_level2_preliminary.nc'    # plot 1 second data
    head_str = 'MOSAiC_tower_'           # leading data file string 
    height_strs = ['2m','6m','10m','mast']

    speed_name = 'wind_speed_metek' #  we're plotting all four temperatures in the vertical
    speed_vars = [speed_name+'_2m',speed_name+'_6m',speed_name+'_10m',speed_name+'_mast']

    dir_name = 'wind_direction_metek' #  we're plotting all four temperatures in the vertical
    dir_vars = [dir_name+'_2m',dir_name+'_6m',dir_name+'_10m',dir_name+'_mast']

    temp_name = 'temp_metek' #  we're plotting all four temperatures in the vertical
    temp_vars = [temp_name+'_2m',temp_name+'_6m',temp_name+'_10m',temp_name+'_mast']

    out_dir  = './quicklooks/'           # where you want to put the png
    plot_str = 'MOSAiC_tower_sonic_winds_temps'.format() # what to name the png file

    parser = argparse.ArgumentParser()                                
    parser.add_argument('-v', '--verbose',    action ='count', help='print verbose log messages')            
    parser.add_argument('-s', '--start_time', metavar='str',   help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time',   metavar='str',   help='end  of processing period, Ymd syntax')

    args         = parser.parse_args()                                        
    v_print      = print if args.verbose else lambda *a, **k: None
    global verboseprint
    verboseprint = v_print

    #start_time = datetime.today()
    start_time = datetime.strptime('20200110', '%Y%m%d') 
    print(start_time.day)
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y%m%d') 

    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y%m%d')   
    else: 
        end_time = start_time # plot one day

    print('---------------------------------------------------------------------------------------')
    print('Plotting data days between {} -----> {}'.format(start_time,end_time))
    print('---------------------------------------------------------------------------------------')
    print('You are plotting: \n{}\n{}\n{}'.format(speed_vars,dir_vars,temp_vars))
    print('---------------------------------------------------------------------------------------')
    print('')

    make_plots_pretty() # ... and higher resolution
    max_len_height_str = np.max(len(height_strs[:]))    

    day_series = pd.date_range(start_time, end_time) # we're going to loop over these days
    for today in day_series: # loop over the days in the processing range
        time_lims = (today, today+timedelta(1))
        print('----------now')
        print(time_lims)

        date_str  = today.strftime('%Y-%m-%d')
        curr_file = data_dir+head_str+'{}'.format(date_str)+tail_str
        try:
            dataset = netCDF4.Dataset(curr_file) 
        except:
            print(' !!! file {} not found for date {}'.format(curr_file,today))
            continue
        print(' ... plotting the date {} with file {} '.format(today,curr_file))

        # get datetime objects out of netcdf var, useful
        time_data  = dataset.variables['time']
        time_dates = netCDF4.num2date(time_data[:], time_data.units,\
                                      only_use_cftime_datetimes=False,only_use_python_datetimes=True)
        # the only_use declarations might only be required for the newest netcdf version...??

        df         = pd.DataFrame(index=time_dates) # put into a dataframe to be easily plotted
        for var in speed_vars + dir_vars + temp_vars:
            df[var] = dataset.variables[var]
            #print(dataset.variables[var]) # shows variable attributes of added variable

        df['time'] = time_dates # duplicates index... but it can be convenient
        df.sort_index(inplace=True)
        fig = plt.figure(figsize=(40,30))

        verboseprint('') 
        verboseprint(' ... data head :')
        verboseprint('================')
        verboseprint(df.head())
 
        ax1 = fig.add_subplot(311)
        h,l = ax1.get_legend_handles_labels()

        # legend_additions_1 = [] 
        i = 0 
        for var in speed_vars:
            df[var].plot(x='time')
            i = i+1
        # # add useful data info to legend
        # i = 0
        
        # for s in height_strs: print(l); l[i] = s + legend_additions_1[i]; i=i+1;

        ax1.legend(l, loc='best',facecolor='white',edgecolor='white')
        ax1.set_ylabel(speed_name+' ('+dataset.variables[var].units+')')
        ax1.set_xlim(time_lims) 
         
        # get style colors used for lines so that we can match them up for the pressure vars
        verboseprint('\nHere are the colors of your lines:')
        verboseprint('===================================')
        i = 0 
        colors = []
        for line in ax1.get_lines():
            verboseprint(' ... %s' % line.get_color())
            colors.append(line.get_color())
            i += 1

        ax2 = fig.add_subplot(312)
        i = 0 
        for var in dir_vars:
            df[var].plot()
            i = i+1

        # add useful data info to legend
        i = 0
        h,l = ax2.get_legend_handles_labels()
        #legend_additions_2 = []
        #for s in height_strs: l[i] = s + legend_additions_2[i]; i=i+1;

        ax2.legend(l, loc='best',facecolor='white',edgecolor='white')
        ax2.set_ylabel(dir_name+' ('+dataset.variables[var].units+')')
        ax2.set_xlim(time_lims)  # fix stupid edges that are wider than data, this used to work with datetime
        ax2.set_ylim((-20,380))
        ax2.set_yticks([0,90,180,270,360])

        ax3 = fig.add_subplot(313)

        i = 0 
        for var in temp_vars:
            df[var].plot()
            i = i+1

        # add useful data info to legend
        i = 0
        h,l = ax3.get_legend_handles_labels()
        #legend_additions_3 = []
        #for s in height_strs: l[i] = s + legend_additions_3[i]; i=i+1;

        ax3.legend(l, loc='best',facecolor='white',edgecolor='white')
        ax3.set_xlim(time_lims)  # fix stupid edges that are wider than data, this used to work with datetime
        ax3.set_ylabel(temp_name+' ('+dataset.variables[var].units+')')

        fig.text(0.43, 0.0001,'(plotted at {})'.format(today.today()))

        fig.tight_layout() # cut off white-space on edges
        fig.savefig('{}/{}_{}.png'.format(out_dir, plot_str, date_str))

        plt.close('all') # closes figure before looping again 

def make_plots_pretty():

    # mpl.rcParams['font.family'] = 'sans-serif'
    # mpl.rcParams['font.serif'] = ['Deja Vu Sans']
    # mpl.rcParams['font.sans-serif'] = ['Deja Vu Sans']

    plt.style.use('ggplot')
    #plt.style.use('seaborn-whitegrid')

    mpl.rcParams['lines.linewidth']     = 3
    mpl.rcParams['font.size']           = 22
    mpl.rcParams['legend.fontsize']     = 'xx-large'
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

