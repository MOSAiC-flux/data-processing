# #######################################################################
# 
# Instrument metadata such as heights, event descriptions, etc etc
# are stored in this file in an object that can be queried by instrument
# or variable name e.g. metcity_metadata.get_var_metadata('temp_2m', 'height')
# With the primary purpose of writing that information in a sane way
# to netcdf files in the form of attributes. 
#
#  To quote the original code, finally got to it:
#   
# "...  would like to do this in a more clever way but haven't
#       had the time to get to it"
#    

# #######################################################################
import numpy  as np
import pandas as pd

from datetime  import datetime as date

#from debug_functions import drop_me as dm

pd.options.mode.use_inf_as_na = True # no inf values anywhere 
def metcity_metadata():

    """

    Function returns a "station_info" object (custom class defined at
    bottom) whose job is to track site and instrument metadata by
    date.  This serves as a catalag, mapping a specific instrument and
    then that instrument to its variables... like heights, serial numbers,
    relevant 'events', etc etc etc. All metadata stored as timeseries
    (pd.Series) It probably seems convoluted but it's much more useful 
    than hardcoded arrays scattered around. 

    """

    # if you're interested in editing the heights for a specific instrument, edit this variable 
    # further down in this file at ~ line #  
    site_name         = 'metcity'
    metcity_site      = station_info(site_name=site_name)

    date_twr_raised = date(2019, 10, 24, 5, 30)  # instrument heights after tower raised
    date_twr_raised_leg4 = date(2020, 6, 27)  # instrument heights after tower raised
    metcity_site_info = {} # holder for information to be added to station_info
    metcity_site_info['site_description'] = pd.Series(name='site_description')
    metcity_site_info['site_description'][date(2019,10,15)] = 'MOSAiC "met city" on-ice atmosphere observation station'

    # ####################################################################################
    # important events relevant to met city itself and the instruments there 
    metcity_site_info['events'] = pd.Series(name='events')

    # these are written out as global attrributes by write_ routines
    metcity_site_info['events'][date(2019,10,15)]       = 'met city was born'
    metcity_site_info['events'][date_twr_raised]        = 'raised met tower; sonics N oriented to GPS N'
    metcity_site_info['events'][date(2019,10,26,8,0)]   = '30-m mast raised'
    metcity_site_info['events'][date(2019,11,18,12,50)] = 'mast collapse'
    metcity_site_info['events'][date(2019,12,9,7,30)]   = 'mast raised again with remaining useable tubes to ~23m'
                
    for metadata_name, site_metadata in metcity_site_info.items():
        metcity_site.add_site_metadata(site_metadata)
 
    instrument_info   = {} # dictionary that maps instruments to their params (pd.Series)
    instrument_params = {'height': float, 'serial': str, 'events':str} # instrument parameter categories

    instrument_var_map_dict =  get_metcity_var_map() # key==instr_name, values==list_of_associated_variables
    for instr_name in instrument_var_map_dict: 
        instrument_info[instr_name] = {}
        instr_vars = instrument_var_map_dict[instr_name]
        metcity_site.add_instrument(instr_name, instr_vars)
        for param_name, param_dtype in instrument_params.items(): 
            instrument_info[instr_name][param_name] = pd.Series(name=param_name, dtype=param_dtype)

    # these are events that are important/relevant to data processing
    instrument_info['sonic_2m'] ['events'][date(2019,10,22,5,0)]  = 'replace 2m sonic w spare (S/N 7255)'
    instrument_info['sonic_2m'] ['events'][date(2019,10,29,0,47)] = 'adjusted orientation of 2-m sonic clockwise'
    instrument_info['licor']    ['events'][date(2019,11,1,5,20)]  = 'lowered Licor from 6 m to 2 m'
    instrument_info['FP_a']     ['events'][date(2019,10,24,5,48)] = 'first flux plate installed'
    instrument_info['FP_b']     ['events'][date(2019,10,25,1,25)] = 'second flux plate installed - under Apogee'

    wxt_insts = ['sensor_P_mast', 'sensor_T_mast', 'sensor_Rh_mast']
    for wi in wxt_insts: 
        instrument_info[wi]['events'][date(2019,10,22,1,0)] = 'move WXT away from lowest boom'
        instrument_info[wi]['events'][date(2019,10,26,1,0)] = 'WXT moved to mast'

    mast_insts = wxt_insts+['sonic_mast']
    for mi in mast_insts: 
        instrument_info[mi]['events'][date(2019,10,26,7,0)]   = 'mast raised to 30 m'
        instrument_info[mi]['events'][date(2019,11,18,12,50)] = 'mast collapses'
        instrument_info[mi]['events'][date(2019,12,9,7,30)]   = 'mast raised again with remaining useable tubes to ~23m'

    # mast sonic transitions, dates/times, & heights:
    instrument_info['sonic_mast']['events'][date(2019,10,19,5,49)] = 'sonic placed on tripod' 
    instrument_info['sonic_mast']['events'][date(2019,11,28,4,30)] = 'mast sonic mounted on 2m boom after repair from fall'
    instrument_info['sonic_mast']['events'][date(2019,12,1,9,50)]  = 'sonic on tripod ~14 m from tower'
    
    # ####################################################################################
    sonic_height_on_ground     = (1.15,1.25,1.3) # height from tower base plate (m)
    sensor_T_height_on_ground  = (1.05,1.2,1.25) # height from tower base plate (m)
    sensor_Rh_height_on_ground = (1.05,1.2,1.25) # height from tower base plate (m)

    instrument_info['sonic_2m']      ['height'][date(2019,10,15,0,0)] = sonic_height_on_ground[0]
    instrument_info['sonic_6m']      ['height'][date(2019,10,15,0,0)] = sonic_height_on_ground[1]
    instrument_info['sonic_10m']     ['height'][date(2019,10,15,0,0)] = sonic_height_on_ground[2]
    instrument_info['sensor_T_2m']   ['height'][date(2019,10,15,0,0)] = sensor_T_height_on_ground[0]
    instrument_info['sensor_T_6m']   ['height'][date(2019,10,15,0,0)] = sensor_T_height_on_ground[1]
    instrument_info['sensor_T_10m']  ['height'][date(2019,10,15,0,0)] = sensor_T_height_on_ground[2]
    instrument_info['sensor_Rh_2m']  ['height'][date(2019,10,15,0,0)] = sensor_Rh_height_on_ground[0]
    instrument_info['sensor_Rh_6m']  ['height'][date(2019,10,15,0,0)] = sensor_Rh_height_on_ground[1]
    instrument_info['sensor_Rh_10m'] ['height'][date(2019,10,15,0,0)] = sensor_Rh_height_on_ground[2]
    instrument_info['sensor_P_2m']   ['height'][date(2019,10,15,0,0)] = 1.2
    instrument_info['SR50']          ['height'][date(2019,10,15,0,0)] = 1.0


    # ####################################################################################
    sonic_height_raised     = (2.62, 6.4, 10.34) # height from tower base plate (m)
    sensor_T_height_raised  = (1.75, 5.63, 9.44)  # height from tower base plate (m)
    sensor_Rh_height_raised = (1.46, 5.34, 9.15)  # height from tower base plate (m)
    sensor_P_height_raised  = (1.54, )

    instrument_info['sonic_2m']      ['height'][date_twr_raised] = sonic_height_raised[0]
    instrument_info['sonic_6m']      ['height'][date_twr_raised] = sonic_height_raised[1]
    instrument_info['sonic_10m']     ['height'][date_twr_raised] = sonic_height_raised[2]
    instrument_info['sensor_T_2m']   ['height'][date_twr_raised] = sensor_T_height_raised[0]
    instrument_info['sensor_T_6m']   ['height'][date_twr_raised] = sensor_T_height_raised[1]
    instrument_info['sensor_T_10m']  ['height'][date_twr_raised] = sensor_T_height_raised[2]
    instrument_info['sensor_Rh_2m']  ['height'][date_twr_raised] = sensor_Rh_height_raised[0]
    instrument_info['sensor_Rh_6m']  ['height'][date_twr_raised] = sensor_Rh_height_raised[1]
    instrument_info['sensor_Rh_10m'] ['height'][date_twr_raised] = sensor_Rh_height_raised[2]
    instrument_info['sensor_P_2m']   ['height'][date_twr_raised] = sensor_P_height_raised[0]
    instrument_info['SR50']          ['height'][date_twr_raised] = 2.0

    wxt_insts = ['sensor_P_mast', 'sensor_T_mast', 'sensor_Rh_mast']
    for wi in wxt_insts: 
        instrument_info[wi]['height'][date(2019,10,15,0,0)]   = np.nan     # 1) not mounted yet
        instrument_info[wi]['height'][date(2019,10,19,6,0)]   = 1.1   # 1) WXT on 2-m level on unraised tower                    
        instrument_info[wi]['height'][date(2019,10,22,1,0)]   = 1.5   # 2) WXT put more upright near 8m level on unraised tower  
        instrument_info[wi]['height'][date(2019,10,24,5,30)]  = 2     # 3) tower raised WXT at 2 m height                        
        instrument_info[wi]['height'][date(2019,10,26,1,0)]   = 3.2   # 4) WXT moved to mast tripod                              

    mast_insts = wxt_insts+['sonic_mast']
    for mi in mast_insts: 
        instrument_info[mi]['height'][date(2019,10,26,7,0)]   = 30.76  # 5) mast raised to 30 m                                   
        instrument_info[mi]['height'][date(2019,11,18,12,50)] = 0      # 6) mast collapses (WXT still running)                    
        instrument_info[mi]['height'][date(2019,11,19,10,30)] = np.nan # 7) WXT removed and brought onboard                       
        instrument_info[mi]['height'][date(2019,11,28,5,0)]   = 2      # 8) WXT mounted on 2-mtower boom                          
        instrument_info[mi]['height'][date(2019,12,8,14,0)]   = 17.5   # 9) WXT moved to mast and raised to 23 m                  
        instrument_info[mi]['height'][date(2019,12,9,7,30)]   = 22.37  # 10) reached 23m

    # licor transitions, dates/times, & heights:
    instrument_info['licor']['height'][date(2019,10,15,0,0)]  = np.nan # 0) not mounted yet
    instrument_info['licor']['height'][date(2019,10,19,6,0)]  = 1.5  # 1) on unraised tower at 6-m height
    instrument_info['licor']['height'][date(2019,10,24,5,30)] = 5.18 # 2) on raised tower at 6-m height
    instrument_info['licor']['height'][date(2019,11,1,5,0)]   = 2.35 # 3) moved to two meters... cause it doesn't stay clean


    # ####################################################################################
    # leg4 height changes
    sonic_height_raised     = (2.63, 6.23, 10.33)
    sensor_T_height_raised  = (1.35, 5.49, 9.29)
    sensor_Rh_height_raised = (1.06, 5.2, 9)
 
    instrument_info['sonic_2m']      ['height'][date_twr_raised_leg4] = sonic_height_raised[0]
    instrument_info['sonic_6m']      ['height'][date_twr_raised_leg4] = sonic_height_raised[1]
    instrument_info['sonic_10m']     ['height'][date_twr_raised_leg4] = sonic_height_raised[2]
    instrument_info['sensor_T_2m']   ['height'][date_twr_raised_leg4] = sensor_T_height_raised[0]
    instrument_info['sensor_T_6m']   ['height'][date_twr_raised_leg4] = sensor_T_height_raised[1]
    instrument_info['sensor_T_10m']  ['height'][date_twr_raised_leg4] = sensor_T_height_raised[2]
    instrument_info['sensor_Rh_2m']  ['height'][date_twr_raised_leg4] = sensor_Rh_height_raised[0]
    instrument_info['sensor_Rh_6m']  ['height'][date_twr_raised_leg4] = sensor_Rh_height_raised[1]
    instrument_info['sensor_Rh_10m'] ['height'][date_twr_raised_leg4] = sensor_Rh_height_raised[2]
    instrument_info['sensor_P_2m']   ['height'][date_twr_raised_leg4] = 1.13
    instrument_info['SR50']          ['height'][date_twr_raised_leg4] = 1.93
    instrument_info['licor']         ['height'][date_twr_raised_leg4] = 5.83

    # leg5 height changes
    instrument_info['sensor_T_2m']   ['height'][date(2020, 8, 27, 10, 15)] = 2.06  
    instrument_info['sensor_Rh_2m']  ['height'][date(2020, 8, 27, 10, 15)] = 1.77  
    instrument_info['sensor_P_2m']   ['height'][date(2020, 8, 27, 10, 15)] = 1.85  
    instrument_info['sonic_2m']      ['height'][date(2020, 8, 27, 10, 15)] = 3.01  
    instrument_info['sensor_T_6m']   ['height'][date(2020, 8, 27, 10, 15)] = 5.50  
    instrument_info['sensor_Rh_6m']  ['height'][date(2020, 8, 27, 10, 15)] = 5.21  
    instrument_info['sonic_6m']      ['height'][date(2020, 8, 27, 10, 15)] = 6.26  
    instrument_info['sensor_T_10m']  ['height'][date(2020, 8, 27, 10, 15)] = 9.41  
    instrument_info['sensor_Rh_10m'] ['height'][date(2020, 8, 27, 10, 15)] = 9.12  
    instrument_info['sonic_10m']     ['height'][date(2020, 8, 27, 10, 15)] = 10.07 
    instrument_info['SR50']          ['height'][date(2020, 8, 27, 10, 58)] = 2.21  
    instrument_info['licor']         ['height'][date(2020, 8, 27, 10, 15)] = 5.91  

    # some copy-pastable code for the instruments
    # ###########################################
    # instrument_info['SR50']['height'][date()]
    # instrument_info['IRT']['height'][date()]
    # instrument_info['SPC_sfc']['height'][date()]
    # instrument_info['SPC_10m']['height'][date()]
    # instrument_info['sonic_2m']['height'][date()]
    # instrument_info['sonic_6m']['height'][date()]
    # instrument_info['sonic_10m']['height'][date()]
    # instrument_info['sonic_mast']['height'][date()]
    # instrument_info['sensor_T_2m']['height'][date()]
    # instrument_info['sensor_T_6m']['height'][date()]
    # instrument_info['sensor_T_10m']['height'][date()]
    # instrument_info['sensor_T_mast']['height'][date()]
    # instrument_info['sensor_Rh_2m']['height'][date()]
    # instrument_info['sensor_Rh_6m']['height'][date()]
    # instrument_info['sensor_Rh_10m']['height'][date()]
    # instrument_info['sensor_Rh_mast']['height'][date()]
    # instrument_info['sensor_P_2m']['height'][date()]
    # instrument_info['sensor_P_6m']['height'][date()]
    # instrument_info['sensor_P_10m']['height'][date()]
    # instrument_info['sensor_P_mast']['height'][date()]

    # now put all of the information we've gathored in our var_map into metcity_site
    # so that create_* routines can access this data via metcity_site.get_var_
    for instr_name in instrument_var_map_dict: 
        for param_name, param_dtype in instrument_params.items(): 
            instr_metadata = instrument_info[instr_name][param_name] 
            metcity_site.add_instrument_metadata(instr_name, instr_metadata)

    return metcity_site

def  get_metcity_var_map():


    """
    This function just defines the instrument names and the variables
    that are derived from these instruments at metcity. It's a
    dictionary mapping an instrument name (key) to a list of its
    corresponding output file variables (values). Not called by the
    main program, only separated for clarity.

     List of sensor names defined below for met city:
    'SR50'
    'IRT'
    'SPC_sfc'
    'SPC_10m'
    'sonic_2m'
    'sonic_6m'
    'sonic_10m'
    'sonic_mast'
    'sensor_T_2m'
    'sensor_T_6m'
    'sensor_T_10m'
    'sensor_T_mast'
    'sensor_Rh_2m'
    'sensor_Rh_6m'
    'sensor_Rh_10m'
    'sensor_Rh_mast'
    'sensor_P_2m'
    'sensor_P_6m'
    'sensor_P_10m'
    'sensor_P_mast'
    
    Returns
    -------
    {instr_name_string : var_name_list}

             dictionary containing all instrument names (keys) with
             corresponding list of associated variables (values)

    """

    # this notation just saves space, a loop smashes these together down below
    level_names         = ['2m', '6m', '10m', 'mast']
    multilev_instr_list = ['sonic', 'sensor_T', 'sensor_Rh', 'sensor_P']

    # individual  instruments, not at all levels
    instr_list      = ['SR50', 'IRT', 'SPC_sfc', 'SPC_10m', 'licor'] 

    # now lets map instruments to the vars they measure, so each var gets a height as necessary
    # when the actual file writing is done in main() 
    instr_vars_map= {
        'sonic'     : ['wspd_vec_mean', 'wdir_vec_mean', 
                       'wspd_u_mean', 'wspd_v_mean', 'wspd_z_mean', 'temp_acoustic_mean', 'temp_acoustic_std',
                       'Hs','Cd','ustar','Tstar','zeta_level_n','wu_csp','wv_csp','uv_csp','wT_csp','uT_csp','vT_csp',
                       'phi_u','phi_v','phi_w','phi_T','phi_uT','epsilon_u','epsilon_v','epsilon_w','epsilon',
                       'Phi_epsilon','nSu','nSv','nSw','nSt','Nt','Phi_Nt','Phix','DeltaU','DeltaV','DeltaT','Kurt_u',
                       'Kurt_v','Kurt_w','Kurt_T','Kurt_uw','Kurt_vw','Kurt_wT','Kurt_uT','Skew_u','Skew_v','Skew_w',
                       'Skew_T','Skew_uw','Skew_vw','Skew_wT','Skew_uT','sus','svs','sws','sTs','cwus','cwvs','cuvs',
                       'cwTs','cuTs','cvTs',],
        'sensor_T'  : ['temp'], 
        'sensor_Rh' : ['rh', 'rhi'],
        'sensor_P'  : ['atmos_pressure'], 
        'SR50'      : ['sr50_dist', 'snow_depth'], 
        'IRT'       : ['brightness_temp_surface', 'skin_temp_surface'] , 
        'FP_a'      : [''], 
        'licor'     : ['temp_licor', 'co2_licor', 'h2o_licor', 'pressure_licor', 'Hl'],
        'FP_b'      : [''], 
        'SPC_sfc'   : [''], 
        'SPC_10m'   : [''], 
    }

    # combine multilev and individual instruments into single map
    for inst in multilev_instr_list: 
        for name in level_names:
            instr_list.append(inst+'_'+name)
            var_list = instr_vars_map[inst]
            new_vars = [v+'_'+name for v in var_list]
            instr_vars_map[inst+'_'+name] = new_vars
        instr_vars_map.pop(inst)


    return instr_vars_map

class station_info(object):

    __version__      = "0.1" # it's a βeta, what can I say-yah
    __doc__ = """

    A quick and dirty class to keep track of station/instrument information. 
    This seems like a lot of work but it will make keeping track of our
    sites so much easier, I should have done this from the beginning. A little 
    extra work saves time in the long run. Although, to be fair, there's some missing
    logic here that should be implemented. For example, if you add metadata
    with the same name it overwrites the old data.. doesn't check or append. 

    Parameters:
    ----------
    site_name : string, required

    Example:
    -------
    metcity_station = station_info(site_name='metcity')

    metcity_station.add_instrument('sonic_2m')
    metcity_station.add_instrument('sonic_2m')
    metcity_station.add_instrument_metadata('sonic_2m', pd.Series(name='height')

    metcity_station.get_site_metadata('events', date_of_interest)
    metcity_station.get_var_metadata(var_name, date_of_interest)

    ================================================================================================

    """

    # constructor, including class properties and their defaults
    def __init__(self, verbose: bool=False, *, site_name: str ):  

        self._verbose           = verbose
        self._name              = site_name

        # internal storage for data provided on the site
        # these can be queried by calling functions defined below 

        self._instrument_list= [] # list of instruments that are at site
        self._site_metadata  = {} # dict w/ key==metadata_name, value==pd.Series
        self._var_map        = {} # dict w/ key==var_name, value==instr_name_associated_with_var 
        self._instr_metadata = {} # dict w/ key==instr_name, value==dict(key==name, val==pd.Series)

    def add_site_metadata(self, site_metadata: pd.Series):
        try: 
            site_metadata = site_metadata.sort_index()
            self._site_metadata[site_metadata.name] = site_metadata
        except: raise

    def add_instrument(self, instr_name: str, var_list: list):
        try:
            if instr_name not in self._instrument_list: self._instrument_list.append(instr_name) 
            else: raise Exception
            self._instr_metadata[instr_name] = {}
            for var in var_list: self._var_map[var] = instr_name
        except: raise
 
    def add_instrument_metadata(self, instr_name: str, instr_metadata: pd.Series):
        try: 
            instr_metadata = instr_metadata.sort_index()
            if not instr_name in self._instrument_list:
                raise ValueError('Requested instrument not in station "%s"' % (target_string))
            self._instr_metadata[instr_name][instr_metadata.name] = instr_metadata    
        except: raise  

    def get_instr_metadata(self, instr_name: str, metadata_name: str, date_requested: date=None, ffill: bool=False):
        try: 
            instr_md   = self._instr_metadata[instr_name][metadata_name]
            if date_requested is None: 
                return instr_md, instr_md.index

            if not ffill:
                date_requested = date(date_requested.year, date_requested.month, date_requested.day)
                try:
                    index_date = instr_md.index[instr_md.index.get_loc(date_requested, method='bfill')]
                except KeyError as ke: # only happens if there is no data ahead of this point
                    return None, None

                if date(index_date.year, index_date.month, index_date.day) != date_requested: 
                    return None, None
            else:
                index_date = instr_md.index[instr_md.index.get_loc(date_requested, method='ffill')]

            return instr_md[index_date], index_date
        except: raise 

    def get_var_metadata(self, var_name: str, metadata_name: str, date_requested: date=None, ffill: bool=False):
        try: 
            instr_name = self._var_map[var_name]
            instr_md   = self._instr_metadata[instr_name][metadata_name]
            if date_requested is None: 
                return instr_md, instr_md.index

            if not ffill: 
                date_requested = date(date_requested.year, date_requested.month, date_requested.day)
                try: 
                    index_date = instr_md.index[instr_md.index.get_loc(date_requested, method='bfill')]
                except KeyError as ke: # only happens if there is no data ahead of this point
                    return None, None

                if date(index_date.year, index_date.month, index_date.day) != date_requested: 
                    return None, None
            else:
                index_date = instr_md.index[instr_md.index.get_loc(date_requested, method='ffill')]

            return instr_md[index_date], index_date
        except: raise 

    def get_site_metadata(self, metadata_name: str, date_requested: date=None, ffill: bool=False):
        try: 
            site_md   = self._site_metadata[metadata_name]
            if date_requested is None: 
                return site_md, site_md.index

            if not ffill: 
                date_requested = date(date_requested.year, date_requested.month, date_requested.day)
                try:
                    index_date = site_md.index[site_md.index.get_loc(date_requested, method='bfill')]
                except KeyError as ke: # only happens if there is no data ahead of this point
                    return None, None

                if date(index_date.year, index_date.month, index_date.day) != date_requested: 
                    return None, None
            else:
                index_date = site_md.index[site_md.index.get_loc(date_requested, method='ffill')]

            return site_md[index_date], index_date
        except: raise 
