# Changelog for major revisions of the tower processing code

## Revision: 0.1, 12/25/2019, M. Gallagher
The Christmas day data beta ... Merry Christmas from the Polarstern!!!

## Revision: 0.2, 2/5/2020, M. Gallagher
Cleaned and fixed things up from the hackey original code base, sent to Chris Cox for collaboration. Have fun on the Dranitsyn Chris!

## Revision 0.3, 2/30/2020  by C. Cox
Presently advancing the Dranitsyn at 0.8 kn with 6 engines on Ludicrous Speed.
- many updates to metadata; global and variable atts, also added cf names as att when applicable
- some modifications to calcs: code is a mix of raw_level_0, qcd_level_1, and derived_level_2:
    striving to make it level_1 & level_2, minimize the "raw": this will take a few iterations
- modified humidity calculations for consistency with vaisala; Wexler
- rotation of sonic coordinates to earth reference frame
- fast data read/despiking/QC/resampling-by-aggregation 20 Hz -> 10 Hz
- Grachev/Fairall turbulence/stress/momentum/MO parameter calculations
- and a few odds and ends
- "stats" are calculated instead of read to account for changes from coordinate transformations
    and QC, though a flag can be flipped to read instead. "good*" currently commented out until
    figure out what we need.
- Concerns/questions flagged with !! throughout.
- Mast headings and GPS headings need a lot of attention for separate reasons


## Revision 0.4, 4/1/2020 by M. Gallagher
Retreating by Dranitsyn like a lepper, happy April fools!
- minor updates to code, fixed small bugs to allow incomplete days to process (aka today)
- allowed days with zero mast data to continue (mid november noodle crash)
- fixed indexing of fast data (indexed and selectable by date) 
- fixed bugs that stopped setting of attributes for resampled stats of 'fast' data
- fixed more bugs that did funny things when running over more than one day of data
- fixed bug that causes missing turbulent flux data at midnight boundary
- big code refactor code to simplify and modularize, rev 0.4
- ... pull out variable definitions for netcdf output into 'define_output_vars.py'
- ... pull out flux calculations and put into 'grachev_fluxcapacitor.py'
- 'time' is now an 'unlimited' dimension, allows simple concatenation of files 
- this refactor included some added documentation that might be helpful

## Revision 0.5 5/25/2020 by M. Gallagher
Major revamping and refactor again, to bring tower code into spec with level 1, level 2, and other group ideas. Too many changes to list but getting closer to a 1.0 release.

## Revision 0.6 7/7/2020 by M. Gallagher
Finalize updates/fixes for leg 3 data and file definitions
- includes many minor changes and improvements after initial commits 
- "noodleville" gps data currently brough into level1 data
- ... but currently neglected in level2 for corrections/orientation/etc
- processing data runs for leg1-leg3 10/15/2019-5/12/2020

## Revision 0.7 7/15/2020 by C. Cox
Added quality control to tower slow instrumentation of level 1 for level 2 in level 2 code
- some dates manually identified, spurious dates hardcoaded and removed
- changes to and implementation of ppl
- despiking where necessary
- removal of some data before tower raise when it is nonsense (e.g. sr50)
- flux plate bury dates estiamted from data, removed prior
- gps qc/hdop/nsat incporporated

Added cor_ice_A10 to the functions_library. This is the COARE/SHEBA (Persson/Andreas) bulk flux algorithm. 
- matlab -> python test data differences 0 to 10^-15 
- additional documentation
- instead of passing LWD, SWD and estimating nets, code now expects netLW and netSW (Cox)
- included rr, rt, rq as outputs
- took nominal zot and zoq out of the loop
- calculating zot, zoq and zo inside the loop now, but not allowing zoq or zot to be smaller than nominal 10^-4 Andreas value
- removed rain rate
- removed cool skin and hardcoded ice concentration to be 1

# Revision 1.0, 8/14/2020 ccox
This is "version 1" of the quality controlled level 2. Many additions including manual screening, automated screening, naming conventions, wind calculations and metadata, 
gps processing, ship distance/bearing, and some variable calculations. The turbulent fluxes are still needeing to be set to 10 min and 30 min with additional variablles 
(covariances) saved and i have removed some wind directions from the mast when the sonic was obviously being rotated in different directions but I don't have notes on this.

# Revision 1.2. 9/8/2020 ccox (pushed later)
Updates specifically to tower were reletively few. Some bug fixes. Some Qc. Updates made to functions library. See ASFS changelog for more details. 
Basically, this is the push for August through mid September by Cox that implemented quality control and "releases" version 1 of level2

## Revision 1.2.1 10/29/2020 ccox
- minor changes to ship_df to accomodate some structural preferences for Leica data location. also updated the leica data.
- minor typos

## Revision 1.3 11/10/2020 ccox
- some revision to the freq dimension in turbulent fluxes after tripping up on 6/25 due to missing 2 m metek
- changed write directory to be the "current" directory within private MOSAIC_dump directory
    - ./MOSAiC_dump/product_development/...
    - level 2 is written to the deveopment directory but level 1 is read from the permenant directory
- changed base time to Unix epoch for level 1 and level 2
- changed filename convention for level 1 to be consistent with level 2 
 
## Revision 1.4 1/1/2021 mgallagher
- modified level1/level2 timing conventions for level1 files to match ARM
- replaced multithreading with multriprocessing and fixed netcdf bugs
    - ... long story, but finally figured it out
- threaded application further to fully utilize new twin behemoths
- int64 time is now uint32
- significant naming convention changes for level2, breaking changes
- some other misc cleaning and improvements
- release level1 and level2 quicklooks with data products
- level1 fast files are now de-grouped and variables post-fixed by level
- new get_data function that's threaded and can pull in level1 or level2 files
- manual qc and flagging has been refactored to a separate file for documentation

## Revision 1.5 1/8/2021 ccox
- remove the relative cal offset from tower temperatures (set to 0). Ola is calculating this and offsets will be entered later when he has them
- heading median filter from 86400 s window -> 21600 s (24 hr -> 6 hr)
- heading median filtering perfomed in unit vector space to accomodate rotations past 0/360 degrees

## Revision 1.99 5/1/2021 mgallagher
- ARM radiation included as a level2 datastream component
- 10hz normalized fast file output for turbulence calculation verification, etc et. al. 
- product reorg, now there is mosmet 1 min files and mosseb 10min files that include turbulent values
- thus there are no more independent turbulence files
- implementation of Ola's met calibration offsets
- attribution for datastreams including ARM and Leeds, as well as data provenance

## Revision 1.99 5/10/2021 mgallagher
- implementation of QC flagging system
- each variable now also includes flags for specific QC scenarios

## Revision 1.999 5/26/2020 ccox
(some of this is asfs)
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




