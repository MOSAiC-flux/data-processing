# Changelog for major revisions of the tower processing code

## Revision: 0.1, 4/10/2020, M. Gallagher
From the tower to the stations, creating the code foundation. Hard to comment on a few thousand lines of code.

## Revision: 0.2, 6/12/2020 M. Gallagher
A ramshackle path forward but getting there. Code was changed to split data processing into level1 and level2 files, including a preliminary turbulent flux product, according to groupspecificationss. "change_var_name.py" was created to provide a quick/easy way to change output variable names inthe code quickly so that you don't have to manually edit by hand.

## Revision 0.3 8/19/2020 ccox
This revision was for create_level1_product_asfs.py with some asosociated additions to asds_definitions.py
-turned off hdf5 locking because its a menace
-changed data_dir to be a passed argument and adjusted paths to generalize, like the tower codes
-expanded the search to +/- 1 day from start_time and end_time and trimmed back at day_series similar to tower code so that individual days could be -calculated and because I think may be needed in some cases, and because I’m shifting by 1 min (see below)
-shifted slow times by 1 min. the logger records dates by end of avg period so we map 00:01-00:00 onto our convention 00:00-23:59 
-shifted fast times by -5s, as above
-made some hand-edits to the “sdcard” directories to make sure they said “sdcard” instead of working in some complicated search
-added a drop_duplicates in the read
-rewrote the way the that column headings are selected
-q -> qq because python spyder explodes if you dare assign variable one-char names, especially q! i never had this problem in the tower codes, but it I am here. python is a trip. wacky bugs in here…
-stopped it from searching for hidden files (‘._*’)
-got rid of the licor_indexes nan filling because it actually isn’t needed…the missing cols are added and fill automatically with nan to be conv to -9999

## Revision 1.2. 9/8/2020 ccox

This is not exhaustive. I’ve lost track a bit. Basically, this is the push for August through mid September by Cox that implemented quality control and "releases" version 1 of level2

note that running codes has asfs# and path args now. can run multiple or 1 asfs.

runfile(‘/path/mosaic-flux-data/create_level2_product_tower.py',args='-s 20191015 -e 20200312 -p /psd3data/arctic/ --verbose')
runfile(‘/procmosaic-flux-data/create_level2_product_asfs.py',args='-s 20200407 -e 20200503 -p /psd3data/arctic/MOSAiC/ -a asfs50 --verbose')

ASFS
- paths
- pass station name(s) as argument
- hdf5
- file naming conventions changed to match matt’s arm-like suggestion
- expanded start_time/end_time by a day to buffer gps smoothing
- variables names, attributes updates
- bug fixes to calc_fluxes = False
- set height of sonic to 3.3 m for turb calc
- added ephemeris
- increased search range of spurious “0.0” finder
- recalculated slow liquor from qc’d fast

QC:
- many, many changes. See external QC documentation

Turbulence
- added bulk to ASFS
- removed high freq calc (“_hi”) and replaced with sequential runs using 10 and 30 min windows
- changed netcdf write to accept multi dimensions
- saved spectra/cospectra/freq
- worked on first guess in bulk, did not change
- improved contants by passing measurements where there used to be guesses
- removed Cd/zot from bulk loop, which I put in earlier
- added a sanity check ppl on Cd for EC and bulk (-1.5e-3,1.5e-2).  allowance for Cd<0 fit around tail of distribution, ie., allows for noise about 0. 
- added latent heat flux, Hl
- added cos mass flux (mg m^-2 s^-1)
- add Webb corrections for Hl and co2 fluxes
- added saved variables, many edits to attributes

## Revision 1.2.1 10/29/2020 ccox

- added metadata for Leg 4 ASFS 
- minor changes to ship_df to accomodate some structural preferences for Leica data location. also updated the leica data.
- minor typos


