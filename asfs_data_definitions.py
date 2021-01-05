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
    cv = ('1.4', '1/1/2020', 'mgallagher')
    return cv

# file_type must be "slow", "fast", "level2", or "turb"
def define_global_atts(station_name, file_type):
    cv = code_version()
    # global attributes to be written into the netcdf output file
    global_atts = {
        'date_created'     :'{}'.format(time.ctime(time.time())),
        'title'            :'MOSAiC flux group data product: ', # blank variables are specific to site characterization 
        'contact'          :'Matthew Shupe, University of Colorado, matthew.shupe@colorado.edu',
        'institution'      :'CIRES, University of Colorado and NOAA Physical Sciences Laboratory',
        'file_creator'     :'Michael R. Gallagher; Christopher J. Cox',
        'creator_email'    :'michael.r.gallagher@noaa.gov; christopher.j.cox@noaa.gov', 
        'project'          :'MOSAiC, PS-122: Thermodynamic and Dynamic Drivers of the Arctic Sea Ice Mass Budget at MOSAiC', 
        'Funding'          :'Funding sources: National Science Foundation Award Number OPP1724551; NOAA Arctic Research Program',
        'source'           :'Observations made during the MOSAiC drifting campaign, 2019-2020', 
        'system'           :'{}'.format(station_name),
        'references'       :'', 
        'keywords'         :'Polar, Arctic, Supersite, Observations, Flux, Atmosphere, MOSAiC',
        'conventions'      :'cf convention variable naming as attribute whenever possible',  
        'history'          :'based on level 1 ingest files',
        'version'          : cv[0]+', '+cv[1], 
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


# we are reading SD card data, which was usually saved without headers, but the headers occasionally change when logger programs are modified. it is what it is...
# the good news is that there are only a dozen or so permutations, so we can just store them here
def get_level1_col_headers(ncol,cver):
    col_len_89_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg']
    col_len_89_1 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Ubat_Avg','efoy_Laus_Avg','sr30_swu_tilt_Avg','sr30_swd_tilt_Avg']
    col_len_91_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg','sr30_swu_tilt_Avg','sr30_swd_tilt_Avg']
    col_len_93_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg']
    col_len_95_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','sr30_swu_tilt_Avg','sr30_swd_tilt_Avg']
    col_len_97_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg']
    col_len_97_1 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Ubat_Avg','efoy_Laus_Avg','sr30_swu_tilt_Avg','sr30_swd_tilt_Avg']
    col_len_98_0 = ['TIMESTAMP','RECORD','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg']
    col_len_99_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg','efoy_Tst_Avg','efoy_Tint_Avg']
    col_len_99_1 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg','sr30_swu_tilt_Avg','sr30_swd_tilt_Avg']
    col_len_100_0 = ['TIMESTAMP','gps_lat_deg_Avg','gps_lat_min_Avg','gps_lon_deg_Avg','gps_lon_min_Avg','gps_hdg_Avg','gps_alt_Avg','gps_qc','gps_hdop_Avg','gps_nsat_Avg','metek_InclX_Avg','metek_InclY_Avg','PTemp_Avg','batt_volt_Avg','counts_main_Tot','call_time_mainscan_Max','call_time_modbus_sr301_Max','call_time_modbus_sr302_Max','call_time_modbus_vaisala_Max','call_time_sdi1_Max','call_time_sdi2_Max','call_time_efoy_Max','sr30_swu_DegC_Avg','sr30_swu_DegC_Std','sr30_swu_Irr_Avg','sr30_swu_Irr_Std','sr30_swu_IrrC_Avg','sr30_swu_IrrC_Std','sr30_swd_DegC_Avg','sr30_swd_DegC_Std','sr30_swd_Irr_Avg','sr30_swd_Irr_Std','sr30_swd_IrrC_Avg','sr30_swd_IrrC_Std','apogee_body_T_Avg','apogee_body_T_Std','apogee_targ_T_Avg','apogee_targ_T_Std','sr50_dist_Avg','sr50_dist_Std','sr50_qc_Avg','vaisala_RH_Avg','vaisala_RH_Std','vaisala_T_Avg','vaisala_T_Std','vaisala_Td_Avg','vaisala_Td_Std','vaisala_P_Avg','vaisala_P_Std','metek_x_Avg','metek_x_Std','metek_y_Avg','metek_y_Std','metek_z_Avg','metek_z_Std','ir20_lwu_mV_Avg','ir20_lwu_mV_Std','ir20_lwu_Case_R_Avg','ir20_lwu_Case_R_Std','ir20_lwu_DegC_Avg','ir20_lwu_DegC_Std','ir20_lwu_Wm2_Avg','ir20_lwu_Wm2_Std','ir20_lwd_mV_Avg','ir20_lwd_mV_Std','ir20_lwd_Case_R_Avg','ir20_lwd_Case_R_Std','ir20_lwd_DegC_Avg','ir20_lwd_DegC_Std','ir20_lwd_Wm2_Avg','ir20_lwd_Wm2_Std','fp_A_mV_Avg','fp_A_mV_Std','fp_A_Wm2_Avg','fp_A_Wm2_Std','fp_B_mV_Avg','fp_B_mV_Std','fp_B_Wm2_Avg','fp_B_Wm2_Std','licor_co2_Avg','licor_co2_Std','licor_h2o_Avg','licor_h2o_Std','licor_t_Avg','licor_t_Std','licor_co2_str_out_Avg','licor_co2_str_out_Std','sr30_swu_fantach_Avg','sr30_swu_heatA_Avg','sr30_swd_fantach_Avg','sr30_swd_heatA_Avg','ir20_lwu_fan_Avg','ir20_lwd_fan_Avg','efoy_Error_Max','efoy_FuellSt_Avg','efoy_Ubat_Avg','efoy_Laus_Avg','efoy_Tst_Avg','efoy_Tint_Avg','efoy_Twt_Avg']

    col_out = eval('col_len_'+str(ncol)+'_'+str(cver)) # yup i did that

    return col_out



# defines the column names of the logger data for the flux stations and thus also the output variable names in
# the level1 data files that are supposed to be "nearly-raw netcdf records". this returns two things. 1) a list of dictionaries
# where the key is the variable name and dictionary is a list of netcdf attributes. 2) a list of variable names
def define_level1_slow():

    licor_location = "sonic mast at 3.3m"
    metek_location = "sonic mast at 3.3m"
    inst_boom_location_string = 'top of station at ~2m'

    lev1_slow_atts = OrderedDict()
    # units defined here, other properties defined in 'update' call below
    lev1_slow_atts['TIMESTAMP']                    = {'units' : 'TS'}
    lev1_slow_atts['gps_lat_deg_Avg']              = {'units' : 'deg'}
    lev1_slow_atts['gps_lat_min_Avg']              = {'units' : 'min'}
    lev1_slow_atts['gps_lon_deg_Avg']              = {'units' : 'deg'}
    lev1_slow_atts['gps_lon_min_Avg']              = {'units' : 'min'}
    lev1_slow_atts['gps_hdg_Avg']                  = {'units' : 'deg'}
    lev1_slow_atts['gps_alt_Avg']                  = {'units' : 'm'}
    lev1_slow_atts['gps_qc']                       = {'units' : 'N'}
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
    lev1_slow_atts['sr30_swu_Irr_Avg']             = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swu_Irr_Std']             = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swu_IrrC_Avg']            = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swu_IrrC_Std']            = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swd_DegC_Avg']            = {'units' : 'degC'}
    lev1_slow_atts['sr30_swd_DegC_Std']            = {'units' : 'degC'}
    lev1_slow_atts['sr30_swd_Irr_Avg']             = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swd_Irr_Std']             = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swd_IrrC_Avg']            = {'units' : 'W/m2'}
    lev1_slow_atts['sr30_swd_IrrC_Std']            = {'units' : 'W/m2'}
    lev1_slow_atts['apogee_body_T_Avg']            = {'units' : 'degC'}
    lev1_slow_atts['apogee_body_T_Std']            = {'units' : 'degC'}
    lev1_slow_atts['apogee_targ_T_Avg']            = {'units' : 'degC'}
    lev1_slow_atts['apogee_targ_T_Std']            = {'units' : 'degC'}
    lev1_slow_atts['sr50_dist_Avg']                = {'units' : 'm'}
    lev1_slow_atts['sr50_dist_Std']                = {'units' : 'm'}
    lev1_slow_atts['sr50_qc_Avg']                  = {'units' : 'unitless'}
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
    lev1_slow_atts['ir20_lwu_Wm2_Avg']             = {'units' : 'W/m2'}
    lev1_slow_atts['ir20_lwu_Wm2_Std']             = {'units' : 'W/m2'}
    lev1_slow_atts['ir20_lwd_mV_Avg']              = {'units' : 'mV'}
    lev1_slow_atts['ir20_lwd_mV_Std']              = {'units' : 'mV'}
    lev1_slow_atts['ir20_lwd_Case_R_Avg']          = {'units' : 'ohms'}
    lev1_slow_atts['ir20_lwd_Case_R_Std']          = {'units' : 'ohms'}
    lev1_slow_atts['ir20_lwd_DegC_Avg']            = {'units' : 'degC'}
    lev1_slow_atts['ir20_lwd_DegC_Std']            = {'units' : 'degC'}
    lev1_slow_atts['ir20_lwd_Wm2_Avg']             = {'units' : 'W/m2'}
    lev1_slow_atts['ir20_lwd_Wm2_Std']             = {'units' : 'W/m2'}
    lev1_slow_atts['fp_A_mV_Avg']                  = {'units' : 'mV'}
    lev1_slow_atts['fp_A_mV_Std']                  = {'units' : 'mV'}
    lev1_slow_atts['fp_A_Wm2_Avg']                 = {'units' : 'W/m2'}
    lev1_slow_atts['fp_A_Wm2_Std']                 = {'units' : 'W/m2'}
    lev1_slow_atts['fp_B_mV_Avg']                  = {'units' : 'mV'}
    lev1_slow_atts['fp_B_mV_Std']                  = {'units' : 'mV'}
    lev1_slow_atts['fp_B_Wm2_Avg']                 = {'units' : 'W/m2'}
    lev1_slow_atts['fp_B_Wm2_Std']                 = {'units' : 'W/m2'}
    lev1_slow_atts['licor_co2_Avg']                = {'units' : 'mg/m3'}
    lev1_slow_atts['licor_co2_Std']                = {'units' : 'mg/m3'}
    lev1_slow_atts['licor_h2o_Avg']                = {'units' : 'g/m3'}
    lev1_slow_atts['licor_h2o_Std']                = {'units' : 'g/m3'}
    lev1_slow_atts['licor_co2_str_out_Avg']        = {'units' : '%'}
    lev1_slow_atts['licor_co2_str_out_Std']        = {'units' : '%'}
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
    lev1_slow_atts['efoy_Tst_Avg']                 = {'units' : 'C'}
    lev1_slow_atts['efoy_Tint_Avg']                = {'units' : 'C'}
    lev1_slow_atts['efoy_Twt_Avg']                 = {'units' : 'C'}
    lev1_slow_atts['sr30_swu_tilt_Avg']            = {'units' : 'deg'}
    lev1_slow_atts['sr30_swd_tilt_Avg']            = {'units' : 'deg'}

    lev1_slow_atts['TIMESTAMP']                    .update({'long_name'     : 'time of measurement',
                                                            'instrument'    : 'CR1000X',
                                                            'methods'       : 'synched to GPS',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['gps_lat_deg_Avg']              .update({'long_name'     : 'latitude degrees from gps at station',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_lat_min_Avg']              .update({'long_name'     : 'latitide minutes from gps at station',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_lon_deg_Avg']              .update({'long_name'     : 'longitude degrees from gps at station',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_lon_min_Avg']              .update({'long_name'     : 'longitude minutes from gps at station',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_hdg_Avg']                  .update({'long_name'     : 'heading from gps at station',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'HEHDT',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_alt_Avg']                  .update({'long_name'     : 'altitude from gps at station',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_qc']                       .update({'long_name'     : 'gps fix quality variable',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPGGA; fix quality: 0 = invalid; 1 = gps fix (sps); 2 = dgps fix; 3 = pps fix; 4 = real time kinematic; 5 = float rtk; 6 = estimated (deck reckoning); 7 = manual input mode; 8 = simulation mode',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_hdop_Avg']                 .update({'long_name'     : 'gps Horizontal Dilution Of Precision (HDOP)',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPGGA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['gps_nsat_Avg']                 .update({'long_name'     : 'gps number of tracked satellites',
                                                            'instrument'    : 'Hemisphere V102',
                                                            'methods'       : 'GPGGA',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['metek_InclX_Avg']              .update({'long_name'     : 'sensor inclinometer pitch angle',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['metek_InclY_Avg']              .update({'long_name'     : 'sensor inclinometer roll angle',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['PTemp_Avg']                    .update({'long_name'     : 'logger electronics panel temperature',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['batt_volt_Avg']                .update({'long_name'     : 'voltage of the power source supplying the logger',
                                                            'instrument'    : 'CCampbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['counts_main_Tot']              .update({'long_name'     : 'number of completed cycles of the main scan during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_mainscan_Max']       .update({'long_name'     : 'duration of the longest scan during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_modbus_sr301_Max']   .update({'long_name'     : 'duration of the longest scan up to the first SR30 call during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_modbus_sr302_Max']   .update({'long_name'     : 'duration of the longest scan up to the second SR30 call during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_modbus_vaisala_Max'] .update({'long_name'     : 'duration of the longest scan up to the Vaisala call during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell R1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_sdi1_Max']           .update({'long_name'     : 'duration of the longest scan up to the first SDI-12 call during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_sdi2_Max']           .update({'long_name'     : 'duration of the longest scan up to the second SDI-12 call during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['call_time_efoy_Max']           .update({'long_name'     : 'duration of the longest scan up to the EFOY call during the 1 min averaging interval',
                                                            'instrument'    : 'Campbell CR1000X',
                                                            'methods'       : '',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['sr30_swu_DegC_Avg']            .update({'long_name'     : 'average case temperature of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swu_DegC_Std']            .update({'long_name'     : 'standard deviation of the case of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swu_Irr_Avg']             .update({'long_name'     : 'average irradiance of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'thermopile pyranometer; RS-485 protocol',
                                                            'methods'       : 'RS-485',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swu_Irr_Std']             .update({'long_name'     : 'standard deviation of the irradiance of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swu_IrrC_Avg']            .update({'long_name'     : 'average irradiance of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swu_IrrC_Std']            .update({'long_name'     : 'standard deviation of the temperature-corrected irradiance of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_DegC_Avg']            .update({'long_name'     : 'average case temperature of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_DegC_Std']            .update({'long_name'     : 'standard deviation of the case of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_Irr_Avg']             .update({'long_name'     : 'average irradiance of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_Irr_Std']             .update({'long_name'     : 'standard deviation of the irradiance of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_IrrC_Avg']            .update({'long_name'     : 'average irradiance of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_IrrC_Std']            .update({'long_name'     : 'standard deviation of the temperature-corrected irradiance of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['apogee_body_T_Avg']            .update({'long_name'     : 'average of the sensor body temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                            'methods'       : 'infrared thermometer; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['apogee_body_T_Std']            .update({'long_name'     : 'standard deviation of the infrared thermometer body temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                            'methods'       : 'infrared thermometer; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['apogee_targ_T_Avg']            .update({'long_name'     : 'average of the sensor target 8-14 micron brightness temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                            'methods'       : 'thermopile infrared thermometer; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['apogee_targ_T_Std']            .update({'long_name'     : 'standard deviation of the the sensor target 8-14 micron brightness temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                            'methods'       : 'thermopile infrared thermometer; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr50_dist_Avg']                .update({'long_name'     : 'average of the uncorrected distance between the sensor and the surface during the 1 min averaging interval',
                                                            'instrument'    : 'SR50A',
                                                            'methods'       : 'acoustic ranger; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr50_dist_Std']                .update({'long_name'     : 'standard deviation of the uncorrected distance between the sensor and the surface during the 1 min averaging interval',
                                                            'instrument'    : 'SR50A',
                                                            'methods'       : 'acoustic ranger; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr50_qc_Avg']                  .update({'long_name'     : 'quality number of the distance measurement',
                                                            'instrument'    : 'SR50A',
                                                            'methods'       : 'acoustic ranger; SDI-12 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_RH_Avg']               .update({'long_name'     : 'average of the relative humidity during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'meteorology sensor, heated capacitive thin-film polymer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_RH_Std']               .update({'long_name'     : 'standard deviation of the relative humidity during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'meteorology sensor, heated capacitive thin-film polymer; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_T_Avg']                .update({'long_name'     : 'average of the air temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'meteorology sensor, PT100 RTD; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_T_Std']                .update({'long_name'     : 'standard deviation of the air temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'meteorology sensor, PT100 RTD; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_Td_Avg']               .update({'long_name'     : 'average of the dewpoint temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'calculated by sensor electonics; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_Td_Std']               .update({'long_name'     : 'standard deviation of the dewpoint temperature during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'calculated by sensor electronics; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_P_Avg']                .update({'long_name'     : 'average of the atmospheric pressure during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'meteorology sensor; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['vaisala_P_Std']                .update({'long_name'     : 'standard deviation of the atmospheric pressure during the 1 min averaging interval',
                                                            'instrument'    : 'Vaisala PTU300',
                                                            'methods'       : 'meteorology sensor; RS-485 protocol',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['metek_x_Avg']                  .update({'long_name'     : 'average wind velocity in x during the 1 min averaging interval',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'sonic anemometer, source data reported at 20 Hz; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['metek_x_Std']                  .update({'long_name'     : 'standard deviation of the wind velocity in x during the 1 min averaging interval',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'sonic anemometer, source data reported at 20 Hz; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['metek_y_Avg']                  .update({'long_name'     : 'average wind velocity in y during the 1 min averaging interval',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'sonic anemometer, source data reported at 20 Hz; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['metek_y_Std']                  .update({'long_name'     : 'standard deviation of the wind velocity in y during the 1 min averaging interval',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'sonic anemometer, source data reported at 20 Hz; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['metek_z_Avg']                  .update({'long_name'     : 'average wind velocity in z during the 1 min averaging interval',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'sonic anemometer, source data reported at 20 Hz; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['metek_z_Std']                  .update({'long_name'     : 'standard deviation of the wind velocity in z during the 1 min averaging interval',
                                                            'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                            'methods'       : 'sonic anemometer, source data reported at 20 Hz; protocol RS-422',
                                                            'height'        : '3.3 m',
                                                            'location'      : metek_location,})

    lev1_slow_atts['ir20_lwu_mV_Avg']              .update({'long_name'     : 'average thermopile voltage of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; differential voltage',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_mV_Std']              .update({'long_name'     : 'standard deviation of the thermopile voltage of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; differential voltage',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_Case_R_Avg']          .update({'long_name'     : 'average resistance of the case thermistor of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_Case_R_Std']          .update({'long_name'     : 'standard deviation of the resistance of the case thermistor of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_DegC_Avg']            .update({'long_name'     : 'average case temperature of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor; Steinhart-Hart A=0.0010295, B=0.0002391, C=0.0000001568',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_DegC_Std']            .update({'long_name'     : 'standard deviation of the case temperature of the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor; Steinhart-Hart A=0.0010295, B=0.0002391, C=0.0000001568',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_Wm2_Avg']             .update({'long_name'     : 'average flux from the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; preliminary calibration: uses thermopile sensitvity but not temperature dependence',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_Wm2_Std']             .update({'long_name'     : 'standard deviation of the flux from the downward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; preliminary calibration: uses thermopile sensitvity but not temperature dependence',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_mV_Avg']              .update({'long_name'     : 'average thermopile voltage of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; differential voltage',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_mV_Std']              .update({'long_name'     : 'standard deviation of the thermopile voltage of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; differential voltage',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_Case_R_Avg']          .update({'long_name'     : 'average resistance of the case thermistor of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_Case_R_Std']          .update({'long_name'     : 'standard deviation of the resistance of the case thermistor of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_DegC_Avg']            .update({'long_name'     : 'average case temperature of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor; Steinhart-Hart A=0.0010295, B=0.0002391, C=0.0000001568',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_DegC_Std']            .update({'long_name'     : 'standard deviation of the case temperature of the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; analog; half-bridge, 100kOhm 0.01% ref resistor; Steinhart-Hart A=0.0010295, B=0.0002391, C=0.0000001568',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_Wm2_Avg']             .update({'long_name'     : 'average flux from the upward-facing sensor during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; preliminary calibration: uses thermopile sensitvity but not temperature dependence',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_Wm2_Std']             .update({'long_name'     : 'standard deviation of the flux from the sensor pyrgeometer during the 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux IR20',
                                                            'methods'       : 'thermopile pyrgeometer; preliminary calibration: uses thermopile sensitvity but not temperature dependence',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_A_mV_Avg']                  .update({'long_name'     : 'average thermopile voltage during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_A_mV_Std']                  .update({'long_name'     : 'standard deviation of the thermopile voltage during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_A_Wm2_Avg']                 .update({'long_name'     : 'average flux during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_A_Wm2_Std']                 .update({'long_name'     : 'standard deviation of the flux during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_B_mV_Avg']                  .update({'long_name'     : 'average thermopile voltage during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_B_mV_Std']                  .update({'long_name'     : 'standard deviation of the thermopile voltage during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_B_Wm2_Avg']                 .update({'long_name'     : 'average flux during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['fp_B_Wm2_Std']                 .update({'long_name'     : 'standard deviation of the flux during 1 min averaging interval',
                                                            'instrument'    : 'Hukseflux HFP01',
                                                            'methods'       : 'thermopile conductive flux plate; analog; differential voltage',
                                                            'height'        : 'subsurface, variable depth',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['licor_co2_Avg']                .update({'long_name'     : 'average CO2 gas density during 1 min averaging interval',
                                                            'instrument'    : 'Licor 7500-DS',
                                                            'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz; protocol TCP/IP',
                                                            'height'        : '3.3 m',
                                                            'location'      : licor_location,})

    lev1_slow_atts['licor_co2_Std']                .update({'long_name'     : 'standard deviation of the CO2 gas density during 1 min averaging interval',
                                                            'instrument'    : 'Licor 7500-DS',
                                                            'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz; protocol TCP/IP',
                                                            'height'        : '3.3 m',
                                                            'location'      : licor_location,})

    lev1_slow_atts['licor_h2o_Avg']                .update({'long_name'     : 'average water vapor density during 1 min averaging interval',
                                                            'instrument'    : 'Licor 7500-DS',
                                                            'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz; protocol TCP/IP',
                                                            'height'        : '3.3 m',
                                                            'location'      : licor_location,})

    lev1_slow_atts['licor_h2o_Std']                .update({'long_name'     : 'standard deviation of the water vapor density during 1 min averaging interval',
                                                            'instrument'    : 'Licor 7500-DS',
                                                            'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz; protocol TCP/IP',
                                                            'height'        : '3.3 m',
                                                            'location'      : licor_location,})

    lev1_slow_atts['licor_co2_str_out_Avg']        .update({'long_name'     : 'average CO2 signal strength diagnostic during 1 min averaging interval',
                                                            'instrument'    : 'Licor 7500-DS',
                                                            'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz; protocol TCP/IP',
                                                            'height'        : '3.3 m',
                                                            'location'      : licor_location,})

    lev1_slow_atts['licor_co2_str_out_Std']        .update({'long_name'     : 'standard deviation of the CO2 signal strength diagnostic during 1 min averaging interval',
                                                            'instrument'    : 'Licor 7500-DS',
                                                            'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz; protocol TCP/IP',
                                                            'height'        : '3.3 m',
                                                            'location'      : licor_location,})

    lev1_slow_atts['sr30_swu_fantach_Avg']         .update({'long_name'     : 'average fan speed of the downward-facing (SWU) pyranometer during 1 min averaging period',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer case fan; RS-485',
                                                            'height'        : '3.3 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swu_heatA_Avg']           .update({'long_name'     : 'average case heating current of the downward-facing sensor during 1 min averaging period',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer case heater; RS-485 protocol',
                                                            'height'        : '3.3 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_fantach_Avg']         .update({'long_name'     : 'average fan speed of the upward-facing sensor during 1 min averaging period',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer case fan; RS-485 protocol',
                                                            'height'        : '3.3 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_heatA_Avg']           .update({'long_name'     : 'average case heating current of the upward-facing sensor during 1 min averaging period',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer case heater; RS-485 protocol',
                                                            'height'        : '3.3 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwu_fan_Avg']             .update({'long_name'     : 'average fan voltage status signal of the downward-facing ventilator during the 1 min averaging period',
                                                            'instrument'    : 'Hukseflux VU01',
                                                            'methods'       : 'ventilator fan; analog',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['ir20_lwd_fan_Avg']             .update({'long_name'     : 'average fan voltage status signal of the upward-facing ventilator during the 1 min averaging period',
                                                            'instrument'    : 'Hukseflux VU01',
                                                            'methods'       : 'ventilator fan; analog',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['efoy_Error_Max']               .update({'long_name'     : 'error code reported by the EFOY',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['efoy_FuellSt_Avg']             .update({'long_name'     : 'mixing tank fluid level',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['efoy_Ubat_Avg']                .update({'long_name'     : 'battery voltage',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['efoy_Laus_Avg']                .update({'long_name'     : 'battery charging current',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['efoy_Tst_Avg']                 .update({'long_name'     : 'stack temperature',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['efoy_Tint_Avg']                .update({'long_name'     : 'internal temperature',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['efoy_Twt_Avg']                 .update({'long_name'     : 'heat exchanger temperature',
                                                            'instrument'    : 'EFOY',
                                                            'methods'       : 'Direct Methanol Fuel Cell (DFMC) power supply; MODBUS RS-232 protocol',
                                                            'height'        : 'N/A',
                                                            'location'      : 'logger box',})

    lev1_slow_atts['sr30_swu_tilt_Avg']            .update({'long_name'     : 'horizontal tilt of the downward-facing sensor',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer case level; RS-485 protocol; level defined as 180 deg',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})

    lev1_slow_atts['sr30_swd_tilt_Avg']            .update({'long_name'     : 'horizontal tilt of the upward-facing sensor',
                                                            'instrument'    : 'Hukseflux SR30',
                                                            'methods'       : 'thermopile pyranometer case level; RS-485 protocol; level defined as 0 deg',
                                                            'height'        : '2 m',
                                                            'location'      : inst_boom_location_string,})


    return lev1_slow_atts, list(lev1_slow_atts.keys()).copy()

# defines the column names of the logger data for the flux stations and thus also the output variable names in
# the level1 data files that are supposed to be "nearly-raw netcdf records". this returns two things. 1) a list of dictionaries
# where the key is the variable name and dictionary is a list of netcdf attributes. 2) a list of variable names
def define_level1_fast():

    metek_location = "sonic mast at 3.3m"
    licor_location = "sonic mast at 3.3m"

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
    lev1_fast_atts['licor_co2']           = {'units' : 'g/m3'    }
    lev1_fast_atts['licor_h2o']           = {'units' : 'mg/m3'   }
    lev1_fast_atts['licor_pr']            = {'units' : 'hPa'     }
    lev1_fast_atts['licor_diag']          = {'units' : 'int'     }
    lev1_fast_atts['licor_co2_str']       = {'units' : 'percent' }

    lev1_fast_atts['TIMESTAMP']           .update({'long_name'     : 'time of measurement',
                                                   'instrument'    : 'CR1000X',
                                                   'methods'       : 'synched to GPS',
                                                   'height'        : 'N/A',
                                                   'location'      : 'logger box',})

    lev1_fast_atts['metek_x']             .update({'long_name'     : 'wind velocity in x',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'sonic anemometer; data reported at 20 Hz; protocol RS-422',
                                                   'height'        : '3.3 m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_y']             .update({'long_name'     : 'wind velocity in y',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'sonic anemometer; data reported at 20 Hz; protocol RS-422',
                                                   'height'        : '3.3 m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_z']             .update({'long_name'     : 'wind velocity in z',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'sonic anemometer; data reported at 20 Hz; protocol RS-422',
                                                   'height'        : '3.3 m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_T']             .update({'long_name'     : 'acoustic temperature',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'sonic anemometer; data reported at 20 Hz; protocol RS-422',
                                                   'height'        : '3.3 m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_heatstatus']    .update({'long_name'     : 'transducer heating status code',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'sonic anemometer; data reported at 20 Hz; protocol RS-422',
                                                   'height'        : '3.3 m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['metek_senspathstate'] .update({'long_name'     : 'number (of 9) of unusable paths',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'sonic anemometer; data reported at 20 Hz; protocol RS-422',
                                                   'height'        : '3.3 m',
                                                   'location'      : metek_location,})

    lev1_fast_atts['licor_diag']          .update({'long_name'     : 'bit-packed diagnostic integer',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol; bits 0-3 = signal strength; bit 5 = PLL; bit 6 = detector temp; bit 7 = chopper temp',
                                                   'height'        : '3.3 m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_co2']           .update({'long_name'     : 'CO2 gas density',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                   'height'        : '3.3 m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_h2o']           .update({'long_name'     : 'Water vapor density',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                   'height'        : '3.3 m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_co2_str']       .update({'long_name'     : 'CO2 signal strength diagnostic',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol; raw co2 reference signal relative to expected value',
                                                   'height'        : '3.3 m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_pr']            .update({'long_name'     : 'air pressure',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol; air pressure measured in electronics box',
                                                   'height'        : '3.3 m',
                                                   'location'      : licor_location,})

    return lev1_fast_atts, list(lev1_fast_atts.keys()).copy()

def define_level2_variables():

    inst_boom_location_string = 'top of station at ~2m'

    lev2_atts = OrderedDict()

    lev2_atts['lat']          = {'units' : 'degrees_north'}
    lev2_atts['lon']          = {'units' : 'degrees_east'}
    lev2_atts['heading']      = {'units' : 'degrees_true'}
    lev2_atts['zenith_true']             = {'units' : 'degrees'}
    lev2_atts['zenith_apparent']              = {'units' : 'degrees'}
    lev2_atts['azimuth']              = {'units' : 'degrees'}
    lev2_atts['ship_distance']        = {'units' : 'meters'}
    lev2_atts['ship_bearing']         = {'units' : 'degrees'}
    lev2_atts['sr50_dist']            = {'units' : 'meters'}
    lev2_atts['snow_depth']           = {'units' : 'cm'}
    lev2_atts['atmos_pressure']        = {'units' : 'hPa'}
    lev2_atts['temp']         = {'units' : 'deg C'}
    lev2_atts['rh'] = {'units' : 'percent'}
    lev2_atts['dew_point']     = {'units' : 'deg C'}
    lev2_atts['mixing_ratio']           = {'units' : 'g/kg'}
    lev2_atts['vapor_pressure']           = {'units' : 'Pa'}
    lev2_atts['rhi']          = {'units' : 'percent'}
    lev2_atts['brightness_temp_surface']        = {'units' : 'deg C'}
    lev2_atts['skin_temp_surface']       = {'units' : 'deg C'}
    lev2_atts['subsurface_heat_flux_A']     = {'units' : 'W/m2'}
    lev2_atts['subsurface_heat_flux_B']     = {'units' : 'W/m2'}
    lev2_atts['wspd_vec_mean']     = {'units' : 'm/s'}
    lev2_atts['wdir_vec_mean'] = {'units' : 'degC'}
    lev2_atts['acoustic_temp']           = {'units' : 'deg C'}
    lev2_atts['h2o_licor']            = {'units' : 'g/m3'}
    lev2_atts['co2_licor']            = {'units' : 'mg/m3'}
    lev2_atts['down_long_hemisp']        = {'units' : 'W/m2'}
    lev2_atts['down_short_hemisp']        = {'units' : 'W/m2'}
    lev2_atts['up_long_hemisp']        = {'units' : 'W/m2'}
    lev2_atts['up_short_hemisp']        = {'units' : 'W/m2'}
    lev2_atts['net_radiation']        = {'units' : 'W/m2'}

    # add everything else to the variable NetCDF attributes
    # #########################################################################################################
    lev2_atts['lat']          .update({ 'long_name'     : 'latitude from gps at station',
                                                'cf_name'       : 'latitude',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['lon']          .update({ 'long_name'     : 'longitude from gps at station',
                                                'cf_name'       : 'longitude',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['heading']      .update({ 'long_name'     : 'heading from gps at station',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'HEHDT',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['zenith_true']             .update({ 'long_name'     : 'true solar zenith angle',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'Reda and Andreas, Solar position algorithm for solar radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['zenith_apparent']             .update({ 'long_name'      : 'estimated apprarent solar zenith angle due to atmospheric refraction',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'Reda and Andreas, Solar position algorithm for solar radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['azimuth']             .update({ 'long_name'      : 'apprarent solar azimuth angle',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102',
                                                'methods'       : 'Reda and Andreas, Solar position algorithm for solar radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['ship_bearing']          .update({'long_name'     : 'absolute bearing (rel. to true north) of ship from the position of the tower',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102 & Polarstern Leica GPS',
                                                'methods'       : '',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['ship_distance']         .update({'long_name'     : 'distance between the ship and the tower',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hemisphere V102 & Polarstern Leica GPS',
                                                'methods'       : '',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['sr50_dist']            .update({ 'long_name'     : 'distance to surface from SR50; temperature compensation correction applied',
                                                'cf_name'       : '',
                                                'instrument'    : 'Campbell Scientific SR50A',
                                                'methods'       : 'unheated, temperature correction applied',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['snow_depth']           .update({ 'long_name'     : 'snow depth near station base',
                                                'cf_name'       : 'surface_snow_thickness',
                                                'instrument'    : 'Hukseflux HFP01',
                                                'methods'       : 'derived snow depth from temperature-corrected SR50 distance values based on initialization. footprint nominally 0.47 m radius.',
                                                'height'        : 'N/A',
                                                'location'      : 'at base of station under SR50',})

    lev2_atts['atmos_pressure']        .update({ 'long_name'     : 'atmospheric pressure',
                                                'cf_name'       : 'air_pressure',
                                                'instrument'    : 'Vaisala PTU 300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['temp']         .update({ 'long_name'     : 'air temperature',
                                                'cf_name'       : 'air_temperature',
                                                'instrument'    : 'Vaisala HMT330',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['rh'] .update({ 'long_name'     : 'relative humidity',
                                                'cf_name'       : 'relative_humidity',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['dew_point']     .update({ 'long_name'     : 'dewpoint temperature',
                                                'cf_name'       : 'dew_point_temperature',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'digitally polled from instument',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['mixing_ratio']           .update({ 'long_name'     : 'mixing ratio',
                                                'cf_name'       : 'specific_humidity',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['vapor_pressure']           .update({ 'long_name'     : 'vapor pressure',
                                                'cf_name'       : '',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['rhi']          .update({ 'long_name'     : 'relative humidity wrt ice',
                                                'cf_name'       : '',
                                                'instrument'    : 'Vaisala PTU300',
                                                'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['brightness_temp_surface']        .update({ 'long_name'     : 'sensor target 8-14 micron brightness temperature',
                                                'cf_name'       : '',
                                                'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                'methods'       : 'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                'height'        : 'surface',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['skin_temp_surface']       .update({ 'long_name'     : 'surface radiometric skin temperature assummed emissivity, corrected for IR reflection',
                                                'cf_name'       : '',
                                                'instrument'    : 'Apogee SI-4H1-SS IRT, IR20 LWu, LWd',
                                                'methods'       : 'Eq.(2.2) Persson et al. (2002) https://www.doi.org/10.1029/2000JC000705; emis = 0.985',
                                                'height'        : 'surface',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['subsurface_heat_flux_A']     .update({ 'long_name'     : 'conductive flux',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hukseflux HFP01',
                                                'methods'       : 'Sensitivity 63.00/1000 [mV/(W/m2)]',
                                                'height'        : 'subsurface, variable',
                                                'location'      : '10m south of station at met city',})

    lev2_atts['subsurface_heat_flux_B']      .update({'units'         : 'W/m2',
                                                'long_name'     : 'conductive flux',
                                                'cf_name'       : '',
                                                'instrument'    : 'Hukseflux HFP01',
                                                'methods'       : 'Sensitivity 63.91/1000 [mV/(W/m2)]',
                                                'height'        : 'subsurface, variable',
                                                'location'      : 'under Apogee and SR50 at station base',})

    lev2_atts['wspd_vec_mean']     .update({ 'long_name'     : 'average metek wind speed',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                'height'        : '3.3 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['wdir_vec_mean'] .update({ 'long_name'     : 'average metek wind direction',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                'height'        : '3.3 m',
                                                'location'      : inst_boom_location_string,})


    lev2_atts['acoustic_temp']           .update({ 'long_name'     : 'acoustic temperature',
                                                'cf_name'       : '',
                                                'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                'height'        : '3.3 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['h2o_licor']            .update({ 'long_name'     : 'Licor water vapor mass density',
                                                'cf_name'       : '',
                                                'instrument'    : 'Licor 7500-DS',
                                                'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                'height'        : '3.3 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['co2_licor']            .update({ 'long_name'     : 'Licor CO2 gas density',
                                                'cf_name'       : '',
                                                'instrument'    : 'Licor 7500-DS',
                                                'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                'height'        : '3.3 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['down_long_hemisp']        .update({ 'long_name'     : 'net downward longwave flux',
                                                'cf_name'       : 'surface_net_downward_longwave_flux',
                                                'instrument'    : 'Hukseflux IR20 pyrgeometer',
                                                'methods'       : 'hemispheric longwave radiation',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['down_short_hemisp']        .update({ 'long_name'     : 'net downward shortwave flux',
                                                'cf_name'       : 'surface_net_downward_shortwave_flux',
                                                'instrument'    : 'Hukseflux SR30 pyranometer',
                                                'methods'       : 'hemispheric shortwave radiation',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['up_long_hemisp']        .update({ 'long_name'     : 'net upward longwave flux',
                                                'cf_name'       : 'surface_net_upward_longwave_flux',
                                                'instrument'    : 'Hukseflux IR20 pyrgeometer',
                                                'methods'       : 'hemispheric longwave radiation',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['up_short_hemisp']        .update({ 'long_name'     : 'net upward shortwave flux',
                                                'cf_name'       : 'surface_net_upward_shortwave_flux',
                                                'instrument'    : 'Hukseflux SR30 pyranometer',
                                                'methods'       : 'hemispheric shortwave radiation',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    lev2_atts['net_radiation']        .update({ 'long_name'     : 'cumulative surface radiative flux',
                                                'cf_name'       : 'surface_net_radiative_flux',
                                                'instrument'    : 'SR30 and IR20 radiometers',
                                                'methods'       : 'combined hemispheric radiation measurements',
                                                'height'        : '2 m',
                                                'location'      : inst_boom_location_string,})

    return lev2_atts, list(lev2_atts.keys()).copy()

def define_turb_variables():
    inst_boom_location_string = 'top of station at ~2m'

    turb_atts = OrderedDict()

    turb_atts['Hs']              = {'units' : 'W/m2'}
    turb_atts['Hl']              = {'units' : 'W/m2'}
    turb_atts['Hl_Webb']         = {'units' : 'W/m2'}
    turb_atts['CO2_flux']        = {'units' : 'mg*m^-2*s^-1'}
    turb_atts['CO2_flux_Webb']   = {'units' : 'mg*m^-2*s^-1'}
    turb_atts['Cd']              = {'units' : 'dimensionless'}
    turb_atts['ustar']           = {'units' : 'm/s'}
    turb_atts['Tstar']           = {'units' : 'degC'}
    turb_atts['zeta_level_n']    = {'units' : 'dimensionless'}
    turb_atts['wu_csp']          = {'units' : 'm^2/s^2'}
    turb_atts['wv_csp']          = {'units' : 'm^2/s^2'}
    turb_atts['uv_csp']          = {'units' : 'm^2/s^2'}
    turb_atts['wT_csp']          = {'units' : 'degC*m/s'}
    turb_atts['uT_csp']          = {'units' : 'degC*m/s'}
    turb_atts['vT_csp']          = {'units' : 'degC*m/s'}
    turb_atts['wq_csp']          = {'units' : 'm/s*kg/m3'}
    turb_atts['uq_csp']          = {'units' : 'm/s*kg/m3'}
    turb_atts['vq_csp']          = {'units' : 'm/s*kg/m3'}
    turb_atts['wc_csp']          = {'units' : 'm*s^-1*mg*m^-2*s^-1'}
    turb_atts['uc_csp']          = {'units' : 'm*s^-1*mg*m^-2*s^-1'}
    turb_atts['vc_csp']          = {'units' : 'm*s^-1*mg*m^-2*s^-1'}
    turb_atts['phi_u']           = {'units' : 'dimensionless'}
    turb_atts['phi_v']           = {'units' : 'dimensionless'}
    turb_atts['phi_w']           = {'units' : 'dimensionless'}
    turb_atts['phi_T']           = {'units' : 'dimensionless'}
    turb_atts['phi_uT']          = {'units' : 'dimensionless'}
    turb_atts['nSu']             = {'units' : 'Power/Hz'}
    turb_atts['nSv']             = {'units' : 'Power/Hz'}
    turb_atts['nSw']             = {'units' : 'Power/Hz'}
    turb_atts['nSt']             = {'units' : 'Power/Hz'}
    turb_atts['nSq']             = {'units' : 'Power/Hz'}
    turb_atts['nSc']             = {'units' : 'Power/Hz'}
    turb_atts['epsilon_u']       = {'units' : 'm^2/s^3'}
    turb_atts['epsilon_v']       = {'units' : 'm^2/s^3'}
    turb_atts['epsilon_w']       = {'units' : 'm^2/s^3'}
    turb_atts['epsilon']         = {'units' : 'm^2/s^3'}
    turb_atts['Phi_epsilon']     = {'units' : 'dimensionless'}
    turb_atts['Nt']              = {'units' : 'degC^2/s'}
    turb_atts['Phi_Nt']          = {'units' : 'dimensionless'}
    turb_atts['Phix']            = {'units' : 'deg'}
    turb_atts['DeltaU']          = {'units' : 'm/s'}
    turb_atts['DeltaV']          = {'units' : 'm/s'}
    turb_atts['DeltaT']          = {'units' : 'degC'}
    turb_atts['Deltaq']          = {'units' : 'kg/kg'}
    turb_atts['Deltac']          = {'units' : 'mg/m3'}
    turb_atts['Kurt_u']          = {'units' : 'unitless'}
    turb_atts['Kurt_v']          = {'units' : 'unitless'}
    turb_atts['Kurt_w']          = {'units' : 'unitless'}
    turb_atts['Kurt_T']          = {'units' : 'unitless'}
    turb_atts['Kurt_q']          = {'units' : 'unitless'}
    turb_atts['Kurt_c']          = {'units' : 'unitless'}
    turb_atts['Kurt_uw']         = {'units' : 'unitless'}
    turb_atts['Kurt_vw']         = {'units' : 'unitless'}
    turb_atts['Kurt_wT']         = {'units' : 'unitless'}
    turb_atts['Kurt_uT']         = {'units' : 'unitless'}
    turb_atts['Kurt_wq']         = {'units' : 'unitless'}
    turb_atts['Kurt_uq']         = {'units' : 'unitless'}
    turb_atts['Kurt_wc']         = {'units' : 'unitless'}
    turb_atts['Kurt_uc']         = {'units' : 'unitless'}
    turb_atts['Skew_u']          = {'units' : 'unitless'}
    turb_atts['Skew_v']          = {'units' : 'unitless'}
    turb_atts['Skew_w']          = {'units' : 'unitless'}
    turb_atts['Skew_T']          = {'units' : 'unitless'}
    turb_atts['Skew_q']          = {'units' : 'unitless'}
    turb_atts['Skew_c']          = {'units' : 'unitless'}
    turb_atts['Skew_uw']         = {'units' : 'unitless'}
    turb_atts['Skew_vw']         = {'units' : 'unitless'}
    turb_atts['Skew_wT']         = {'units' : 'unitless'}
    turb_atts['Skew_uT']         = {'units' : 'unitless'}
    turb_atts['Skew_wq']         = {'units' : 'unitless'}
    turb_atts['Skew_uq']         = {'units' : 'unitless'}
    turb_atts['Skew_wc']         = {'units' : 'unitless'}
    turb_atts['Skew_uc']         = {'units' : 'unitless'}
    turb_atts['fs']              = {'units' : 'Hz'}
    turb_atts['sus']             = {'units' : '(m/s)^2/Hz'}
    turb_atts['svs']             = {'units' : '(m/s)^2/Hz'}
    turb_atts['sws']             = {'units' : '(m/s)^2/Hz'}
    turb_atts['sTs']             = {'units' : 'degC^2/Hz'}
    turb_atts['sqs']             = {'units' : '(kg/m3)/Hz'}
    turb_atts['scs']             = {'units' : '(mg m^-2 s^-1)^2/Hz'}
    turb_atts['cwus']            = {'units' : '(m/s)^2/Hz'}
    turb_atts['cwvs']            = {'units' : '(m/s)^2/Hz'}
    turb_atts['cuvs']            = {'units' : '(m/s)^2/Hz'}
    turb_atts['cwTs']            = {'units' : '(m/s*degC)/Hz'}
    turb_atts['cuTs']            = {'units' : '(m/s*degC)/Hz'}
    turb_atts['cvTs']            = {'units' : '(m/s*degC)/Hz'}
    turb_atts['cwqs']            = {'units' : '(m/s*kg/m3)/Hz'}
    turb_atts['cuqs']            = {'units' : '(m/s*kg/m3)/Hz'}
    turb_atts['cvqs']            = {'units' : '(m/s*kg/m3)/Hz'}
    turb_atts['cwcs']            = {'units' : '(m/s*mg*m^-2*s^-1)/Hz'}
    turb_atts['cucs']            = {'units' : '(m/s*mg*m^-2*s^-1)/Hz'}
    turb_atts['cvcs']            = {'units' : '(m/s*mg*m^-2*s^-1)/Hz'}
    turb_atts['bulk_Hs']         = {'units' : 'W/m2'}
    turb_atts['bulk_Hl']         = {'units' : 'W/m2'}
    turb_atts['bulk_Hl_Webb']    = {'units' : 'W/m2'}
    turb_atts['bulk_tau']        = {'units' : 'Pa'}
    turb_atts['bulk_z0']         = {'units' : 'm'}
    turb_atts['bulk_z0t']        = {'units' : 'm'}
    turb_atts['bulk_z0q']        = {'units' : 'm'}
    turb_atts['bulk_L']          = {'units' : 'm'}
    turb_atts['bulk_ustar']      = {'units' : 'm/s'}
    turb_atts['bulk_tstar']      = {'units' : 'K'}
    turb_atts['bulk_qstar']      = {'units' : 'kg/kg'}
    turb_atts['bulk_dter']       = {'units' : 'degC'}
    turb_atts['bulk_dqer']       = {'units' : 'kg/kg'}
    turb_atts['bulk_Cd']         = {'units' : 'unitless'}
    turb_atts['bulk_Ch']         = {'units' : 'unitless'}
    turb_atts['bulk_Ce']         = {'units' : 'unitless'}
    turb_atts['bulk_Cdn_10m']    = {'units' : 'unitless'}
    turb_atts['bulk_Chn_10m']    = {'units' : 'unitless'}
    turb_atts['bulk_Cen_10m']    = {'units' : 'unitless'}
    turb_atts['bulk_Rr']         = {'units' : 'unitless'}
    turb_atts['bulk_Rt']         = {'units' : 'unitless'}
    turb_atts['bulk_Rq']         = {'units' : 'unitless'}


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
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Hl']              .update({'long_name'  : 'latent heat flux',
                                          'cf_name'    : 'upward_latent_heat_flux_in_air',
                                          'instrument' : 'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                          'methods'    : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source h2o data was vapor density (g/m3). No WPL correction applied.',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Hl_Webb']         .update({'long_name'  : 'Webb density correction for the latent heat flux',
                                          'cf_name'    : '',
                                          'instrument' : 'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                          'methods'    : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source h2o data was vapor density (g/m3). No WPL correction applied.',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['CO2_flux']        .update({'long_name'  : 'co2 mass flux',
                                          'cf_name'    : '',
                                          'instrument' : 'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                          'methods'    : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source co2 data was co2 density (mmol/m3). No WPL correction applied.',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['CO2_flux_Webb']    .update({'long_name'  : 'Webb density correction for the co2 mass flux',
                                          'cf_name'    : '',
                                          'instrument' : 'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                          'methods'    : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source co2 data was co2 density (mmol/m3). No WPL correction applied.',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Cd']              .update({'long_name'  : 'Drag coefficient based on the momentum flux, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['ustar']           .update({'long_name'  : 'friction velocity (based only on the downstream, uw, stress components)',
                                          'cf_name'    : '',
                                          'height'     : 'n/a',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Tstar']           .update({'long_name'  : 'temperature scale',
                                          'cf_name'    : '',
                                          'height'     : 'n/a',
                                          'location'   : inst_boom_location_string,})

    turb_atts['zeta_level_n']    .update({'long_name'  : 'Monin-Obukhov stability parameter, z/L, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wu_csp']          .update({'long_name'  : 'wu-covariance based on the wu-cospectra integration',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wv_csp']          .update({'long_name'  : 'wv-covariance based on the wv-cospectra integration',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['uv_csp']          .update({'long_name'  : 'uv-covariance based on the uv-cospectra integration',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wT_csp']          .update({'long_name'  : 'wT-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['uT_csp']          .update({'long_name'  : 'uT-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['vT_csp']          .update({'long_name'  : 'vT-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wq_csp']          .update({'long_name'  : 'wq-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['uq_csp']          .update({'long_name'  : 'uq-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['vq_csp']          .update({'long_name'  : 'vq-covariance, vertical flux of the sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['wc_csp']          .update({'long_name'  : 'wc-covariance, vertical flux of co2',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['uc_csp']          .update({'long_name'  : 'uc-covariance, vertical flux of co2',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['vc_csp']          .update({'long_name'  : 'vc-covariance, vertical flux of co2',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_u']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_v']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_w']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_T']           .update({'long_name'  : 'MO universal function for the standard deviations, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['phi_uT']          .update({'long_name'  : 'MO universal function for the horizontal heat flux, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon_u']       .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon_v']       .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon_w']       .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['epsilon']         .update({'long_name'  : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phi_epsilon']     .update({'long_name'  : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['nSu']             .update({'long_name'  : 'Median spectral slope in the inertial subrange of u',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['nSv']             .update({'long_name'  : 'Median spectral slope in the inertial subrange of v',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['nSw']             .update({'long_name'  : 'Median spectral slope in the inertial subrange of w',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['nSt']             .update({'long_name'  : 'Median spectral slope in the inertial subrange of sonic temperature',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['nSq']             .update({'long_name'  : 'Median spectral slope in the inertial subrange of q',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['nSc']             .update({'long_name'  : 'Median spectral slope in the inertial subrange of co2',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Nt']              .update({'long_name'  : 'The dissipation (destruction) rate for half the temperature variance',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phi_Nt']          .update({'long_name'  : 'Monin-Obukhov universal function Phi_Nt, calculated from 2 m',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Phix']            .update({'long_name'  : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['DeltaU']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['DeltaV']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['DeltaT']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Deltaq']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of q (trend)',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Deltac']          .update({'long_name'  : 'Stationarity diagnostic: Steadiness of co2 (trend)',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_u']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_v']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_w']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_T']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_q']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_c']          .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_uw']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_vw']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_wT']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_uT']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_wq']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_uq']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_wc']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Kurt_uc']         .update({'long_name'  : 'Kurtosis',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_u']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_v']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_w']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_T']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_q']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_c']          .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_uw']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_vw']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_wT']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_uT']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_wq']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_uq']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_wc']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['Skew_uc']         .update({'long_name'  : 'Skewness',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['fs']              .update({'long_name'  : 'frequency',
                                          'cf_name'    : '',
                                          'height'     : 'n/a',
                                          'location'   : inst_boom_location_string,})

    turb_atts['sus']             .update({'long_name'  : 'smoothed power spectral density (Welch) of u wind vector on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['svs']             .update({'long_name'  : 'smoothed power spectral density (Welch) of v wind vector on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['sws']             .update({'long_name'  : 'smoothed power spectral density (Welch) of w wind vector on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['sTs']             .update({'long_name'  : 'smoothed power spectral density (Welch) of sonic temperature on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['sqs']             .update({'long_name'  : 'smoothed power spectral density (Welch) of q on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['scs']             .update({'long_name'  : 'smoothed power spectral density (Welch) of co2 on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cwus']            .update({'long_name'  : 'smoothed co-spectral density between w and u wind vectors on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cwvs']            .update({'long_name'  : 'smoothed co-spectral density between w and v wind vectors on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cuvs']            .update({'long_name'  : 'smoothed co-spectral density between u and v wind vectors on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : 'n/a',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cwTs']            .update({'long_name'  : 'smoothed co-spectral density between w wind vector and sonic temperature on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cuTs']            .update({'long_name'  : 'smoothed co-spectral density between u wind vector and sonic temperature on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cvTs']            .update({'long_name'  : 'smoothed co-spectral density between v wind vector and sonic temperature on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cwqs']            .update({'long_name'  : 'smoothed co-spectral density between w wind vector and q on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cuqs']            .update({'long_name'  : 'smoothed co-spectral density between u wind vector and q on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cvqs']            .update({'long_name'  : 'smoothed co-spectral density between v wind vector and q on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cwcs']            .update({'long_name'  : 'smoothed co-spectral density between w wind vector and co2 on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cucs']            .update({'long_name'  : 'smoothed co-spectral density between u wind vector and co2 on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['cvcs']            .update({'long_name'  : 'smoothed co-spectral density between v wind vector and co2 on frequency, fs',
                                          'cf_name'    : '',
                                          'height'     : '3.3 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Hs']         .update({'long_name'  : 'sensible heat flux',
                                          'cf_name'    : 'upward_sensible_heat_flux_in_air',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Hl']         .update({'long_name'  : 'latent heat flux',
                                          'cf_name'    : 'upward_latent_heat_flux_in_air',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Hl_Webb']     .update({'long_name' : 'Webb density correction for the latent heat flux',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm, Webb et al. (1980) https://doi.org/10.1002/qj.49710644707',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_tau']        .update({'long_name'  : 'wind stress',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_z0']          .update({'long_name' : 'roughness length',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_z0t']         .update({'long_name' : 'roughness length, temperature',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_z0q']         .update({'long_name' : 'roughness length, humidity',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_L']           .update({'long_name' : 'Obukhov length',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_ustar']       .update({'long_name' : 'friction velocity (sqrt(momentum flux)), ustar',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_tstar']       .update({'long_name' : 'temperature scale, tstar',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_qstar']       .update({'long_name' : 'specific humidity scale, qstar ',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_dter']        .update({'long_name' : 'diagnostic',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_dqer']        .update({'long_name' : 'diagnostic',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Cd']          .update({'long_name' : 'transfer coefficient for stress',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '2 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Ch']          .update({'long_name' : 'transfer coefficient for Hs',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Ce']          .update({'long_name' : 'transfer coefficient for Hl',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Cdn_10m']     .update({'long_name' : '10 m neutral transfer coefficient for stress',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Chn_10m']     .update({'long_name' : '10 m neutral transfer coefficient for Hs',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Cen_10m']     .update({'long_name' : '10 m neutral transfer coefficient for Hl',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Rr']          .update({'long_name' : 'roughness Reynolds number for velocity',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Rt']          .update({'long_name' : 'roughness Reynolds number for temperature',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    turb_atts['bulk_Rq']          .update({'long_name' : 'roughness Reynolds number for humidity',
                                          'cf_name'    : '',
                                          'instrument' : 'various',
                                          'methods'    : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                          'height'     : '10 m',
                                          'location'   : inst_boom_location_string,})

    return turb_atts, list(turb_atts.keys()).copy()
