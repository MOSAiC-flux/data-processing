# #####################################################################
# this file functions take the full dataset and return the same  dataset
# with more nans. if you provide a subset of data it will work though.

import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere 

from datetime  import datetime as dt
import time

from tower_data_definitions import define_qc_variables as tower_qc_variables
from tower_data_definitions import define_turb_variables
from asfs_data_definitions import define_qc_variables as asfs_qc_variables
import functions_library as fl

try:
    from debug_functions import drop_me as dm
except: do_nothing=True

global nan,Rd,K_offset,h2o_mass,co2_mass,sb,emis
nan      = np.NaN
Rd       = 287     # gas constant for dry air
K_offset = 273.15  # convert C to K
h2o_mass = 18      # are the obvious things...
co2_mass = 44      # ... ever obvious?
sb       = 5.67e-8 # stefan-boltzmann
emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

def qc_tower(tower_data): 

    tower_data = qc_flagging(tower_data, "./qc_tables/qc_table_tower.csv", tower_qc_variables()[1])

    return tower_data 

def qc_stations(asfs_data, station_name): 

    asfs_data = qc_flagging(asfs_data, f"./qc_tables/qc_table_{station_name}.csv", asfs_qc_variables()[1])
    
    return asfs_data 

# thanks ola for doing the legwork on this, code translated by mgallagher 
def qc_tower_winds(tower_data, ship_data):

    '''
    there are XXX flagging cases here:
        1: the wind is coming from the direction of the tower frame +/- YY degrees (YY=30 degrees)
        2: the wind is coming from the direction of the met hut
        3: the wind is coming from the direction of the ship +/- 10 degrees

    There is a special sector qc variable that gives more detailed information, wind_sector_qc_info_XXm
        - 10: In Polarstern sector (i.e. Caution)
        - 11: In Polarstern sector and in footprint (i.e., Bad)
        - 12: In Polarstern sector and above sig2/ustar threshold (i.e. Bad)
        - 20: In Met Hut sector (i.e. Caution)
        - 21: In Met Hut sector and in footprint (i.e., Bad)
        - 22: In Met Hut sector and above sig2/ustar threshold (i.e. Bad)
        - 30: In Tower sector (i.e. Caution)
        - 31: In Tower sector and in footprint (i.e., Bad)
        - 32: In Tower sector and above sig2/ustar threshold (i.e. Bad)
        - 40: Other issue

    '''

    # #############################################################################################
    #wind_vars_to_qc = ['wspd_u_mean','wspd_v_mean','wspd_w_mean','wspd_vec_mean','wdir_vec_mean']
    heights_to_qc   = ['2m', '6m', '10m', 'mast']
    min_sigw_u = 0.8; max_sigw_u = 1.8

    # create the more detailed qc information variable specifically for the wind sector editing here
    for h in heights_to_qc: tower_data.loc[:, f'wind_sector_qc_info_{h}'] = [0]*len(tower_data)

    # calculate footprint distance - Mason (1988; QJRMS)
    height_arrays = {'2m': [2.66]*len(tower_data),'6m':[5.66]*len(tower_data), '10m':[10.54]*len(tower_data)} #heights on tower

    if tower_data.index[0] < dt(2019,11,18): height_arrays['mast'] = [30]*len(tower_data)
    else:                                    height_arrays['mast'] = [23]*len(tower_data)

    footprint_df = pd.DataFrame(index=tower_data.index)
    turb_today = {}

    for h in heights_to_qc:
        try: 
            turb_today[h] = True
            footprint_df[f'tstarr_{h}'] = tower_data[f'ustar_{h}']/tower_data[f'wspd_vec_mean_{h}']
            footprint_df[f'fp_{h}']     = height_arrays[h]/(2*footprint_df[f'tstarr_{h}']**2)
            tower_data[f'fp_{h}']       = footprint_df[f'fp_{h}']
        except: turb_today[h] = False # can't calculate this  

    # calculate the wind angle relative to the tower heading, and
    # sigw/ustar for the sector editing
    wind_relative = pd.DataFrame(index=tower_data.index)
    sigw_ustar    = pd.DataFrame(index=tower_data.index)
    for h in heights_to_qc:
        wind_relative[h] = tower_data[f'wdir_vec_mean_{h}']  - tower_data['heading_tower'] ; 
        wind_relative[h][wind_relative[h]<0] = wind_relative[h] [wind_relative[h]<0] +360
        if turb_today[h]:
            sigw_ustar[h] = tower_data[f'sigW_{h}']/tower_data[f'ustar_{h}']

    # ################################################################################################
    # case 1! wdir and tower_heading are ~ the same +/-, wind is passing through tower frame
    if tower_data.index[0] > dt(2020,6,19) and tower_data.index[0] < dt(2020, 8, 3):
        min_angle = 245; max_angle = 275
    else: min_angle = 65; max_angle = 95

    for h in heights_to_qc:
        if h == 'mast': do_nothing = True; continue

        values_caution_tower = (wind_relative[h]>min_angle) & (wind_relative[h]<max_angle)
        tower_data.loc[values_caution_tower, f'wind_sector_qc_info_{h}'] = 30

        # for wv in wind_vars_to_qc:
        #     try: tower_data[f'{wv}_{h}_qc']               
        #     except: tower_data.loc[:, f'{wv}_{h}_qc'] = 0 
        #     tower_data.loc[values_caution_tower, f'{wv}_{h}_qc'] = 1

        # remove points in met hut direction with sigw/ustar outside physical bounds
        if turb_today[h]: 
            values_bad_sigwustar = (sigw_ustar[h] < min_sigw_u) | (sigw_ustar[h] > max_sigw_u)
            #for wv in wind_vars_to_qc:
                #tower_data.loc[(values_caution_tower & values_bad_sigwustar) , f'{wv}_{h}_qc'] = 2
            tower_data.loc[(values_caution_tower & values_bad_sigwustar) , f'wind_sector_qc_info_{h}'] = 32

    # ########################################################################################
    # case 2! angles with met hut influence, tower-relative of met hut
    # varied for Legs 1-3, Leg 4, and Leg 5.
    if tower_data.index[0] <= dt(2020,6,19):
        min_angle = 45  ; max_angle = 70;  qc_case = 'and' # for the discontinuity O_o
    if tower_data.index[0] > dt(2020,6,19) and tower_data.index[0] <= dt(2020,8,3):
        min_angle = 165 ; max_angle = 188; qc_case = 'and' # # 188??wtf?
    if tower_data.index[0] > dt(2020,8,3):
        min_angle = 340 ; max_angle = 10;  qc_case = 'or'

    for h in heights_to_qc:
        if h == 'mast': do_nothing = True; continue

        if qc_case == 'and': values_caution_methut = (wind_relative[h]>min_angle) & (wind_relative[h]<max_angle)
        else: values_caution_methut = (wind_relative[h]>min_angle) | (wind_relative[h]<max_angle)
        tower_data.loc[values_caution_methut, f'wind_sector_qc_info_{h}'] = 20
        #for wv in wind_vars_to_qc: tower_data.loc[values_caution_methut, f'{wv}_{h}_qc'] = 1

        # remove points in met hut direction with sigw/ustar outside physical bounds
        if turb_today[h]: 
            values_bad_sigwustar = (sigw_ustar[h] < min_sigw_u) | (sigw_ustar[h] > max_sigw_u)
            # for wv in wind_vars_to_qc:
            #     tower_data.loc[(values_caution_methut & values_bad_sigwustar), f'{wv}_{h}_qc'] = 2
            tower_data.loc[(values_caution_methut & values_bad_sigwustar) , f'wind_sector_qc_info_{h}'] = 22

    # ###########################################################################################
    # case 3! calculate tower-relative wind directions from ship bearing to
    # identify/qc angles with ship influence
    qc_window = 10 # the number of degrees influenced negatively by the shlip, flag!

    ship_relative = pd.DataFrame(index=tower_data.index)
    for h in heights_to_qc:
        ship_distance = tower_data['ship_distance']
        ship_bearing  = tower_data['ship_bearing']

        if h=='mast': 
            if dt(2019,12,7) < tower_data.index[0] < dt(2020,3,12):
                ship_distance = tower_data['ship_distance']-63.3
                ship_bearing  = tower_data['ship_bearing']+8.83

            if dt(2020,3,12) <= tower_data.index[0] <= dt(2020, 5, 10):


                ship_distance = fl.distance(tower_data['lat_mast'], tower_data['lon_mast'],
                                            ship_data['lat'], ship_data['lon'])*1000

                ship_bearing = fl.calculate_initial_angle(tower_data['lat_mast'], tower_data['lon_mast'],
                                                          ship_data['lat'],ship_data['lon']) 

        ship_relative[h] = np.abs(tower_data[f'wdir_vec_mean_{h}'] - ship_bearing)
        values_caution_ship = (ship_relative[h]>360-qc_window) | (ship_relative[h]<qc_window)
        tower_data.loc[values_caution_ship, f'wind_sector_qc_info_{h}'] = 10
        #for wv in wind_vars_to_qc: tower_data.loc[values_caution_ship, f'{wv}_{h}_qc'] = 1

        # remove points in ship direction within footprint distance or outside of sigw_ustar bounds
        if turb_today[h]: 
            distance_fraction = 4 # footprint factor for point editing
            in_fp_to_qc       = (ship_distance < footprint_df[f'fp_{h}']/distance_fraction )   
            values_bad_sigwustar = (sigw_ustar[h] < min_sigw_u) | (sigw_ustar[h] > max_sigw_u)

            tower_data.loc[(values_caution_ship & in_fp_to_qc), f'wind_sector_qc_info_{h}'] = 10
            # for wv in wind_vars_to_qc:
            #     tower_data.loc[(values_caution_ship & in_fp_to_qc), f'{wv}_{h}_qc'] = 2
            #     tower_data.loc[(values_caution_ship & values_bad_sigwustar), f'{wv}_{h}_qc'] = 2
            tower_data.loc[(values_caution_ship & in_fp_to_qc), f'wind_sector_qc_info_{h}'] = 11
            tower_data.loc[(values_caution_ship & values_bad_sigwustar), f'wind_sector_qc_info_{h}'] = 12

    return tower_data


# thanks ola for doing the legwork on this, code translated by mgallagher 
def qc_asfs_winds(station_data): 

    '''
    there is only one case for the flux stations
        1: the wind is coming from the direction of the ship +/- 10 degrees

    There is a special sector qc variable that gives more detailed information, wind_sector_qc_info_XXm
        - 10: In Polarstern sector (i.e. Caution)
        - 11: In Polarstern sector and in footprint (i.e., Bad)
        - 12: In Polarstern sector and above sig2/ustar threshold (i.e. Bad)
        - 40: Other issue??? noooooooooooooooooooooooooooo

    '''

    # #############################################################################################
    #wind_vars_to_qc = ['wspd_u_mean','wspd_v_mean','wspd_w_mean','wspd_vec_mean','wdir_vec_mean']
    min_sigw_u = 0.8; max_sigw_u = 1.8

    # create the more detailed qc information variable specifically for the wind sector editing here
    station_data.loc[:, f'wind_sector_qc_info'] = [0]*len(station_data)

    # calculate footprint distance - Mason (1988; QJRMS)
    height_array = [3.0]*len(station_data)

    footprint_df = pd.DataFrame(index=station_data.index)
    try: 
        turb_today              = True
        footprint_df[f'tstarr'] = station_data[f'ustar']/station_data[f'wspd_vec_mean']
        footprint_df[f'fp']     = height_arrays[h]/(2*footprint_df[f'tstarr']**2)
        station_data[f'fp']     = footprint_df[f'fp']
    except: turb_today = False # can't calculate this  

    # calculate the wind angle relative to the tower heading, and
    # sigw/ustar for the sector editing
    wind_relative = station_data[f'wdir_vec_mean']  - station_data['heading'] ; 
    wind_relative[wind_relative<0] = wind_relative[wind_relative<0] +360
    if turb_today:
        sigw_ustar = station_data[f'sigW']/station_data[f'ustar']

    # ###########################################################################################
    # case 3! calculate tower-relative wind directions from ship bearing to
    # identify/qc angles with ship influence
    qc_window = 10 # the number of degrees influenced negatively by the shlip, flag!

    ship_distance = station_data['ship_distance']
    ship_bearing  = station_data['ship_bearing']

    ship_relative = np.abs(station_data[f'wdir_vec_mean'] - ship_bearing)
    values_caution_ship = (ship_relative>360-qc_window) | (ship_relative<qc_window)
    station_data.loc[values_caution_ship, f'wind_sector_qc_info'] = 10
    #for wv in wind_vars_to_qc: station_data.loc[values_caution_ship, f'{wv}_qc'] = 1

    # remove points in ship direction within footprint distance or outside of sigw_ustar bounds
    if turb_today: 
        distance_fraction = 4 # footprint factor for point editing
        in_fp_to_qc       = (ship_distance < footprint_df[f'fp']/distance_fraction )   
        values_bad_sigwustar = (sigw_ustar < min_sigw_u) | (sigw_ustar > max_sigw_u)

        station_data.loc[(values_caution_ship & in_fp_to_qc), f'wind_sector_qc_info'] = 10
        # for wv in wind_vars_to_qc:
        #     station_data.loc[(values_caution_ship & in_fp_to_qc), f'{wv}_qc'] = 2
        #     station_data.loc[(values_caution_ship & values_bad_sigwustar), f'{wv}_qc'] = 2
        station_data.loc[(values_caution_ship & in_fp_to_qc), f'wind_sector_qc_info'] = 11
        station_data.loc[(values_caution_ship & values_bad_sigwustar), f'wind_sector_qc_info'] = 12

    return wind_relative, ship_relative, station_data

def qc_flagging(data_frame, table_file, var_names):

    flag_df = get_qc_table(table_file)

    zero_array = np.array([0]*len(data_frame))
    qc_var_list = []
    for iv, v in enumerate(var_names):
        if v.rsplit("_")[-1] == 'qc':
            data_frame[v] =  [0]*len(data_frame)
            qc_var_list.append(v)

    # lookup table for "group" names, these need to include the "_qc", as the code below
    # puts the value into that field, i.e. temp_qc, not just temp
    lookup_table = {
        'ALL_FIELDS' : [v for v in var_names if v.split('_')[-1] == 'qc'], # if the variable has an "_qc", it deserves a flag
        'ALL_MAST'   : [v for v in var_names if v.split('_')[-1] == 'qc' and v.rstrip('_qc').split('_')[-1] == 'mast'], # if mast variable, flag
    } 

    problem_rows = {}
    for irow, row in flag_df.iterrows():
        var_to_qc = row['var_name']+'_qc'
        try: data_frame[var_to_qc].loc[row['start_date']:row['end_date']] = row['qc_val']
        except KeyError as ke: 
            special_key = row['var_name'] # things like "ALL_FIELDS", grouped vars
            if special_key in lookup_table.keys():
                for v in lookup_table[special_key]: 
                    data_frame[v].loc[row['start_date']:row['end_date']] = row['qc_val']
            else:
                print(f"!!! problem with entry in manual QC table for var {var_to_qc} at row {irow}!!!")
                print(f"{row}")
                print("==========================================================================================")
                print("Python traceback: \n\n")
                import traceback
                import sys
                print(traceback.format_exc())
                print("==========================================================================================")

                problem_rows[irow] = row

    if len(problem_rows)>1:
        print(f"\n\n There were some prolems with the QC file {table_file}, specifically,  {len(problem_rows)} of them...\n\n")
        time.sleep(10)
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

        try: 
            rtime = dt.strptime(date_str, "%Y%m%d %H:%M:%S")
            return rtime
        except:
            print(f" BAD DATE FORMAT!!!! {date_str}")
            return pd.NaT

    cols = ['var_name', 'start_date', 'end_date', 'qc_val', 'explanation', 'author']
    mqc = pd.read_csv(table_file , skiprows=range(0,6), names=cols)     

    mqc['start_date'] = mqc['start_date'].apply(custom_date_parser)
    mqc['end_date']   = mqc['end_date'].apply(custom_date_parser)

    drop_rows = (mqc['start_date'].isna() | mqc['end_date'].isna())
    if len(mqc[drop_rows]) > 0:
        print(mqc[drop_rows])
        print(f"\n\n DROPPING THE FOLLOWING QC ROWS DUE TO BAD TIME FORMATTING:\n")
        for irow in mqc[drop_rows].index:
            for ir in mqc.loc[irow].index:
                print(f"{mqc.loc[irow].loc[ir]} ", end='')
            print()
        print("\n\n")
    mqc = mqc[~drop_rows]

    return mqc

# wrapper that loops through instruments and feeds them to generic qc algorithm in next function 
def qc_tower_turb_data(tower_df, turb_df):

    height_list = ['2m', '6m', '10m', 'mast']

    for h in height_list: 
        var_list = [] # this is stupid and hacky and ugly
        for var in define_turb_qc_vars(): 
            try: 
                turb_df[var+'_'+h] # ensure it exists
                var_list.append(var+'_'+h)
            except: 
                turb_df[var] # single height variable
                var_list.append(var)

        tdf = turb_df.copy()[var_list]
        tdf.columns = tdf.columns.str.replace(f'_{h}','') # remove height suffix before passing to qc routine

        tower_df[f'turbulence_qc_{h}'] = qc_turb_data(tdf)

        sector_qc_info = tower_df[f'wind_sector_qc_info_{h}']   

        # tower specific stuff        
        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 10] = 1 # in polarstern sector
        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 11] = 2 # *and* within footprint
        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 12] = 2 # *and* sigw/ustar thresh

        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 20] = 1 # in methut sector
        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 21] = 2 # *and* within footprint
        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 22] = 2 # *and* sigw/ustar thresh

        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 30] = 1 # in tower frame sector
        tower_df[f'turbulence_qc_{h}'][sector_qc_info == 32] = 2 # *and* sigw/ustar thresh

        # if pressure missing flag nan, if pressure exists then it's bad data
        tower_df[f'Hl_qc'] = tower_df['turbulence_qc_2m']

    return tower_df, turb_df 

# wrapper that loops through instruments and feeds them to generic qc algorithm in next function 
def qc_asfs_turb_data(asfs_df, turb_df):

    var_list = [] # this is stupid and hacky and ugly
    for var in define_turb_qc_vars(): 
        try: 
            turb_df[var] # ensure it exists
            var_list.append(var)
        except: 
            print(f"WE SHOULDN'T MAKE IT HERE {var}")

    tdf = turb_df.copy()[var_list]

    asfs_df[f'turbulence_qc'] = qc_turb_data(tdf)

    sector_qc_info = asfs_df[f'wind_sector_qc_info']   

    # asfs specific stuff        
    asfs_df[f'turbulence_qc'][sector_qc_info == 10] = 1 # in polarstern sector
    asfs_df[f'turbulence_qc'][sector_qc_info == 11] = 2 # *and* within footprint
    asfs_df[f'turbulence_qc'][sector_qc_info == 12] = 2 # *and* sigw/ustar thresh

    # if pressure missing flag nan, if pressure exists then it's bad data
    asfs_df[f'Hl_qc'] = asfs_df['turbulence_qc']

    return asfs_df, turb_df 


def qc_turb_data(df):

    # does the generic turbulence variable exist, if it doesn't or it's entirely NaNs, let's fill it with zeros, aka good
    try:
        if df['turbulence_qc'].isna().all(): df['turbulence_qc'] = 0
    except: df['turbulence_qc'] = [0]*len(df)

    turbulence_qc = df['turbulence_qc'].copy()

    turbulence_qc[df['ustar'] < 0] = 1   # ustar < 0 is caution
    turbulence_qc[df['Hs'].isna()] = 2   # missing sensible heat flux means bad turb data

    return turbulence_qc

def define_turb_qc_vars():
    turb_vars_for_qc   = ['ustar', 'Hs']
    return turb_vars_for_qc
 
