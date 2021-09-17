# #####################################################################
# these functions take the full dataset and return the same  dataset
# with more nans. if you provide a subset of data it will work though.
# 

import numpy  as np
import pandas as pd

pd.options.mode.use_inf_as_na = True # no inf values anywhere

from datetime  import datetime

global nan,Rd,K_offset,h2o_mass,co2_mass,sb,emis
nan      = np.NaN
Rd       = 287     # gas constant for dry air
K_offset = 273.15  # convert C to K
h2o_mass = 18      # are the obvious things...
co2_mass = 44      # ... ever obvious?
sb       = 5.67e-8 # stefan-boltzmann
emis     = 0.985   # snow emis assumption following Andreas, Persson, Miller, Warren and so on

def qc_stations(curr_station, station_data):

    if 'asfs30' in curr_station:
#        # ##############
#        #
#        # When the RH sensor is powered, it needs to warm up and so you get bd data for 20 min or so.
#        # Also, some bad data around the time a station goes off. Hand-edited here.
#
#        # garbage setup data setup... the  ol'e Fedorov hold, I think
#        station_data['rh'] .loc[                           :datetime(2019,10,7,2,9)]    = nan 
#        station_data['rh'] .loc[datetime(2019,11,12,11,9)  :datetime(2019,11,12,12,43)] = nan
#        station_data['rh'] .loc[datetime(2019,11,30,11,15) :datetime(2019,11,30,15,25)] = nan 
#        station_data['rh'] .loc[datetime(2020,3,4,10,31)   :datetime(2020,3,4,10,48)]   = nan 
#        station_data['rh'] .loc[datetime(2020,3,6,3,0)     :datetime(2020,3,6,4,56)]    = nan 
#        station_data['rh'] .loc[datetime(2020,3,17,12,51)  :datetime(2020,3,17,13,23)]  = nan 
#        station_data['rh'] .loc[datetime(2020,3,30,9,0)    :datetime(2020,3,30,9,36)]   = nan  
#        station_data['rh'] .loc[datetime(2020,3,30,12,5)   :datetime(2020,3,31,2,55)]   = nan  
#        station_data['dew_point']     .loc[                           :datetime(2019,10,7,2,9)]    = nan 
#        station_data['dew_point']     .loc[datetime(2019,11,12,11,9)  :datetime(2019,11,12,12,43)] = nan 
#        station_data['dew_point']     .loc[datetime(2019,11,30,11,15) :datetime(2019,11,30,15,25)] = nan
#        station_data['dew_point']     .loc[datetime(2020,3,4,10,31)   :datetime(2020,3,4,10,48)]   = nan
#        station_data['dew_point']     .loc[datetime(2020,3,6,3,0)     :datetime(2020,3,6,4,56)]    = nan
#        station_data['dew_point']     .loc[datetime(2020,3,17,12,51)  :datetime(2020,3,17,13,23)]  = nan
#        station_data['dew_point']     .loc[datetime(2020,3,30,9,0)    :datetime(2020,3,30,9,36)]   = nan 
#        station_data['dew_point']     .loc[datetime(2020,3,30,12,5)   :datetime(2020,3,31,2,55)]   = nan
#
#        # a couple hiccups in temps
#        station_data['temp']     .loc[                           :datetime(2019,10,7,1,11)]   = nan
#        station_data['dew_point'] .loc[                           :datetime(2019,10,7,1,11)]   = nan
#        station_data['temp']     .loc[datetime(2019,10,7,6,33)   :datetime(2019,10,7,6,36)]   = nan
#        station_data['dew_point'] .loc[datetime(2019,10,7,6,33)   :datetime(2019,10,7,6,36)]   = nan
#        station_data['temp']     .loc[datetime(2019,11,12,11,18) :datetime(2019,11,12,12,41)] = nan 
#        station_data['dew_point'] .loc[datetime(2019,11,12,11,18) :datetime(2019,11,12,12,41)] = nan 
#        station_data['temp']     .loc[datetime(2019,11,30,12,0)  :datetime(2019,11,30,15,23)] = nan 
#        station_data['dew_point'] .loc[datetime(2019,11,30,12,0)  :datetime(2019,11,30,15,23)] = nan 
#        station_data['temp']     .loc[datetime(2020,2,26,21,30)  :datetime(2020,2,26,21,45)]  = nan   
#        station_data['dew_point'] .loc[datetime(2020,2,26,21,30)  :datetime(2020,2,26,21,45)]  = nan
#        station_data['temp']     .loc[datetime(2020,3,6,3,0)     :datetime(2020,3,6,4,58)]    = nan
#        station_data['dew_point'] .loc[datetime(2020,3,6,3,0)     :datetime(2020,3,6,4,58)]    = nan
#        station_data['temp']     .loc[datetime(2020,3,30,12,27)  :datetime(2020,3,31,2,52)]   = nan
#        station_data['dew_point'] .loc[datetime(2020,3,30,12,27)  :datetime(2020,3,31,2,52)]   = nan
#        station_data['temp']     .loc[datetime(2020,3,31,10,41)  :datetime(2020,3,31,15,0)]   = nan
#        station_data['dew_point'] .loc[datetime(2020,3,31,10,41)  :datetime(2020,3,31,15,0)]   = nan  
#        station_data['temp']     .loc[datetime(2020,5,5,9,9)    :datetime(2020,5,5,9,14)]    = nan
#        station_data['dew_point'] .loc[datetime(2020,5,5,9,9)     :datetime(2020,5,5,9,14)]   = nan
#        station_data['temp']     .loc[datetime(2020,5,5,14,43)    :datetime(2020,5,5,14,44)]    = nan
#        station_data['dew_point'] .loc[datetime(2020,5,5,14,43)     :datetime(2020,5,5,14,44)]   = nan
#
#        station_data['rh'] .loc[datetime(2020,3,31,10,41):datetime(2020,3,31,15,0)] = nan
#
#        station_data['brightness_temp_surface'] .loc[datetime(2020,3,5,18,24):datetime(2020,3,5,18,32)] = nan
#
#        # Removing data from the flux plates prior to being buried in October and April and some other nonsense
#        station_data['subsurface_heat_flux_A'] .loc[:datetime(2019,10,7,4,53)] = nan # after initial install, this is when it equillibrated
#        station_data['subsurface_heat_flux_B'] .loc[:datetime(2019,10,7,4,16)] = nan # after initial install, this is when it equillibrated
#
#        # the plate was plugged in but not installed at first, jsut hanging in a loop on the frame
#        station_data['subsurface_heat_flux_A'] .loc[datetime(2020,4,7,12,0):datetime(2020,4,15,12,47)] = nan 
#        station_data['subsurface_heat_flux_A'] .loc[datetime(2020,3,5,18,23):datetime(2020,3,5,18,32)] = nan # probably when chris turned it back on?
#        station_data['subsurface_heat_flux_B'] .loc[datetime(2020,3,5,18,23):datetime(2020,3,5,18,32)] = nan # probably when chris turned it back on?

        # Fix the flux plates that were insalled upside down
        station_data['subsurface_heat_flux_A'] = station_data['subsurface_heat_flux_A'] * -1
        station_data['subsurface_heat_flux_B'].loc[datetime(2020,4,1,0,0):] = station_data['subsurface_heat_flux_B'].loc[datetime(2020,4,1,0,0):] * -1

#        # A fan on the LWD failed during installation and Chris failed to notice :( It appeared to stay
#        # clear until clearing skies midday 10/8. It was fixed again on Nov 6.  I'm manually screening
#        # instead of thresholding fan spin because it is less restrictive, allowong for some likely good data to go thru.
#        station_data['down_long_hemisp'] .loc[datetime(2019,10,8,11,49):datetime(2019,11,6,9,7)] = nan
#
#        # two stray points without enough context for auto-qc
#        station_data['sr50_dist'] .loc[datetime(2020,1,5,19,30):datetime(2020,1,5,20,15)] = nan
#
#        # These are shadows
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,17,9,40)  :datetime(2020,4,17,9,43)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,21,23,22) :datetime(2020,4,21,23,24)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,1,12)  :datetime(2020,4,22,1,17)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,2,11)  :datetime(2020,4,22,2,15)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,9,19)  :datetime(2020,4,22,9,26)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,23,18) :datetime(2020,4,22,23,20)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,1,7)   :datetime(2020,4,23,1,13)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,2,6)   :datetime(2020,4,23,2,11)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,9,22)  :datetime(2020,4,23,9,25)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,23,18) :datetime(2020,4,23,23,21)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,1,8)   :datetime(2020,4,24,1,14)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,2,7)   :datetime(2020,4,24,2,12)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,9,24)  :datetime(2020,4,24,9,26)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,25,1,9)   :datetime(2020,4,25,1,15)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,25,2,9)   :datetime(2020,4,25,2,14)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,25,9,16)  :datetime(2020,4,25,9,24)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,1,7)   :datetime(2020,4,26,1,13)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,2,8)   :datetime(2020,4,26,2,12)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,9,18)  :datetime(2020,4,26,9,29)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,27,9,25)  :datetime(2020,4,27,9,35)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,10,21,20) :datetime(2020,5,10,21,26)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,10,22,17) :datetime(2020,5,10,22,28)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,18,13) :datetime(2020,6,22,18,20)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,30,22,6)  :datetime(2020,6,30,22,19)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,7,22,19,6)  :datetime(2020,7,22,19,19)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,7,22,19,59) :datetime(2020,7,22,20,9)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,8,6,1,12)   :datetime(2020,8,6,2,8)]    = nan
#        
#        # a couple others that snuck through
#        station_data['down_short_hemisp'] .loc[datetime(2020,3,31,14,48):datetime(2020,3,31,14,50)] = nan 
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,7,12,36):datetime(2020,4,7,12,37)] = nan 
#        station_data['down_long_hemisp'] .loc[datetime(2020,3,17,12,44):datetime(2020,3,17,12,46)] = nan
#
#        # some sr50 times that are not easily auto-qc'd
#        station_data['sr50_dist'] .loc[datetime(2020,1,5,20,16):datetime(2020,1,6,11,12)] = nan
#        station_data['sr50_dist'] .loc[datetime(2020,1,7,22,54):datetime(2020,1,7,22,57)] = nan
#
#        # some weirdness in the gps sometimes when the system shuts off
#        station_data['lat']     .loc[datetime(2019,11,12,11,7):datetime(2019,11,12,12,56)] = nan 
#        station_data['lon']     .loc[datetime(2019,11,12,11,7):datetime(2019,11,12,12,56)] = nan 
#        station_data['ship_distance']   .loc[datetime(2019,11,12,11,7):datetime(2019,11,12,12,56)] = nan 
#        station_data['ship_bearing']    .loc[datetime(2019,11,12,11,7):datetime(2019,11,12,12,56)] = nan 
#        station_data['ice_alt']         .loc[datetime(2019,11,12,11,7):datetime(2019,11,12,12,56)] = nan 
#        station_data['heading'] .loc[datetime(2019,11,12,11,7):datetime(2019,11,12,12,56)] = nan
#
#        station_data['lat']     .loc[datetime(2020,2,26,21,28):datetime(2020,2,26,22,0)] = nan 
#        station_data['lon']     .loc[datetime(2020,2,26,21,28):datetime(2020,2,26,22,0)] = nan 
#        station_data['ship_distance']   .loc[datetime(2020,2,26,21,28):datetime(2020,2,26,22,0)] = nan 
#        station_data['ship_bearing']    .loc[datetime(2020,2,26,21,28):datetime(2020,2,26,22,0)] = nan 
#        station_data['ice_alt']         .loc[datetime(2020,2,26,21,28):datetime(2020,2,26,22,0)] = nan 
#        station_data['heading'] .loc[datetime(2020,2,26,21,28):datetime(2020,2,26,22,0)] = nan 
#
#        station_data['lat']     .loc[datetime(2020,3,6,3,0):datetime(2020,3,6,5,5)] = nan 
#        station_data['lon']     .loc[datetime(2020,3,6,3,0):datetime(2020,3,6,5,5)] = nan 
#        station_data['ship_distance']   .loc[datetime(2020,3,6,3,0):datetime(2020,3,6,5,5)] = nan 
#        station_data['ship_bearing']    .loc[datetime(2020,3,6,3,0):datetime(2020,3,6,5,5)] = nan 
#        station_data['ice_alt']         .loc[datetime(2020,3,6,3,0):datetime(2020,3,6,5,5)] = nan 
#        station_data['heading'] .loc[datetime(2020,3,6,3,0):datetime(2020,3,6,5,5)] = nan 
#
#        station_data['lat']     .loc[datetime(2020,3,27,18,25):datetime(2020,3,27,18,55)] = nan 
#        station_data['lon']     .loc[datetime(2020,3,27,18,25):datetime(2020,3,27,18,55)] = nan 
#        station_data['ship_distance']   .loc[datetime(2020,3,27,18,25):datetime(2020,3,27,18,55)] = nan 
#        station_data['ship_bearing']    .loc[datetime(2020,3,27,18,25):datetime(2020,3,27,18,55)] = nan 
#        station_data['ice_alt']         .loc[datetime(2020,3,27,18,25):datetime(2020,3,27,18,55)] = nan 
#        station_data['heading'] .loc[datetime(2020,3,27,18,25):datetime(2020,3,27,18,55)] = nan 
#
#        station_data['lat']     .loc[datetime(2020,3,31,10,42):datetime(2020,3,31,14,10)] = nan 
#        station_data['lon']     .loc[datetime(2020,3,31,10,42):datetime(2020,3,31,14,10)] = nan 
#        station_data['ship_distance']   .loc[datetime(2020,3,31,10,42):datetime(2020,3,31,14,10)] = nan 
#        station_data['ship_bearing']    .loc[datetime(2020,3,31,10,42):datetime(2020,3,31,14,10)] = nan 
#        station_data['ice_alt']         .loc[datetime(2020,3,31,10,42):datetime(2020,3,31,14,10)] = nan 
#        station_data['heading'] .loc[datetime(2020,3,31,10,42):datetime(2020,3,31,14,10)] = nan 
#
#        station_data['lat']     .loc[datetime(2020,4,15,11,58):datetime(2020,4,15,12,13)] = nan 
#        station_data['lon']     .loc[datetime(2020,4,15,11,58):datetime(2020,4,15,12,13)] = nan 
#        station_data['ship_distance']   .loc[datetime(2020,4,15,11,58):datetime(2020,4,15,12,13)] = nan 
#        station_data['ship_bearing']    .loc[datetime(2020,4,15,11,58):datetime(2020,4,15,12,13)] = nan 
#        station_data['ice_alt']         .loc[datetime(2020,4,15,11,58):datetime(2020,4,15,12,13)] = nan 
#        station_data['heading'] .loc[datetime(2020,4,15,11,58):datetime(2020,4,15,12,13)] = nan 
#                       
#        # acoustic temp
#        station_data['temp_acoustic'] .loc[datetime(2019,11,10,13,58) :datetime(2019,11,12,0,0)] = nan
#        station_data['temp_acoustic'] .loc[datetime(2020,3,31,23,7) :datetime(2020,3,31,23,8)] = nan

    elif 'asfs40' in curr_station:

        # ##############
        #

#        # When the RH sensor is powered, it needs to warm up and so you get bd data for 20 min or so.
#        # Also, some bad data around the time a station goes off. Hand-edited here.
#        station_data['rh']        .loc[datetime(2019,11,8,7,52)   :datetime(2019,11,8,9,28)]   = nan 
#        station_data['rh']        .loc[datetime(2020,2,27,2,1)    :]                           = nan # that's all she wrote
#        station_data['dew_point'] .loc[datetime(2019,11,8,7,52)   :datetime(2019,11,8,9,28)]   = nan 
#        station_data['dew_point'] .loc[datetime(2020,2,27,2,1)    :]                           = nan # that's all she wrote
#
#        # Hiccup
#        station_data['temp']      .loc[datetime(2019,12,25,10,14) :datetime(2019,12,25,10,14)] = nan
#        station_data['dew_point'] .loc[datetime(2019,12,25,10,14) :datetime(2019,12,25,10,14)] = nan
#        station_data['temp']      .loc[datetime(2020,2,4,6,50)    :datetime(2020,2,4,6,50)]    = nan
#        station_data['dew_point'] .loc[datetime(2020,2,4,6,50)    :datetime(2020,2,4,6,50)]    = nan
#
#        # Some nonsense in the FP that needed to go
#        station_data['subsurface_heat_flux_A'] .loc[datetime(2019,10,15,5,23):datetime(2019,10,15,6,0)] = nan

        # Fix the flux plates that were insalled upside down
        station_data['subsurface_heat_flux_A'] = station_data['subsurface_heat_flux_A'] * -1
        station_data['subsurface_heat_flux_B'] = station_data['subsurface_heat_flux_B'] * -1

        # what on earth happend here?
       # station_data['ice_alt'] .loc[datetime(2019,11,7,20,30):datetime(2019,11,10,15,46)] = nan

    elif 'asfs50' in curr_station:

#        # ##############
#        #
#        # When the RH sensor is powered, it needs to warm up and so you get bd data for 20 min or so.
#        # Also, some bad data around the time a station goes off. Hand-edited here.
#        station_data['rh'] .loc[                          :datetime(2019,10,10,1,14)] = nan # firing it up in October
#        station_data['rh'] .loc[datetime(2020,1,30,13,21) :datetime(2020,1,30,13,37)] = nan 
#        station_data['rh'] .loc[datetime(2020,2,5,3,2)    :datetime(2020,2,5,3,6)]    = nan 
#        station_data['rh'] .loc[datetime(2020,4,14,12,43) :datetime(2020,4,14,12,49)] = nan 
#        station_data['rh'] .loc[datetime(2020,6,25,7,29)  :datetime(2020,6,25,7,43)]  = nan 
#        station_data['rh'] .loc[datetime(2020,9,24,8,34)  :datetime(2020,9,24,10,19)] = nan # flat lines...maybe station failed?
#        station_data['rh'] .loc[datetime(2020,9,25,12,38) :datetime(2020,9,25,13,3)]  = nan
#
#        station_data['dew_point']     .loc[                          :datetime(2019,10,10,1,14)] = nan # firing it up in October
#        station_data['dew_point']     .loc[datetime(2020,1,30,13,21) :datetime(2020,1,30,13,37)] = nan 
#        station_data['dew_point']     .loc[datetime(2020,2,5,3,2)    :datetime(2020,2,5,3,6)]    = nan 
#        station_data['dew_point']     .loc[datetime(2020,4,14,12,43) :datetime(2020,4,14,12,49)] = nan 
#        station_data['dew_point']     .loc[datetime(2020,6,25,7,29)  :datetime(2020,6,25,7,43)]  = nan 
#        station_data['dew_point']     .loc[datetime(2020,9,24,8,34)  :datetime(2020,9,24,10,19)] = nan # flat lines...maybe station failed?
#        station_data['dew_point']     .loc[datetime(2020,9,25,12,38) :datetime(2020,9,25,13,3)]  = nan
#
#        # Temp weirdness at on/off
#        station_data['temp']         .loc[datetime(2020,1,22,21,28) :datetime(2020,1,23,0,15)]   = nan
#        station_data['dew_point']     .loc[datetime(2020,1,22,21,28) :datetime(2020,1,23,0,15)]   = nan
#        station_data['temp']         .loc[datetime(2020,4,4,16,45) :datetime(2020,4,5,12,0)]    = nan
#        station_data['dew_point']     .loc[datetime(2020,4,4,16,45)  :datetime(2020,4,5,12,0)]    = nan
#
#        # ??
#        station_data['temp']         .loc[datetime(2019,12,6,12,23):datetime(2019,12,6,13,12)]  = nan
#        station_data['dew_point']     .loc[datetime(2019,12,6,12,23):datetime(2019,12,6,13,12)]  = nan
#        station_data['rh'] .loc[datetime(2019,12,6,12,23):datetime(2019,12,6,13,12)]  = nan
#
#        # zeros that are isolated and fall through the auto-qc
#        station_data['temp']         .loc[datetime(2020,2,5,5,24)  :datetime(2020,2,5,6,0)]     = nan
#        station_data['dew_point']     .loc[datetime(2020,2,5,5,24)  :datetime(2020,2,5,6,0)]     = nan
#        station_data['temp']         .loc[datetime(2020,4,4,10,48) :datetime(2020,4,4,18,0)]    = nan
#        station_data['dew_point']     .loc[datetime(2020,4,4,10,48) :datetime(2020,4,4,18,0)]    = nan    
#        station_data['body_T_IRT']           .loc[datetime(2020,4,4,9,36)  :datetime(2020,4,5,14,24)]   = nan
#        station_data['brightness_temp_surface']        .loc[datetime(2020,4,4,9,36)  :datetime(2020,4,5,14,24)]   = nan
#
#        # FP equillibrating and some other nonsense
#        station_data['subsurface_heat_flux_A']     .loc[datetime(2020,4,15,13,54) :datetime(2020,4,15,14,21)] = nan 
#        station_data['subsurface_heat_flux_A']     .loc[datetime(2020,2,1,1,10)   :datetime(2020,2,3,16,26)]  = nan 
#        station_data['subsurface_heat_flux_B']     .loc[                          :datetime(2019,10,10,1,51)] = nan 
#        station_data['subsurface_heat_flux_B']     .loc[datetime(2020,2,1,1,24)   :datetime(2020,2,4,1,17)]   = nan 
#        station_data['subsurface_heat_flux_B']     .loc[datetime(2020,4,5,0,0)    :datetime(2020,5,2,23,59)]  = nan

        # Fix the flux plates that were insalled upside down
        station_data['subsurface_heat_flux_B'] = station_data['subsurface_heat_flux_B'] * -1
        station_data['subsurface_heat_flux_A'].loc[datetime(2020,4,1,0,0):] = station_data['subsurface_heat_flux_A'].loc[datetime(2020,4,1,0,0):] * -1

#        # Removing data from the flux plates prior to being buried in October and April
#        station_data['subsurface_heat_flux_A'] .loc[datetime(2020,2,3,12,0):datetime(2020,2,5,12,0)] = nan # I think when L3 got flipped the plates were exposed??
#        station_data['subsurface_heat_flux_B'] .loc[datetime(2020,2,3,12,0):datetime(2020,2,5,12,0)] = nan # I think when L3 got flipped the plates were exposed??
#
#        # These are shadows
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,17,10,41) :datetime(2020,4,17,10,50)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,17,12,26) :datetime(2020,4,17,12,28)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,17,13,0)  :datetime(2020,4,17,13,3)]  = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,21,22,15) :datetime(2020,4,21,22,20)] = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,21,23,1)  :datetime(2020,4,21,23,16)] = nan
#        station_data['up_short_hemisp'] .loc[datetime(2020,4,21,23,1)  :datetime(2020,4,21,23,16)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,21,23,25) :datetime(2020,4,21,23,35)] = nan
#        station_data['up_short_hemisp'] .loc[datetime(2020,4,21,23,25) :datetime(2020,4,21,23,35)] = nan 
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,8,24)  :datetime(2020,4,22,8,26)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,8,57)  :datetime(2020,4,22,9,0)]   = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,10,13) :datetime(2020,4,22,10,16)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,10,38) :datetime(2020,4,22,10,40)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,10,25) :datetime(2020,4,22,10,31)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,11,59) :datetime(2020,4,22,12,2)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,12,33) :datetime(2020,4,22,12,35)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,22,10) :datetime(2020,4,22,22,15)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,22,23,3)  :datetime(2020,4,22,23,29)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,22,22,55) :datetime(2020,4,22,23,29)] = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,8,22)  :datetime(2020,4,23,8,24)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,8,56)  :datetime(2020,4,23,8,58)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,10,13) :datetime(2020,4,23,10,15)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,10,23) :datetime(2020,4,23,10,31)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,10,35) :datetime(2020,4,23,10,37)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,11,57) :datetime(2020,4,23,12,1)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,12,33) :datetime(2020,4,23,12,35)] = nan 
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,22,12) :datetime(2020,4,23,22,17)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,22,47) :datetime(2020,4,23,23,8)]  = nan 
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,23,22,47) :datetime(2020,4,23,23,7)]  = nan 
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,23,23,21) :datetime(2020,4,23,23,28)] = nan 
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,23,23,21) :datetime(2020,4,23,23,28)] = nan 
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,8,24)  :datetime(2020,4,24,8,26)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,8,58)  :datetime(2020,4,24,9,1)]   = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,10,15) :datetime(2020,4,24,10,18)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,10,24) :datetime(2020,4,24,10,37)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,11,57) :datetime(2020,4,24,11,59)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,12,33) :datetime(2020,4,24,12,34)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,22,13) :datetime(2020,4,24,22,17)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,22,59) :datetime(2020,4,24,23,9)]  = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,24,22,59) :datetime(2020,4,24,23,9)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,24,23,22) :datetime(2020,4,24,23,25)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,24,23,21) :datetime(2020,4,24,23,30)] = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,25,22,11) :datetime(2020,4,25,22,14)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,25,23,2)  :datetime(2020,4,25,23,14)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,25,22,59) :datetime(2020,4,25,23,14)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,25,23,19) :datetime(2020,4,25,23,23)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,4,25,23,19) :datetime(2020,4,25,23,23)] = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,8,29)  :datetime(2020,4,26,8,31)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,9,4)   :datetime(2020,4,26,9,7)]   = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,10,21) :datetime(2020,4,26,10,37)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,11,57) :datetime(2020,4,26,11,59)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,26,22,15) :datetime(2020,4,26,22,20)] = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,27,8,36)  :datetime(2020,4,27,8,39)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,27,9,12)  :datetime(2020,4,27,9,15)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,27,10,29) :datetime(2020,4,27,10,41)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,27,12,2)  :datetime(2020,4,27,12,5)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,30,10,31) :datetime(2020,4,30,10,39)] = nan
#
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,2,8,40)   :datetime(2020,5,2,8,41)]   = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,2,9,18)   :datetime(2020,5,2,9,21)]   = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,2,10,33)  :datetime(2020,5,2,10,39)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,2,11,55)  :datetime(2020,5,2,11,57)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,2,12,33)  :datetime(2020,5,2,12,35)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,5,2,22,19)  :datetime(2020,5,2,22,24)]  = nan
#        
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,21,8,57)  :datetime(2020,6,21,9,2)]   = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,21,14,3)  :datetime(2020,6,21,14,45)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,21,14,48) :datetime(2020,6,21,15,35)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,8,47)  :datetime(2020,6,22,8,52)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,12,52) :datetime(2020,6,22,12,56)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,12,58) :datetime(2020,6,22,13,4)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,13,7)  :datetime(2020,6,22,13,8)]  = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,13,43) :datetime(2020,6,22,14,17)] = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,6,22,14,24) :datetime(2020,6,22,15,36)] = nan
#        
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,21,8,57)  :datetime(2020,6,21,9,2)]   = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,21,14,3)  :datetime(2020,6,21,14,45)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,21,14,48) :datetime(2020,6,21,15,35)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,22,8,47)  :datetime(2020,6,22,8,52)]  = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,22,12,52) :datetime(2020,6,22,12,56)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,22,12,58) :datetime(2020,6,22,13,4)]  = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,22,13,7)  :datetime(2020,6,22,13,8)]  = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,22,13,43) :datetime(2020,6,22,14,17)] = nan
#        station_data['up_short_hemisp']   .loc[datetime(2020,6,22,14,24) :datetime(2020,6,22,15,36)] = nan
#        
#        station_data['down_short_hemisp'] .loc[datetime(2020,7,1,2,55)   :datetime(2020,7,1,3,3)]    = nan
#        station_data['down_short_hemisp'] .loc[datetime(2020,8,6,1,12)   :datetime(2020,8,6,2,3)]    = nan
#           
#        # and a couple other hiccups
#        station_data['down_short_hemisp'] .loc[datetime(2020,4,4,9,36)   :datetime(2020,4,5,14,24)]  = nan
#        station_data['up_short_hemisp'] .loc[datetime(2020,4,4,9,36)   :datetime(2020,4,5,14,24)]  = nan
#
#        # some weirdness in the gps sometimes when the system shuts off
#        station_data['lat']           .loc[datetime(2020,2,5,3,7):datetime(2020,2,5,3,24)] = nan 
#        station_data['lon']           .loc[datetime(2020,2,5,3,7):datetime(2020,2,5,3,24)] = nan 
#        station_data['ship_distance'] .loc[datetime(2020,2,5,3,7):datetime(2020,2,5,3,24)] = nan 
#        station_data['ship_bearing']  .loc[datetime(2020,2,5,3,7):datetime(2020,2,5,3,24)] = nan 
#        station_data['ice_alt']       .loc[datetime(2020,2,5,3,7):datetime(2020,2,5,3,24)] = nan 
#        station_data['heading']       .loc[datetime(2020,2,5,3,7):datetime(2020,2,5,3,24)] = nan
#        
#        # acoustic temp
#        station_data['temp_acoustic'] .loc[datetime(2020,1,22,21,56) :datetime(2020,1,22,22,50)] = nan
#        station_data['temp_acoustic'] .loc[datetime(2020,8,5,9,54)   :datetime(2020,8,5,9,55)]   = nan
#
#        # data gap due to fast data stream issues early on 
#        station_data['temp_acoustic'] .loc[datetime(2020,1,22,21,56) :datetime(2020,1,22,22,50)] = nan
#        station_data['temp_acoustic'] .loc[datetime(2020,8,5,9,54)   :datetime(2020,8,5,9,55)]   = nan
        

    return station_data;

