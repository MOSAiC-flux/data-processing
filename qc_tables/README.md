# QC table information

This subdirectory contains the tables from the manual, human-led, QC flagging process. It's a bit complex, as it needs to take into consideration various of the detailed properties of the data. There are hierarchies of variables, special qc variable references (the ALL_* flags that have children), and an understanding of which variables do what. To avoid spaghetti code an attempt was made to make the underlying code generically applicable to both ASFS and tower data files. That means there are some divergent sections where asfs/tower specific code couldn't be avoided for varying reasons.

## Table locations:

The original spreadsheets can be found in the NOAA google drive under the title at [the url MOSAiCFlux_QC_Flagging.xlsx](https://docs.google.com/spreadsheets/d/1CgrC5zb9t6fZn8Nn5dnrkVSvmiqBD2Jl/edit?pli=1#gid=1176467439), I think clicking that will work if you are logged into your NOAA email. 

## Uploading/processing a new table

If you've modified the spreadsheet and want that ingested by the code, you can File->Download it from drive as a CSV and then put the file into this directory. There is a bash script, clean_tables.sh, that will reorder the spreadsheet by the priority of qc flag that also has some sed-lines that will replace the typos that have been commonly made over the months. Once the file is in this directory and you run a create_level2* code, the new flags will be ingested. If the code finds an error in a row and doesn't understand the date, or the variable field, because of a human error it will print the line number and the associated error. You must manually fix the csv file or the spreadsheet and go through the process again. This 'checker' function can be run manually via ipython etc et al before running the create* code if so desired. 

## Wind sector QC:

qc_level2.py also contains some functions that manually qc for the wind sector depending on the locations of various objects throughout the MOSAiC year. This code is highly specific and hopefully decently documented. Wind sector cautions do *not* overwrite the maual flags present in the flagging csv/spreadsheet. 