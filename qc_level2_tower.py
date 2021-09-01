# #####################################################################
# this file functions take the full dataset and return the same  dataset
# with more nans. if you provide a subset of data it will work though.

import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere 

from datetime  import datetime as date
from tower_data_definitions import define_level2_variables, define_turb_variables

from debug_functions import drop_me as dm

global nan,Rd,K_offset,h2o_mass,co2_mass,sb,emis
nan      = np.NaN
Rd       = 287     # gas constant for dry air
K_offset = 273.15  # convert C to K
h2o_mass = 18      # are the obvious things...
co2_mass = 44      # ... ever obvious?
sb       = 5.67e-8 # stefan-boltzmann
emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

def qc_flagging(tower_data):

    tower_flags = tower_data 

    var_atts, var_names = define_level2_variables()
    flag_df   = get_qc_table("./manual_qc_table.csv")

    zero_array = np.array([0]*len(tower_data))
    qc_var_list = []
    for iv, v in enumerate(var_names):
        if v.rsplit("_")[-1] == 'qc':
            tower_data[v] =  0
            qc_var_list.append(v)

    for irow, row in flag_df.iterrows():
        var_to_qc = row['var_name']+'_qc'
        try: 
            tower_data[var_to_qc].loc[row['start_date']:row['end_date']] = row['qc_val']
        except KeyError as ke: 
            print(f"!!! problem with entry in manual QC table for var {var_to_qc}!!!")

    return tower_data 
        

def get_qc_table(table_file="./manual_qc_table.csv"):
    
    mos_begin = '20191015 000000'
    mos_end = '20200919 000000'

    def custom_date_parser(d):

        if d == 'beg': d = mos_begin
        elif d=='end': d =mos_end
            
        hour = (str_two := d.split(' ')[1])[0:2]
        mins = str_two[2:4]
        secs = str_two[4:6]
        date_str = f"{d.split(' ')[0]} {hour}:{mins}:{secs}"

        return date.strptime(date_str, "%Y%m%d %H:%M:%S")

    cols = ['var_name', 'start_date', 'end_date', 'qc_val', 'explanation', 'author']
    mqc = pd.read_csv("./manual_qc_table.csv", skiprows=range(0,6), names=cols)     

    mqc['start_date'] = mqc['start_date'].apply(custom_date_parser)
    mqc['end_date'] = mqc['end_date'].apply(custom_date_parser)

    return mqc

def qc_tower(tower_data):

    date_twr_raised = date(2019, 10, 24, 5, 30)

    td = tower_data # pointer, c-style.. shorthand

    # #####################################################################################
    # manual flagging done by Chris and Michael prior to document creation
    # -> nans for specific periods

    # Fix the flux plates that were insalled upside down
    td['fp_A_Wm2'] = td['fp_A_Wm2'] * -1
    td['fp_B_Wm2'] = td['fp_B_Wm2'] * -1

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
    td['tower_ice_alt'] .loc[:date_twr_raised] = nan 
    td['heading_tower'] .loc[:date_twr_raised] = nan # we are going to fill this in with manual obs for each sonic inividually when the wind is calculated in lvl2 
    td['sr50_dist']     .loc[:date_twr_raised] = nan # sr50 data is garbage when the tower is down

    return td
