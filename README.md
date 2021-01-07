# MOSAiC Flux Data

This code and the associated libraries create the ATMOS flux team data product for observations for the three
remote flux stations and the central "met City" observatory at the MOSAiC drifting ice campaign from Oct 2019 to
Oct 2020. The python code found here was primarily developed by [Chris Cox
NOAA](mailto:christopher.j.cox@noaa.gov) (NOAA) and [Michael Gallagher
(CIRES/NOAA)](mailto:michael.r.gallagher@noaa.gov). This code integrates significant data processing work by [Ola
Persson (CIRES/NOAA)](mailto:ola.persson@noaa.gov) and many components are derived from important research on turbulence calculations by Ola Persson, Andrey Grachev (CIRES/NOAA), and Chris Fairall (NOAA). 

## Data description: 

Flux team data products exist at 4 "levels":

  — level 0: raw data, the collection of observation files gathered as data in the field that is ingested to higher level products
  — level 1: raw data that has been re-formatted as binary netCDF files, these files contain only minor changes to the data that are necessary for organization such as sign changes or de-duplication.
  — level 2: preliminary processed data, a 'first-cut' processed data product under active development that evolves as improvements are made
  — level 3: polished release data, a fully integrated data product that is stable for broad user consumption with well documented releases cycles

All processed levels (1-3) are provided as compressed netCDF files aligned closely with ARM specifications for data products. Daily data files are created with the available level 0 data and should be readable with any software package. Scripts that create data quicklooks for each processed level can be found in plot_scripts.

## Code description:

The data processing is done in level-stages seperately for both the tower and the flux stations. Each level is organized into functionally distinct code pieces. Variable names and attributes at all levels are documented and defined in the "*_data_definitions.py". The actual data processing and calculations are done in the "create_" files, and these are the "main" programs that run the data processing. These create functions are threaded across days, meaning if you request a large time range the code will use many CPU cores, this is configurable. Manual data quality control (QC) has been separated into "qc_*" files so that questions about QC and further implementation can be well documented and understood seperate from automated processing routines. 

Data processing functions common to multiple pieces of code or levels are included in "functions_library.py". Some of these functions process data and derive useful scientific variables/parameters and others are helper functions written to make coding easier/simpler. Anything that can be abstracted in a generic way should ideally be separated in this way to minimize code duplication and maximize ease of maintenance. 

The program "change_var_name.py" is provided for simplicity as a quick and dirty way to rename data variables inside the code files so that you don't have to manually edit the text for each variable you would like to change. Backup your code changes before using this, it should make name changes quick but it's a simple program. It searches for variable names in single quotes matching your query and replaces them automagically. 

## How to look at and use this code: 

### Git tutorial: 

If you're new to git, there are a few ways to look at this code. The simplest way is to download the package zip file from the download button to the top right of this readme and then open the code files in your favorite text editor. If you're new to python, you would probably like to use [Anaconda](https://docs.anaconda.com/anaconda/user-guide/getting-started/). If you're using Anaconda, you can make a copy of this code by [installing git](https://anaconda.org/conda-forge/git) and then running `git clone http://USERNAME@gitlab.psd.esrl.noaa.gov/flux/mosaic-flux-data.git` while networked via the VPN. The NOAA documentation for this NOAA hosted GitLab page can be found [in the NOAA PSD user docs here](https://userdocs.psd.esrl.noaa.gov/git)

[A great in depth tutorial on using git and python on the command line can be found at the Earth Lab CU webpage  here](https://www.earthdatascience.org/workshops/setup-earth-analytics-python/)

If you have any questions about running, modifying, or understanding the software, don't hesitate to contact [Michael Gallagher](mailto:michael.r.gallagher@noaa.gov) or [Chris Cox]((mailto:christopher.j.cox@gmail.com)

### Required packages:

If you would like to run and process raw data files, there are a few pieces of software required. You need:

~~~
python  ≥ 3.6
netCDF4 ≥ 1.3.0
numpy   ≥ 1.13.0
pandas  ≥ 0.20
xarray  ≥ 0.11
~~~

Quicklooks plotting is dependent on: 
~~~
matplotlib ≥ 2.0
~~~

These can be installed in Anaconda with the following command:

~~~
conda install -c anaconda pandas netcdf4 numpy xarray matplotlib
~~~

### Running the data processing:

Once you have installed the correct python packages, the data can be processed by running the netcdf "create" code directly and providing it with the dates you would like to run. To process all tower data with verbose feedback: 

~~~
./create_level1_product_tower.py --start 20191015 --end 20200927 --verbose
# ... wait some time... 
./create_level1_product_tower.py --start 20191015 --end 20200927 --verbose
# then plot if you want!
./plot_scripts/plot_tower_lev1_quicklooks.py --start 20191015 --end 20200927 --verbose
./plot_scripts/plot_tower_lev2_quicklooks.py --start 20191015 --end 20200927 --verbose
~~~

Be aware that the data processing and plotting is multi-threaded and will use as much of your CPU as possible. There are also more options/flags available and documented in the code such as creating interstitial "pickle" files that will save you ingest/IO time.
