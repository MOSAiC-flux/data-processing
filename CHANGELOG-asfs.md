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

## Revision 1.3 11/10/2020 ccox
- changed write directory to be the "current" directory within private MOSAIC_dump directory.
    - ./MOSAiC_dump/product_development/...
    - level 2 is written to the deveopment directory but level 1 is read from the permenant directory
- moved directory paths up front and cleaned up a little
- changed base time to Unix epoch for level 1 and level 2
- changed filename convention for level 1 to be consistent with level 2

## Revision 1.4 1/1/2020 mgallagher
- modified level1/level2 timing conventions for level1 files to match ARM
- replaced multithreading with multriprocessing and fixed netcdf bugs
    - ... long story, but finally figured it out
- threaded application further to fully utilize new twin behemoths
- int64 time is now uint32
- significant naming convention changes for level2, breaking changes
- some other misc cleaning and improvements
- release level1 and level2 quicklooks with data products
- new get_data function that's threaded and can pull in level1 or level2 files
- manual qc and flagging has been refactored to a separate file for documentation

## Revision 1.5 1/8/2021 ccox
- rh equilibration periods in asfs50 legs 4/5 removed
- heading median filter from 86400 s window -> 21600 s (24 hr -> 6 hr)
- heading median filtering perfomed in unit vector space to accomodate rotations past 0/360 degrees

## Revision 1.999 5/26/2021 ccox
(some of this is tower)
- Webb correction recalculated to be flux with correction applied (rather than just the correction) and attributes updated accordingly
- Fixed type in bulk_Hl_Webb_10m
- Added “defined positive upwards” clarity to flux plate long_names. Tower & ASFS
- Global attribute “11 m flux tower” to “Met City”
- Added get_arm_radiation_data to create_level2_product_asfs.py 
- When available PSPdif (PSPglobal*SPN1dif/SPN1tot) is used to correct SR30 SWD for tilt, else parametrized. Missing values from ARM replaced with param.
- Flipped all tower flux plate data *-1 so it is defined as positive upward = positive ocean warms ice, as in autumn
- Flipped ASFS30’s FPB beginning Apr 1.
- Flipped ASFS50’s FPA beginning Apr 1.
- Assigned location attribute for arm to be “Met City”
- Updated the IR20 bias coefficient from 1.42 to 1.28
- Updated attributes for tower/mast wind vectors to be met convention: U = west-to-east (eastward) and V = south-to-north (northward)
- Added u,v,w min means to ASFS level 2 and attributes as above
- Changed all u,v conventions to be meteorological, as above, for tower, mast, and asfs
- Refined height reporting in ASFS attributes
- Several typos were found in the tower and ASFS attributes and were corrected
- Added metadata for SR50 initialization for Leg 5

## Revision 2.0 7/15/21 
- Added initialization metadata for the tower in Legs 4 & 5. In Leg 4 two initializations, the original tower raise and after SR50 moved on the boom.
- Fixed error in U, V caught by Byron 7/15/21
- Re-checked and updated attribute corrections from Matt “level2 version2 — updated summary and information” email
- Made version 1.9999 to 2.0

## Revision 2.1 9/8/21
- Remove Kurt_* and Skew_* from turbulent vars
- Include sigmas for rotated versions of u/v/w
- Renamed cross-stream and streamwise u/v/w to U/V/W to distinguish from earth u/v/w and expanded attribute long-names to spell it out 
- Add a more strict second level of despiking (Fairall despik.m) to the 10 min turbulent flux periods
- Add missing SWD > 50 qualifier for the Rayleigh limit test from ASFS QCRAD.
- len(fdt.inx) > 1 to len(fdt.index > 0 in ASFS top of turbulence: fixes NaN issue showing up in turbulent netcdf instead of -9999 (reported by Amy)
- Fix missing multidimensionality in 10 min file spectral vars when no turbulence at all for the day (reported by Amy)


## Revision 3.0 2/9/22 mgallagher
- ingest of manual qc table (https://docs.google.com/spreadsheets/d/1CgrC5zb9t6fZn8Nn5dnrkVSvmiqBD2Jl/edit#gid=302154633)
- corresponding qc variables 
- differential algorithm to despike outside of variance
- other minor bugfixes
