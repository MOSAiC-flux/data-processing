# MOSAiC Flux Data

The code and associated libraries that will create the ATMOS flux team data product using observations from the remote 
flux stations and central observatory at the MOSAiC drifting ice campaign in 2019-2020.

** This code is a work in progress ** I'm doing updates in another branch so the current code checked in here might not represent the state of the art changes. Consider this the 'stable' repository and I will check in my changes periodically here. 

## Code description: 

The processing of the data is done in stages via three code pieces, for each the tower and the flux stations. The first piece of code, "*_data_definitions.py" defines the names and attributes of the data for all components of the code. The actual processing of data is done by the "create_" files. Daily level 1 "ingest files" are produced by the "create_level1_*.py", with extremely minimal QC or processing of data. Then, "create_level2_*.py" takes in these level1 ingest files and produces a daily QCed level 2 science product that contains variables relevant for scientific analyses. 

There is also some code in the file "functions_library.py" that provides basic processing functions that are used by all pieces of code. Some of these functions process data and derive useful scientific variables/parameters and others are helper functions that make coding easier.

"change_var_name.py" is a quick and dirty text processing script that will rename the variables inside the code files so that you don't have to manually edit the text for each variable you would like to change. 

Also provided is the code "devour_data_example.py" that should help quickstart looking at the data files we are producing. It brings processed data files into a dataframe and prints some examples. This can be provide to collaborators who are interested in looking at our data so they can get moving on their analysis and don't have to spend time figuring out how to pull in the data. This file pulls in the level 2 data from the flux stations and prints the variables and their

## How to look at and use this code: 

### Git tutorial: 

If you're new to git, there are a few ways to look at this code. The simplest way is to download the package zip file from the download button to the top right of this readme  and then open the code files in your favorite text editor. If you're new to python, you would probably like to use [Anaconda](https://docs.anaconda.com/anaconda/user-guide/getting-started/). If you're using Anaconda, you can make a copy of this code by [installing git](https://anaconda.org/conda-forge/git) and then running `git clone http://USERNAME@gitlab.psd.esrl.noaa.gov/mgallagher/mosaic-flux-data.git` while attached to the VPN. The NOAA documentation for this NOAA hosted GitLab page can be found [in the NOAA PSD user docs here](https://userdocs.psd.esrl.noaa.gov/git)

[A great in depth tutorial on using git and python on the command line can be found at the Earth Lab CU webpage  here](https://www.earthdatascience.org/workshops/setup-earth-analytics-python/)

If you have any questions about running, modifying, or understanding the software, don't hesitate to contact me [Michael Gallagher](mailto:michael.r.gallagher@noaa.gov). I'm happy to help with anything. 

### Required software:

If you would like to run and modify the code to process the raw data files, there are a few pieces of software required. You need:

~~~
python  ≥ 3.6
netCDF4 ≥ 1.3.0
numpy   ≥ 1.13.0
pandas  ≥ 0.20
xarray  ≥ 0.11
~~~

These can be installed in Anaconda with the following command:

~~~
conda install -c anaconda pandas netcdf4 numpy xarray
~~~

### Running the data processing:

Once you have the correct software, the data can be processed by running the create netcdf code directly and providing it with the dates you would like to create, i.e. to run over all of leg 1 and leg 2 with verbose feedback: 

~~~
create_Daily_Tower_NetCDF.py -s 20191015 -e 20200301 --verbose
~~~

There is also a bash script that can parallel process the tower data for you, when run on a server. This can be modified to suit your needs and then run via `./produce_tower_data_parallel.sh`. It was written to run on 8 cores at once so be careful about how you use it.
