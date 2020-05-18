#!/usr/bin/python3
code_version = ('0.4β', '5/17/2020', 'mgallagher')
# ############################################################################################
# AUTHORS:
#
#   Michael Gallagher (CIRES/NOAA)  michael.r.gallagher@noaa.gov
#   Christopher Cox (NOAA) christopher.j.cox@noaa.gov
#
#   Many sections based on Matlab code written by O. Persson (CIRES), A. Grachev (CIRES/NOAA), and
#   C. Fairall (NOAA); We thank them for their many contributions.
#
# PURPOSE:
#
# Takes in various MOSAiC data files and outputs a sane NetCDF file that is usable by
# all... should save duplication of effort on the part of multiple scientists and ensure that
# we don't waste time getting to the science. Here raw data files are cleaned up and packaged
# nicely, some new parameters are calculated. This work follows on Ola's first looks at MOSAiC
# observations. This code aims to be clear. If something is unclear, please talk to us about it 
#
# Right now, the read routines for the 20hz fast data (licor/sonic) are written... but the
# data processing component is not... this is the next thing on the list.
#
# TODO:
# ... write 20hz fast data avgs to 1s files and decide on how to package the 20hz files
            # ccox packaged 10 hz files, qc'd, rotated to earth refernce frame and put on a
            # common grid. no 20 hz in netcdf files I think
# ... other attributes for vars in NetCDF files...?
# ... create "event log" class with just a time series of events and dates/times??
# ... put the metek diagnostics into a separate netcdf group... or consider grouping otherwise
# ... do you want to add output of 30 min or 1 hr avgs? might be nice for plotting weeks/months etc
            # sure. 30 min data created for turbulence anyhow. can just add other relevant vars
# ... clean up the calibration stuff (height on ground, height raised, etc)...

# HOWTO:
#
# To run this package with verbose printing over the data from Dec 1st:
# python3 create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201
#
# To profile the code and see what's taking so long:
# python -m cProfile -s cumulative ./create_Daily_Tower_NetCDF.py -v -s 20191201 -e 20191201 -f
#
# UPDATES:
#
# Date: 12/25/2019
# Revision: 0.1 ... the Christmas day data beta ... Merry Christmas!!!
#
# Date: 2/5/2020
# Revision: 0.2 ... cleaned and fixed things up, sent to Chris Cox ... have fun on the Dranitsyn!
#
# Date: 2/15 - 2/30 2020 
# Revision 0.3 by C. Cox presently advancing the Dranitsyn at 0.8 kn with 6 engines on Ludicrous Speed
#   - many updates to metadata; global and variable atts, also added cf names as att when applicable
#   - some modifications to calcs: code is a mix of raw_level_0, qcd_level_1, and derived_level_2:
#       striving to make it level_1 & level_2, minimize the "raw": this will take a few iterations
#   - modified humidity calculations for consistency with vaisala; Wexler
#   - rotation of sonic coordinates to earth reference frame
#   - fast data read/despiking/QC/resampling-by-aggregation 20 Hz -> 10 Hz
#   - Grachev/Fairall turbulence/stress/momentum/MO parameter calculations
#   - and a few odds and ends
#   - "stats" are calculated instead of read to account for changes from coordinate transformations
#       and QC, though a flag can be flipped to read instead. "good*" currently commented out until
#       figure out what we need.
#   - Concerns/questions flagged with !! throughout.
#   - Mast headings and GPS headings need a lot of attention for separate reasons

# Date: 3/1 - XXXX 2020
# Revision 0.4 by M. Gallagher retreating by Dranitsyn like a lepper
#   - minor updates to code, fixed small bugs to allow incomplete days to process (aka today)
#   - allowed days with zero mast data to continue (mid november noodle crash)
#   - fixed indexing of fast data (indexed and selectable by date) 
#   - fixed bugs that stopped setting of attributes for resampled stats of 'fast' data
#   - fixed more bugs that did funny things when running over more than one day of data
#   - fixed bug that causes missing turbulent flux data at midnight boundary
#   - big code refactor code to simplify and modularize, rev 0.4
#   - ... pull out variable definitions for netcdf output into 'define_output_vars.py'
#   - ... pull out flux calculations and put into 'grachev_fluxcapacitor.py'
#   - 'time' is now an 'unlimited' dimension, allows concatenation of files if ever desiredq 
#   - this refactor included some added documentation that might be helpful
#   
# ###############################################################################################

import os, inspect, argparse, time

import numpy  as np
import pandas as pd
import scipy  as sp

from datetime import datetime, timedelta
from numpy    import sqrt
from netCDF4  import Dataset

import warnings; warnings.filterwarnings(action='ignore') # vm python version problems, cleans output....

version_msg = '\n\nPS-122 MOSAiC Met Tower processing code v.'+code_version[0]\
              +', last updates: '+code_version[1]+' by '+code_version[2]+'\n\n'

print('---------------------------------------------------------------------------------------------')
print(version_msg)
print('---------------------------------------------------------------------------------------------')

def main(): # the main data crunching program

    # the date on which the first MOSAiC data was taken... there will be a "seconds_since" variable 
    global beginning_of_time
    beginning_of_time    = datetime(2019,10,15,0,0) # the first day of MOSAiC tower data
    integ_time_turb_flux = 30 # [minutes] the integration time for the turbulent flux calculation
    process_fast_data    = True
    calc_fluxes          = True # if you want to run turbulent flux calculations 
    calc_stats           = True # If False, stats are read from NOAA Services. If True calculated here.
    # should set to True normally because recalculating here accounts for coordinate rotations, QC, and the like

    global data_dir      # make available to the functions at bottom
    global verboseprint  # defines a function that prints only if -v is used when running

    # where do we get the data from
    data_dir   = './tower_data/'
    #data_dir   = '/workstation_data/tower'
    output_dir = data_dir+'/processed_data/'     # where the processed data will be put
    #output_dir = './' # for testing

    # these are subdirs of the data_dir
    metek_bottom_dir = '/Metek02m/'
    metek_middle_dir = '/Metek06m/'
    metek_top_dir    = '/Metek10m/'
    metek_mast_dir   = '/Metek30m/'
    licor_dir        = '/Licor02m/'
    tower_logger_dir = '/CR1000X/daily_files/'

    # constants for calculations
    global nan
    nan      = np.NaN  # make using nans look better
    Rd       = 287     # gas constant for dry air
    K_offset = 273.15  # convert C to K
    h2o_mass = 18      # are the obvious things...
    co2_mass = 44      # ... ever obvious?

    # there are two command line options that effect processing, the start and end date...
    # ... if not specified it runs over all the data. format: '20191001' AKA '%Y%m%d'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_time', metavar='str', help='beginning of processing period, Ymd syntax')
    parser.add_argument('-e', '--end_time', metavar='str', help='end  of processing period, Ymd syntax')

    # add verboseprint function for extra info using verbose flag, ignore these 5 lines if you want
    parser.add_argument('-v', '--verbose', action ='count', help='print verbose log messages')

    args         = parser.parse_args()
    v_print      = print if args.verbose else lambda *a, **k: None
    verboseprint = v_print

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
        if start_time == end_time: # processing current days data, pull out of the dump dir
            tower_logger_dir = '/CR1000X/'

    print('The first day of the experiment is:    %s' % beginning_of_time)
    print('The first day we  process data is:     %s' % start_time)
    print('The last day we will process data is:  %s' % end_time)
    print('---------------------------------------------------------------------------------------------')

    # thresholds! limits that can warn you about bad data!
    # these aren't used yet but should be used to warn about spurious data
    lat_thresh        = (70   ,90)   # limits area where tower can be
    hdg_thresh_lo     = (0    ,360)  # limits on gps heading
    irt_targ_lo       = (-80  ,5)    # IRT surface brightness temperature limits [Celsius]
    sr50d             = (1    ,2.5)  # distance limits from SR50 to surface [m]; install height -1 m or +0.5
    sr50_qc           = (152  ,210)  # reported "quality numbers" 0-151=can't read dist;
                                     # 210-300=reduced signal; 300+=high uncertainty
    flxp              = (-120 ,120)  # minimum and maximum conductive heat flux (W/m2)
    T_thresh          = (-70  ,20)   # minimum & maximum air temperatures (C)
    rh_thresh         = (5    ,130)  # relative humidity (#)
    p_thresh          = (850  ,1100) # air pressure
    ws_thresh         = (0    ,40)   # wind speed from sonics (m/s)
    lic_co2sig_thresh = (85   ,100)  # rough estimate of minimum CO2 signal value corresponding to
                                     # optically-clean window. < 90 = needs cleaned (e.g., salt residue); < ~80?? = ice!
    lic_h2o           = (0    ,100)  # Licor h2o [mg/m3]
    lic_co2           = (0    ,5000) # Licor co2 [g/m3]
    max_bad_paths     = (0.01 ,1)    # METEK: maximum [fraction] of bad paths allowed. (0.01 = 1%), but is
                                     # actually in 1/9 increments. This just says we require all paths to be usable.
    incl_range        = (-90  ,90)   # The inclinometer on the metek
    met_t             = T_thresh     # Vaisala air temperature [C]
    met_rh            = rh_thresh    # Vaisala relative humidity [#]
    met_p             = p_thresh     # Vaisala air pressure [hPa or ~mb]

    # various calibration params
    # ##########################
    # initial distance measurement for sr50 to snow (187.9cm) corrected
    # by 2-m Tvais (-25.7 C) at 0430 UTC Oct 27, 2019
    sr50_init_dist  = sqrt((-25.7+K_offset)/K_offset)*187.9
    sr50_init_depth = 2.3 #snow depth (cm) measured under SR50 at 0430 UTC Oct 27, 2019

    # the following is currently N/A, we don't have the ARM data yet to read in
    #sr30      = (-4,1000) # SWD & SWU [Wm^2]
    #ir20      = (50,400)  # LWD & LWU [Wm^2] (FYI, 315 W/m2 ~ 0 C)
    #ir20_case = (-80,10)  # IR20 instrument case temperature [C]

    # from Ola's original code... these are events that are important/relevant to data processing
    # here they are stored as a list of tuple pairs, (date, event_description)...
    # ... I would like to do this in a more clever way but haven't had the time to get to it
    raise_day = datetime(2019,10,25,5,30) # used elsewhere
    events = []
    events.append( (datetime(2019,10,22,1,0),   'move WXT away from lowest boom') )
    events.append( (datetime(2019,10,22,5,0),   'replace 2m sonic w spare (S/N 7255)') )
    events.append( (datetime(2019,10,24,1,0),   'rotate & calibrate GPS') )
    events.append( (datetime(2019,10,25,1,25),  'put in second flux plate - under Apogee') )
    events.append( (raise_day,                  'raised met tower; sonics N oriented to GPS N') )
    events.append( (datetime(2019,10,26,1,0),   'move WXT to mast') )
    events.append( (datetime(2019,10,26,8,0),   '30-m mast raised') )
    events.append( (datetime(2019,10,29,0,47),  'adjusted orientation of 2-m sonic slightly clockwise') )
    events.append( (datetime(2019,11,1,5,20),   'lowered Licor from 6 m to 2 m') )

    # these are important instrument parameters stored as a list of tuple pairs, (datetime, param_value)
    # #################################################################################################
    # tower instrument heights before tower was raised-estimates, i.e. while laying down... why keep?
    sonic_height_on_ground      = [(1.15,1.25,1.3)] # height from tower base plate (m)
    vasaila_T_height_on_ground  = [(1.05,1.2,1.25)] # height from tower base plate (m)
    vasaila_Rh_height_on_ground = [(1.05,1.2,1.25)] # height from tower base plate (m)
    vasaila_P_height_on_ground  = [(1.2)]
    GPS_height_on_ground        = [(1)]
    SR50_height_on_ground       = [(1)]

    # instrument heights after tower raised
    date_twr_raised = datetime(2019, 10, 24, 5, 30)

    sonic_height_raised      = [(2.66, 5.68, 10.54)] # height from tower base plate (m)
    vasaila_T_height_raised  = [(1.65, 5.44, 9.34)]  # height from tower base plate (m)
    vasaila_Rh_height_raised = [(1.45, 5.24, 9.14)]  # height from tower base plate (m)
    vasaila_P_height_raised  = [(1.65)]
    GPS_height_raised        = [(2)]
    SR50_height_raised       = [(2)]

    # these are the parameters associated with these dates, also stored in a list of tuples
    mast_params = {}
    mast_dates  = []
    mast_index  = 0
    mast_params['mast_hdg'] = []
    mast_params['gps_hdg_mast_setup'] = []
    mast_params['mast_sonic_heights'] = []

    # mast sonic transitions, dates/times, & heights:
    mast_dates.append(datetime(2019,10,19,5,49))  # 1) sonic on tripod
    mast_dates.append(datetime(2019,10,26,7,0))   # 2) raising mast to 30 m
    mast_dates.append(datetime(2019,11,18,12,50)) # 3) mast collapse
    mast_dates.append(datetime(2019,11,28,4,30))  # 4) sonic on stand close to 2-m tower sonic
    mast_dates.append(datetime(2019,12,1,9,50))   # 5) sonic on tripod ~14 m from tower
    mast_dates.append(datetime(2019,12,8,14,00))  # 6) raising mast to 23 m, a pause?
    mast_dates.append(datetime(2019,12,9,7,30))   # 7) reached 23 m

    # Ola says he's guessed at some of these... ... ...
    mast_params['mast_hdg'].append(nan)
    mast_params['mast_hdg'].append(40.7)
    mast_params['mast_hdg'].append(40.7)
    mast_params['mast_hdg'].append(291.2)
    mast_params['mast_hdg'].append(291.2)
    mast_params['mast_hdg'].append(215)
    mast_params['mast_hdg'].append(228)

    mast_params['gps_hdg_mast_setup'].append(nan)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(291.2)
    mast_params['gps_hdg_mast_setup'].append(290)
    mast_params['gps_hdg_mast_setup'].append(291.2)

    mast_params['mast_sonic_heights'].append(3.1)
    mast_params['mast_sonic_heights'].append(31.72)
    mast_params['mast_sonic_heights'].append(nan)
    mast_params['mast_sonic_heights'].append(1.6)
    mast_params['mast_sonic_heights'].append(3.78)
    mast_params['mast_sonic_heights'].append(18.4)
    mast_params['mast_sonic_heights'].append(23.28)

    # sanity check, prolly not necessary
    if len(mast_params['mast_hdg']) != len(mast_dates)\
    or len(mast_params['gps_hdg_mast_setup']) != len(mast_dates)\
    or len(mast_params['mast_sonic_heights']) != len(mast_dates):
        fatal('something went awry... this is not good')

    # make sure we're at the right index for the day we're starting on, where
    if start_time > mast_dates[mast_index]:
        for date in mast_dates:
            if start_time > date and date!= mast_dates[0]:
                mast_index += 1

    # WXT transitions, dates/times, & heights:
    wxt_index   = 0
    wxt_dates   = []
    wxt_heights = []
    wxt_dates.append(datetime(2019,10,19,6,0))   # 1) WXT on 2-m level on unraised tower
    wxt_dates.append(datetime(2019,10,22,1,0))   # 2) WXT put more upright near 8m level on unraised tower
    wxt_dates.append(datetime(2019,10,24,5,30))  # 3) tower raised WXT at 2 m height
    wxt_dates.append(datetime(2019,10,26,1,0))   # 4) WXT moved to mast tripod
    wxt_dates.append(datetime(2019,10,26,7,0))   # 5) mast raised to 30 m
    wxt_dates.append(datetime(2019,11,18,12,50)) # 6) mast collapses (WXT still running)
    wxt_dates.append(datetime(2019,11,19,10,30)) # 7) WXT removed and brought onboard
    wxt_dates.append(datetime(2019,11,28,5,0))   # 8) WXT mounted on 2-mtower boom
    wxt_dates.append(datetime(2019,12,8,14,0))   # 9) WXT moved to mast and raised to 23 m
    wxt_dates.append(datetime(2019,12,9,7,30))   # 10) reached 23m
    wxt_heights.append(1.1)
    wxt_heights.append(1.5)
    wxt_heights.append(2)
    wxt_heights.append(3.2)
    wxt_heights.append(30.76)
    wxt_heights.append(0)
    wxt_heights.append(nan)
    wxt_heights.append(2)
    wxt_heights.append(17.5)
    wxt_heights.append(22.37)
    if len(wxt_heights) != len(wxt_dates):
        fatal('something went awry... this is bad')

    # make sure we're at the right index for the day we're starting on
    if start_time > wxt_dates[wxt_index]:
        for date in wxt_dates:
            if start_time > date and date!= wxt_dates[0]:
                wxt_index += 1

    # licor transitions, dates/times, & heights:
    licor_index   = 0 # used to keep track of where you are in the dates, this is ugly, can't you get the index
    licor_dates   = []
    licor_heights = []
    licor_dates.append(datetime(2019,10,19,6,0))  # 1) on unraised tower at 6-m height
    licor_dates.append(datetime(2019,10,24,5,30)) # 2) on raised tower at 6-m height
    licor_dates.append(datetime(2019,11,1,5,0))   # 3) moved to two meters... cause it doesn't stay clean
    licor_heights.append(1.5)
    licor_heights.append(5.18)
    licor_heights.append(2.35)

    if len(licor_heights) != len(licor_dates):
        fatal('something went awry... this is ... not the best')

    # make sure we're at the right index for the day we're starting on
    if start_time > licor_dates[licor_index]:
        for date in licor_dates:
            if start_time > date and date!= licor_dates[0]:
                licor_index += 1

    global_atts = {                # attributes to be written into the netcdf output file
        'date_created'     :'{}'.format(time.ctime(time.time())),
        'contact'          :'University of Colorado, MOSAiC. matthew.shupe@colorado.edu, PI',
        'keywords'         :'Polar, Arctic, Supersite, Observations, Flux, Atmosphere, MOSAiC',
        'conventions'      :'cf convention variable naming as attribute whenever possible',
        'title'            :'MOSAiC flux group data product ', # blank variables are specific to site characterization
        'institution'      :'CIRES/NOAA',
        'file_creator'     :'Michael R. Gallagher; Christopher J. Cox',
        'creator_email'    :'michael.r.gallagher@noaa.gov; christopher.j.cox@noaa.gov',
        'source'           :'Observations made during the MOSAiC drifting campaign',
        'references'       :'A paper reference here at some point',
        'Funding'          :'Funding sources: National Science Foundation (NSF) Award Number OPP1724551; NOAA Arctic Research Program (ARP)',
        'acknowledgements' :'Dr. Ola Persson (CIRES)',
        'license'          :'Creative Commons Attribution 4.0 License, CC 4.0', 
        'disclaimer'       :'These data do not represent any determination, view, or policy of NOAA or the University of Colorado.',
        'project'          :'PS-122 MOSAiC, ATMOS-MET Team: Thermodynamic and Dynamic Drivers of the Arctic sea ice mass budget at MOSAiC',
        'comment'          :'Preliminary product under development and should not be used for analysis!',
        'version'          :'{}'.format(np.str(code_version[0])+', '+np.str(code_version[1])), 
        # !! matlab reads this as UNSUPPORTED DATA TYPE. No idea why. this was true before when it was just a string
        # !! as well for some reason and the beta isnt the reason.
    }

    # Some specifics for the tubulence file
    global_atts_turb                     = global_atts.copy()
    global_atts_turb['quality_control']  = 'The source data measured at 20 Hz was quality controlled. Variables relevant for quality control of the derived quantities supplied in this file are also supplied, but the derived quantities themselves are NOT quality-controlled.',
    global_atts_turb['methods']          = 'Code developed from routines used by NOAA ETL/PSD3. Original code read_sonic_hr was written by Chris Fairall and later adopted by Andrey Grachev as read_sonic_10Hz_1hr_Tiksi_2012_9m_v2.m, read_sonic_hr_10.m, read_Eureka_sonic_0_hr_2009_egu.m, read_sonic_20Hz_05hr_Materhorn2012_es2',
    global_atts_turb['file_creator']     = 'Michael R. Gallagher; Christopher J. Cox',
    global_atts_turb['references']       = 'Grachev et al. (2013), BLM, 147(1), 51-82, doi 10.1007/s10546-012-9771-0; Grachev et al. (2008) Acta Geophysica. 56(1): 142-166; J.C. Kaimal & J.J. Finnigan "Atmospheric Boundary Layer Flows" (1994)',
    global_atts_turb['acknowledgements'] = 'Dr. Andrey Grachev (CIRES), Dr. Chris Fairall (NOAA), Dr. Ludovic Bariteau (CIRES)'

    # #################################################################################################
    # look at this file for documentation on how the netcdf vars are named and what goes into them 
    # as well as additional information on the syntax/nomenclature used to designate certain things
    from tower_variable_definitions import define_output_variables
    data_out = define_output_variables() # dictionary that maps output var names/properties with data columns
    # all of the data definitions happen in here, go check it out if you need to
    # #################################################################################################
    # Now that everything is defined, we read in the logger data for the date range requested and then do vector
    # operations for data QC, as well as any processing to derive output variables from these data. i.e. no loops

    # read *all* of the tower logger data...? this could be too much. but why have so much RAM if you don't use it?
    logger_data = get_logger_data(tower_logger_dir, start_time, end_time)
    n_entries   = logger_data.size
    if logger_data.empty: # 'fatal' is a print function defined at the bottom of this script that exits
        fatal('No logger data for time range {} ---> {} ?'.format(start_time,end_time))
    logger_data.drop_duplicates(inplace=True) # drop any rows that are duplicated between files due to DAQ issues
    n_entries_after = logger_data.size
    n_removed       = n_entries-n_entries_after
    verboseprint('... there were %s duplicates removed from the logger data in this time range!' % n_removed)

    verboseprint('===================================================')
    verboseprint('Data and observations provided by the tower logger:')
    verboseprint('===================================================')
    if args.verbose: logger_data.info(verbose=True) # must be contained

    # now clean and QC the logger data 'subtleties'. any and all fixing of logger data is done here
    # ###################################################################################################
    # correct apogee_body and apogee_target data, body & targ temperatures were reversed before this time
    apogee_switch_date = datetime(2019,11,12,10,21,29) # Nov. 12th, 10:21::29
    logger_data['apogee_targ_T'] = np.where(logger_data.index < apogee_switch_date,\
                                            logger_data['apogee_body_T'],\
                                            logger_data['apogee_targ_T'])
    logger_data['apogee_body_T'] = np.where(logger_data.index < apogee_switch_date,\
                                            logger_data['apogee_targ_T'],\
                                            logger_data['apogee_body_T'])

    # missing met data comes as '0' instead of NaN... good stuff
    zeros_list = ['vaisala_RH_2m','vaisala_RH_6m','vaisala_RH_10m', 'mast_RH','vaisala_P_2m','mast_P','sr50_dist']
    for param in zeros_list: # make the zeros nans
        logger_data[param] = np.where(logger_data[param]==0.0, nan, logger_data[param])

    temps_list = ['vaisala_T_2m','vaisala_T_6m','vaisala_T_10m','mast_T','apogee_targ_T','apogee_body_T']
    for param in temps_list: # identify when mast T=0 is missing data, this takes some thinking/logic
        potential_inds  = np.where(logger_data[param]==0.0)
        if potential_inds[0].size==0: continue # if empty, do nothing, this is unnecessary
        for ind in potential_inds[0]:
            lo = ind-500
            hi = ind+500
            T_nearby = logger_data[param][lo:hi]
            if np.any(T_nearby < -5) or np.any(T_nearby < 5):    # temps cant go from 0 to +/-5C in 60 seconds
                logger_data[param].iat[ind] = nan
            elif logger_data[param][ind-30:ind+30].count() == 0: # no way all values for a minute are *exactly* 0
                logger_data[param].iat[ind-30:ind+30] = nan

    # here we derive useful parameters computed from logger data that we want to write to the output file
    # ###################################################################################################
    # compute RH wrt ice -- compute RHice(%) from RHw(%), Temperature(deg C), and pressure(mb)
    Td2, h2, a2, x2, Pw2, Pws2, rhi2 = calc_humidity_ptu300(logger_data['vaisala_RH_2m'],\
                                                           logger_data['vaisala_T_2m']+K_offset,
                                                           logger_data['vaisala_P_2m'],
                                                           0)
    logger_data['RHi_vaisala_2m']          = rhi2
    logger_data['enthalpy_vaisala_2m']     = h2
    logger_data['abs_humidity_vaisala_2m'] = a2
    logger_data['pw_vaisala_2m']           = Pw2
    logger_data['MR_vaisala_2m']           = x2

    # atm pressure adjusted assuming 1 hPa per 10 m (1[hPA]*ht[m]/10[m]), except for mast, which has a direct meas.
    p6    = logger_data['vaisala_P_2m']-1*6/10
    p10   = logger_data['vaisala_P_2m']-1*10/10
    pmast = logger_data['mast_P']

    Td6, h6, a6, x6, Pw6, Pws6, rhi6 = calc_humidity_ptu300(logger_data['vaisala_RH_6m'],\
                                                           logger_data['vaisala_T_6m']+K_offset,
                                                           p6,
                                                           0)
    logger_data['RHi_vaisala_6m']          = rhi6
    logger_data['enthalpy_vaisala_6m']     = h6
    logger_data['abs_humidity_vaisala_6m'] = a6
    logger_data['pw_vaisala_6m']           = Pw6
    logger_data['MR_vaisala_6m']           = x6

    Td10, h10, a10, x10, Pw10, Pws10, rhi10 = calc_humidity_ptu300(logger_data['vaisala_RH_10m'],\
                                                                   logger_data['vaisala_T_10m']+K_offset,
                                                                   p10,
                                                                   0)
    logger_data['RHi_vaisala_10m']          = rhi10
    logger_data['enthalpy_vaisala_10m']     = h10
    logger_data['abs_humidity_vaisala_10m'] = a10
    logger_data['pw_vaisala_10m']           = Pw10
    logger_data['MR_vaisala_10m']           = x10

    Tdm, hm, am, xm, Pwm, Pwsm, rhim = calc_humidity_ptu300(logger_data['mast_RH'],\
                                                           logger_data['mast_T']+K_offset,
                                                           logger_data['mast_P'],
                                                           -1)
    logger_data['dewpoint_vaisala_mast']     = Tdm
    logger_data['RHi_vaisala_mast']          = rhim
    logger_data['enthalpy_vaisala_mast']     = hm
    logger_data['abs_humidity_vaisala_mast'] = am
    logger_data['pw_vaisala_mast']           = Pwm
    logger_data['MR_vaisala_mast']           = xm

    # add useful data columns, these were sprinkled throughout Ola's code, like information nuggets
    logger_data['gps_lat_frac'] = logger_data['gps_lat_deg']+logger_data['gps_lat_min']/60.0 # add decimal values
    logger_data['gps_lon_frac'] = logger_data['gps_lon_deg']+logger_data['gps_lon_min']/60.0
    logger_data['gps_hdg']      = logger_data['gps_hdg']/100.0  # convert to degrees
    logger_data['gps_hdg']      = logger_data['gps_hdg'].where(~np.isinf(logger_data['gps_hdg'])) # infinities->nan
    logger_data['gps_alt']      = logger_data['gps_alt']/1000.0 # convert to meters

    # sr50 dist in m & snow depth in cm, both corrected for temperature, snwdpth_meas is height in cm on oct 27 2019
    logger_data['sr50_dist']  = logger_data['sr50_dist']*sqrt((logger_data['vaisala_T_2m']+K_offset)/K_offset)
    logger_data['snow_depth'] = sr50_init_dist-logger_data['sr50_dist']*100\

    # ###################################################################################################
    # OK, all is done with the logger data, now get the 20hz data and put it into its own netcdf file
    # done in a loop because I only have 32GB of RAM in my laptop and there's no sense doing otherwise
    day_series = pd.date_range(start_time, end_time)    # we're going to loop over these days
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we want to go up to but not including 00:00
    # ^lol

    verboseprint("All of the days that we will process:")
    for day in day_series: verboseprint('... %s' % day)

    for today in day_series: # loop over the days in the processing range
        tomorrow  = today+day_delta
        flux_freq = '{}T'.format(integ_time_turb_flux)
        Hz10_today        = pd.date_range(today, tomorrow, freq='0.1S')           # all the 0.1 seconds today, for obs
        seconds_today     = pd.date_range(today, tomorrow, freq='S')              # all the seconds today, for obs
        minutes_today     = pd.date_range(today, tomorrow, freq='T')              # all the minutes today, for obs
        ten_minutes_today = pd.date_range(today, tomorrow, freq='10T')            # all the 10 minutes today, for obs
        flux_time_today   = pd.date_range(today, today+timedelta(1), freq=flux_freq) # flux calc intervals

        # Chris moved this block to the top of the day_series loop because he needed some of the output
        # earlier. Nothing bad happened...  this probably doesn't really need to be a loop
        for this_second in seconds_today:
            # get the right instrument heights for this day... goes in the day loop
            if today < raise_day:
                sonic_z  = sonic_height_on_ground
                Tvais_z  = vasaila_T_height_on_ground
                RHvais_z = vasaila_Rh_height_on_ground
                GPS_z    = vasaila_P_height_on_ground
                Pvais_z  = GPS_height_on_ground
                SR50_z   = SR50_height_on_ground
            else:
                sonic_z  = sonic_height_raised
                Tvais_z  = vasaila_T_height_raised
                RHvais_z = vasaila_Rh_height_raised
                GPS_z    = vasaila_P_height_raised
                Pvais_z  = GPS_height_raised
                SR50_z   = SR50_height_raised

            # has the licor moved today?
            if licor_index+1 < len(licor_dates): # make sure we aren't past the last event
                if today >= licor_dates[licor_index+1]:
                    licor_index +=1
            licor_z = licor_heights[licor_index]

            # has the mast moved today?
            if mast_index+1 < len(mast_dates): # make sure we aren't past the last event
                if today >= mast_dates[mast_index+1]:
                    mast_index += 1
            mast_hdg           = mast_params['mast_hdg'][mast_index]
            gps_hdg_mast_setup = mast_params['gps_hdg_mast_setup'][mast_index]
            mast_sonic_height  = mast_params['mast_sonic_heights'][mast_index]

            # has the wxt moved today?
            if wxt_index+1 < len(wxt_dates): # make sure we aren't past the last event
                if today > wxt_dates[wxt_index+1]:
                    wxt_index += 1
            wxt_z = wxt_heights[wxt_index]

        # before putting the data in, make sure it's indexed for the full time range (i.e. times without obs
        # become NaNs) and select only the data from today to keep in the output file
        logger_data  = logger_data.sort_index()
        logger_today = logger_data[:][today:tomorrow] # does this do what you think?
        logger_today = logger_today.reindex(labels=seconds_today, copy=False)

        # read in the stats from NOAA Services, you're not likely to ever want this
        if calc_stats == False:
            # get metek stats into data frames, statistics are straight from the meteks collected every minute
            # this function can be found at the bottom of this file
            metek_bottom_stats = get_fast_data(metek_bottom_dir, 'stats', today)
            metek_middle_stats = get_fast_data(metek_middle_dir, 'stats', today)
            metek_top_stats    = get_fast_data(metek_top_dir,    'stats', today)
            metek_mast_stats   = get_fast_data(metek_mast_dir,   'stats', today)

            metek_bottom_stats.drop_duplicates(inplace=True) # I don't think this is necessary
            metek_middle_stats.drop_duplicates(inplace=True) # and if it is, then we should also
            metek_top_stats   .drop_duplicates(inplace=True) # understand why there's duplicate data...
            metek_mast_stats  .drop_duplicates(inplace=True)

            metek_bottom_stats = metek_bottom_stats.sort_index()
            metek_middle_stats = metek_middle_stats.sort_index()
            metek_top_stats    = metek_top_stats   .sort_index()
            metek_mast_stats   = metek_mast_stats  .sort_index()

            print(metek_bottom_stats)
            print('=======================')
            print(today)
            print(tomorrow)
            print('=======================')
            print(metek_bottom_stats)
            metek_bottom_stats = metek_bottom_stats[:][today:tomorrow]
            metek_middle_stats = metek_middle_stats[:][today:tomorrow]
            metek_top_stats    = metek_top_stats   [:][today:tomorrow]
            metek_mast_stats   = metek_mast_stats  [:][today:tomorrow]

            metek_bottom_stats = metek_bottom_stats.reindex(index=minutes_today, copy=False)
            metek_middle_stats = metek_middle_stats.reindex(index=minutes_today, copy=False)
            metek_top_stats    = metek_top_stats   .reindex(index=minutes_today, copy=False)
            metek_mast_stats   = metek_mast_stats  .reindex(index=minutes_today, copy=False)

            # calculate wind speed and wind direction
            print('-------------------------------------------------------------------------------------------')
            print('Now calculating windspeed and direction from sonic stats data...')
            bottom_ws, bottom_wd = calculate_metek_ws_wd(metek_bottom_stats.index, metek_bottom_stats['Average_u_velocity'], metek_bottom_stats['Average_v_velocity'], logger_today['gps_hdg'])
            middle_ws, middle_wd = calculate_metek_ws_wd(metek_middle_stats.index, metek_middle_stats['Average_u_velocity'], metek_middle_stats['Average_v_velocity'], logger_today['gps_hdg'])
            top_ws   , top_wd    = calculate_metek_ws_wd(metek_top_stats.index, metek_top_stats['Average_u_velocity'], metek_top_stats['Average_v_velocity'], logger_today['gps_hdg'])
            mast_ws  , mast_wd   = calculate_metek_ws_wd(metek_mast_stats.index, metek_mast_stats['Average_u_velocity'], metek_mast_stats['Average_v_velocity'], logger_today['gps_hdg'], True)

            verboseprint('============================================')
            verboseprint('Data provided by the metek stats generator:')
            verboseprint('============================================')
            if args.verbose: verboseprint(metek_bottom_stats.info(verbose=True)) # has to be contained
            # licor data, also collected through NOAA services, read by the same function, different header
            licor_bottom_stats = get_fast_data(licor_dir, 'stats', today)
            licor_bottom_stats = licor_bottom_stats.sort_index() # order in time because files are random
            licor_bottom_stats.drop_duplicates(inplace=True) # might not be necessary, no duplicates?

            verboseprint('=================')
            verboseprint('Licor stats data:')
            verboseprint('=================')
            if args.verbose: verboseprint(licor_bottom_stats.info(verbose=True)) # must be contained

        # raw data... ~20 Hz data, 5Mb files each hour...
        if process_fast_data:
            #                              !! Important !!
            #   In get_fast_data, the data is first resampled to 10 Hz by averaging then reindexed to a
            #   continuous 10 Hz time grid (NaN at blackouts) of Lenth 60 min x 60 sec x 10 Hz = 36000
            #   Later on (below) we will fill all missing times with the median of the (30 min?) flux sample.

            # ~~~~~~~~~~~~~~~~~~~~ (1) Read the raw data ~~~~~~~~~~~~~~~~~~~~~~~
            #   The data are nominally 20 Hz for MOSAiC, but irregular time stamping
            #   because NOAA Services timestamped to the ~ms at time of processing by Windows OS
            #
            metek_bottom_raw = get_fast_data(metek_bottom_dir, 'raw', today)
            metek_middle_raw = get_fast_data(metek_middle_dir, 'raw', today)
            metek_top_raw    = get_fast_data(metek_top_dir,    'raw', today)
            metek_mast_raw   = get_fast_data(metek_mast_dir, 'raw', today)
            verboseprint('\n===============')
            verboseprint('Metek raw data:')
            verboseprint('===============')
            if args.verbose: verboseprint(metek_bottom_raw.info(verbose=True)) # must be contained
            licor_bottom_raw = get_fast_data(licor_dir, 'raw', today)
            verboseprint('\n================')
            verboseprint('Licor raw data:')
            verboseprint('================')
            if args.verbose: verboseprint(licor_bottom_raw.info(verbose=True)) # must be contained
            print(licor_bottom_raw.head())

            # ~~~~~~~~~~~~~~~~~~~~~ (2) Quality control ~~~~~~~~~~~~~~~~~~~~~~~~
            print('\nQuality controlling the fast data now.')

            # I'm being a bit lazy here: no accouting for reasons data was rejected. For another day.

            # Begin with Metek #################################################

            # Physically-possible limits
            metek_bottom_raw['T'][metek_bottom_raw['T'] < T_thresh[0]]=nan
            metek_bottom_raw['T'][metek_bottom_raw['T'] > T_thresh[1]]=nan
            metek_middle_raw['T'][metek_middle_raw['T'] < T_thresh[0]]=nan
            metek_middle_raw['T'][metek_middle_raw['T'] > T_thresh[1]]=nan
            metek_top_raw['T'][metek_top_raw['T'] < T_thresh[0]]=nan
            metek_top_raw['T'][metek_top_raw['T'] > T_thresh[1]]=nan
            metek_mast_raw['T'][metek_mast_raw['T'] < T_thresh[0]]=nan
            metek_mast_raw['T'][metek_mast_raw['T'] > T_thresh[1]]=nan
            metek_bottom_raw['incx'][np.abs(metek_bottom_raw['incx']) > incl_range[1]]=nan
            metek_bottom_raw['incy'][np.abs(metek_bottom_raw['incy']) > incl_range[1]]=nan
            metek_middle_raw['incx'][np.abs(metek_middle_raw['incx']) > incl_range[1]]=nan
            metek_middle_raw['incy'][np.abs(metek_middle_raw['incy']) > incl_range[1]]=nan
            metek_top_raw['incx'][np.abs(metek_top_raw['incx']) > incl_range[1]]=nan
            metek_top_raw['incy'][np.abs(metek_top_raw['incy']) > incl_range[1]]=nan
            metek_bottom_raw['x'][np.abs(metek_bottom_raw['x']) > ws_thresh[1]]=nan
            metek_bottom_raw['y'][np.abs(metek_bottom_raw['y']) > ws_thresh[1]]=nan
            metek_bottom_raw['z'][np.abs(metek_bottom_raw['z']) > ws_thresh[1]]=nan
            metek_middle_raw['x'][np.abs(metek_middle_raw['x']) > ws_thresh[1]]=nan
            metek_middle_raw['y'][np.abs(metek_middle_raw['y']) > ws_thresh[1]]=nan
            metek_middle_raw['z'][np.abs(metek_middle_raw['z']) > ws_thresh[1]]=nan
            metek_top_raw['x'][np.abs(metek_top_raw['x']) > ws_thresh[1]]=nan
            metek_top_raw['y'][np.abs(metek_top_raw['y']) > ws_thresh[1]]=nan
            metek_top_raw['z'][np.abs(metek_top_raw['z']) > ws_thresh[1]]=nan
            metek_mast_raw['x'][np.abs(metek_mast_raw['x']) > ws_thresh[1]]=nan
            metek_mast_raw['y'][np.abs(metek_mast_raw['y']) > ws_thresh[1]]=nan
            metek_mast_raw['z'][np.abs(metek_mast_raw['z']) > ws_thresh[1]]=nan

            # Diagnostic: break up the diagnostic and search for bad paths. the diagnostic
            # is as follows:
            # 1234567890123
            # 1000096313033
            #
            # char 1-2   = protocol stuff. 10 is actualy 010 and it says we are receiving instantaneous data from network. ignore
            # char 3-7   = data format. we use 96 = 00096
            # char 8     = heating operation mode. we set it to 3 = on but control internally for temp and data quality (ie dont operate the heater if you dont really have to)
            # char 9     = heating state, 0 = off, 1 = on, 2 = on but faulty
            # char 10    = number of unusable radial paths (max 9). we want this to be 0 and it is redundant with the next...
            # char 11-13 = percent of unusuable paths. in the example above, 3033 = 3 of 9 or 33% bad paths
            #
            # We want to strip off the last 3 digits here and remove data that are not all 0s.
            # To do this fast I will do it by subtracting off the top sig figs like below.
            # The minumum value is 1/9 so I will set the threhsold a little > 0 for slop in precision
            # We could set this higher. Perhaps 1 or 2 bad paths is not so bad? Not sure.
            bad_data = (metek_bottom_raw['status']/1000-np.floor(metek_bottom_raw['status']/1000)) >  max_bad_paths[0]
            metek_bottom_raw['x'][bad_data]=nan
            metek_bottom_raw['y'][bad_data]=nan
            metek_bottom_raw['z'][bad_data]=nan
            metek_bottom_raw['T'][bad_data]=nan

            bad_data = (metek_middle_raw['status']/1000-np.floor(metek_middle_raw['status']/1000)) >  max_bad_paths[0]
            metek_middle_raw['x'][bad_data]=nan
            metek_middle_raw['y'][bad_data]=nan
            metek_middle_raw['z'][bad_data]=nan
            metek_middle_raw['T'][bad_data]=nan

            bad_data = (metek_top_raw['status']/1000-np.floor(metek_top_raw['status']/1000)) >  max_bad_paths[0]
            metek_top_raw['x'][bad_data]=nan
            metek_top_raw['y'][bad_data]=nan
            metek_top_raw['z'][bad_data]=nan
            metek_top_raw['T'][bad_data]=nan

            #
            # And now Licor ####################################################
            #

            # Physically-possible limits
            licor_bottom_raw['T'][licor_bottom_raw['T'] < T_thresh[0]]=nan # python is not happy with conventions in ambiguity of "or" im accustomed to in matlab so i split it into two lines
            licor_bottom_raw['T'][licor_bottom_raw['T'] > T_thresh[1]]=nan
            licor_bottom_raw['pr'][licor_bottom_raw['pr'] < p_thresh[0]/10]=nan
            licor_bottom_raw['pr'][licor_bottom_raw['pr'] > p_thresh[1]/10]=nan
            licor_bottom_raw['h2o'][licor_bottom_raw['h2o'] < lic_h2o[0]]=nan
            licor_bottom_raw['h2o'][licor_bottom_raw['h2o'] > lic_h2o[1]]=nan
            licor_bottom_raw['co2'][licor_bottom_raw['co2'] < lic_co2[0]]=nan
            licor_bottom_raw['co2'][licor_bottom_raw['co2'] > lic_co2[1]]=nan

            # CO2 signal strength is a measure of window cleanliness applicable to CO2 and H2O vars
            licor_bottom_raw['co2'][licor_bottom_raw['co2_str'] < lic_co2sig_thresh[0]]=nan
            licor_bottom_raw['h2o'][licor_bottom_raw['co2_str'] < lic_co2sig_thresh[0]]=nan
            licor_bottom_raw['co2'][licor_bottom_raw['co2_str'] > lic_co2sig_thresh[1]]=nan
            licor_bottom_raw['h2o'][licor_bottom_raw['co2_str'] > lic_co2sig_thresh[1]]=nan

            # The diagnostic is coded
            print('Decoding the Licor diagnostics. It\'s fast like the Dranitsyn. Gimme a minute...')
            pll, detector_temp, chopper_temp = decode_licor_diag(licor_bottom_raw['diag'])
            # Phase Lock Loop. Optical filter wheel rotating normally if 1, else "abnormal"
            bad_pll = pll == 0
            # If 0, detector temp has drifted too far from set point. Should yield a bad calibration, I think
            bad_dt = detector_temp == 0
            # Ditto for the chopper housing temp
            bad_ct = chopper_temp == 0
            # Get rid of diag QC failures
            licor_bottom_raw['h2o'][bad_pll]=nan
            licor_bottom_raw['co2'][bad_pll]=nan
            licor_bottom_raw['h2o'][bad_dt]=nan
            licor_bottom_raw['co2'][bad_dt]=nan
            licor_bottom_raw['h2o'][bad_ct]=nan
            licor_bottom_raw['co2'][bad_ct]=nan

            # Despike: meant to replace despik.m by Fairall. Works a little different tho
            #   Here screens +/-5 m/s outliers relative to a running 1 min median
            #
            #   args go like return = despike(input,oulier_threshold_in_m/s,window_length_in_n_samples)
            #
            #   !!!! Replaces failures with the median of the window !!!!
            #
            metek_bottom_raw['x'] = despike(metek_bottom_raw['x'],5,1200)
            metek_bottom_raw['y'] = despike(metek_bottom_raw['y'],5,1200)
            metek_bottom_raw['z'] = despike(metek_bottom_raw['z'],5,1200)
            metek_bottom_raw['T'] = despike(metek_bottom_raw['T'],5,1200)

            metek_middle_raw['x'] = despike(metek_middle_raw['x'],5,1200)
            metek_middle_raw['y'] = despike(metek_middle_raw['y'],5,1200)
            metek_middle_raw['z'] = despike(metek_middle_raw['z'],5,1200)
            metek_middle_raw['T'] = despike(metek_middle_raw['T'],5,1200)

            metek_top_raw['x'] = despike(metek_top_raw['x'],5,1200)
            metek_top_raw['y'] = despike(metek_top_raw['y'],5,1200)
            metek_top_raw['z'] = despike(metek_top_raw['z'],5,1200)
            metek_top_raw['T'] = despike(metek_top_raw['T'],5,1200)

            metek_mast_raw['x'] = despike(metek_mast_raw['x'],5,1200)
            metek_mast_raw['y'] = despike(metek_mast_raw['y'],5,1200)
            metek_mast_raw['z'] = despike(metek_mast_raw['z'],5,1200)
            metek_mast_raw['T'] = despike(metek_mast_raw['T'],5,1200)

            # ~~~~~~~~~~~~~~~~~~~~~~~ (3) Resample  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            print('Resampling 20 Hz -> 10 Hz.')
            #
            # 20 Hz irregular grid -> 10 Hz regular grid
            #
            # The method is to first resample the 20 Hz data to a 10 Hz regular
            # grid using the average of the (expect n=2) points at each 0.1s
            # interval. Then the result is indexed onto a complete grid for the
            # whole day, which is nominally 1 hour = 36000 samples at 10 Hz
            # Missing data (like NOAA Services blackouts) are nan

            metek_bottom_10hz = metek_bottom_raw.resample('100ms').mean()
            metek_bottom_10hz = metek_bottom_10hz.reindex(index=Hz10_today)
            metek_middle_10hz = metek_middle_raw.resample('100ms').mean()
            metek_middle_10hz = metek_middle_10hz.reindex(index=Hz10_today)
            metek_top_10hz    = metek_top_raw.resample('100ms').mean()
            metek_top_10hz    = metek_top_10hz.reindex(index=Hz10_today)
            # if metek_mast_raw.empty: # only the mast has been down for a full day, I think
            #     metek_mast_10hz = pd.DataFrame(index=Hz10_today, columns = )
            #     print(metek_mast_10hz
            # else:
            metek_mast_10hz   = metek_mast_raw.resample('100ms').mean()
            metek_mast_10hz   = metek_mast_10hz.reindex(index=Hz10_today)
            licor_bottom_10hz = licor_bottom_raw.resample('100ms').mean()
            licor_bottom_10hz = licor_bottom_10hz.reindex(index=Hz10_today)

            # ~~~~~~~~~~~~~~~~~ (4) Do the Tilt Rotation  ~~~~~~~~~~~~~~~~~~~~~~
            print('Cartesian tilt rotation. Translating body -> earth coordinates. Caveats! Read in-line comments please! Solution being developed with J. Hutchings.')

            # This really only affects the slow interpretation of the data.
            # When we do the fluxes it will be a double rotation into the streamline that implicitly accounts for deviations between body and earth
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
            #             psi     =  azimuth        is about the z axis. the inclinometer does not measure this despite what the manual may say (it's "aspirational").
            #             metek y -> earth u, +North
            #             metek x -> earth v, +West
            #             Have a look also at pg 21-23 of NEW_MANUAL_20190624_uSonic-3_Cage_MP_Manual for metek conventions. Pg 21 seems to have errors in the diagram?
            #
            #  !! Azimuth is from a linear interpolation of the gps heading. Two questions:
            #       (1) Were the meteks mounted such that metek north = gps north or if not, what is the offset? offset presently assumed = 0
            #       (2) We could calculate the wind direction based on the 1 Hz data, with some code like this:
            #               logger_data['gps_hdg'].reindex(index=Hz10_today, copy=False).interpolate('linear')
            #           However, there is low-frequency variability in the heading information recevied at the gps. The period is roughly
            #           1-2 hours and the standard deviation is 1-1.5 deg. This variability is NOT movement of the ice floe! We saw this in
            #           the GPS when stationary in Boulder and it looks similar at MOSAiC. Jenny H. says it is normal and calls it "noise".
            #           Probably somehow related to the satellite constellation, though it was uncorrelated with GPS qc vars in Colorado.
            #           It is not noise in the conventional sense, but appears very systematic, which makes it something we need to take into account.
            #           In order to avoid propogating the error into the reported wind directions, we need some sort of low-pass filter having an
            #           averaging period that is shorter than significant deviations in the actual heading of the floe but at least ~3 hours.
            #                           For now, I will use the DAILY AVERAGE HEADING!
            #                           Working with J Hutchings to analyze the times scales of floe rotation vs the time scales of GPS HEHDT errors.
            #                           Planning to develop of floe-scale hdg by using multiple GPS acroess the floe to beat down the error

            ct_u, ct_v, ct_w = tilt_rotation(metek_bottom_10hz['incy'],\
                                             metek_bottom_10hz['incx'],\
                                             np.zeros(len(metek_bottom_10hz))+logger_today['gps_hdg'].mean(),\
                                             metek_bottom_10hz['y'],metek_bottom_10hz['x'],metek_bottom_10hz['z'])
            metek_bottom_10hz['y'] = ct_u # y -> u on uSonic!
            metek_bottom_10hz['x'] = ct_v # x -> v on uSonic!
            metek_bottom_10hz['z'] = ct_w
            metek_bottom_10hz.columns = ['status','u','v','w','T','hspd','ts','incx','incy'] # start referring to xyz as uvw now

            ct_u, ct_v, ct_w = tilt_rotation(metek_middle_10hz['incy'],\
                                             metek_middle_10hz['incx'],\
                                             np.zeros(len(metek_middle_10hz))+logger_today['gps_hdg'].mean(),\
                                             metek_middle_10hz['y'],metek_middle_10hz['x'],metek_middle_10hz['z'])
            metek_middle_10hz['y'] = ct_u # y -> u on uSonic!
            metek_middle_10hz['x'] = ct_v # x -> v on uSonic!
            metek_middle_10hz['z'] = ct_w
            metek_middle_10hz.columns = ['status','u','v','w','T','hspd','ts','incx','incy'] # start referring to xyz as uvw now

            ct_u, ct_v, ct_w = tilt_rotation(metek_top_10hz['incy'],\
                                             metek_top_10hz['incx'],\
                                             np.zeros(len(metek_top_10hz))+logger_today['gps_hdg'].mean(),\
                                             metek_top_10hz['y'],metek_top_10hz['x'],metek_top_10hz['z'])
            metek_top_10hz['y'] = ct_u # y -> u on uSonic!
            metek_top_10hz['x'] = ct_v # x -> v on uSonic!
            metek_top_10hz['z'] = ct_w
            metek_top_10hz.columns = ['status','u','v','w','T','hspd','ts','incx','incy'] # start referring to xyz as uvw now

            # !! The mast wind vectors/directions need work.
            #   Byron has v*-1 after swapping x/y, which is the left-hand to right-hand cooridnate swap, which I think is correct, but it isn't working well or consistently
            # No inclinometer up here. For now we are assuming it is plum
            ct_u, ct_v, ct_w = tilt_rotation(np.zeros(len(metek_mast_10hz)),\
                                             np.zeros(len(metek_mast_10hz)),\
                                             np.zeros(len(metek_mast_10hz))+logger_today['gps_hdg'].mean(),\
                                             metek_mast_10hz['x']*-1,metek_mast_10hz['y'],metek_mast_10hz['z'])
                                                  # not sure this ^ is correct: It should be on y

            metek_mast_10hz['x'] = ct_u # x -> u on USA-1!
            metek_mast_10hz['y'] = ct_v # y -> v on USA-1!
            metek_mast_10hz['z'] = ct_w
            metek_mast_10hz.columns = ['u','v','w','T','status']

            # !!
            # Now we recalculate the 1 min average wind direction and speed from the u and v velocities.
            # These values differ from the stats calcs (*_ws and *_wd) in two ways:
            #   (1) The underlying data has been quality controlled
            #   (2) We have rotated that sonic y,x,z into earth u,v,w
            #
            # I have modified the netCDF build to use *_ws_corr and *_wd_corr but have not removed the
            # original calculation because I think it is a nice opportunity for a sanity check. I did
            # move the netCDF organization from above to this code block and I am putting the values
            # into the *_stats data flow and maybe that should be managed in some other way?
            print('Calculating a corrected set of slow wind speed and direction.')

            u_min = metek_bottom_10hz['u'].resample('1T',label='left').apply(take_average)
            v_min = metek_bottom_10hz['v'].resample('1T',label='left').apply(take_average)
            bottom_ws_corr, bottom_wd_corr = calculate_metek_ws_wd(u_min.index, u_min, v_min, logger_today['gps_hdg']*0) # !! we are already in earth coordinates, so hdg = 0!

            u_min = metek_middle_10hz['u'].resample('1T',label='left').apply(take_average)
            v_min = metek_middle_10hz['v'].resample('1T',label='left').apply(take_average)
            middle_ws_corr, middle_wd_corr = calculate_metek_ws_wd(u_min.index, u_min, v_min, logger_today['gps_hdg']*0) # we are already in earth coordinates, so hdg = 0!

            u_min = metek_top_10hz['u'].resample('1T',label='left').apply(take_average)
            v_min = metek_top_10hz['v'].resample('1T',label='left').apply(take_average)
            top_ws_corr, top_wd_corr = calculate_metek_ws_wd(u_min.index, u_min, v_min, logger_today['gps_hdg']*0) # we are already in earth coordinates, so hdg = 0!

            u_min = metek_mast_10hz['u'].resample('1T',label='left').apply(take_average)
            v_min = metek_mast_10hz['v'].resample('1T',label='left').apply(take_average)
            mast_ws_corr, mast_wd_corr = calculate_metek_ws_wd(u_min.index, u_min, v_min, logger_today['gps_hdg']*0+logger_today['gps_hdg'].mean(), True)

            # ~~~~~~~~~~~~~~~~~~ (5) Recalculate Stats ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # !!  Sorry... This is a little messed up. The original stats are read from the NOAA Services stats
            # files, contents calculated from the raw data. But we have QC'd the data and changed the raw
            # values, so we need to update the stats. I do that here. But then was there ever any point in
            # reading the stats data in the first place?
            if calc_stats == True:

                print('Recalculating the NOAA Services style stats data with the corrected, rotated, and quality controlled values.')

                metek_bottom_stats  = pd.DataFrame()
                metek_middle_stats  = pd.DataFrame()
                metek_top_stats     = pd.DataFrame()
                metek_mast_stats    = pd.DataFrame()
                licor_bottom_stats  = pd.DataFrame()

                metek_bottom_stats['wind_speed_metek_2m']       = bottom_ws_corr
                metek_middle_stats['wind_speed_metek_6m']       = middle_ws_corr
                metek_top_stats   ['wind_speed_metek_10m']      = top_ws_corr
                metek_mast_stats  ['wind_speed_metek_mast']     = mast_ws_corr

                metek_bottom_stats['wind_direction_metek_2m']   = bottom_wd_corr
                metek_middle_stats['wind_direction_metek_6m']   = middle_wd_corr
                metek_top_stats   ['wind_direction_metek_10m']  = top_wd_corr
                metek_mast_stats  ['wind_direction_metek_mast'] = mast_wd_corr

                metek_bottom_stats['temp_variance_metek_2m']    = metek_bottom_10hz['T'].resample('1T',label='left').var()
                metek_middle_stats['temp_variance_metek_6m']    = metek_middle_10hz['T'].resample('1T',label='left').var()
                metek_top_stats   ['temp_variance_metek_10m']   = metek_top_10hz['T'].resample('1T',label='left').var()
                metek_mast_stats  ['temp_variance_metek_mast']  = metek_mast_10hz['T'].resample('1T',label='left').var()

                licor_bottom_stats['H2O_licor']                 = licor_bottom_10hz['h2o'].resample('1T',label='left').mean()
                licor_bottom_stats['CO2_licor']                 = licor_bottom_10hz['co2'].resample('1T',label='left').mean()
                licor_bottom_stats['temp_licor']                = licor_bottom_10hz['T'].resample('1T',label='left').mean()
                licor_bottom_stats['pr_licor']                  = licor_bottom_10hz['pr'].resample('1T',label='left').mean()*10 # [to hPa]
                licor_bottom_stats['co2_signal_licor']          = licor_bottom_10hz['co2_str'].resample('1T',label='left').mean()

                metek_bottom_stats['u_metek_2m']                = metek_bottom_10hz['u'].resample('1T',label='left').mean()
                metek_middle_stats['u_metek_6m']                = metek_middle_10hz['u'].resample('1T',label='left').mean()
                metek_top_stats['u_metek_10m']                  = metek_top_10hz['u'].resample('1T',label='left').mean()
                metek_mast_stats['u_metek_mast']                = metek_mast_10hz['u'].resample('1T',label='left').mean()

                metek_bottom_stats['v_metek_2m']                = metek_bottom_10hz['v'].resample('1T',label='left').mean()
                metek_middle_stats['v_metek_6m']                = metek_middle_10hz['v'].resample('1T',label='left').mean()
                metek_top_stats['v_metek_10m']                  = metek_top_10hz['v'].resample('1T',label='left').mean()
                metek_mast_stats['v_metek_mast']                = metek_mast_10hz['v'].resample('1T',label='left').mean()

                metek_bottom_stats['w_metek_2m']                = metek_bottom_10hz['w'].resample('1T',label='left').mean()
                metek_middle_stats['w_metek_6m']                = metek_middle_10hz['w'].resample('1T',label='left').mean()
                metek_top_stats['w_metek_10m']                  = metek_top_10hz['w'].resample('1T',label='left').mean()
                metek_mast_stats['w_metek_mast']                = metek_mast_10hz['w'].resample('1T',label='left').mean()

                metek_bottom_stats['temp_metek_2m']             = metek_bottom_10hz['T'].resample('1T',label='left').mean()
                metek_middle_stats['temp_metek_6m']             = metek_middle_10hz['T'].resample('1T',label='left').mean()
                metek_top_stats['temp_metek_10m']               = metek_top_10hz['T'].resample('1T',label='left').mean()
                metek_mast_stats['temp_metek_mast']             = metek_mast_10hz['T'].resample('1T',label='left').mean()

                metek_bottom_stats['stddev_u_metek_2m']         = metek_bottom_10hz['u'].resample('1T',label='left').std()
                metek_middle_stats['stddev_u_metek_6m']         = metek_middle_10hz['u'].resample('1T',label='left').std()
                metek_top_stats['stddev_u_metek_10m']           = metek_top_10hz['u'].resample('1T',label='left').std()
                metek_mast_stats['stddev_u_metek_mast']         = metek_mast_10hz['u'].resample('1T',label='left').std()

                metek_bottom_stats['stddev_v_metek_2m']         = metek_bottom_10hz['v'].resample('1T',label='left').std()
                metek_middle_stats['stddev_v_metek_6m']         = metek_middle_10hz['v'].resample('1T',label='left').std()
                metek_top_stats['stddev_v_metek_10m']           = metek_top_10hz['v'].resample('1T',label='left').std()
                metek_mast_stats['stddev_v_metek_mast']         = metek_mast_10hz['v'].resample('1T',label='left').std()

                metek_bottom_stats['stddev_w_metek_2m']         = metek_bottom_10hz['w'].resample('1T',label='left').std()
                metek_middle_stats['stddev_w_metek_6m']         = metek_middle_10hz['w'].resample('1T',label='left').std()
                metek_top_stats['stddev_w_metek_10m']           = metek_top_10hz['w'].resample('1T',label='left').std()
                metek_mast_stats['stddev_w_metek_mast']         = metek_mast_10hz['w'].resample('1T',label='left').std()

                metek_bottom_stats['stddev_T_metek_2m']         = metek_bottom_10hz['T'].resample('1T',label='left').std()
                metek_middle_stats['stddev_T_metek_6m']         = metek_middle_10hz['T'].resample('1T',label='left').std()
                metek_top_stats['stddev_T_metek_10m']           = metek_top_10hz['T'].resample('1T',label='left').std()
                metek_mast_stats['stddev_T_metek_mast']         = metek_mast_10hz['T'].resample('1T',label='left').std()

            # ~~~~~~~~~~~~~~~~~~~~ (6) Flux Capacitor  ~~~~~~~~~~~~~~~~~~~~~~~~~
            verboseprint('Calculating turbulent fluxes and associated MO parameters.')
            verboseprint('Turbulent flux code not yet set up for Licor and CLASP :( \n')
            #
            # Rotation to the streamline, FFT window segmentation, detrending,
            # hamming, and computation of power [welch] & cross spectral densities,
            # covariances and associated diagnostics and plots, as well as derived
            # variables (fluxes and stress parameters) are performed within a
            # sub-function called below.
            #
            # turbulence_data = grachev_fluxcapacitor(z_level_nominal,z_level_n,sonic_dir,metek,licor,clasp)
            #       z_level_nominal = nomoinal height nomenclature as a string: '2m', '6m', '10m', or 'mast' so that we can reference unique column names later
            #       z_level_n = Height of measurements in m, being precise because it affects the calculation
            #       sonic_dir = Orientation (azimuth) of the sonic anemoneter relative to true North
            #       flux_time_today = a DatetimeIndex defined earlier and based on integ_time_turb_flux, the integration window for the calculations that is defined at the top of the code
            #       metek = the metek DataFrame
            #       licor = the licor DataFrame - currently unused until we get that coded up
            #       clasp = the clasp data frame - currently unused until we get that coded up
            #
            if calc_fluxes == True:

                for time_i in range(0,len(flux_time_today)-1): # flux_time_today = a DatetimeIndex defined earlier and based on integ_time_turb_flux, the integration window for the calculations that is defined at the top  of the code

                    verboseprint('Processing turbulence data '+np.str(flux_time_today[time_i])+' to '+np.str(flux_time_today[time_i+1]))

                    # Get the index, ind, of the metek frame that pertains to the present calculation This
                    # statement cannot be evaluated with the "and", only one side or the other. wtf?  i =
                    # metek_bottom_10hz.index >= flux_time_today[time_i] and metek_bottom_10hz.index <
                    # flux_time_today[time_i+1] so we have to split it up in this wacky way
                    ind_bot = metek_bottom_10hz.index >= flux_time_today[time_i]
                    ind_mid = metek_middle_10hz.index >= flux_time_today[time_i]
                    ind_top = metek_top_10hz.index >= flux_time_today[time_i]
                    ind_mst = metek_mast_10hz.index >= flux_time_today[time_i]

                    ind_bot[metek_bottom_10hz.index > flux_time_today[time_i+1]] = False
                    ind_mid[metek_middle_10hz.index > flux_time_today[time_i+1]] = False
                    ind_top[metek_top_10hz.index    > flux_time_today[time_i+1]] = False
                    ind_mst[metek_mast_10hz.index   > flux_time_today[time_i+1]] = False

                    # !! tower heading...is this meant to be oriented with the sonic North? like, does this
                    # equal "sonic north"?  
                    # hdg = np.float64(logger_today['gps_hdg'][logger_today['gps_hdg'].index ==
                    # flux_time_today[time_i]])
                    hdg = logger_today['gps_hdg'].mean()

                    # make the turbulent flux calculations via Grachev module
                    from functions_library import grachev_fluxcapacitor
                    v = False
                    if args.verbose: v = True; 
                    data_bot = grachev_fluxcapacitor('2m', sonic_z[0][0], hdg, metek_bottom_10hz[ind_bot], 
                                                     [], [], verbose=v)
                    data_mid = grachev_fluxcapacitor('6m', sonic_z[0][1], hdg, metek_middle_10hz[ind_bot],
                                                     [], [], verbose=v)
                    data_top = grachev_fluxcapacitor('10m', sonic_z[0][2], hdg, metek_top_10hz[ind_bot], 
                                                     [], [], verbose=v)
                    data_mst = grachev_fluxcapacitor('mast', mast_sonic_height, mast_hdg, metek_mast_10hz[ind_bot],
                                                     [], [], verbose=v)
                    if time_i == 0: # doubtless there is a better way to initialize this
                        turbulence_bottom = data_bot
                        turbulence_middle = data_mid
                        turbulence_top    = data_top
                        turbulence_mast   = data_mst
                    else:
                        turbulence_bottom = turbulence_bottom.append(data_bot)
                        turbulence_middle = turbulence_middle.append(data_mid)
                        turbulence_top    = turbulence_top.append(data_top)
                        turbulence_mast   = turbulence_mast.append(data_mst)

                # now add the indexer datetime doohicky
                turbulence_bottom.index = flux_time_today[0:-1] 
                turbulence_middle.index = flux_time_today[0:-1] 
                turbulence_top.index    = flux_time_today[0:-1] 
                turbulence_mast.index   = flux_time_today[0:-1] 

                turb_cols = turbulence_bottom.keys()
                turb_cols = turb_cols.append(turbulence_middle.keys())
                turb_cols = turb_cols.append(turbulence_top.keys())
                turb_cols = turb_cols.append(turbulence_mast.keys())

            else:
                turb_cols = []

            # ~~~~~~~~~~~~~~~~~~~~~~~~ (7) Rename  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # It is necessecary to rename the 10hz data...again. This time it
            # is so that the nomenclature matches what is expected for the netcdf
            metek_bottom_10hz.columns = ['status','u_metek_2m','v_metek_2m','w_metek_2m','temp_metek_2m','hspd','ts','incx','incy'] # start referring to xyz as uvw now
            metek_middle_10hz.columns = ['status','u_metek_6m','v_metek_6m','w_metek_6m','temp_metek_6m','hspd','ts','incx','incy'] # start referring to xyz as uvw now
            metek_top_10hz.columns    = ['status','u_metek_10m','v_metek_10m','w_metek_10m','temp_metek_10m','hspd','ts','incx','incy'] # start referring to xyz as uvw now
            metek_mast_10hz.columns   = ['u_metek_mast','v_metek_mast','w_metek_mast','temp_metek_mast','status']
            licor_bottom_10hz.columns = ['diag','CO2_licor','H2O_licor','temp_licor','pr_licor','co2_str']

        print('---------------------------------------------------------------------------------------------')
        print('Outputting to netcdf files and calcuating averages for day: {}'.format(today))
        print('---------------------------------------------------------------------------------------------')

        netcdf_1sec_name  = '{}/MOSAiC_tower_{}_1sec_preliminary.nc'.format(output_dir,today.strftime('%Y-%m-%d'))
        netcdf_1min_name  = '{}/MOSAiC_tower_{}_1min_preliminary.nc'.format(output_dir,today.strftime('%Y-%m-%d'))
        netcdf_10min_name = '{}/MOSAiC_tower_{}_10min_preliminary.nc'.format(output_dir,today.strftime('%Y-%m-%d'))
        netcdf_10hz_name  = '{}/MOSAiC_tower_{}_10hz_preliminary.nc'.format(output_dir,today.strftime('%Y-%m-%d'))
        netcdf_turb_name  = '{}/MOSAiC_tower_{}_turb_flux_preliminary.nc'.format(output_dir,today.strftime('%Y-%m-%d'))

        # output netcdf4_classic files, for backwards compatibility... can be changed later but has some useful
        # features when using the data with 'vintage' processing code. it's the netcdf3 api, wrapped in hdf5
        netcdf_1sec  = Dataset(netcdf_1sec_name  , 'w', format='NETCDF4_CLASSIC')
        netcdf_1min  = Dataset(netcdf_1min_name  , 'w', format='NETCDF4_CLASSIC')
        netcdf_10min = Dataset(netcdf_10min_name , 'w', format='NETCDF4_CLASSIC')
        netcdf_10hz  = Dataset(netcdf_10hz_name  , 'w', format='NETCDF4_CLASSIC')
        netcdf_turb  = Dataset(netcdf_turb_name  , 'w', format='NETCDF4_CLASSIC')

        file_list = [netcdf_1sec,netcdf_1min,netcdf_10min,netcdf_10hz]
        for att_name, att_val in global_atts.items(): # write the global attributes to each file
            for f in file_list: f.setncattr(att_name, att_val)

        # !! sorry, i have a different set of globals for this file so it isnt in the file list
        for att_name, att_val in global_atts_turb.items(): netcdf_turb.setncattr(att_name, att_val) 

        n_seconds_in_day = 86400
        n_mins_in_day    = 1440
        n_10mins_in_day  = 144
        n_10hz_in_day    = 864000
        n_turb_in_day    = np.int(24*60/integ_time_turb_flux)

        # unlimited dimension to show that time is split over multiple files (makes dealing with data easier)
        netcdf_1sec .createDimension('time', None)# n_seconds_in_day) 
        netcdf_1min .createDimension('time', None)# n_mins_in_day)    
        netcdf_10min.createDimension('time', None)# n_10mins_in_day)  
        netcdf_10hz .createDimension('time', None)# n_10hz_in_day)    
        netcdf_turb .createDimension('time', None)# n_turb_in_day)    

        time_atts_1s   = {'units'     : 'seconds since {}'.format(beginning_of_time),
                          'delta_t'   : '0000-00-00 00:00:01',
                          'long_name' : 'seconds since the first day of MOSAiC',
                          'calendar'  : 'standard',}

        time_atts_1m   = time_atts_1s.copy()
        time_atts_10m  = time_atts_1s.copy()
        time_atts_10hz = time_atts_1s.copy()
        time_atts_turb = time_atts_1s.copy()

        time_atts_1m  ['delta_t']   = '0000-00-00 00:01:00'
        time_atts_10m ['delta_t']   = '0000-00-00 00:10:00'
        time_atts_10hz['delta_t']   = '0000-00-00 00:00:00.10' 
        time_atts_10hz['units']     = 'milliseconds since {}'.format(beginning_of_time)
        time_atts_10hz['long_name'] = 'milliseconds since the first day of MOSAiC'
        time_atts_turb['delta_t']   = '0000-00-00 '+np.str(pd.Timedelta(integ_time_turb_flux,'m')).split(sep=' ')[2] # this is a bit klugy

        bot = beginning_of_time # create the arrays that are 'time since beginning' for indexing netcdf files
        times_1s   = np.floor((pd.date_range(today, tomorrow, freq='s')   - bot).total_seconds())
        times_1m   = np.floor((pd.date_range(today, tomorrow, freq='T')   - bot).total_seconds())
        times_10m  = np.floor((pd.date_range(today, tomorrow, freq='10T') - bot).total_seconds())
        times_10hz = np.floor(((pd.date_range(today, tomorrow, freq='100ms') - bot).total_seconds())*1000)
        times_turb = np.floor(((pd.date_range(today, tomorrow, freq=np.str(integ_time_turb_flux)+'T') - bot).total_seconds()))

        # fix problems with rounding errors for high temporal resolution (occasional errant 0.00000001)
        times_1s   = pd.Int64Index(times_1s)
        times_1m   = pd.Int64Index(times_1m)
        times_10m  = pd.Int64Index(times_10m)
        times_10hz = pd.Int64Index(times_10hz) # we want ints to stick with spec
        times_turb = pd.Int64Index(times_turb)

        # set the time dimension and variable attributes to what's defined above
        time_list = [times_1s,times_1m,times_10m,times_10hz]
        for i in range(0,len(time_list)):
            t    = file_list[i].createVariable('time', 'i','time') # seconds since
            t[:] = time_list[i].values
        # !! sorry, i have a different set of globals for this file...see file list
        t    = netcdf_turb.createVariable('time', 'i','time') # seconds since
        t[:] = times_turb.values


        for att_name, att_val in time_atts_1s.items()   : netcdf_1sec  ['time'].setncattr(att_name,att_val)
        for att_name, att_val in time_atts_1m.items()   : netcdf_1min  ['time'].setncattr(att_name,att_val)
        for att_name, att_val in time_atts_10m.items()  : netcdf_10min ['time'].setncattr(att_name,att_val)
        for att_name, att_val in time_atts_10hz.items() : netcdf_10hz  ['time'].setncattr(att_name,att_val)
        for att_name, att_val in time_atts_turb.items() : netcdf_turb  ['time'].setncattr(att_name,att_val)

        logger_cols = logger_today.keys() # vars in logger file, used to find vars

        max_str_len = 30 # these lines are for printing prettilly

        # loop over all the data_out variables and save them to the netcdf along with their atts, etc
        for var_name, att_dict in data_out.items():      # dict of dicts! write each var to appropriate files
            mosaic_var_name = att_dict.pop('mosaic_var') # removes mosaic_var so it's not written and returns val
            att_dict['height'] = ''                      # add and pop 'height' att cause you haven't finished that
            att_dict.pop('height')                       # this is ugly...

            if mosaic_var_name == 'derived': mosaic_var_name = var_name # same thing, if the var is derived

            mvn = mosaic_var_name # shorten to keep code cleaner below, sorry

            # these ifs *could* be replaced by an attribute that says what file each value is in, this is hacky
            if mvn in logger_cols: # get data from logger file

                var_dtype = logger_today[mvn].dtype # dtype inferred from data file via pandas
                if var_dtype == 'int64': var_dtype = 'i' # netcdf4_classic has no 64bit integers... but thats ok
                var1s     = netcdf_1sec .createVariable(var_name, var_dtype, 'time')
                var1m     = netcdf_1min .createVariable(var_name, var_dtype, 'time')
                var10m    = netcdf_10min.createVariable(var_name, var_dtype, 'time')

                # take averages of logger data and put in files, the 'take_average' function is defined below
                var1s_tmp  = logger_today[mvn]
                var1m_tmp  = logger_today[mvn].resample('1T',label='left') .apply(take_average)
                var10m_tmp = logger_today[mvn].resample('10T',label='left').apply(take_average)

                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas)
                vals_1s = var1s_tmp.values
                var1s[:]  = vals_1s
                var1m[:]  = var1m_tmp .values
                var10m[:] = var10m_tmp.values

                # add variable descriptions from above to each file
                for att_name, att_desc in att_dict.items(): netcdf_1sec[var_name] .setncattr(att_name, att_desc)
                for att_name, att_desc in att_dict.items(): netcdf_1min[var_name] .setncattr(att_name, att_desc)
                for att_name, att_desc in att_dict.items(): netcdf_10min[var_name].setncattr(att_name, att_desc)

                # add a percent_missing attribute to give a first look at "data quality"
                perc_miss = perc_missing(vals_1s)
                netcdf_1sec[var_name].setncattr('percent_missing', perc_miss)
                var_change_str = 'var: {} '.format(mvn)+'-'*(max_str_len-len(mvn)+1)+'> {}'.format(var_name)
                print(var_change_str+' '*(max_str_len-len(var_name)+1)+'({} percent missing)'.format(perc_miss))

                max_val = np.nanmax(var1s) # masked array max/min/etc
                min_val = np.nanmin(var1s)
                avg_val = np.nanmean(var1s)
                netcdf_1sec[var_name]. setncattr('max_val', max_val)
                netcdf_1sec[var_name]. setncattr('min_val', min_val)
                netcdf_1sec[var_name]. setncattr('avg_val', avg_val)
                netcdf_1min [var_name].setncattr('max_val', max_val)
                netcdf_1min [var_name].setncattr('min_val', min_val)
                netcdf_1min [var_name].setncattr('avg_val', avg_val)
                netcdf_10min[var_name].setncattr('max_val', max_val)
                netcdf_10min[var_name].setncattr('min_val', min_val)
                netcdf_10min[var_name].setncattr('avg_val', avg_val)

            elif mvn in turb_cols:

                # get the right data set
                name = mvn.split('_')[-1]
                if name=='2m': 
                    turbulence_data = turbulence_bottom
                elif name=='6m':
                    turbulence_data = turbulence_middle
                elif name=='10m':
                    turbulence_data = turbulence_top
                elif name=='mast':
                    turbulence_data = turbulence_mast

                if turbulence_data[mvn].dtype == object: # happens when all fast data is missing...
                    turbulence_data[mvn] = np.float64(turbulence_data[mvn])

                # create variable, # dtype inferred from data file via pandas
                var_dtype = turbulence_data[mvn].dtype
                var_turb  = netcdf_turb.createVariable(var_name, var_dtype, 'time')

                # convert DataFrame to np.ndarray and pass data into netcdf (netcdf can't handle pandas data)
                var_tmp     = turbulence_data[mvn]
                val_turb    = var_tmp.values
                var_turb[:] = val_turb

                # add variable descriptions from above to each file
                for att_name, att_desc in att_dict.items(): netcdf_turb[var_name] .setncattr(att_name, att_desc)

                # add a percent_missing attribute to give a first look at "data quality"
                perc_miss = perc_missing(val_turb)
                netcdf_turb[var_name].setncattr('percent_missing', perc_miss)
                var_change_str = 'var: {} '.format(mvn)+'-'*(max_str_len-len(mvn)+1)+'> {}'.format(var_name)
                print(var_change_str+' '*(max_str_len-len(var_name)+1)+'({} percent missing)'.format(perc_miss))

                max_val = np.nanmax(var_turb) # masked array max/min/etc
                min_val = np.nanmin(var_turb)
                avg_val = np.nanmean(var_turb)
                netcdf_turb[var_name].setncattr('max_val', max_val)
                netcdf_turb[var_name].setncattr('min_val', min_val)
                netcdf_turb[var_name].setncattr('avg_val', avg_val)

            else: # data not in logger or the turbulence output, get data from metek/licor files

                # !! sorry this is messy. i am getting pretty lost trying to keep track of the netcdf output flow

                var_words      = var_name.split(sep='_') # get var info to choose correct metek data file
                instrument_set = var_words.pop()         # last word should indicate where to get the data

                # get the right data set
                if instrument_set == '2m':
                    stats_data = metek_bottom_stats
                    if process_fast_data: fast_data = metek_bottom_10hz
                elif instrument_set == '6m':
                    stats_data = metek_middle_stats
                    if process_fast_data: fast_data = metek_middle_10hz
                elif instrument_set == '10m':
                    stats_data = metek_top_stats
                    if process_fast_data: fast_data = metek_top_10hz
                elif instrument_set == 'mast':
                    stats_data = metek_mast_stats
                    if process_fast_data: fast_data = metek_mast_10hz
                elif instrument_set == 'licor':
                    stats_data = licor_bottom_stats
                    if process_fast_data: fast_data = licor_bottom_10hz

                else:
                    fatal('Something is wrong, this shouldn\'t happen... can\'t handle var: {}'.format(var_name))

                if mvn in stats_data.keys():  # if mvn is in the stats file, proceed
                    var1m     = netcdf_1min .createVariable(var_name, var_dtype, 'time')
                    var10m    = netcdf_10min.createVariable(var_name, var_dtype, 'time')
                    var_dtype = stats_data[mvn].dtype
                    var1m_tmp  = stats_data[mvn]
                    # take averages of stats data and put in files, the 'take_average' function is defined below
                    var1m_tmp  = stats_data[mvn]
                    var1m_tmp  = var1m_tmp.reindex(index=minutes_today, copy=False)
                    var10m_tmp = stats_data[mvn].resample('10T',label='left').apply(take_average)
                    var10m_tmp = var10m_tmp.reindex(index=ten_minutes_today, copy=False)
                    var1m_vals = var1m_tmp .values
                    var1m[:]   = var1m_vals
                    var10m[:]  = var10m_tmp.values
                    for att_name, att_desc in att_dict.items(): netcdf_1min[var_name] .setncattr(att_name, att_desc)
                    for att_name, att_desc in att_dict.items(): netcdf_10min[var_name].setncattr(att_name, att_desc)

                    # add a percent_missing attribute to give a first look at "data quality"
                    perc_miss = perc_missing(var1m_tmp)
                    netcdf_1min[var_name].setncattr('percent_missing', perc_miss)
                    var_change_str = 'var: {} '.format(mvn)+'-'*(max_str_len-len(mvn)+1)+'> {}'.format(var_name)
                    print(var_change_str+' '*(max_str_len-len(var_name)+1)+'({} percent missing)'.format(perc_miss) )

                if var_name in fast_data.keys(): # if var_name is in the fast file, proceed
                    if process_fast_data:
                        var1s   = netcdf_1sec.createVariable(var_name, var_dtype, 'time')
                        var10hz = netcdf_10hz.createVariable(var_name, var_dtype, 'time')
                        var10hz_tmp = fast_data[var_name]
                        var10hz[:] = var10hz_tmp.values
                        for att_name, att_desc in att_dict.items(): netcdf_10hz[var_name] .setncattr(att_name, att_desc)
                        for att_name, att_desc in att_dict.items(): netcdf_1sec[var_name] .setncattr(att_name, att_desc)
                        # add a percent_missing attribute to give a first look at "data quality"
                        perc_miss = perc_missing(var1s_tmp)
                        max_val = np.nanmax(var1s_tmp) # masked array max/min/etc
                        min_val = np.nanmin(var1s_tmp)
                        avg_val = np.nanmean(var1s_tmp)
                        netcdf_1sec[var_name].setncattr('percent_missing', perc_miss)
                        netcdf_1sec[var_name].setncattr('max_val', max_val)
                        netcdf_1sec[var_name].setncattr('min_val', min_val)
                        netcdf_1sec[var_name].setncattr('avg_val', avg_val)
                        var_change_str = 'var: {} '.format(mvn)+'-'*(max_str_len-len(mvn)+1)+'> {}'.format(var_name)
                        print(var_change_str+' '*(max_str_len-len(var_name)+1)+'({} percent missing)'.format(perc_miss) )
            att_dict['mosaic_var'] = mosaic_var_name # 'unpops' mosaic_var so it is there for next day if we need it

        for f in file_list: f.close() # close and write files for today
        #exit() # only do the first day for now

    print('---------------------------------------------------------------------------------------------')
    print('All done! Netcdf output files can be found in: {}'.format(output_dir))
    print(version_msg)
    print('---------------------------------------------------------------------------------------------')

def get_logger_data(subdir,start_time,end_time):
    logger_data  = pd.DataFrame()
    fuzzy_window = timedelta(2) # we look for files 1 day before and after because we didn't save even days...(?!)
    # fuzzy_window>=2 required for the earlier days of MOSAiC where logger info is spread out across 'daily-ish' files
    print('Getting logger data from: %s' % data_dir+subdir)
    for file in os.listdir(data_dir+subdir):
        if file.endswith('.dat'):
            file_words = file.split(sep='_')
            if file == 'cr1000x_tower.dat':
                use_file = True
                verboseprint('... using the daily file {}'.format(file))
            elif len(file_words) > 2:
                file_date  = datetime.strptime(file_words[2]+file_words[3].strip('.dat'),'%m%d%Y%H%M') # (!)
                if file_date >= (start_time-fuzzy_window) and file_date <= (end_time+fuzzy_window): # weirdness
                    use_file = True
                    verboseprint('... using the file {} from the day: {}'.format(file,file_date))
                else:
                    use_file = False
            else: 
                use_file = False 
            if use_file:
                path  = data_dir+subdir+'/'+file
                na_vals = ['nan','NaN','NAN','NA','\"INF\"','\"-INF\"','\"NAN\"','\"NA','\"NAN','inf','-inf''\"inf\"','\"-inf\"']
                frame = pd.read_csv(path,parse_dates=[0],sep=',',na_values=na_vals,\
                                    index_col=0,header=[1],skiprows=[2,3],engine='c',\
                                    converters={'gps_alt':convert_sci, 'gps_hdop':convert_sci})#,\
                                    #dtype=dtype_dict)
                logger_data = pd.concat([logger_data,frame]) # is concat computationally efficient?
        else:
            warn('There is a logger file I cant use, this makes no sense... {}'.format(file))
    return logger_data.sort_index() # sort logger data (when copied, you lose the file create ordering...)


# gets data that is in the metek format, either 'raw' or 'stats' can but put in as a data_str
def get_fast_data(subdir, data_str, date):
    metek_data = pd.DataFrame()
    day_delta  = pd.to_timedelta(86399999999,unit='us') # we look for files from date+(1day-1microsecond)
    verboseprint('---------------------------------------------------------------------------------------')
    print('Getting fast data from: %s' % data_dir+subdir)
    nfiles = 0

    if data_str == 'stats':
        # manually entered headers for file because... dumb flux, etc.
        if subdir == '/Licor02m/':
            cols = ['ObsTimeStart','NumSamp_blackout','NumError_chopper','NumError_detector','NumError_pll','NumError_sync','Average_agc','GoodSamp_CO2','BadSamp_CO2','Average_CO2','StdDev_CO2','Skewness_CO2','Kurtosis_CO2','GoodSamp_H2O','BadSamp_H2O','Average_H2O','StdDev_H2O','Skewness_H2O','Kurtosis_H2O','GoodSamp_temp','BadSamp_temp','Average_temp','StdDev_temp','GoodSamp_press','BadSamp_press','Average_press','StdDev_press','GoodSamp_CO2_signal','BadSamp_CO2_signal','Average_CO2_signal','StdDev_CO2_signal']
        # 30m metek is serial, so different data stream with less info
        elif subdir == '/Metek30m/':
            cols = ['ObsTimeStart','NumSamp_blackout','GoodSamp_u_velocity','BadSamp_u_velocity','Average_u_velocity','StdDev_u_velocity','Skewness_u_velocity','Kurtosis_u_velocity','GoodSamp_v_velocity','BadSamp_v_velocity','Average_v_velocity','StdDev_v_velocity','Skewness_v_velocity','Kurtosis_v_velocity','GoodSamp_w_velocity','BadSamp_w_velocity','Average_w_velocity','StdDev_w_velocity','Skewness_w_velocity','Kurtosis_w_velocity','GoodSamp_virtual_temp','BadSamp_virtual_temp','Average_virtual_temp','StdDev_virtual_temp','Skewness_virtual_temp','Kurtosis_virtual_temp','GoodSamp_uw','BadSamp_uw','Covariance_uw','GoodSamp_vw','BadSamp_vw','Covariance_vw','GoodSamp_wt','BadSamp_wt','Covariance_wt']
            
        else:# all other meteks are tcp/ip
            cols = ['ObsTimeStart','NumSamp_Blackout','OffSamp_HeatingStatus','OnGoodSamp_HeatingStatus','OnBadSamp_HeatingStatus','BlockSamp_SensorPathStatus','BlockAvg_SensorPathStatus','BlockPctAvg_SensorPathStatus','GoodSamp_u_velocity','BadSamp_u_velocity','Average_u_velocity','StdDev_u_velocity','Skewness_u_velocity','Kurtosis_u_velocity','GoodSamp_v_velocity','BadSamp_v_velocity','Average_v_velocity','StdDev_v_velocity','Skewness_v_velocity','Kurtosis_v_velocity','GoodSamp_w_velocity','BadSamp_w_velocity','Average_w_velocity','StdDev_w_velocity','Skewness_w_velocity','Kurtosis_w_velocity','GoodSamp_virtual_temp','BadSamp_virtual_temp','Average_virtual_temp','StdDev_virtual_temp','Skewness_virtual_temp','Kurtosis_virtual_temp','GoodSamp_uw','BadSamp_uw','Covariance_uw','GoodSamp_vw','BadSamp_vw','Covariance_vw','GoodSamp_wt','BadSamp_wt','Covariance_wt']

    else:
        dtypes = {'mmssuuu': np.str, 'status': np.float64, 'x': np.float64, 'y': np.float64,
                  'z': np.float64, 'T': np.float64, 'hspd': np.float64, 'ts': np.float64, 
                  'incx': np.float64, 'incy': np.float64}
        if subdir == '/Licor02m/':
            cols = ['mmssuuu','diag','co2','h2o','T','pr','co2_str']
        elif subdir == '/Metek30m/':
            cols = ['mmssuuu','x','y','z','T','status']
        else:
            cols   = ['mmssuuu','status','x','y','z','T','hspd','ts','incx','incy']
            
    for file in os.listdir(data_dir+subdir):
        if file.startswith('msc'.format(data_str)) and file.endswith('_{}.txt'.format(data_str)):
            file_words  = file.split(sep='_')
            date_string = file_words[0].strip('msc') # YYYJJJHH

            global metek_file_date # annoying global declartion to give converter access to var
            metek_file_date = datetime.strptime('2'+date_string,'%Y%j%H')

            first_file = True
            if metek_file_date >= (date) and metek_file_date < (date+day_delta):
                nfiles += 1
                if first_file:
                    verboseprint('... using the file {} from the day: {}'.format(file, metek_file_date))
                    first_file = False
                path        = data_dir+subdir+'/'+file
                header_list = None

                if data_str == 'stats':
                    frame = pd.read_csv(path,parse_dates=False,index_col=0,sep='\s+',na_values=['nan','NaN'],\
                                        header=header_list,skiprows=[0,1,2],engine='c',names=cols,\
                                        converters={'ObsTimeStart':convert_metek_timestamp},warn_bad_lines=True)

                else: # raw data, not stats

                    # Read the data. The instructions after the read could be passed to a converter,
                    # but the converter is slow because it loops where these instructions can be vectorized
                    frame       = pd.read_csv(path, parse_dates=False, sep='\s+', na_values=['nan','NaN'],
                                              header=header_list, skiprows=[0], engine='c', names=cols,
                                              dtype=dtypes)
                    # Get this hour's time and make a regular 10 Hz vector where we resample irregular ~20 Hz data
                    noaadate    = frame['mmssuuu']
                    date_now    = ' {}-{}-{}-{}'.format(metek_file_date.year, metek_file_date.month,
                                                        metek_file_date.day,  metek_file_date.hour)

                    # Make a date object from the 20 Hz raw time stamps and add it to the frame
                    time_now    = noaadate+date_now
                    date_object = pd.to_datetime(time_now, format='%M%S%f %Y-%m-%d-%H').rename('dateobj')
                    #date_object = date_object.rename('dateobj')
                    frame       = pd.concat([date_object,frame],axis=1)
                    frame       = frame.set_index('dateobj')

                # put the date from all files into one data frame before giving it back
                metek_data = pd.concat([metek_data,frame]) # is concat computationally efficient?

        else: # found a file that is not an 'msc' file...warn user??
            x = 'do nothing' # placeholder, guess we won't warn the user, sorry user!

    if nfiles == 0: 
        warn('NO FAST DATA FOR {} on {} ... MAKE SENSE??\n\n'.format(subdir,date)\
             +'IS THIS A DAY WHEN THE MAST WAS DOWN? NO? UH OH...')  

        # create a fake 20hz data frame that's empty and return it             
        Hz20_today       = pd.date_range(date, date+day_delta, freq="0.05S") 
        empty_cols = cols+['dateobj']
        empty_cols.remove('mmssuuu')
        frame            = pd.DataFrame(index=Hz20_today, 
                                        columns=empty_cols, 
                                        dtype=np.float64) 
        frame['dateobj'] = Hz20_today
        dateobj          = frame['dateobj'] 
        frame            = frame.set_index('dateobj')
        return frame

    elif nfiles != 24:
        warn('{} of 24 {} {} files available for today {}'.format(nfiles,subdir,data_str,date))

    return metek_data

# calculate wind speeds from appropriate metek columns, heading info is from Ola's code
# this code assumes that 'metek_data' is a fully indexed entire days worth of 'T' frequency data
# !! Chris modified this to pass u,v,data_dates directly to generalize for other dataframes, thanks Chris
def calculate_metek_ws_wd(data_dates, u, v, twr_hdg_data, is_mast=False): # tower heading data is 1s, metek data is 1m
    ws = sqrt(u**2+v**2)
    wd = np.mod(90+np.arctan2(v,-u)*180/np.pi,360)

    if not is_mast: # correct wd for tower heading, averaged across 60 seconds
        for time in data_dates[:]: # there has to be a more clever, non-loop, way of doing this
            avg_twr_hdg = np.nanmean(twr_hdg_data[time:time+timedelta(seconds=60)])
            old_wd = wd[time]
            wd[time]    = np.mod(wd[time]+avg_twr_hdg, 360)

    else: # correct for mast heading by comparing obs of mast orientation wrt tower, a bit more complicated

        # From Ola's code, Ola says he's guessed at some of these... ... ...
        hdg_dates   = [datetime(2019,10,19,5,49) , datetime(2019,10,26,7,0) , datetime(2019,11,18,12,50),\
                       datetime(2019,11,28,4,30) , datetime(2019,12,1,9,50) , datetime(2019,12,8,14,00),\
                       datetime(2019,12,9,7,30)]
        hdg_vals    = {'mast_hdg' : [nan, 40.7, 40.7, 291.2, 291.2, 215, 228],
                       'gps_hdg'  : [nan, 291.2, 291.2, 291.2, 291.2, 290, 291.5], # 'gps_hdg_mast_setup'??
                       'date'     : hdg_dates,}
        mast_hdg_df = pd.DataFrame(hdg_vals, index=hdg_dates)

        this_day = data_dates[0].normalize() # compare data timestamp to hdg_dates with normalize
        mast_hdg_df.index = mast_hdg_df.index.normalize() # mast heading changed today
        if this_day in mast_hdg_df.index.values: # mast heading changed today
            verboseprint('heading changed today {}'.format(this_day))
            before_change_time = mast_hdg_df[beginning_of_time:this_day+timedelta(1)].iloc[-2]
            after_change_time  = mast_hdg_df[beginning_of_time:this_day+timedelta(1)].iloc[-1]
            for time in data_dates[:]: # there has to be a more clever, non-loop, way of doing this

                if time < after_change_time['date']:
                    mast_hdg = before_change_time['mast_hdg']
                    gps_hdg  = before_change_time['gps_hdg']
                else:
                    mast_hdg = after_change_time['mast_hdg']
                    gps_hdg  = after_change_time['gps_hdg']

                avg_twr_hdg = np.nanmean(twr_hdg_data[time:time+timedelta(seconds=60)])
                wd[time]    = np.mod(wd[time]+(mast_hdg+(avg_twr_hdg-gps_hdg)),360)
    # Ola's code: wd_mtk30(igdmtk30(i))=mod(sd(2)+(mast_hdg+(gps_hdg_twr(igdmtk30(i))-gps_hdg_mast_setup)),360);

        else: # heading didn't change, use the most recent heading from mast_hdg_df above
            most_recent_gps  = mast_hdg_df[beginning_of_time:this_day].iloc[-1]['gps_hdg']
            most_recent_mast = mast_hdg_df[beginning_of_time:this_day].iloc[-1]['mast_hdg']
            for time in data_dates[:]: # there has to be a more clever, non-loop, way of doing this
                avg_twr_hdg = np.nanmean(twr_hdg_data[time:time+timedelta(seconds=60)])
                wd[time]    = np.mod(wd[time]+(most_recent_mast+(avg_twr_hdg-most_recent_gps)), 360)

    return ws, wd

# this is the function that averages for the 1m and 10m averages, could be more complex
def take_average(array_like_thing):
    # should we put a cutoff on the number of allowed missing values for an average before it's meaningless
    # i.e. if you're averaging over 10 minutes and only have one non-NaN value... what do you do?
    if array_like_thing.size == 0:
        return nan
    else:
        return np.nanmean(array_like_thing)

# despiker
def despike(spikey_panda, thresh, filterlen):
    # outlier detection from a running median !!!! Replaces outliers with that median !!!!
    tmp                    = spikey_panda.rolling(window=filterlen, center=True).median()
    spikes_i               = (np.abs(spikey_panda - tmp)) > thresh
    spikey_panda[spikes_i] = tmp
    return spikey_panda

# convert the timestamp in metek files to something usable, this is slow and only used for noaa 'stats' files
def convert_metek_timestamp(array_like_thing):
    # var 'metek_file date' was declared global in 'get_fast_data' function, sketchy!
    date_now = ' {}-{}-{}'.format(metek_file_date.year, metek_file_date.month, metek_file_date.day)
    time_now = array_like_thing.split('-')[0].rpartition(':')[0]
    time_now = metek_file_date.strftime('%H')+':'+time_now+date_now
    date_object = pd.to_datetime(time_now, format='%H:%M:%S %Y-%m-%d')
    return date_object

# annoying, convert E to e so that python recognizes scientific notation in logger files...
def convert_sci(array_like_thing):
    return np.float64(array_like_thing.replace('E','e'))

def decode_licor_diag(raw_diag):

    # licor diagnostics are encoded in the binary of an integer reported by the sensor. the coding is described
    # in Licor Technical Document, 7200_TechTip_Diagnostic_Values_TTP29 and unpacked here.
    licor_diag    = np.int16(raw_diag)
    pll           = licor_diag*nan
    detector_temp = licor_diag*nan
    chopper_temp  = licor_diag*nan
    for i in range(0,len(licor_diag)):
        licor_diag_bin = bin(licor_diag[i]) # why the %$@$)* can't this be vectorized? This loop is slow
        b1 = np.int(licor_diag_bin[2])
        b2 = np.int(licor_diag_bin[3])
        b3 = np.int(licor_diag_bin[4])
        pll[i] = b3 # PLL: 1 = good, 0 = bad
        detector_temp[i] = b2 # temp near set point = 1, not near set point = 0
        chopper_temp[i]  = b1 # temp near set point = 1, not near set point = 0
        # Can do this to for co2_signal_strength, but we recorded that elsewhere so commented out to save time
        #b4 = np.int(licor_diag_bin[5])
        #b5 = np.int(licor_diag_bin[6])
        #b6 = np.int(licor_diag_bin[7])
        #b7 = np.int(licor_diag_bin[8])
        #b8 = np.int(licor_diag_bin[9])
        #ss[i] = 6.67*(b5*2**3+b6*2**2+b2*2**1+b8*2**0) # in percent, the signal strength. we will ignore and report the value
    return pll, detector_temp, chopper_temp

# calculate humidity variables following Vaisala
def calc_humidity_ptu300(RHw, temp, press, Td):

    # Calculations based on Appendix B of the PTU/HMT manual to be mathematically consistent with the
    # derivations in the on onboard electronics. Checked against Ola's code and found acceptable
    # agreement (<0.1% in MR). RHi calculation is then made following Hyland & Wexler (1983), which
    # yields slightly higher (<1%) compared a different method of Ola's

    # calculate saturation vapor pressure (Pws) using two equations sets, Wexler (1976) eq 5 & coefficients
    c0    = 0.4931358
    c1    = -0.46094296*1e-2
    c2    = 0.13746454*1e-4
    c3    = -0.12743214*1e-7
    omega = temp - ( c0*temp**0 + c1*temp**1 + c2*temp**2 + c3*temp**3 )

    # eq 6 & coefficients
    bm1 = -0.58002206*1e4
    b0  = 0.13914993*1e1
    b1  = -0.48640239*1e-1
    b2  = 0.41764768*1e-4
    b3  = -0.14452093*1e-7
    b4  = 6.5459673
    Pws = np.exp( ( bm1*omega**-1 + b0*omega**0 + b1*omega**1 + b2*omega**2 + b3*omega**3 ) + b4*np.log(omega) ) # [Pa]

    Pw = RHw*Pws/100 # # actual vapor pressure (Pw), eq. 7, [Pa]

    x = 1000*0.622*Pw/((press*100)-Pw) # mixing ratio by weight (eq 2), [g/kg]

    # if we no dewpoint available (WXT!) then calculate it, else no need to worry about it
    if Td == -1:   # dewpoint (frostpoint), we are assuming T ambient < 0 C, which corresponds to these coefs:
        A = 6.1134
        m = 9.7911
        Tn = 273.47
        Td = Tn / ((m/np.log10((Pw/100)/A)) - 1) # [C] (temperature, not depression!)

    # else: do nothing if arg 4 is any other value and input flag will be returned.
    a = 216.68*(Pw/temp) # # absolute humidity, eq 3, [g/m3]

    h = (temp-273.15)*(1.01+0.00189*x)+2.5*x # ...and enthalpy, eq 4, [kJ/kg]

    # RHi, the saturation vapor pressure over ice, then finally RHI, Hyland & Wexler (1983)
    c0 = -5.6745359*1e3     # coefficients
    c1 = 6.3925247
    c2 = -9.6778430*1e-3
    c3 = 6.2215701*1e-7
    c4 = 2.0747825*1e-9
    c5 = -9.4840240*1e-13
    D  = 4.1635019

    # calculate
    term = (c0*temp**(-1)) + (c1*temp**(0)) + (c2*temp**1) + (c3*temp**2) + (c4*temp**3)+(c5*temp**4)

    # calculate saturation vapor pressure over ice
    Psi = np.exp(term + (D*np.log(temp)))  # Pa

    # convert to rhi
    rhi = 100*(RHw*0.01*Pws)/Psi

    return Td, h, a, x, Pw, Pws, rhi

def tilt_rotation(ct_phi,ct_theta,ct_psi,ct_up,ct_vp,ct_wp):

    # This subroutine rotates a vector from one cartesian basis to another, based upon the
    # three Euler angles, defined as rotations around the reference axes, xyz.

    # Rotates the sonic winds from body coordinates to earth coordinates.  This is the tild
    # rotation that corrects for heading and the tilt of the sonic reltive to plum.

    # y,x,z in -> u,v,w out

    # This differs from the double rotation into the plane of the wind streamline that is
    # needed for the flux calculations and is performed in the grachev_fluxcapacitor. The
    # output from this rotation is the best estimate of the actual wind direction, having
    # corrected for both heading and contributions to the horizontal wind by z

    # Adapted from coord_trans.m (6/27/96) from Chris Fairall's group by C. Cox 2/22/20
    #
    #  phi   = about inclinometer y/u axis (anti-clockwise about Metek north-south) (roll)
    #  theta = about inclinometer x/v axis (anti-clockwise about Metek east-west) (pitch)
    #  psi   = about z/w axis (yaw, "heading")

    # calculations are in radians, but inputs are in degrees
    ct_phi   = np.radians(ct_phi)
    ct_theta = np.radians(ct_theta)
    ct_psi   = np.radians(ct_psi)

    ct_u = ct_up*np.cos(ct_theta)*np.cos(ct_psi)\
           + ct_vp*(np.sin(ct_phi)*np.sin(ct_theta)*np.cos(ct_psi)-np.cos(ct_phi)*np.sin(ct_psi))\
           + ct_wp*(np.cos(ct_phi)*np.sin(ct_theta)*np.cos(ct_psi)+np.sin(ct_phi)*np.sin(ct_psi))

    ct_v = ct_up*np.cos(ct_theta)*np.sin(ct_psi)\
           + ct_vp*(np.sin(ct_phi)*np.sin(ct_theta)*np.sin(ct_psi)+np.cos(ct_phi)*np.cos(ct_psi))\
           + ct_wp*(np.cos(ct_phi)*np.sin(ct_theta)*np.sin(ct_psi)-np.sin(ct_phi)*np.cos(ct_psi))

    ct_w = ct_up*(-np.sin(ct_theta))\
           + ct_vp*(np.cos(ct_theta)*np.sin(ct_phi))\
           + ct_wp*(np.cos(ct_theta)*np.cos(ct_phi))

    return ct_u, ct_v, ct_w
 
def num_missing(series):
    # return series.count()-series.size
    return np.count_nonzero(series==np.NaN)

def perc_missing(series):
    return np.round((np.count_nonzero(np.isnan(series))/float(series.size))*100.0, decimals=4)

# functions to make grepping lines easier, differentiating between normal output, warnings, and fatal errors
def warn(string):
    max_line = len(max(string.splitlines(), key=len))
    print('')
    print("!! Warning: {} !!".format("!"*(max_line)))
    for line in string.splitlines():
        print("!! Warning: {} {}!! ".format(line," "*(max_line-len(line))))
    print("!! Warning: {} !!".format("!"*(max_line)))
    print('')

def fatal(string):
    max_line = len(max(string.splitlines(), key=len))
    print('')
    print("!! FATAL {} !!".format("!"*(max_line)))
    for line in string.splitlines():
        print("!! FATAL {} {}!! ".format(line," "*(max_line-len(line))))
    center_off = int((max_line-48)/2.)
    if center_off+center_off != (max_line-len(line)):
        print("!! FATAL {} I'm sorry, but this forces an exit... goodbye! {} !!".format(" "*center_off," "*(center_off)))
    else:
        print("!! FATAL {} I'm sorry, but this forces an exit... goodbye! {} !!".format(" "*center_off," "*center_off))
    print("!! FATAL {} !!".format("!"*(max_line)))
    exit()

# this runs the function main as the main program... this is a hack that allows functions
# to come after the main code so it presents in a more logical, C-like, way
if __name__ == '__main__':
    main()
