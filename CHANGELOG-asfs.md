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
