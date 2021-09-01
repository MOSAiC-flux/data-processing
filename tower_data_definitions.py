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
    cv = ['2.0', '7/15/2021', 'ccox']
    return cv

# file_type must be "slow", "fast", "level2", or "turb"
def define_global_atts(file_type):
    cv = code_version()
    global_atts = {                # attributes to be written into the netcdf output file
        'date_created'     :'{}'.format(time.ctime(time.time())),
        'title'            :'MOSAiC flux group data product', # blank variables are specific to site characterization 
        'contact'          :'Matthew Shupe, University of Colorado, matthew.shupe@colorado.edu',
        'institution'      :'CIRES, University of Colorado and NOAA Physical Sciences Laboratory',
        'file_creator'     :'Michael R. Gallagher; Christopher J. Cox',
        'creator_email'    :'michael.r.gallagher@noaa.gov; christopher.j.cox@noaa.gov', 
        'project'          :'Thermodynamic and Dynamic Drivers of the Arctic Sea Ice Mass Budget at MOSAiC', 
        'funding'          :'Funding sources: National Science Foundation Award Number OPP1724551; NOAA Physical Science Laboratory and Arctic Research Program; Department of Energy Office of Science Atmospheric Radiation Measurement Program;',
        'source'           :'Observations made during the Multidisciplinary drifting Observatory for the Study of Arctic Climate (MOSAiC 2019-2020) expedition PS-122',
        'system'           :'10m Tower',
        'references'       :'', 
        'keywords'         :'Polar, Arctic, Supersite, Observations, Flux, Atmosphere, MOSAiC',
        'conventions'      :'cf convention variable naming as attribute whenever possible',  
        'history'          :'based on raw instrument data files',
        'version'          : cv[0]+', '+cv[1], 
    }
    # Some specifics for the tubulence file
    if file_type == "slow":
        global_atts['quality_control']  = 'This Level 1 product is for archival purposes and has undergone minimal data processing and quality control, please contact the authors/PI if you would like to know more.',

    elif file_type == "fast":
        global_atts['quality_control']  = 'This Level 1 product is for archival purposes and has undergone minimal data processing and quality control, please contact the authors/PI if you would like to know more.',

    elif file_type == "level2":
        global_atts['quality_control']  = 'Significant quality control in place for the observations used in the derived products. This Level 2 data is processed in many significant ways and this particular version is *for preliminary results only*. Please have discussions with the authors about what this means if you would like to use this data for any analyses.',

    elif file_type == "`10hz`":
        global_atts['quality_control']  = 'This 10Hz product is a product for turbulence junkies that would like to evaluate sonic/licor observations at their own peril. Minor quality control is in place, including rotation to x/y/z but the data remains untouched in processing terms.',
        global_atts['Funding']          = 'Funding sources: National Science Foundation Award Number OPP1724551; NOAA Physical Science Laboratory and Arctic Research Program'

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
    lev1_slow_atts['fp_A_Wm2']           = {'units' : 'W/m2'}      
    lev1_slow_atts['fp_B_mV']            = {'units' : 'mV'}       
    lev1_slow_atts['fp_B_Wm2']           = {'units' : 'W/m2'}      
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
                                                  'methods'    : 'synched with GPS',                                     
                                                  'height'     : 'N/A',
                                                  'location'   : 'logger box',})

    lev1_slow_atts['RECORD']             .update({'long_name'  : 'record number from tower data logger',
                                                  'instrument' : 'Campbell CR1000X',
                                                  'methods'    : '',
                                                  'height'     : 'N/A',			            
                                                  'location'   : 'logger box',})               

    lev1_slow_atts['gps_lat_deg']        .update({'long_name'  : 'latitude from gps at tower',  
                                                  'instrument' : 'Hemisphere V102',		    
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                  'height'     : '2 m',			    
                                                  'location'   : bottom_location_string,})    	    
                                                                                                  
    lev1_slow_atts['gps_lat_min']        .update({'long_name'  : 'latitude from gps at tower',
                                                  'instrument' : 'Hemisphere V102',		    
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	      
                                                  'height'     : '2 m',			            
                                                  'location'   : bottom_location_string,})    

    lev1_slow_atts['gps_lon_deg']        .update({'long_name'  :'longitude from gps at tower', 
                                                  'instrument' : 'Hemisphere V102',		      
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	  
                                                  'height'     : '2 m',			              
                                                  'location'   : bottom_location_string,})      

    lev1_slow_atts['gps_lon_min']        .update({'long_name'  :'longitude from gps at tower', 
                                                  'instrument' : 'Hemisphere V102',		      
                                                  'methods'    : 'GPRMC,  GPGGA, GPGZDA',	  
                                                  'height'     : '2 m',			              
                                                  'location'   : bottom_location_string,})      

    lev1_slow_atts['gps_hdg']            .update({'long_name'  : 'heading from gps at tower', 
                                                  'instrument' : 'Hemisphere V102',		   
                                                  'methods'    : 'HEHDT',			   
                                                  'height'     : '2 m',			   
                                                  'location'   : bottom_location_string,})     

    lev1_slow_atts['gps_alt']            .update({'long_name'  : 'altitude from gps at tower',
                                                  'instrument' : 'Hemisphere V102',		   
                                                  'methods'    : 'GPRMC, GPGGA, GPGZDA',	   
                                                  'height'     : '2 m',			   
                                                  'location'   : bottom_location_string,})     

    lev1_slow_atts['gps_qc']             .update({'long_name'  : 'gps fix quality variable',
                                                  'instrument' : 'Hemisphere V102',
                                                  'methods'    : 'GPGGA; fix quality: 0 = invalid; 1 = gps fix (sps); 2 = dgps fix; 3 = pps fix; 4 = real time kinematic; 5 = float rtk; 6 = estimated (deck reckoning); 7 = manual input mode; 8 = simulation mode',
                                                  'height'     : '2 m',
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['gps_nsat']           .update({'long_name'  : 'gps number of tracked satellites', 
                                                  'instrument' : 'Hemisphere V102',			       
                                                  'methods'    : 'GPGGA',		       
                                                  'height'     : '2 m',				       
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['gps_hdop']           .update({'long_name'  : 'gps Horizontal Dilution Of Precision (HDOP)', 
                                                  'instrument' : 'Hemisphere V102',			  
                                                  'methods'    : 'GPGGA',		  
                                                  'height'     : '2 m',				  
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['PTemp']              .update({'long_name'  : 'logger electronics panel temperature',
                                                  'instrument' : 'Campbell CR1000X',
                                                  'methods'    : '',
                                                  'height'     : 'N/A',			                       
                                                  'location'   : 'logger box',})               

    lev1_slow_atts['batt_volt']          .update({'long_name'  : 'voltage of the power source supplying the logger', 
                                                  'instrument' : 'Campbell CR1000X',                     
                                                  'methods'    : '',                                     
                                                  'height'     : 'N/A',
                                                  'location'   : 'logger box',})               

    lev1_slow_atts['call_time_mainscan'] .update({'long_name'  : 'duration of the logger scan', 
                                                  'instrument' : 'Campbell CR1000X',                     
                                                  'methods'    : '',                                     
                                                  'height'     : 'N/A',			                       
                                                  'location'   : 'logger box',})               

    lev1_slow_atts['apogee_body_T']      .update({'long_name'  : 'sensor body temperature',   
                                                  'instrument' : 'Apogee SI-4H1-SS IRT',	       
                                                  'methods'    : 'infrared thermometer; SDI-12 protocol',
                                                  'height'     : '2 m',			       
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['apogee_targ_T']      .update({'long_name'  : 'sensor target 8-14 micron brightness temperature',
                                                  'instrument' : 'Apogee SI-4H1-SS IRT',
                                                  'methods'    : 'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                  'height'     : 'surface',
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['sr50_dist']          .update({'long_name'  : 'distance to surface from SR50; temperature compensation correction applied',
                                                  'instrument' : 'Campbell Scientific SR50A',
                                                  'methods'    : 'unheated, temperature correction applied',
                                                  'height'     : '2 m',
                                                  'location'   : bottom_location_string,})

    lev1_slow_atts['vaisala_RH_2m']      .update({'long_name'  : 'relative humidity wrt water',   
                                                  'instrument' : 'Vaisala PTU300',		       
                                                  'methods'    : 'meteorology sensor, heated capacitive thin-film polymer; RS-485 protocol',
                                                  'height'     : '2 m',			       
                                                  'location'   : bottom_location_string,})         

    lev1_slow_atts['vaisala_T_2m']       .update({'long_name'  : 'temperature',		       
                                                  'instrument' : 'Vaisala HMT330',		       
                                                  'methods'    : 'meteorology sensor, PT100 RTD; RS-485 protocol',
                                                  'height'     : '2 m',			       
                                                  'location'   : bottom_location_string,})         

    lev1_slow_atts['vaisala_Td_2m']      .update({'long_name'  : 'dewpoint temperature',		       
                                                  'instrument' : 'Vaisala PTU300',		       
                                                  'methods'    : 'calculated by sensor electonics; RS-485 protocol',
                                                  'height'     : '2 m',			       
                                                  'location'   : bottom_location_string,})         

    lev1_slow_atts['vaisala_P_2m']       .update({'long_name'  : 'air pressure at 2 m',	       
                                                  'instrument' : 'Vaisala PTU 300',		       
                                                  'methods'    : 'meteorology sensor; RS-485 protocol',
                                                  'height'     : '2 m',			       
                                                  'location'   : mast_location_string,})           

    lev1_slow_atts['vaisala_RH_6m']      .update({'long_name'  : 'relative humidity wrt water',   
                                                  'instrument' : 'Vaisala HMT330',		       
                                                  'methods'    : 'meteorology sensor, heated capacitive thin-film polymer; RS-485 protocol',
                                                  'height'     : '6 m',			       
                                                  'location'   : middle_location_string,})         

    lev1_slow_atts['vaisala_T_6m']       .update({'long_name'  : 'temperature',				
                                                  'instrument' : 'Vaisala HMT330',				
                                                  'methods'    : 'meteorology sensor, PT100 RTD; RS-485 protocol',		
                                                  'height'     : '6 m',					
                                                  'location'   : middle_location_string,})                  

    lev1_slow_atts['vaisala_Td_6m']      .update({'long_name'  : 'dewpoint temperature',				
                                                  'instrument' : 'Vaisala HMT330',				
                                                  'methods'    : 'calculated by sensor electonics; RS-485 protocol',		
                                                  'height'     : '6 m',					
                                                  'location'   : middle_location_string,})                  

    lev1_slow_atts['vaisala_RH_10m']     .update({'long_name'  : 'relative humidity wrt water',	     
                                                  'instrument' : 'Vaisala HMT330',			     
                                                  'methods'    : 'meteorology sensor, heated capacitive thin-film polymer; RS-485 protocol',	     
                                                  'height'     : '10 m',				     
                                                  'location'   : top_location_string,})                  

    lev1_slow_atts['vaisala_T_10m']      .update({'long_name'  : 'temperature',			     
                                                  'instrument' : 'Vaisala HMT330',			     
                                                  'methods'    : 'meteorology sensor, PT100 RTD; RS-485 protocol',	     
                                                  'height'     : '10 m',				     
                                                  'location'   : top_location_string,})                  

    lev1_slow_atts['vaisala_Td_10m']     .update({'long_name'  : 'dewpoint temperature',			     
                                                  'instrument' : 'Vaisala HMT330',			     
                                                  'methods'    : 'calculated by sensor electonics; RS-485 protocol',	     
                                                  'height'     : '10 m',				     
                                                  'location'   : top_location_string,})                  

    lev1_slow_atts['fp_A_mV']            .update({'long_name'  : 'voltage from Hukseflux plate A',	
                                                  'instrument' : 'Hukseflux HFP01',			
                                                  'methods'    : 'analog voltage read by CR1000X',	
                                                  'height'     : '',				
                                                  'location'   : 'near base of flux tower',})

    lev1_slow_atts['fp_A_Wm2']           .update({'long_name'  : 'conductive flux from plate A',	   
                                                  'instrument' : 'Hukseflux HFP01',			   
                                                  'methods'    : 'Sensitivity 63.00/1000 [mV/(W/m2)]', 
                                                  'height'     : '',				   
                                                  'location'   : 'near base of flux tower',})   

    lev1_slow_atts['fp_B_mV']            .update({'long_name'  : 'voltage from Hukseflux plate B',	     
                                                  'instrument' : 'Hukseflux HFP01',			     
                                                  'methods'    : 'analog voltage read by CR1000X',	     
                                                  'height'     : '',				     
                                                  'location'   : 'near base of flux tower',})

    lev1_slow_atts['fp_B_Wm2']           .update({'long_name'  : 'conductive flux from plate B',	     
                                                  'instrument' : 'Hukseflux HFP01',			     
                                                  'methods'    : 'Sensitivity 63.91/1000 [mV/(W/m2)]',   
                                                  'height'     : '',				     
                                                  'location'   : 'near base of flux tower',})

    lev1_slow_atts['mast_T']             .update({'long_name'  : 'temperature',			      
                                                  'instrument' : 'Vaisala WXT530',			      
                                                  'methods'    : 'meteorology sensor, PT1000 RTD; SDI-12 protocol',	      
                                                  'height'     : 'variable',				      
                                                  'location'   : mast_location_string,})                  

    lev1_slow_atts['mast_RH']            .update({'long_name'  : 'relative humidity wrt water',	      
                                                  'instrument' : 'Vaisala WXT530',			      
                                                  'methods'    : 'digitally polled from instument',	      
                                                  'height'     : 'variable',			      
                                                  'location'   : mast_location_string,})                  

    lev1_slow_atts['mast_P']             .update({'long_name'  : 'air pressure',				
                                                  'instrument' : 'Vaisala WXT530',				
                                                  'methods'    : 'digitally polled from instument',		
                                                  'height'     : 'variable 23-30m',				
                                                  'location'   : mast_location_string,})

    lev1_slow_atts['licor_ball_mV']      .update({'long_name'  : 'licor heating mv',
                                                  'instrument' : 'extended-lead thermocouple',
                                                  'methods'    : 'uncalibrated diagnostic, relative tracking to prevent overheating',		
                                                  'height'     : 'variable',				
                                                  'location'   : licor_location,})

    # noodleville stuff
    lev1_slow_atts['mast_RECORD']             .update({'long_name'  : 'record number from tower data logger',
                                                       'instrument' : 'Campbell CR1000X',                     
                                                       'methods'    : '',
                                                       'height'     : 'N/A',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lat_deg_Avg']    .update({'long_name'  : 'latitude degrees from gps at mast',  
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lat_min_Avg']    .update({'long_name'  : 'latitude minutes from gps at mast',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lon_deg_Avg']    .update({'long_name'  : 'longitude degrees from gps at mast',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_lon_min_Avg']    .update({'long_name'  : 'longitude minutes from gps at mast',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_hdg_Avg']        .update({'long_name'  : 'heading from gps at mast',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'HEHDT',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_alt_Avg']        .update({'long_name'  : 'altitude from gps at mast',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPRMC, GPGGA, GPGZDA',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_qc']             .update({'long_name'  : 'gps fix quality variable',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPGGA; fix quality: 0 = invalid; 1 = gps fix (sps); 2 = dgps fix; 3 = pps fix; 4 = real time kinematic; 5 = float rtk; 6 = estimated (deck reckoning); 7 = manual input mode; 8 = simulation mode.',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_hdop_Avg']       .update({'long_name'  : 'gps Horizontal Dilution Of Precision (HDOP)',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPGGA',	    
                                                       'height'     : '0.5 m',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_gps_nsat_Avg']       .update({'long_name'  : 'gps number of tracked satellites',
                                                       'instrument' : 'Hemisphere V102',		    
                                                       'methods'    : 'GPGGA',	    
                                                       'height'     : 'N/A',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_PTemp']              .update({'long_name'  : 'logger electronics panel temperature',
                                                       'instrument' : 'Campbell CR1000X',
                                                       'methods'    : '',
                                                       'height'     : 'N/A',				
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_batt_volt']          .update({'long_name'  : 'voltage of the power source supplying the logger', 
                                                       'instrument' : 'Campbell CR1000X',           
                                                       'methods'    : '',                           
                                                       'height'     : 'N/A',			    
                                                       'location'   : noodleville_location_string,})
    
    lev1_slow_atts['mast_call_time_mainscan'] .update({'long_name'  : 'duration of the logger scan', 
                                                       'instrument' : 'Campbell CR1000X',                     
                                                       'methods'    : '',                                     
                                                       'height'     : 'N/A',			                       
                                                       'location'   : noodleville_location_string,})


    return lev1_slow_atts, list(lev1_slow_atts.keys()).copy() 

# because I decided to include all of the fast instruments in groups inside of one netcdf file, the variable names
# for the fast level1 data are much more integral to the level1/level2 processing code. so. if you decide you want these
# names to be different, you're going to have to change the "get_fast" functions in the "create" code as well as some
# of the processing code in the level2 create file. it's annoying, maybe not the best design choice.
def define_level1_fast():

    licor_location         = 'first level on flux tower'
    bottom_location_string = 'first level on flux tower'
    middle_location_string = 'second level on flux tower'
    top_location_string    = 'third level on flux tower'
    mast_location_string   = 'top of radio mast'
    
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
    lev1_fast_atts['metek_2m_hspd']        = {'units' : 'm/s'     }
    lev1_fast_atts['metek_2m_ts']          = {'units' : 'deg'     }
    lev1_fast_atts['metek_2m_incx']        = {'units' : 'deg'     }
    lev1_fast_atts['metek_2m_incy']        = {'units' : 'deg'     }

    lev1_fast_atts['metek_6m_TIMESTAMP']   = {'units' : 'time'    }
    lev1_fast_atts['metek_6m_heatstatus']  = {'units' : 'int'     }
    lev1_fast_atts['metek_6m_x']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_y']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_z']           = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_T']           = {'units' : 'C'       }
    lev1_fast_atts['metek_6m_hspd']        = {'units' : 'm/s'     }
    lev1_fast_atts['metek_6m_ts']          = {'units' : 'deg'     }
    lev1_fast_atts['metek_6m_incx']        = {'units' : 'deg'     }
    lev1_fast_atts['metek_6m_incy']        = {'units' : 'deg'     }

    lev1_fast_atts['metek_10m_TIMESTAMP']  = {'units' : 'time'    }
    lev1_fast_atts['metek_10m_heatstatus'] = {'units' : 'int'     }
    lev1_fast_atts['metek_10m_x']          = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_y']          = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_z']          = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_T']          = {'units' : 'C'       }
    lev1_fast_atts['metek_10m_hspd']       = {'units' : 'm/s'     }
    lev1_fast_atts['metek_10m_ts']         = {'units' : 'deg'     }
    lev1_fast_atts['metek_10m_incx']       = {'units' : 'deg'     }
    lev1_fast_atts['metek_10m_incy']       = {'units' : 'deg'     }
 
    lev1_fast_atts['metek_mast_TIMESTAMP'] = {'units' : 'time'    }
    lev1_fast_atts['metek_mast_x']         = {'units' : 'm/s'     }
    lev1_fast_atts['metek_mast_y']         = {'units' : 'm/s'     }
    lev1_fast_atts['metek_mast_z']         = {'units' : 'm/s'     }
    lev1_fast_atts['metek_mast_T']         = {'units' : 'C'       }

    lev1_fast_atts['licor_TIMESTAMP']      = {'units' : 'time'    }
    lev1_fast_atts['licor_diag']           = {'units' : 'int'     }
    lev1_fast_atts['licor_co2']            = {'units' : 'mmol/m3' }
    lev1_fast_atts['licor_h2o']            = {'units' : 'mmol/m3' }
    lev1_fast_atts['licor_T']              = {'units' : 'deg C'   }
    lev1_fast_atts['licor_pr']             = {'units' : 'hPa'     }
    lev1_fast_atts['licor_co2_str']        = {'units' : 'percent' }
    lev1_fast_atts['licor_pll']            = {'units' : 'boolean' }
    lev1_fast_atts['licor_dt']             = {'units' : 'boolean' }
    lev1_fast_atts['licor_ct']             = {'units' : 'boolean' }

    lev1_fast_atts['metek_2m_TIMESTAMP']   .update({  'long_name'                              :'time stamp of receipt of sensor message',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,}) 

    lev1_fast_atts['metek_2m_x']           .update({  'long_name'                              :'wind velocity in x',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_y']           .update({  'long_name'                              :'wind velocity in y',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_z']           .update({  'long_name'                              :'wind velocity in z',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_T']           .update({  'long_name'                              :'acoustic temperature',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_heatstatus']  .update({  'long_name'                              :'sensor diagnostics code',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; char 8 = heating setting (0=off,1=on,2=auto,3=auto and quality detection); char 9 = heating state (0=off,1=on/operational,2=on/faulty); char 10 = how many of 9 paths failed',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_hspd']        .update({  'long_name'                              :'horizontal wind speed',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; based on x,y in sensor coordinate frame',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_ts']          .update({  'long_name'                              :'wind direction',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_incx']        .update({  'long_name'                              :'sensor inclinometer pitch angle',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_2m_incy']        .update({  'long_name'                              :'sensor inclinometer roll angle',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north',
                                                      'height'                                 :'2 m',
                                                      'location'                               : bottom_location_string,})

    lev1_fast_atts['metek_6m_TIMESTAMP']   .update({  'long_name'                              :'time stamp of receipt of sensor message',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,}) 

    lev1_fast_atts['metek_6m_x']           .update({  'long_name'                              :'wind velocity in x',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_y']           .update({  'long_name'                              :'wind velocity in y',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_z']           .update({  'long_name'                              :'wind velocity in z',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_T']           .update({  'long_name'                              :'acoustic temperature',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_heatstatus']  .update({  'long_name'                              :'sensor diagnostics code',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; char 8 = heating setting (0=off,1=on,2=auto,3=auto and quality detection); char 9 = heating state (0=off,1=on/operational,2=on/faulty); char 10 = how many of 9 paths failed',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_hspd']        .update({  'long_name'                              :'horizontal wind speed',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; based on x,y in sensor coordinate frame',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_ts']          .update({  'long_name'                              :'wind direction',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_incx']        .update({  'long_name'                              :'sensor inclinometer pitch angle',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_6m_incy']        .update({  'long_name'                              :'sensor inclinometer roll angle',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,})

    lev1_fast_atts['metek_10m_TIMESTAMP']  .update({  'long_name'                              :'time stamp of receipt of sensor message',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,}) 

    lev1_fast_atts['metek_10m_x']          .update({  'long_name'                              :'wind velocity in x',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_y']          .update({  'long_name'                              :'wind velocity in y',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_z']          .update({  'long_name'                              :'wind velocity in z',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_T']          .update({  'long_name'                              :'acoustic temperature',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_heatstatus'] .update({  'long_name'                              :'sensor diagnostics code',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; char 8 = heating setting (0=off,1=on,2=auto,3=auto and quality detection); char 9 = heating state (0=off,1=on/operational,2=on/faulty); char 10 = how many of 9 paths failed',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_hspd']       .update({  'long_name'                              :'horizontal wind speed',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; based on x,y in sensor coordinate frame',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_ts']         .update({  'long_name'                              :'wind direction',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_incx']       .update({  'long_name'                              :'sensor inclinometer pitch angle',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_10m_incy']       .update({  'long_name'                              :'sensor inclinometer roll angle',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north',
                                                      'height'                                 :'10 m',
                                                      'location'                               : top_location_string,})

    lev1_fast_atts['metek_mast_TIMESTAMP'] .update({  'long_name'                              :'time stamp of receipt of sensor message',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'mast',
                                                      'location'                               : mast_location_string,}) 

    lev1_fast_atts['metek_mast_x']         .update({  'long_name'                              :'wind velocity in x',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'mast',
                                                      'location'                               : mast_location_string,})

    lev1_fast_atts['metek_mast_y']         .update({  'long_name'                              :'wind velocity in y',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'mast',
                                                      'location'                               : mast_location_string,})

    lev1_fast_atts['metek_mast_z']         .update({  'long_name'                              :'wind velocity in z',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'mast',
                                                      'location'                               : mast_location_string,})

    lev1_fast_atts['metek_mast_T']         .update({  'long_name'                              :'acoustic temperature',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'mast',
                                                      'location'                               : mast_location_string,})

    lev1_fast_atts['licor_diag']           .update({  'long_name'                              :'bit-packed diagnostic integer',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol; bits 0-3 = signal strength; bit 5 = PLL; bit 6 = detector temp; bit 7 = chopper temp',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_co2']            .update({  'long_name'                              :'CO2 gas density',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_h2o']            .update({  'long_name'                              :'water vapor density',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})
    
    lev1_fast_atts['licor_pr']             .update({  'long_name'                              :'air pressure',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_T']              .update({  'long_name'                              :'temperature at strut',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_co2_str']        .update({  'long_name'                              :'CO2 signal strength diagnostic',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; raw co2 reference signal relative to expected value',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_pll']            .update({  'long_name'                              :'phase lock loop',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; 1 = optical filter wheel rotating at correct rate',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_dt']             .update({  'long_name'                              :'detector temperature',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; 1 = temperature near set point',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    lev1_fast_atts['licor_ct']             .update({  'long_name'                              :'chopper temperature',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; 1 = temperature near set point',
                                                      'height'                                 :'2 m',
                                                      'location'                               : licor_location,})

    return lev1_fast_atts, list(lev1_fast_atts.keys()).copy() 
 
def define_level2_variables():
 
    # these are the installation heights recorded.
    # it is a nominal height because the surface height changed in time
   
    licor_location         ='first level on met city tower'
    bottom_location_string ='first level on met city tower'
    middle_location_string ='second level on met city tower'
    top_location_string    ='third level on met city tower'
    mast_location_string   ='top of radio mast at met city'
    arm_location_string    ='Met City'

    # platform
    tower_platform     = "10-m Met Tower"
    mast_platform      = "X-m Mast"
    radiation_platform = "Radiation Station"
    
    # data_provenance 
    flux_slow_provenance = "Based on data from the mosflxtowerslow.level1 datastream with doi  :xxxxxxxx" 
    flux_fast_provenance = "Based on data from the mosflxtowerfast.level1 datastream with doi  :xxxxxxxx" 
    radiation_provenance = "Based on data from the mosiceradriihimakiS3.b2 datastream with doi :xxxxxxxx"
 
    # measurement_source
    radiation_source = "Department of Energy Atmospheric Radiation Measurement (ARM) User Facility"
    flux_source      = "CIRES, University of Colorado / NOAA atmospheric surface flux team"
    mast_source      = "School of Earth and Environment, University of Leeds" 

    # funding_sources
    radiation_funding = "Department of Energy, Office of Science, Biological and Environmental Research Program"
    flux_funding      = "National Science Foundation OPP1724551 and NOAA Physical Science Laboratory"
    mast_funding      = "UK Natural Environment Research Council"

    lev2_atts = OrderedDict()

    lev2_atts['lat_tower']               = {'units'                                            :'degrees_north'}
    lev2_atts['lon_tower']               = {'units'                                            :'degrees_east'}
    lev2_atts['heading_tower']           = {'units'                                            :'degrees_true'}
    lev2_atts['heading_mast']            = {'units'                                            :'deg'}
    lev2_atts['lat_mast']                = {'units'                                            :'min'}
    lev2_atts['lon_mast']                = {'units'                                            :'deg'}
    lev2_atts['zenith_true']             = {'units'                                            :'degrees'}
    lev2_atts['zenith_apparent']         = {'units'                                            :'degrees'}
    lev2_atts['azimuth']                 = {'units'                                            :'degrees'}
    lev2_atts['ship_bearing']            = {'units'                                            :'degrees'}
    lev2_atts['ship_distance']           = {'units'                                            :'meters'}
    lev2_atts['sr50_dist']               = {'units'                                            :'meters'}
    lev2_atts['temp_2m']                 = {'units'                                            :'deg C'}
    lev2_atts['temp_6m']                 = {'units'                                            :'deg C'}
    lev2_atts['temp_10m']                = {'units'                                            :'deg C'}
    lev2_atts['temp_mast']               = {'units'                                            :'deg C'}
    lev2_atts['dew_point_2m']            = {'units'                                            :'deg C'}
    lev2_atts['dew_point_6m']            = {'units'                                            :'deg C'}
    lev2_atts['dew_point_10m']           = {'units'                                            :'deg C'}
    lev2_atts['dew_point_mast']          = {'units'                                            :'deg C'}
    lev2_atts['rh_2m']                   = {'units'                                            :'percent'}
    lev2_atts['rh_6m']                   = {'units'                                            :'percent'}
    lev2_atts['rh_10m']                  = {'units'                                            :'percent'}
    lev2_atts['rh_mast']                 = {'units'                                            :'percent'}
    lev2_atts['atmos_pressure_2m']       = {'units'                                            :'hPa'}
    lev2_atts['atmos_pressure_mast']     = {'units'                                            :'hPa'}
    lev2_atts['brightness_temp_surface'] = {'units'                                            :'deg C'}
    lev2_atts['subsurface_heat_flux_A']  = {'units'                                            :'W/m2'}
    lev2_atts['subsurface_heat_flux_B']  = {'units'                                            :'W/m2'}
    lev2_atts['snow_depth']              = {'units'                                            :'cm'}
    lev2_atts['mixing_ratio_2m']         = {'units'                                            :'g/kg'}
    lev2_atts['mixing_ratio_6m']         = {'units'                                            :'g/kg'}
    lev2_atts['mixing_ratio_10m']        = {'units'                                            :'g/kg'}
    lev2_atts['mixing_ratio_mast']       = {'units'                                            :'g/kg'}
    lev2_atts['rhi_2m']                  = {'units'                                            :'percent'}
    lev2_atts['rhi_6m']                  = {'units'                                            :'percent'}
    lev2_atts['rhi_10m']                 = {'units'                                            :'percent'}
    lev2_atts['rhi_mast']                = {'units'                                            :'percent'}
    lev2_atts['vapor_pressure_2m']       = {'units'                                            :'Pa'}
    lev2_atts['vapor_pressure_6m']       = {'units'                                            :'Pa'}
    lev2_atts['vapor_pressure_10m']      = {'units'                                            :'Pa'}
    lev2_atts['vapor_pressure_mast']     = {'units'                                            :'Pa'}
    lev2_atts['wspd_vec_mean_2m']        = {'units'                                            :'m/s'}
    lev2_atts['wspd_vec_mean_6m']        = {'units'                                            :'m/s'}
    lev2_atts['wspd_vec_mean_10m']       = {'units'                                            :'m/s'}
    lev2_atts['wspd_vec_mean_mast']      = {'units'                                            :'m/s'}
    lev2_atts['wdir_vec_mean_2m']        = {'units'                                            :'deg true'}
    lev2_atts['wdir_vec_mean_6m']        = {'units'                                            :'deg true'}
    lev2_atts['wdir_vec_mean_10m']       = {'units'                                            :'deg true'}
    lev2_atts['wdir_vec_mean_mast']      = {'units'                                            :'deg true'}
    lev2_atts['h2o_licor']               = {'units'                                            :'mmol/m3'}
    lev2_atts['co2_licor']               = {'units'                                            :'mmol/m3'}
    lev2_atts['temp_licor']              = {'units'                                            :'deg C'}
    lev2_atts['pressure_licor']          = {'units'                                            :'hPa'}
    lev2_atts['wspd_u_mean_2m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_u_mean_6m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_u_mean_10m']         = {'units'                                            :'m/s'}
    lev2_atts['wspd_u_mean_mast']        = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_mean_2m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_mean_6m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_mean_10m']         = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_mean_mast']        = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_mean_2m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_mean_6m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_mean_10m']         = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_mean_mast']        = {'units'                                            :'m/s'}
    lev2_atts['temp_acoustic_mean_2m']   = {'units'                                            :'deg C'}
    lev2_atts['temp_acoustic_mean_6m']   = {'units'                                            :'deg C'}
    lev2_atts['temp_acoustic_mean_10m']  = {'units'                                            :'deg C'}
    lev2_atts['temp_acoustic_mean_mast'] = {'units'                                            :'deg C'}
    lev2_atts['wspd_u_std_2m']           = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_std_2m']           = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_std_2m']           = {'units'                                            :'m/s'}
    lev2_atts['temp_acoustic_std_2m']    = {'units'                                            :'deg C'}
    lev2_atts['wspd_u_std_6m']           = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_std_6m']           = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_std_6m']           = {'units'                                            :'m/s'}
    lev2_atts['temp_acoustic_std_6m']    = {'units'                                            :'deg C'}
    lev2_atts['wspd_u_std_10m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_std_10m']          = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_std_10m']          = {'units'                                            :'m/s'}
    lev2_atts['temp_acoustic_std_10m']   = {'units'                                            :'deg C'}
    lev2_atts['wspd_u_std_mast']         = {'units'                                            :'m/s'}
    lev2_atts['wspd_v_std_mast']         = {'units'                                            :'m/s'}
    lev2_atts['wspd_w_std_mast']         = {'units'                                            :'m/s'}
    lev2_atts['temp_acoustic_std_mast']  = {'units'                                            :'deg C'}

    lev2_atts['skin_temp_surface']       = {'units'                                            :'deg C'}
    lev2_atts['down_long_hemisp']        = {'units'                                            :'W/m2'}
    lev2_atts['down_short_hemisp']       = {'units'                                            :'W/m2'}
    lev2_atts['up_long_hemisp']          = {'units'                                            :'W/m2'}
    lev2_atts['up_short_hemisp']         = {'units'                                            :'W/m2'}
    lev2_atts['net_radiation']           = {'units'                                            :'W/m2'}

    
    # add the other important things to the data variable NetCDF attributes
    # #########################################################################################################
    lev2_atts['lat_tower']               .update({    'long_name'                              :'latitude from gps at the tower',
                                                      'cf_name'                                :'latitude',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'GPRMC, GPGGA, GPGZDA',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})
 
    lev2_atts['lon_tower']               .update({    'long_name'                              : 'longitude from gps at the tower',
                                                      'cf_name'                                : 'longitude',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'$GPRMC, $GPGGA, GPGZDA',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['heading_tower']           .update({    'long_name'                              :'heading from gps at the tower',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'$HEHDT',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['lat_mast']                .update({    'long_name'                              :'latitude from gps at the mast',
                                                      'cf_name'                                :'latitude',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'GPRMC, GPGGA, GPGZDA',
                                                      'height'                                 :'N/A',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['lon_mast']                .update({    'long_name'                              : 'longitude from gps at the mast',
                                                      'cf_name'                                : 'longitude',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'$GPRMC, $GPGGA, GPGZDA',
                                                      'height'                                 :'N/A',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['heading_mast']            .update({    'long_name'                              :'heading from gps at the mast',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'$HEHDT',
                                                      'height'                                 :'N/A',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 
    
    lev2_atts['zenith_true']             .update({    'long_name'                              :'true solar zenith angle',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'Reda and Andreas, Solar position algorithm for solar radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})
    
    lev2_atts['zenith_apparent']         .update({    'long_name'                              :'estimated apprarent solar zenith angle due to atmospheric refraction',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'Reda and Andreas, Solar position algorithm for solar radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})
    
    lev2_atts['azimuth']                 .update({    'long_name'                              :'apprarent solar azimuth angle',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102',
                                                      'methods'                                :'Reda and Andreas, Solar position algorithm for solar radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})
    
    lev2_atts['ship_bearing']            .update({    'long_name'                              :'absolute bearing (rel. to true north) of ship from the position of the tower',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102 & Polarstern Leica GPS',
                                                      'methods'                                :'',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,})
    
    lev2_atts['ship_distance']           .update({    'long_name'                              :'distance between the ship and the tower',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hemisphere V102 & Polarstern Leica GPS',
                                                      'methods'                                :'',
                                                      'height'                                 :'N/A',
                                                      'location'                               : bottom_location_string,})  

    lev2_atts['sr50_dist']               .update({    'long_name'                              :'distance to surface from SR50; temperature compensation correction applied',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Campbell Scientific SR50A',
                                                      'methods'                                :'unheated, temperature correction applied',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_2m']                 .update({    'long_name'                              :'temperature',
                                                      'cf_name'                                :'air_temperature',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_6m']                 .update({    'long_name'                              :'temperature',
                                                      'cf_name'                                :'air_temperature',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_10m']                .update({    'long_name'                              :'temperature',
                                                      'cf_name'                                :'air_emperature',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_mast']               .update({    'long_name'                              :'temperature',
                                                      'cf_name'                                :'air_temperature',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'digitally polled from instument',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['dew_point_2m']            .update({    'long_name'                              :'dewpoint',
                                                      'cf_name'                                :'dew_point_temperature',
                                                      'instrument'                             :'Vaisala PTU300',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['dew_point_6m']            .update({    'long_name'                              :'dewpoint',
                                                      'cf_name'                                :'dew_point_temperature',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['dew_point_10m']           .update({    'long_name'                              :'dewpoint',
                                                      'cf_name'                                :'dew_point_temperature',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['dew_point_mast']          .update({    'long_name'                              :'dewpoint',
                                                      'cf_name'                                :'dew_point_temperatre',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'digitally polled from instument',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['rh_2m']                   .update({    'long_name'                              :'relative humidity wrt water',
                                                      'cf_name'                                :'relative_humidity',
                                                      'instrument'                             :'Vaisala PTU300',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['rh_6m']                   .update({    'long_name'                              :'relative humidity wrt water',
                                                      'cf_name'                                :'relative humidity',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['rh_10m']                  .update({    'long_name'                              :'relative humidity wrt water',
                                                      'cf_name'                                :'relative humidity',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['rh_mast']                 .update({    'long_name'                              :'relative humidity wrt water',
                                                      'cf_name'                                :'relative humidity',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'digitally polled from instument',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['atmos_pressure_2m']       .update({    'long_name'                              :'air pressure at 2m',
                                                      'cf_name'                                :'air_pressure',
                                                      'instrument'                             :'Vaisala PTU 300',
                                                      'methods'                                :'digitally polled from instument',
                                                      'location'                               : mast_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['atmos_pressure_mast']     .update({    'long_name'                              :'air pressure',
                                                      'cf_name'                                :'air_pressure',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'digitally polled from instument',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['brightness_temp_surface'] .update({    'long_name'                              :'Apogee IRT target 8-14 micron brightness temperature.',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Apogee SI-4H1-SS IRT',
                                                      'methods'                                :'digitally polled from instument. No emmisivity correction. No correction for reflected incident.',
                                                      'height'                                 :'surface',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['subsurface_heat_flux_A']  .update({    'long_name'                              :'conductive flux from plate A, defined positive upward',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hukseflux HFP01',
                                                      'methods'                                :'Sensitivity 63.00/1000 [mV/(W/m2)]',
                                                      'height'                                 :'subsurface, variable',
                                                      'location'                               :'10m south of tower at met city',
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['subsurface_heat_flux_B']  .update({    'long_name'                              :'conductive flux from plate B, defined positive upward',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Hukseflux HFP01',
                                                      'methods'                                :'Sensitivity 63.91/1000 [mV/(W/m2)]',
                                                      'height'                                 :'subsurface, variable',
                                                      'location'                               :'under Apogee and SR50 at tower base',
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['snow_depth']              .update({    'long_name'                              :'snow depth near tower base',
                                                      'cf_name'                                :'surface_snow_thickness',
                                                      'instrument'                             :'Hukseflux HFP01',
                                                      'methods'                                :'derived snow depth from temperature-corrected SR50 distance values based on initialization 10/27/19. footprint nominally 0.47 m radius.',
                                                      'height'                                 :'',
                                                      'location'                               :'at base of tower under SR50',
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['mixing_ratio_2m']         .update({    'long_name'                              :'mixing ratio derived using T/P/RH from HMT',
                                                      'cf_name'                                :'humidity_mixing_ratio',
                                                      'instrument'                             :'Vaisala PTU300',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['mixing_ratio_6m']         .update({    'long_name'                              :'mixing ratio derived using T/P/RH from HMT',
                                                      'cf_name'                                :'humidity_mixing_ratio',
                                                      'instrument'                             :'Vaisala PTU300',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['mixing_ratio_10m']        .update({    'long_name'                              :'mixing ratio derived using T/P/RH from HMT',
                                                      'cf_name'                                :'humidity_mixing_ratio',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['mixing_ratio_mast']       .update({    'long_name'                              :'mixing ratio derived from WXT',
                                                      'cf_name'                                :'humidity_mixing_ratio',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['rhi_2m']                  .update({    'long_name'                              :'ice RH derived using T/P/RH',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala PTU300',
                                                      'methods'                                :'calculated from measured variables following Hyland & Wexler (1983)',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['rhi_6m']                  .update({    'long_name'                              :'ice RH derived using T/P/RH',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'calculated from measured variables following Hyland & Wexler (1983)',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['rhi_10m']                 .update({    'long_name'                              :'ice RH derived using T/P/RH',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'calculated from measured variables following Hyland & Wexler (1983)',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['rhi_mast']                .update({    'long_name'                              :'ice RH derived using T/P/RH',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'calculated from measured variables following Hyland & Wexler (1983)',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['vapor_pressure_2m']       .update({    'long_name'                              :'vapor pressure',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala PTU300',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['vapor_pressure_6m']       .update({    'long_name'                              :'vapor pressure',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['vapor_pressure_10m']      .update({    'long_name'                              :'vapor pressure',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala HMT330',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['vapor_pressure_mast']     .update({    'long_name'                              :'vapor pressure',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Vaisala WXT530',
                                                      'methods'                                :'calculated from measured variables following Wexler (1976)',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['wspd_vec_mean_2m']        .update({    'long_name'                              :'average metek wind speed',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_vec_mean_6m']        .update({    'long_name'                              :'average metek wind speed',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_vec_mean_10m']       .update({    'long_name'                              :'average metek wind speed',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_vec_mean_mast']      .update({    'long_name'                              :'average metek wind speed',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 


    lev2_atts['wdir_vec_mean_2m']        .update({    'long_name'                              :'average metek wind direction',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wdir_vec_mean_6m']        .update({    'long_name'                              :'average metek wind direction',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wdir_vec_mean_10m']       .update({    'long_name'                              :'average metek wind direction',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wdir_vec_mean_mast']      .update({    'long_name'                              :'average metek wind direction',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'derived from horizontal wind components after coordinate transformation from body to earth reference frame',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 


    lev2_atts['h2o_licor']               .update({    'long_name'                              :'Licor water vapor molar density',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, source data reported at 20 Hz',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['co2_licor']               .update({    'long_name'                              :'Licor CO2 gas molar density',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'open-path optical gas analyzer, source data reported at 20 Hz',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_licor']              .update({    'long_name'                              :'temperature',
                                                      'cf_name'                                :'air_temperature',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'thermistor positioned along strut of open-path optical gas analyzer, source data reported at 20 Hz',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['pressure_licor']          .update({    'long_name'                              :'Licor pressure',
                                                      'cf_name'                                :'air_pressure',
                                                      'instrument'                             :'Licor 7500-DS',
                                                      'methods'                                :'pressure sensor located in electronics box. source data reported at 20 Hz',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_mean_2m']          .update({    'long_name'                              :'Metek u-component',
                                                      'cf_name'                                :'eastward_wind',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_mean_6m']          .update({    'long_name'                              :'Metek u-component',
                                                      'cf_name'                                :'eastward_wind',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_mean_10m']         .update({    'long_name'                              :'Metek u-component',
                                                      'cf_name'                                :'eastward_wind',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_mean_mast']        .update({    'long_name'                              :'Metek u-component',
                                                      'cf_name'                                :'eastward_wind',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 

    lev2_atts['wspd_v_mean_2m']          .update({    'long_name'                              :'Metek v-component',
                                                      'cf_name'                                :'northward_wind',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_v_mean_6m']          .update({    'long_name'                              :'Metek v-component',
                                                      'cf_name'                                :'northward_wind',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_v_mean_10m']         .update({    'long_name'                              :'Metek v-component',
                                                      'cf_name'                                :'northward_wind',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_v_mean_mast']        .update({    'long_name'                              :'Metek v-component',
                                                      'cf_name'                                :'northward_wind',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 


    lev2_atts['wspd_w_mean_2m']          .update({    'long_name'                              :'Metek w-component',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_w_mean_6m']          .update({    'long_name'                              :'Metek w-component',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'height'                                 :'6 m',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_w_mean_10m']         .update({    'long_name'                              :'Metek w-component',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_w_mean_mast']        .update({    'long_name'                              :'Metek w-component',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['temp_acoustic_mean_2m']   .update({    'long_name'                              :'Metek sonic temperature',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_acoustic_mean_6m']   .update({    'long_name'                              :'Metek sonic temperature',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_acoustic_mean_10m']  .update({    'long_name'                              :'Metek sonic temperature',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_acoustic_mean_mast'] .update({    'long_name'                              :'Metek sonic temperature',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['wspd_u_std_2m']           .update({    'long_name'                              :'u metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_v_std_2m']           .update({    'long_name'                              :'v metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_w_std_2m']           .update({    'long_name'                              :'w metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_acoustic_std_2m']    .update({    'long_name'                              :'T metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'location'                               : bottom_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_std_6m']           .update({    'long_name'                              :'u metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_v_std_6m']           .update({    'long_name'                              :'v metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_w_std_6m']           .update({    'long_name'                              :'w metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_acoustic_std_6m']    .update({    'long_name'                              :'T metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'location'                               : middle_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_std_10m']          .update({    'long_name'                              :'u metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_v_std_10m']          .update({    'long_name'                              :'v metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_w_std_10m']          .update({    'long_name'                              :'w metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['temp_acoustic_std_10m']   .update({    'long_name'                              :'T metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek uSonic-Cage MP sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'location'                               : top_location_string,
                                                      'platform'                               : tower_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : flux_source,
                                                      'funding_sources'                        : flux_funding,})

    lev2_atts['wspd_u_std_mast']         .update({    'long_name'                              :'u metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'u defined positive west-to-east',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['wspd_v_std_mast']         .update({    'long_name'                              :'v metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'v defined positive south-to-north',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['wspd_w_std_mast']         .update({    'long_name'                              :'w metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'w defined positive up',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['temp_acoustic_std_mast']  .update({    'long_name'                              :'T metek obs standard deviation',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'Metek USA-1 sonic anemometer',
                                                      'methods'                                :'this is an acoustic temperature, not a thermodynamic temperature',
                                                      'platform'                               : mast_platform,
                                                      'data_provenance'                        : flux_slow_provenance,
                                                      'measurement_source'                     : mast_source,
                                                      'funding_sources'                        : mast_funding,
                                                      'location'                               : mast_location_string,}) 
 

    lev2_atts['skin_temp_surface']       .update({    'long_name'                              :'surface radiometric skin temperature assummed emissivity, corrected for IR reflection',
                                                      'cf_name'                                :'',
                                                      'instrument'                             :'PIR LWu, LWd',
                                                      'methods'                                :'Eq.(2.2) Persson et al. (2002) https://www.doi.org/10.1029/2000JC000705; emis = 0.985',
                                                      'height'                                 :'surface',
                                                      'platform'                               : radiation_platform,
                                                      'data_provenance'                        : radiation_provenance,
                                                      'measurement_source'                     : radiation_source,
                                                      'funding_sources'                        : radiation_funding,
                                                      'location'                               : arm_location_string,})

    lev2_atts['down_long_hemisp']        .update({    'long_name'                              :'net downward longwave flux',
                                                      'cf_name'                                :'surface_net_downward_longwave_flux',
                                                      'instrument'                             :'Eppley PIR',
                                                      'methods'                                :'hemispheric longwave radiation',
                                                      'height'                                 :'3 m nominal',
                                                      'platform'                               : radiation_platform,
                                                      'data_provenance'                        : radiation_provenance,
                                                      'measurement_source'                     : radiation_source,
                                                      'funding_sources'                        : radiation_funding,
                                                      'location'                               : arm_location_string,})

    lev2_atts['down_short_hemisp']       .update({    'long_name'                              :'net downward shortwave flux',
                                                      'cf_name'                                :'surface_net_downward_shortwave_flux',
                                                      'instrument'                             :'Eppley PSP',
                                                      'methods'                                :'hemispheric shortwave radiation',
                                                      'height'                                 :'3 m nominal',
                                                      'platform'                               : radiation_platform,
                                                      'data_provenance'                        : radiation_provenance,
                                                      'measurement_source'                     : radiation_source,
                                                      'funding_sources'                        : radiation_funding,
                                                      'location'                               : arm_location_string,})

    lev2_atts['up_long_hemisp']          .update({    'long_name'                              :'net upward longwave flux',
                                                      'cf_name'                                :'surface_net_upward_longwave_flux',
                                                      'instrument'                             :'Eppley PIR',
                                                      'methods'                                :'hemispheric longwave radiation',
                                                      'height'                                 :'1.5 m nominal',
                                                      'platform'                               : radiation_platform,
                                                      'data_provenance'                        : radiation_provenance,
                                                      'measurement_source'                     : radiation_source,
                                                      'funding_sources'                        : radiation_funding,
                                                      'location'                               : arm_location_string,})

    lev2_atts['up_short_hemisp']         .update({    'long_name'                              :'net upward shortwave flux',
                                                      'cf_name'                                :'surface_net_upward_shortwave_flux',
                                                      'instrument'                             :'Eppley PSP',
                                                      'methods'                                :'hemispheric shortwave radiation',
                                                      'height'                                 :'1.5 m nominal',
                                                      'platform'                               : radiation_platform,
                                                      'data_provenance'                        : radiation_provenance,
                                                      'measurement_source'                     : radiation_source,
                                                      'funding_sources'                        : radiation_funding,
                                                      'location'                               : arm_location_string,})

    lev2_atts['net_radiation']           .update({    'long_name'                              :'cumulative surface radiative flux',
                                                      'cf_name'                                :'surface_net_radiative_flux',
                                                      'instrument'                             :'PSP and PIR radiometers',
                                                      'methods'                                :'combined hemispheric radiation measurements',
                                                      'platform'                               : radiation_platform,
                                                      'data_provenance'                        : radiation_provenance,
                                                      'measurement_source'                     : radiation_source,
                                                      'funding_sources'                        : radiation_funding,
                                                      'location'                               : arm_location_string,})

    lev2_atts['lat_tower_qc']               = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['lon_tower_qc']               = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['heading_tower_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['heading_mast_qc']            = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['lat_mast_qc']                = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['lon_mast_qc']                = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['zenith_true_qc']             = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['zenith_apparent_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['azimuth_qc']                 = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['ship_bearing_qc']            = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['ship_distance_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['sr50_dist_qc']               = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_2m_qc']                 = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_6m_qc']                 = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_10m_qc']                = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_mast_qc']               = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['dew_point_2m_qc']            = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['dew_point_6m_qc']            = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['dew_point_10m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['dew_point_mast_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rh_2m_qc']                   = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rh_6m_qc']                   = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rh_10m_qc']                  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rh_mast_qc']                 = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['atmos_pressure_2m_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['atmos_pressure_mast_qc']     = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['brightness_temp_surface_qc'] = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['subsurface_heat_flux_A_qc']  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['subsurface_heat_flux_B_qc']  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['snow_depth_qc']              = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['mixing_ratio_2m_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['mixing_ratio_6m_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['mixing_ratio_10m_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['mixing_ratio_mast_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rhi_2m_qc']                  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rhi_6m_qc']                  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rhi_10m_qc']                 = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['rhi_mast_qc']                = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['vapor_pressure_2m_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['vapor_pressure_6m_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['vapor_pressure_10m_qc']      = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['vapor_pressure_mast_qc']     = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_vec_mean_2m_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_vec_mean_6m_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_vec_mean_10m_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_vec_mean_mast_qc']      = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wdir_vec_mean_2m_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wdir_vec_mean_6m_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wdir_vec_mean_10m_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wdir_vec_mean_mast_qc']      = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['h2o_licor_qc']               = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['co2_licor_qc']               = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_licor_qc']              = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['pressure_licor_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_mean_2m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_mean_6m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_mean_10m_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_mean_mast_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_mean_2m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_mean_6m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_mean_10m_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_mean_mast_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_mean_2m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_mean_6m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_mean_10m_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_mean_mast_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_mean_2m_qc']   = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_mean_6m_qc']   = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_mean_10m_qc']  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_mean_mast_qc'] = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_std_2m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_std_2m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_std_2m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_std_2m_qc']    = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_std_6m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_std_6m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_std_6m_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_std_6m_qc']    = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_std_10m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_std_10m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_std_10m_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_std_10m_qc']   = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_u_std_mast_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_v_std_mast_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['wspd_w_std_mast_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['temp_acoustic_std_mast_qc']  = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['skin_temp_surface_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['down_long_hemisp_qc']        = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['down_short_hemisp_qc']       = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['up_long_hemisp_qc']          = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['up_short_hemisp_qc']         = {'long_name'                              :'QC flag integer indicating data quality'}    
    lev2_atts['net_radiation_qc']           = {'long_name'                              :'QC flag integer indicating data quality'}    

    return lev2_atts, list(lev2_atts.keys()).copy() 

def define_turb_variables(): 

    # these are the installation heights recorded.
    # it is a nominal height because the surface height changed in time
    
    licor_location ='first level on flux tower'
    bottom_location_string ='first level on flux tower'
    middle_location_string ='second level on flux tower'
    top_location_string    ='third level on flux tower'
    mast_location_string   ='top of radio mast'

    # platform
    tower_platform     = "10-m Met Tower"
    mast_platform      = "met Mast"
    
    # data_provenance 
    flux_slow_provenance = "Based on data from the mosflxtowerslow.level1 datastream with doi  :xxxxxxxx" 
    flux_fast_provenance = "Based on data from the mosflxtowerfast.level1 datastream with doi  :xxxxxxxx" 
 
    # measurement_source
    flux_source      = "CIRES, University of Colorado / NOAA atmospheric surface flux team"
    mast_source      = "School of Earth and Environment, University of Leeds" 

    # funding_sources
    flux_funding      = "National Science Foundation OPP1724551 and NOAA Physical Science Laboratory"
    mast_funding      = "UK Natural Environment Research Council"

    turb_atts = OrderedDict()

    turb_atts['Hs_2m']                     = {'units' :'W/m2'}
    turb_atts['Hs_6m']                     = {'units' :'W/m2'}
    turb_atts['Hs_10m']                    = {'units' :'W/m2'}
    turb_atts['Hs_mast']                   = {'units' :'W/m2'}
    turb_atts['Hl']                        = {'units' :'W/m2'}
    turb_atts['Hl_Webb']                   = {'units' :'W/m2'}
    turb_atts['CO2_flux']                  = {'units' :'mg*m^-2*s^-1'}
    turb_atts['CO2_flux_Webb']             = {'units' :'mg*m^-2*s^-1'}
    turb_atts['Cd_2m']                     = {'units' :'dimensionless'}
    turb_atts['Cd_6m']                     = {'units' :'dimensionless'}
    turb_atts['Cd_10m']                    = {'units' :'dimensionless'}
    turb_atts['Cd_mast']                   = {'units' :'dimensionless'}
    turb_atts['ustar_2m']                  = {'units' :'m/s'}
    turb_atts['ustar_6m']                  = {'units' :'m/s'}
    turb_atts['ustar_10m']                 = {'units' :'m/s'}
    turb_atts['ustar_mast']                = {'units' :'m/s'}
    turb_atts['Tstar_2m']                  = {'units' :'degC'}
    turb_atts['Tstar_6m']                  = {'units' :'degC'}
    turb_atts['Tstar_10m']                 = {'units' :'degC'}
    turb_atts['Tstar_mast']                = {'units' :'degC'}
    turb_atts['zeta_level_n_2m']           = {'units' :'dimensionless'}
    turb_atts['zeta_level_n_6m']           = {'units' :'dimensionless'}
    turb_atts['zeta_level_n_10m']          = {'units' :'dimensionless'}
    turb_atts['zeta_level_n_mast']         = {'units' :'dimensionless'}
    turb_atts['wu_csp_2m']                 = {'units' :'m^2/s^2'}
    turb_atts['wu_csp_6m']                 = {'units' :'m^2/s^2'}
    turb_atts['wu_csp_10m']                = {'units' :'m^2/s^2'}
    turb_atts['wu_csp_mast']               = {'units' :'m^2/s^2'}
    turb_atts['wv_csp_2m']                 = {'units' :'m^2/s^2'}
    turb_atts['wv_csp_6m']                 = {'units' :'m^2/s^2'}
    turb_atts['wv_csp_10m']                = {'units' :'m^2/s^2'}
    turb_atts['wv_csp_mast']               = {'units' :'m^2/s^2'}
    turb_atts['uv_csp_2m']                 = {'units' :'m^2/s^2'}
    turb_atts['uv_csp_6m']                 = {'units' :'m^2/s^2'}
    turb_atts['uv_csp_10m']                = {'units' :'m^2/s^2'}
    turb_atts['uv_csp_mast']               = {'units' :'m^2/s^2'}
    turb_atts['wT_csp_2m']                 = {'units' :'degC*m/s'}
    turb_atts['wT_csp_6m']                 = {'units' :'degC*m/s'}
    turb_atts['wT_csp_10m']                = {'units' :'degC*m/s'}
    turb_atts['wT_csp_mast']               = {'units' :'degC*m/s'}
    turb_atts['uT_csp_2m']                 = {'units' :'degC*m/s'}
    turb_atts['uT_csp_6m']                 = {'units' :'degC*m/s'}
    turb_atts['uT_csp_10m']                = {'units' :'degC*m/s'}
    turb_atts['uT_csp_mast']               = {'units' :'degC*m/s'}
    turb_atts['vT_csp_2m']                 = {'units' :'degC*m/s'}
    turb_atts['vT_csp_6m']                 = {'units' :'degC*m/s'}
    turb_atts['vT_csp_10m']                = {'units' :'degC*m/s'}
    turb_atts['vT_csp_mast']               = {'units' :'degC*m/s'}  
    turb_atts['wq_csp']                    = {'units' :'m/s*kg/m3'}
    turb_atts['uq_csp']                    = {'units' :'m/s*kg/m3'}
    turb_atts['vq_csp']                    = {'units' :'m/s*kg/m3'}
    turb_atts['wc_csp']                    = {'units' :'m*s^-1*mg*m^-2*s^-1'}
    turb_atts['uc_csp']                    = {'units' :'m*s^-1*mg*m^-2*s^-1'}
    turb_atts['vc_csp']                    = {'units' :'m*s^-1*mg*m^-2*s^-1'}
    turb_atts['phi_u_2m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_u_6m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_u_10m']                = {'units'  :'dimensionless'}
    turb_atts['phi_u_mast']               = {'units'  :'dimensionless'}
    turb_atts['phi_v_2m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_v_6m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_v_10m']                = {'units'  :'dimensionless'}
    turb_atts['phi_v_mast']               = {'units'  :'dimensionless'}
    turb_atts['phi_w_2m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_w_6m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_w_10m']                = {'units'  :'dimensionless'}
    turb_atts['phi_w_mast']               = {'units'  :'dimensionless'}
    turb_atts['phi_T_2m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_T_6m']                 = {'units'  :'dimensionless'}
    turb_atts['phi_T_10m']                = {'units'  :'dimensionless'}
    turb_atts['phi_T_mast']               = {'units'  :'dimensionless'}
    turb_atts['phi_uT_2m']                = {'units'  :'dimensionless'}
    turb_atts['phi_uT_6m']                = {'units'  :'dimensionless'}
    turb_atts['phi_uT_10m']               = {'units'  :'dimensionless'}
    turb_atts['phi_uT_mast']              = {'units'  :'dimensionless'}
    turb_atts['epsilon_u_2m']             = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_u_6m']             = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_u_10m']            = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_u_mast']           = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_v_2m']             = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_v_6m']             = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_v_10m']            = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_v_mast']           = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_w_2m']             = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_w_6m']             = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_w_10m']            = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_w_mast']           = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_2m']               = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_6m']               = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_10m']              = {'units'  :'m^2/s^3'}
    turb_atts['epsilon_mast']             = {'units'  :'m^2/s^3'}
    turb_atts['Phi_epsilon_2m']           = {'units'  :'dimensionless'}
    turb_atts['Phi_epsilon_6m']           = {'units'  :'dimensionless'}
    turb_atts['Phi_epsilon_10m']          = {'units'  :'dimensionless'}
    turb_atts['Phi_epsilon_mast']         = {'units'  :'dimensionless'}  
    turb_atts['nSu_2m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSu_6m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSu_10m']                  = {'units'  :'Power/Hz'}
    turb_atts['nSu_mast']                 = {'units'  :'Power/Hz'}
    turb_atts['nSv_2m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSv_6m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSv_10m']                  = {'units'  :'Power/Hz'}
    turb_atts['nSv_mast']                 = {'units'  :'Power/Hz'}
    turb_atts['nSw_2m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSw_6m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSw_10m']                  = {'units'  :'Power/Hz'}
    turb_atts['nSw_mast']                 = {'units'  :'Power/Hz'}
    turb_atts['nSt_2m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSt_6m']                   = {'units'  :'Power/Hz'}
    turb_atts['nSt_10m']                  = {'units'  :'Power/Hz'}
    turb_atts['nSt_mast']                 = {'units'  :'Power/Hz'}
    turb_atts['nSq']                      = {'units'  :'Power/Hz'}
    turb_atts['nSc']                      = {'units'  :'Power/Hz'}    
    turb_atts['Nt_2m']                    = {'units'  :'degC^2/s'}
    turb_atts['Nt_6m']                    = {'units'  :'degC^2/s'}
    turb_atts['Nt_10m']                   = {'units'  :'degC^2/s'}
    turb_atts['Nt_mast']                  = {'units'  :'degC^2/s'}
    turb_atts['Phi_Nt_2m']                = {'units'  :'dimensionless'}
    turb_atts['Phi_Nt_6m']                = {'units'  :'dimensionless'}
    turb_atts['Phi_Nt_10m']               = {'units'  :'dimensionless'}
    turb_atts['Phi_Nt_mast']              = {'units'  :'dimensionless'}
    turb_atts['Phix_2m']                  = {'units'  :'deg'}
    turb_atts['Phix_6m']                  = {'units'  :'deg'}
    turb_atts['Phix_10m']                 = {'units'  :'deg'}
    turb_atts['Phix_mast']                = {'units'  :'deg'}
    turb_atts['DeltaU_2m']                = {'units'  :'m/s'}
    turb_atts['DeltaU_6m']                = {'units'  :'m/s'}
    turb_atts['DeltaU_10m']               = {'units'  :'m/s'}
    turb_atts['DeltaU_mast']              = {'units'  :'m/s'}
    turb_atts['DeltaV_2m']                = {'units'  :'m/s'}
    turb_atts['DeltaV_6m']                = {'units'  :'m/s'}
    turb_atts['DeltaV_10m']               = {'units'  :'m/s'}
    turb_atts['DeltaV_mast']              = {'units'  :'m/s'}
    turb_atts['DeltaT_2m']                = {'units'  :'degC'}
    turb_atts['DeltaT_6m']                = {'units'  :'degC'}
    turb_atts['DeltaT_10m']               = {'units'  :'degC'}
    turb_atts['DeltaT_mast']              = {'units'  :'degC'}
    turb_atts['Deltaq']                   = {'units'  :'mg/m3'}
    turb_atts['Deltac']                   = {'units'  :'unitless'}
    turb_atts['Kurt_u_2m']                = {'units'  :'unitless'}
    turb_atts['Kurt_u_6m']                = {'units'  :'unitless'}
    turb_atts['Kurt_u_10m']               = {'units'  :'unitless'}
    turb_atts['Kurt_u_mast']              = {'units'  :'unitless'}
    turb_atts['Kurt_v_2m']                = {'units'  :'unitless'}
    turb_atts['Kurt_v_6m']                = {'units'  :'unitless'}
    turb_atts['Kurt_v_10m']               = {'units'  :'unitless'}
    turb_atts['Kurt_v_mast']              = {'units'  :'unitless'}
    turb_atts['Kurt_w_2m']                = {'units'  :'unitless'}
    turb_atts['Kurt_w_6m']                = {'units'  :'unitless'}
    turb_atts['Kurt_w_10m']               = {'units'  :'unitless'}
    turb_atts['Kurt_w_mast']              = {'units'  :'unitless'}
    turb_atts['Kurt_T_2m']                = {'units'  :'unitless'}
    turb_atts['Kurt_T_6m']                = {'units'  :'unitless'}
    turb_atts['Kurt_T_10m']               = {'units'  :'unitless'}
    turb_atts['Kurt_T_mast']              = {'units'  :'unitless'}
    turb_atts['Kurt_q']                   = {'units'  :'unitless'}
    turb_atts['Kurt_c']                   = {'units'  :'unitless'}
    turb_atts['Kurt_uw_2m']               = {'units'  :'unitless'}
    turb_atts['Kurt_uw_6m']               = {'units'  :'unitless'}
    turb_atts['Kurt_uw_10m']              = {'units'  :'unitless'}
    turb_atts['Kurt_uw_mast']             = {'units'  :'unitless'}
    turb_atts['Kurt_vw_2m']               = {'units'  :'unitless'}
    turb_atts['Kurt_vw_6m']               = {'units'  :'unitless'}
    turb_atts['Kurt_vw_10m']              = {'units'  :'unitless'}
    turb_atts['Kurt_vw_mast']             = {'units'  :'unitless'}
    turb_atts['Kurt_wT_2m']               = {'units'  :'unitless'}
    turb_atts['Kurt_wT_6m']               = {'units'  :'unitless'}
    turb_atts['Kurt_wT_10m']              = {'units'  :'unitless'}
    turb_atts['Kurt_wT_mast']             = {'units'  :'unitless'}
    turb_atts['Kurt_wq']                  = {'units'  :'unitless'}
    turb_atts['Kurt_wc']                  = {'units'  :'unitless'}
    turb_atts['Kurt_uT_2m']               = {'units'  :'unitless'}
    turb_atts['Kurt_uT_6m']               = {'units'  :'unitless'}
    turb_atts['Kurt_uT_10m']              = {'units'  :'unitless'}
    turb_atts['Kurt_uT_mast']             = {'units'  :'unitless'}
    turb_atts['Kurt_uq']                  = {'units'  :'unitless'}
    turb_atts['Kurt_uc']                  = {'units'  :'unitless'}
    turb_atts['Skew_u_2m']                = {'units'  :'unitless'}
    turb_atts['Skew_u_6m']                = {'units'  :'unitless'}
    turb_atts['Skew_u_10m']               = {'units'  :'unitless'}
    turb_atts['Skew_u_mast']              = {'units'  :'unitless'}
    turb_atts['Skew_v_2m']                = {'units'  :'unitless'}
    turb_atts['Skew_v_6m']                = {'units'  :'unitless'}
    turb_atts['Skew_v_10m']               = {'units'  :'unitless'}
    turb_atts['Skew_v_mast']              = {'units'  :'unitless'}
    turb_atts['Skew_w_2m']                = {'units'  :'unitless'}
    turb_atts['Skew_w_6m']                = {'units'  :'unitless'}
    turb_atts['Skew_w_10m']               = {'units'  :'unitless'}
    turb_atts['Skew_w_mast']              = {'units'  :'unitless'}
    turb_atts['Skew_T_2m']                = {'units'  :'unitless'}
    turb_atts['Skew_T_6m']                = {'units'  :'unitless'}
    turb_atts['Skew_T_10m']               = {'units'  :'unitless'}
    turb_atts['Skew_T_mast']              = {'units'  :'unitless'}
    turb_atts['Skew_q']                   = {'units'  :'unitless'}
    turb_atts['Skew_c']                   = {'units'  :'unitless'}
    turb_atts['Skew_uw_2m']               = {'units'  :'unitless'}
    turb_atts['Skew_uw_6m']               = {'units'  :'unitless'}
    turb_atts['Skew_uw_10m']              = {'units'  :'unitless'}
    turb_atts['Skew_uw_mast']             = {'units'  :'unitless'}
    turb_atts['Skew_vw_2m']               = {'units'  :'unitless'}
    turb_atts['Skew_vw_6m']               = {'units'  :'unitless'}
    turb_atts['Skew_vw_10m']              = {'units'  :'unitless'}
    turb_atts['Skew_vw_mast']             = {'units'  :'unitless'}
    turb_atts['Skew_wT_2m']               = {'units'  :'unitless'}
    turb_atts['Skew_wT_6m']               = {'units'  :'unitless'}
    turb_atts['Skew_wT_10m']              = {'units'  :'unitless'}
    turb_atts['Skew_wT_mast']             = {'units'  :'unitless'}
    turb_atts['Skew_wq']                  = {'units'  :'unitless'}
    turb_atts['Skew_wc']                  = {'units'  :'unitless'}
    turb_atts['Skew_uT_2m']               = {'units'  :'unitless'}
    turb_atts['Skew_uT_6m']               = {'units'  :'unitless'}
    turb_atts['Skew_uT_10m']              = {'units'  :'unitless'}
    turb_atts['Skew_uT_mast']             = {'units'  :'unitless'}  
    turb_atts['Skew_uq']                  = {'units'  :'unitless'}
    turb_atts['Skew_uc']                  = {'units'  :'unitless'}
    turb_atts['fs']                       = {'units'  :'Hz'}
    turb_atts['sus_2m']                   = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sus_6m']                   = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sus_10m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sus_mast']                 = {'units'  :'(m/s)^2/Hz'}
    turb_atts['svs_2m']                   = {'units'  :'(m/s)^2/Hz'}
    turb_atts['svs_6m']                   = {'units'  :'(m/s)^2/Hz'}
    turb_atts['svs_10m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['svs_mast']                 = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sws_2m']                   = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sws_6m']                   = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sws_10m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sws_mast']                 = {'units'  :'(m/s)^2/Hz'}
    turb_atts['sTs_2m']                   = {'units'  :'degC^2/Hz'}
    turb_atts['sTs_6m']                   = {'units'  :'degC^2/Hz'}
    turb_atts['sTs_10m']                  = {'units'  :'degC^2/Hz'}
    turb_atts['sTs_mast']                 = {'units'  :'degC^2/Hz'}
    turb_atts['sqs']                      = {'units'  :'(kg/m3)/hz'}
    turb_atts['scs']                      = {'units'  :'(mg m^-2 s^-1)^2/Hz'}
    turb_atts['cwus_2m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwus_6m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwus_10m']                 = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwus_mast']                = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwvs_2m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwvs_6m']                  = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwvs_10m']                 = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cwvs_mast']                = {'units'  :'(m/s)^2/Hz'}
    turb_atts['cuvs_2m']                  = {'units'  :'(m/s)^2/Hz'}  
    turb_atts['cuvs_6m']                  = {'units'  :'(m/s)^2/Hz'} 
    turb_atts['cuvs_10m']                 = {'units'  :'(m/s)^2/Hz'} 
    turb_atts['cuvs_mast']                = {'units'  :'(m/s)^2/Hz'} 
    turb_atts['cwTs_2m']                  = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cwTs_6m']                  = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cwTs_10m']                 = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cwTs_mast']                = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cuTs_2m']                  = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cuTs_6m']                  = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cuTs_10m']                 = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cuTs_mast']                = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cvTs_2m']                  = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cvTs_6m']                  = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cvTs_10m']                 = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cvTs_mast']                = {'units'  :'(m/s*degC)/Hz'}
    turb_atts['cwqs']                     = {'units'  :'(m/s*kg/m3)/Hz'}
    turb_atts['cuqs']                     = {'units'  :'(m/s*kg/m3)/Hz'}
    turb_atts['cvqs']                     = {'units'  :'(m/s*kg/m3)/Hz'}  
    turb_atts['cwcs']                     = {'units'  :'(m/s*mg*m^-2*s^-1)/Hz'}
    turb_atts['cucs']                     = {'units'  :'(m/s*mg*m^-2*s^-1)/Hz'}
    turb_atts['cvcs']                     = {'units'  :'(m/s*mg*m^-2*s^-1)/Hz'}  
    turb_atts['bulk_Hs_10m']              = {'units'  :'W/m2'}
    turb_atts['bulk_Hl_10m']              = {'units'  :'W/m2'}
    turb_atts['bulk_Hl_Webb_10m']         = {'units'  :'W/m2'}  
    turb_atts['bulk_tau']                 = {'units'  :'Pa'}
    turb_atts['bulk_z0']                  = {'units'  :'m'}
    turb_atts['bulk_z0t']                 = {'units'  :'m'}
    turb_atts['bulk_z0q']                 = {'units'  :'m'}
    turb_atts['bulk_L']                   = {'units'  :'m'}
    turb_atts['bulk_ustar']               = {'units'  :'m/s'}
    turb_atts['bulk_tstar']               = {'units'  :'K'}
    turb_atts['bulk_qstar']               = {'units'  :'kg/kg'}
    turb_atts['bulk_dter']                = {'units'  :'degC'}
    turb_atts['bulk_dqer']                = {'units'  :'kg/kg'}  
    turb_atts['bulk_Cd_10m']              = {'units'  :'unitless'}
    turb_atts['bulk_Ch_10m']              = {'units'  :'unitless'}                                  
    turb_atts['bulk_Ce_10m']              = {'units'  :'unitless'}
    turb_atts['bulk_Cdn_10m']             = {'units'  :'unitless'}
    turb_atts['bulk_Chn_10m']             = {'units'  :'unitless'}                                  
    turb_atts['bulk_Cen_10m']             = {'units'  :'unitless'}                                        
    turb_atts['bulk_Rr']                  = {'units'  :'unitless'}                                         
    turb_atts['bulk_Rt']                  = {'units'  :'unitless'}  
    turb_atts['bulk_Rq']                  = {'units'  :'unitless'}  

    # Some variables are dimensionless, meaning they are both scaled & unitless and the result is
    # independent of height such that it sounds a little funny to have a var name like
    # MO_dimensionless_param_2_m, but that is the only way to distinguish between the 4
    # calculations. So, for these I added ", calculated from 2 m" or whatever into the long_name.
    # Maybe there is a more clever way way?
    turb_atts['Hs_2m']             .update({ 'long_name'          :'sensible heat flux',
                                             'cf_name'            :'upward_sensible_heat_flux_in_air',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Hs_6m']             .update({ 'long_name'          :'sensible heat flux',
                                             'cf_name'            :'upward_sensible_heat_flux_in_air',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Hs_10m']            .update({ 'long_name'          :'sensible heat flux',
                                             'cf_name'            :'upward_sensible_heat_flux_in_air',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Hs_mast']           .update({ 'long_name'          :'sensible heat flux',
                                             'cf_name'            :'upward_sensible_heat_flux_in_air',
                                             'instrument'         :'Metek USA-1 sonic anemometer',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['Hl']                .update({ 'long_name'          :'latent heat flux',
                                             'cf_name'            :'upward_latent_heat_flux_in_air',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source h2o data was vapor density (g/m3). No WPL correction applied.',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Hl_Webb']           .update({ 'long_name'          :'Latent heat flux with Webb density correction applied',
                                             'cf_name'            :'upward_latent_heat_flux_in_air',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source h2o data was vapor density (g/m3). No WPL correction applied.',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['CO2_flux']          .update({ 'long_name'          :'co2 mass flux',
                                             'cf_name'            :'',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source co2 data was co2 density (mmol/m3). No WPL correction applied.',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
       
    turb_atts['CO2_flux_Webb']     .update({ 'long_name'          :'co2 mass flux with Webb density correction applied',
                                             'cf_name'            :'',
                                             'instrument'         :'Metek uSonic-Cage MP sonic anemometer, Licor 7500 DS',
                                             'methods'            :'source data was 20 Hz samples averged to 10 Hz. Calculatation by eddy covariance using sonic temperature based on integration of the wT-covariance spectrum. Source co2 data was co2 density (mmol/m3). No WPL correction applied.',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
        
    turb_atts['Cd_2m']             .update({ 'long_name'          :'Drag coefficient based on the momentum flux, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Cd_6m']             .update({ 'long_name'          :'Drag coefficient based on the momentum flux, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Cd_10m']            .update({ 'long_name'          :'Drag coefficient based on the momentum flux, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Cd_mast']           .update({ 'long_name'          :'Drag coefficient based on the momentum flux, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['ustar_2m']          .update({ 'long_name'          :'friction velocity (based only on the downstream, uw, stress components)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['ustar_6m']          .update({ 'long_name'          :'friction velocity (based only on the downstream, uw, stress components)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['ustar_10m']         .update({ 'long_name'          :'friction velocity (based only on the downstream, uw, stress components)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['ustar_mast']        .update({ 'long_name'          :'friction velocity (based only on the downstream, uw, stress components)',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Tstar_2m']          .update({ 'long_name'          :'temperature scale',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Tstar_6m']          .update({ 'long_name'          :'temperature scale',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Tstar_10m']         .update({ 'long_name'          :'temperature scale',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Tstar_mast']        .update({ 'long_name'          :'temperature scale',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['zeta_level_n_2m']   .update({ 'long_name'          :'Monin-Obukhov stability parameter, z/L, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['zeta_level_n_6m']   .update({ 'long_name'          :'Monin-Obukhov stability parameter, z/L, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['zeta_level_n_10m']  .update({ 'long_name'          :'Monin-Obukhov stability parameter, z/L, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['zeta_level_n_mast'] .update({ 'long_name'          :'Monin-Obukhov stability parameter, z/L, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['wu_csp_2m']         .update({ 'long_name'          :'wu-covariance based on the wu-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['wu_csp_6m']         .update({ 'long_name'          :'wu-covariance based on the wu-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['wu_csp_10m']        .update({ 'long_name'          :'wu-covariance based on the wu-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['wu_csp_mast']       .update({ 'long_name'          :'wu-covariance based on the wu-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['wv_csp_2m']         .update({ 'long_name'          :'wv-covariance based on the wv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['wv_csp_6m']         .update({ 'long_name'          :'wv-covariance based on the wv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['wv_csp_10m']        .update({ 'long_name'          :'wv-covariance based on the wv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['wv_csp_mast']       .update({ 'long_name'          :'wv-covariance based on the wv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['uv_csp_2m']         .update({ 'long_name'          :'uv-covariance based on the uv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['uv_csp_6m']         .update({ 'long_name'          :'uv-covariance based on the uv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['uv_csp_10m']        .update({ 'long_name'          :'uv-covariance based on the uv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['uv_csp_mast']       .update({ 'long_name'          :'uv-covariance based on the uv-cospectra integration',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['wT_csp_2m']         .update({ 'long_name'          :'wT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['wT_csp_6m']         .update({ 'long_name'          :'wT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['wT_csp_10m']        .update({ 'long_name'          :'wT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['wT_csp_mast']       .update({ 'long_name'          :'wT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['wq_csp']            .update({ 'long_name'          :'wq-covariance, vertical flux of q',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['wc_csp']            .update({ 'long_name'          :'wc-covariance, vertical flux of co2',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['uT_csp_2m']         .update({ 'long_name'          :'uT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['uT_csp_6m']         .update({ 'long_name'          :'uT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['uT_csp_10m']        .update({ 'long_name'          :'uT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['uT_csp_mast']       .update({ 'long_name'          :'uT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['uq_csp']            .update({ 'long_name'          :'uq-covariance, vertical flux of q',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['uc_csp']            .update({ 'long_name'          :'uc-covariance, vertical flux of co2',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['vT_csp_2m']         .update({ 'long_name'          :'vT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['vT_csp_6m']         .update({ 'long_name'          :'vT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['vT_csp_10m']        .update({ 'long_name'          :'vT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['vT_csp_mast']       .update({ 'long_name'          :'vT-covariance, vertical flux of the sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['vq_csp']            .update({ 'long_name'          :'vq-covariance, vertical flux q',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['vc_csp']            .update({ 'long_name'          :'vc-covariance, vertical flux c',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['phi_u_2m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['phi_u_6m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['phi_u_10m']         .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['phi_u_mast']        .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['phi_v_2m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['phi_v_6m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['phi_v_10m']         .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['phi_v_mast']        .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['phi_w_2m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['phi_w_6m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['phi_w_10m']         .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['phi_w_mast']        .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['phi_T_2m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['phi_T_6m']          .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['phi_T_10m']         .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['phi_T_mast']        .update({ 'long_name'          :'MO universal function for the standard deviations, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['phi_uT_2m']         .update({ 'long_name'          :'MO universal function for the horizontal heat flux, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['phi_uT_6m']         .update({ 'long_name'          :'MO universal function for the horizontal heat flux, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['phi_uT_10m']        .update({ 'long_name'          :'MO universal function for the horizontal heat flux, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['phi_uT_mast']       .update({ 'long_name'          :'MO universal function for the horizontal heat flux, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['epsilon_u_2m']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['epsilon_u_6m']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['epsilon_u_10m']     .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['epsilon_u_mast']    .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in u based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['epsilon_v_2m']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['epsilon_v_6m']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['epsilon_v_10m']     .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['epsilon_v_mast']    .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in v based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['epsilon_w_2m']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['epsilon_w_6m']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['epsilon_w_10m']     .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['epsilon_w_mast']    .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy in w based on the energy spectra of the longitudinal velocity component in the inertial subrange',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['epsilon_2m']        .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['epsilon_6m']        .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['epsilon_10m']       .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['epsilon_mast']      .update({ 'long_name'          :'Dissipation rate of the turbulent kinetic energy = median of the values derived from u, v, & w',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Phi_epsilon_2m']    .update({ 'long_name'          :'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Phi_epsilon_6m']    .update({ 'long_name'          :'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Phi_epsilon_10m']   .update({ 'long_name'          :'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Phi_epsilon_mast']  .update({ 'long_name'          :'Monin-Obukhov universal function Phi_epsilon based on the median epsilon, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
   
    turb_atts['nSu_2m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of u',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['nSu_6m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of u',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})
    
    turb_atts['nSu_10m']           .update({ 'long_name'          :'Median spectral slope in the inertial subrange of u',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['nSu_mast']          .update({ 'long_name'          :'Median spectral slope in the inertial subrange of u',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['nSv_2m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of v',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['nSv_6m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of v',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})
    
    turb_atts['nSv_10m']           .update({ 'long_name'          :'Median spectral slope in the inertial subrange of v',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['nSv_mast']          .update({ 'long_name'          :'Median spectral slope in the inertial subrange of v',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['nSw_2m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of w',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['nSw_6m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of w',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})
    
    turb_atts['nSw_10m']           .update({ 'long_name'          :'Median spectral slope in the inertial subrange of w',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['nSw_mast']          .update({ 'long_name'          :'Median spectral slope in the inertial subrange of w',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['nSt_2m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['nSt_6m']            .update({ 'long_name'          :'Median spectral slope in the inertial subrange of sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})
    
    turb_atts['nSt_10m']           .update({ 'long_name'          :'Median spectral slope in the inertial subrange of sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['nSt_mast']          .update({ 'long_name'          :'Median spectral slope in the inertial subrange of sonic temperature',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['nSq']               .update({ 'long_name'          :'Median spectral slope in the inertial subrange of q',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,})
    
    turb_atts['nSc']               .update({ 'long_name'          :'Median spectral slope in the inertial subrange of co2',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,})
    
    turb_atts['Nt_2m']             .update({ 'long_name'          :'The dissipation (destruction) rate for half the temperature variance',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Nt_6m']             .update({ 'long_name'          :'The dissipation (destruction) rate for half the temperature variance',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Nt_10m']            .update({ 'long_name'          :'The dissipation (destruction) rate for half the temperature variance',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Nt_mast']           .update({ 'long_name'          :'The dissipation (destruction) rate for half the temperature variance',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Phi_Nt_2m']         .update({ 'long_name'          :'Monin-Obukhov universal function Phi_Nt, calculated from 2 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Phi_Nt_6m']         .update({ 'long_name'          :'Monin-Obukhov universal function Phi_Nt, calculated from 6 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Phi_Nt_10m']        .update({ 'long_name'          :'Monin-Obukhov universal function Phi_Nt, calculated from 10 m',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Phi_Nt_mast']       .update({ 'long_name'          :'Monin-Obukhov universal function Phi_Nt, calculated from the mast',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Phix_2m']           .update({ 'long_name'          :'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Phix_6m']           .update({ 'long_name'          :'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Phix_10m']          .update({ 'long_name'          :'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Phix_mast']         .update({ 'long_name'          :'Angle of attack. Should be < 15 deg; else a correction should be applied',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['DeltaU_2m']         .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['DeltaU_6m']         .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['DeltaU_10m']        .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['DeltaU_mast']       .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the along-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['DeltaV_2m']         .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['DeltaV_6m']         .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['DeltaV_10m']        .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['DeltaV_mast']       .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the cross-wind component (trend)',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['DeltaT_2m']         .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['DeltaT_6m']         .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['DeltaT_10m']        .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['DeltaT_mast']       .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of the sonic temperature (trend)',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['Deltaq']            .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of q (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['Deltac']            .update({ 'long_name'          :'Stationarity diagnostic: Steadiness of co2 (trend)',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_u_2m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_u_6m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_u_10m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_u_mast']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Kurt_v_2m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_v_6m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_v_10m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_v_mast']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Kurt_w_2m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_w_6m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_w_10m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_w_mast']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Kurt_T_2m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_T_6m']         .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_T_10m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_T_mast']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['Kurt_q']            .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['Kurt_c']            .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_uw_2m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_uw_6m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_uw_10m']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_uw_mast']      .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Kurt_vw_2m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_vw_6m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_vw_10m']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_vw_mast']      .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Kurt_wT_2m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_wT_6m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_wT_10m']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_wT_mast']      .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['Kurt_wq']           .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
        
    turb_atts['Kurt_wc']           .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_uT_2m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Kurt_uT_6m']        .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Kurt_uT_10m']       .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Kurt_uT_mast']      .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['Kurt_uq']           .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['Kurt_uc']           .update({ 'long_name'          :'Kurtosis',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_u_2m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_u_6m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_u_10m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_u_mast']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Skew_v_2m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_v_6m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_v_10m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_v_mast']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Skew_w_2m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_w_6m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_w_10m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_w_mast']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Skew_T_2m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_T_6m']         .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_T_10m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_T_mast']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Skew_q']            .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['Skew_c']            .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['Skew_uw_2m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_uw_6m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_uw_10m']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_uw_mast']      .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Skew_vw_2m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_vw_6m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_vw_10m']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_vw_mast']      .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})

    turb_atts['Skew_wT_2m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_wT_6m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_wT_10m']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_wT_mast']      .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['Skew_wq']           .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
    
    turb_atts['Skew_wc']           .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_uT_2m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['Skew_uT_6m']        .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})

    turb_atts['Skew_uT_10m']       .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['Skew_uT_mast']      .update({ 'long_name'          :'Skewness',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})
    
    turb_atts['fs']                .update({ 'long_name'          :'frequency',
                                             'cf_name'            :'',
                                             'height'             :'n/a',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})
 
    turb_atts['sus_2m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of u wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['sus_6m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of u wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})    
    
    turb_atts['sus_10m']           .update({ 'long_name'          :'smoothed power spectral density (Welch) of u wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 

    turb_atts['sus_mast']          .update({ 'long_name'          :'smoothed power spectral density (Welch) of u wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})         
 
    turb_atts['svs_2m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of v wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['svs_6m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of v wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})    
    
    turb_atts['svs_10m']           .update({ 'long_name'          :'smoothed power spectral density (Welch) of v wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 

    turb_atts['svs_mast']          .update({ 'long_name'          :'smoothed power spectral density (Welch) of v wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})  
    
    turb_atts['sws_2m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of w wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['sws_6m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of w wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})    
    
    turb_atts['sws_10m']           .update({ 'long_name'          :'smoothed power spectral density (Welch) of w wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 

    turb_atts['sws_mast']          .update({ 'long_name'          :'smoothed power spectral density (Welch) of w wind vector on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})  

    turb_atts['sTs_2m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,})

    turb_atts['sTs_6m']            .update({ 'long_name'          :'smoothed power spectral density (Welch) of sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,})    
    
    turb_atts['sTs_10m']           .update({ 'long_name'          :'smoothed power spectral density (Welch) of sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 

    turb_atts['sTs_mast']          .update({ 'long_name'          :'smoothed power spectral density (Welch) of sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,})  

    turb_atts['sqs']               .update({ 'long_name'          :'smoothed power spectral density (Welch) of q on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,})
    
    turb_atts['scs']               .update({ 'long_name'          :'smoothed power spectral density (Welch) of co2 on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,})
    
    turb_atts['cwus_2m']           .update({ 'long_name'          :'smoothed co-spectral density between w and u wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,}) 
    
    turb_atts['cwus_6m']           .update({ 'long_name'          :'smoothed co-spectral density between w and u wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,}) 
    
    turb_atts['cwus_10m']          .update({ 'long_name'          :'smoothed co-spectral density between w and u wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 
    
    turb_atts['cwus_mast']         .update({ 'long_name'          :'smoothed co-spectral density between w and u wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,}) 

    turb_atts['cwvs_2m']           .update({ 'long_name'          :'smoothed co-spectral density between w and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,}) 
    
    turb_atts['cwvs_6m']           .update({ 'long_name'          :'smoothed co-spectral density between w and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,}) 
    
    turb_atts['cwvs_10m']          .update({ 'long_name'          :'smoothed co-spectral density between w and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 
    
    turb_atts['cwvs_mast']         .update({ 'long_name'          :'smoothed co-spectral density between w and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,}) 
    
    turb_atts['cuvs_2m']           .update({ 'long_name'          :'smoothed co-spectral density between u and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,}) 
    
    turb_atts['cuvs_6m']           .update({ 'long_name'          :'smoothed co-spectral density between u and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,}) 
    
    turb_atts['cuvs_10m']          .update({ 'long_name'          :'smoothed co-spectral density between u and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 
    
    turb_atts['cuvs_mast']         .update({ 'long_name'          :'smoothed co-spectral density between u and v wind vectors on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,}) 

    turb_atts['cwTs_2m']           .update({ 'long_name'          :'smoothed co-spectral density between w wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,}) 
    
    turb_atts['cwTs_6m']           .update({ 'long_name'          :'smoothed co-spectral density between w wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,}) 
    
    turb_atts['cwTs_10m']          .update({ 'long_name'          :'smoothed co-spectral density between w wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 
    
    turb_atts['cwTs_mast']         .update({ 'long_name'          :'smoothed co-spectral density between w wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,}) 

    turb_atts['cuTs_2m']           .update({ 'long_name'          :'smoothed co-spectral density between u wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,}) 
    
    turb_atts['cuTs_6m']           .update({ 'long_name'          :'smoothed co-spectral density between u wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,}) 
    
    turb_atts['cuTs_10m']          .update({ 'long_name'          :'smoothed co-spectral density between u wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 
    
    turb_atts['cuTs_mast']         .update({ 'long_name'          :'smoothed co-spectral density between u wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,}) 

    turb_atts['cvTs_2m']           .update({ 'long_name'          :'smoothed co-spectral density between v wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : bottom_location_string,}) 
    
    turb_atts['cvTs_6m']           .update({ 'long_name'          :'smoothed co-spectral density between v wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : middle_location_string,}) 
    
    turb_atts['cvTs_10m']          .update({ 'long_name'          :'smoothed co-spectral density between v wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,}) 
    
    turb_atts['cvTs_mast']         .update({ 'long_name'          :'smoothed co-spectral density between v wind vector and sonic temperature on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : mast_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : mast_source,
                                             'funding_sources'    : mast_funding,
                                             'location'           : mast_location_string,}) 
    
    turb_atts['cwqs']              .update({ 'long_name'          :'smoothed co-spectral density between w wind vector and q on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,}) 
    
    turb_atts['cuqs']              .update({ 'long_name'          :'smoothed co-spectral density between u wind vector and q on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,}) 
    
    turb_atts['cvqs']              .update({ 'long_name'          :'smoothed co-spectral density between v wind vector and q on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,})     
    
    turb_atts['cwcs']              .update({ 'long_name'          :'smoothed co-spectral density between w wind vector and co2 on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,}) 
    
    turb_atts['cucs']              .update({ 'long_name'          :'smoothed co-spectral density between u wind vector and co2 on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,}) 
    
    turb_atts['cvcs']              .update({ 'long_name'          :'smoothed co-spectral density between v wind vector and co2 on frequency, fs',
                                             'cf_name'            :'',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : licor_location,})   

    turb_atts['bulk_Hs_10m']       .update({ 'long_name'          :'sensible heat flux',
                                             'cf_name'            :'upward_sensible_heat_flux_in_air',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['bulk_Hl_10m']       .update({ 'long_name'          :'latent heat flux',
                                             'cf_name'            :'upward_latent_heat_flux_in_air',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['bulk_Hl_Webb_10m']  .update({ 'long_name'          :'Latent heat flux with Webb density correction applied',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm, Webb et al. (1980) https://doi.org/10.1002/qj.49710644707',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   
    
    turb_atts['bulk_tau']          .update({ 'long_name'          :'wind stress',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['bulk_z0']           .update({ 'long_name'          :'roughness length',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['bulk_z0t']          .update({ 'long_name'          :'roughness length, temperature',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['bulk_z0q']          .update({ 'long_name'          :'roughness length, humidity',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})
    
    turb_atts['bulk_L']            .update({ 'long_name'          :'Obukhov length',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})       
        
    turb_atts['bulk_ustar']        .update({ 'long_name'          :'friction velocity (sqrt(momentum flux)), ustar',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   

    turb_atts['bulk_tstar']        .update({ 'long_name'          :'temperature scale, tstar',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   

    turb_atts['bulk_qstar']        .update({ 'long_name'          :'specific humidity scale, qstar',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})       
    
    turb_atts['bulk_dter']         .update({ 'long_name'          :'cool skin temperature difference',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})            

    turb_atts['bulk_dqer']         .update({ 'long_name'          :'cool skin q difference',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})         

    turb_atts['bulk_Cd_10m']       .update({ 'long_name'          :'transfer coefficient for stress',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   

    turb_atts['bulk_Ch_10m']       .update({ 'long_name'          :'transfer coefficient for Hs',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})

    turb_atts['bulk_Ce_10m']       .update({ 'long_name'          :'transfer coefficient for Hl',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   

    turb_atts['bulk_Cdn_10m']      .update({ 'long_name'          :'10 m neutral transfer coefficient for stress',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})       

    turb_atts['bulk_Chn_10m']      .update({ 'long_name'          :'10 m neutral transfer coefficient for Hs',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})       

    turb_atts['bulk_Cen_10m']      .update({ 'long_name'          :'10 m neutral transfer coefficient for Hl',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})       

    turb_atts['bulk_Rr']           .update({ 'long_name'          :'roughness Reynolds number for velocity',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})      
    
    turb_atts['bulk_Rt']           .update({ 'long_name'          :'roughness Reynolds number for temperature',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   

    turb_atts['bulk_Rq']           .update({ 'long_name'          :'roughness Reylnolds numbe for humidityr',
                                             'cf_name'            :'',
                                             'instrument'         :'various',
                                             'methods'            :'Bulk calc. Fairall et al. (1996) https://doi.org/10.1029/95JC03205, Andreas et al. (2004) https://ams.confex.com/ams/7POLAR/techprogram/paper_60666.htm',
                                             'height'             :'10 m',
                                             'platform'           : tower_platform,
                                             'data_provenance'    : flux_fast_provenance,
                                             'measurement_source' : flux_source,
                                             'funding_sources'    : flux_funding,
                                             'location'           : top_location_string,})   
 
    return turb_atts, list(turb_atts.keys()).copy() 

def define_10hz_variables():
 
    licor_location         = 'first level on met city tower'
    bottom_location_string = 'first level on met city tower'
    middle_location_string = 'second level on met city tower'
    top_location_string    = 'third level on met city tower'
    mast_location_string   = 'top of radio mast at met city'
    arm_location_string    = 'top of radio mast at met city'

    # funding_sources
    radiation_funding = "Department of Energy, Office of Science, Biological and Environmental Research Program"
    flux_funding      = "National Science Foundation OPP1724551 and NOAA Physical Science Laboratory"
    mast_funding      = "UK Natural Environment Research Council"

    atts_10hz = OrderedDict()
    
    # units defined here, other properties defined in 'update' call below
    atts_10hz['metek_2m_heatstatus']  = {'units' : 'int'     }
    atts_10hz['metek_2m_u']           = {'units' : 'm/s'     }
    atts_10hz['metek_2m_v']           = {'units' : 'm/s'     }
    atts_10hz['metek_2m_w']           = {'units' : 'm/s'     }
    atts_10hz['metek_2m_T']           = {'units' : 'C'       }
    atts_10hz['metek_2m_hspd']        = {'units' : 'm/s'     }
    atts_10hz['metek_2m_ts']          = {'units' : 'deg'     }
    atts_10hz['metek_2m_incx']        = {'units' : 'deg'     }
    atts_10hz['metek_2m_incy']        = {'units' : 'deg'     }

    atts_10hz['metek_6m_heatstatus']  = {'units' : 'int'     }
    atts_10hz['metek_6m_u']           = {'units' : 'm/s'     }
    atts_10hz['metek_6m_v']           = {'units' : 'm/s'     }
    atts_10hz['metek_6m_w']           = {'units' : 'm/s'     }
    atts_10hz['metek_6m_T']           = {'units' : 'C'       }
    atts_10hz['metek_6m_hspd']        = {'units' : 'm/s'     }
    atts_10hz['metek_6m_ts']          = {'units' : 'deg'     }
    atts_10hz['metek_6m_incx']        = {'units' : 'deg'     }
    atts_10hz['metek_6m_incy']        = {'units' : 'deg'     }

    atts_10hz['metek_10m_heatstatus'] = {'units' : 'int'     }
    atts_10hz['metek_10m_u']          = {'units' : 'm/s'     }
    atts_10hz['metek_10m_v']          = {'units' : 'm/s'     }
    atts_10hz['metek_10m_w']          = {'units' : 'm/s'     }
    atts_10hz['metek_10m_T']          = {'units' : 'C'       }
    atts_10hz['metek_10m_hspd']       = {'units' : 'm/s'     }
    atts_10hz['metek_10m_ts']         = {'units' : 'deg'     }
    atts_10hz['metek_10m_incx']       = {'units' : 'deg'     }
    atts_10hz['metek_10m_incy']       = {'units' : 'deg'     }
 
    atts_10hz['metek_mast_u']         = {'units' : 'm/s'     }
    atts_10hz['metek_mast_v']         = {'units' : 'm/s'     }
    atts_10hz['metek_mast_w']         = {'units' : 'm/s'     }
    atts_10hz['metek_mast_T']         = {'units' : 'C'       }

    atts_10hz['licor_diag']           = {'units' : 'int'     }
    atts_10hz['licor_co2']            = {'units' : 'mmol/m3' }
    atts_10hz['licor_h2o']            = {'units' : 'mmol/m3' }
    atts_10hz['licor_T']              = {'units' : 'deg C'   }
    atts_10hz['licor_pr']             = {'units' : 'hPa'     }
    atts_10hz['licor_co2_str']        = {'units' : 'percent' }
    atts_10hz['licor_pll']            = {'units' : 'boolean' }
    atts_10hz['licor_dt']             = {'units' : 'boolean' }
    atts_10hz['licor_ct']             = {'units' : 'boolean' }

    atts_10hz['metek_2m_u']           .update({  'long_name'       : 'wind velocity in u',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol', 
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_v']           .update({  'long_name'       : 'wind velocity in v',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_w']           .update({  'long_name'       : 'wind velocity in w',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_T']           .update({  'long_name'       : 'acoustic temperature',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_heatstatus']  .update({  'long_name'       : 'sensor diagnostics code',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; char 8 = heating setting (0=off,1=on,2=auto,3=auto and quality detection); char 9 = heating state (0=off,1=on/operational,2=on/faulty); char 10 = how many of 9 paths failed',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_hspd']        .update({  'long_name'       : 'horizontal wind speed',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; based on x,y in sensor coordinate frame',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_ts']          .update({  'long_name'       : 'wind direction',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_incx']        .update({  'long_name'       : 'sensor inclinometer pitch angle',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_2m_incy']        .update({  'long_name'       : 'sensor inclinometer roll angle',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : bottom_location_string,})

    atts_10hz['metek_6m_u']           .update({  'long_name'       : 'wind velocity in u',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_v']           .update({  'long_name'       : 'wind velocity in v',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_w']           .update({  'long_name'       : 'wind velocity in w',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_T']           .update({  'long_name'       : 'acoustic temperature',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_heatstatus']  .update({  'long_name'       : 'sensor diagnostics code',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; char 8 = heating setting (0=off,1=on,2=auto,3=auto and quality detection); char 9 = heating state (0=off,1=on/operational,2=on/faulty); char 10 = how many of 9 paths failed',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_hspd']        .update({  'long_name'       : 'horizontal wind speed',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; based on x,y in sensor coordinate frame',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_ts']          .update({  'long_name'       : 'wind direction',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_incx']        .update({  'long_name'       : 'sensor inclinometer pitch angle',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_6m_incy']        .update({  'long_name'       : 'sensor inclinometer roll angle',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : middle_location_string,})

    atts_10hz['metek_10m_u']          .update({  'long_name'       : 'wind velocity in u',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_v']          .update({  'long_name'       : 'wind velocity in v',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_w']          .update({  'long_name'       : 'wind velocity in w',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_T']          .update({  'long_name'       : 'acoustic temperature',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_heatstatus'] .update({  'long_name'       : 'sensor diagnostics code',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; char 8 = heating setting (0=off,1=on,2=auto,3=auto and quality detection); char 9 = heating state (0=off,1=on/operational,2=on/faulty); char 10 = how many of 9 paths failed',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_hspd']       .update({  'long_name'       : 'horizontal wind speed',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; based on x,y in sensor coordinate frame',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_ts']         .update({  'long_name'       : 'wind direction',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_incx']       .update({  'long_name'       : 'sensor inclinometer pitch angle',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic east-west axis when viewing east to west',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_10m_incy']       .update({  'long_name'       : 'sensor inclinometer roll angle',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol; inclination sensor embedded in anemometer sensor head; postive is anticlockwise about sonic south-north axis when viewing south to north',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : top_location_string,})

    atts_10hz['metek_mast_u']         .update({  'long_name'       : 'wind velocity in u',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : mast_funding,
                                                 'location'        : mast_location_string,})

    atts_10hz['metek_mast_v']         .update({  'long_name'       : 'wind velocity in v',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : mast_funding,
                                                 'location'        : mast_location_string,})

    atts_10hz['metek_mast_w']         .update({  'long_name'       : 'wind velocity in w',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : mast_funding,
                                                 'location'        : mast_location_string,})

    atts_10hz['metek_mast_T']         .update({  'long_name'       : 'acoustic temperature',
                                                 'instrument'      : 'Metek uSonic-Cage MP sonic anemometer',
                                                 'methods'         : 'sonic anemometer; data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : mast_funding,
                                                 'location'        : mast_location_string,})

    atts_10hz['licor_diag']           .update({  'long_name'       : 'bit-packed diagnostic integer',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol; bits 0-3 = signal strength; bit 5 = PLL; bit 6 = detector temp; bit 7 = chopper temp',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_co2']            .update({  'long_name'       : 'CO2 gas density',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_h2o']            .update({  'long_name'       : 'water vapor density',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})
    
    atts_10hz['licor_pr']             .update({  'long_name'       : 'air pressure',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_T']              .update({  'long_name'       : 'temperature at strut',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, data reported at 20 Hz; TCP/IP protocol',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_co2_str']        .update({  'long_name'       : 'CO2 signal strength diagnostic',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; raw co2 reference signal relative to expected value',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_pll']            .update({  'long_name'       : 'phase lock loop',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; 1 = optical filter wheel rotating at correct rate',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_dt']             .update({  'long_name'       : 'detector temperature',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; 1 = temperature near set point',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    atts_10hz['licor_ct']             .update({  'long_name'       : 'chopper temperature',
                                                 'instrument'      : 'Licor 7500-DS',
                                                 'methods'         : 'open-path optical gas analyzer, source data reported at 20 Hz; TCP/IP protocol; 1 = temperature near set point',
                                                 'funding_sources' : flux_funding,
                                                 'location'        : licor_location,})

    return atts_10hz, list(atts_10hz.keys()).copy() 

