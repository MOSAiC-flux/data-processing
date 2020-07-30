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

from collections import OrderedDict

def code_version():
    cv = ['0.7', '7/15/2020', 'ccox']
    return cv

# file_type must be "slow", "fast", "level2", or "turb"
def define_global_atts(file_type):
    cv = code_version()
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
        'version'          : cv[0]+', '+cv[1],
    }
    # Some specifics for the tubulence file
    if file_type == "slow":
        global_atts['quality_control']  = 'This Level 1 product is for archival purposes and has undergone minimal data processing and quality control, please contact the authors/PI if you would like to know more.',

    elif file_type == "fast":
        global_atts['quality_control']  = 'This "Level 1" product is for archival purposes and has undergone minimal data processing and quality control, please contact the authors/PI if you would like to know more.',

    elif file_type == "level2":
        global_atts['quality_control']  = 'Significant quality control in place for the observations used in the derived products. This Level 2 data is processed in many significant ways and this particular version is *for preliminary results only*. Please have discussions with the authors about what this means if you would like to use it this data for any analyses.',

    elif file_type == "turb":  # some specifics for the tubulence file
        global_atts['quality_control']  = 'The source data measured at 20 Hz was quality controlled. Variables relevant for quality control of the derived quantities supplied in this file are also supplied, but the derived quantities themselves are NOT quality-controlled.',
        global_atts['methods']          = 'Code developed from routines used by NOAA ETL/PSD3. Original code read_sonic_hr was written by Chris Fairall and later adopted by Andrey Grachev as read_sonic_10Hz_1hr_Tiksi_2012_9m_v2.m, read_sonic_hr_10.m, read_Eureka_sonic_0_hr_2009_egu.m, read_sonic_20Hz_05hr_Materhorn2012_es2',
        global_atts['file_creator']     = 'Michael R. Gallagher; Christopher J. Cox',
        global_atts['references']       = 'Grachev et al. (2013), BLM, 147(1), 51-82, doi 10.1007/s10546-012-9771-0; Grachev et al. (2008) Acta Geophysica. 56(1): 142-166; J.C. Kaimal & J.J. Finnigan "Atmospheric Boundary Layer Flows" (1994)',
        global_atts['acknowledgements'] = 'Dr. Andrey Grachev (CIRES), Dr. Chris Fairall (NOAA), Dr. Ludovic Bariteau (CIRES)'

    return OrderedDict(global_atts) 
    
def define_level1_slow():

    licor_location              = 'first level on met city tower'
    bottom_location_string      = 'first level on met city tower'
    middle_location_string      = 'second level on met city tower'
    top_location_string         = 'third level on met city tower'
    mast_location_string        = 'top of radio mast at met city'
    noodleville_location_string = 'spring noodleville at met city'

    lev1_slow_atts = {}
    lev1_slow_atts['TIMESTAMP']          = {'units' : 'TS'}       
    lev1_slow_atts['RECORD']             = {'units' : 'RN'}       
    lev1_slow_atts['gps_lat_deg']        = {'units' : 'deg'}      
    lev1_slow_atts['gps_lat_min']        = {'units' : 'min'}      
    lev1_slow_atts['gps_lon_deg']        = {'units' : 'deg'}      
    lev1_slow_atts['gps_lon_min']        = {'units' : 'min'}      
    lev1_slow_atts['gps_hdg']            = {'units' : 'deg'}      
    lev1_slow_atts['gps_alt']            = {'units' : 'm'}        
    lev1_slow_atts['gps_qc']             = {'units' : 'unitless'}         
    lev1_slow_atts['gps_nsat']           = {'units' : 'N'}        
    lev1_slow_atts['gps_hdop']           = {'units' : 'unitless'} 
    lev1_slow_atts['PTemp']              = {'units' : 'degC'}     
    lev1_slow_atts['batt_volt']          = {'units' : 'V'}        
    lev1_slow_atts['call_time_mainscan'] = {'units' : 'mSec'}     
    lev1_slow_atts['apogee_body_T']      = {'units' : 'degC'}     
    lev1_slow_atts['apogee_targ_T']      = {'units' : 'degC'}     
    lev1_slow_atts['sr50_dist']          = {'units' : 'm'}        
    lev1_slow_atts['vaisala_RH_2m']      = {'units' : '%'}        
    lev1_slow_atts['vaisala_T_2m']       = {'units' : 'degC'}     
    lev1_slow_atts['vaisala_Td_2m']      = {'units' : 'degC'}     
    lev1_slow_atts['vaisala_P_2m']       = {'units' : 'hPa'}      
    lev1_slow_atts['vaisala_RH_6m']      = {'units' : '%'}        
    lev1_slow_atts['vaisala_T_6m']       = {'units' : 'degC'}     
    lev1_slow_atts['vaisala_Td_6m']      = {'units' : 'degC'}     
    lev1_slow_atts['vaisala_RH_10m']     = {'units' : '%'}        
    lev1_slow_atts['vaisala_T_10m']      = {'units' : 'degC'}     
    lev1_slow_atts['vaisala_Td_10m']     = {'units' : 'degC'}     
    lev1_slow_atts['fp_A_mV']            = {'units' : 'mV'}       
    lev1_slow_atts['fp_A_Wm2']           = {'units' : 'Wm2'}      
    lev1_slow_atts['fp_B_mV']            = {'units' : 'mV'}       
    lev1_slow_atts['fp_B_Wm2']           = {'units' : 'Wm2'}      
    lev1_slow_atts['mast_T']             = {'units' : 'degC'}     
    lev1_slow_atts['mast_RH']            = {'units' : '%'}        
    lev1_slow_atts['mast_P']             = {'units' : 'hPa'}

    # noodleville stuff
    lev1_slow_atts['mast_RECORD']             = {'units' : 'RN'}
    lev1_slow_atts['mast_gps_lat_deg_Avg']    = {'units' : 'deg'}
    lev1_slow_atts['mast_gps_lat_min_Avg']    = {'units' : 'min'}
    lev1_slow_atts['mast_gps_lon_deg_Avg']    = {'units' : 'deg'}
    lev1_slow_atts['mast_gps_lon_min_Avg']    = {'units' : 'min'}
    lev1_slow_atts['mast_gps_hdg_Avg']        = {'units' : 'deg'}
    lev1_slow_atts['mast_gps_alt_Avg']        = {'units' : 'm'}
    lev1_slow_atts['mast_gps_qc']             = {'units' : 'unitless'}
    lev1_slow_atts['mast_gps_hdop_Avg']       = {'units' : 'unitless'}
    lev1_slow_atts['mast_gps_nsat_Avg']       = {'units' : 'N'}
    lev1_slow_atts['mast_PTemp']              = {'units' : 'degC'}
    lev1_slow_atts['mast_batt_volt']          = {'units' : 'V'}
    lev1_slow_atts['mast_call_time_mainscan'] = {'units' : 'mSec'}
    
    lev1_slow_atts['licor_ball_mV']      = {'units' : 'mv'}

    lev1_slow_atts['TIMESTAMP']          .update({'long_name'  : 'timestamp from tower data logger',     
                                                  'instrument' : 'Campbell CR1000X',                     
                                                  'methods'    : '',                                     
                                                  'height'     : '0m',			                       
                                                  'location'   : bottom_location_string,})               

    lev1_slow_atts['RECORD']             .update({'long_name'  : 'record number from tower data logger',
                                                  'instrument' : 'Campbell CR1000X',
                                                  'methods'    : '',
                                                  'height'     : '0m',			            
                                                  'location'   : bottom_location_string,})               

    lev1_slow_atts['gps_lat_deg']        .update({'long_name'  : 'latitude from gps at tower',  
                                                  'instrument' : 'Hemisphere V102',		    
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                  'height'     : '1m',			    
                                                  'location'   : bottom_location_string,})    	    
                                                                                                  
    lev1_slow_atts['gps_lat_min']        .update({'long_name'  : 'latitude from gps at tower',
                                                  'instrument' : 'Hemisphere V102',		    
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	      
                                                  'height'     : '1m',			            
                                                  'location'   : bottom_location_string,})    

    lev1_slow_atts['gps_lon_deg']        .update({'long_name'  :'longitude from gps at tower', 
                                                  'instrument' : 'Hemisphere V102',		      
                                                  'methods'    : '$GPRMC, $GPGGA, GPGZDA',	  
                                                  'height'     : '1m',			              
                                                  'location'   : bottom_location_string,})      

    lev1_slow_atts['gps_lon_min']        .update({'long_name'  :'longitude from gps at tower', 
                                                  'instrument' : 'Hemisphere V102',		      
                                                  'methods'    : '$GPRMC, $GPGGA, GPGZDA',	  
                                                  'height'     : '1m',			              
                                                  'location'   : bottom_location_string,})      

    lev1_slow_atts['gps_hdg']            .update({'long_name'  : 'heading from gps at tower', 
                                                  'instrument' : 'Hemisphere V102',		   
                                                  'methods'    : '$HEHDT',			   
                                                  'height'     : '1m',			   
                                                  'location'   : bottom_location_string,})     

    lev1_slow_atts['gps_alt']            .update({'long_name'  : 'altitude from gps at tower',
                                                  'instrument' : 'Hemisphere V102',		   
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	   
                                                  'height'     : '1m',			   
                                                  'location'   : bottom_location_string,})     

    lev1_slow_atts['gps_qc']             .update({'long_name'  : 'fix quality: 0 = invalid; 1 = gps fix (sps); 2 = dgps fix; 3 = pps fix; 4 = real time kinematic; 5 = float rtk; 6 = estimated (deck reckoning); 7 = manual input mode; 8 = simulation mode.',
                                                  'instrument' : 'Hemisphere V102',
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',
                                                  'height'     : '1m',
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['gps_nsat']           .update({'long_name'  : 'number of satellites available to gps', 
                                                  'instrument' : 'Hemisphere V102',			       
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',		       
                                                  'height'     : '1m',				       
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['gps_hdop']           .update({'long_name'  : 'horizontal dilution of precision', 
                                                  'instrument' : 'Hemisphere V102',			  
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',		  
                                                  'height'     : '1m',				  
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['PTemp']              .update({'long_name'  : 'CR1000X Panel Temp (box internal temp) in C*10',
                                                  'instrument' : 'Campbell CR1000X',
                                                  'methods'    : '',
                                                  'height'     : '0m',			                       
                                                  'location'   : bottom_location_string,})               


    lev1_slow_atts['batt_volt']          .update({'long_name'  : 'logger internal battery voltage', 
                                                  'instrument' : 'Campbell CR1000X',                     
                                                  'methods'    : '',                                     
                                                  'height'     : '0m',			                       
                                                  'location'   : bottom_location_string,})               


    lev1_slow_atts['call_time_mainscan'] .update({'long_name'  : 'tower data logger maintain scan time duration', 
                                                  'instrument' : 'Campbell CR1000X',                     
                                                  'methods'    : '',                                     
                                                  'height'     : '0m',			                       
                                                  'location'   : bottom_location_string,})               


    lev1_slow_atts['apogee_body_T']      .update({'long_name'  : 'instrument body temperature',   
                                                  'instrument' : 'Apogee SI-4H1-SS IRT',	       
                                                  'methods'    : 'digitally polled from instument',
                                                  'height'     : '2m',			       
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['apogee_targ_T']      .update({'long_name'  : 'Apogee IRT target 8-14 micron brightness temperature.',
                                                  'instrument' : 'Apogee SI-4H1-SS IRT',
                                                  'methods'    : 'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                  'height'     : 'surface',
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['sr50_dist']          .update({'long_name'  : 'distance to surface from SR50; temperature compensation correction applied',
                                                  'instrument' : 'Campbell Scientific SR50A',
                                                  'methods'    : 'unheated, temperature correction applied',
                                                  'height'     : '1.75m',
                                                  'location'   : bottom_location_string,})


    lev1_slow_atts['vaisala_RH_2m']      .update({'long_name'  : 'relative humidity wrt water',   
                                                  'instrument' : 'Vaisala PTU300',		       
                                                  'methods'    : 'digitally polled from instument',
                                                  'height'     : '2m',			       
                                                  'location'   : bottom_location_string,})         

    lev1_slow_atts['vaisala_T_2m']       .update({'long_name'  : 'temperature',		       
                                                  'instrument' : 'Vaisala HMT330',		       
                                                  'methods'    : 'digitally polled from instument',
                                                  'height'     : '',			       
                                                  'location'   : bottom_location_string,})         

    lev1_slow_atts['vaisala_Td_2m']      .update({'long_name'  : 'dewpoint',		       
                                                  'instrument' : 'Vaisala PTU300',		       
                                                  'methods'    : 'digitally polled from instument',
                                                  'height'     : '2m',			       
                                                  'location'   : bottom_location_string,})         

    lev1_slow_atts['vaisala_P_2m']       .update({'long_name'  : 'air pressure at 2m',	       
                                                  'instrument' : 'Vaisala PTU 300',		       
                                                  'methods'    : 'digitally polled from instument',
                                                  'height'     : '2m',			       
                                                  'location'   : mast_location_string,})           

    lev1_slow_atts['vaisala_RH_6m']      .update({'long_name'  : 'relative humidity wrt water',   
                                                  'instrument' : 'Vaisala HMT330',		       
                                                  'methods'    : 'digitally polled from instument',
                                                  'height'     : '6m',			       
                                                  'location'   : middle_location_string,})         

    lev1_slow_atts['vaisala_T_6m']       .update({'long_name'  : 'temperature',				
                                                  'instrument' : 'Vaisala HMT330',				
                                                  'methods'    : 'digitally polled from instument',		
                                                  'height'     : '',					
                                                  'location'   : middle_location_string,})                  

    lev1_slow_atts['vaisala_Td_6m']      .update({'long_name'  : 'dewpoint',				
                                                  'instrument' : 'Vaisala HMT330',				
                                                  'methods'    : 'digitally polled from instument',		
                                                  'height'     : '6m',					
                                                  'location'   : middle_location_string,})                  

    lev1_slow_atts['vaisala_RH_10m']     .update({'long_name'  : 'relative humidity wrt water',	     
                                                  'instrument' : 'Vaisala HMT330',			     
                                                  'methods'    : 'digitally polled from instument',	     
                                                  'height'     : '10m',				     
                                                  'location'   : top_location_string,})                  

    lev1_slow_atts['vaisala_T_10m']      .update({'long_name'  : 'temperature',			     
                                                  'instrument' : 'Vaisala HMT330',			     
                                                  'methods'    : 'digitally polled from instument',	     
                                                  'height'     : '',				     
                                                  'location'   : top_location_string,})                  

    lev1_slow_atts['vaisala_Td_10m']     .update({'long_name'  : 'dewpoint',			     
                                                  'instrument' : 'Vaisala HMT330',			     
                                                  'methods'    : 'digitally polled from instument',	     
                                                  'height'     : '10m',				     
                                                  'location'   : top_location_string,})                  

    lev1_slow_atts['fp_A_mV']            .update({'long_name'  : 'voltage from Hukseflux plate A',	
                                                  'instrument' : 'Hukseflux HFP01',			
                                                  'methods'    : 'analog voltage read by CR1000X',	
                                                  'height'     : '',				
                                                  'location'   : '10m south of tower at met city',})

    lev1_slow_atts['fp_A_Wm2']           .update({'long_name'  : 'conductive flux from plate A',	   
                                                  'instrument' : 'Hukseflux HFP01',			   
                                                  'methods'    : 'Sensitivity 63.00/1000 [mV/(W/m2)]', 
                                                  'height'     : '',				   
                                                  'location'   : '10m south of tower at met city',})   

    lev1_slow_atts['fp_B_mV']            .update({'long_name'  : 'voltage from Hukseflux plate B',	     
                                                  'instrument' : 'Hukseflux HFP01',			     
                                                  'methods'    : 'analog voltage read by CR1000X',	     
                                                  'height'     : '',				     
                                                  'location'   : 'under Apogee and SR50 at tower base',})

    lev1_slow_atts['fp_B_Wm2']           .update({'long_name'  : 'conductive flux from plate B',	     
                                                  'instrument' : 'Hukseflux HFP01',			     
                                                  'methods'    : 'Sensitivity 63.91/1000 [mV/(W/m2)]',   
                                                  'height'     : '',				     
                                                  'location'   : 'under Apogee and SR50 at tower base',})

    lev1_slow_atts['mast_T']             .update({'long_name'  : 'temperature',			      
                                                  'instrument' : 'Vaisala WXT530',			      
                                                  'methods'    : 'digitally polled from instument',	      
                                                  'height'     : '',				      
                                                  'location'   : mast_location_string,})                  

    lev1_slow_atts['mast_RH']            .update({'long_name'  : 'relative humidity wrt water',	      
                                                  'instrument' : 'Vaisala WXT530',			      
                                                  'methods'    : 'digitally polled from instument',	      
                                                  'height'     : 'variable 23-30m',			      
                                                  'location'   : mast_location_string,})                  

    lev1_slow_atts['mast_P']             .update({'long_name'  : 'air pressure',				
                                                  'instrument' : 'Vaisala WXT530',				
                                                  'methods'    : 'digitally polled from instument',		
                                                  'height'     : 'variable 23-30m',				
                                                  'location'   : mast_location_string,})

    lev1_slow_atts['licor_ball_mV']      .update({'long_name'  : 'licor heating mv',
                                                  'instrument' : '',
                                                  'methods'    : 'digitally polled from instument',		
                                                  'height'     : '',				
                                                  'location'   : licor_location,})

    # noodleville stuff
    lev1_slow_atts['mast_RECORD']             .update({'long_name'  : 'record number from tower data logger',
                                                       'instrument' : 'Campbell CR1000X',                     
                                                       'methods'    : '',
                                                       'height'     : '0m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lat_deg_Avg']    .update({'long_name'  : 'latitude from gps at noodleville',  
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lat_min_Avg']    .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lon_deg_Avg']    .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lon_min_Avg']    .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_hdg_Avg']        .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_alt_Avg']        .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_qc']             .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_hdop_Avg']       .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_nsat_Avg']       .update({'long_name'  : 'licor heating mv',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '1m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_PTemp']              .update({'long_name'  : 'CR1000X Panel Temp (box internal temp) in C*10',
                                                       'instrument' : 'Campbell CR1000X',
                                                       'methods'    : '',
                                                       'height'     : '0m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_batt_volt']          .update({'long_name'  : 'logger internal battery voltage', 
                                                       'instrument' : 'Campbell CR1000X',           
                                                       'methods'    : '',                           
                                                       'height'     : '0m',			    
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_call_time_mainscan'] .update({'long_name'  : 'noodleville data logger maintain scan time duration', 
                                                       'instrument' : 'Campbell CR1000X',                     
                                                       'methods'    : '',                                     
                                                       'height'     : '0m',			                       
                                                       'location'   : noodleville_location_string,})


    return lev1_slow_atts, list(lev1_slow_atts.keys()).copy() 

# because I decided to include all of the fast instruments in groups inside of one netcdf file, the variable names
# for the fast level1 data are much more integral to the level1/level2 processing code. so. if you decide you want these
# names to be different, you're going to have to change the "get_fast" functions in the "create" code as well as some
# of the processing code in the level2 create file. it's annoying, maybe not the best design choice.
def define_level1_fast():

    licor_location         = 'first level on met city tower'
    bottom_location_string = 'first level on met city tower'
    middle_location_string = 'second level on met city tower'
    top_location_string    = 'third level on met city tower'
    mast_location_string   = 'top of radio mast at met city'
    
    lev1_fast_atts = OrderedDict()

    # if you change the names here, you're going to have to change the write_level1_fast function
    # in the create product code. annoying, sorry. hopefully when I finish this I'll redesign a bit more logically

    # units defined here, other properties defined in 'update' call below
    lev1_fast_atts['metek_2m_TIMESTAMP']   = {'units' : 'time'    }
    lev1_fast_atts['metek_2m_heatstatus']  = {'units' : 'int'     }
    lev1_fast_atts['metek_2m_x']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_2m_y']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_2m_z']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_2m_T']           = {'units' : 'C'       }
    lev1_fast_atts['metek_2m_hspd']        = {'units' : 'int'     }
    lev1_fast_atts['metek_2m_ts']          = {'units' : 'int'     }
    lev1_fast_atts['metek_2m_incx']        = {'units' : 'deg'     }
    lev1_fast_atts['metek_2m_incy']        = {'units' : 'deg'     }

    lev1_fast_atts['metek_6m_TIMESTAMP']   = {'units' : 'time'    }
    lev1_fast_atts['metek_6m_heatstatus']  = {'units' : 'int'     }
    lev1_fast_atts['metek_6m_x']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_y']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_z']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_T']           = {'units' : 'C'       }
    lev1_fast_atts['metek_6m_hspd']        = {'units' : 'int'     }
    lev1_fast_atts['metek_6m_ts']          = {'units' : 'int'     }
    lev1_fast_atts['metek_6m_incx']        = {'units' : 'deg'     }
    lev1_fast_atts['metek_6m_incy']        = {'units' : 'deg'     }

    lev1_fast_atts['metek_10m_TIMESTAMP']  = {'units' : 'time'    }
    lev1_fast_atts['metek_10m_heatstatus'] = {'units' : 'int'     }
    lev1_fast_atts['metek_10m_x']          = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_y']          = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_z']          = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_T']          = {'units' : 'C'       }
    lev1_fast_atts['metek_10m_hspd']       = {'units' : 'int'     }
    lev1_fast_atts['metek_10m_ts']         = {'units' : 'int'     }
    lev1_fast_atts['metek_10m_incx']       = {'units' : 'deg'     }
    lev1_fast_atts['metek_10m_incy']       = {'units' : 'deg'     }
 
    lev1_fast_atts['metek_mast_TIMESTAMP'] = {'units' : 'time'    }
    lev1_fast_atts['metek_mast_x']         = {'units' : 'm/s'     }
    lev1_fast_atts['metek_mast_y']         = {'units' : 'm/s'     }
    lev1_fast_atts['metek_mast_z']         = {'units' : 'm/s'     }
    lev1_fast_atts['metek_mast_T']         = {'units' : 'C'       }

    lev1_fast_atts['licor_TIMESTAMP']      = {'units' : 'g/kg'    }
    lev1_fast_atts['licor_diag']           = {'units' : 'int'     }
    lev1_fast_atts['licor_co2']            = {'units' : 'g/kg'    }
    lev1_fast_atts['licor_h2o']            = {'units' : 'g/kg'    }
    lev1_fast_atts['licor_T']              = {'units' : 'deg C'   }
    lev1_fast_atts['licor_pr']             = {'units' : 'hPa'     }
    lev1_fast_atts['licor_co2_str']        = {'units' : 'percent' }
    lev1_fast_atts['licor_pll']            = {'units' : 'boolean' }
    lev1_fast_atts['licor_dt']             = {'units' : 'boolean' }
    lev1_fast_atts['licor_ct']             = {'units' : 'boolean' }

    lev1_fast_atts['metek_2m_TIMESTAMP']   .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,}) 

    lev1_fast_atts['metek_2m_x']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_y']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_z']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_T']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_heatstatus']  .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_hspd']        .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_ts']          .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_incx']        .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev1_fast_atts['metek_2m_incy']        .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})


    lev1_fast_atts['metek_6m_TIMESTAMP']   .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,}) 

    lev1_fast_atts['metek_6m_x']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_y']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_z']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_T']           .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_heatstatus']  .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_hspd']        .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_ts']          .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_incx']        .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev1_fast_atts['metek_6m_incy']        .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})


    lev1_fast_atts['metek_10m_TIMESTAMP']  .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,}) 

    lev1_fast_atts['metek_10m_x']          .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_y']          .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_z']          .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_T']          .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_heatstatus'] .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_hspd']       .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_ts']         .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_incx']       .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_10m_incy']       .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev1_fast_atts['metek_mast_TIMESTAMP'] .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : 'mast',
                                                    'location'      : mast_location_string,}) 

    lev1_fast_atts['metek_mast_x']         .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : 'mast',
                                                    'location'      : mast_location_string,})

    lev1_fast_atts['metek_mast_y']         .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : 'mast',
                                                    'location'      : mast_location_string,})

    lev1_fast_atts['metek_mast_z']         .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : 'mast',
                                                    'location'      : mast_location_string,})

    lev1_fast_atts['metek_mast_T']         .update({'long_name'     : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : '',
                                                    'height'        : 'mast',
                                                    'location'      : mast_location_string,})


    lev1_fast_atts['licor_diag']           .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    lev1_fast_atts['licor_co2']            .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    lev1_fast_atts['licor_h2o']            .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    
    lev1_fast_atts['licor_pr']             .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    lev1_fast_atts['licor_T']             .update({'long_name'     : '',
                                                   'instrument'    : 'Licor 7500-DS',
                                                   'methods'       : '',
                                                   'height'        : '2m',
                                                   'location'      : licor_location,})

    lev1_fast_atts['licor_co2_str']        .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    lev1_fast_atts['licor_pll']        .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    lev1_fast_atts['licor_dt']        .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    lev1_fast_atts['licor_ct']        .update({'long_name'     : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : '',
                                                    'height'        : '2m',
                                                    'location'      : licor_location,})

    return lev1_fast_atts, list(lev1_fast_atts.keys()).copy() 

def define_level2_variables():  

    licor_location = 'first level on met city tower'
    bottom_location_string = 'first level on met city tower'
    middle_location_string = 'second level on met city tower'
    top_location_string    = 'third level on met city tower'
    mast_location_string   = 'top of radio mast at met city'

    lev2_atts = OrderedDict()

    lev2_atts['tower_lat']                 = {'units'         : 'degrees_north'}
    lev2_atts['tower_lon']                 = {'units'         : 'degrees_east'}
    lev2_atts['tower_heading']             = {'units'         : 'degrees_true'}
    lev2_atts['gps_alt']                   = {'units'         : 'meters'}
    lev2_atts['gps_qc']                    = {'units'         : 'code'}
    lev2_atts['gps_nsat']                  = {'units'         : 'counts'}
    lev2_atts['gps_hdop']                  = {'units'         : 'unitless'}
    lev2_atts['logger_scantime']           = {'units'         : 'milliseconds'}
    lev2_atts['sr50_dist']                 = {'units'         : 'meters'}
    lev2_atts['temp_vaisala_2m']           = {'units'         : 'deg C'}
    lev2_atts['temp_vaisala_6m']           = {'units'         : 'deg C'}
    lev2_atts['temp_vaisala_10m']          = {'units'         : 'deg C'}
    lev2_atts['temp_vaisala_mast']         = {'units'         : 'deg C'}
    lev2_atts['dewpoint_vaisala_2m']       = {'units'         : 'deg C'}
    lev2_atts['dewpoint_vaisala_6m']       = {'units'         : 'deg C'}
    lev2_atts['dewpoint_vaisala_10m']      = {'units'         : 'deg C'}
    lev2_atts['dewpoint_vaisala_mast']     = {'units'         : 'deg C'}
    lev2_atts['rel_humidity_vaisala_2m']   = {'units'         : 'percent'}
    lev2_atts['rel_humidity_vaisala_6m']   = {'units'         : 'percent'}
    lev2_atts['rel_humidity_vaisala_10m']  = {'units'         : 'percent'}
    lev2_atts['rel_humidity_vaisala_mast'] = {'units'         : 'percent'}
    lev2_atts['pressure_vaisala_2m']       = {'units'         : 'hPa'}
    lev2_atts['mast_pressure']             = {'units'         : 'hPa'}
    lev2_atts['body_T_IRT']                = {'units'         : 'deg C'}
    lev2_atts['surface_T_IRT']             = {'units'         : 'deg C'}
    lev2_atts['flux_plate_A_mv']           = {'units'         : 'mv'}
    lev2_atts['flux_plate_B_mv']           = {'units'         : 'mv'}
    lev2_atts['flux_plate_A_Wm2']          = {'units'         : 'Wm2'}
    lev2_atts['flux_plate_B_Wm2']          = {'units'         : 'Wm2'}
    lev2_atts['snow_depth']                = {'units'         : 'cm'}
    lev2_atts['MR_vaisala_2m']             = {'units'         : 'g/kg'}
    lev2_atts['MR_vaisala_6m']             = {'units'         : 'g/kg'}
    lev2_atts['MR_vaisala_10m']            = {'units'         : 'g/kg'}
    lev2_atts['MR_vaisala_mast']           = {'units'         : 'g/kg'}
    lev2_atts['RHi_vaisala_2m']            = {'units'         : 'percent'}
    lev2_atts['RHi_vaisala_6m']            = {'units'         : 'percent'}
    lev2_atts['RHi_vaisala_10m']           = {'units'         : 'percent'}
    lev2_atts['RHi_vaisala_mast']          = {'units'         : 'percent'}
    lev2_atts['pw_vaisala_2m']             = {'units'         : 'Pa'}
    lev2_atts['pw_vaisala_6m']             = {'units'         : 'Pa'}
    lev2_atts['pw_vaisala_10m']            = {'units'         : 'Pa'}
    lev2_atts['pw_vaisala_mast']           = {'units'         : 'Pa'}
    lev2_atts['wind_speed_metek_2m']       = {'units'         : 'm/s'}
    lev2_atts['wind_speed_metek_6m']       = {'units'         : 'm/s'}
    lev2_atts['wind_speed_metek_10m']      = {'units'         : 'm/s'}
    lev2_atts['wind_speed_metek_mast']     = {'units'         : 'm/s'}
    lev2_atts['wind_direction_metek_2m']   = {'units'         : 'deg true'}
    lev2_atts['wind_direction_metek_6m']   = {'units'         : 'deg true'}
    lev2_atts['wind_direction_metek_10m']  = {'units'         : 'deg true'}
    lev2_atts['wind_direction_metek_mast'] = {'units'         : 'deg true'}
    lev2_atts['temp_variance_metek_2m']    = {'units'         : '(deg C)^2'}
    lev2_atts['temp_variance_metek_6m']    = {'units'         : '(deg C)^2'}
    lev2_atts['temp_variance_metek_10m']   = {'units'         : '(deg C)^2'}
    lev2_atts['temp_variance_metek_mast']  = {'units'         : '(deg C)^2'}
    lev2_atts['H2O_licor']                 = {'units'         : 'g/kg'}
    lev2_atts['CO2_licor']                 = {'units'         : 'g/kg'}
    lev2_atts['temp_licor']                = {'units'         : 'deg C'}
    lev2_atts['pr_licor']                  = {'units'         : 'hPa'}
    lev2_atts['u_metek_2m']                = {'units'         : 'm/s'}
    lev2_atts['u_metek_6m']                = {'units'         : 'm/s'}
    lev2_atts['u_metek_10m']               = {'units'         : 'm/s'}
    lev2_atts['u_metek_mast']              = {'units'         : 'm/s'}
    lev2_atts['v_metek_2m']                = {'units'         : 'm/s'}
    lev2_atts['v_metek_6m']                = {'units'         : 'm/s'}
    lev2_atts['v_metek_10m']               = {'units'         : 'm/s'}
    lev2_atts['v_metek_mast']              = {'units'         : 'm/s'}
    lev2_atts['w_metek_2m']                = {'units'         : 'm/s'}
    lev2_atts['w_metek_6m']                = {'units'         : 'm/s'}
    lev2_atts['w_metek_10m']               = {'units'         : 'm/s'}
    lev2_atts['w_metek_mast']              = {'units'         : 'm/s'}
    lev2_atts['temp_metek_2m']             = {'units'         : 'deg C'}
    lev2_atts['temp_metek_6m']             = {'units'         : 'deg C'}
    lev2_atts['temp_metek_10m']            = {'units'         : 'deg C'}
    lev2_atts['temp_metek_mast']           = {'units'         : 'deg C'}
    lev2_atts['stddev_u_metek_2m']         = {'units'         : 'm/s'}
    lev2_atts['stddev_v_metek_2m']         = {'units'         : 'm/s'}
    lev2_atts['stddev_w_metek_2m']         = {'units'         : 'm/s'}
    lev2_atts['stddev_T_metek_2m']         = {'units'         : 'deg C'}
    lev2_atts['stddev_u_metek_6m']         = {'units'         : 'm/s'}
    lev2_atts['stddev_v_metek_6m']         = {'units'         : 'm/s'}
    lev2_atts['stddev_w_metek_6m']         = {'units'         : 'm/s'}
    lev2_atts['stddev_T_metek_6m']         = {'units'         : 'deg C'}
    lev2_atts['stddev_u_metek_10m']        = {'units'         : 'm/s'}
    lev2_atts['stddev_v_metek_10m']        = {'units'         : 'm/s'}
    lev2_atts['stddev_w_metek_10m']        = {'units'         : 'm/s'}
    lev2_atts['stddev_T_metek_10m']        = {'units'         : 'deg C'}
    lev2_atts['stddev_u_metek_mast']       = {'units'         : 'm/s'}
    lev2_atts['stddev_v_metek_mast']       = {'units'         : 'm/s'}
    lev2_atts['stddev_w_metek_mast']       = {'units'         : 'm/s'}
    lev2_atts['stddev_T_metek_mast']       = {'units'         : 'deg C'}
    lev2_atts['co2_signal_licor']          = {'units'         : 'percent'}

    # lev2_atts['good_u_2m']                 = {'units'         : 'counts'}
    # lev2_atts['good_v_2m']                 = {'units'         : 'counts'}
    # lev2_atts['good_w_2m']                 = {'units'         : 'counts'}
    # lev2_atts['good_T_2m']                 = {'units'         : 'counts'}
    # lev2_atts['good_u_6m']                 = {'units'         : 'counts'}
    # lev2_atts['good_v_6m']                 = {'units'         : 'counts'}
    # lev2_atts['good_w_6m']                 = {'units'         : 'counts'}
    # lev2_atts['good_T_6m']                 = {'units'         : 'counts'}
    # lev2_atts['good_u_10m']                = {'units'         : 'counts'}
    # lev2_atts['good_v_10m']                = {'units'         : 'counts'}
    # lev2_atts['good_w_10m']                = {'units'         : 'counts'}
    # lev2_atts['good_T_10m']                = {'units'         : 'counts'}
    # lev2_atts['good_u_mast']               = {'units'         : 'counts'}
    # lev2_atts['good_v_mast']               = {'units'         : 'counts'}
    # lev2_atts['good_w_mast']               = {'units'         : 'counts'}
    # lev2_atts['good_T_mast']               = {'units'         : 'counts'}


    # add the other important things to the data variable NetCDF attributes
    # #########################################################################################################
    lev2_atts['tower_lat']                 .update({'long_name'     : 'latitude from gps at tower',
                                                    'cf_name'       : 'latitude',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['tower_lon']                 .update({'long_name'     :'longitude from gps at tower',
                                                    'cf_name'       :'longitude',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : '$GPRMC, $GPGGA, GPGZDA',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['tower_heading']             .update({'long_name'     : 'heading from gps at tower',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : '$HEHDT',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['gps_alt']                   .update({'long_name'     : 'altitude from gps at tower',
                                                    'cf_name'       : 'altitude',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['gps_qc']                    .update({'long_name'     : 'fix quality: 0 = invalid; 1 = gps fix (sps); 2 = dgps fix; 3 = pps fix; 4 = real time kinematic; 5 = float rtk; 6 = estimated (deck reckoning); 7 = manual input mode; 8 = simulation mode.',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['gps_nsat']                  .update({'long_name'     : 'number of satellites available to gps',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['gps_hdop']                  .update({'long_name'     : 'horizontal dilution of precision',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hemisphere V102',
                                                    'methods'       : 'GPRMC, GPGGA, GPGZDA',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['logger_scantime']           .update({'long_name'     : 'time taken for logger to complete scan',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Campbell Scientific CR1000X',
                                                    'methods'       : '',
                                                    'height'        : 'N/A',
                                                    'location'      : bottom_location_string,})

    lev2_atts['sr50_dist']                 .update({'long_name'     : 'distance to surface from SR50; temperature compensation correction applied',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Campbell Scientific SR50A',
                                                    'methods'       : 'unheated, temperature correction applied',
                                                    'height'        : '1.75m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['temp_vaisala_2m']           .update({'long_name'     : 'temperature',
                                                    'cf_name'       : 'air_temperature',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['temp_vaisala_6m']           .update({'long_name'     : 'temperature',
                                                    'cf_name'       : 'air_temperature',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['temp_vaisala_10m']          .update({'long_name'     : 'temperature',
                                                    'cf_name'       : 'air_emperature',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['temp_vaisala_mast']         .update({'long_name'     : 'temperature',
                                                    'cf_name'       : 'air_temperature',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['dewpoint_vaisala_2m']       .update({'long_name'     : 'dewpoint',
                                                    'cf_name'       : 'dew_point_temperature',
                                                    'instrument'    : 'Vaisala PTU300',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['dewpoint_vaisala_6m']       .update({'long_name'     : 'dewpoint',
                                                    'cf_name'       : 'dew_point_temperature',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev2_atts['dewpoint_vaisala_10m']       .update({'long_name'     : 'dewpoint',
                                                     'cf_name'       : 'dew_point_temperature',
                                                     'instrument'    : 'Vaisala HMT330',
                                                     'methods'       : 'digitally polled from instument',
                                                     'height'        : '10m',
                                                     'location'      : top_location_string,})

    lev2_atts['dewpoint_vaisala_mast']     .update({'long_name'     : 'dewpoint',
                                                    'cf_name'       : 'dew_point_temperatre',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '23 or 30m',
                                                    'location'      : mast_location_string,})

    lev2_atts['rel_humidity_vaisala_2m']   .update({'long_name'     : 'relative humidity wrt water',
                                                    'cf_name'       : 'relative_humidity',
                                                    'instrument'    : 'Vaisala PTU300',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['rel_humidity_vaisala_6m']   .update({'long_name'     : 'relative humidity wrt water',
                                                    'cf_name'       : 'relative humidity',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '6m',
                                                    'location'      : middle_location_string,})

    lev2_atts['rel_humidity_vaisala_10m']  .update({'long_name'     : 'relative humidity wrt water',
                                                    'cf_name'       : 'relative humidity',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '10m',
                                                    'location'      : top_location_string,})

    lev2_atts['rel_humidity_vaisala_mast'] .update({'long_name'     : 'relative humidity wrt water',
                                                    'cf_name'       : 'relative humidity',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : 'variable 23-30m',
                                                    'location'      : mast_location_string,})

    lev2_atts['pressure_vaisala_2m']       .update({'long_name'     : 'air pressure at 2m',
                                                    'cf_name'       : 'air_pressure',
                                                    'instrument'    : 'Vaisala PTU 300',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '2m',
                                                    'location'      : mast_location_string,})

    lev2_atts['mast_pressure']             .update({'long_name'     : 'air pressure',
                                                    'cf_name'       : 'air_pressure',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : 'variable 23-30m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['body_T_IRT']                .update({'long_name'     : 'instrument body temperature',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                    'methods'       : 'digitally polled from instument',
                                                    'height'        : '2m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['surface_T_IRT']             .update({'long_name'     : 'Apogee IRT target 8-14 micron brightness temperature.',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Apogee SI-4H1-SS IRT',
                                                    'methods'       : 'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                    'height'        : 'surface',
                                                    'location'      : bottom_location_string,})

    lev2_atts['flux_plate_A_mv']           .update({'long_name'     : 'voltage from Hukseflux plate A',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hukseflux HFP01',
                                                    'methods'       : 'analog voltage read by CR1000X',
                                                    'height'        : '',
                                                    'location'      : '10m south of tower at met city',})

    lev2_atts['flux_plate_B_mv']           .update({'long_name'     : 'voltage from Hukseflux plate B',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hukseflux HFP01',
                                                    'methods'       : 'analog voltage read by CR1000X',
                                                    'height'        : '',
                                                    'location'      : 'under Apogee and SR50 at tower base',})

    lev2_atts['flux_plate_A_Wm2']          .update({'long_name'     : 'conductive flux from plate A',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hukseflux HFP01',
                                                    'methods'       : 'Sensitivity 63.00/1000 [mV/(W/m2)]',
                                                    'height'        : '',
                                                    'location'      : '10m south of tower at met city',})

    lev2_atts['flux_plate_B_Wm2']          .update({'long_name'     : 'conductive flux from plate B',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Hukseflux HFP01',
                                                    'methods'       : 'Sensitivity 63.91/1000 [mV/(W/m2)]',
                                                    'height'        : '',
                                                    'location'      : 'under Apogee and SR50 at tower base',})


    lev2_atts['snow_depth']                .update({'long_name'     : 'snow depth near tower base',
                                                    'cf_name'       : 'surface_snow_thickness',
                                                    'instrument'    : 'Hukseflux HFP01',
                                                    'methods'       : 'derived snow depth from temperature-corrected SR50 distance values based on initialization 10/27/19. footprint nominally 0.47 m radius.',
                                                    'height'        : 'N/A',
                                                    'location'      : 'at base of tower under SR50',})

    lev2_atts['MR_vaisala_2m']             .update({'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                    'cf_name'       : 'specific_humidity',
                                                    'instrument'    : 'Vaisala PTU300',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['MR_vaisala_6m']             .update({'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                    'cf_name'       : 'specific_humidity',
                                                    'instrument'    : 'Vaisala PTU300',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['MR_vaisala_10m']            .update({'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                    'cf_name'       : 'specific_humidity',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['MR_vaisala_mast']           .update({'long_name'     : 'mixing ratio derived using T/P/RH from HMT',
                                                    'cf_name'       : 'specific_humidity',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['RHi_vaisala_2m']            .update({'long_name'     : 'ice RH derived using T/P/RH',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala PTU300',
                                                    'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['RHi_vaisala_6m']            .update({'long_name'     : 'ice RH derived using T/P/RH',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['RHi_vaisala_10m']           .update({'long_name'     : 'ice RH derived using T/P/RH',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['RHi_vaisala_mast']          .update({'long_name'     : 'ice RH derived using T/P/RH',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'calculated from measured variables following Hyland & Wexler (1983)',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['pw_vaisala_2m']             .update({'long_name'     : 'vapor pressure',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala PTU300',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['pw_vaisala_6m']             .update({'long_name'     : 'vapor pressure',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['pw_vaisala_10m']            .update({'long_name'     : 'vapor pressure',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala HMT330',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['pw_vaisala_mast']           .update({'long_name'     : 'vapor pressure',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Vaisala WXT530',
                                                    'methods'       : 'calculated from measured variables following Wexler (1976)',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['wind_speed_metek_2m']       .update({'long_name'     : 'average metek wind speed',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['wind_speed_metek_6m']       .update({'long_name'     : 'average metek wind speed',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['wind_speed_metek_10m']      .update({'long_name'     : 'average metek wind speed',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['wind_speed_metek_mast']     .update({'long_name'     : 'average metek wind speed',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})


    lev2_atts['wind_direction_metek_2m']   .update({'long_name'     : 'average metek wind direction',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['wind_direction_metek_6m']   .update({'long_name'     : 'average metek wind direction',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['wind_direction_metek_10m']  .update({'long_name'     : 'average metek wind direction',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['wind_direction_metek_mast'] .update({'long_name'     : 'average metek wind direction',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'derived from hozirontal wind components after coordinate transformation from body to earth reference frame',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})


    lev2_atts['temp_variance_metek_2m']    .update({'long_name'     : 'metek sonic temperature obs variance',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['temp_variance_metek_6m']    .update({'long_name'     : 'metek sonic temperature obs variance',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['temp_variance_metek_10m']   .update({'long_name'     : 'metek sonic temperature obs variance',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['temp_variance_metek_mast']  .update({'long_name'     : 'metek sonic temperature obs variance',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['H2O_licor']                 .update({'long_name'     : 'Licor water vapor mixing ratio',
                                                    'cf_name'       : 'specific_humidity',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['CO2_licor']                 .update({'long_name'     : 'Licor CO2 mixing ratio',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : 'open-path optical gas analyzer, source data reported at 20 Hz',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['temp_licor']                .update({'long_name'     : 'temperature',
                                                    'cf_name'       : 'air_temperature',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : 'thermistor positioned along strut of open-path optical gas analyzer, source data reported at 20 Hz',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['pr_licor']                  .update({'long_name'     : 'Licor pressure',
                                                    'cf_name'       : 'air_pressure',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : 'pressure sensor located in electronics box. source data reported at 20 Hz',
                                                    'height'        : '1m',
                                                    'location'      : bottom_location_string,})

    lev2_atts['u_metek_2m']                .update({'long_name'     : 'Metek u-component',
                                                    'cf_name'       : 'northward_wind',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['u_metek_6m']                .update({'long_name'     : 'Metek u-component',
                                                    'cf_name'       : 'northward_wind',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['u_metek_10m']               .update({'long_name'     : 'Metek u-component',
                                                    'cf_name'       : 'northward_wind',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['u_metek_mast']              .update({'long_name'     : 'Metek u-component',
                                                    'cf_name'       : 'northward_wind',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})


    lev2_atts['v_metek_2m']                .update({'long_name'     : 'Metek v-component',
                                                    'cf_name'       : 'westward_wind',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['v_metek_6m']                .update({'long_name'     : 'Metek v-component',
                                                    'cf_name'       : 'westward_wind',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['v_metek_10m']               .update({'long_name'     : 'Metek v-component',
                                                    'cf_name'       : 'westward_wind',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['v_metek_mast']              .update({'long_name'     : 'Metek v-component',
                                                    'cf_name'       : 'westward_wind',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})


    lev2_atts['w_metek_2m']                .update({'long_name'     : 'Metek w-component',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['w_metek_6m']                .update({'long_name'     : 'Metek w-component',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['w_metek_10m']               .update({'long_name'     : 'Metek w-component',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['w_metek_mast']              .update({'long_name'     : 'Metek w-component',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['temp_metek_2m']             .update({'long_name'     : 'Metek sonic temperature',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['temp_metek_6m']             .update({'long_name'     : 'Metek sonic temperature',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['temp_metek_10m']            .update({'long_name'     : 'Metek sonic temperature',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['temp_metek_mast']           .update({'long_name'     : 'Metek sonic temperature',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['stddev_u_metek_2m']         .update({'long_name'     : 'u metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['stddev_v_metek_2m']         .update({'long_name'     : 'v metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['stddev_w_metek_2m']         .update({'long_name'     : 'w metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['stddev_T_metek_2m']         .update({'long_name'     : 'T metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})

    lev2_atts['stddev_u_metek_6m']         .update({'long_name'     : 'u metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['stddev_v_metek_6m']         .update({'long_name'     : 'v metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['stddev_w_metek_6m']         .update({'long_name'     : 'w metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['stddev_T_metek_6m']         .update({'long_name'     : 'T metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : middle_location_string,})

    lev2_atts['stddev_u_metek_10m']        .update({'long_name'     : 'u metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'u defined positive north in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['stddev_v_metek_10m']        .update({'long_name'     : 'v metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['stddev_w_metek_10m']        .update({'long_name'     : 'w metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['stddev_T_metek_10m']        .update({'long_name'     : 'T metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : top_location_string,})

    lev2_atts['stddev_u_metek_mast']       .update({'long_name'     : 'u metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['stddev_v_metek_mast']       .update({'long_name'     : 'v metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'v defined positive west in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['stddev_w_metek_mast']       .update({'long_name'     : 'w metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'w defined positive up in right-hand coordinate system',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['stddev_T_metek_mast']       .update({'long_name'     : 'T metek obs standard deviation',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Metek USA-1 sonic anemometer',
                                                    'methods'       : 'this is an acoustic temperature, not a thermodynamic temperature',
                                                    'height'        : '',
                                                    'location'      : mast_location_string,})

    lev2_atts['co2_signal_licor']          .update({'long_name'     : 'Licor CO2 signal strength diagnostic',
                                                    'cf_name'       : '',
                                                    'instrument'    : 'Licor 7500-DS',
                                                    'methods'       : 'signal strength [0-100%] is a measure of attenuation of the optics (e.g., by salt residue or ice) that applies to both co2 and h2o observations',
                                                    'height'        : '',
                                                    'location'      : bottom_location_string,})


    # lev2_atts['good_u_2m']                 .update({
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # lev2_atts['good_v_2m']                 .update({
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # lev2_atts['good_w_2m']                 .update({
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # lev2_atts['good_T_2m']                 .update({
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'height'        : '',
    #                                                'location'      : bottom_location_string,})
    #
    # lev2_atts['good_u_6m']                 .update({
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # lev2_atts['good_v_6m']                 .update({
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # lev2_atts['good_w_6m']                 .update({
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # lev2_atts['good_T_6m']                 .update({
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'height'        : '',
    #                                                'location'      : middle_location_string,})
    #
    # lev2_atts['good_u_10m']                .update({
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # lev2_atts['good_v_10m']                .update({
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # lev2_atts['good_w_10m']                .update({
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # lev2_atts['good_T_10m']                .update({
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'height'        : '',
    #                                                'location'      : top_location_string,})
    #
    # lev2_atts['good_u_mast']               .update({
    #                                                'long_name'     : '# of good values for Metek u-component',
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})
    #
    # lev2_atts['good_v_mast']               .update({
    #                                                'long_name'     : '# of good values for Metek v-component',
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})
    #
    # lev2_atts['good_w_mast']               .update({
    #                                                'long_name'     : '# of good values for Metek w-component',
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})
    #
    # lev2_atts['good_T_mast']               .update({
    #                                                'long_name'     : '# of good values for Metek temperatures',
    #                                                'height'        : '',
    #                                                'location'      : mast_location_string,})


    return lev2_atts, list(lev2_atts.keys()).copy() 

def define_turb_variables():

    licor_location = 'first level on met city tower'
    bottom_location_string = 'first level on met city tower'
    middle_location_string = 'second level on met city tower'
    top_location_string    = 'third level on met city tower'
    mast_location_string   = 'top of radio mast at met city'

    turb_atts = OrderedDict()

    turb_atts['Hs_2m']                     = {'units'         : 'Wm2'}
    turb_atts['Hs_6m']                     = {'units'         : 'Wm2'}
    turb_atts['Hs_10m']                    = {'units'         : 'Wm2'}
    turb_atts['Hs_mast']                   = {'units'         : 'Wm2'}
    turb_atts['Hs_hi_2m']                  = {'units'         : 'Wm2'}
    turb_atts['Hs_hi_6m']                  = {'units'         : 'Wm2'}
    turb_atts['Hs_hi_10m']                 = {'units'         : 'Wm2'}
    turb_atts['Hs_hi_mast']                = {'units'         : 'Wm2'}
    turb_atts['Cd_2m']                     = {'units'         : 'dimensionless'}
    turb_atts['Cd_6m']                     = {'units'         : 'dimensionless'}
    turb_atts['Cd_10m']                    = {'units'         : 'dimensionless'}
    turb_atts['Cd_mast']                   = {'units'         : 'dimensionless'}
    turb_atts['Cd_hi_2m']                  = {'units'         : 'dimensionless'}
    turb_atts['Cd_hi_6m']                  = {'units'         : 'dimensionless'}
    turb_atts['Cd_hi_10m']                 = {'units'         : 'dimensionless'}
    turb_atts['Cd_hi_mast']                = {'units'         : 'dimensionless'}
    turb_atts['ustar_2m']                  = {'units'         : 'm/s'}
    turb_atts['ustar_6m']                  = {'units'         : 'm/s'}
    turb_atts['ustar_10m']                 = {'units'         : 'm/s'}
    turb_atts['ustar_mast']                = {'units'         : 'm/s'}
    turb_atts['ustar_hi_2m']               = {'units'         : 'm/s'}
    turb_atts['ustar_hi_6m']               = {'units'         : 'm/s'}
    turb_atts['ustar_hi_10m']              = {'units'         : 'm/s'}
    turb_atts['ustar_hi_mast']             = {'units'         : 'm/s'}
    turb_atts['Tstar_2m']                  = {'units'         : 'degC'}
    turb_atts['Tstar_6m']                  = {'units'         : 'degC'}
    turb_atts['Tstar_10m']                 = {'units'         : 'degC'}
    turb_atts['Tstar_mast']                = {'units'         : 'degC'}
    turb_atts['Tstar_hi_2m']               = {'units'         : 'degC'}
    turb_atts['Tstar_hi_6m']               = {'units'         : 'degC'}
    turb_atts['Tstar_hi_10m']              = {'units'         : 'degC'}
    turb_atts['Tstar_hi_mast']             = {'units'         : 'degC'}
    turb_atts['zeta_level_n_2m']           = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_6m']           = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_10m']          = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_mast']         = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_hi_2m']        = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_hi_6m']        = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_hi_10m']       = {'units'         : 'dimensionless'}
    turb_atts['zeta_level_n_hi_mast']      = {'units'         : 'dimensionless'}
    turb_atts['wu_csp_2m']                 = {'units'         : 'm^2/s^2'}
    turb_atts['wu_csp_6m']                 = {'units'         : 'm^2/s^2'}
    turb_atts['wu_csp_10m']                = {'units'         : 'm^2/s^2'}
    turb_atts['wu_csp_mast']               = {'units'         : 'm^2/s^2'}
    turb_atts['wv_csp_2m']                 = {'units'         : 'm^2/s^2'}
    turb_atts['wv_csp_6m']                 = {'units'         : 'm^2/s^2'}
    turb_atts['wv_csp_10m']                = {'units'         : 'm^2/s^2'}
    turb_atts['wv_csp_mast']               = {'units'         : 'm^2/s^2'}
    turb_atts['uv_csp_2m']                 = {'units'         : 'm^2/s^2'}
    turb_atts['uv_csp_6m']                 = {'units'         : 'm^2/s^2'}
    turb_atts['uv_csp_10m']                = {'units'         : 'm^2/s^2'}
    turb_atts['uv_csp_mast']               = {'units'         : 'm^2/s^2'}
    turb_atts['wT_csp_2m']                 = {'units'         : 'degC m/s'}
    turb_atts['wT_csp_6m']                 = {'units'         : 'degC m/s'}
    turb_atts['wT_csp_10m']                = {'units'         : 'degC m/s'}
    turb_atts['wT_csp_mast']               = {'units'         : 'degC m/s'}
    turb_atts['uT_csp_2m']                 = {'units'         : 'degC m/s'}
    turb_atts['uT_csp_6m']                 = {'units'         : 'degC m/s'}
    turb_atts['uT_csp_10m']                = {'units'         : 'degC m/s'}
    turb_atts['uT_csp_mast']               = {'units'         : 'degC m/s'}
    turb_atts['vT_csp_2m']                 = {'units'         : 'degC m/s'}
    turb_atts['vT_csp_6m']                 = {'units'         : 'degC m/s'}
    turb_atts['vT_csp_10m']                = {'units'         : 'degC m/s'}
    turb_atts['vT_csp_mast']               = {'units'         : 'degC m/s'}
    turb_atts['phi_u_2m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_u_6m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_u_10m']                = {'units'          : 'dimensionless'}
    turb_atts['phi_u_mast']               = {'units'          : 'dimensionless'}
    turb_atts['phi_v_2m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_v_6m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_v_10m']                = {'units'          : 'dimensionless'}
    turb_atts['phi_v_mast']               = {'units'          : 'dimensionless'}
    turb_atts['phi_w_2m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_w_6m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_w_10m']                = {'units'          : 'dimensionless'}
    turb_atts['phi_w_mast']               = {'units'          : 'dimensionless'}
    turb_atts['phi_T_2m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_T_6m']                 = {'units'          : 'dimensionless'}
    turb_atts['phi_T_10m']                = {'units'          : 'dimensionless'}
    turb_atts['phi_T_mast']               = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_2m']                = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_6m']                = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_10m']               = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_mast']              = {'units'          : 'dimensionless'}
    turb_atts['phi_u_hi_2m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_u_hi_6m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_u_hi_10m']             = {'units'          : 'dimensionless'}
    turb_atts['phi_u_hi_mast']            = {'units'          : 'dimensionless'}
    turb_atts['phi_v_hi_2m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_v_hi_6m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_v_hi_10m']             = {'units'          : 'dimensionless'}
    turb_atts['phi_v_hi_mast']            = {'units'          : 'dimensionless'}
    turb_atts['phi_w_hi_2m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_w_hi_6m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_w_hi_10m']             = {'units'          : 'dimensionless'}
    turb_atts['phi_w_hi_mast']            = {'units'          : 'dimensionless'}
    turb_atts['phi_T_hi_2m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_T_hi_6m']              = {'units'          : 'dimensionless'}
    turb_atts['phi_T_hi_10m']             = {'units'          : 'dimensionless'}
    turb_atts['phi_T_hi_mast']            = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_hi_2m']             = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_hi_6m']             = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_hi_10m']            = {'units'          : 'dimensionless'}
    turb_atts['phi_uT_hi_mast']           = {'units'          : 'dimensionless'}
    turb_atts['epsilon_u_2m']             = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_u_6m']             = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_u_10m']            = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_u_mast']           = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_v_2m']             = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_v_6m']             = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_v_10m']            = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_v_mast']           = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_w_2m']             = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_w_6m']             = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_w_10m']            = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_w_mast']           = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_2m']               = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_6m']               = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_10m']              = {'units'          : 'm^2/s^3'}
    turb_atts['epsilon_mast']             = {'units'          : 'm^2/s^3'}
    turb_atts['Phi_epsilon_2m']           = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_6m']           = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_10m']          = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_mast']         = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_hi_2m']        = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_hi_6m']        = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_hi_10m']       = {'units'          : 'dimensionless'}
    turb_atts['Phi_epsilon_hi_mast']      = {'units'          : 'dimensionless'}
    turb_atts['Nt_2m']                    = {'units'          : 'degC^2/s'}
    turb_atts['Nt_6m']                    = {'units'          : 'degC^2/s'}
    turb_atts['Nt_10m']                   = {'units'          : 'degC^2/s'}
    turb_atts['Nt_mast']                  = {'units'          : 'degC^2/s'}
    turb_atts['Phi_Nt_2m']                = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_6m']                = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_10m']               = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_mast']              = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_hi_2m']             = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_hi_6m']             = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_hi_10m']            = {'units'          : 'dimensionless'}
    turb_atts['Phi_Nt_hi_mast']           = {'units'          : 'dimensionless'}
    turb_atts['Phix_2m']                  = {'units'          : 'deg'}
    turb_atts['Phix_6m']                  = {'units'          : 'deg'}
    turb_atts['Phix_10m']                 = {'units'          : 'deg'}
    turb_atts['Phix_mast']                = {'units'          : 'deg'}
    turb_atts['DeltaU_2m']                = {'units'          : 'm/s'}
    turb_atts['DeltaU_6m']                = {'units'          : 'm/s'}
    turb_atts['DeltaU_10m']               = {'units'          : 'm/s'}
    turb_atts['DeltaU_mast']              = {'units'          : 'm/s'}
    turb_atts['DeltaV_2m']                = {'units'          : 'm/s'}
    turb_atts['DeltaV_6m']                = {'units'          : 'm/s'}
    turb_atts['DeltaV_10m']               = {'units'          : 'm/s'}
    turb_atts['DeltaV_mast']              = {'units'          : 'm/s'}
    turb_atts['DeltaT_2m']                = {'units'          : 'degC'}
    turb_atts['DeltaT_6m']                = {'units'          : 'degC'}
    turb_atts['DeltaT_10m']               = {'units'          : 'degC'}
    turb_atts['DeltaT_mast']              = {'units'          : 'degC'}
    turb_atts['Kurt_u_2m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_u_6m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_u_10m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_u_mast']              = {'units'          : 'unitless'}
    turb_atts['Kurt_v_2m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_v_6m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_v_10m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_v_mast']              = {'units'          : 'unitless'}
    turb_atts['Kurt_w_2m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_w_6m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_w_10m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_w_mast']              = {'units'          : 'unitless'}
    turb_atts['Kurt_T_2m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_T_6m']                = {'units'          : 'unitless'}
    turb_atts['Kurt_T_10m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_T_mast']              = {'units'          : 'unitless'}
    turb_atts['Kurt_uw_2m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_uw_6m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_uw_10m']              = {'units'          : 'unitless'}
    turb_atts['Kurt_uw_mast']             = {'units'          : 'unitless'}
    turb_atts['Kurt_vw_2m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_vw_6m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_vw_10m']              = {'units'          : 'unitless'}
    turb_atts['Kurt_vw_mast']             = {'units'          : 'unitless'}
    turb_atts['Kurt_wT_2m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_wT_6m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_wT_10m']              = {'units'          : 'unitless'}
    turb_atts['Kurt_wT_mast']             = {'units'          : 'unitless'}
    turb_atts['Kurt_uT_2m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_uT_6m']               = {'units'          : 'unitless'}
    turb_atts['Kurt_uT_10m']              = {'units'          : 'unitless'}
    turb_atts['Kurt_uT_mast']             = {'units'          : 'unitless'}
    turb_atts['Skew_u_2m']                = {'units'          : 'unitless'}
    turb_atts['Skew_u_6m']                = {'units'          : 'unitless'}
    turb_atts['Skew_u_10m']               = {'units'          : 'unitless'}
    turb_atts['Skew_u_mast']              = {'units'          : 'unitless'}
    turb_atts['Skew_v_2m']                = {'units'          : 'unitless'}
    turb_atts['Skew_v_6m']                = {'units'          : 'unitless'}
    turb_atts['Skew_v_10m']               = {'units'          : 'unitless'}
    turb_atts['Skew_v_mast']              = {'units'          : 'unitless'}
    turb_atts['Skew_w_2m']                = {'units'          : 'unitless'}
    turb_atts['Skew_w_6m']                = {'units'          : 'unitless'}
    turb_atts['Skew_w_10m']               = {'units'          : 'unitless'}
    turb_atts['Skew_w_mast']              = {'units'          : 'unitless'}
    turb_atts['Skew_T_2m']                = {'units'          : 'unitless'}
    turb_atts['Skew_T_6m']                = {'units'          : 'unitless'}
    turb_atts['Skew_T_10m']               = {'units'          : 'unitless'}
    turb_atts['Skew_T_mast']              = {'units'          : 'unitless'}
    turb_atts['Skew_uw_2m']               = {'units'          : 'unitless'}
    turb_atts['Skew_uw_6m']               = {'units'          : 'unitless'}
    turb_atts['Skew_uw_10m']              = {'units'          : 'unitless'}
    turb_atts['Skew_uw_mast']             = {'units'          : 'unitless'}
    turb_atts['Skew_vw_2m']               = {'units'          : 'unitless'}
    turb_atts['Skew_vw_6m']               = {'units'          : 'unitless'}
    turb_atts['Skew_vw_10m']              = {'units'          : 'unitless'}
    turb_atts['Skew_vw_mast']             = {'units'          : 'unitless'}
    turb_atts['Skew_wT_2m']               = {'units'          : 'unitless'}
    turb_atts['Skew_wT_6m']               = {'units'          : 'unitless'}
    turb_atts['Skew_wT_10m']              = {'units'          : 'unitless'}
    turb_atts['Skew_wT_mast']             = {'units'          : 'unitless'}
    turb_atts['Skew_uT_2m']               = {'units'          : 'unitless'}
    turb_atts['Skew_uT_6m']               = {'units'          : 'unitless'}
    turb_atts['Skew_uT_10m']              = {'units'          : 'unitless'}
    turb_atts['Skew_uT_mast']             = {'units'          : 'unitless'}  
    turb_atts['bulk_Hs_10m']              = {'units'          : 'Wm2'}
    turb_atts['bulk_Hl_10m']              = {'units'          : 'Wm2'}
    turb_atts['bulk_tau']                 = {'units'          : 'Pa'}
    turb_atts['bulk_z0']                  = {'units'          : 'm'}
    turb_atts['bulk_z0t']                 = {'units'          : 'm'}
    turb_atts['bulk_z0q']                 = {'units'          : 'm'}
    turb_atts['bulk_L']                   = {'units'          : 'm'}
    turb_atts['bulk_ustar']               = {'units'          : 'm/s'}
    turb_atts['bulk_tstar']               = {'units'          : 'K'}
    turb_atts['bulk_qstar']               = {'units'          : 'kg/kg'}
    turb_atts['bulk_dter']                = {'units'          : ''}
    turb_atts['bulk_dqer']                = {'units'          : ''}
    turb_atts['bulk_Hl_Webb_10m']         = {'units'          : 'Wm2'}    
    turb_atts['bulk_Cd_10m']              = {'units'          : 'unitless'}
    turb_atts['bulk_Ch_10m']              = {'units'          : 'unitless'}                                  
    turb_atts['bulk_Ce_10m']              = {'units'          : 'unitless'}
    turb_atts['bulk_Cdn_10m']             = {'units'          : 'unitless'}
    turb_atts['bulk_Chn_10m']             = {'units'          : 'unitless'}                                  
    turb_atts['bulk_Cen_10m']             = {'units'          : 'unitless'}                                        
    turb_atts['bulk_Rr']                  = {'units'          : 'unitless'}                                         
    turb_atts['bulk_Rt']                  = {'units'          : 'unitless'}  
    turb_atts['bulk_Rq']                  = {'units'          : 'unitless'}  

    

    # Some variables are dimensionless, meaning they are both scaled & unitless and the result is
    # independent of height such that it sounds a little funny to have a var name like
    # MO_dimensionless_param_2_m, but that is the only way to distinguish between the 4
    # calculations. So, for these I added ", calculated from 2 m" or whatever into the long_name.
    # Maybe there is a more clever way way?
    turb_atts['Hs_2m']                .update({'long_name'     : 'sensible heat flux',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Hs_6m']                .update({'long_name'     : 'sensible heat flux',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Hs_10m']               .update({'long_name'     : 'sensible heat flux',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Hs_mast']              .update({'long_name'     : 'sensible heat flux',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek USA-1 sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Hs_hi_2m']             .update({'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Hs_hi_6m']             .update({'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Hs_hi_10m']            .update({'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek uSonic-Cage MP sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : top_location_string,})
    turb_atts['Hs_hi_mast']           .update({'long_name'     : 'sensible heat flux calculated by eddy covariance, using sonic temperature, based on the high-frequency part of the cospectrum',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'Metek USA-1 sonic anemometer',
                                               'methods'       : 'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the high-frequency part of th wT-covariance spectrum',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Cd_2m']                .update({'long_name'     : 'Drag coefficient based on the momentum flux, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Cd_6m']                .update({'long_name'     : 'Drag coefficient based on the momentum flux, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Cd_10m']               .update({'long_name'     : 'Drag coefficient based on the momentum flux, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Cd_mast']              .update({'long_name'     : 'Drag coefficient based on the momentum flux, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Cd_hi_2m']             .update({'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Cd_hi_6m']             .update({'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Cd_hi_10m']            .update({'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Cd_hi_mast']           .update({'long_name'     : 'Drag coefficient based on the high-frequency part of the momentum flux, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['ustar_2m']             .update({'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['ustar_6m']             .update({'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['ustar_10m']            .update({'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['ustar_mast']           .update({'long_name'     : 'friction velocity (based only on the downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['ustar_hi_2m']          .update({'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['ustar_hi_6m']          .update({'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['ustar_hi_10m']         .update({'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['ustar_hi_mast']        .update({'long_name'     : 'friction velocity (based only on the high-frequency part of downstream, uw, stress components)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Tstar_2m']             .update({'long_name'     : 'temperature scale',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Tstar_6m']             .update({'long_name'     : 'temperature scale',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Tstar_10m']            .update({'long_name'     : 'temperature scale',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Tstar_mast']           .update({'long_name'     : 'temperature scale',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Tstar_hi_2m']          .update({'long_name'     : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Tstar_hi_6m']          .update({'long_name'     : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Tstar_hi_10m']         .update({'long_name'     : 'ftemperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Tstar_hi_mast']        .update({'long_name'     : 'temperature scale (based only on the high-frequency part of the turbulent fluxes)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['zeta_level_n_2m']      .update({'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['zeta_level_n_6m']      .update({'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['zeta_level_n_10m']     .update({'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['zeta_level_n_mast']    .update({'long_name'     : 'Monin-Obukhov stability parameter, z/L, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['zeta_level_n_hi_2m']   .update({'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['zeta_level_n_hi_6m']   .update({'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['zeta_level_n_hi_10m']  .update({'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['zeta_level_n_hi_mast'] .update({'long_name'     : 'Monin-Obukhov stability parameter based on the high-frequency part of the turbulent fluxes, z/L_hi, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['wu_csp_2m']            .update({'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['wu_csp_6m']            .update({'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['wu_csp_10m']           .update({'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['wu_csp_mast']          .update({'long_name'     : 'wu-covariance based on the wu-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['wv_csp_2m']            .update({'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['wv_csp_6m']            .update({'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['wv_csp_10m']           .update({'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['wv_csp_mast']          .update({'long_name'     : 'wv-covariance based on the wv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['uv_csp_2m']            .update({'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['uv_csp_6m']            .update({'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['uv_csp_10m']           .update({'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['uv_csp_mast']          .update({'long_name'     : 'uv-covariance based on the uv-cospectra integration',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['wT_csp_2m']            .update({'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['wT_csp_6m']            .update({'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['wT_csp_10m']           .update({'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['wT_csp_mast']          .update({'long_name'     : 'wT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['uT_csp_2m']            .update({'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['uT_csp_6m']            .update({'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['uT_csp_10m']           .update({'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['uT_csp_mast']          .update({'long_name'     : 'uT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['vT_csp_2m']            .update({'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['vT_csp_6m']            .update({'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['vT_csp_10m']           .update({'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['vT_csp_mast']          .update({'long_name'     : 'vT-covariance, vertical flux of the sonic temperature',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_u_2m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_u_6m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_u_10m']            .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_u_mast']           .update({'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_v_2m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_v_6m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_v_10m']            .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_v_mast']           .update({'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_w_2m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_w_6m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_w_10m']            .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_w_mast']           .update({'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_T_2m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_T_6m']             .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_T_10m']            .update({'long_name'     : 'MO universal function for the standard deviations, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_T_mast']           .update({'long_name'     : 'MO universal function for the standard deviations, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_uT_2m']            .update({'long_name'     : 'MO universal function for the horizontal heat flux, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_uT_6m']            .update({'long_name'     : 'MO universal function for the horizontal heat flux, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_uT_10m']           .update({'long_name'     : 'MO universal function for the horizontal heat flux, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_uT_mast']          .update({'long_name'     : 'MO universal function for the horizontal heat flux, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_u_hi_2m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_u_hi_6m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_u_hi_10m']         .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_u_hi_mast']        .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_v_hi_2m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_v_hi_6m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_v_hi_10m']         .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_v_hi_mast']        .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_w_hi_2m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_w_hi_6m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_w_hi_10m']         .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_w_hi_mast']        .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_T_hi_2m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_T_hi_6m']          .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_T_hi_10m']         .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_T_hi_mast']        .update({'long_name'     : 'MO universal function for the standard deviations based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['phi_uT_hi_2m']         .update({'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxesx, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['phi_uT_hi_6m']         .update({'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['phi_uT_hi_10m']        .update({'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['phi_uT_hi_mast']       .update({'long_name'     : 'MO universal function for the horizontal heat flux based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['epsilon_u_2m']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['epsilon_u_6m']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['epsilon_u_10m']        .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['epsilon_u_mast']       .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['epsilon_v_2m']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['epsilon_v_6m']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['epsilon_v_10m']        .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['epsilon_v_mast']       .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['epsilon_w_2m']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['epsilon_w_6m']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['epsilon_w_10m']        .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['epsilon_w_mast']       .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['epsilon_2m']           .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['epsilon_6m']           .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['epsilon_10m']          .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['epsilon_mast']         .update({'long_name'     : 'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Phi_epsilon_2m']       .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Phi_epsilon_6m']       .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Phi_epsilon_10m']      .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Phi_epsilon_mast']     .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Phi_epsilon_hi_2m']    .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Phi_epsilon_hi_6m']    .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Phi_epsilon_hi_10m']   .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Phi_epsilon_hi_mast']  .update({'long_name'     : 'Monin-Obukhov universal function Phi_epsilon based on the median epsilon based on the high-frequency part of the momentum flux, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Nt_2m']                .update({'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Nt_6m']                .update({'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Nt_10m']               .update({'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Nt_mast']              .update({'long_name'     : 'The dissipation (destruction) rate for half the temperature variance',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Phi_Nt_2m']            .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Phi_Nt_6m']            .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Phi_Nt_10m']           .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Phi_Nt_mast']          .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Phi_Nt_hi_2m']         .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 2 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Phi_Nt_hi_6m']         .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 6 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Phi_Nt_hi_10m']        .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from 10 m',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Phi_Nt_hi_mast']       .update({'long_name'     : 'Monin-Obukhov universal function Phi_Nt based on the high-frequency part of the turbulent fluxes, calculated from the mast',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Phix_2m']              .update({'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Phix_6m']              .update({'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Phix_10m']             .update({'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Phix_mast']            .update({'long_name'     : 'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['DeltaU_2m']            .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['DeltaU_6m']            .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['DeltaU_10m']           .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['DeltaU_mast']          .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['DeltaV_2m']            .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['DeltaV_6m']            .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['DeltaV_10m']           .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['DeltaV_mast']          .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['DeltaT_2m']            .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['DeltaT_6m']            .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['DeltaT_10m']           .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['DeltaT_mast']          .update({'long_name'     : 'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_u_2m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_u_6m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_u_10m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_u_mast']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_v_2m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_v_6m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_v_10m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_v_mast']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_w_2m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_w_6m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_w_10m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_w_mast']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_T_2m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_T_6m']            .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_T_10m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_T_mast']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_uw_2m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_uw_6m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_uw_10m']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_uw_mast']         .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_vw_2m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_vw_6m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_vw_10m']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_vw_mast']         .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_wT_2m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_wT_6m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_wT_10m']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_wT_mast']         .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Kurt_uT_2m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Kurt_uT_6m']           .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Kurt_uT_10m']          .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Kurt_uT_mast']         .update({'long_name'     : 'Kurtosis',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_u_2m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_u_6m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_u_10m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_u_mast']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_v_2m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_v_6m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_v_10m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_v_mast']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_w_2m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_w_6m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_w_10m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_w_mast']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_T_2m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_T_6m']            .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_T_10m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_T_mast']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_uw_2m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_uw_6m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_uw_10m']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_uw_mast']         .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_vw_2m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_vw_6m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_vw_10m']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_vw_mast']         .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_wT_2m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_wT_6m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_wT_10m']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_wT_mast']         .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['Skew_uT_2m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : bottom_location_string,})

    turb_atts['Skew_uT_6m']           .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : middle_location_string,})

    turb_atts['Skew_uT_10m']          .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : top_location_string,})

    turb_atts['Skew_uT_mast']         .update({'long_name'     : 'Skewness',
                                               'cf_name'       : '',
                                               'height'        : '',
                                               'location'      : mast_location_string,})

    turb_atts['bulk_Hs_10m']          .update({'long_name'     : 'sensible heat flux',
                                               'cf_name'       : 'upward_sensible_heat_flux_in_air',
                                               'instrument'    : 'various',
                                               'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                               'height'        : '10m',
                                               'location'      : top_location_string,})
    
    turb_atts['bulk_Hl_10m']          .update({'long_name'     : 'latent heat flux',
                                               'cf_name'       : 'upward_latent_heat_flux_in_air',
                                               'instrument'    : 'various',
                                               'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                               'height'        : '10m',
                                               'location'      : top_location_string,})
    
    turb_atts['bulk_tau']            .update({'long_name'      : 'stress',
                                               'cf_name'       : '',
                                               'instrument'    : 'various',
                                               'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                               'height'        : '10m',
                                               'location'      : top_location_string,})
    
    turb_atts['bulk_z0']             .update({'long_name'      : 'roughness length',
                                               'cf_name'       : '',
                                               'instrument'    : 'various',
                                               'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                               'height'        : 'n/a',
                                               'location'      : top_location_string,})

    turb_atts['bulk_z0t']            .update({'long_name'      : 'roughness length, temperature',
                                               'cf_name'       : '',
                                               'instrument'    : 'various',
                                               'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                               'height'        : 'n/a',
                                               'location'      : top_location_string,})

    turb_atts['bulk_z0q']            .update({'long_name'      : 'roughness length, humidity',
                                               'cf_name'       : '',
                                               'instrument'    : 'various',
                                               'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                               'height'        : 'n/a',
                                               'location'      : top_location_string,})
    
    turb_atts['bulk_L']             .update({'long_name'      : 'Obukhov length',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})       
        
    turb_atts['bulk_ustar']        .update({'long_name'       : 'friction velocity (sqrt(momentum flux)), ustar',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})   

    turb_atts['bulk_tstar']        .update({'long_name'       : 'temperature scale, tstar',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})   

    turb_atts['bulk_qstar']        .update({'long_name'       : 'specific humidity scale, qstar ',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})       
    
    turb_atts['bulk_dter']         .update({'long_name'       : 'diagnostic',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})            

    turb_atts['bulk_dqer']         .update({'long_name'       : 'diagnostic',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})         

    turb_atts['bulk_Hl_Webb_10m']  .update({'long_name'       : 'latent heat flux, Webb density correction applied',
                                              'cf_name'       : 'upward_latent_heat_flux_in_air',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm, Webb et al. (1980) https://doi.org/10.1002/qj.49710644707',
                                              'height'        : 'n/a',
                                              'location'      : top_location_string,})   

    turb_atts['bulk_Cd_10m']       .update({'long_name'       : 'transfer coefficient for stress',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '10m',
                                              'location'      : top_location_string,})   


    turb_atts['bulk_Ch_10m']       .update({'long_name'       : 'transfer coefficient for Hs',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '10m',
                                              'location'      : top_location_string,})

    turb_atts['bulk_Ce_10m']       .update({'long_name'       : 'transfer coefficient for Hl',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '10m',
                                              'location'      : top_location_string,})   

    turb_atts['bulk_Cdn_10m']      .update({'long_name'       : '10 m neutral transfer coefficient for stress',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '10m',
                                              'location'      : top_location_string,})       

    turb_atts['bulk_Chn_10m']      .update({'long_name'       : '10 m neutral transfer coefficient for Hs',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '10m',
                                              'location'      : top_location_string,})       

    turb_atts['bulk_Cen_10m']      .update({'long_name'       : '10 m neutral transfer coefficient for Hl',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '10m',
                                              'location'      : top_location_string,})       

    turb_atts['bulk_Rr']           .update({'long_name'       : 'Reynolds number',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '',
                                              'location'      : top_location_string,})      
    
    turb_atts['bulk_Rt']           .update({'long_name'       : '',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '',
                                              'location'      : top_location_string,})   

    turb_atts['bulk_Rq']           .update({'long_name'       : '',
                                              'cf_name'       : '',
                                              'instrument'    : 'various',
                                              'methods'       : 'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                              'height'        : '',
                                              'location'      : top_location_string,})   

    return turb_atts, list(turb_atts.keys()).copy() 
