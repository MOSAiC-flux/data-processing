# #####################################################################
# this file functions take the full dataset and return the same  dataset
# with more nans. if you provide a subset of data it will work though.
import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere 

from datetime  import datetime as dt
import time

from collections import OrderedDict

from tower_data_definitions import define_qc_variables as tower_qc_variables
from tower_data_definitions import define_turb_variables
from asfs_data_definitions import define_qc_variables as asfs_qc_variables
import functions_library as fl

try:
    from debug_functions import drop_me as dm
except: do_nothing = True

global nan,Rd,K_offset,h2o_mass,co2_mass,sb,emis
nan      = np.NaN
Rd       = 287     # gas constant for dry air
K_offset = 273.15  # convert C to K
h2o_mass = 18      # are the obvious things...
co2_mass = 44      # ... ever obvious?
sb       = 5.67e-8 # stefan-boltzmann
emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

def qc_tower(tower_data): 

    tower_data = qc_flagging(tower_data, "./qc_tables/qc_table_tower.csv", tower_qc_variables()[1], 'tower')

    return tower_data 

def qc_stations(asfs_data, station_name): 

    asfs_data = qc_flagging(asfs_data, f"./qc_tables/qc_table_{station_name}.csv", asfs_qc_variables()[1], station_name)
    
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
        wind_relative[h] = tower_data[f'wdir_vec_mean_{h}']  - tower_data['tower_heading'] ; 
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
            if dt(2019,12,7) < tower_data.index[0] < dt(2020,4,13):
                ship_distance = tower_data['ship_distance']-63.3
                ship_bearing  = tower_data['ship_bearing']+8.83

            if dt(2020,4,13) <= tower_data.index[0] <= dt(2020, 5, 10):

                try:

                    ship_distance = fl.distance_wgs84(tower_data['lat_mast'], tower_data['lon_mast'],
                                                      ship_data['lat'], ship_data['lon'])

                    ship_bearing = fl.calculate_initial_angle_wgs84(tower_data['lat_mast'], tower_data['lon_mast'],
                                                                    ship_data['lat'],ship_data['lon']) 
                except:

                    ship_distance = tower_data['ship_distance']-63.3
                    ship_bearing  = tower_data['ship_bearing']+8.83

 
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
        distance_fraction    = 4 # footprint factor for point editing
        in_fp_to_qc          = (ship_distance < footprint_df[f'fp']/distance_fraction )   
        values_bad_sigwustar = (sigw_ustar < min_sigw_u) | (sigw_ustar > max_sigw_u)

        station_data.loc[(values_caution_ship & in_fp_to_qc), f'wind_sector_qc_info'] = 10
        # for wv in wind_vars_to_qc:
        #     station_data.loc[(values_caution_ship & in_fp_to_qc), f'{wv}_qc'] = 2
        #     station_data.loc[(values_caution_ship & values_bad_sigwustar), f'{wv}_qc'] = 2
        station_data.loc[(values_caution_ship & in_fp_to_qc), f'wind_sector_qc_info'] = 11
        station_data.loc[(values_caution_ship & values_bad_sigwustar), f'wind_sector_qc_info'] = 12

    return wind_relative, ship_relative, station_data

# this is all so ugly and I hate it
def qc_flagging(data_frame, table_file, qc_var_names, station_name):

    print(f"…………… getting qc file, {table_file}")
    flag_df = get_qc_table(table_file)

    print("…………… setting qc vals to 0")

    qcdf = pd.DataFrame(index=data_frame.index, columns=qc_var_names, dtype=np.int64)
    qcdf = qcdf.fillna(0)
    data_frame = pd.concat([data_frame, qcdf], axis=1)

    # instantiate the turbulence qc variables as nan/0... depending
    if station_name == 'tower':
        height_strs = ['2m', '6m', '10m', 'mast'] 

        add_str = '_tower'
        turb_qc_vars = []
        for h in height_strs:
            var = f'turbulence_{h}_qc'
            turb_qc_vars.append(var)
            data_frame[var] = np.nan
            if h!='mast': data_frame.loc[~data_frame[f'vaisala_T_{h}'].isnull(), var] = 0
            else: data_frame.loc[~data_frame[f'{h}_T'].isnull(), var] = 0 #... WHY, is this a different name

        data_frame['bulk_qc'] = np.nan
        data_frame.loc[~data_frame[f'vaisala_T_10m'].isnull(), 'bulk_qc'] = 0

    else:
        data_frame['turbulence_qc'] = np.nan
        data_frame['bulk_qc']       = np.nan
        data_frame.loc[~data_frame['temp'].isnull(), 'turbulence_qc'] = 0
        data_frame.loc[~data_frame['temp'].isnull(), 'bulk_qc']       = 0

        add_str = '' # some vars are different for tower... :::|

    print("…………… done, moving on to table")

    # lookup table for "group" names, these need to include the "_qc", as the code below
    # puts the value into that field, i.e. temp_qc, not just temp, aka 'inheritance'/hierarchy
    # the order matters, btw, since ALL_FIELDS should be evaluated in the loop below last
    lookup_table = {
        'up_long_hemisp'   : ['up_long_hemisp', 'skin_temp_surface'],
        'down_long_hemisp' : ['down_long_hemisp', 'skin_temp_surface'],
        'sr50_dist'        : ['sr50_dist', 'snow_depth'], 
        'rh'               : ['rh', 'rhi', 'mixing_ratio', 'dew_point', 'vapor_pressure'],
        'temp'             : ['temp','rh', 'rhi', 'mixing_ratio', 'dew_point', 'vapor_pressure'],#, 'bulk_Hs'],
        'lon'+add_str      : ['lon'+add_str, 'lat'+add_str] , 
        'lat'+add_str      : ['lon'+add_str, 'lat'+add_str] , 

    }
    if station_name == 'tower':
        lookup_table.update({
            'ALL_TURBULENCE_2M' : ['turbulence_2m'],
            'ALL_TURBULENCE_6M' : ['turbulence_6m'],
            'ALL_TURBULENCE_10M' : ['turbulence_10m', 'bulk'],
            'ALL_TURBULENCE_MAST' : ['turbulence_mast'],
            'ALL_MAST'   : [v.rstrip('_qc') for v in qc_var_names if v.split('_')[-1] == 'qc' and v.rstrip('_qc').split('_')[-1] == 'mast'] \
                          +['turbulence_mast'], 


            'ALL_FIELDS' : [v.rstrip('_qc') for v in qc_var_names if v.split('_')[-1] == 'qc'] \
                          +['turbulence_2m', 'turbulence_6m', 'turbulence_10m', 'turbulence_mast', 'bulk'], 
        })
    else:
        lookup_table.update({
            'ALL_TURBULENCE' : ['turbulence', 'bulk'],
            'ALL_MET' : ['temp', 'rh', 'mixing_ratio' ,'dew_point', 'skin_temp_surface'],
            'ALL_FIELDS' : [v.rstrip('_qc') for v in qc_var_names if v.split('_')[-1] == 'qc'] \
                          +['turbulence', 'bulk'], 
        })

    lookup_table = OrderedDict(lookup_table) # ensure order doesn't change


    problem_rows = {} # dictionary to keep rows that don't match any of the conditionals, i.e. bad/nonsense rows
    # we go through every entry in the qc table and fill in the qc vars in the dataframe
    for irow, row in flag_df.iterrows():

        # hackery to account for heights that might exist avoiding duplicating stuff up there ^
        height_strs = ['2m', '6m', '10m', 'mast'] 
        if any(h in row['var_name'] for h in height_strs):
            hstr = '_'+row['var_name'].split('_')[-1]
            special_key = row['var_name'].rstrip('_'+hstr)

        else:
            hstr = ''
            special_key = row['var_name']

        # is the current variable in the lookup list
        if any(special_key in c for c in lookup_table.keys()):
            
            for v in lookup_table[special_key]: 

                try: 
                    special_var = v+hstr+'_qc'
                    data_frame.loc[row['start_date']:row['end_date'], special_var] = row['qc_val']
                except Exception as ex:
                    print(ex)
                    print(f"... failed for {special_key=} and val {v+hstr}")

        # it wasn't in the lookup list, only fill out the qc var for this individual variable
        else:
            try:
                var_to_qc = row['var_name']+'_qc' # get var_name column from file
                data_frame.loc[row['start_date']:row['end_date'], var_to_qc] = row['qc_val']

            except KeyError as ke: 
                    print(f"!!! problem with entry in manual QC table for {table_file} for var {var_to_qc} at row {irow}!!!")
                    print(f"{row}")
                    print("==========================================================================================")
                    print("Python traceback: \n\n")
                    import traceback, sys
                    print(traceback.format_exc())
                    print("==========================================================================================")

                    problem_rows[irow] = row

    print("…………… done, moving on to inheritance")


    # now make sure that everything is inherited from before as well, this could include the automatic qc..
    # we loop through the list of inherited variables
    for parent_var, child_var_list in lookup_table.items():
        # if the parent variable is a "real" measured param, copy all engineering/bad data
        # from the parent variable and apply it to all inherited variables...
        if 'ALL_' not in parent_var:

            try:
                data_frame[parent_var+'_qc'] # does this var exist?
                height_strs = ['',]
            except KeyError as ke:
                data_frame[parent_var+'_2m_qc'] # if no, then it has to be a height var
                height_strs = ['_2m', '_6m', '_10m', '_mast'] 
            for h in height_strs:
                caut_inds = (data_frame[parent_var+h+'_qc']==1)  
                bad_inds  = (data_frame[parent_var+h+'_qc']==2)  
                eng_inds  = (data_frame[parent_var+h+'_qc']==3)
                for child_var in child_var_list:

                    no_overwrite = (data_frame[child_var+h+'_qc']!=2)&(data_frame[child_var+h+'_qc']!=3)
                    data_frame.loc[(caut_inds)&(no_overwrite), child_var+h+'_qc'] = 1

                    no_overwrite = (data_frame[child_var+h+'_qc']!=2)

                    data_frame.loc[(eng_inds)&(no_overwrite), child_var+h+'_qc']  = 3
                    data_frame.loc[bad_inds, child_var+h+'_qc']  = 2


        # but for "ALL_" variables we're going to manually apply the qc values for each time
        # range specified in the qc table to all of the applicable variables...
        # ... this is done here and not above because it needs to supersede any of the other
        # possible qc values specified
        else:

            for irow, row in flag_df.iterrows():
                if parent_var == row['var_name']: 
                    for child_var in child_var_list:
                        try: 
                            child_qc_var = child_var+'_qc'

                            no_overwrite = (data_frame[child_qc_var]!=2)&(data_frame[child_qc_var]!=3)
                            if row['qc_val'] == 2:
                                no_overwrite = (data_frame[child_qc_var]!=2)

                            time_range = (data_frame.index>row['start_date'])&(data_frame.index<row['end_date'])

                            data_frame.loc[(time_range) & (no_overwrite), child_qc_var] = row['qc_val']
                        except:

                            height_strs = ['_2m', '_6m', '_10m', '_mast'] 
                            for h in height_strs:
                                child_qc_var = child_var+h+'_qc'
                                try:
                                    no_overwrite = (data_frame[child_qc_var]!=2)&(data_frame[child_qc_var]!=3)
                                    if row['qc_val'] == 2:
                                        no_overwrite = (data_frame[child_qc_var]!=2)

                                    time_range = (data_frame.index>row['start_date'])&(data_frame.index<row['end_date'])

                                    data_frame.loc[(time_range) & (no_overwrite), child_qc_var] = row['qc_val']
                                except: 
                                    import traceback, sys
                                    print(traceback.format_exc())
                                    print(f"... an 'ALL_*' ({parent_var})variable had an invalid child ({child_var})"+
                                          f"! this should never happen...!!!!")
                                    raise


    if len(problem_rows)>1:
        print(f"\n\n There were some problems with the QC file {table_file}, specifically,"+
              f"{len(problem_rows)} of them...\n\n")
        time.sleep(10)

    else:
        print("…………… CONGRATULATIONS THERE WERE ZERO TYPOS FOR ONCE OMG")

    print("…………… done, returning")

    return data_frame 

def get_qc_table(table_file):

    mos_begin = '20191015 000000'
    mos_end = '20200919 000000'

    def custom_date_parser(d):

        if d == 'beg': d = mos_begin
        elif d=='end': d = mos_end

        try:
            
            hour = (str_two := d.split(' ')[1])[0:2] # no walrus in the trio python
            str_two = d.split(' ')[1]
            hour = str_two[0:2]
            mins = str_two[2:4]
            secs = str_two[4:6]
            date_str = f"{d.split(' ')[0]} {hour}:{mins}:{secs}"

        except:
            print(f" BAD DATE FORMAT!!!! {d}")
            return pd.NaT 

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

    drop_rows = (mqc['start_date'].isna() | mqc['end_date'].isna() | mqc['qc_val'].isna())
    if len(mqc[drop_rows]) > 0:
        print(mqc[drop_rows])
        print(f"\n\n DROPPING THE FOLLOWING QC ROWS DUE TO BAD TIME FORMATTING:\n")
        mqc[drop_rows].index = mqc[drop_rows].index+6 #header adjustment to realign with spreadsheet
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

        tdf = pd.concat([tower_df[f'turbulence_{h}_qc' ], turb_df.copy()[var_list]], axis=1) #_qc is in the tower_df
        tdf.columns = tdf.columns.str.replace(f'_{h}','') # remove height suffix before passing to qc routine
        tdf.columns = tdf.columns.str.replace(f'_{h}_qc','_qc') # remove height suffix before passing to qc routine

        tower_df[f'turbulence_{h}_qc'] = qc_turb_data(tdf)

        sector_qc_info = tower_df[f'wind_sector_qc_info_{h}'] # the info needed to make cuts
        no_overwrite   = (tower_df[f'turbulence_{h}_qc']!=2)&(tower_df[f'turbulence_{h}_qc']!=3)

        tower_df.loc[(sector_qc_info == 10) & (no_overwrite) , f'turbulence_{h}_qc'] = 1 # in polarstern sector
        tower_df.loc[ sector_qc_info == 11                   , f'turbulence_{h}_qc'] = 2 # *and* within footprint
        tower_df.loc[ sector_qc_info == 12                   , f'turbulence_{h}_qc'] = 2 # *and* sigw/ustar thresh

        tower_df.loc[(sector_qc_info == 20) & (no_overwrite) , f'turbulence_{h}_qc'] = 1 # in methut sector
        tower_df.loc[ sector_qc_info == 21                   , f'turbulence_{h}_qc'] = 2 # *and* within footprint
        tower_df.loc[ sector_qc_info == 22                   , f'turbulence_{h}_qc'] = 2 # *and* sigw/ustar thresh

        tower_df.loc[(sector_qc_info == 30) & (no_overwrite) , f'turbulence_{h}_qc'] = 1 # in tower frame sector
        tower_df.loc[ sector_qc_info == 32                   , f'turbulence_{h}_qc'] = 2 # *and* sigw/ustar thresh

        # if pressure missing flag nan, if pressure exists then it's bad data
        tower_df[f'Hl_qc'] = tower_df['turbulence_2m_qc']
        tower_df[f'Hl_qc'] = tower_df['turbulence_2m_qc']

    qc_df = tower_df[['turbulence_10m_qc', 'wspd_vec_mean_10m_qc','temp_10m_qc', 'rh_10m_qc',
                      'atmos_pressure_2m_qc','skin_temp_surface_qc']].copy()
        
    tower_df  = qc_bulk_fluxes(tower_df, qc_df)

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

    tdf['turbulence_qc'] = asfs_df['turbulence_qc'] # init
    tdf['bulk_qc']       = asfs_df['bulk_qc']

    asfs_df[f'turbulence_qc'] = qc_turb_data(tdf)
 
    sector_qc_info = asfs_df[f'wind_sector_qc_info']   
    no_overwrite   = (asfs_df[f'turbulence_qc']!=2)&(asfs_df[f'turbulence_qc']!=3)

    # asfs specific stuff        
    asfs_df.loc[(sector_qc_info == 10) & (no_overwrite), f'turbulence_qc'] = 1 # in polarstern sector
    asfs_df.loc[ sector_qc_info == 11,                   f'turbulence_qc'] = 2 # *and* within footprint
    asfs_df.loc[ sector_qc_info == 12,                   f'turbulence_qc'] = 2 # *and* sigw/ustar thresh

    # if pressure missing flag nan, if pressure exists then it's bad data
    asfs_df[f'Hl_qc'] = asfs_df['turbulence_qc']

    qc_df = asfs_df[['turbulence_qc', 'wspd_vec_mean_qc','temp_qc', 'rh_qc',
                      'atmos_pressure_qc','skin_temp_surface_qc']].copy()
        
    asfs_df  = qc_bulk_fluxes(asfs_df, qc_df)

    tdf['turbulence_qc'] = asfs_df['turbulence_qc'] # re-copy, to be sure nothing weird happens. unnecessary 
    tdf['bulk_qc']       = asfs_df['bulk_qc']

    return asfs_df, turb_df 

def qc_bulk_fluxes(df, qc_df):

    for ic, c in enumerate(qc_df.columns):
        if ic==0: df['bulk_qc'] = qc_df[c]
        else:
            caut_inds = qc_df[c]==1
            bad_inds  = qc_df[c]==2
            eng_inds  = qc_df[c]==3

            df.loc[bad_inds, 'bulk_qc'] = 2 

            # only label caution if it's not bad or engineering
            df.loc[(caut_inds) & (df['bulk_qc']!=2) & (df['bulk_qc']!=3), 'bulk_qc'] = 1

            # only label engineering if it's not bad
            df.loc[(eng_inds) & (df['bulk_qc']!=2), 'bulk_qc']  = 3

    return df

def qc_turb_data(df):

    turbulence_qc = df['turbulence_qc'].copy()
    
    turbulence_qc.loc[(df['ustar'] < 0) & ((turbulence_qc!=2)&(turbulence_qc!=3))] = 1   # ustar < 0 is caution
    turbulence_qc.loc[df['Hs'].isna()] = 2   # missing sensible heat flux means bad turb data

    return turbulence_qc

def define_turb_qc_vars():
    turb_vars_for_qc   = ['ustar', 'Hs']
    return turb_vars_for_qc
 
