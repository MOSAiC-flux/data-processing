# ############################################################################################
#
# This file does the heady work of defining the attributes of the parameters observed at the
# flux stations to variable names that make it into the netcdf files.  This file is where you
# can change anything that doesn't look right in the netcdf files. Caveat!: the variable
# names used here are also used in the "create" code that actually builds the netcdf file. If
# you want to change a variable name, please run the "change_code_var_name" script and it will
# find/replace all instances in both pieces of code, here *and* in the "create" code
#
# But! Changing attributes shouldn't affect the create code, so hack away on that. Please use
# only single quotes for variable names and related attributes.
# 
# ############################################################################################

import time
import numpy as np

# some of the 'create' code assumes that the first entry in the
# variable dictionaries is the time dimension. it's special for stupid
# pandas reasons ... you can't refer to a dataframe index by its name
# ... so order matters.
from collections import OrderedDict

def code_version():
    cv = ('0.2β', '6/12/2020', 'mgallagher')
    return cv

# file_type must be "slow", "fast", "level2", or "turb"
def define_global_atts(station_name, file_type):
    cv = code_version()
    # global attributes to be written into the netcdf output file
    global_atts = {                
        'date_created'     :'{}'.format(time.ctime(time.time())),
        'station'          :'data taken at remote flux station {}'.format(station_name),
        'contact'          :'University of Colorado, MOSAiC. matthew.shupe@colorado.edu, PI',
        'keywords'         :'Polar, Arctic, Supersite, Observations, Flux, Atmosphere, MOSAiC',
        'conventions'      :'cf convention variable naming as attribute whenever possible',
        'title'            :'MOSAiC flux group data product ', # blank variables are specific to site characterization
        'institution'      :'CIRES/NOAA',
        'file_creator'     :'Michael R. Gallagher; Christopher J. Cox, Ola Persson ',
        'creator_email'    :'michael.r.gallagher@noaa.gov; christopher.j.cox@noaa.gov; ola.persson@noaa.gov',
        'source'           :'Observations made during the MOSAiC drifting campaign',
        'references'       :'A paper reference here at some point',
        'Funding'          :'Funding sources: National Science Foundation (NSF) Award Number OPP1724551; NOAA Arctic Research Program (ARP)',
        'acknowledgements' :'',
        'license'          :'Creative Commons Attribution 4.0 License, CC 4.0', 
        'disclaimer'       :'These data do not represent any determination, view, or policy of NOAA or the University of Colorado.',
        'project'          :'PS-122 MOSAiC, ATMOS Flux Team: Thermodynamic and Dynamic Drivers of the Arctic sea ice mass budget at MOSAiC',
        'comment'          :'Preliminary product under development and should not be used for analysis without consultation!',
        'version'          :'{}'.format(np.str(cv[0])+', '+np.str(cv[1])), 
        # !! matlab reads this as UNSUPPORTED DATA TYPE. No idea why. this was true before when it was just a string
        # !! as well for some reason and the beta isnt the reason.
    }

    if file_type == "slow":
        global_atts['quality_control']  = 'This Level 1 product is for archival purposes and has undergone minimal data processing and quality control, please contact the authors/PI if you would like to know more.',

    elif file_type == "fast":
        global_atts['quality_control']  = 'This "Level 1" product is for archival purposes and has undergone minimal data processing and quality control, please contact the authors/PI if you would like to know more.',

    elif file_type == "level2":
        global_atts['quality_control']  = 'Significant quality control in place for the observations used in the derived products. This Level 2 data is processed in many significant ways and this particular version is *for preliminary results only*. Please have discussions with the authors about what this means if you would like to use it this data for any analyses.',

    elif file_type == "turb":  # some specifics for the tubulence file
        global_atts['quality_control']  = 'The source data measured at 20 Hz was quality controlled. Variables relevant for quality control of the derived quantities supplied in this file are also supplied, but the derived quantities themselves are NOT quality-controlled.',
        global_atts['methods']          = 'Code developed from routines used by NOAA ETL/PSD3. Original code read_sonic_hr was written by Chris Fairall and later adopted by Andrey Grachev as read_sonic_10Hz_1hr_Tiksi_2012_9m_v2.m, read_sonic_hr_10.m, read_Eureka_sonic_0_hr_2009_egu.m, read_sonic_20Hz_05hr_Materhorn2012_es2',
        global_atts['references']       = 'Grachev et al. (2013), BLM, 147(1), 51-82, doi 10.1007/s10546-012-9771-0; Grachev et al. (2008) Acta Geophysica. 56(1): 142-166; J.C. Kaimal & J.J. Finnigan "Atmospheric Boundary Layer Flows" (1994)',
        global_atts['acknowledgements'] = 'Dr. Andrey Grachev (CIRES), Dr. Chris Fairall (NOAA), Dr. Ludovic Bariteau (CIRES)'

    return OrderedDict(global_atts)

# defines the column names of the logger data for the flux stations and thus also the output variable names in
# the level1 data files that are supposed to be "nearly-raw netcdf records". this returns two things. 1) a list of dictionaries
# where the key is the variable name and dictionary is a list of netcdf attributes. 2) a list of variable names
def define_level1_slow():  

    lev1_slow_atts = OrderedDict()
    # units defined here, other properties defined in 'update' call below
    lev1_slow_atts['TIMESTAMP']                    = {'units' : 'TS'}           
    lev1_slow_atts['gps_lat_deg_Avg']              = {'units' : 'deg'}          
    lev1_slow_atts['gps_lat_min_Avg']              = {'units' : 'min'}          
    lev1_slow_atts['gps_lon_deg_Avg']              = {'units' : 'deg'}          
    lev1_slow_atts['gps_lon_min_Avg']              = {'units' : 'min'}          
    lev1_slow_atts['gps_hdg_Avg']                  = {'units' : 'deg'}          
    lev1_slow_atts['gps_alt_Avg']                  = {'units' : 'm'}            
    lev1_slow_atts['gps_qc']                       = {'units' : '?'}            
    lev1_slow_atts['gps_hdop_Avg']                 = {'units' : 'unitless'}     
    lev1_slow_atts['gps_nsat_Avg']                 = {'units' : 'N'}            
    lev1_slow_atts['metek_InclX_Avg']              = {'units' : 'deg'}          
    lev1_slow_atts['metek_InclY_Avg']              = {'units' : 'deg'}          
    lev1_slow_atts['PTemp_Avg']                    = {'units' : 'degC'}         
    lev1_slow_atts['batt_volt_Avg']                = {'units' : 'V'}            
    lev1_slow_atts['counts_main_Tot']              = {'units' : 'N'}            
    lev1_slow_atts['call_time_mainscan_Max']       = {'units' : 'mSec'}         
    lev1_slow_atts['call_time_modbus_sr301_Max']   = {'units' : 'mSec'}         
    lev1_slow_atts['call_time_modbus_sr302_Max']   = {'units' : 'mSec'}         
    lev1_slow_atts['call_time_modbus_vaisala_Max'] = {'units' : 'mSec'}         
    lev1_slow_atts['call_time_sdi1_Max']           = {'units' : 'mSec'}         
    lev1_slow_atts['call_time_sdi2_Max']           = {'units' : 'mSec'}         
    lev1_slow_atts['call_time_efoy_Max']           = {'units' : 'mSec'}         
    lev1_slow_atts['sr30_swu_DegC_Avg']            = {'units' : 'degC'}         
    lev1_slow_atts['sr30_swu_DegC_Std']            = {'units' : 'degC'}         
    lev1_slow_atts['sr30_swu_Irr_Avg']             = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swu_Irr_Std']             = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swu_IrrC_Avg']            = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swu_IrrC_Std']            = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swd_DegC_Avg']            = {'units' : 'degC'}         
    lev1_slow_atts['sr30_swd_DegC_Std']            = {'units' : 'degC'}         
    lev1_slow_atts['sr30_swd_Irr_Avg']             = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swd_Irr_Std']             = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swd_IrrC_Avg']            = {'units' : 'Wm2'}          
    lev1_slow_atts['sr30_swd_IrrC_Std']            = {'units' : 'Wm2'}          
    lev1_slow_atts['apogee_body_T_Avg']            = {'units' : 'degC'}         
    lev1_slow_atts['apogee_body_T_Std']            = {'units' : 'degC'}         
    lev1_slow_atts['apogee_targ_T_Avg']            = {'units' : 'degC'}         
    lev1_slow_atts['apogee_targ_T_Std']            = {'units' : 'degC'}         
    lev1_slow_atts['sr50_dist_Avg']                = {'units' : 'm'}            
    lev1_slow_atts['sr50_dist_Std']                = {'units' : 'm'}            
    lev1_slow_atts['sr50_qc_Avg']                  = {'units' : '?'}            
    lev1_slow_atts['vaisala_RH_Avg']               = {'units' : '%'}            
    lev1_slow_atts['vaisala_RH_Std']               = {'units' : '%'}            
    lev1_slow_atts['vaisala_T_Avg']                = {'units' : 'degC'}         
    lev1_slow_atts['vaisala_T_Std']                = {'units' : 'degC'}         
    lev1_slow_atts['vaisala_Td_Avg']               = {'units' : 'degC'}         
    lev1_slow_atts['vaisala_Td_Std']               = {'units' : 'degC'}         
    lev1_slow_atts['vaisala_P_Avg']                = {'units' : 'hPa'}          
    lev1_slow_atts['vaisala_P_Std']                = {'units' : 'hPa'}          
    lev1_slow_atts['metek_x_Avg']                  = {'units' : 'm/s'}          
    lev1_slow_atts['metek_x_Std']                  = {'units' : 'm/s'}          
    lev1_slow_atts['metek_y_Avg']                  = {'units' : 'm/s'}          
    lev1_slow_atts['metek_y_Std']                  = {'units' : 'm/s'}          
    lev1_slow_atts['metek_z_Avg']                  = {'units' : 'm/s'}          
    lev1_slow_atts['metek_z_Std']                  = {'units' : 'm/s'}          
    lev1_slow_atts['ir20_lwu_mV_Avg']              = {'units' : 'mV'}           
    lev1_slow_atts['ir20_lwu_mV_Std']              = {'units' : 'mV'}           
    lev1_slow_atts['ir20_lwu_Case_R_Avg']          = {'units' : 'ohms'}         
    lev1_slow_atts['ir20_lwu_Case_R_Std']          = {'units' : 'ohms'}         
    lev1_slow_atts['ir20_lwu_DegC_Avg']            = {'units' : 'degC'}         
    lev1_slow_atts['ir20_lwu_DegC_Std']            = {'units' : 'degC'}         
    lev1_slow_atts['ir20_lwu_Wm2_Avg']             = {'units' : 'Wm2'}          
    lev1_slow_atts['ir20_lwu_Wm2_Std']             = {'units' : 'Wm2'}          
    lev1_slow_atts['ir20_lwd_mV_Avg']              = {'units' : 'mV'}           
    lev1_slow_atts['ir20_lwd_mV_Std']              = {'units' : 'mV'}           
    lev1_slow_atts['ir20_lwd_Case_R_Avg']          = {'units' : 'ohms'}         
    lev1_slow_atts['ir20_lwd_Case_R_Std']          = {'units' : 'ohms'}         
    lev1_slow_atts['ir20_lwd_DegC_Avg']            = {'units' : 'degC'}         
    lev1_slow_atts['ir20_lwd_DegC_Std']            = {'units' : 'degC'}         
    lev1_slow_atts['ir20_lwd_Wm2_Avg']             = {'units' : 'Wm2'}          
    lev1_slow_atts['ir20_lwd_Wm2_Std']             = {'units' : 'Wm2'}          
    lev1_slow_atts['fp_A_mV_Avg']                  = {'units' : 'mV'}           
    lev1_slow_atts['fp_A_mV_Std']                  = {'units' : 'mV'}           
    lev1_slow_atts['fp_A_Wm2_Avg']                 = {'units' : 'Wm2'}          
    lev1_slow_atts['fp_A_Wm2_Std']                 = {'units' : 'Wm2'}          
    lev1_slow_atts['fp_B_mV_Avg']                  = {'units' : 'mV'}           
    lev1_slow_atts['fp_B_mV_Std']                  = {'units' : 'mV'}           
    lev1_slow_atts['fp_B_Wm2_Avg']                 = {'units' : 'Wm2'}          
    lev1_slow_atts['fp_B_Wm2_Std']                 = {'units' : 'Wm2'}          
    lev1_slow_atts['licor_co2_Avg']                = {'units' : 'mg/m3'}    
    lev1_slow_atts['licor_co2_Std']                = {'units' : 'mg/m3'}        
    lev1_slow_atts['licor_h2o_Avg']                = {'units' : 'g/m3'}         
    lev1_slow_atts['licor_h2o_Std']                = {'units' : 'g/m3'}         
    lev1_slow_atts['licor_T_Avg']                  = {'units' : 'degC'}         
    lev1_slow_atts['licor_T_Std']                  = {'units' : 'degC'}         
    lev1_slow_atts['licor_co2_str_out_Avg']        = {'units' : '0-100'}        
    lev1_slow_atts['licor_co2_str_out_Std']        = {'units' : '0-100'}        
    lev1_slow_atts['sr30_swu_fantach_Avg']         = {'units' : 'Hz'}               
    lev1_slow_atts['sr30_swu_heatA_Avg']           = {'units' : 'mA'}
    lev1_slow_atts['sr30_swd_fantach_Avg']         = {'units' : 'Hz'}           
    lev1_slow_atts['sr30_swd_heatA_Avg']           = {'units' : 'mA'}           
    lev1_slow_atts['ir20_lwu_fan_Avg']             = {'units' : 'mV'}           
    lev1_slow_atts['ir20_lwd_fan_Avg']             = {'units' : 'mV'}           
    lev1_slow_atts['efoy_Error_Max']               = {'units' : 'N'}            
    lev1_slow_atts['efoy_FuellSt_Avg']             = {'units' : '%'}            
    lev1_slow_atts['efoy_Ubat_Avg']                = {'units' : 'V'}            
    lev1_slow_atts['efoy_Laus_Avg']                = {'units' : 'A'}            
    lev1_slow_atts['efoy_Tst_Avg']                 = {'units' : '?'}            
    lev1_slow_atts['efoy_Tint_Avg']                = {'units' : '?'}            
    lev1_slow_atts['efoy_Twt_Avg']                 = {'units' : '?'}            


    lev1_slow_atts['TIMESTAMP']                    .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_lat_deg_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_lat_min_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_lon_deg_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_lon_min_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_hdg_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_alt_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_qc']                       .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_hdop_Avg']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['gps_nsat_Avg']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_InclX_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_InclY_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['PTemp_Avg']                    .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['batt_volt_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['counts_main_Tot']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_mainscan_Max']       .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_modbus_sr301_Max']   .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_modbus_sr302_Max']   .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_modbus_vaisala_Max'] .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_sdi1_Max']           .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_sdi2_Max']           .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['call_time_efoy_Max']           .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_DegC_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_DegC_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_Irr_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_Irr_Std']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_IrrC_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_IrrC_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_DegC_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_DegC_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_Irr_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_Irr_Std']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_IrrC_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_IrrC_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['apogee_body_T_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['apogee_body_T_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['apogee_targ_T_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['apogee_targ_T_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr50_dist_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr50_dist_Std']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr50_qc_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_RH_Avg']               .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_RH_Std']               .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_T_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_T_Std']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_Td_Avg']               .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_Td_Std']               .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_P_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['vaisala_P_Std']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_x_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_x_Std']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_y_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_y_Std']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_z_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['metek_z_Std']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_mV_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_mV_Std']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_Case_R_Avg']          .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_Case_R_Std']          .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_DegC_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_DegC_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_Wm2_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_Wm2_Std']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_mV_Avg']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_mV_Std']              .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_Case_R_Avg']          .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_Case_R_Std']          .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_DegC_Avg']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_DegC_Std']            .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_Wm2_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_Wm2_Std']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_A_mV_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_A_mV_Std']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_A_Wm2_Avg']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_A_Wm2_Std']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_B_mV_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_B_mV_Std']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_B_Wm2_Avg']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['fp_B_Wm2_Std']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_co2_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_co2_Std']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_h2o_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_h2o_Std']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_T_Avg']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_T_Std']                  .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_co2_str_out_Avg']        .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['licor_co2_str_out_Std']        .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_fantach_Avg']         .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swu_heatA_Avg']           .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_fantach_Avg']         .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['sr30_swd_heatA_Avg']           .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwu_fan_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['ir20_lwd_fan_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_Error_Max']               .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_FuellSt_Avg']             .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_Ubat_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_Laus_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_Tst_Avg']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_Tint_Avg']                .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})

    lev1_slow_atts['efoy_Twt_Avg']                 .update({'long_name'     : '',
                                                            'instrument'    : '',
                                                            'methods'       : '',
                                                            'height'        : '',
                                                            'location'      : '',})


    return lev1_slow_atts, list(lev1_slow_atts.keys()).copy() 

# defines the column names of the logger data for the flux stations and thus also the output variable names in
# the level1 data files that are supposed to be "nearly-raw netcdf records". this returns two things. 1) a list of dictionaries
# where the key is the variable name and dictionary is a list of netcdf attributes. 2) a list of variable names
def define_level1_fast():  

    metek_location = "sonic mast at 2m"
    licor_location = "sonic mast at 2m"

    # !!!! I know the licor order is probably wrong... but moving on so that I can finish this
    # I can't figure out why there are less columns in the fast files than I would expect given
    # the definitions in the CR1X files... 
    lev1_fast_atts = OrderedDict()

    # units defined here, other properties defined in 'update' call below
    lev1_fast_atts['TIMESTAMP']           = {'units' : 'time'    }
    lev1_fast_atts['metek_x']             = {'units' : 'm/s'     }
    lev1_fast_atts['metek_y']             = {'units' : 'm/s'     }
    lev1_fast_atts['metek_z']             = {'units' : 'm/s'     }
    lev1_fast_atts['metek_T']             = {'units' : 'C'       }
    lev1_fast_atts['metek_heatstatus']    = {'units' : 'int'     }
    lev1_fast_atts['metek_senspathstate'] = {'units' : 'int'     }
    lev1_fast_atts['licor_co2']           = {'units' : 'g/kg'    }
    lev1_fast_atts['licor_h2o']           = {'units' : 'g/kg'    }
    lev1_fast_atts['licor_pr']            = {'units' : 'hPa'     }
    lev1_fast_atts['licor_diag']          = {'units' : 'int'     }
    lev1_fast_atts['licor_co2_str']       = {'units' : 'percent' }
    lev1_fast_atts['licor_T']             = {'units' : 'deg C'   }

    lev1_fast_atts['TIMESTAMP']           .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,}) 

    lev1_fast_atts['metek_x']             .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_y']             .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_z']             .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_T']             .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_heatstatus']    .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_senspathstate'] .update({'long_name'     : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['licor_diag']          .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_co2']           .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_h2o']           .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_co2_str']       .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_pr']            .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_T']             .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    return lev1_fast_atts, list(lev1_fast_atts.keys()).copy() 

def define_level2_variables():  

    inst_boom_location_string = 'top of station at ~2m'

    lev2_atts = OrderedDict()

    lev2_atts['station_lat']          = {'units' : 'degrees_north'}    
    lev2_atts['station_lon']          = {'units' : 'degrees_east'}   
    lev2_atts['station_heading']      = {'units' : 'degrees_true'}
    lev2_atts['gps_alt']              = {'units' : 'meters'}   
    lev2_atts['sr50_dist']            = {'units' : 'meters'}   
    lev2_atts['snow_depth']           = {'units' : 'cm'}     
    lev2_atts['press_vaisala']        = {'units' : 'hPa'}     
    lev2_atts['temp_vaisala']         = {'units' : 'deg C'}
    lev2_atts['rel_humidity_vaisala'] = {'units' : 'percent'}     
    lev2_atts['dewpoint_vaisala']     = {'units' : 'deg C'}   
    lev2_atts['MR_vaisala']           = {'units' : 'g/kg'}   
    lev2_atts['abs_humidity_vaisala'] = {'units' : 'g/m3'}  
    lev2_atts['enthalpy_vaisala']     = {'units' : 'kJ/kg'}     
    lev2_atts['pw_vaisala']           = {'units' : 'Pa'}     
    lev2_atts['RHi_vaisala']          = {'units' : 'percent'}  
    lev2_atts['body_T_IRT']           = {'units' : 'deg C'}  
    lev2_atts['surface_T_IRT']        = {'units' : 'deg C'}  
    lev2_atts['flux_plate_A_Wm2']     = {'units' : 'Wm2'}  
    lev2_atts['flux_plate_B_Wm2']     = {'units' : 'Wm2'}  
    lev2_atts['wind_speed_metek']     = {'units' : 'm/s'}  
    lev2_atts['wind_direction_metek'] = {'units' : 'degC'}  
    lev2_atts['temp_metek']           = {'units' : 'deg C'}   
    lev2_atts['temp_variance_metek']  = {'units' : '(deg C)^2'}
    lev2_atts['H2O_licor']            = {'units' : 'g/kg'}   
    lev2_atts['CO2_licor']            = {'units' : 'g/kg'}   
    lev2_atts['temp_licor']           = {'units' : 'deg C'}   
    lev2_atts['co2_signal_licor']     = {'units' : 'percent'}  
    lev2_atts['radiation_LWd']        = {'units' : 'Wm2'}  
    lev2_atts['radiation_SWd']        = {'units' : 'Wm2'}  
    lev2_atts['radiation_LWu']        = {'units' : 'Wm2'}  
    lev2_atts['radiation_SWu']        = {'units' : 'Wm2'}  
    lev2_atts['radiation_net']        = {'units' : 'Wm2'}     

    # add everything else to the variable NetCDF attributes
    # #########################################################################################################
    lev2_atts['station_lat']          .update({ 'long_name'     : 'latitude from gps at station',
                                                'cf_name'       : 'latitude',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                'height'        : '1m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['station_lon']          .update({ 'long_name'     : 'longitude from gps at station',
                                                'cf_name'       : 'longitude',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : '$GPRMC, $GPGGA, GPGZDA',
                                                'height'        : '1m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['station_heading']      .update({ 'long_name'     : 'heading from gps at station',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : '$HEHDT',
                                                'height'        : '1m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['gps_alt']              .update({ 'long_name'     : 'altitude from gps at station',
                                                'cf_name'       : 'altitude',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                'height'        : '1m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['sr50_dist']            .update({ 'long_name'     : 'distance to surface from SR50; temperature compensation correction applied',
                                                'cf_name'       : '',
                                                'instrument'    : 'Campbell Scientific SR50A',
                                                'methods'       : 'unheated, temperature correction applied',
                                                'height'        : '1.75m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['snow_depth']           .update({ 'long_name'     : 'snow depth near station base',
                                                'cf_name'       : 'surface_snow_thickness',
                                                'instrument'    : 'Hukseflux HFP01',
                                                'methods'       : 'derived snow depth from temperature-corrected SR50 distance values based on initialization. footprint nominally 0.47 m radius.',
                                                'height'        : 'N/A',
                                                'location'      : 'at base of station under SR50',})

    lev2_atts['press_vaisala']        .update({ 'long_name'     : 'air pressure',
                                                'cf_name'       : 'air_pressure',
                                                'instrument'    : 'Vaisala PTU 300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['temp_vaisala']         .update({ 'long_name'     : 'temperature',
                                                'cf_name'       : 'air_temperature',
                                                'instrument'    : 'Vaisala HMT330',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['rel_humidity_vaisala'] .update({ 'long_name'     : 'relative humidity wrt water',
                                                'cf_name'       : 'relative_humidity',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['dewpoint_vaisala']     .update({ 'long_name'     : 'dewpoint',
                                                'cf_name'       : 'dew_point_temperature',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})
    lev2_atts['MR_vaisala']           .update({ 'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                'cf_name'       : 'specific_humidity',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['abs_humidity_vaisala'] .update({ 'long_name'     : 'absolute humidity',
                                                'cf_name'       : 'absolute_humidity',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['enthalpy_vaisala']     .update({ 'long_name'     : 'enthalpy',
                                                'cf_name'       : 'enthalpy',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['pw_vaisala']           .update({ 'long_name'     : 'vapor pressure',
                                                'cf_name'       : '',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['RHi_vaisala']          .update({ 'long_name'     : 'ice RH derived using T/P/RH',
                                                'cf_name'       : '',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['body_T_IRT']           .update({ 'long_name'     : 'instrument body temperature',
                                                'cf_name'       : '',
                                                'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['surface_T_IRT']        .update({ 'long_name'     : 'Apogee IRT target 8-14 micron brightness temperature.',
                                                'cf_name'       : '',
                                                'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                'methods'       : 'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                'height'        : 'surface',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['flux_plate_A_Wm2']     .update({ 'long_name'     : 'conductive flux from plate A',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hukseflux HFP01',
                                                'methods'       : 'Sensitivity 63.00/1000 [mV/(W/m2)]',
                                                'height'        : '',
                                                'location'      : '10m south of station at met city',})

    lev2_atts['flux_plate_B_Wm2']     .update({'units'         : 'Wm2',
                                               'long_name'     : 'conductive flux from plate B',
                                               'cf_name'       : '',
                                               'instrument'    : 'Hukseflux HFP01',
                                               'methods'       : 'Sensitivity 63.91/1000 [mV/(W/m2)]',
                                               'height'        : '',
                                               'location'      : 'under Apogee and SR50 at station base',})

    lev2_atts['wind_speed_metek']     .update({ 'long_name'     : 'average metek wind speed',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})
    lev2_atts['wind_direction_metek'] .update({ 'long_name'     : 'average metek wind direction',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})


    lev2_atts['temp_metek']           .update({ 'long_name'     : 'Metek sonic temperature',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['temp_variance_metek']  .update({ 'long_name'     : 'metek sonic temperature obs variance',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})


    lev2_atts['H2O_licor']            .update({ 'long_name'     : 'Licor water vapor mixing ratio',
                                                'cf_name'       : 'specific_humidity',
                                                'instrument'    : 'Licor 7500-DS',
                                                'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['CO2_licor']            .update({ 'long_name'     : 'Licor CO2 mixing ratio',
                                                'cf_name'       : '',
                                                'instrument'    : 'Licor 7500-DS',
                                                'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['temp_licor']           .update({ 'long_name'     : 'temperature',
                                                'cf_name'       : 'air_temperature',
                                                'instrument'    : 'Licor 7500-DS',
                                                'methods'       : 'thermistor positioned along strut of open-path optical gas analyzer, source data reported at 20 Hz',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})


    lev2_atts['co2_signal_licor']     .update({ 'long_name'     : 'Licor CO2 signal strength diagnostic',
                                                'cf_name'       : '',
                                                'instrument'    : 'Licor 7500-DS',
                                                'methods'       : 'signal strength [0-100%] is a measure of attenuation of the optics (e.g., by salt residue or ice) that applies to both co2 and h2o observations',
                                                'height'        : '',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['radiation_LWd']        .update({ 'long_name'     : 'net downward longwave flux',
                                                'cf_name'       : 'surface_net_downward_longwave_flux',
                                                'instrument'    : 'Hukseflux IR20 pyrgeometer',
                                                'methods'       : 'hemispheric longwave radiation',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['radiation_SWd']        .update({ 'long_name'     : 'net downward shortwave flux',
                                                'cf_name'       : 'surface_net_downward_shortwave_flux',
                                                'instrument'    : 'Hukseflux SR30 pyranometer',
                                                'methods'       : 'hemispheric shortwave radiation',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['radiation_LWu']        .update({ 'long_name'     : 'net upward longwave flux',
                                                'cf_name'       : 'surface_net_upward_longwave_flux',
                                                'instrument'    : 'Hukseflux IR20 pyrgeometer',
                                                'methods'       : 'hemispheric longwave radiation',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['radiation_SWu']        .update({ 'long_name'     : 'net upward shortwave flux',
                                                'cf_name'       : 'surface_net_upward_shortwave_flux',
                                                'instrument'    : 'Hukseflux SR30 pyranometer',
                                                'methods'       : 'hemispheric shortwave radiation',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['radiation_net']        .update({ 'long_name'     : 'cumulative surface radiative flux',
                                                'cf_name'       : 'surface_net_radiative_flux',
                                                'instrument'    : 'SR30 and IR20 radiometers',
                                                'methods'       : 'combined hemispheric radiation measurements',
                                                'height'        : '2m',
                                                'location'      : inst_boom_location_string,})

    return lev2_atts, list(lev2_atts.keys()).copy() 
 
def define_turb_variables():
    inst_boom_location_string = 'top of station at ~2m'

    turb_atts = OrderedDict()

    turb_atts['Hs']              = {'units' : 'Wm2'}
    turb_atts['Hs_hi']           = {'units' : 'Wm2'}
    turb_atts['Cd']              = {'units' : 'dimensionless'}
    turb_atts['Cd_hi']           = {'units' : 'dimensionless'}
    turb_atts['ustar']           = {'units' : 'm/s'}
    turb_atts['ustar_hi']        = {'units' : 'm/s'}
    turb_atts['Tstar']           = {'units' : 'degC'}
    turb_atts['Tstar_hi']        = {'units' : 'degC'}
    turb_atts['zeta_level_n']    = {'units' : 'dimensionless'}
    turb_atts['zeta_level_n_hi'] = {'units' : 'dimensionless'}
    turb_atts['wu_csp']          = {'units' : 'm^2/s^2'}
    turb_atts['wv_csp']          = {'units' : 'm^2/s^2'}
    turb_atts['uv_csp']          = {'units' : 'm^2/s^2'}
    turb_atts['wT_csp']          = {'units' : 'degC m/s'}
    turb_atts['uT_csp']          = {'units' : 'degC m/s'}
    turb_atts['vT_csp']          = {'units' : 'degC m/s'}
    turb_atts['phi_u']           = {'units' : 'dimensionless'}
    turb_atts['phi_v']           = {'units' : 'dimensionless'}
    turb_atts['phi_w']           = {'units' : 'dimensionless'}
    turb_atts['phi_T']           = {'units' : 'dimensionless'}
    turb_atts['phi_uT']          = {'units' : 'dimensionless'}
    turb_atts['phi_u_hi']        = {'units' : 'dimensionless'}
    turb_atts['phi_v_hi']        = {'units' : 'dimensionless'}
    turb_atts['phi_w_hi']        = {'units' : 'dimensionless'}
    turb_atts['phi_T_hi']        = {'units' : 'dimensionless'}
    turb_atts['phi_uT_hi']       = {'units' : 'dimensionless'}
    turb_atts['epsilon_u']       = {'units' : 'm^2/s^3'}
    turb_atts['epsilon_v']       = {'units' : 'm^2/s^3'}
    turb_atts['epsilon_w']       = {'units' : 'm^2/s^3'}
    turb_atts['epsilon']         = {'units' : 'm^2/s^3'}
    turb_atts['Phi_epsilon']     = {'units' : 'dimensionless'}
    turb_atts['Phi_epsilon_hi']  = {'units' : 'dimensionless'}
    turb_atts['Nt']              = {'units' : 'degC^2/s'}
    turb_atts['Phi_Nt']          = {'units' : 'dimensionless'}
    turb_atts['Phi_Nt_hi']       = {'units' : 'dimensionless'}
    turb_atts['Phix']            = {'units' : 'deg'}
    turb_atts['DeltaU']          = {'units' : 'm/s'}
    turb_atts['DeltaV']          = {'units' : 'm/s'}
    turb_atts['DeltaT']          = {'units' : 'degC'}
    turb_atts['Kurt_u']          = {'units' : 'unitless'}
    turb_atts['Kurt_v']          = {'units' : 'unitless'}
    turb_atts['Kurt_w']          = {'units' : 'unitless'}
    turb_atts['Kurt_T']          = {'units' : 'unitless'}
    turb_atts['Kurt_uw']         = {'units' : 'unitless'}
    turb_atts['Kurt_vw']         = {'units' : 'unitless'}
    turb_atts['Kurt_wT']         = {'units' : 'unitless'}
    turb_atts['Kurt_uT']         = {'units' : 'unitless'}
    turb_atts['Skew_u']          = {'units' : 'unitless'}
    turb_atts['Skew_v']          = {'units' : 'unitless'}
    turb_atts['Skew_w']          = {'units' : 'unitless'}
    turb_atts['Skew_T']          = {'units' : 'unitless'}
    turb_atts['Skew_uw']         = {'units' : 'unitless'}
    turb_atts['Skew_vw']         = {'units' : 'unitless'}
    turb_atts['Skew_wT']         = {'units' : 'unitless'}
    turb_atts['Skew_uT']         = {'units' : 'unitless'}

    # !! The turbulence data. A lot of it... Almost wonder if this metadata should reside in a separate
    # file?  Some variables are dimensionless, meaning they are both scaled & unitless and the result is
    # independent of height such that it sounds a little funny to have a var name like
    # MO_dimensionless_param_2_m, but that is the only way to distinguish between the 4 calculations. So,
    # for these I added ", calculated from 2 m" or whatever into the long_name.  Maybe there is a better
    # way?

    turb_atts['Hs']              .update({'long_name'  : 'sensible heat flux',
                                          'cf_name'    : 'upward_sensible_heat_flux_in_air',
                                          'instrument' : 'Metek uSonic-Cage MP sonic anemometer',
                                          'methods'    : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Hs_hi']           .update({'long_name'  : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                          'cf_name'    : 'upward_sensible_heat_flux_in_air',
                                          'instrument' : 'Metek uSonic-Cage MP sonic anemometer',
                                          'methods'    : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Cd']              .update({'long_name'  : 'Drag coefficient based on the momentum flux, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Cd_hi']           .update({'long_name'  : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['ustar']           .update({'long_name'  : 'friction velocity (based only on the downstream, uw, stress components)',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['ustar_hi']        .update({'long_name'  : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Tstar']           .update({'long_name'  : 'temperature scale',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Tstar_hi']        .update({'long_name'  : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['zeta_level_n']    .update({'long_name'  : 'Monin-Obukhov stability parameter, z/L, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['zeta_level_n_hi'] .update({'long_name'  : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wu_csp']          .update({'long_name'  : 'wu-covariance based on the wu-cospectra integration',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wv_csp']          .update({'long_name'  : 'wv-covariance based on the wv-cospectra integration',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['uv_csp']          .update({'long_name'  : 'uv-covariance based on the uv-cospectra integration',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wT_csp']          .update({'long_name'  : 'wT-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['uT_csp']          .update({'long_name'  : 'uT-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['vT_csp']          .update({'long_name'  : 'vT-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_u']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_v']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_w']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_T']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_uT']          .update({'long_name'  : 'MO universal function for the horizontal heat flux, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_u_hi']        .update({'long_name'  : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_v_hi']        .update({'long_name'  : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_w_hi']        .update({'long_name'  : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_T_hi']        .update({'long_name'  : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_uT_hi']       .update({'long_name'  : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxesx, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon_u']       .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon_v']       .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon_w']       .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon']         .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})
    

    turb_atts['Phi_epsilon']     .update({'long_name'  : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phi_epsilon_hi']  .update({'long_name'  : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Nt']              .update({'long_name'  : 'The dissipation (destruction) rate for half the temperature variance',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phi_Nt']          .update({'long_name'  : 'Monin-Obukhov universal function Phi_Nt, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phi_Nt_hi']       .update({'long_name'  : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phix']            .update({'long_name'  : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['DeltaU']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['DeltaV']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['DeltaT']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_u']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_v']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_w']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_T']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_uw']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_vw']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_wT']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_uT']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_u']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_v']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})
    
    turb_atts['Skew_w']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_T']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_uw']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_vw']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_wT']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_uT']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '',
                                          'location'   : inst_boom_location_string,})

    return turb_atts, list(turb_atts.keys()).copy() 
