#!/usr/bin/env bash

# fix typos programmatically

for f in *.csv;
do
      sed -i 's/metek_x/wspd_u_mean/g' $f 
      sed -i 's/metek_y/wspd_v_mean/g' $f 
      sed -i 's/metek_z/wspd_w_mean/g' $f 
      sed -i 's/up_long_hemisph/up_long_hemisp/g' $f 
      sed -i 's/up_long_hemisph/up_long_hemisp/g' $f 
      sed -i '/acoustic_temp/d' $f
      sed -i 's/apogee_targ_T/brightness_surface_temperature/g' $f
      sed -i 's/apogee_targ_T/brightness_surface_temperature/g' $f
      sed -i 's/apogee_body_T/brightness_surface_temperature/g' $f
      sed -i 's/body_T_IRT/brightness_temp_surface/g' $f
      sed -i 's/CO2_flux/co2_licor/g' $f
      sed -i 's/tower_ice_alt/sr50_dist/g' $f
      sed -i 's/ice_alt/sr50_dist/g' $f
      sed -i 's/heading_tower/tower_heading/g' $f
      sed -i 's/heading_mast/mast_heading/g' $f
      sed -i 's/ALL_BULK/bulk/g' $f 
      sed -i 's/ALL_EC_FIELDS/turbulence/g' $f 
done

./reorder_tables.py
