# ############################################################################################
# This file does the heady work of mapping the parameters observed at the tower to the output
# variable names and attributes that make it into the netcdf files.  This file essentially
# provides a map of where the data came from and where it went to.
#
# Syntax:
#
# If a variable was measured at the tower and renamed, the 'mosaic_var' attribute shows the
# name of the variable as was originally provided by the logging system (loggernet or NOAA
# services). If a variable is derived by calculation using the raw observed parameters,
# 'mosaic_var' is given the special key word 'derived'. This is done because...  
# ############################################################################################
def define_output_variables(): 
    default_fill_value   = -9999.0

    data_out = {} 

    # data variables that are pulled in by logger at 1sec intervals ...
    # #################################################################################################
    # data_out[''] = {'mosaic_var' : ''}
    data_out['tower_lat']                 = {'mosaic_var' : 'gps_lat_frac'}
    data_out['tower_lon']                 = {'mosaic_var' : 'gps_lon_frac'}
    data_out['tower_heading']             = {'mosaic_var' : 'gps_hdg'}
    data_out['gps_alt']                   = {'mosaic_var' : 'gps_alt'}
    data_out['gps_qc']                    = {'mosaic_var' : 'gps_qc'}
    data_out['gps_nsat']                  = {'mosaic_var' : 'gps_nsat'}
    data_out['gps_hdop']                  = {'mosaic_var' : 'gps_hdop'}
    data_out['PTemp']                     = {'mosaic_var' : 'PTemp'}
    data_out['logger_scantime']           = {'mosaic_var' : 'call_time_mainscan'}
    data_out['sr50_dist']                 = {'mosaic_var' : 'sr50_dist'}
    data_out['temp_vaisala_2m']           = {'mosaic_var' : 'vaisala_T_2m'}
    data_out['temp_vaisala_6m']           = {'mosaic_var' : 'vaisala_T_6m'}
    data_out['temp_vaisala_10m']          = {'mosaic_var' : 'vaisala_T_10m'}
    data_out['temp_vaisala_mast']         = {'mosaic_var' : 'mast_T'}
    data_out['rel_humidity_vaisala_2m']   = {'mosaic_var' : 'vaisala_RH_2m'}
    data_out['rel_humidity_vaisala_6m']   = {'mosaic_var' : 'vaisala_RH_6m'}
    data_out['rel_humidity_vaisala_10m']  = {'mosaic_var' : 'vaisala_RH_10m'}
    data_out['rel_humidity_vaisala_mast'] = {'mosaic_var' : 'mast_RH'}
    data_out['dewpoint_vaisala_2m']       = {'mosaic_var' : 'vaisala_Td_2m'}
    data_out['dewpoint_vaisala_6m']       = {'mosaic_var' : 'vaisala_Td_6m'}
    data_out['dewpoint_vaisala_10m']      = {'mosaic_var' : 'vaisala_Td_10m'}
    data_out['pressure_vaisala_2m']       = {'mosaic_var' : 'vaisala_P_2m'}
    data_out['mast_pressure']             = {'mosaic_var' : 'mast_P'}
    data_out['body_T_IRT']                = {'mosaic_var' : 'apogee_targ_T'}
    data_out['surface_T_IRT']             = {'mosaic_var' : 'apogee_body_T'}
    data_out['flux_plate_A_mv']           = {'mosaic_var' : 'fp_A_mV'}
    data_out['flux_plate_B_mv']           = {'mosaic_var' : 'fp_B_mV'}
    data_out['flux_plate_A_Wm2']          = {'mosaic_var' : 'fp_A_Wm2'}
    data_out['flux_plate_B_Wm2']          = {'mosaic_var' : 'fp_B_Wm2'}

    # data variables that are derived from the observations above that are of interest
    # 'derived' is a just keyword used in this software to note that it wasn't pulled in from the data files
    data_out['snow_depth']                = {'mosaic_var' : 'derived'}
    data_out['MR_vaisala_2m']             = {'mosaic_var' : 'derived'}
    data_out['MR_vaisala_6m']             = {'mosaic_var' : 'derived'}
    data_out['MR_vaisala_10m']            = {'mosaic_var' : 'derived'}
    data_out['MR_vaisala_mast']           = {'mosaic_var' : 'derived'}
    data_out['abs_humidity_vaisala_2m']   = {'mosaic_var' : 'derived'}
    data_out['abs_humidity_vaisala_6m']   = {'mosaic_var' : 'derived'}
    data_out['abs_humidity_vaisala_10m']  = {'mosaic_var' : 'derived'}
    data_out['abs_humidity_vaisala_mast'] = {'mosaic_var' : 'derived'}
    data_out['enthalpy_vaisala_2m']       = {'mosaic_var' : 'derived'}
    data_out['enthalpy_vaisala_6m']       = {'mosaic_var' : 'derived'}
    data_out['enthalpy_vaisala_10m']      = {'mosaic_var' : 'derived'}
    data_out['enthalpy_vaisala_mast']     = {'mosaic_var' : 'derived'}
    data_out['pw_vaisala_2m']             = {'mosaic_var' : 'derived'}
    data_out['pw_vaisala_6m']             = {'mosaic_var' : 'derived'}
    data_out['pw_vaisala_10m']            = {'mosaic_var' : 'derived'}
    data_out['pw_vaisala_mast']           = {'mosaic_var' : 'derived'}
    data_out['RHi_vaisala_2m']            = {'mosaic_var' : 'derived'}
    data_out['RHi_vaisala_6m']            = {'mosaic_var' : 'derived'}
    data_out['RHi_vaisala_10m']           = {'mosaic_var' : 'derived'}
    data_out['RHi_vaisala_mast']          = {'mosaic_var' : 'derived'}
    data_out['dewpoint_vaisala_mast']     = {'mosaic_var' : 'derived'}
    data_out['Hs_2m']                     = {'mosaic_var' : 'derived'}
    data_out['Hs_6m']                     = {'mosaic_var' : 'derived'}
    data_out['Hs_10m']                    = {'mosaic_var' : 'derived'}
    data_out['Hs_mast']                   = {'mosaic_var' : 'derived'}
    data_out['Hs_hi_2m']                  = {'mosaic_var' : 'derived'}
    data_out['Hs_hi_6m']                  = {'mosaic_var' : 'derived'}
    data_out['Hs_hi_10m']                 = {'mosaic_var' : 'derived'}
    data_out['Hs_hi_mast']                = {'mosaic_var' : 'derived'}
    data_out['Cd_2m']                     = {'mosaic_var' : 'derived'}
    data_out['Cd_6m']                     = {'mosaic_var' : 'derived'}
    data_out['Cd_10m']                    = {'mosaic_var' : 'derived'}
    data_out['Cd_mast']                   = {'mosaic_var' : 'derived'}
    data_out['Cd_hi_2m']                  = {'mosaic_var' : 'derived'}
    data_out['Cd_hi_6m']                  = {'mosaic_var' : 'derived'}
    data_out['Cd_hi_10m']                 = {'mosaic_var' : 'derived'}
    data_out['Cd_hi_mast']                = {'mosaic_var' : 'derived'}
    data_out['ustar_2m']                  = {'mosaic_var' : 'derived'}
    data_out['ustar_6m']                  = {'mosaic_var' : 'derived'}
    data_out['ustar_10m']                 = {'mosaic_var' : 'derived'}
    data_out['ustar_mast']                = {'mosaic_var' : 'derived'}
    data_out['ustar_hi_2m']               = {'mosaic_var' : 'derived'}
    data_out['ustar_hi_6m']               = {'mosaic_var' : 'derived'}
    data_out['ustar_hi_10m']              = {'mosaic_var' : 'derived'}
    data_out['ustar_hi_mast']             = {'mosaic_var' : 'derived'}
    data_out['Tstar_2m']                  = {'mosaic_var' : 'derived'}
    data_out['Tstar_6m']                  = {'mosaic_var' : 'derived'}
    data_out['Tstar_10m']                 = {'mosaic_var' : 'derived'}
    data_out['Tstar_mast']                = {'mosaic_var' : 'derived'}
    data_out['Tstar_hi_2m']               = {'mosaic_var' : 'derived'}
    data_out['Tstar_hi_6m']               = {'mosaic_var' : 'derived'}
    data_out['Tstar_hi_10m']              = {'mosaic_var' : 'derived'}
    data_out['Tstar_hi_mast']             = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_2m']           = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_6m']           = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_10m']          = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_mast']         = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_hi_2m']        = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_hi_6m']        = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_hi_10m']       = {'mosaic_var' : 'derived'}
    data_out['zeta_level_n_hi_mast']      = {'mosaic_var' : 'derived'}
    data_out['wu_csp_2m']                 = {'mosaic_var' : 'derived'}
    data_out['wu_csp_6m']                 = {'mosaic_var' : 'derived'}
    data_out['wu_csp_10m']                = {'mosaic_var' : 'derived'}
    data_out['wu_csp_mast']               = {'mosaic_var' : 'derived'}
    data_out['wv_csp_2m']                 = {'mosaic_var' : 'derived'}
    data_out['wv_csp_6m']                 = {'mosaic_var' : 'derived'}
    data_out['wv_csp_10m']                = {'mosaic_var' : 'derived'}
    data_out['wv_csp_mast']               = {'mosaic_var' : 'derived'}
    data_out['uv_csp_2m']                 = {'mosaic_var' : 'derived'}
    data_out['uv_csp_6m']                 = {'mosaic_var' : 'derived'}
    data_out['uv_csp_10m']                = {'mosaic_var' : 'derived'}
    data_out['uv_csp_mast']               = {'mosaic_var' : 'derived'}
    data_out['wT_csp_2m']                 = {'mosaic_var' : 'derived'}
    data_out['wT_csp_6m']                 = {'mosaic_var' : 'derived'}
    data_out['wT_csp_10m']                = {'mosaic_var' : 'derived'}
    data_out['wT_csp_mast']               = {'mosaic_var' : 'derived'}
    data_out['uT_csp_2m']                 = {'mosaic_var' : 'derived'}
    data_out['uT_csp_6m']                 = {'mosaic_var' : 'derived'}
    data_out['uT_csp_10m']                = {'mosaic_var' : 'derived'}
    data_out['uT_csp_mast']               = {'mosaic_var' : 'derived'}
    data_out['vT_csp_2m']                 = {'mosaic_var' : 'derived'}
    data_out['vT_csp_6m']                 = {'mosaic_var' : 'derived'}
    data_out['vT_csp_10m']                = {'mosaic_var' : 'derived'}
    data_out['vT_csp_mast']               = {'mosaic_var' : 'derived'}
    data_out['phi_u_2m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_u_6m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_u_10m']                 = {'mosaic_var' : 'derived'}
    data_out['phi_u_mast']                = {'mosaic_var' : 'derived'}
    data_out['phi_v_2m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_v_6m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_v_10m']                 = {'mosaic_var' : 'derived'}
    data_out['phi_v_mast']                = {'mosaic_var' : 'derived'}
    data_out['phi_w_2m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_w_6m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_w_10m']                 = {'mosaic_var' : 'derived'}
    data_out['phi_w_mast']                = {'mosaic_var' : 'derived'}
    data_out['phi_T_2m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_T_6m']                  = {'mosaic_var' : 'derived'}
    data_out['phi_T_10m']                 = {'mosaic_var' : 'derived'}
    data_out['phi_T_mast']                = {'mosaic_var' : 'derived'}
    data_out['phi_uT_2m']                 = {'mosaic_var' : 'derived'}
    data_out['phi_uT_6m']                 = {'mosaic_var' : 'derived'}
    data_out['phi_uT_10m']                = {'mosaic_var' : 'derived'}
    data_out['phi_uT_mast']               = {'mosaic_var' : 'derived'}
    data_out['phi_u_hi_2m']               = {'mosaic_var' : 'derived'}
    data_out['phi_u_hi_6m']               = {'mosaic_var' : 'derived'}
    data_out['phi_u_hi_10m']              = {'mosaic_var' : 'derived'}
    data_out['phi_u_hi_mast']             = {'mosaic_var' : 'derived'}
    data_out['phi_v_hi_2m']               = {'mosaic_var' : 'derived'}
    data_out['phi_v_hi_6m']               = {'mosaic_var' : 'derived'}
    data_out['phi_v_hi_10m']              = {'mosaic_var' : 'derived'}
    data_out['phi_v_hi_mast']             = {'mosaic_var' : 'derived'}
    data_out['phi_w_hi_2m']               = {'mosaic_var' : 'derived'}
    data_out['phi_w_hi_6m']               = {'mosaic_var' : 'derived'}
    data_out['phi_w_hi_10m']              = {'mosaic_var' : 'derived'}
    data_out['phi_w_hi_mast']             = {'mosaic_var' : 'derived'}
    data_out['phi_T_hi_2m']               = {'mosaic_var' : 'derived'}
    data_out['phi_T_hi_6m']               = {'mosaic_var' : 'derived'}
    data_out['phi_T_hi_10m']              = {'mosaic_var' : 'derived'}
    data_out['phi_T_hi_mast']             = {'mosaic_var' : 'derived'}
    data_out['phi_uT_hi_2m']              = {'mosaic_var' : 'derived'}
    data_out['phi_uT_hi_6m']              = {'mosaic_var' : 'derived'}
    data_out['phi_uT_hi_10m']             = {'mosaic_var' : 'derived'}
    data_out['phi_uT_hi_mast']            = {'mosaic_var' : 'derived'}
    data_out['epsilon_u_2m']              = {'mosaic_var' : 'derived'}
    data_out['epsilon_u_6m']              = {'mosaic_var' : 'derived'}
    data_out['epsilon_u_10m']             = {'mosaic_var' : 'derived'}
    data_out['epsilon_u_mast']            = {'mosaic_var' : 'derived'}
    data_out['epsilon_v_2m']              = {'mosaic_var' : 'derived'}
    data_out['epsilon_v_6m']              = {'mosaic_var' : 'derived'}
    data_out['epsilon_v_10m']             = {'mosaic_var' : 'derived'}
    data_out['epsilon_v_mast']            = {'mosaic_var' : 'derived'}
    data_out['epsilon_w_2m']              = {'mosaic_var' : 'derived'}
    data_out['epsilon_w_6m']              = {'mosaic_var' : 'derived'}
    data_out['epsilon_w_10m']             = {'mosaic_var' : 'derived'}
    data_out['epsilon_w_mast']            = {'mosaic_var' : 'derived'}
    data_out['epsilon_2m']                = {'mosaic_var' : 'derived'}
    data_out['epsilon_6m']                = {'mosaic_var' : 'derived'}
    data_out['epsilon_10m']               = {'mosaic_var' : 'derived'}
    data_out['epsilon_mast']              = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_2m']            = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_6m']            = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_10m']           = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_mast']          = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_hi_2m']         = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_hi_6m']         = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_hi_10m']        = {'mosaic_var' : 'derived'}
    data_out['Phi_epsilon_hi_mast']       = {'mosaic_var' : 'derived'}
    data_out['Nt_2m']                     = {'mosaic_var' : 'derived'}
    data_out['Nt_6m']                     = {'mosaic_var' : 'derived'}
    data_out['Nt_10m']                    = {'mosaic_var' : 'derived'}
    data_out['Nt_mast']                   = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_10m']                = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_mast']               = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_hi_2m']              = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_hi_6m']              = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_hi_10m']             = {'mosaic_var' : 'derived'}
    data_out['Phi_Nt_hi_mast']            = {'mosaic_var' : 'derived'}
    data_out['Phix_2m']                   = {'mosaic_var' : 'derived'}
    data_out['Phix_6m']                   = {'mosaic_var' : 'derived'}
    data_out['Phix_10m']                  = {'mosaic_var' : 'derived'}
    data_out['Phix_mast']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaU_2m']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaU_6m']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaU_10m']                = {'mosaic_var' : 'derived'}
    data_out['DeltaU_mast']               = {'mosaic_var' : 'derived'}
    data_out['DeltaV_2m']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaV_6m']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaV_10m']                = {'mosaic_var' : 'derived'}
    data_out['DeltaV_mast']               = {'mosaic_var' : 'derived'}
    data_out['DeltaT_2m']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaT_6m']                 = {'mosaic_var' : 'derived'}
    data_out['DeltaT_10m']                = {'mosaic_var' : 'derived'}
    data_out['DeltaT_mast']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_u_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_u_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_u_10m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_u_mast']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_v_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_v_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_v_10m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_v_mast']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_w_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_w_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_w_10m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_w_mast']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_T_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_T_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Kurt_T_10m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_T_mast']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_uw_2m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_uw_6m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_uw_10m']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_uw_mast']              = {'mosaic_var' : 'derived'}
    data_out['Kurt_vw_2m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_vw_6m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_vw_10m']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_vw_mast']              = {'mosaic_var' : 'derived'}
    data_out['Kurt_wT_2m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_wT_6m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_wT_10m']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_wT_mast']              = {'mosaic_var' : 'derived'}
    data_out['Kurt_uT_2m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_uT_6m']                = {'mosaic_var' : 'derived'}
    data_out['Kurt_uT_10m']               = {'mosaic_var' : 'derived'}
    data_out['Kurt_uT_mast']              = {'mosaic_var' : 'derived'}
    data_out['Skew_u_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_u_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_u_10m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_u_mast']               = {'mosaic_var' : 'derived'}
    data_out['Skew_v_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_v_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_v_10m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_v_mast']               = {'mosaic_var' : 'derived'}
    data_out['Skew_w_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_w_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_w_10m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_w_mast']               = {'mosaic_var' : 'derived'}
    data_out['Skew_T_2m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_T_6m']                 = {'mosaic_var' : 'derived'}
    data_out['Skew_T_10m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_T_mast']               = {'mosaic_var' : 'derived'}
    data_out['Skew_uw_2m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_uw_6m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_uw_10m']               = {'mosaic_var' : 'derived'}
    data_out['Skew_uw_mast']              = {'mosaic_var' : 'derived'}
    data_out['Skew_vw_2m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_vw_6m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_vw_10m']               = {'mosaic_var' : 'derived'}
    data_out['Skew_vw_mast']              = {'mosaic_var' : 'derived'}
    data_out['Skew_wT_2m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_wT_6m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_wT_10m']               = {'mosaic_var' : 'derived'}
    data_out['Skew_wT_mast']              = {'mosaic_var' : 'derived'}
    data_out['Skew_uT_2m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_uT_6m']                = {'mosaic_var' : 'derived'}
    data_out['Skew_uT_10m']               = {'mosaic_var' : 'derived'}
    data_out['Skew_uT_mast']              = {'mosaic_var' : 'derived'}

    # from NOAA services, pulled in at 20Hz ('raw') and 1 minute averages ('stats')
    # 1 second data is computed from the 'raw' files to align with logger observations
    data_out['wind_speed_metek_2m']       = {'mosaic_var' : 'derived'} # derived from u/v
    data_out['wind_speed_metek_6m']       = {'mosaic_var' : 'derived'}
    data_out['wind_speed_metek_10m']      = {'mosaic_var' : 'derived'}
    data_out['wind_speed_metek_mast']     = {'mosaic_var' : 'derived'}

    data_out['wind_direction_metek_2m']   = {'mosaic_var' : 'derived'} # derived from u/v)
    data_out['wind_direction_metek_6m']   = {'mosaic_var' : 'derived'}
    data_out['wind_direction_metek_10m']  = {'mosaic_var' : 'derived'}
    data_out['wind_direction_metek_mast'] = {'mosaic_var' : 'derived'}

    data_out['temp_variance_metek_2m']    = {'mosaic_var' : 'derived'} # derived from u/v
    data_out['temp_variance_metek_6m']    = {'mosaic_var' : 'derived'}
    data_out['temp_variance_metek_10m']   = {'mosaic_var' : 'derived'}
    data_out['temp_variance_metek_mast']  = {'mosaic_var' : 'derived'}

    data_out['H2O_licor']                 = {'mosaic_var' : 'derived'}
    data_out['CO2_licor']                 = {'mosaic_var' : 'derived'}
    data_out['temp_licor']                = {'mosaic_var' : 'derived'}
    data_out['pr_licor']                  = {'mosaic_var' : 'derived'}

    data_out['u_metek_2m']                = {'mosaic_var' : 'derived'}
    data_out['u_metek_6m']                = {'mosaic_var' : 'derived'}
    data_out['u_metek_10m']               = {'mosaic_var' : 'derived'}
    data_out['u_metek_mast']              = {'mosaic_var' : 'derived'}

    data_out['v_metek_2m']                = {'mosaic_var' : 'derived'}
    data_out['v_metek_6m']                = {'mosaic_var' : 'derived'}
    data_out['v_metek_10m']               = {'mosaic_var' : 'derived'}
    data_out['v_metek_mast']              = {'mosaic_var' : 'derived'}

    data_out['w_metek_2m']                = {'mosaic_var' : 'derived'}
    data_out['w_metek_6m']                = {'mosaic_var' : 'derived'}
    data_out['w_metek_10m']               = {'mosaic_var' : 'derived'}
    data_out['w_metek_mast']              = {'mosaic_var' : 'derived'}

    data_out['temp_metek_2m']             = {'mosaic_var' : 'derived'}
    data_out['temp_metek_6m']             = {'mosaic_var' : 'derived'}
    data_out['temp_metek_10m']            = {'mosaic_var' : 'derived'}
    data_out['temp_metek_mast']           = {'mosaic_var' : 'derived'}

    data_out['stddev_u_metek_2m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_v_metek_2m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_w_metek_2m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_T_metek_2m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_u_metek_6m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_v_metek_6m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_w_metek_6m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_T_metek_6m']         = {'mosaic_var' : 'derived'}
    data_out['stddev_u_metek_10m']        = {'mosaic_var' : 'derived'}
    data_out['stddev_v_metek_10m']        = {'mosaic_var' : 'derived'}
    data_out['stddev_w_metek_10m']        = {'mosaic_var' : 'derived'}
    data_out['stddev_T_metek_10m']        = {'mosaic_var' : 'derived'}
    data_out['stddev_u_metek_mast']       = {'mosaic_var' : 'derived'}
    data_out['stddev_v_metek_mast']       = {'mosaic_var' : 'derived'}
    data_out['stddev_w_metek_mast']       = {'mosaic_var' : 'derived'}
    data_out['stddev_T_metek_mast']       = {'mosaic_var' : 'derived'}

    # diagnostic information from the metek stats files, these can go in their own netcdf 'group'
    # to keep the netcdf file clean(er) I think... haven't used this feature yet
    #   !! I'm not sure this is necessary. More operational. It is sort of implicit in the fast file, albeit
    #   with lower resolution than the raw file (like a 10hz sample coupld be the avg of jsut 1
    #   20 hz meas if the other is missing). Perhaps we return to this and build some code that
    #   makes summary plots for uptime or something.
    data_out['co2_signal_licor']          = {'mosaic_var' : 'derived'}
    # data_out['good_u_2m']                 = {'mosaic_var' : 'GoodSamp_u_velocity'}
    # data_out['good_v_2m']                 = {'mosaic_var' : 'GoodSamp_v_velocity'}
    # data_out['good_w_2m']                 = {'mosaic_var' : 'GoodSamp_w_velocity'}
    # data_out['good_T_2m']                 = {'mosaic_var' : 'GoodSamp_virtual_temp'}
    # data_out['good_u_6m']                 = {'mosaic_var' : 'GoodSamp_u_velocity'}
    # data_out['good_v_6m']                 = {'mosaic_var' : 'GoodSamp_v_velocity'}
    # data_out['good_w_6m']                 = {'mosaic_var' : 'GoodSamp_w_velocity'}
    # data_out['good_T_6m']                 = {'mosaic_var' : 'GoodSamp_virtual_temp'}
    # data_out['good_u_10m']                = {'mosaic_var' : 'GoodSamp_u_velocity'}
    # data_out['good_v_10m']                = {'mosaic_var' : 'GoodSamp_v_velocity'}
    # data_out['good_w_10m']                = {'mosaic_var' : 'GoodSamp_w_velocity'}
    # data_out['good_T_10m']                = {'mosaic_var' : 'GoodSamp_virtual_temp'}
    # data_out['good_u_mast']               = {'mosaic_var' : 'GoodSamp_u_velocity'}
    # data_out['good_v_mast']               = {'mosaic_var' : 'GoodSamp_v_velocity'}
    # data_out['good_w_mast']               = {'mosaic_var' : 'GoodSamp_w_velocity'}
    # data_out['good_T_mast']               = {'mosaic_var' : 'GoodSamp_virtual_temp'}

    # add the other important things to the data variable NetCDF attributes
    # #########################################################################################################
    bottom_location_string = 'first level on met city tower'
    middle_location_string = 'second level on met city tower'
    top_location_string    = 'third level on met city tower'
    mast_location_string   = 'top of radio mast at met city'

    data_out['tower_lat']                 .update({'units'         : 'degrees_north',
                                                   'long_name'     : 'latitude from gps at tower',
                                                   'cf_name'       : 'latitude',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['tower_lon']                 .update({'units'         : 'degrees_east',
                                                   'long_name'     : 'longitude from gps at tower',
                                                   'cf_name'       : 'longitude',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : '$GPRMC, $GPGGA, GPGZDA',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['tower_heading']             .update({'units'         : 'degrees_true',
                                                   'long_name'     : 'heading from gps at tower',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : '$HEHDT',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['gps_alt']                   .update({'units'         : 'meters',
                                                   'long_name'     : 'altitude from gps at tower',
                                                   'cf_name'       : 'altitude',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['gps_qc']                    .update({'units'         : 'code',
                                                   'long_name'     : 'fix quality: 0 = invalid; 1 = gps fix (sps); 2 = dgps fix; 3 = pps fix; 4 = real time kinematic; 5 = float rtk; 6 = estimated (deck reckoning); 7 = manual input mode; 8 = simulation mode.',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['gps_nsat']                  .update({'units'         : 'counts',
                                                   'long_name'     : 'number of satellites available to gps',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['gps_hdop']                  .update({'units'         : 'unitless',
                                                   'long_name'     : 'horizontal dilution of precision',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hemisphere V102',
                                                   'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['logger_scantime']           .update({'units'         : 'milliseconds',
                                                   'long_name'     : 'time taken for logger to complete scan',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Campbell Scientific CR1000X',
                                                   'methods'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : 'N/A',
                                                   'location'      : bottom_location_string,})

    data_out['sr50_dist']                 .update({'units'         : 'meters',
                                                   'long_name'     : 'distance to surface from SR50; temperature compensation correction applied',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Campbell Scientific SR50A',
                                                   'methods'       : 'unheated, temperature correction applied',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1.75m',
                                                   'location'      : bottom_location_string,})

    data_out['temp_vaisala_2m']           .update({'units'         : 'deg C',
                                                   'long_name'     : 'temperature',
                                                   'cf_name'       : 'air_temperature',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['temp_vaisala_6m']           .update({'units'         : 'deg C',
                                                   'long_name'     : 'temperature',
                                                   'cf_name'       : 'air_temperature',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['temp_vaisala_10m']          .update({'units'         : 'deg C',
                                                   'long_name'     : 'temperature',
                                                   'cf_name'       : 'air_emperature',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['temp_vaisala_mast']         .update({'units'         : 'deg C',
                                                   'long_name'     : 'temperature',
                                                   'cf_name'       : 'air_temperature',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['dewpoint_vaisala_2m']       .update({'units'         : 'dec C',
                                                   'long_name'     : 'dewpoint',
                                                   'cf_name'       : 'dew_point_temperature',
                                                   'instrument'    : 'Vaisala PTU300',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '2m',
                                                   'location'      : bottom_location_string,})

    data_out['dewpoint_vaisala_6m']       .update({'units'         : 'dec C',
                                                   'long_name'     : 'dewpoint',
                                                   'cf_name'       : 'dew_point_temperature',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '6m',
                                                   'location'      : middle_location_string,})

    data_out['dewpoint_vaisala_10m']       .update({'units'         : 'dec C',
                                                   'long_name'     : 'dewpoint',
                                                   'cf_name'       : 'dew_point_temperature',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '10m',
                                                   'location'      : top_location_string,})

    data_out['dewpoint_vaisala_mast']     .update({'units'         : 'dec C',
                                                   'long_name'     : 'dewpoint',
                                                   'cf_name'       : 'dew_point_temperatre',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '23 or 30m',
                                                   'location'      : mast_location_string,})

    data_out['rel_humidity_vaisala_2m']   .update({'units'         : 'percent',
                                                   'long_name'     : 'relative humidity wrt water',
                                                   'cf_name'       : 'relative_humidity',
                                                   'instrument'    : 'Vaisala PTU300',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '2m',
                                                   'location'      : bottom_location_string,})

    data_out['rel_humidity_vaisala_6m']   .update({'units'         : 'percent',
                                                   'long_name'     : 'relative humidity wrt water',
                                                   'cf_name'       : 'relative humidity',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '6m',
                                                   'location'      : middle_location_string,})

    data_out['rel_humidity_vaisala_10m']  .update({'units'         : 'percent',
                                                   'long_name'     : 'relative humidity wrt water',
                                                   'cf_name'       : 'relative humidity',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '10m',
                                                   'location'      : top_location_string,})

    data_out['rel_humidity_vaisala_mast'] .update({'units'         : 'percent',
                                                   'long_name'     : 'relative humidity wrt water',
                                                   'cf_name'       : 'relative humidity',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : 'variable 23-30m',
                                                   'location'      : mast_location_string,})

    data_out['pressure_vaisala_2m']       .update({'units'         : 'hPa',
                                                   'long_name'     : 'air pressure at 2m',
                                                   'cf_name'       : 'air_pressure',
                                                   'instrument'    : 'Vaisala PTU 300',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '2m',
                                                   'location'      : mast_location_string,})

    data_out['mast_pressure']             .update({'units'         : 'hPa',
                                                   'long_name'     : 'air pressure',
                                                   'cf_name'       : 'air_pressure',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : 'variable 23-30m',
                                                   'location'      : bottom_location_string,})

    data_out['body_T_IRT']                .update({'units'         : 'deg C',
                                                   'long_name'     : 'instrument body temperature',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                   'methods'       : 'digitally polled from instument',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '2m',
                                                   'location'      : bottom_location_string,})

    data_out['surface_T_IRT']             .update({'units'         : 'deg C',
                                                   'long_name'     : 'Apogee IRT target 8-14 micron brightness temperature.',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                   'methods'       : 'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : 'surface',
                                                   'location'      : bottom_location_string,})

    data_out['flux_plate_A_mv']           .update({'units'         : 'mv',
                                                   'long_name'     : 'voltage from Hukseflux plate A',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hukseflux HFP01',
                                                   'methods'       : 'analog voltage read by CR1000X',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : '10m south of tower at met city',})

    data_out['flux_plate_B_mv']           .update({'units'         : 'mv',
                                                   'long_name'     : 'voltage from Hukseflux plate B',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hukseflux HFP01',
                                                   'methods'       : 'analog voltage read by CR1000X',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : 'under Apogee and SR50 at tower base',})

    data_out['flux_plate_A_Wm2']          .update({'units'         : 'Wm2',
                                                   'long_name'     : 'conductive flux from plate A',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hukseflux HFP01',
                                                   'methods'       : 'Sensitivity 63.00/1000 [mV/(W/m2)]',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : '10m south of tower at met city',})

    data_out['flux_plate_B_Wm2']          .update({'units'         : 'Wm2',
                                                   'long_name'     : 'conductive flux from plate B',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Hukseflux HFP01',
                                                   'methods'       : 'Sensitivity 63.91/1000 [mV/(W/m2)]',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : 'under Apogee and SR50 at tower base',})


    data_out['snow_depth']                .update({'units'         : 'cm',
                                                   'long_name'     : 'snow depth near tower base',
                                                   'cf_name'       : 'surface_snow_thickness',
                                                   'instrument'    : 'Hukseflux HFP01',
                                                   'methods'       : 'derived snow depth from temperature-corrected SR50 distance values based on initialization 10/27/19. footprint nominally 0.47 m radius.',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : 'N/A',
                                                   'location'      : 'at base of tower under SR50',})

    data_out['MR_vaisala_2m']             .update({'units'         : 'g/kg',
                                                   'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                   'cf_name'       : 'specific_humidity',
                                                   'instrument'    : 'Vaisala PTU300',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['MR_vaisala_6m']             .update({'units'         : 'g/kg',
                                                   'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                   'cf_name'       : 'specific_humidity',
                                                   'instrument'    : 'Vaisala PTU300',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['MR_vaisala_10m']            .update({'units'         : 'g/kg',
                                                   'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                   'cf_name'       : 'specific_humidity',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['MR_vaisala_mast']           .update({'units'         : 'g/kg',
                                                   'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                   'cf_name'       : 'specific_humidity',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['RHi_vaisala_2m']            .update({'units'         : 'percent',
                                                   'long_name'     : 'ice RH derived using T/P/RH',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala PTU300',
                                                   'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['RHi_vaisala_6m']            .update({'units'         : 'percent',
                                                   'long_name'     : 'ice RH derived using T/P/RH',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['RHi_vaisala_10m']           .update({'units'         : 'percent',
                                                   'long_name'     : 'ice RH derived using T/P/RH',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['RHi_vaisala_mast']          .update({'units'         : 'percent',
                                                   'long_name'     : 'ice RH derived using T/P/RH',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['pw_vaisala_2m']             .update({'units'         : 'Pa',
                                                   'long_name'     : 'vapor pressure',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala PTU300',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['pw_vaisala_6m']             .update({'units'         : 'Pa',
                                                   'long_name'     : 'vapor pressure',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['pw_vaisala_10m']            .update({'units'         : 'Pa',
                                                   'long_name'     : 'vapor pressure',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala HMT330',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['pw_vaisala_mast']           .update({'units'         : 'Pa',
                                                   'long_name'     : 'vapor pressure',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Vaisala WXT530',
                                                   'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['wind_speed_metek_2m']       .update({'units'         : 'm/s',
                                                   'long_name'     : 'average metek wind speed',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['wind_speed_metek_6m']       .update({'units'         : 'm/s',
                                                   'long_name'     : 'average metek wind speed',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['wind_speed_metek_10m']      .update({'units'         : 'm/s',
                                                   'long_name'     : 'average metek wind speed',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['wind_speed_metek_mast']     .update({'units'         : 'm/s',
                                                   'long_name'     : 'average metek wind speed',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})


    data_out['wind_direction_metek_2m']   .update({'units'         : 'deg true',
                                                   'long_name'     : 'average metek wind direction',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['wind_direction_metek_6m']   .update({'units'         : 'deg true',
                                                   'long_name'     : 'average metek wind direction',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['wind_direction_metek_10m']  .update({'units'         : 'deg true',
                                                   'long_name'     : 'average metek wind direction',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['wind_direction_metek_mast'] .update({'units'         : 'deg true',
                                                   'long_name'     : 'average metek wind direction',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})


    data_out['temp_variance_metek_2m']    .update({'units'         : '(deg C)^2',
                                                   'long_name'     : 'metek sonic temperature obs variance',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['temp_variance_metek_6m']    .update({'units'         : '(deg C)^2',
                                                   'long_name'     : 'metek sonic temperature obs variance',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['temp_variance_metek_10m']   .update({'units'         : '(deg C)^2',
                                                   'long_name'     : 'metek sonic temperature obs variance',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['temp_variance_metek_mast']  .update({'units'         : '(deg C)^2',
                                                   'long_name'     : 'metek sonic temperature obs variance',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['H2O_licor']                 .update({'units'         : 'g/kg',
                                                   'long_name'     : 'Licor water vapor mixing ratio',
                                                   'cf_name'       : 'specific_humidity',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['CO2_licor']                 .update({'units'         : 'g/kg',
                                                   'long_name'     : 'Licor CO2 mixing ratio',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['temp_licor']                .update({'units'         : 'deg C',
                                                   'long_name'     : 'temperature',
                                                   'cf_name'       : 'air_temperature',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'thermistor positioned along strut of open-path optical gas analyzer, source data reported at 20 Hz',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['pr_licor']                  .update({'units'         : 'hPa',
                                                   'long_name'     : 'Licor pressure',
                                                   'cf_name'       : 'air_pressure',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'pressure sensor located in electronics box. source data reported at 20 Hz',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '1m',
                                                   'location'      : bottom_location_string,})

    data_out['u_metek_2m']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek u-component',
                                                   'cf_name'       : 'northward_wind',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['u_metek_6m']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek u-component',
                                                   'cf_name'       : 'northward_wind',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['u_metek_10m']               .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek u-component',
                                                   'cf_name'       : 'northward_wind',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['u_metek_mast']              .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek u-component',
                                                   'cf_name'       : 'northward_wind',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})


    data_out['v_metek_2m']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek v-component',
                                                   'cf_name'       : 'westward_wind',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['v_metek_6m']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek v-component',
                                                   'cf_name'       : 'westward_wind',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['v_metek_10m']               .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek v-component',
                                                   'cf_name'       : 'westward_wind',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['v_metek_mast']              .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek v-component',
                                                   'cf_name'       : 'westward_wind',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})


    data_out['w_metek_2m']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek w-component',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['w_metek_6m']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek w-component',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['w_metek_10m']               .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek w-component',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['w_metek_mast']              .update({'units'         : 'm/s',
                                                   'long_name'     : 'Metek w-component',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['temp_metek_2m']             .update({'units'         : 'deg C',
                                                   'long_name'     : 'Metek sonic temperature',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['temp_metek_6m']             .update({'units'         : 'deg C',
                                                   'long_name'     : 'Metek sonic temperature',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['temp_metek_10m']            .update({'units'         : 'deg C',
                                                   'long_name'     : 'Metek sonic temperature',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['temp_metek_mast']           .update({'units'         : 'deg C',
                                                   'long_name'     : 'Metek sonic temperature',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['stddev_u_metek_2m']         .update({'units'         : 'm/s',
                                                   'long_name'     : 'u metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['stddev_v_metek_2m']         .update({'units'         : 'm/s',
                                                   'long_name'     : 'v metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['stddev_w_metek_2m']         .update({'units'         : 'm/s',
                                                   'long_name'     : 'w metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['stddev_T_metek_2m']         .update({'units'         : 'deg C',
                                                   'long_name'     : 'T metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['stddev_u_metek_6m']         .update({'units'         : 'm/s',
                                                   'long_name'     : 'u metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['stddev_v_metek_6m']         .update({'units'         : 'm/s',
                                                   'long_name'     : 'v metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['stddev_w_metek_6m']         .update({'units'         : 'm/s',
                                                   'long_name'     : 'w metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['stddev_T_metek_6m']         .update({'units'         : 'deg C',
                                                   'long_name'     : 'T metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['stddev_u_metek_10m']        .update({'units'         : 'm/s',
                                                   'long_name'     : 'u metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'u defined positive north in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['stddev_v_metek_10m']        .update({'units'         : 'm/s',
                                                   'long_name'     : 'v metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['stddev_w_metek_10m']        .update({'units'         : 'm/s',
                                                   'long_name'     : 'w metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['stddev_T_metek_10m']        .update({'units'         : 'deg C',
                                                   'long_name'     : 'T metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['stddev_u_metek_mast']       .update({'units'         : 'm/s',
                                                   'long_name'     : 'u metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['stddev_v_metek_mast']       .update({'units'         : 'm/s',
                                                   'long_name'     : 'v metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'v defined positive west in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['stddev_w_metek_mast']       .update({'units'         : 'm/s',
                                                   'long_name'     : 'w metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'w defined positive up in right-hand coordinate system',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['stddev_T_metek_mast']       .update({'units'         : 'deg C',
                                                   'long_name'     : 'T metek obs standard deviation',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['co2_signal_licor']          .update({'units'         : 'percent',
                                                   'long_name'     : 'Licor CO2 signal strength diagnostic',
                                                   'cf_name'       : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : 'signal strength [0-100%] is a measure of attenuation of the optics (e.g., by salt residue or ice) that applies to both co2 and h2o observations',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    # data_out['good_u_2m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # data_out['good_v_2m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # data_out['good_w_2m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # data_out['good_T_2m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # data_out['good_u_6m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # data_out['good_v_6m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # data_out['good_w_6m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # data_out['good_T_6m']                 .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # data_out['good_u_10m']                .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # data_out['good_v_10m']                .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # data_out['good_w_10m']                .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # data_out['good_T_10m']                .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # data_out['good_u_mast']               .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})
    #
    # data_out['good_v_mast']               .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})
    #
    # data_out['good_w_mast']               .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})
    #
    # data_out['good_T_mast']               .update({'units'         : 'counts',
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'missing_value' : default_fill_value,
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})

    # !! The turbulence data. A lot of it... Almost wonder if this metadata should reside in a separate
    # file?  Some variables are dimensionless, meaning they are both scaled & unitless and the result is
    # independent of height such that it sounds a little funny to have a var name like
    # MO_dimensionless_param_2_m, but that is the only way to distinguish between the 4 calculations. So,
    # for these I added ", calculated from 2 m" or whatever into the long_name.  Maybe there is a better
    # way?

    data_out['Hs_2m']                     .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Hs_6m']                     .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Hs_10m']                    .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Hs_mast']                   .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Hs_hi_2m']                  .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Hs_hi_6m']                  .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Hs_hi_10m']                 .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})
    data_out['Hs_hi_mast']                .update({'units'         : 'Wm2',
                                                   'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                                   'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                                   'instrument'    : 'Metek USA-1 sonic anemometer',
                                                   'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Cd_2m']                     .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the momentum flux, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Cd_6m']                     .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the momentum flux, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Cd_10m']                    .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the momentum flux, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Cd_mast']                   .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the momentum flux, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Cd_hi_2m']                  .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Cd_hi_6m']                  .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Cd_hi_10m']                 .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Cd_hi_mast']                .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['ustar_2m']                  .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['ustar_6m']                  .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['ustar_10m']                 .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['ustar_mast']                .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['ustar_hi_2m']               .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['ustar_hi_6m']               .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['ustar_hi_10m']              .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['ustar_hi_mast']             .update({'units'         : 'm/s',
                                                   'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Tstar_2m']                  .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Tstar_6m']                  .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Tstar_10m']                 .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Tstar_mast']                .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Tstar_hi_2m']               .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Tstar_hi_6m']               .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Tstar_hi_10m']              .update({'units'         : 'degC',
                                                   'long_name'     : 'ftemperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Tstar_hi_mast']             .update({'units'         : 'degC',
                                                   'long_name'     : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['zeta_level_n_2m']           .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['zeta_level_n_6m']           .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['zeta_level_n_10m']          .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['zeta_level_n_mast']         .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['zeta_level_n_hi_2m']        .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['zeta_level_n_hi_6m']        .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['zeta_level_n_hi_10m']       .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['zeta_level_n_hi_mast']      .update({'units'         : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['wu_csp_2m']                 .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['wu_csp_6m']                 .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['wu_csp_10m']                .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['wu_csp_mast']               .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['wv_csp_2m']                 .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['wv_csp_6m']                 .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['wv_csp_10m']                .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['wv_csp_mast']               .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['uv_csp_2m']                 .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['uv_csp_6m']                 .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['uv_csp_10m']                .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['uv_csp_mast']               .update({'units'         : 'm^2/s^2',
                                                   'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['wT_csp_2m']                 .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['wT_csp_6m']                 .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['wT_csp_10m']                .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['wT_csp_mast']               .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['uT_csp_2m']                 .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['uT_csp_6m']                 .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['uT_csp_10m']                .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['uT_csp_mast']               .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['vT_csp_2m']                 .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['vT_csp_6m']                 .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['vT_csp_10m']                .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['vT_csp_mast']               .update({'units'         : 'degC m/s',
                                                   'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_u_2m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_u_6m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_u_10m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_u_mast']               .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_v_2m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_v_6m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_v_10m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_v_mast']               .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_w_2m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_w_6m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_w_10m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_w_mast']               .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_T_2m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_T_6m']                 .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_T_10m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_T_mast']               .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_uT_2m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_uT_6m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_uT_10m']               .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_uT_mast']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_u_hi_2m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_u_hi_6m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_u_hi_10m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_u_hi_mast']            .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_v_hi_2m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_v_hi_6m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_v_hi_10m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_v_hi_mast']            .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_w_hi_2m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_w_hi_6m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_w_hi_10m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_w_hi_mast']            .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_T_hi_2m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_T_hi_6m']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_T_hi_10m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_T_hi_mast']            .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['phi_uT_hi_2m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxesx, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['phi_uT_hi_6m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['phi_uT_hi_10m']            .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['phi_uT_hi_mast']           .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['epsilon_u_2m']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['epsilon_u_6m']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['epsilon_u_10m']            .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['epsilon_u_mast']           .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['epsilon_v_2m']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['epsilon_v_6m']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['epsilon_v_10m']            .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['epsilon_v_mast']           .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['epsilon_w_2m']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['epsilon_w_6m']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['epsilon_w_10m']            .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['epsilon_w_mast']           .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['epsilon_2m']               .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['epsilon_6m']               .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['epsilon_10m']              .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['epsilon_mast']             .update({'units'          : 'm^2/s^3',
                                                   'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Phi_epsilon_2m']           .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Phi_epsilon_6m']           .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Phi_epsilon_10m']          .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Phi_epsilon_mast']         .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Phi_epsilon_hi_2m']        .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Phi_epsilon_hi_6m']        .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Phi_epsilon_hi_10m']       .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Phi_epsilon_hi_mast']      .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Nt_2m']                    .update({'units'          : 'degC^2/s',
                                                   'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Nt_6m']                    .update({'units'          : 'degC^2/s',
                                                   'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Nt_10m']                   .update({'units'          : 'degC^2/s',
                                                   'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Nt_mast']                  .update({'units'          : 'degC^2/s',
                                                   'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Phi_Nt_2m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Phi_Nt_6m']                .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Phi_Nt_10m']               .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Phi_Nt_mast']              .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Phi_Nt_hi_2m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Phi_Nt_hi_6m']             .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Phi_Nt_hi_10m']            .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Phi_Nt_hi_mast']           .update({'units'          : 'dimensionless',
                                                   'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Phix_2m']                  .update({'units'          : 'deg',
                                                   'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Phix_6m']                  .update({'units'          : 'deg',
                                                   'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Phix_10m']                 .update({'units'          : 'deg',
                                                   'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Phix_mast']                .update({'units'          : 'deg',
                                                   'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['DeltaU_2m']                .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['DeltaU_6m']                .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['DeltaU_10m']               .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['DeltaU_mast']              .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['DeltaV_2m']                .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['DeltaV_6m']                .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['DeltaV_10m']               .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['DeltaV_mast']              .update({'units'          : 'm/s',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['DeltaT_2m']                .update({'units'          : 'degC',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['DeltaT_6m']                .update({'units'          : 'degC',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['DeltaT_10m']               .update({'units'          : 'degC',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['DeltaT_mast']              .update({'units'          : 'degC',
                                                   'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_u_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_u_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_u_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_u_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_v_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_v_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_v_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_v_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_w_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_w_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_w_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_w_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_T_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_T_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_T_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_T_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_uw_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_uw_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_uw_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_uw_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_vw_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_vw_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_vw_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_vw_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_wT_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_wT_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_wT_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_wT_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Kurt_uT_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Kurt_uT_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Kurt_uT_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Kurt_uT_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Kurtosis',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_u_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_u_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_u_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_u_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_v_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_v_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_v_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_v_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_w_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_w_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_w_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_w_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_T_2m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_T_6m']                .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_T_10m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_T_mast']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_uw_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_uw_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_uw_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_uw_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_vw_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_vw_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_vw_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_vw_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_wT_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_wT_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_wT_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_wT_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    data_out['Skew_uT_2m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : bottom_location_string,})

    data_out['Skew_uT_6m']               .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : middle_location_string,})

    data_out['Skew_uT_10m']              .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : top_location_string,})

    data_out['Skew_uT_mast']             .update({'units'          : 'unitless',
                                                   'long_name'     : 'Skewness',
                                                   'cf_name'       : '',
                                                   'missing_value' : default_fill_value,
                                                   'height'        : '',
                                                   'location'      : mast_location_string,})

    return data_out
