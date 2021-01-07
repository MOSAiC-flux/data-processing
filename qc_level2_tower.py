# #####################################################################
# these functions take the full dataset and return the same  dataset
# with more nans. if you provide a subset of data it will work though.
# 

import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere 

from datetime  import datetime as date

global nan,Rd,K_offset,h2o_mass,co2_mass,sb,emis
nan      = np.NaN
Rd       = 287     # gas constant for dry air
K_offset = 273.15  # convert C to K
h2o_mass = 18      # are the obvious things...
co2_mass = 44      # ... ever obvious?
sb       = 5.67e-8 # stefan-boltzmann
emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

def qc_tower(tower_data):

    td = tower_data 

    raise_day = date(2019,10,25,5,30) # used for nan-ing data before the tower is up

    # something went horribly wrong with the pressure sensor during the leg 3 newdle reboot  
    td['mast_P']         .loc[date(2020,3,13,0,0,0)    :date(2020,5,13,0,0,0)]    = nan 
    td['mast_RH']        .loc[date(2019,11,26,12,14,0) :date(2019,11,26,12,45,0)] = nan 

    # something unexplained here, need to remove it manually
    td['vaisala_T_2m']   .loc[date(2020,1,17,17,21,32) :date(2020,1,19,11,55,0)]  = nan 
    td['vaisala_RH_2m']  .loc[date(2020,1,17,17,21,32) :date(2020,1,19,11,55,0)]  = nan # ditto
    td['vaisala_P_2m']   .loc[date(2020,1,17,17,21,32) :date(2020,1,19,11,55,0)]  = nan # ditto
    td['vaisala_Td_2m']  .loc[date(2020,1,17,17,21,32) :date(2020,1,19,11,55,0)]  = nan # ditto

    # right at the beginning bogus T values
    td['vaisala_T_2m']   .loc[                         :date(2019,10,19,7,19,37)] = nan 
    td['vaisala_T_6m']   .loc[                         :date(2019,10,19,5,57,56)] = nan # ditto
    td['vaisala_T_10m']  .loc[                         :date(2019,10,15,7,31,29)] = nan # ditto    
    td['vaisala_RH_2m']  .loc[                         :date(2019,10,15,8,55,0)]  = nan # ditto
    td['vaisala_RH_6m']  .loc[                         :date(2019,10,15,8,55,0)]  = nan # ditto
    td['vaisala_RH_10m'] .loc[                         :date(2019,10,15,8,55,0)]  = nan # ditto   
    td['vaisala_Td_2m']  .loc[                         :date(2019,10,15,8,55,0)]  = nan # ditto
    td['vaisala_Td_6m']  .loc[                         :date(2019,10,15,8,55,0)]  = nan # ditto
    td['vaisala_Td_10m'] .loc[                         :date(2019,10,15,8,55,0)]  = nan # ditto  
    
    # When the tower was powered back on after being off, the (heated) RH sensor needed to warm and
    # equillibrate. The equillibration period is 15-30 min and has a characteristic shape: when the
    # tower turns on the RH starts ver low, increases very high then falls back to the accurate
    # value. Instead of automating a screening procedure I just mannually screened the RH data.
    td['vaisala_RH_6m']   .loc[date(2019,10,19,5,56,0)  :date(2019,10,19,6,6,0)]   = nan

    td['vaisala_RH_2m']   .loc[date(2019,10,19,6,52,0)  :date(2019,10,19,6,53,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,18,11,11,0) :date(2019,11,18,11,13,0)] = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,18,11,11,0) :date(2019,11,18,11,13,0)] = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,18,11,11,0) :date(2019,11,18,11,13,0)] = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,19,3,59,0)  :date(2019,11,19,4,26,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,19,3,59,0)  :date(2019,11,19,4,26,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,19,3,59,0)  :date(2019,11,19,4,26,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,19,11,16,0) :date(2019,11,19,11,20,0)] = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,19,11,16,0) :date(2019,11,19,11,20,0)] = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,19,11,16,0) :date(2019,11,19,11,20,0)] = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,20,8,39,0)  :date(2019,11,20,8,55,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,20,8,39,0)  :date(2019,11,20,8,55,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,20,8,39,0)  :date(2019,11,20,8,55,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,20,9,50,0)  :date(2019,11,20,9,56,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,20,9,50,0)  :date(2019,11,20,9,56,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,20,9,50,0)  :date(2019,11,20,9,56,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,21,4,5,0)   :date(2019,11,21,4,16,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,21,4,5,0)   :date(2019,11,21,4,16,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,21,4,5,0)   :date(2019,11,21,4,16,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,21,11,23,0) :date(2019,11,21,11,34,0)] = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,21,11,23,0) :date(2019,11,21,11,34,0)] = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,21,11,23,0) :date(2019,11,21,11,34,0)] = nan

    td['vaisala_RH_2m']   .loc[date(2019,11,23,4,16,0)  :date(2019,11,23,4,30,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,23,4,16,0)  :date(2019,11,23,4,30,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,23,4,16,0)  :date(2019,11,23,4,30,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,23,11,11,0) :date(2019,11,23,11,33,0)] = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,23,11,11,0) :date(2019,11,23,11,33,0)] = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,23,11,11,0) :date(2019,11,23,11,33,0)] = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,25,4,51,0)  :date(2019,11,25,4,59,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,25,4,51,0)  :date(2019,11,25,4,59,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,25,4,51,0)  :date(2019,11,25,4,59,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,25,9,34,0)  :date(2019,11,25,9,54,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,25,9,34,0)  :date(2019,11,25,9,54,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,25,9,34,0)  :date(2019,11,25,9,54,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,26,5,36,0)  :date(2019,11,26,6,0,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,26,5,36,0)  :date(2019,11,26,6,0,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,26,5,36,0)  :date(2019,11,26,6,0,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,27,4,55,0)  :date(2019,11,27,5,44,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,27,4,55,0)  :date(2019,11,27,5,44,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,27,4,55,0)  :date(2019,11,27,5,44,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,28,4,35,0)  :date(2019,11,28,4,48,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,28,4,35,0)  :date(2019,11,28,4,48,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,28,4,35,0)  :date(2019,11,28,4,48,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,11,28,12,11,0) :date(2019,11,28,12,37,0)] = nan
    td['vaisala_RH_6m']   .loc[date(2019,11,28,12,11,0) :date(2019,11,28,12,37,0)] = nan
    td['vaisala_RH_10m']  .loc[date(2019,11,28,12,11,0) :date(2019,11,28,12,37,0)] = nan
    
    td['vaisala_RH_6m']   .loc[date(2019,12,4,6,0,0)    :date(2019,12,4,11,8,0)]   = nan
    
    td['vaisala_RH_6m']   .loc[date(2019,12,5,6,5,0)    :date(2019,12,5,6,7,0)]    = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,12,10,7,17,0)  :date(2019,12,10,7,43,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,12,10,7,17,0)  :date(2019,12,10,7,43,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,12,10,7,17,0)  :date(2019,12,10,7,43,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2019,12,11,8,4,0)   :date(2019,12,11,8,29,0)]  = nan
    td['vaisala_RH_6m']   .loc[date(2019,12,11,8,4,0)   :date(2019,12,11,8,29,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2019,12,11,8,4,0)   :date(2019,12,11,8,29,0)]  = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,1,15,7,53,0)   :date(2020,1,15,8,18,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,1,15,7,53,0)   :date(2020,1,15,8,18,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,1,15,7,53,0)   :date(2020,1,15,8,18,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,2,13,7,59,0)   :date(2020,2,13,8,27,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,2,13,7,59,0)   :date(2020,2,13,8,27,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,2,13,7,59,0)   :date(2020,2,13,8,27,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,3,11,17,33,0)  :date(2020,3,11,18,1,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,3,11,17,33,0)  :date(2020,3,11,18,1,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,3,11,17,33,0)  :date(2020,3,11,18,1,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,3,12,9,50,0)   :date(2020,3,12,12,2,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,3,12,9,50,0)   :date(2020,3,12,10,26,0)]  = nan
    td['vaisala_RH_10m']  .loc[date(2020,3,12,9,50,0)   :date(2020,3,12,10,26,0)]  = nan

    td['vaisala_RH_2m']   .loc[date(2020,3,23,23,57,0)  :date(2020,3,24,0,23,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,3,23,23,57,0)  :date(2020,3,24,0,23,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,3,23,23,57,0)  :date(2020,3,24,0,23,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,4,2,13,58,0)   :date(2020,4,2,14,26,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,4,2,13,58,0)   :date(2020,4,2,14,26,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,4,2,13,58,0)   :date(2020,4,2,14,26,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,4,4,9,13,0)    :date(2020,4,4,9,38,0)]    = nan
    td['vaisala_RH_6m']   .loc[date(2020,4,4,9,13,0)    :date(2020,4,4,9,38,0)]    = nan
    td['vaisala_RH_10m']  .loc[date(2020,4,4,9,13,0)    :date(2020,4,4,9,38,0)]    = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,4,7,15,42,0)   :date(2020,4,7,16,10,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,4,7,15,42,0)   :date(2020,4,7,16,10,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,4,7,15,42,0)   :date(2020,4,7,16,10,0)]   = nan
    
    td['vaisala_RH_2m']   .loc[date(2020,4,20,8,43,0)   :date(2020,4,20,8,46,0)]   = nan
    td['vaisala_RH_6m']   .loc[date(2020,4,20,8,43,0)   :date(2020,4,20,8,46,0)]   = nan
    td['vaisala_RH_10m']  .loc[date(2020,4,20,8,43,0)   :date(2020,4,20,8,46,0)]   = nan

    td['apogee_targ_T']  .loc[                          :date(2019,10,15,7,54)]    = nan
    td['apogee_body_T']  .loc[                          :date(2019,10,15,7,54)]    = nan

    # not very useful before the tower is up
    td['tower_ice_alt'] .loc[:raise_day] = nan 
    td['heading_tower'] .loc[:raise_day] = nan # ditto
    td['sr50_dist']     .loc[:raise_day] = nan # sr50 data is garbage when the tower is down
                                                      # (it's pointed at the horizon or something)


    td['heading_tower'].loc[:date(2019,10,24,4,59,49)] = nan # this is a couple hours after the gps
                                                                 # was calibrated and mounted and is
                                                                 # when the data looks ok

    return td
