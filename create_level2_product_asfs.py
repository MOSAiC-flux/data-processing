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
# To create a uniform data product for the three "remote flux stations" (aka ASFS') at MOSAiC
# and to document the data processing workflow. At this time, this code only uses data from
# the SD cards. This will change if we're ever receiving data via radio/iridium and fail to
# recover an SD card.
#
# This code creates three different *daily* NetCDF files from raw observations by ASFS' at
# MOSAiC. "level2" files contain derived and quality controlled data products that are
# created using data from the "level1" product for each flux station. level2 files are
# created for both 1 minute and 10 minute averages. A "turbulent" data product is also
# created, using calculations researched and by a range of NOAA team members (named above)
#
# I've tried to optimize the software as best as possible to not waste your (or my) cpu
# cycles. Function calls are parallelized/threaded when possible and this software occupies
# 4 cores most of the time it is running. But, it's entirely I/O limited and so it runs much
# faster on my NVME based laptop than it does on the rusty disked server at NOAA.
# 
# Descriptions of the three different output files and their contents:
# (look at "asfs_data_definitions.py" for detailed product description)
# #########################################################################
#
# level2 (10 and 1 minute averages): 
#
#       This is the first QCed derived science product to be used in analyses, contains
#       the basic scientific params at specified intervals.
#
# turbulent (calculated over 30 minute configurable window):
#
#       Based on Andrey Grachev's matlab code, the turbulent product includes all
#       relevant parameters created while calculatinghe fluxes, including the final results.
# 
# HOWTO:
#
# To run this package with verbose printing over all of the data:
# ./create_level2_product_asfs.py -v -s 20191005 -e 20201005 -p /psd3data/arctic/
#
# To profile the code and see what's taking so long:
# python3 -m cProfile -s cumulative ./create_level2_product_asfs.py etc etc -v -s 20191201 -e 20191201 
#
# ###############################################################################################
#
# look at these files for documentation on netcdf vars and nomenclature
# as well as additional information on the syntax used to designate certain variables here
from asfs_data_definitions import define_global_atts, define_level2_variables, define_turb_variables, define_qc_variables
from asfs_data_definitions import define_level1_slow, define_level1_fast, define_10hz_variables

from qc_level2 import qc_asfs_winds, qc_stations, qc_asfs_turb_data
from get_data_functions import get_flux_data, get_arm_radiation_data

import functions_library as fl # includes a bunch of helper functions that we wrote

# Ephemeris
# SPA is NREL's (Ibrahim Reda's) emphemeris calculator that all those BSRN/ARM radiometer geeks use ;) 
# pvlib is NREL's photovoltaic library
from pvlib import spa 
    # .. [1] I. Reda and A. Andreas, Solar position algorithm for solar radiation
    #    applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.

    # .. [2] I. Reda and A. Andreas, Corrigendum to Solar position algorithm for
    #    solar radiation applications. Solar Energy, vol. 81, no. 6, p. 838,
    #    2007.

import os, inspect, argparse, time, sys, socket

global nthreads 
hostname = socket.gethostname()
if '.psd.' in hostname:
    if hostname.split('.')[0] in ['linux1024', 'linux512']:
        nthreads = 25  # the twins have 32 cores/64 threads, won't hurt if we use <30 threads
    elif hostname.split('.')[0] in ['linux64', 'linux128', 'linux256']:
        nthreads = 12  # 
    else:
        nthreads = 90  # the new compute is hefty.... real hefty

else: nthreads = 8     # laptops don't tend to have 12  cores... yet

from multiprocessing import Process as P
from multiprocessing import Queue   as Q

# need to debug something? this makes useful pickle files in ./tests/ ... uncomment below if you want to kill threading
we_want_to_debug = True
if we_want_to_debug:

    # from multiprocessing.dummy import Process as P
    # from multiprocessing.dummy import Queue   as Q
    # nthreads = 1
    try: from debug_functions import drop_me as dm
    except: you_dont_care=True
     
import numpy  as np
import pandas as pd
import xarray as xr

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from datetime  import datetime, timedelta
from numpy     import sqrt
from scipy     import stats
from netCDF4   import Dataset, MFDataset, num2date

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....


version_msg = '\n\nPS-122 MOSAiC Flux team ASFS processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)

def main(): # the main data crunching program

    # the UNIX epoch... provides a common reference, used with base_time
    global epoch_time
    epoch_time        = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers

    global integ_time_turb_flux
    integ_time_turb_flux = [10]                  # [minutes] the integration time for the turbulent flux calculation
    calc_fluxes          = True                     # if you want to run turbulent flux calculations and write files

    global verboseprint  # defines a function that prints only if -v is used when running
    global printline     # prints a line out of dashes, pretty boring
    global verbose       # a useable flag to allow subroutines etc when using -v 
    global tilt_data     # some variables seem to be unavailable when others defined similarly are ...????
    
    # constants for calculations
    global nan, def_fill_int, def_fill_flt # make using nans look better
    nan = np.NaN
    def_fill_int = -9999
    def_fill_flt = -9999.0

    Rd       = 287     # gas constant for dry air
    K_offset = 273.15  # convert C to K
    h2o_mass = 18      # are the obvious things...
    co2_mass = 44      # ... ever obvious?
    sb       = 5.67e-8 # stefan-boltzmann
    emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

    global version  # names directory where data will be written
    global lvlname  # will appear in filename
    lvlname = 'level2.4' 

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over all the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')
    parser.add_argument('-p', '--path', metavar='str', help='base path of data location, up to andincluding /data/, include trailing slash') 
    parser.add_argument('-a', '--station', metavar='str',help='asfs#0, if omitted all will be procesed')
    parser.add_argument('-pd', '--pickledir', metavar='str',help='want to store a pickle of the data for debugging?')
    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    
    args         = parser.parse_args()
    verbose      = True if args.verbose else False # use this to run segments of code via v/verbose flag
    v_print      = print if verbose else lambda *a, **k: None     # placeholder
    verboseprint = v_print # use this function to print a line if the -v/--verbose flag is provided
    
    global data_dir, in_dir, out_dir # make data available
    if args.path: data_dir = args.path
    else: data_dir = '/Projects/MOSAiC/'

    leica_dir = '/Projects/MOSAiC_internal/partner_data/AWI/polarstern/WXstation/' # this is where the ship track lives 
    arm_dir   = '/Projects/MOSAiC_internal/partner_data/'
    
    if args.station: flux_stations = args.station.split(',')
    else: flux_stations = ['asfs30', 'asfs40', 'asfs50']
 
    if args.pickledir: pickle_dir=args.pickledir
    else: pickle_dir=False
        
    def printline(startline='',endline=''):
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

    print('The first day of data we will process data is:     %s' % str(start_time+timedelta(1)))
    print('The last day we will process data is:              %s\n\n' % str(end_time-timedelta(1)))
    printline()

    # thresholds! limits that can warn you about bad data!
    # these aren't used yet but should be used to warn about spurious data
    lat_thresh        = (70   ,90)       # limits area where station
    hdg_thresh_lo     = (0    ,360)      # limits on gps heading
    irt_targ_lo       = (-80  ,5)        # IRT surface brightness temperature limits [Celsius]
    sr50d             = (1    ,2.5)      # distance limits from SR50 to surface [m]; install height -1 m or +0.5
    sr50_qc           = (152  ,300)      # reported "quality numbers" 0-151=can't read dist;
                                         # 210-300=reduced signal; 300+=high uncertainty
    irt_targ          = (-80  ,5)        # IRT surface brightness temperature limits [Celsius]
    flxp              = (-120 ,120)      # minimum and maximum conductive heat flux (W/m2)
    T_thresh          = (-70  ,20)       # minimum & maximum air temperatures (C)
    rh_thresh         = (55   ,110)      # relative humidity (#)
    p_thresh          = (900  ,1100)     # air pressure
    ws_thresh         = (0    ,40)       # wind speed from sonics (m/s)
    lic_co2sig_thresh = (94   ,105)      # rough estimate of minimum CO2 signal value corresponding to
                                         # optically-clean window. < 90 = needs cleaned (e.g., salt residue); < ~80?? = ice!
    lic_h2o           = (1e-3 ,10)       # Licor h2o [mg/m3]
    lic_co2           = (600  ,1000)     # Licor co2 [g/m3]
    max_bad_paths     = (0.01 ,1)        # METEK: maximum [fraction] of bad paths allowed. (0.01 = 1%), but is
                                         # actually in 1/9 increments. This just says we require all paths to be usable.
    incl_range        = (-90  ,90)       # The inclinometer on the metek
    met_t             = T_thresh         # Vaisala air temperature [C]
    met_rh            = rh_thresh        # Vaisala relative humidity [#]
    met_p             = p_thresh         # Vaisala air pressure [hPa or ~mb]
    alt_lim           = (-5.1,10.1)      # largest range of +/- 3sigma on the altitude data between the stations
    cd_lim            = (-2.3e-3,1.5e-2) # drag coefficinet sanity check. really it can't be < 0, but a small negative
                                         # threshold allows for empiracally defined (from EC) 3 sigma noise distributed about 0.

                                         # QCRAD thresholds & coefficents    
    sw_range          = (-4   ,1000)     # SWD & SWU max [Wm^2]
    lw_range          = (50  ,400)       # LWD & LWU max [Wm^2] 
    D1                = 1.15             # SWD CCL for Alert, which seems to work well here too (less data than climatology to check against!)
    D5                = 0.9              # SWU. Bumbed up a little from 0.88 used at Alert.
    D11               = 0.62             # LWD<->Tair low (bumped up from 0.58 at Alert)
    D12               = 23               # LWD<->Tair high (Alert)
    D13               = 8                # LWU<->Tair Low side. A lot stricter than Alert; I think the tighter LWU is because of the consitent
                                         # surface type relatve to the land site
    D14               = 8                # LWU<->Tair High side. A lot stricter than Alert; 
    D15               = 120              # LWU <-> LWD test. Low side. Stricter than Alert, as with above.
    D16               = 20               # LWU <-> LWD test. High side. As at Alert.
    A0                = 1                # albedo limit

    # official "start" times, defined as EFOY-on on install day per Station Book
    station_initial_start_time = {}
    station_initial_start_time['asfs30'] = datetime(2019,10,7,2,14,0) 
    station_initial_start_time['asfs40'] = datetime(2019,10,5,5,15,0)
    station_initial_start_time['asfs50'] = datetime(2019,10,10,10,49,0) 
    
    # Load the ship track and reindex to slow_data, calculate distance [m] and bearing [deg from tower rel to true north, as wind direction]
    ship_df = pd.read_csv(leica_dir+'Leica_Sep20_2019_Oct01_2020_clean.dat',sep='\s+',parse_dates={'date': [0,1]}).set_index('date')          
    ship_df.columns = ['u1','lon_ew','latd','latm','lond','lonm','u2','u3','u4','u5','u6','u7']
    ship_df['lat']=ship_df['latd']+ship_df['latm']/60

    # 9 is a missing value in the original file. when combined from above line 9+9/60=9.15 is the new missing data
    ship_df['lat'].mask(ship_df['lat'] == 9+9/60, inplace=True) 
    ship_df['lon']=ship_df['lond']+ship_df['lonm']/60
    ship_df['lon'].mask(ship_df['lon'] == 9+9/60, inplace=True) 
    ship_df['lon'] = ship_df['lon']*ship_df['lon_ew'] # deg west will be negative now

    # ###################################################################################################
    # various calibration params
    
    init_asfs30 = pd.DataFrame()
    init_asfs40 = pd.DataFrame()
    init_asfs50 = pd.DataFrame()
      
                                                                       # ASFS 30 ---------------------------
    init_asfs30['init_date']  = [
                                station_initial_start_time['asfs30'],  # L2 distance (201.8 cm) and 2-m Tvais (-7.75 C) at 0430 UTC Oct 7, 2019
                                datetime(2020,4,7,0,0),                # LOG
                                datetime(2020,4,15,12),                # Balloon Town
                                datetime(2020,5,5,0),                  # BGC1LOG
                                datetime(2020,5,7,11,37),              # BGC1
                                datetime(2020,6,30,15,49),             # L2
                                datetime(2020,7,14,13,10),             # settling, reset
                                datetime(2020,8,2,14,20),              # Back on board
                                datetime(2020,8,21,16,30),             # Met City
                                datetime(2020,9,4,10,18),              # Hinterland Pond
                                datetime(2020,9,19,10,33),             # Remote Sensing
                                datetime(2020,9,20,4,53),              # Back on board
                                datetime(2020,9,24,5,16),              # Ice Station 1
                                datetime(2020,9,26,6,20),              # Ice Station 2
                                datetime(2020,9,30,7,50),              # Ice Station 3
                                datetime(2020,10,1,0,0)                # end
                                ]
        
    init_asfs30['init_dist']  = [
                                sqrt((-7.75+K_offset)/K_offset)*201.8, # L2 distance (201.8 cm) and 2-m Tvais (-7.75 C) at 0430 UTC Oct 7, 2019 
                                nan,                                   # LOG
                                sqrt((-17.9+K_offset)/K_offset)*206.9, # Ballooon Town
                                nan,                                   # BGC1LOG
                                sqrt((-9.7+K_offset)/K_offset)*192.7,  # BGC1
                                sqrt((-0.2+K_offset)/K_offset)*208.8,  # L2
                                sqrt((-1.2+K_offset)/K_offset)*228.4,  # settling, reset
                                nan,                                   # Back on board
                                sqrt((-0.3+K_offset)/K_offset)*203.2,  # Met City
                                sqrt((-0.9+K_offset)/K_offset)*205.4,  # Hinterland Pond
                                nan,                                   # Remote Sensing
                                nan,                                   # Back on board
                                nan,                                   # Ice Station 1
                                nan,                                   # Ice Station 2
                                nan,                                   # Ice Station 3
                                nan                                    # end
                                ]
        
    init_asfs30['init_depth'] = [
                                8.3,            # L2 distance (201.8 cm) and 2-m Tvais (-7.75 C) at 0430 UTC Oct 7, 2019 
                                nan,            # LOG
                                66,             # Balloon Town
                                nan,            # BGC1LOG
                                36.1,           # BGC1. last snow depth from asfs50 sr50 in this spot on 5/7...for continuity
                                0,              # L2. Depth reported as difficult to quantify in melting state
                                -13.14,         # settling, reset
                                nan,            # Back on board
                                0,              # Met City
                                0,              # Hinterland Pond
                                nan,            # Remote Sensing
                                nan,            # Back on board
                                nan,            # Ice Station 1
                                nan,            # Ice Station 2
                                nan,            # Ice Station 3
                                nan             # end
                                ]    
        
    init_asfs30['init_loc']   = [
                                'L2',           # L2 distance (201.8 cm) and 2-m Tvais (-7.75 C) at 0430 UTC Oct 7, 2019 
                                'LOG',          # LOG
                                'Balloon_Town', # Ballooon Town
                                'BGC1LOG',      # BGC1LOG
                                'BGC1',         # BGC1
                                'L2',           # L2
                                'L2',           # settling, reset
                                'PS',           # Back on board
                                'MC',           # Met City
                                'HP',           # Hinterland Pond
                                'RS',           # Remote Sensing
                                'PS',           # Back on board
                                'IS1',          # Ice Station 1
                                'IS2',          # Ice Station 2
                                'IS3',          # Ice Station 3 
                                'PS'            # end
                                ]       


                                                                      # ASFS 40 ---------------------------
    init_asfs40['init_date']  = [
                                station_initial_start_time['asfs40'],  # L1 921 UTC Oct 5, 2019
                                datetime(2019,12,22,8,43),             # Discontinuity in SR50 during site visit ...resetting
                                datetime(2020,3,1,0,0)                 # end 
                                ]
        
    init_asfs40['init_dist']  = [
                                sqrt((-6.8+K_offset)/K_offset)*212,   # L1 distance (212 cm) and 2-m Tvais (-6.8 C) at 921 UTC Oct 5, 2019
                                sqrt((-28.4+K_offset)/K_offset)*219.7, # Discontinuity in SR50 during site visit ...resetting
                                nan                                    # end
                                ]
        
    init_asfs40['init_depth'] = [
                                8.3,                                   # L1 distance (214.9 cm) and 2-m Tvais (-13.9 C) at 921 UTC Oct 5, 2019
                                10.4,                                  # Discontinuity in SR50 during site visit ...resetting
                                nan                                    # end
                                ]    
        
    init_asfs40['init_loc']   = [
                                'L1',                                  # L2 distance (201.8 cm) and 2-m Tvais (-7.75 C) at 0430 UTC Oct 7, 2019 
                                'L1',                                  # Discontinuity in SR50 during site visit ...resetting
                                'NA'                                   # end
                                ]       


    
                                                                       # ASFS 50 ---------------------------
    init_asfs50['init_date']  = [
                                station_initial_start_time['asfs50'],  # L3 distance (213.3 cm) and 2-m Tvais (-10.1 C) at 0400 UTC Oct 10, 2019
                                datetime(2020,4,4,0,0),                # LOG
                                datetime(2020,4,14,12,45),             # BGC1
                                datetime(2020,6,24,0),                 # LOG
                                datetime(2020,6,29,13,0),              # FYI - First Year Ice
                                datetime(2020,7,10,12,20),             # FYI, same as before but moved a few feet and re-initialized
                                datetime(2020,7,30,13,40),             # Back on board
                                datetime(2020,8,21,15,0),              # ASFS50 Leg 5 position at CO Lead Site
                                datetime(2020,9,19,9,46),              # Remote Sensing Site
                                datetime(2020,9,20,4,50),              # Back on board
                                datetime(2020,9,26,6,20),              # Ice Station 2
                                datetime(2020,9,30,7,50),              # Ice Station 3
                                datetime(2020,10,1,0,0)                # end
                                ]
        
    init_asfs50['init_dist']  = [
                                sqrt((-10.1+K_offset)/K_offset)*213.3, # L3 distance (213.3 cm) and 2-m Tvais (-10.1 C) at 0400 UTC Oct 10, 2019
                                nan,                                   # LOG
                                sqrt((-17.7+K_offset)/K_offset)*198.6, # BGC1
                                nan,                                   # LOG
                                nan,                                   # FYI - First Year Ice
                                sqrt((0+K_offset)/K_offset)*208.0,     # FYI - First Year Ice 
                                nan,                                   # Back on board
                                sqrt((-0.3+K_offset)/K_offset)*202.9,  # ASFS50 Leg 5 position at CO Lead Site
                                nan,                                   # Remote Sensing Site
                                nan,                                   # Back on board
                                nan,                                   # Ice Station 2
                                nan,                                   # Ice Station 3
                                nan                                    # end
                                ]
                                
        
    init_asfs50['init_depth'] = [
                                6.5,                                   # L3 distance (213.3 cm) and 2-m Tvais (-10.1 C) at 0400 UTC Oct 10, 2019
                                nan,                                   # LOG
                                32,                                    # BGC1
                                nan,                                   # LOG
                                nan,                                   # FYI - First Year Ice. Depth reported not quantifiable in melting state.
                                5,                                     # FYI - First Year Ice. "soft-to-hard interface was 5cm down"
                                nan,                                   # Back on board
                                0,                                     # ASFS50 Leg 5 position at CO Lead Site 
                                nan,                                   # Remote Sensing Site
                                nan,                                   # Back on board
                                nan,                                   # Ice Station 2
                                nan,                                   # Ice Station 3
                                nan                                    # end
                                ]    
        
    init_asfs50['init_loc']   = [
                                'L3',                                  # L3 distance (213.3 cm) and 2-m Tvais (-10.1 C) at 0400 UTC Oct 10, 2019
                                'LOG',                                 # LOG
                                'BGC1',                                # BGC1
                                'LOG',                                 # LOG  
                                'FYI',                                 # FYI - First Year Ice
                                'FYI',                                 # FYI - First Year Ice
                                'PS',                                  # Back on board
                                'COlead',                              # ASFS50 Leg 5 position at CO Lead Site
                                'RS',                                  # Remote Sensing Site 
                                'PS',                                  # Back on board
                                'IS2',                                 # Ice Station 2
                                'IS3',                                 # Ice Station 3
                                'PS'                                   # end
                                ]       
    
    # Set the index
    init_asfs30.set_index(init_asfs30['init_date'],inplace=True)
    init_asfs40.set_index(init_asfs40['init_date'],inplace=True)
    init_asfs50.set_index(init_asfs50['init_date'],inplace=True)

    init_data = {}
    init_data['asfs30'] = init_asfs30
    init_data['asfs40'] = init_asfs40
    init_data['asfs50'] = init_asfs50
    
    # Metadata for the radiometer tilt correction. We need a priori (i.e., when level prior to change in orientation) knowledge 
    # of the offsets between Metek inclinometer and SWD. Dates are begining of period and values should be persisted until the 
    # next date. nan signifies no correction should be performed.
                     
    asfs30_tilt_data = pd.DataFrame(np.array([ # date               IncX_offset IncY_offset  
                                            [datetime(2019,10,1,0,0),    nan,     nan], # Beg. MOSAiC in the dark. No corrections until spring!
                                            [datetime(2020,3,22,4,48),   nan,     nan], # Leg 3; tilts logging turned on. L2. rads level so no correction
                                            [datetime(2020,4,7,12,0),    nan,     nan], # Leg 3; LOG, no correction
                                            [datetime(2020,4,15,12,25),  nan,     nan], # Leg 3; Balloon Town install. rads level no correction
                                            [datetime(2020,5,5,8,29),    nan,     nan], # Leg 3; LOG, EFOY tests in BGC1 rd
                                            [datetime(2020,5,7,11,37),   nan,     nan], # Leg 3; to BGC1. rads level no correction
                                            [datetime(2020,5,12,22,16),  nan,     nan], # Leg 3; BGC1 reequillibrates after braking in storm. rads remain level. no correction
                                            [datetime(2020,5,26,0,0),    0.0298, -0.7043], # Leg 3; BGC1 melt onset
                                            [datetime(2020,6,21,8,8),    nan,     nan], # Leg 4; sled being moved. no correction 
                                            [datetime(2020,6,21,8,27),   0.3285, -1.9358], # Leg 4; releveled at BGC1
                                            [datetime(2020,6,30,15,51),  0.0776, -0.2305], # Leg 4; FYI
                                            [datetime(2020,7,14,13,11), -0.1341, -0.0376], # Leg 4; FYI, reset
                                            [datetime(2020,8,2,18,0),    nan,     nan], # Leg 4; PS deck, no correction
                                            [datetime(2020,8,21,16,35),  0.9804, -0.6325], # Leg 5; tower location
                                            [datetime(2020,8,31,5,7),    nan,     nan], # Leg 5; ASFS being moved, no correction 
                                            [datetime(2020,8,31,5,29),   nan,     nan], # Leg 5; tower location, reset. installed out of level so cant be corrected
                                            [datetime(2020,9,4,9,16),    nan,     nan], # Leg 5; ASFS being moved, no correction
                                            [datetime(2020,9,4,11,18),   nan,     nan], # Leg 5; icing. Hinterland. rads level so no correction
                                            [datetime(2020,9,19,8,45),   nan,     nan], # Leg 5; sledge intercomparison. brief. little chang in level. no correction
                                            [datetime(2020,9,20,4,51),   nan,     nan], # Leg 5; PS deck, no correction
                                            [datetime(2020,9,24,5,15),   0.1248,  1.0505], # Leg 5; Ice Stn 1 transect
                                            [datetime(2020,9,24,11,57),  nan,     nan], # Leg 5; PS deck, no correction
                                            [datetime(2020,9,26,5,18),   0.4665,  0.5202], # Leg 5; Ice Stn 2 transect
                                            [datetime(2020,9,26,10,59),  nan,     nan], # Leg 5; PS deck, no correction
                                            [datetime(2020,9,30,8,38),   1.1053,  0.3600], # Leg 5; Ice Stn 3 transect
                                            [datetime(2020,9,30,14,3),   nan,     nan], # Leg 5; PS deck, no correction
                                            [datetime(2020,10,5,0,0),    nan,     nan], # End.
                                            ]),columns=['date', 'incx_offset', 'incy_offset'])

    asfs30_tilt_data.set_index(asfs30_tilt_data['date'],inplace=True)
    
    asfs40_tilt_data = pd.DataFrame(np.array([ # date               IncX_offset IncY_offset  
                                            [datetime(2019,10,1,0,0),    nan,     nan], # Beg. MOSAiC in the dark. No corrections until spring!
                                            [datetime(2020,10,5,0,0),    nan,     nan], # End.
                                            ]),columns=['date', 'incx_offset', 'incy_offset'])
    
    asfs40_tilt_data.set_index(asfs40_tilt_data['date'],inplace=True)
                    
    asfs50_tilt_data = pd.DataFrame(np.array([ # date               IncX_offset IncY_offset  
                                            [datetime(2019,10,1,0,0),    nan,     nan], # Beg. MOSAiC in the dark. No corrections until spring!
                                            [datetime(2020,4,7,13,12),   nan,     nan], # Leg 3; LOG. no correction
                                            [datetime(2020,4,14,12,45),  nan,     nan], # Leg 3; BGC1. rads level so no correction
                                            [datetime(2020,4,15,0,0),    nan,     nan], # Leg 3; BGC1 reset. rads level so no correction
                                            [datetime(2020,5,7,11,23),   nan,     nan], # Leg 3; instrument off and stored. no correction
                                            [datetime(2020,6,15,11,45), -0.4499, -3.6961], # Leg 4; PS deck. correctable so why not?
                                            [datetime(2020,6,25,7,29),   nan,     nan], # Leg 4; LOG. no correction
                                            [datetime(2020,6,29,12,49), -0.0585, -0.4529], # Leg 4; FYI install. SPN1 nearby
                                            [datetime(2020,7,4,12,39),  -0.0821,  0.0843], # Leg 4; FYI reset. SPN1 nearby
                                            [datetime(2020,7,4,13,39),  -0.0523, -0.0108], # Leg 4; FYI reset. SPN1 nearby
                                            [datetime(2020,7,10,11,30),  nan,     nan], # Leg 4; FYI reset. rads level so no correction
                                            [datetime(2020,7,30,14,30),  nan,     nan], # Leg 4; PS deck. no correction
                                            [datetime(2020,8,22,23,58),  1.3793, -0.8614], # Leg 5; installed 8/21, but data available now. 
                                            [datetime(2020,8,31,6,8),    nan,     nan], # Leg 5; reset
                                            [datetime(2020,9,1,11,31),   nan,     nan], # Leg 5; reset
                                            [datetime(2020,9,14,5,48),   nan,     nan], # Leg 5; reset
                                            [datetime(2020,9,19,9,44),   nan,     nan], # Leg 5; sled being moved for extend period. no correction
                                            [datetime(2020,9,19,10,13),  nan,     nan], # Leg 5; sled/sledge intercomparison
                                            [datetime(2020,9,20,8,8),    nan,     nan], # Leg 5; PS deck. no correction
                                            [datetime(2020,9,26,6,2),    nan,     nan], # Leg 5; Ice Stn 2
                                            [datetime(2020,9,26,6,15),   nan,     nan], # Leg 5; Ice Stn 2, sled being moved about. no correction
                                            [datetime(2020,9,26,6,50),   nan,     nan], # Leg 5; Ice Stn 2
                                            [datetime(2020,9,26,11,11),  nan,     nan], # Leg 5; PS deck. no correction
                                            [datetime(2020,9,30,8,29),   nan,     nan], # Leg 5; Ice Stn 3
                                            [datetime(2020,9,30,8,44),   nan,     nan], # Leg 5; Ice Stn 3, sled being moved about. no correction
                                            [datetime(2020,9,30,8,51),   nan,     nan], # Leg 5; Ice Stn 3
                                            [datetime(2020,9,30,14,11),  nan,     nan], # Leg 5; PS deck. no correction
                                            [datetime(2020,10,5,0,0),    nan,     nan], # End.
                                            ]),columns=['date', 'incx_offset', 'incy_offset'])
    
    asfs50_tilt_data.set_index(asfs50_tilt_data['date'],inplace=True)
    
    tilt_data = {}
    tilt_data['asfs30'] = asfs30_tilt_data
    tilt_data['asfs40'] = asfs40_tilt_data
    tilt_data['asfs50'] = asfs50_tilt_data
 
    # program logic starts here, the logic flow goes like this:
    # #########################################################
    # 
    #     1) read in all days of slow data from netcdf level 1 files
    #     2) loop over days requested
    #     3) for each day, pull in fast data from netcdf level 1 files
    #     5) for each day, apply strict QC and derive desired products in level2 definitions
    #     6) for each day, write level2 netcdf files
    #     7) if desired, using QCed observations, produce turbulent flux data product
    #     8) all done
    #
    # ... here we go then
    # ##########################################################################################

    print("Getting data from level1 netcdf files for stations: {}!!".format(flux_stations))
    print("   and doing it in threads, hopefully this doesn't burn your lap")
    printline()

    # getting the "slow" raw/level1 data is done here, heavy lifting is in "get_slow_data()" 
    # the slow dataset is small, so we load it all at once, the fast has to be done for each day
    # ##########################################################################################
    # dataframes are in dicts with station name keys, parallellizing data ingesting, saves time.
    slow_data   = {}
    slow_atts   = {}
    slow_vars   = {}

    slow_q_dict = {}
    slow_atts_from_definitions, slow_vars_from_definitions = define_level1_slow()

    print(f"Retreiving data from netcdf files... {data_dir}")
    for curr_station in flux_stations:
    
        in_dir = data_dir+'/'+curr_station+'/1_level_ingest_'+curr_station+'/'      # where does level 1 data live?
        df_station, code_version = get_flux_data(curr_station, start_time, end_time, 1,
                                                 data_dir, 'slow', verbose, nthreads, False, pickle_dir)
        slow_data[curr_station] = df_station

        printline()
        # verboseprint("\n===================================================")
        # verboseprint("Data and observations provided by {}:".format(curr_station))
        # verboseprint('===================================================')
        # if verbose: slow_data[curr_station].info(verbose=True) # must be contained; 

    # get the diffuse flux from ARM. If ARM is missing or if the station is > 2 km away from the CO (i.e., an L-site), then parameterize it
    arm_data, arm_version = get_arm_radiation_data(start_time, end_time, arm_dir, verbose, nthreads, pickle_dir)
    arm_data = arm_data.sort_index(); 
    arm_data = arm_data.drop_duplicates(); 

    print("\n\nRetreived slow/ARM data for all stations, moving on to fast data and daily processing.\n\n")
    printline()


    # mention big data gaps, good sanity check, using battvolt, because if battery voltage is missing...
    if verbose: 
        for curr_station in  flux_stations:
            curr_slow_data = slow_data[curr_station]

            try: 
                bv = curr_slow_data["batt_volt_Avg"]
            except:
                print(f"\n No data for {curr_station} for your requested range\n")
            threshold   = 60 # warn if the station was down for more than 60 minutes
            nan_groups  = bv.isnull().astype(int).groupby(bv.notnull().astype(int).cumsum()).cumsum()
            mins_down   = np.sum( nan_groups > 0 )

            prev_val   = 0 
            if np.sum(nan_groups > threshold) > 0:
                perc_down = round(((bv.size-mins_down)/bv.size)*100, 3)
                print(f"\nFor your time range, the {curr_station} was down for a total of {mins_down} minutes...")
                print(f"... which gives an uptime of approx {perc_down}% over the period data exists")

            else:
                print("\nStation {} was alive for the entire time range you requested!! Not bad... "
                      .format(curr_station, threshold))

    # first rename some columns to something we like better in way that deletes the old version
    # so we make sure not to perform operations on the wrong version below
                        # old name              : new name
    for curr_station in  flux_stations:
        slow_data[curr_station].rename(columns={'sr50_dist_Avg'         : 'sr50_dist'               , \
                                                'vaisala_P_Avg'         : 'atmos_pressure'          , \
                                                'vaisala_T_Avg'         : 'temp'                    , \
                                                'vaisala_Td_Avg'        : 'dew_point'               , \
                                                'vaisala_RH_Avg'        : 'rh'                      , \
                                                'apogee_body_T_Avg'     : 'body_T_IRT'              , \
                                                'apogee_targ_T_Avg'     : 'brightness_temp_surface' , \
                                                'fp_A_Wm2_Avg'          : 'subsurface_heat_flux_A'  , \
                                                'fp_B_Wm2_Avg'          : 'subsurface_heat_flux_B'  , \
                                                'licor_h2o_Avg'         : 'h2o_licor'               , \
                                                'licor_co2_Avg'         : 'co2_licor'               , \
                                                'licor_co2_str_out_Avg' : 'co2_signal_licor'        , \
                                                'sr30_swd_IrrC_Avg'     : 'down_short_hemisp'       , \
                                                'sr30_swu_IrrC_Avg'     : 'up_short_hemisp'         , \
                                                },inplace=True)
    
    ########################################  # # Process the GPS # #  #############################################
    # I'm going to do all the gps qc up front mostly because I need to smooth the heading before we split individual days  
    print('\n---------------------------------------------------------------------------------------------\n')            
    def process_gps(curr_station, sd, ship_df):
  
        # Get the current station's initialzation dataframe. ...eval...sorry, it had to be
        init_data[curr_station] = init_data[curr_station].reindex(method='pad',index=sd.index)
        print('Processing GPS: qc, calculations, and band-pass median filter applied to heading for '+curr_station) 

        # convert to degrees
        try: 
            sd['lat']     = sd['gps_lat_deg_Avg'] + sd['gps_lat_min_Avg']/60.0 # add decimal values
        except KeyError as e: 
            print(f"!!! No GPS data for station {curr_station} during requested time range !!! ")
            return (sd, False)

        sd['lon']     = sd['gps_lon_deg_Avg']+sd['gps_lon_min_Avg']/60.0
        sd['heading'] = sd['gps_hdg_Avg']

        # QC, infinities->nan
        sd['heading'] = sd['heading'].where(~np.isinf(sd['heading'])) 

        sd['gps_alt_Avg']     .mask( (sd['gps_alt_Avg']<alt_lim[0]) | (sd['gps_alt_Avg']>alt_lim[1]), inplace=True) # stat lims
        sd['lat']     .mask( (sd['gps_qc']==0) | (sd['gps_hdop_Avg']>4), inplace=True) 
        sd['lon']     .mask( (sd['gps_qc']==0) | (sd['gps_hdop_Avg']>4), inplace=True) 
        sd['gps_alt_Avg']     .mask( (sd['gps_qc']==0) | (sd['gps_hdop_Avg']>4), inplace=True) 
        sd['heading'] .mask( (sd['gps_qc']==0) | (sd['gps_hdop_Avg']>4), inplace=True) 

        # infrequent hiccups sneak through. not sure of the origin, but we can
        # easily filter, replace spikes outside 0.01 deg over 2 min interp
        sd['lat'] = fl.despike(sd['lat'],0.01,24,'no').interpolate(limit=15)  
        sd['lon'] = fl.despike(sd['lon'],0.01,24,'no').interpolate(limit=15) 
        
        # since we have altitude data, lets make it somewhat useful and correct to reference the ice surface
        # 2.228 is what I think the distance is from the top of the plywood to the gps sensor
        sd['ice_alt'] = sd['gps_alt_Avg'] - (2.228 +  init_data[curr_station]['init_depth']/100) 
        
        # !! Important !!
        # The v102 gps is mounted perpendicualr to the berm, but "station north", which is the sonic
        # orientation is defined along the boom. the gps is mount 90 degrees to the left of sonic-north.
        sd['heading'] = np.mod(sd['heading']+90,360)     
        
        # The heading/alt from the v102 is "noisey" at regular frequencies, about ~1, 2.1, 6.4, and 12.8
        # hours. I've considered several approaches: wavelet frequency rejection, various band-pass filters,
        # Kalman filter, tower->ais bearing baseline. Median filter works the best. J. Hutchings results indicate
        # that the 12 hour signal is tidal - throughout the year! - so it shuld be retained. So, we implement 
        # a 6 hour running median filter. I have implemented a 1 day buffer on the start_time, end_time for
        # this. For missing data we forward pad to reduce edge effects but report nan in the padded space.
        
        # The filter needs to be carried out in vector space. the filter is 6 hrs = 360 min
        unitv1 = np.cos(np.radians(sd['heading'])) # degrees -> unit vector
        unitv2 = np.sin(np.radians(sd['heading'])) # degrees -> unit vector
        unitv1 = unitv1.interpolate(method='pad').rolling(360,min_periods=1,center=True).median() # filter the unit vector
        unitv2 = unitv2.interpolate(method='pad').rolling(360,min_periods=1,center=True).median() # filter the unit vector
        tmph = np.degrees(np.arctan2(-unitv2,-unitv1))+180 # back to degrees
        tmph.mask(sd['heading'].isna(),inplace=True)
        sd['heading'] = tmph
        tmpa = sd['ice_alt'].interpolate(method='pad').rolling(360,min_periods=1,center=True).median()
        tmpa.mask(sd['ice_alt'].isna(),inplace=True)
        sd['ice_alt'] = tmpa
                  
        # Get the bearing on the ship
        ship_df = ship_df.reindex(sd.index)
        sd['ship_distance'] = fl.distance_wgs84(sd['lat'],sd['lon'],ship_df['lat'],ship_df['lon'])
        sd['ship_bearing']  = fl.calculate_initial_angle_wgs84(sd['lat'],sd['lon'],ship_df['lat'],ship_df['lon'])
        sd['ship_distance'] = fl.despike(sd['ship_distance'],2,15,'yes')   # tiny spikes in lat/lon resulting in 
        sd['ship_bearing']  = fl.despike(sd['ship_bearing'],0.02,15,'yes') # spikes of ~5 m in distance, so despike

        return (sd, True)

    # IR20  radiometer calibration coefficients
    coef_S_down = {'asfs30': 12.15/1000 , 'asfs40' : 9.52/1000 , 'asfs50' : 11.42/1000} 
    coef_a_down = {'asfs30': -16.36e-6  , 'asfs40' : -15.75e-6 , 'asfs50' : -16.05e-6}  
    coef_b_down = {'asfs30':2.62e-3     , 'asfs40' : 2.53e-3   , 'asfs50' : 2.57e-3}    
    coef_c_down = {'asfs30':0.9541      , 'asfs40' : 0.9556    , 'asfs50' : 0.9551}     

    coef_S_up = {'asfs30': 12.48/1000 , 'asfs40' : 8.99/1000 , 'asfs50' : 12.01/1000} 
    coef_a_up = {'asfs30': -16.25e-6  , 'asfs40' : -16.96e-6 , 'asfs50' : -16.58e-6}  
    coef_b_up = {'asfs30': 2.62e-3    , 'asfs40' : 2.30e-3   , 'asfs50' : 2.49e-3}    
    coef_c_up = {'asfs30': 0.9541     , 'asfs40' : 0.9608    , 'asfs50' : 0.9568}     

    # actually call the gps functions and recalibrate LW sensors, minor adjustments to plates
    for curr_station in flux_stations:
        slow_data[curr_station], return_status = process_gps (curr_station, slow_data[curr_station], ship_df)
        station_data = slow_data[curr_station]
   
        c_Sd =coef_S_down[curr_station]
        c_ad =coef_a_down[curr_station] 
        c_bd =coef_b_down[curr_station] 
        c_cd =coef_c_down[curr_station]                    
        c_Su =coef_S_up[curr_station] 
        c_au =coef_a_up[curr_station] 
        c_bu =coef_b_up[curr_station] 
        c_cu =coef_c_up[curr_station] 

        # Recalibrate IR20s. The logger code saved the raw and offered a preliminary cal that ignored the minor terms. We can do better.
        term = (c_ad*station_data['ir20_lwd_DegC_Avg']**2 + c_bd*station_data['ir20_lwd_DegC_Avg'] + c_cd)
        station_data['down_long_hemisp'] = station_data['ir20_lwd_mV_Avg'] / (c_Sd * term) + sb * (station_data['ir20_lwd_DegC_Avg']+273.15)**4
        term = (c_au*station_data['ir20_lwu_DegC_Avg']**2 + c_bu*station_data['ir20_lwu_DegC_Avg'] + c_cu)
        station_data['up_long_hemisp'] = station_data['ir20_lwu_mV_Avg'] / (c_Su * term) + sb * (station_data['ir20_lwu_DegC_Avg']+273.15)**4

        if 'asfs30' in curr_station:

            # Fix the flux plates that were insalled upside down
            station_data['subsurface_heat_flux_A'] = station_data['subsurface_heat_flux_A'] * -1
            station_data['subsurface_heat_flux_B'].loc[datetime(2020,4,1,0,0):] = station_data['subsurface_heat_flux_B'].loc[datetime(2020,4,1,0,0):] * -1

        elif 'asfs40' in curr_station:

            # Fix the flux plates that were insalled upside down
            station_data['subsurface_heat_flux_A'] = station_data['subsurface_heat_flux_A'] * -1
            station_data['subsurface_heat_flux_B'] = station_data['subsurface_heat_flux_B'] * -1

        elif 'asfs50' in curr_station:

            # Fix the flux plates that were insalled upside down
            station_data['subsurface_heat_flux_B'] = station_data['subsurface_heat_flux_B'] * -1
            station_data['subsurface_heat_flux_A'].loc[datetime(2020,4,1,0,0):] = station_data['subsurface_heat_flux_A'].loc[datetime(2020,4,1,0,0):] * -1


        slow_data[curr_station] = station_data



    # ###############################################################################
    # OK we have all the slow data, now loop over each day and get fast data for that
    # day and do the QC/processing you want. all calculations are done in this loop
    # ... here's the meat and potatoes!!!

    day_series = pd.date_range(start_time+timedelta(1), end_time-timedelta(1)) # data was requested for these days
    day_delta  = pd.to_timedelta(86399999999,unit='us')                        # we want to go up to but not including 00:00

    printline(startline='\n')
    print("\n We have retreived all slow data, now processing each day...\n")

    # #########################################################################################################
    # here's where we actually call the data crunching function. for each station we process days sequentially
    # *then* move on to the next station, function for daily processing defined below
    def process_station_day(curr_station, today, tomorrow, slow_data_today, day_q=None):
        try:
            data_to_return = [] # this function processes the requested day then returns processed DFs appended to this
                                # list, e.g. data_to_return(data_name='slow', slow_df, None) or data_to_return(data_name='turb', turb_df, win_len)

            printline(endline="\n")
            print("Retreiving level1 fast data for {} on {}\n".format(curr_station,today))

            # get fast data from netcdf files for daily processing
            fast_data_today, fd_version = get_flux_data(curr_station, today-timedelta(1), today+timedelta(1),
                                                        1, data_dir, 'fast', verbose=False)

            # shorthand to save some space/make code more legible
            fdt = fast_data_today[today-timedelta(hours=1):tomorrow+timedelta(hours=1)]   
            sdt = slow_data_today[today-timedelta(hours=1):tomorrow+timedelta(hours=1)]   

            idt = init_data[curr_station][today:tomorrow]
            if len(fdt.index)<=1: # data warnings and sanity checks
                if sdt.empty:
                    fail_msg = " !!! No data available for {} on {} !!!".format(curr_station, fl.dstr(today))
                    print(fail_msg)
                    try: day_q.put([('fail',fail_msg)]); return [('fail',fail_msg)]
                    except: return [('fail',fail_msg)]
                print("... no fast data available for {} on {}... ".format(curr_station, fl.dstr(today)))
            if len(sdt.index)<=1 or sdt['PTemp_Avg'].isnull().values.all():
                fail_msg = "... no slow data available for {} on {}... ".format(curr_station, fl.dstr(today))
                print(fail_msg)
                try: day_q.put([('fail',fail_msg)]); return [('fail',fail_msg)]
                except: return [('fail',fail_msg)]
            printline(startline="\n")

            print("\nQuality controlling data for {} on {}".format(curr_station, today))                  

            # First remove any data before official start of station in October (there may be some indoor or Fedorov hold test data)
            sdt[:].loc[:station_initial_start_time[curr_station]]=nan    

            # met sensor ppl
            sdt['atmos_pressure'].mask((sdt['atmos_pressure']<p_thresh[0]) | (sdt['atmos_pressure']>p_thresh[1]) , inplace=True) 
            sdt['temp']          .mask((          sdt['temp']<T_thresh[0]) | (sdt['temp']>T_thresh[1])           , inplace=True) 
            sdt['dew_point']     .mask((     sdt['dew_point']<T_thresh[0]) | (sdt['dew_point']>T_thresh[1])      , inplace=True) 
            sdt['rh']            .mask((           sdt['rh']<rh_thresh[0]) | (sdt['rh']>rh_thresh[1])            , inplace=True) 

            # Ephemeris, set it up
            utime_in = np.array(sdt.index.astype(np.int64)/10**9)                   # unix time. sec since 1/1/70
            lat_in   = sdt['lat']                                                   # latitude
            lon_in   = sdt['lon']                                                   # latitude
            elv_in   = np.zeros(sdt.index.size)+2                                   # elevation shall be 2 m; deets are negligible
            pr_in    = sdt['atmos_pressure'].fillna(sdt['atmos_pressure'].median()) # mb 
            t_in     = sdt['temp'].fillna(sdt['temp'].median())                     # degC

            # est of atm ref at sunrise/set following U. S. Naval Observatory's Vector Astrometry Software
            # @ wikipedia https://en.wikipedia.org/wiki/Atmospheric_refraction. This really just
            # sets a flag for when to apply the refraction adjustment. 
            atm_ref  = ( 1.02 * 1/np.tan(np.deg2rad(0+(10.3/(0+5.11)))) ) * pr_in/1010 * (283/(273.15+t_in))/60 
            delt_in  = spa.calculate_deltat(sdt.index.year, sdt.index.month) # seconds. delta_t between terrestrial and UT1 time

            # do the thing
            app_zenith, zenith, app_elevation, elevation, azimuth, eot = spa.solar_position(utime_in,lat_in,lon_in,
                                                                                            elv_in,pr_in,t_in,delt_in,atm_ref)

            # write it out
            sdt['zenith_true']     = zenith
            sdt['zenith_apparent'] = app_zenith 
            sdt['azimuth']         = azimuth 

            # in matlab, there were rare instabilities in the Reda and Andreas algorithm that resulted in spikes
            # (a few per year). no idea if this is a problem in the python version, but lets make sure
            sdt['zenith_true']     = fl.despike(sdt['zenith_true']     ,2,5,'no')
            sdt['zenith_apparent'] = fl.despike(sdt['zenith_apparent'] ,2,5,'no')
            sdt['azimuth']         = fl.despike(sdt['azimuth']         ,2,5,'no')

            # IR20 ventilation bias. The IRT was heated with 1.5 W. If the ventilator fan was off, lab & field
            # analysis suggests that the heat was improperly diffused causing a positive bias in the instrument
            # calculated at 1.42 Wm2 in the field and 1.28 Wm2 in the lab. We will use the latter here.
            sdt['up_long_hemisp'].loc[sdt['ir20_lwu_fan_Avg'] < 400]   = sdt['up_long_hemisp']-1.28
            sdt['down_long_hemisp'].loc[sdt['ir20_lwd_fan_Avg'] < 400] = sdt['down_long_hemisp']-1.28

            # IRT QC
            sdt['body_T_IRT']              .mask( (sdt['body_T_IRT']<irt_targ[0])    | (sdt['body_T_IRT']>irt_targ[1]) ,    inplace=True) # ppl
            sdt['brightness_temp_surface'] .mask( (sdt['brightness_temp_surface']<irt_targ[0]) | (sdt['brightness_temp_surface']>irt_targ[1]) , inplace=True) # ppl

            sdt['body_T_IRT']              .mask( (sdt['temp']<-1) & (abs(sdt['body_T_IRT'])==0) ,    inplace=True) # reports spurious 0s sometimes
            sdt['brightness_temp_surface'] .mask( (sdt['temp']<-1) & (abs(sdt['brightness_temp_surface'])==0) , inplace=True) # reports spurious 0s sometimes

            sdt['body_T_IRT']              = fl.despike(sdt['body_T_IRT'],2,60,'yes')              # replace spikes outside 2C
            sdt['brightness_temp_surface'] = fl.despike(sdt['brightness_temp_surface'],2,60,'yes') # over 60 sec with 60 s median

            # Flux plate QC
            sdt['subsurface_heat_flux_A'].mask( (sdt['subsurface_heat_flux_A']<flxp[0]) | (sdt['subsurface_heat_flux_A']>flxp[1]) , inplace=True) # ppl
            sdt['subsurface_heat_flux_B'].mask( (sdt['subsurface_heat_flux_B']<flxp[0]) | (sdt['subsurface_heat_flux_B']>flxp[1]) , inplace=True) # ppl

            # SR50
            sdt['sr50_dist'].mask( (sdt['sr50_qc_Avg']<sr50_qc[0]) | (sdt['sr50_qc_Avg']>sr50_qc[1]) , inplace=True) # ppl
            sdt['sr50_dist'].mask( (sdt['sr50_dist']<sr50d[0])     | (sdt['sr50_dist']>sr50d[1]) ,     inplace=True) # ppl
            
            if curr_station == 'asfs30': sdt['sr50_dist'].loc[datetime(2020,8,2,18,56,0):].mask(sdt['sr50_dist']<1.97, inplace=True) 

            sdt['sr50_dist']  = fl.despike(sdt['sr50_dist'],0.01,5,"no") # screen but do not replace

            # if the qc is high, say 210-300 I think there is intermittent icing. this seems to work.
            if sdt['sr50_qc_Avg'].mean(): sdt['sr50_dist']  = fl.despike(sdt['sr50_dist'],0.05,720,"no")

            # clean up missing met data that comes in as '0' instead of NaN... good stuff
            zeros_list = ['rh', 'atmos_pressure', 'sr50_dist']
            for param in zeros_list: # make the zeros nans
                sdt[param] = np.where(sdt[param]==0.0, nan, sdt[param])

            temps_list = ['temp', 'brightness_temp_surface', 'body_T_IRT']
            for param in temps_list: # identify when T==0 is actually missing data, this takes some logic
                potential_inds  = np.where(sdt[param]==0.0)
                if potential_inds[0].size==0: continue # if empty, do nothing, this is unnecessary
                for ind in potential_inds[0]:
                    #ind = ind.item() # convert to native python type from np.int64, so we can index
                    lo = ind
                    hi = ind+15
                    T_nearby = sdt[param][lo:hi]
                    if np.any(T_nearby < -5) or np.any(T_nearby > 5):    # temps cant go from 0 to +/-5C in 5 minutes
                        sdt[param].iloc[ind] = nan
                    elif (sdt[param].iloc[lo:hi] == 0).all(): # no way all values for a minute are *exactly* 0
                        sdt[param].iloc[lo:hi] = nan

            # Radiation
            sdt = fl.qcrad(sdt,sw_range,lw_range,D1,D5,D11,D12,D13,D14,D15,D16,A0)       
            # Tilt correction 
            # get the tilt data
            sdt['incx_offset'] = tilt_data[curr_station]['incx_offset'].reindex(index=sdt.index,method='pad').astype('float')
            sdt['incy_offset'] = tilt_data[curr_station]['incy_offset'].reindex(index=sdt.index,method='pad').astype('float')

            if arm_data.empty or sdt.ship_distance.mean() > 2000:
                diffuse_flux = -1 # we don't have an spn1 so we model the error. later we can use it if we have it
            else:
                diffuse_flux = arm_data[today-timedelta(1):tomorrow-timedelta(1)].PSPdif.reindex(index=sdt.index)

            # now run the correcting function      
            fl.tilt_corr(sdt,diffuse_flux) # modified sdt is returned

            # ###################################################################################################
            # derive some useful parameters that we want to write to the output file

            # compute RH wrt ice -- compute RHice(%) from RHw(%), Temperature(deg C), and pressure(mb)
            Td2, h2, a2, x2, Pw2, Pws2, rhi2 = fl.calc_humidity_ptu300(sdt['rh'],\
                                                                       sdt['temp']+K_offset,
                                                                       sdt['atmos_pressure'],
                                                                       0)
            sdt['rhi']                  = rhi2
            sdt['abs_humidity_vaisala'] = a2
            sdt['vapor_pressure']       = Pw2
            sdt['mixing_ratio']         = x2

            # snow depth in cm, corrected for temperature
            sdt['sr50_dist']  = sdt['sr50_dist']*sqrt((sdt['temp']+K_offset)/K_offset)
            sdt['snow_depth'] = idt['init_dist'] + (idt['init_depth']-sdt['sr50_dist']*100)

            # net radiation
            sdt['radiation_LWnet'] = sdt['down_long_hemisp']-sdt['up_long_hemisp']
            sdt['radiation_SWnet'] = sdt['down_short_hemisp']-sdt['up_short_hemisp']
            sdt['net_radiation']   = sdt['radiation_LWnet'] + sdt['radiation_SWnet'] 

            # surface skin temperature Persson et al. (2002) https://www.doi.org/10.1029/2000JC000705
            sdt['skin_temp_surface'] = (((sdt['up_long_hemisp']-(1-emis)*sdt['down_long_hemisp'])/(emis*sb))**0.25)-K_offset
            
            # Add empiraclly-calculated offsets to the Metek inclinometer to make it plumb  
            # we need to use the original values for the radiometer tilt correction, but this correction has already been done about 50 lines up
            if curr_station == 'asfs30':
                sdt['metek_InclX_Avg']       .loc[datetime(2019,10,7) : datetime(2019,11,7)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,10,7) : datetime(2019,11,7)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,10,7) : datetime(2019,11,7)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,10,7) : datetime(2019,11,7)] + 0.
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2019,11,7) : datetime(2020,1,1)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,11,7) : datetime(2020,1,1)] + 1.5   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,11,7) : datetime(2020,1,1)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,11,7) : datetime(2020,1,1)] + 2.25
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,1,1) : datetime(2020,2,25)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,1,1) : datetime(2020,2,25)] + 2.25   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,1,1) : datetime(2020,2,25)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,1,1) : datetime(2020,2,25)] + 1.5
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,2,25) : datetime(2020,4,1)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,2,25) : datetime(2020,4,1)] + 2.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,2,25) : datetime(2020,4,1)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,2,25) : datetime(2020,4,1)] + 2.75

                sdt['metek_InclX_Avg']       .loc[datetime(2020,4,1) : datetime(2020,4,14)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,4,1) : datetime(2020,4,14)] + -2.25   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,4,1) : datetime(2020,4,14)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,4,1) : datetime(2020,4,14)] + 7.5
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,4,14) : datetime(2020,5,7)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,4,14) : datetime(2020,5,7)] + 0.75   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,4,14) : datetime(2020,5,7)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,4,14) : datetime(2020,5,7)] + 3.
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,5,7) : datetime(2020,5,13)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,5,7) : datetime(2020,5,13)] + 2.75   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,5,7) : datetime(2020,5,13)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,5,7) : datetime(2020,5,13)] + 0.25
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,5,13) : datetime(2020,5,27)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,5,13) : datetime(2020,5,27)] + 0.5   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,5,13) : datetime(2020,5,27)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,5,13) : datetime(2020,5,27)] + 1.25
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,5,27) : datetime(2020,6,21)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,5,27) : datetime(2020,6,21)] + -2.5   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,5,27) : datetime(2020,6,21)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,5,27) : datetime(2020,6,21)] + 6.75
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,6,21) : datetime(2020,6,30)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,6,21) : datetime(2020,6,30)] + -1.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,6,21) : datetime(2020,6,30)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,6,21) : datetime(2020,6,30)] + 4.75
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,6,30) : datetime(2020,8,3)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,6,30) : datetime(2020,8,3)] + 1.5   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,6,30) : datetime(2020,8,3)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,6,30) : datetime(2020,8,3)] + 0.5
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,8,3) : datetime(2020,8,22)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,8,3) : datetime(2020,8,22)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,8,3) : datetime(2020,8,22)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,8,3) : datetime(2020,8,22)] + 0.
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,8,22) : datetime(2020,9,20)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,8,22) : datetime(2020,9,20)] + -0.25  
                sdt['metek_InclY_Avg']       .loc[datetime(2020,8,22) : datetime(2020,9,20)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,8,22) : datetime(2020,9,20)] + 2.
            
            elif curr_station == 'asfs40':
                
                sdt['metek_InclX_Avg']       .loc[datetime(2019,10,5) : datetime(2019,11,10)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,10,5) : datetime(2019,11,10)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,10,5) : datetime(2019,11,10)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,10,5) : datetime(2019,11,10)] + 0.
                
                sdt['metek_InclX_Avg']       .loc[datetime(2019,11,10) : datetime(2019,12,20)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,11,10) : datetime(2019,12,20)] + -1.   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,11,10) : datetime(2019,12,20)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,11,10) : datetime(2019,12,20)] + -0.25

                sdt['metek_InclX_Avg']       .loc[datetime(2019,12,20) : datetime(2020,1,30)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,12,20) : datetime(2020,1,30)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,12,20) : datetime(2020,1,30)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,12,20) : datetime(2020,1,30)] + 0.                    
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,1,30) : datetime(2020,2,28)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,1,30) : datetime(2020,2,28)] + -1.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,1,30) : datetime(2020,2,28)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,1,30) : datetime(2020,2,28)] + 0.

            elif curr_station == 'asfs50':
                
                sdt['metek_InclX_Avg']       .loc[datetime(2019,10,10) : datetime(2019,12,22)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,10,10) : datetime(2019,12,22)] + 0.25   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,10,10) : datetime(2019,12,22)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,10,10) : datetime(2019,12,22)] + 0.25  
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2019,12,22) : datetime(2020,4,9)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2019,12,22) : datetime(2020,4,9)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2019,12,22) : datetime(2020,4,9)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2019,12,22) : datetime(2020,4,9)] + -0.25
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,4,9) : datetime(2020,5,12)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,4,9) : datetime(2020,5,12)] + 9.25   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,4,9) : datetime(2020,5,12)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,4,9) : datetime(2020,5,12)] + 1.75 
                    
                sdt['metek_InclX_Avg']       .loc[datetime(2020,5,12) : datetime(2020,6,29)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,5,12) : datetime(2020,6,29)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,5,12) : datetime(2020,6,29)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,5,12) : datetime(2020,6,29)] + 0.   
                                        
                sdt['metek_InclX_Avg']       .loc[datetime(2020,6,29) : datetime(2020,7,10)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,6,29) : datetime(2020,7,10)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,6,29) : datetime(2020,7,10)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,6,29) : datetime(2020,7,10)] + 0.
                                        
                sdt['metek_InclX_Avg']       .loc[datetime(2020,7,10) : datetime(2020,7,30)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,7,10) : datetime(2020,7,30)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,7,10) : datetime(2020,7,30)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,7,10) : datetime(2020,7,30)] + 0.
                                        
                sdt['metek_InclX_Avg']       .loc[datetime(2020,7,30) : datetime(2020,8,21)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,7,30) : datetime(2020,8,21)] + 0.   
                sdt['metek_InclY_Avg']       .loc[datetime(2020,7,30) : datetime(2020,8,21)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,7,30) : datetime(2020,8,21)] + 0.
                                        
                sdt['metek_InclX_Avg']       .loc[datetime(2020,8,21) : datetime(2020,10,1)] = \
                    sdt['metek_InclX_Avg']   .loc[datetime(2020,8,21) : datetime(2020,10,1)] + 0.5  
                sdt['metek_InclY_Avg']       .loc[datetime(2020,8,21) : datetime(2020,10,1)] = \
                    sdt['metek_InclY_Avg']   .loc[datetime(2020,8,21) : datetime(2020,10,1)] + -0.25 
                    
                    
            # ###################################################################################################
            # all the 0.1 seconds today, for obs. we buffer by 1 hr for easy of po2 in turbulent fluxes below
            Hz10_today        = pd.date_range(today-pd.Timedelta(1,'hour'), tomorrow+pd.Timedelta(1,'hour'), freq='0.1S') 
            seconds_today     = pd.date_range(today, tomorrow, freq='S')    # all the seconds today, for obs
            minutes_today     = pd.date_range(today, tomorrow, freq='T')    # all the minutes today, for obs
            ten_minutes_today = pd.date_range(today, tomorrow, freq='10T')  # all the 10 minutes today, for obs

            #                              !! Important !!
            #   first resample to 10 Hz by averaging and reindexed to a continuous 10 Hz time grid (NaN at
            #   blackouts) of Lenth 60 min x 60 sec x 10 Hz = 36000 Later on (below) we will fill all missing
            #   times with the median of the (30 min?) flux sample.
            # ~~~~~~~~~~~~~~~~~~~~~ (2) Quality control ~~~~~~~~~~~~~~~~~~~~~~~~
            print("... quality controlling the fast data now")

            # check to see if fast data actually exists...
            # no data for param, sometimes fast is missing but slow isn't... very rare
            fast_var_list = ['metek_x', 'metek_y','metek_z','metek_T', 'metek_heatstatus',
                             'licor_h2o','licor_co2','licor_pr','licor_co2_str','licor_diag']
            for param in fast_var_list:
                try: test = fdt[param]
                except KeyError: fdt[param] = nan

            if fdt.empty: # create a fake dataframe
                nan_df = pd.DataFrame([[nan]*len(fdt.columns)], columns=fdt.columns)
                nan_df = nan_df.reindex(pd.DatetimeIndex([today]))
                fdt = nan_df.copy()

            metek_list = ['metek_x', 'metek_y','metek_z','metek_T']
            for param in metek_list: # identify when T==0 is actually missing data, this takes some logic
                potential_inds  = np.where(fdt[param]==0.0)


                if potential_inds[0].size==0: continue # if empty, do nothing, this is unnecessary
                if potential_inds[0].size>100000:
                    print("!!! there were a lot of zeros in your fast data, this shouldn't happen often !!!")
                    print("!!! {}% of {} was zero today!!!".format(round((potential_inds[0].size/1728000)*100,4),param))
                    split_val = 10000
                else: split_val=200

                while split_val>199: 
                    ind = 0
                    while ind < len(potential_inds[0]):
                        curr_ind = potential_inds[0][ind]
                        hi = int(curr_ind+(split_val))
                        if hi >= len(fdt[param]): hi=len(fdt[param])-1
                        vals_nearby = fdt[param][curr_ind:hi]
                        if (fdt[param].iloc[curr_ind:hi] == 0).all(): # no way all values are consecutively *exactly* 0
                            fdt[param].iloc[curr_ind:hi] = nan
                            ind = ind+split_val
                            continue
                        else:
                            ind = ind+1

                    potential_inds  = np.where(fdt[param]==0.0)
                    if split_val ==10000:
                        split_val = 200
                    else:
                        split_val = split_val -1
                #print("...ended with {} zeros in the array".format(len(potential_inds[0])))

            # I'm being a bit lazy here: no accouting for reasons data was rejected. For another day.
            # Chris said he was lazy first, now I'm being lazy by not making it up, sorry Chris

            # begin with bounding the Metek data to the physically-possible limits
            fdt ['metek_T']  [fdt['metek_T'] < T_thresh[0]] = nan
            fdt ['metek_T']  [fdt['metek_T'] > T_thresh[1]] = nan

            fdt ['metek_x']  [np.abs(fdt['metek_x'])  > ws_thresh[1]] = nan
            fdt ['metek_y']  [np.abs(fdt['metek_y'])  > ws_thresh[1]] = nan
            fdt ['metek_z']  [np.abs(fdt['metek_z'])  > ws_thresh[1]] = nan

            # Diagnostic: break up the diagnostic and search for bad paths. the diagnostic is as follows:
            # 1234567890123
            # 1000096313033
            #
            # char 1-2   = protocol stuff. 10 is actualy 010 and it says we are receiving instantaneous data from network. ignore
            # char 3-7   = data format. we use 96 = 00096
            # char 8     = heating operation mode. we set it to 3 = on but control internally for temp and data quality
                         # (ie dont operate the heater if you dont really have to)
            # char 9     = heating state, 0 = off, 1 = on, 2 = on but faulty
            # char 10    = number of unusable radial paths (max 9). we want this to be 0 and it is redundant with the next...
            # char 11-13 = percent of unusuable paths. in the example above, 3033 = 3 of 9 or 33% bad paths

            # We want to strip off the last 3 digits here and remove data that are not all 0s.  To do this
            # fast I will do it by subtracting off the top sig figs like below.  The minumum value is 1/9 so
            # I will set the threhsold a little > 0 for slop in precision. We could set this higher. Perhaps 1
            # or 2 bad paths is not so bad? Not sure.
            status = fdt['metek_heatstatus']
            bad_data = (status/1000-np.floor(status/1000)) >  max_bad_paths[0]
            fdt['metek_x'][bad_data]=nan
            fdt['metek_y'][bad_data]=nan
            fdt['metek_z'][bad_data]=nan
            fdt['metek_T'][bad_data]=nan

            # And now Licor ####################################################
            #
            # Physically-possible limits
            fdt['licor_h2o'] .mask( (fdt['licor_h2o']<lic_h2o[0]) | (fdt['licor_h2o']>lic_h2o[1]) , inplace=True) # ppl
            fdt['licor_co2'] .mask( (fdt['licor_co2']<lic_co2[0]) | (fdt['licor_co2']>lic_co2[1]) , inplace=True) # ppl
            fdt['licor_pr']  .mask( (fdt['licor_pr']<p_thresh[0]) | (fdt['licor_pr']>p_thresh[1]) , inplace=True) # ppl

            # CO2 signal strength is a measure of window cleanliness applicable to CO2 and H2O vars
            # first map the signal strength onto the fast data since it is empty in the fast files
            fdt['licor_co2_str'] = sdt['co2_signal_licor'].reindex(fdt.index).interpolate()
            fdt['licor_h2o'].mask( (fdt['licor_co2_str']<lic_co2sig_thresh[0]), inplace=True) # ppl
            fdt['licor_co2'].mask( (fdt['licor_co2_str']<lic_co2sig_thresh[0]), inplace=True) # ppl

            # The diagnostic is coded                                       
            print("... decoding Licor diagnostics.")

            pll, detector_temp, chopper_temp = fl.decode_licor_diag(fdt['licor_diag'])
            # Phase Lock Loop. Optical filter wheel rotating normally if 1, else "abnormal"
            bad_pll = pll == 0
            # If 0, detector temp has drifted too far from set point. Should yield a bad calibration, I think
            bad_dt = detector_temp == 0
            # Ditto for the chopper housing temp
            bad_ct = chopper_temp == 0
            # Get rid of diag QC failures
            fdt['licor_h2o'][bad_pll] = nan
            fdt['licor_co2'][bad_pll] = nan
            fdt['licor_h2o'][bad_dt]  = nan
            fdt['licor_co2'][bad_dt]  = nan
            fdt['licor_h2o'][bad_ct]  = nan
            fdt['licor_co2'][bad_ct]  = nan

            # Despike: meant to replace despik.m by Fairall. Works a little different tho
            #   Here screens +/-5 m/s outliers relative to a running 1 min median
            #
            #   args go like return = despike(input,oulier_threshold_in_m/s,window_length_in_n_samples)
            #
            #   !!!! Replaces failures with the median of the window !!!!
            #
            fdt['metek_x'] = fl.despike(fdt['metek_x'],5,1200,'yes')
            fdt['metek_y'] = fl.despike(fdt['metek_y'],5,1200,'yes')
            fdt['metek_z'] = fl.despike(fdt['metek_z'],5,1200,'yes')
            fdt['metek_T'] = fl.despike(fdt['metek_T'],5,1200,'yes')           
            fdt['licor_h2o'] = fl.despike(fdt['licor_h2o'],0.5,1200,'yes')
            fdt['licor_co2'] = fl.despike(fdt['licor_co2'],50,1200,'yes')

            # ~~~~~~~~~~~~~~~~~~~~~~~ (3) Resample  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            print('... resampling 20 Hz -> 10 Hz.')
            #
            # 20 Hz irregular grid -> 10 Hz regular grid
            #
            # The method is to first resample the 20 Hz data to a 10 Hz regular
            # grid using the average of the (expect n=2) points at each 0.1s
            # interval. Then the result is indexed onto a complete grid for the
            # whole day, which is nominally 1 hour = 36000 samples at 10 Hz
            # Missing data (like NOAA Services blackouts) are nan

            fdt_10hz = fdt.resample('100ms').mean()

            fdt_10hz_ri = fdt_10hz.reindex(index=Hz10_today, method='nearest', tolerance='50ms')
            fdt_10hz = fdt_10hz_ri

            # ~~~~~~~~~~~~~~~~~ (4) Do the Tilt Rotation  ~~~~~~~~~~~~~~~~~~~~~~
            print("... cartesian tilt rotation. Translating body -> earth coordinates.")

            # This really only affects the slow interpretation of the data.
            # When we do the fluxes it will be a double rotation into the streamline that
            # implicitly accounts for deviations between body and earth
            #
            # The rotation is done in subroutine tilt_rotation, which is based on code from Chris Fairall et al.
            #
            # tilt_rotation(ct_phi,ct_theta,ct_psi,ct_up,ct_vp,ct_wp)
            #             ct_phi   = inclinometer roll angle (y)
            #             ct_theta = inclinometer pitchi angle (x)
            #             ct_psi   = yaw/heading/azimuth (z)
            #             ct_up    = y(u) wind
            #             ct_vp    = x(v) wind
            #             ct_zp    = z(w) wind
            #
            # Right-hand coordinate system convention:
            #             phi     =  inclinometer y is about the u axis
            #             theta   =  inclinometer x is about the v axis
            #             psi     =  azimuth        is about the z axis. the inclinometer does not measure this
            #                                                            despite what the manual may say (it's "aspirational").
            #             metek y -> earth u, +North
            #             metek x -> earth v, +West
            #             Have a look also at pg 21-23 of NEW_MANUAL_20190624_uSonic-3_Cage_MP_Manual for metek conventions.
            #             Pg 21 seems to have errors in the diagram?
            
            hdg = sdt['heading'].reindex(fdt_10hz.index).interpolate() # nominally, metek N is in line with the boom
            # but at the beginning of Leg 5 it wasn't and was adjusted after the first week
            if curr_station == 'asfs30':
                hdg.loc[(hdg.index >= datetime(2020,8,21,11,37,0)) & (hdg.index <= datetime(2020,8,31,5,17,0))] += 13 # Ola's notes report 15 deg, but 13 to match post rotation winds
                
            if curr_station == 'asfs50':
                hdg.loc[(hdg.index >= datetime(2020,8,24,4,57,0)) & (hdg.index <= datetime(2020,8,31,6,0,0))] += 50 # Ola's notes report 90 deg, but 50 to match post rotation winds                
                

            ct_u, ct_v, ct_w = fl.tilt_rotation(sdt['metek_InclY_Avg'].reindex(fdt_10hz.index).interpolate(),\
                                                sdt['metek_InclX_Avg'].reindex(fdt_10hz.index).interpolate(),\
                                                hdg,\
                                                fdt_10hz['metek_y'], fdt_10hz['metek_x'], fdt_10hz['metek_z'])

            # reassign corrected vals in meteorological convention, which involves swapping u and v and occurs in the following two blocks of 3 lines
            fdt_10hz['metek_x'] = ct_v 
            fdt_10hz['metek_y'] = ct_u
            fdt_10hz['metek_z'] = ct_w   

            # start referring to xyz as uvw now
            fdt_10hz.rename(columns={'metek_x':'metek_u'}, inplace=True)
            fdt_10hz.rename(columns={'metek_y':'metek_v'}, inplace=True)
            fdt_10hz.rename(columns={'metek_z':'metek_w'}, inplace=True)

            # !!
            # Now we recalculate the 1 min average wind direction and speed from the u and v velocities.
            # These values differ from the stats calcs (*_ws and *_wd) in two ways:
            #   (1) The underlying data has been quality controlled
            #   (2) We have rotated that sonic y,x,z into earth u,v,w
            #
            # I have modified the netCDF build to use *_ws_corr and *_wd_corr but have not removed the
            # original calculation because I think it is a nice opportunity for a sanity check. 
            print('... calculating a corrected set of slow wind speed and direction.')

            u_min = fdt_10hz['metek_u'].resample('1T',label='left').apply(fl.take_average)
            v_min = fdt_10hz['metek_v'].resample('1T',label='left').apply(fl.take_average)
            w_min = fdt_10hz['metek_w'].resample('1T',label='left').apply(fl.take_average)

            u_sigmin = fdt_10hz['metek_u'].resample('1T',label='left').std()
            v_sigmin = fdt_10hz['metek_v'].resample('1T',label='left').std()
            w_sigmin = fdt_10hz['metek_w'].resample('1T',label='left').std()
            
            ws = np.sqrt(u_min**2+v_min**2)
            wd = np.mod((np.arctan2(-u_min,-v_min)*180/np.pi),360)

            # manually patch time period where asfs30 had fast datastream issue
            if today > datetime(2019,10,15) and today < datetime(2019,10,30) and curr_station == 'asfs30':
                
                ct_u, ct_v, ct_w = fl.tilt_rotation(sdt['metek_InclY_Avg'], sdt['metek_InclX_Avg'],\
                                                    sdt['heading'],\
                                                    sdt['metek_y_Avg'], sdt['metek_x_Avg'], sdt['metek_z_Avg'])
                
                ct_usig, ct_vsig, ct_wsig = fl.tilt_rotation(sdt['metek_InclY_Avg'], sdt['metek_InclX_Avg'],\
                                                    sdt['heading'],\
                                                    sdt['metek_y_Std'], sdt['metek_x_Std'], sdt['metek_z_Std'])

                u_min_slow = ct_v # swapping u and v convention to met  
                v_min_slow = ct_u # swapping u and v convention to met
                w_min_slow = ct_w

                u_sigmin_slow = ct_vsig
                v_sigmin_slow = ct_usig
                w_sigmin_slow = ct_wsig
                
                ws_slow = np.sqrt(u_min_slow**2+v_min_slow**2)
                wd_slow = np.mod((np.arctan2(-u_min_slow,-v_min_slow)*180/np.pi),360)

                ws[np.isnan(ws)]       = ws_slow[np.isnan(ws)]
                wd[np.isnan(wd)]       = wd_slow[np.isnan(wd)]

                u_min[np.isnan(u_min)] = u_min_slow[np.isnan(u_min)]
                v_min[np.isnan(v_min)] = v_min_slow[np.isnan(v_min)]
                w_min[np.isnan(w_min)] = w_min_slow[np.isnan(w_min)]          

                u_sigmin[np.isnan(u_sigmin)] = u_sigmin_slow[np.isnan(u_sigmin)]
                v_sigmin[np.isnan(v_sigmin)] = v_sigmin_slow[np.isnan(v_sigmin)]
                w_sigmin[np.isnan(w_sigmin)] = w_sigmin_slow[np.isnan(w_sigmin)]

            # ~~~~~~~~~~~~~~~~~~ (5) Recalculate Stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # !!  Sorry... This is a little messed up. The original stats are read from the NOAA Services stats
            # files, contents calculated from the raw data. But we have QC'd the data and changed the raw
            # values, so we need to update the stats. I do that here. But then was there ever any point in
            # reading the stats data in the first place?
            print('... recalculating NOAA Services style stats with corrected, rotated, and QCed values.')
            
            sdt['wspd_vec_mean']     = ws
            sdt['wdir_vec_mean']     = wd
            sdt['wspd_u_mean']       = u_min
            sdt['wspd_v_mean']       = v_min
            sdt['wspd_w_mean']       = w_min
            sdt['wspd_u_std']        = u_sigmin
            sdt['wspd_v_std']        = v_sigmin
            sdt['wspd_w_std']        = w_sigmin            
            sdt['temp_acoustic_std'] = fdt_10hz['metek_T'].resample('1T',label='left').std()
            sdt['temp_acoustic']     = fdt_10hz['metek_T'].resample('1T',label='left').mean()

            sdt['h2o_licor']         = fdt_10hz['licor_h2o'].resample('1T',label='left').mean()
            sdt['co2_licor']         = fdt_10hz['licor_co2'].resample('1T',label='left').mean()
            sdt['pr_licor']          = fdt_10hz['licor_pr'].resample('1T',label='left').mean()*10 # [to hPa]

            # ~~~~~~~~~~~~~~~~~~~~ (6) Flux Capacitor  ~~~~~~~~~~~~~~~~~~~~~~~~~
    
            if calc_fluxes == True and len(fdt.index) > 0:

                verboseprint('\nCalculating turbulent fluxes and associated MO parameters.')

                # Rotation to the streamline, FFT window segmentation, detrending,
                # hamming, and computation of power [welch] & cross spectral densities,
                # covariances and associated diagnostics and plots, as well as derived
                # variables (fluxes and stress parameters) are performed within a
                # sub-function called below.
                #
                # turbulence_data = fl.grachev_fluxcapacitor(sz, sonic_data, licor_data, h2o_units, co2_units, p, t, q, verbose=v)
                #       sz = instrument height
                #       sonic_data = dataframe of u,v,w winds
                #       licor_data = dataframe of h2o adn co2
                #       h2o_units = units of licor h2o, e.g., 'mmol/m3'
                #       co2_units = units of licor co2, e.g., 'mmol/m3'
                #       p = pressure in hPa, scaler
                #       t = air temperature in C, scaler
                #       q = vapor mixing ratio, scaler

                metek_10hz = fdt_10hz[['metek_u', 'metek_v', 'metek_w','metek_T']].copy()
                metek_10hz.rename(columns={\
                                           'metek_u':'u',
                                           'metek_v':'v',
                                           'metek_w':'w',
                                           'metek_T':'T'}, inplace=True)
                licor_10hz = fdt_10hz[['licor_h2o', 'licor_co2']].copy()

                # ######################################################################################
                # corrections to the high frequency component of the turbulence spectrum... the metek
                # sonics used seem to have correlated cross talk between T and w that results in biased
                # flux values with a dependency on frequency...
                #
                # this correction fixes that and is documented in the data paper, see comments in
                # functions_library
                metek_10hz = fl.fix_high_frequency(metek_10hz)

                turb_ec_data = {}

                # calculate before loop, used to modify height offsets below to be 'more correct'
                # snow depth calculation shouldn't/doesn't fail but catch the exception just in case
                try: 
                    snow_depth = sdt['snow_depth'][minutes_today].copy()  # get snow_depth, heights evolve in time
                    snow_depth[(np.abs(stats.zscore(snow_depth.values)) < 3)]   # remove weird outliers
                    snow_depth = snow_depth*0.01                                # convert to meters
                    snow_depth = snow_depth.rolling(30, min_periods=5).mean() # fill nans for bulk calc only
                except Exception as ex: 
                    print(f"... calculating snow depth for {today} failed for some reason...")
                    print(sdt)
                    snow_depth = pd.Series(0, index=sdt[minutes_today].index)

                for win_len in range(0,len(integ_time_turb_flux)):
                    integration_window = integ_time_turb_flux[win_len]
                    flux_freq_str = '{}T'.format(integration_window) # flux calc intervals
                    flux_time_today   = pd.date_range(today-timedelta(hours=1), tomorrow+timedelta(hours=1), freq=flux_freq_str) 

                    # recalculate wind vectors to be saved with turbulence data  later
                    u_min  = metek_10hz['u'].resample(flux_freq_str, label='left').apply(fl.take_average)
                    v_min  = metek_10hz['v'].resample(flux_freq_str, label='left').apply(fl.take_average)
                    ws     = np.sqrt(u_min**2+v_min**2)
                    wd     = np.mod((np.arctan2(-u_min,-v_min)*180/np.pi),360)

                    turb_winds = pd.DataFrame()
                    turb_winds['wspd_vec_mean'] = ws
                    turb_winds['wdir_vec_mean'] = wd

                    for time_i in range(0,len(flux_time_today)-1): # flux_time_today = a DatetimeIndex defined earlier and based
                                                                   # on integ_time_turb_flux, the integration window for the
                                                                   # calculations that is defined at the top of the code

                        if time_i % 24 == 0:
                            verboseprint(f'... turbulence integration across {flux_freq_str} for '+
                                         f'{flux_time_today[time_i].strftime("%m-%d-%Y %H")}h {curr_station}')

                        # Get the index, ind, of the metek frame that pertains to the present calculation A
                        # little tricky. We need to make sure we give it enough data to encompass the nearest
                        # power of 2: for 30 min fluxes this is ~27 min so you are good, but for 10 min fluxes
                        # it is 13.6 min so you need to give it more.

                        # We buffered the 10 Hz so that we can go outside the edge of "today" by up to an hour.
                        # It's a bit of a formality, but for general cleanliness we are going to
                        # center all fluxes to the nearest min so that e.g:
                        # 12:00-12:10 is actually 11:58 through 12:12
                        # 12:00-12:30 is actually 12:01 through 12:28     
                        po2_len  = np.ceil(2**round(np.log2(integration_window*60*10))/10/60) # @10Hz, min needed to cover nearet po2 [minutes]
                        t_win    = pd.Timedelta((po2_len-integration_window)/2,'minutes')
                        metek_in = metek_10hz.loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].copy()

                        # we need pressure and temperature and humidity
                        Pr_time_i = sdt['atmos_pressure'] .loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].mean()
                        T_time_i  = sdt['temp']  .loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].mean()
                        Q_time_i  = sdt['mixing_ratio']    .loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].mean()/1000

                        # get the licor data
                        licor_data = licor_10hz.loc[flux_time_today[time_i]-t_win:flux_time_today[time_i+1]+t_win].copy()

                        # make th1e turbulent flux calculations via Grachev module
                        v = False
                        if verbose: v = True;
                        sonic_z       = 3.3 # what is sonic_z for the flux stations

                        data = fl.grachev_fluxcapacitor(sonic_z, metek_in, licor_data, 'g/m3', 'mg/m3',
                                                            Pr_time_i, T_time_i, Q_time_i, verbose=v)
                        
                        # Sanity check on Cd. Ditch the run if it fails
                        #data[:].mask( (data['Cd'] < cd_lim[0])  | (data['Cd'] > cd_lim[1]) , inplace=True) 

                        # doubtless there is a better way to initialize this
                        if time_i == 0: turbulencetom = data
                        else: turbulencetom = turbulencetom.append(data)

                    # now add the indexer datetime doohicky
                    turbulencetom.index = flux_time_today[0:-1] 

                    turb_cols = turbulencetom.keys()

                    # ugh. there are 2 dimensions to the spectral variables, but the spectra are smoothed. The smoothing routine
                    # is a bit strange in that is is dependent on the length of the window (to which it should be orthogonal!)
                    # and worse, is not obviously predictable...it groes in a for loop nested in a while loop that is seeded by
                    # a counter and limited by half the length of the window, but the growth is not entirely predictable and
                    # neither is the result so I can't preallocate the frequency vector. I need to talk to Andrey about this and
                    # I need a programatic solution to assigning a frequency dimension when pandas actually treats that
                    # dimension indpendently along the time dimension. I will search the data frame for instances of a frequency
                    # dim then assign times without it nan of that length. for days without a frequency dim I will assign it to
                    # be length of 2 arbitrarily so that the netcdf can be written. This is ugly.

                    # (1) figure out the length of the freq dim and how many times are missing. also, save the frequency itself
                    # or you will write that vector as nan later on...
                    missing_f_dim_ind = []
                    f_dim_len = 1 
                    for ii in range(0, np.array(turbulencetom['fs']).size):
                        len_var = np.array(turbulencetom['fs'][ii]).size
                        if len_var == 1:
                            missing_f_dim_ind.append(ii)
                        else:
                            f_dim_len = len_var
                            fs = turbulencetom['fs'][ii]


                    # (2) if missing times were found, fill with nans of the freq length you discovered. this happens on days
                    # when the instruents are turned on and also perhaps runs when missing data meant the flux_capacitor
                    # returned for lack of inputs
                    if f_dim_len > 0 and missing_f_dim_ind:        
                                                                    
                        # case we have no data we need to remake a nominal fs as a filler
                        if 'fs' not in locals(): 
                            fs = pd.DataFrame(np.zeros((60,1)),columns=['fs'])
                            fs = fs['fs']*nan
                        

                        for ii in range(0,len(missing_f_dim_ind)):
                            # these are the array with multiple dims...  im filling the ones that are missing with nan (of fs in
                            # the case of fs...) such that they can form a proper and square array for the netcdf
                            turbulencetom['fs'][missing_f_dim_ind[ii]] = fs
                            turbulencetom['sUs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['sVs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['sWs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['sTs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['sqs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['scs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cWUs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cWVs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cWTs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cUTs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cVTs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cWqs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cUqs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cVqs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cWcs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cUcs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cVcs'][missing_f_dim_ind[ii]] = fs*nan
                            turbulencetom['cUVs'][missing_f_dim_ind[ii]] = fs*nan
                    turb_ec_data[win_len] = turbulencetom.copy()

                # calculate the bulk 
                print('... calculating bulk fluxes for day: {}'.format(today))

                # Input dataframe
                empty_data = np.zeros(np.size(sdt['mixing_ratio'][minutes_today]))
                bulk_input = pd.DataFrame()
                bulk_input['u']  = sdt['wspd_vec_mean'][minutes_today]     # wind speed                         (m/s)
                bulk_input['ts'] = sdt['skin_temp_surface'][minutes_today] # bulk water/ice surface tempetature (degC) 
                bulk_input['t']  = sdt['temp'][minutes_today]              # air temperature                    (degC) 
                bulk_input['Q']  = sdt['mixing_ratio'][minutes_today]/1000 # air moisture mixing ratio          (kg/kg)
                bulk_input['zi'] = empty_data+600                          # inversion height                   (m) wild guess
                bulk_input['P']  = sdt['atmos_pressure'][minutes_today]    # surface pressure                   (mb)

                bulk_input['zu'] = 3.86-snow_depth   # height of anemometer               (m)
                bulk_input['zt'] = 2.13-snow_depth   # height of thermometer              (m)
                bulk_input['zq'] = 1.84-snow_depth   # height of hygrometer               (m)      
                bulk_input = bulk_input.resample(str(integration_window)+'min',label='left').apply(fl.take_average)

                # output dataframe
                empty_data = np.zeros(len(bulk_input))
                bulk = pd.DataFrame() 
                bulk['bulk_Hs']      = empty_data*nan # hsb: sensible heat flux (Wm-2)
                bulk['bulk_Hl']      = empty_data*nan # hlb: latent heat flux (Wm-2)
                bulk['bulk_tau']     = empty_data*nan # tau: stress                             (Pa)
                bulk['bulk_z0']      = empty_data*nan # zo: roughness length, veolicity              (m)
                bulk['bulk_z0t']     = empty_data*nan # zot:roughness length, temperature (m)
                bulk['bulk_z0q']     = empty_data*nan # zoq: roughness length, humidity (m)
                bulk['bulk_L']       = empty_data*nan # L: Obukhov length (m)       
                bulk['bulk_ustar']   = empty_data*nan # usr: friction velocity (sqrt(momentum flux)), ustar (m/s)
                bulk['bulk_tstar']   = empty_data*nan # tsr: temperature scale, tstar (K)
                bulk['bulk_qstar']   = empty_data*nan # qsr: specific humidity scale, qstar (kg/kg?)
                bulk['bulk_dter']    = empty_data*nan # dter
                bulk['bulk_dqer']    = empty_data*nan # dqer
                bulk['bulk_Hl_Webb'] = empty_data*nan # hl_webb: Webb density-corrected Hl (Wm-2)
                bulk['bulk_Cd']      = empty_data*nan # Cd: transfer coefficient for stress
                bulk['bulk_Ch']      = empty_data*nan # Ch: transfer coefficient for Hs
                bulk['bulk_Ce']      = empty_data*nan # Ce: transfer coefficient for Hl
                bulk['bulk_Cdn_10m'] = empty_data*nan # Cdn_10: 10 m neutral transfer coefficient for stress
                bulk['bulk_Chn_10m'] = empty_data*nan # Chn_10: 10 m neutral transfer coefficient for Hs
                bulk['bulk_Cen_10m'] = empty_data*nan # Cen_10: 10 m neutral transfer coefficient for Hl
                bulk['bulk_Rr']      = empty_data*nan # Reynolds number
                bulk['bulk_Rt']      = empty_data*nan # 
                bulk['bulk_Rq']      = empty_data*nan # 
                bulk=bulk.reindex(index=bulk_input.index)

                if we_want_to_debug:
                    import pickle
                    with open(f'./tests/{today.strftime("%Y%m%d")}_bulk_debug_{curr_station}.pkl', 'wb') as pkl_file:
                        pickle.dump(bulk_input, pkl_file)


                for ii in range(len(bulk)):
                    tmp = [bulk_input['u'][ii], bulk_input['ts'][ii], bulk_input['t'][ii], \
                           bulk_input['Q'][ii], bulk_input['zi'][ii], bulk_input['P'][ii], \
                           bulk_input['zu'][ii],bulk_input['zt'][ii], bulk_input['zq'][ii]] 

                    if not any(np.isnan(tmp)):
                        bulkout = fl.cor_ice_A10(tmp)
                        for hh in range(len(bulkout)):
                            if bulkout[13] < cd_lim[0] or bulkout[13] > cd_lim[1]:  # Sanity check on Cd. Ditch the whole run if it fails
                                bulk[bulk.columns[hh]][ii]=nan                      # for some reason this needs to be in a loop
                            else:
                                bulk[bulk.columns[hh]][ii]=bulkout[hh]

                for win_len in range(0,len(integ_time_turb_flux)):

                    # add this to the EC data, concat columns alongside each other without adding indexes
                    turbulencenew = pd.concat( [turb_ec_data[win_len], bulk, turb_winds], axis=1)  
                    data_to_return.append(('turb', turbulencenew.copy()[today:tomorrow], win_len))
                    if win_len < len(integ_time_turb_flux)-1: print('\n')

            out_dir   = '/Projects/MOSAiC_internal/flux_data_tests/'+curr_station+'/2_level_product_'+curr_station+'/' # where will level 2 data written?
            #out_dir   = '/Projects/MOSAiC_internal/mgallagher/'+curr_station+'/2_level_product_'+curr_station+'/' # where will level 2 data written?
    
            try: 
                trash_var = write_level2_10hz(curr_station, metek_10hz[today:tomorrow], licor_10hz[today:tomorrow], today, out_dir)
            except UnboundLocalError as ule:
                this_will_fail_if_no_fast_data = True

            data_to_return.append(('slow', sdt.copy()[today:tomorrow], None)) 

            try: day_q.put(data_to_return); return data_to_return
            except: return data_to_return
            

        except Exception as e: # this day failed with some sort of exception, but we want to keep processing 

            print(f"!!! processing of {curr_station} failed for {today}  !!!")
            print("==========================================================================================")
            print("Python traceback: \n\n")
            import traceback
            import sys
            print(traceback.format_exc())
            print("==========================================================================================")

            let_fail = True
            if let_fail: raise
            try: day_q.put([('trace', tbs)]); return [('trace', tbs)]
            except: return [('trace', tbs)]


    # used to store dataframes to be QCed/written after all days are processed,
    turb_data_dict = {}; slow_data_dict = {}
    for st in flux_stations: 
        turb_data_dict[st] = {}; slow_data_dict[st] = []
        for win_len in range(0,len(integ_time_turb_flux)):
            turb_data_dict[st][win_len] = []

    # call processing by day then station (allows threading for processing a single days data)
    failed_days = {}
    for curr_station in flux_stations:
        failed_days[curr_station] = []
        printline(endline=f"\n\n  Processing all requested days of data for {curr_station}\n\n"); printline()

        day_ind = -1*nthreads
        while day_ind < len(day_series): # loop over the days in the processing range and crunch away
            day_ind += nthreads

            q_list = []
            for day_i in range(day_ind, day_ind+nthreads): # with nthreads parallel processing
                if day_i >= len(day_series): continue

                today    = day_series[day_i]
                tomorrow = today+day_delta
                sd_today = slow_data[curr_station][today-timedelta(hours=1):tomorrow+timedelta(hours=1)]
                if len(sd_today[today:tomorrow]) == 0: continue # weird corner case where data begins tomorrow/ended yesterday

                q_today = Q()
                P(target=process_station_day, args=(curr_station, today, tomorrow, sd_today, q_today)).start()
                q_list.append((q_today, today))
                
            for qq, day in q_list: 
                try: df_tuple_list = qq.get(timeout=600)
                except:
                    import traceback
                    import sys
                    exc = traceback.format_exc()
                    failed_days[curr_station].append((day,exc))
                    df_tuple_list= None

                if type(df_tuple_list) != type([]): 
                    failed_days[curr_station].append((day,f"failed for undetermined reason, look at log {df_tuple_list}"))
                    continue

                for dft in df_tuple_list: 
                    return_status = dft[0]
                    if any(return_status in s for s in ['fail', 'trace']):
                        failed_days[curr_station].append((day, dft[1]))
                        break
                    elif dft[0] == 'slow':
                        slow_data_dict[curr_station].append(dft[1])
                    elif dft[0] == 'turb':
                        win_len = dft[2]
                        turb_data_dict[curr_station][win_len].append(dft[1])
                    else:
                        failed_days[curr_station].append((day,"failed for undetermined reason, look at log {dft}"))
                        break

    printline(endline=f"\n\n  Finished with data processing, now we QC and write out all files!!!"); printline()
    print("\n ... but first we have to concat the data and then QC, a bit slow")

    turb_all = {}; slow_all = {}; 
    for curr_station in flux_stations:
        slow_all[curr_station] = pd.concat( slow_data_dict[curr_station] )
        slow_all[curr_station] = slow_all[curr_station].sort_index() 
        turb_all[curr_station] = {}
        for win_len in range(0, len(integ_time_turb_flux)):
            turb_all[curr_station][win_len] = pd.concat( turb_data_dict[curr_station][win_len] ).sort_index()

        # if we_want_to_debug:
        #     with open(f'./tests/{datetime(2022,10,10).today().strftime("%Y%m%d")}_qc_debug_before_{curr_station}.pkl', 'wb') as pkl_file:
        #         import pickle
        #         pickle.dump(slow_all[curr_station], pkl_file)

        slow_all[curr_station] = qc_stations(slow_all[curr_station], curr_station)


        # if we_want_to_debug:
        #     with open(f'./tests/{datetime(2022,10,10).today().strftime("%Y%m%d")}_qc_debug_after_{curr_station}.pkl', 'wb') as pkl_file:
        #         import pickle
        #         pickle.dump(slow_all[curr_station], pkl_file)

    print(" ... done with concatting and QC, now we write! here's a sample of the output data:\n\n")
    for curr_station in flux_stations:
        print(slow_all[curr_station])
    
    def write_todays_data(curr_station, today, day_q):
        tomorrow = today+day_delta

        station_data = slow_all[curr_station][today:tomorrow].copy()

        out_dir   = '/Projects/MOSAiC_internal/flux_data_tests/'+curr_station+'/2_level_product_'+curr_station+'/' # where will level 2 data written?
        #out_dir   = '/Projects/MOSAiC_internal/mgallagher/'+curr_station+'/2_level_product_'+curr_station+'/' # where will level 2 data written?
 
        #out_dir   = '/Projects/MOSAiC_internal/flux_data_tests/'+curr_station+'/2_level_product_'+curr_station+'/' 
        #out_dir   = data_dir+'/'+curr_station+'/2_level_product_'+curr_station+'/' # where will level 2 data written?

        wr, sr, write_data = qc_asfs_winds(station_data.copy())

        # import pickle
        # met_args = [write_data.copy(), curr_station, today, "1min", out_dir]
        # pkl_file = open(f'./tests/{today.strftime("%Y%m%d")}_{curr_station}_met_data_write.pkl', 'wb')
        # pickle.dump(met_args, pkl_file)
        # pkl_file.close()

        trash_var = write_level2_netcdf(write_data.copy(), curr_station, today, "1min", out_dir)

        for win_len in range(0, len(integ_time_turb_flux)):
            integration_window = integ_time_turb_flux[win_len]
            fstr = f'{integ_time_turb_flux[win_len]}T' # pandas notation for timestep
            turb_data = turb_all[curr_station][win_len][today:tomorrow]

            # do averaging, a little weird, a little kludgy, a little annoying... whatever...
            # should have built the qc pipeline into the original code as a module and this would be cleaner

            data_list = []

            l2_atts, l2_cols = define_level2_variables(); qc_atts, qc_cols = define_qc_variables(include_turb=True)
            l2_cols = l2_cols+qc_cols

            vector_vars = ['wspd_vec_mean', 'wdir_vec_mean']
            angle_vars  = ['heading', 'ship_bearing']

            for ivar, var_name in enumerate(l2_cols):
                try: 
                    if var_name.split('_')[-1] == 'qc':
                        data_list.append(fl.average_mosaic_flags(station_data[var_name], fstr))
                    elif any(substr in var_name for substr in vector_vars):
                        data_list.append(turb_data[var_name]) # yank a few select variables out of turbulence, vestigial nonsense
                    elif any(substr in var_name for substr in angle_vars):
                        data_list.append(station_data[var_name].resample(fstr, label='left').apply(fl.take_average, is_angle=True))
                    else:
                        data_list.append(station_data[var_name].resample(fstr, label='left').apply(fl.take_average))
                except Exception as e: 
                    # this is a little silly, data didn't exist for var fill with nans so computation continues
                    print(f"... wait what/why/huh??? {var_name} — {e}")
                    data_list.append(pd.Series([np.nan]*len(station_data), index=station_data.index, name=var_name)\
                                     .resample(fstr, label='left').apply(fl.take_average))

            avged_data = pd.concat(data_list, axis=1)
            avged_data = avged_data[today:tomorrow]

            try:

                # import pickle
                # pkl_file = open(f'./tests/{today.strftime("%Y%m%d")}_{curr_station}_seb_qc_before.pkl', 'wb')
                # pickle.dump([avged_data,turb_data], pkl_file)
                # pkl_file.close()

                wr, sr, avged_data = qc_asfs_winds(avged_data)

                avged_data, turb_data = qc_asfs_turb_data(avged_data.copy(), turb_data.copy())

                # for debugging the write function.... ugh
                # import pickle
                # seb_args = [avged_data.copy(), turb_data]
                # pkl_file = open(f'./tests/{today.strftime("%Y%m%d")}_{curr_station}_seb_qc_after.pkl', 'wb')
                # pickle.dump(seb_args, pkl_file)
                # pkl_file.close()

                trash_var = write_level2_netcdf(avged_data.copy(), curr_station, today,
                                                f"{integration_window}min", out_dir, turb_data)


            except: 
                print(f"!!! failed to qc and write turbulence data for {win_len} on {today} !!!")
                print("==========================================================================================")
                print("Python traceback: \n\n")
                import traceback
                import sys
                print(traceback.format_exc())
                print("==========================================================================================")
                #print(sys.exc_info()[2])


        day_q.put(True) 

    # call processing by day then station (allows threading for processing a single days data)
    for curr_station in flux_stations:
        printline(endline=f"\n\n  Writing all requested days of data for {curr_station}\n\n"); printline()
        q_list = []  # setup queue storage
        for i_day, today in enumerate(day_series): # loop over the days in the processing range and crunch away

            q_today = Q()
            P(target=write_todays_data, args=(curr_station, today, q_today)).start()
            q_list.append(q_today)

            if (i_day+1) % nthreads == 0 or today == day_series[-1]:
                for qq in q_list: qq.get()
                q_list = []

    printline()
    print("All done! Go check out your freshly baked files!!!")
    print(version_msg)
    printline()
    if any(len(fdays)>0 for fdays in failed_days.values()):
        print("\n\n ... but wait, there's more, the following days failed with exceptions: \n\n")
        printline()
        for curr_station in flux_stations: 
            for fday in failed_days[curr_station]:
                date, exception = fday
                print(f"... {date} for {curr_station} -- with:\n {exception}\n\n")


# do the stuff to write out the level1 files, set timestep equal to anything from "1min" to "XXmin"
# and we will average the native 1min data to that timestep. right now we are writing 1 and 10min files
def write_level2_netcdf(l2_data, curr_station, date, timestep, out_dir, turb_data=None):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    l2_atts, l2_cols = define_level2_variables()

    all_missing     = True 
    first_loop      = True
    n_missing_denom = 0

    if l2_data.empty:
        print("... there was no data to write today {} for {} at station {}".format(date,timestep,curr_station))
        return False

    # get some useful missing data information for today and print it for the user
    for var_name, var_atts in l2_atts.items():
        try: dt = l2_data[var_name].dtype
        except KeyError as e: 
            print(" !!! no {} in data for {} ... does this make sense??".format(var_name, curr_station))
        perc_miss = fl.perc_missing(l2_data[var_name].values)
        if perc_miss < 100: all_missing = False
        if first_loop: 
            avg_missing = perc_miss
            first_loop=False
        elif perc_miss < 100: 
            avg_missing = avg_missing + perc_miss
            n_missing_denom += 1
    if n_missing_denom > 1: avg_missing = round(avg_missing/n_missing_denom,2)
    else: avg_missing = 100.

    print("... writing {} level2 for {} on {}, ~{}% of data is present".format(timestep, curr_station, date, 100-avg_missing))

    short_name = "met"
    if timestep != "1min":
        short_name = 'seb'
        
    #FIXME after debugging, uncomment this
    file_str = 'mos{}.{}.{}.{}.{}.nc'.format(short_name,curr_station,lvlname,timestep,date.strftime('%Y%m%d.%H%M%S'))
    lev2_name  = '{}/{}'.format(out_dir, file_str)
 
    # AND DELETE ALL THIS
    # def_fill_int = -9999
    # def_fill_flt = -9999.0
    # epoch_time        = datetime(1970,1,1,0,0,0) # Unix epoch, sets time integers
    # file_str = 'mos{}.{}.{}.{}.{}.nc'.format(short_name,curr_station,'newtest',timestep,date.strftime('%Y%m%d.%H%M%S'))
    # lev2_name  = '{}/{}'.format('./', file_str)
    # nan = np.nan

    if short_name=="seb": 
        global_atts = define_global_atts(curr_station,"seb") # global atts for level 1 and level 2
    else:
        global_atts = define_global_atts(curr_station,"level2") # global atts for level 1 and level 2

    netcdf_lev2 = Dataset(lev2_name, 'w')# format='NETCDF4_CLASSIC')

    for att_name, att_val in global_atts.items(): # write global attributes 
        netcdf_lev2.setncattr(att_name, att_val)

    # put turbulence and 'slow' data together
    if isinstance(turb_data, type(pd.DataFrame())):
        turb_atts, turb_cols = define_turb_variables()
        qc_atts, qc_cols = define_qc_variables(include_turb=True)
    else:
        qc_atts, qc_cols = define_qc_variables()
        turb_atts = {}

    l2_atts.update(qc_atts) # combine qc atts/vars now
    l2_cols = l2_cols+qc_cols

    write_data_list = []
    fstr = '{}T'.format(timestep.rstrip("min"))
    
    if timestep != "1min":

        # we also need freq. dim for some turbulence vars and fix some object-oriented confusion
        # this loop effectively exists to normalize data in a way that the netcdf4 library 
        # can easily write them out, clean up weird dtypes==object, multi dimensional
        # missing data (time, freq) for turbulence calcultations, etc etc etc   
        first_exception = True
        for var_name, var_atts in turb_atts.items(): 
            try: turb_data[var_name]
            except KeyError as ke: 
                if var_name.split("_")[-1] == 'qc': continue; do_nothing = True # we don't fill in all qc variables yet
                else: raise 
                
            chosen_index = 0 # pick first time point to find the number of frequency datapoints written

            if turb_data[var_name].isna().all() or type(turb_data[var_name][chosen_index]) == type(float()):
                turb_data[var_name] = np.float64(turb_data[var_name])

            # this is weird and should only every happen if there was all nans in the fast data
            elif turb_data[var_name][chosen_index].dtype != np.dtype('float64') and turb_data[var_name][chosen_index].len > 1:

                if first_exception:
                    print(f"... something was strange about the fast data on {date} {ae}"); first_exception = False

                max_size = 0 
                for i in turb_data.index: 
                    try:
                        this_size = turb_data[var_name][i].size
                        if this_size > max_size:
                            max_size = this_size
                            chosen_index = i
                    except: do_nothing = True

                for i in turb_data.index: 
                    try: this_size = turb_data[var_name][i].size
                    except: 
                        turb_data[var_name][i] = pd.Series([nan]*max_size)

            # create variable, # dtype inferred from data file via pandas
            if 'fs' in var_name:
                netcdf_lev2.createDimension('freq', turb_data[var_name][chosen_index].size)   
 
    write_data = l2_data # vestigial, like many things

    # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
    netcdf_lev2.createDimension('time', None)

    dti = pd.DatetimeIndex(write_data.index.values)
    fstr = '{}T'.format(timestep.rstrip("min"))
    if timestep != "1min":
        dti = pd.date_range(date, tomorrow, freq=fstr)

    try:
        fms = write_data.index[0]
    except Exception as e:
        print("... something went really wrong with the indexing")
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
    base = netcdf_lev2.createVariable('base_time', 'i') # seconds since
    base[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])      # seconds

    base_atts = {'string'     : '{}'.format(bot),
                 'long_name' : 'Base time since Epoch',
                 'units'     : 'seconds since {}'.format(et),
                 'ancillary_variables'  : 'time_offset',}
    for att_name, att_val in base_atts.items(): netcdf_lev2['base_time'].setncattr(att_name,att_val)

    # here we create the array and attributes for 'time'
    t_atts   = { 'units'     : 'seconds since {}'.format(tm),
                 'delta_t'   : '0000-00-00 00:01:00',
                 'long_name' : 'Time offset from midnight',
                 'calendar'  : 'standard',}


    bt_atts   = {'units'     : 'seconds since {}'.format(bot),
                     'delta_t'   : '0000-00-00 00:01:00',
                     'long_name' : 'Time offset from base_time',
                     'calendar'  : 'standard',}


    delta_ints = np.floor((dti - tm).total_seconds())      # seconds

    t_ind = pd.Int64Index(delta_ints)

    # set the time dimension and variable attributes to what's defined above
    t = netcdf_lev2.createVariable('time', 'd','time') # seconds since

    # now we create the array and attributes for 'time_offset'
    bt_delta_ints = np.floor((dti - bot).total_seconds())      # seconds

    bt_ind = pd.Int64Index(bt_delta_ints)

    # set the time dimension and variable attributes to what's defined above
    bt = netcdf_lev2.createVariable('time_offset', 'd','time') # seconds since

    # this try/except is vestigial, this bug should be fixed
    t[:]  = t_ind.values
    bt[:] = bt_ind.values

    for att_name, att_val in t_atts.items(): netcdf_lev2['time'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts.items(): netcdf_lev2['time_offset'].setncattr(att_name,att_val)

    for var_name, var_atts in l2_atts.items():

        try: var_dtype = write_data[var_name].dtype
        except: 
            print(f"NOT WRITING VARIABLE {var_name} for {date} —— it didn't exist")
            continue

        perc_miss = fl.perc_missing(write_data[var_name])

        if fl.column_is_ints(write_data[var_name]):
            var_dtype = np.int32
            fill_val  = def_fill_int
            var_tmp = write_data[var_name].values.astype(np.int32)
        else:
            fill_val  = def_fill_flt
            var_tmp = write_data[var_name].values.astype(np.int32)

        # all qc flags set to -1 for when corresponding variables are missing data
        exception_cols = {'bulk_qc': 'bulk_Hs', 'turbulence_qc': 'Hs', 'Hl_qc': 'Hl'}

        try:
            if var_name.split('_')[-1] == 'qc':
                fill_val = np.int32(-1)
                if not any(var_name in c for c in list(exception_cols.keys())): 
                    write_data.loc[write_data[var_name].isnull(), var_name] = 0
                    write_data.loc[write_data[var_name.rstrip('_qc')].isnull(), var_name] = fill_val
            
                else: 
                    write_data.loc[write_data[var_name].isnull(), var_name] = 0
                    write_data.loc[turb_data[exception_cols[var_name]].isnull(), var_name] = fill_val

        except Exception as e:
            print("Python traceback: \n\n")
            import traceback
            import sys
            print(traceback.format_exc())
            print("==========================================================================================\n")
            
            print(f"!!! failed to fill in qc var: {var_name}!!!\n !!! {e}")

        var  = netcdf_lev2.createVariable(var_name, var_dtype, 'time')

        # write atts to the var now
        for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name].setncattr(att_name, att_desc)
        netcdf_lev2[var_name].setncattr('missing_value', fill_val)

        vtmp = write_data[var_name].copy()

        max_val = np.nanmax(vtmp.values) # masked array max/min/etc
        min_val = np.nanmin(vtmp.values)
        avg_val = np.nanmean(vtmp.values)
        
        if var_name.split('_')[-1] != 'qc':
            netcdf_lev2[var_name].setncattr('max_val', max_val)
            netcdf_lev2[var_name].setncattr('min_val', min_val)
            netcdf_lev2[var_name].setncattr('avg_val', avg_val)

        vtmp.fillna(fill_val, inplace=True)
        var[:] = vtmp.values

        # add a percent_missing attribute to give a first look at "data quality"
        netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)

    # loop over all the data_out variables and save them to the netcdf along with their atts, etc
    ivar=0
    for var_name, var_atts in turb_atts.items():
        ivar+=1
        if not turb_data.empty: 
            # create variable, # dtype inferred from data file via pandas
            var_dtype = turb_data[var_name][0].dtype
            if turb_data[var_name][0].size == 1:

                # all qc flags set to -1 for when corresponding variables are missing data
                exception_cols = {'bulk_qc': 'bulk_Hs', 'turbulence_qc': 'Hs', 'Hl_qc': 'Hl'}

                var_turb  = netcdf_lev2.createVariable(var_name, var_dtype, 'time')

                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data)
                td = turb_data[var_name]
                td.fillna(def_fill_flt, inplace=True)
                var_turb[:] = td.values

            else:
                if 'fs' in var_name:  
                    var_turb  = netcdf_lev2.createVariable(var_name, var_dtype, ('freq'))
                    # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data). this is even stupider in multipple dimensions
                    td = turb_data[var_name][0]
                    try: 
                        td.fillna(def_fill_flt, inplace=True)
                        var_turb[:] = td.values
                    except: 
                        var_turb[:] = nan
                        print(f"... weird, {date} failed to get frequency data...")

                else:   
                    var_turb  = netcdf_lev2.createVariable(var_name, var_dtype, ('time','freq'))

                    tmp_df = pd.DataFrame(index=turb_data.index)

                    try: 
                        # replaced some sketchy code loops with functional OO calls and list comprehensions
                        # put the timeseries into a temporary DF that's a simple timeseries, not an array of 'freq'
                        tmp_list    = [col.values for col in turb_data[var_name].values]
                        tmp_df      = pd.DataFrame(tmp_list, index=turb_data.index).fillna(def_fill_flt)
                        tmp         = tmp_df.to_numpy()
                        var_turb[:] = tmp         
                    except:
                        var_turb[:] = nan

        else:
            var_turb  = netcdf_lev2.createVariable(var_name, np.double(), 'time')
            var_turb[:] = nan

        # add variable descriptions from above to each file
        for att_name, att_desc in var_atts.items(): netcdf_lev2[var_name] .setncattr(att_name, att_desc)

        # add a percent_missing attribute to give a first look at "data quality"
        perc_miss = fl.perc_missing(var_turb)
        netcdf_lev2[var_name].setncattr('percent_missing', perc_miss)
        netcdf_lev2[var_name].setncattr('missing_value', def_fill_flt)

    netcdf_lev2.close() # close and write files for today

    return  True

def write_level2_10hz(curr_station, sonic_data, licor_data, date, out_dir):

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    # these keys are the names of the groups in the netcdf files and the
    # strings in the tuple on the right will be the strings that we search for
    # in fast_atts to know which atts to apply to which group/variable, the
    # data is the value of the search string, a dict of dicts...
    sonic_data = sonic_data.add_prefix('metek_')

    inst_dict = {}
    inst_dict['metek'] = ('metek' , sonic_data)
    inst_dict['licor'] = ('licor' , licor_data)

    fast_atts, fast_vars = define_10hz_variables()

    print("... writing level1 fast data {}".format(date))

    # if there's no data, bale (had to look up how to spell bale)
    num_empty=0; 
    for inst in inst_dict:
        if inst_dict[inst][1].empty: num_empty+=1

    if num_empty == len(inst_dict): 
        print("!!! no data on day {}, returning from fast write without writing".format(date))
        return False

    file_str_fast = 'moswind10hz.{}.{}.{}.nc'.format(curr_station,lvlname,date.strftime('%Y%m%d.%H%M%S'))
    
    lev2_10hz_name  = '{}/{}'.format(out_dir, file_str_fast)

    global_atts_fast = define_global_atts(curr_station, "10hz") # global atts for level 1 and level 2

    netcdf_10hz  = Dataset(lev2_10hz_name, 'w',zlib=True)

    for att_name, att_val in global_atts_fast.items(): # write the global attributes to fast
        netcdf_10hz.setncattr(att_name, att_val)

    # setup the appropriate time dimensions
    netcdf_10hz.createDimension(f'time', None)

    fms = sonic_data.index[0]
    beginning_of_time = fms 

    # base_time, ARM spec, the difference between the time of the first data point and the BOT
    today_midnight = datetime(fms.year, fms.month, fms.day)
    beginning_of_time = fms 

    # create the three 'bases' that serve for calculating the time arrays
    et  = np.datetime64(epoch_time)
    bot = np.datetime64(beginning_of_time)
    tm  =  np.datetime64(today_midnight)

    # first write the int base_time, the temporal distance from the UNIX epoch
    base_fast = netcdf_10hz.createVariable(f'base_time', 'i') # seconds since
    base_fast[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])

    base_atts = {'string'              : '{}'.format(bot),
                 'long_name'           : 'Base time since Epoch',
                 'units'               : 'seconds since {}'.format(et),
                 'ancillary_variables' : 'time_offset',}

    t_atts_fast   = {'units'     : 'milliseconds since {}'.format(tm),
                     'delta_t'   : '0000-00-00 00:00:00.001',
                     'long_name' : 'Time offset from midnight',
                     'calendar'  : 'standard',}

    bt_atts_fast   = {'units'    : 'milliseconds since {}'.format(bot),
                      'delta_t'   : '0000-00-00 00:00:00.001',
                      'long_name' : 'Time offset from base_time',
                      'calendar'  : 'standard',}

    bt_fast_dti = pd.DatetimeIndex(sonic_data.index.values)   
    fast_dti    = pd.DatetimeIndex(sonic_data.index.values)

    # set the time dimension and variable attributes to what's defined above
    t_fast      = netcdf_10hz.createVariable(f'time', 'd',f'time') 
    bt_fast     = netcdf_10hz.createVariable(f'time_offset', 'd',f'time') 

    bt_fast_delta_ints = np.floor((bt_fast_dti - bot).total_seconds()*1000)      # milliseconds
    fast_delta_ints    = np.floor((fast_dti - tm).total_seconds()*1000)      # milliseconds

    bt_fast_ind = pd.Int64Index(bt_fast_delta_ints)
    t_fast_ind  = pd.Int64Index(fast_delta_ints)

    t_fast[:]   = t_fast_ind.values
    bt_fast[:]  = bt_fast_ind.values

    for att_name, att_val in t_atts_fast.items():
        netcdf_10hz[f'time'].setncattr(att_name,att_val)
    for att_name, att_val in base_atts.items():
        netcdf_10hz[f'base_time'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts_fast.items():
        netcdf_10hz[f'time_offset'].setncattr(att_name,att_val)

    # loop through the 4 instruments and set vars in each group based on the strings contained in those vars.
    # a bit sketchy but better than hardcoding things... probably. can at least be done in loop
    # and provides some flexibility for var name changes and such.
    for inst in inst_dict: # for instrument in instrument list create a group and stuff it with data/vars

        inst_str  = inst_dict[inst][0]
        inst_data = inst_dict[inst][1][date:tomorrow]

        #curr_group = netcdf_10hz.createGroup(inst) 

           
        used_vars = [] # used to sanity check and make sure no vars get left out of the file by using string ids
        for var_name, var_atts in fast_atts.items():
            if inst_str not in var_name: continue # check if this variable belongs to this instrument/group
            # if 'TIMESTAMP' in var_name:
            #     used_vars.append(var_name)
            #     continue # already did time stuff
            # actually, commenting out because maybe we should preserve the original timestamp integers???

            try: 
                var_dtype = inst_data[var_name].dtype
            except: 
                print(f" !!! variable {var_name} didn't exist in 10hz data, not writing any 10hz !!!")
                return False

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
                var_fast = netcdf_10hz.createVariable(var_name, var_dtype, f'time', zlib=True)
                var_fast[:] = var_tmp # compress fast data via zlib=True

            except Exception as e:
                print("!!! something wrong with variable {} on date {} !!!".format(var_name, date))
                print(inst_data[var_name])
                print("!!! {} !!!".format(e))
                continue

            for att_name, att_desc in var_atts.items(): # write atts to the var now
                netcdf_10hz[var_name].setncattr(att_name, att_desc)

            # add a percent_missing attribute to give a first look at "data quality"
            perc_miss = fl.perc_missing(var_fast)
            netcdf_10hz[var_name].setncattr('percent_missing', perc_miss)
            netcdf_10hz[var_name].setncattr('missing_value'  , fill_val)
            used_vars.append(var_name)  # all done, move on to next variable

    print(f"... finished writing 10hz data for {date}")
    netcdf_10hz.close()
    return True

# do the stuff to write out the level1 files, set timestep equal to anything from "1min" to "XXmin"
# and we will average the native 1min data to that timestep. right now we are writing 1 and 10min files
def write_turb_netcdf(turb_data, curr_station, date, integration_window, win_len, out_dir):
    
    timestep = str(integration_window)+"min"

    day_delta = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    tomorrow  = date+day_delta

    turb_atts, turb_cols = define_turb_variables()

    if turb_data.empty:
        print("... there was no turbulence data to write today {} at station {}".format(date,curr_station))
        return False

    # get some useful missing data information for today and print it for the user
    if not turb_data.empty: avg_missing = (1-turb_data.iloc[:,0].notnull().count()/len(turb_data.iloc[:,1]))*100.
    #fl.perc_missing(turb_data.iloc[:,0].values)
    else: avg_missing = 100.

    print("... writing turbulence data for {} on {}, ~{}% of data is present".format(curr_station, date, 100-avg_missing))
    
    file_str = 'mos{}turb.level2.{}.{}.nc'.format(curr_station,timestep,date.strftime('%Y%m%d.%H%M%S'))

    turb_name  = '{}/{}'.format(out_dir, file_str)

    global_atts = define_global_atts(curr_station, "turb") # global atts for level 1 and level 2
    netcdf_turb = Dataset(turb_name, 'w', zlib=True)
    # output netcdf4_classic files, for backwards compatibility... can be changed later but has some useful
    # features when using the data with 'vintage' processing code. it's the netcdf3 api, wrapped in hdf5

    # !! sorry, i have a different set of globals for this file so it isnt in the file list
    for att_name, att_val in global_atts.items(): netcdf_turb.setncattr(att_name, att_val) 
    n_turb_in_day = np.int(24*60/integration_window)

    netcdf_turb.createDimension('time', None)

    try:
        fms = turb_data.index[0]
    except Exception as e:
        print("... something went really wrong with the indexing")
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
    base = netcdf_turb.createVariable('base_time', 'i') # seconds since
    base[:] = int((pd.DatetimeIndex([bot]) - et).total_seconds().values[0])      # seconds

    base_atts = {'string'     : '{}'.format(bot),
                 'long_name' : 'Base time since Epoch',
                 'units'     : 'seconds since {}'.format(et),
                 'ancillary_variables'  : 'time_offset',}
    for att_name, att_val in base_atts.items(): netcdf_turb['base_time'].setncattr(att_name,att_val)

    if integ_time_turb_flux[win_len] < 10:
        delt_str = f"0000-00-00 00:0{integ_time_turb_flux[win_len]}:00"
    else:
        delt_str = f"0000-00-00 00:{integ_time_turb_flux[win_len]}:00"

    # here we create the array and attributes for 'time'
    t_atts   = {'units'     : 'seconds since {}'.format(tm),
                'delta_t'   : delt_str,
                'long_name' : 'Time offset from midnight',
                'calendar'  : 'standard',}


    bt_atts   = {'units'     : 'seconds since {}'.format(bot),
                 'delta_t'   : delt_str,
                 'long_name' : 'Time offset from base_time',
                 'calendar'  : 'standard',}

    dti = pd.DatetimeIndex(turb_data.index.values)
    delta_ints = np.floor((dti - tm).total_seconds())      # seconds

    t_ind = pd.Int64Index(delta_ints)

    # set the time dimension and variable attributes to what's defined above
    t = netcdf_turb.createVariable('time', 'd','time') # seconds since

    # now we create the array and attributes for 'time_offset'
    bt_dti = pd.DatetimeIndex(turb_data.index.values)   

    bt_delta_ints = np.floor((bt_dti - bot).total_seconds())      # seconds

    bt_ind = pd.Int64Index(bt_delta_ints)

    # set the time dimension and variable attributes to what's defined above
    bt = netcdf_turb.createVariable('time_offset', 'd','time') # seconds since

    # this try/except is vestigial, this bug should be fixed
    t[:]  = t_ind.values
    bt[:] = bt_ind.values

    for att_name, att_val in t_atts.items(): netcdf_turb['time'].setncattr(att_name,att_val)
    for att_name, att_val in bt_atts.items(): netcdf_turb['time_offset'].setncattr(att_name,att_val)

    # loop over all the data_out variables and save them to the netcdf along with their atts, etc
    for var_name, var_atts in turb_atts.items():
         
        # seriously python, seriously????
        if turb_data[var_name].isnull().all():
            if turb_data[var_name].dtype == object: # happens when all fast data is missing...
                turb_data[var_name] = np.float64(turb_data[var_name])     
        elif turb_data[var_name][0].size > 1:
            if turb_data[var_name][0].dtype == object: # happens when all fast data is missing...
                turb_data[var_name] = np.float64(turb_data[var_name])
        else:         
            if turb_data[var_name].dtype == object: # happens when all fast data is missing...
                turb_data[var_name] = np.float64(turb_data[var_name]) 

        # create variable, # dtype inferred from data file via pandas
        var_dtype = turb_data[var_name][0].dtype
        if turb_data[var_name][0].size == 1:
            var_turb  = netcdf_turb.createVariable(var_name, var_dtype, 'time')
            turb_data[var_name].fillna(def_fill_flt, inplace=True)
            # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data)
            var_turb[:] = turb_data[var_name].values
        else:
            if 'fs' in var_name:  
                netcdf_turb.createDimension('freq', turb_data[var_name][0].size)   
                var_turb  = netcdf_turb.createVariable(var_name, var_dtype, ('freq'))
                turb_data[var_name][0].fillna(def_fill_flt, inplace=True)
                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data). this is even stupider in multipple dimensions
                var_turb[:] = turb_data[var_name][0].values      
            else:   
                var_turb  = netcdf_turb.createVariable(var_name, var_dtype, ('time','freq'))
                for jj in range(0,turb_data[var_name].size):
                    turb_data[var_name][jj].fillna(def_fill_flt, inplace=True)
                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data). this is even stupider in multipple dimensions
                tmp = np.empty([turb_data[var_name].size,turb_data[var_name][0].size])
                for jj in range(0,turb_data[var_name].size):
                    tmp[jj,:]=np.array(turb_data[var_name][jj])
                var_turb[:] = tmp         

        # add variable descriptions from above to each file
        for att_name, att_desc in var_atts.items(): netcdf_turb[var_name] .setncattr(att_name, att_desc)

        # add a percent_missing attribute to give a first loop at "data quality"
        perc_miss = fl.perc_missing(var_turb)
        max_val = np.nanmax(var_turb) # masked array max/min/etc
        min_val = np.nanmin(var_turb)
        avg_val = np.nanmean(var_turb)

        netcdf_turb[var_name].setncattr('max_val', max_val)
        netcdf_turb[var_name].setncattr('min_val', min_val)
        netcdf_turb[var_name].setncattr('avg_val', avg_val)
        netcdf_turb[var_name].setncattr('percent_missing', perc_miss)
        netcdf_turb[var_name].setncattr('missing_value', def_fill_flt)

    netcdf_turb.close() # close and write files for today
    return True
    
# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
