# #####################################################################
# this file functions take the full dataset and return the same  dataset
# with more nans. if you provide a subset of data it will work though.

import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere 

from datetime  import datetime as date
from tower_data_definitions import define_level2_variables, define_turb_variables

#from debug_functions import drop_me as dm

global nan,Rd,K_offset,h2o_mass,co2_mass,sb,emis
nan      = np.NaN
Rd       = 287     # gas constant for dry air
K_offset = 273.15  # convert C to K
h2o_mass = 18      # are the obvious things...
co2_mass = 44      # ... ever obvious?
sb       = 5.67e-8 # stefan-boltzmann
emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

def qc_flagging(data_frame, table_file):

    var_atts, var_names = define_level2_variables()
    flag_df   = get_qc_table(table_file)

    zero_array = np.array([0]*len(data_frame))
    qc_var_list = []
    for iv, v in enumerate(var_names):
        if v.rsplit("_")[-1] == 'qc':
            data_frame[v] =  0
            qc_var_list.append(v)

    # lookup table for "group" names, these need to include the "_qc", as the code below
    # puts the value into that field, i.e. temp_qc, not just temp
    lookup_table = {
        'ALL_FIELDS' : [v for v in data_frame.columns if v.split('_')[-1]=='qc'], # if the variable has an "_qc", then it deserves a flag
    }

    for irow, row in flag_df.iterrows():
        var_to_qc = row['var_name']+'_qc'
        try: data_frame[var_to_qc].loc[row['start_date']:row['end_date']] = row['qc_val']
        except KeyError as ke: 
            special_key = row['var_name'] # things like "ALL_FIELDS", grouped vars
            if special_key in lookup_table.keys():
                for v in lookup_table[special_key]: 
                    data_frame[v].loc[row['start_date']:row['end_date']] = row['qc_val']
            else:
                print(f"!!! problem with entry in manual QC table for var {var_to_qc}!!!")

    return data_frame 

def get_qc_table(table_file):
    
    mos_begin = '20191015 000000'
    mos_end = '20200919 000000'

    def custom_date_parser(d):

        if d == 'beg': d = mos_begin
        elif d=='end': d =mos_end
            
        #hour = (str_two := d.split(' ')[1])[0:2] # no walrus in the trio python
        str_two = d.split(' ')[1]
        hour = str_two[0:2]
        mins = str_two[2:4]
        secs = str_two[4:6]
        date_str = f"{d.split(' ')[0]} {hour}:{mins}:{secs}"

        return date.strptime(date_str, "%Y%m%d %H:%M:%S")

    cols = ['var_name', 'start_date', 'end_date', 'qc_val', 'explanation', 'author']
    mqc = pd.read_csv(table_file , skiprows=range(0,6), names=cols)     

    mqc['start_date'] = mqc['start_date'].apply(custom_date_parser)
    mqc['end_date'] = mqc['end_date'].apply(custom_date_parser)

    return mqc

def qc_tower(tower_data): 

    # Fix the flux plates that were insalled upside down, why is this here... it doesn't have to be... vestigial
    slow_data['fp_A_Wm2'] = slow_data['fp_A_Wm2'] * -1
    slow_data['fp_B_Wm2'] = slow_data['fp_B_Wm2'] * -1

    tower_data = qc_flagging(tower_data, "./qc_tables/qc_table_tower.csv")

    return tower_data 

def qc_stations(curr_station, station_data):

    if 'asfs30' in curr_station:

        # Fix the flux plates that were insalled upside down
        station_data['subsurface_heat_flux_A'] = station_data['subsurface_heat_flux_A'] * -1
        station_data['subsurface_heat_flux_B'].loc[datetime(2020,4,1,0,0):] = station_data['subsurface_heat_flux_B'].loc[datetime(2020,4,1,0,0):] * -1
        station_data = qc_flagging(station_data, "./qc_tables/qc_table_asfs30.csv")

    elif 'asfs40' in curr_station:

        # Fix the flux plates that were insalled upside down
        station_data['subsurface_heat_flux_A'] = station_data['subsurface_heat_flux_A'] * -1
        station_data['subsurface_heat_flux_B'] = station_data['subsurface_heat_flux_B'] * -1
        station_data = qc_flagging(station_data, "./qc_tables/qc_table_asfs40.csv")

    elif 'asfs50' in curr_station:

        # Fix the flux plates that were insalled upside down
        station_data['subsurface_heat_flux_B'] = station_data['subsurface_heat_flux_B'] * -1
        station_data['subsurface_heat_flux_A'].loc[datetime(2020,4,1,0,0):] = station_data['subsurface_heat_flux_A'].loc[datetime(2020,4,1,0,0):] * -1
        station_data = qc_flagging(station_data, "./qc_tables/qc_table_asfs50.csv")


    return station_data;

