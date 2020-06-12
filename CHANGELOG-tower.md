# Changelog to track changes between major revisions for the tower processing code


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

