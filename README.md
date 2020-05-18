# MOSAiC Flux Data

The code and associated libraries that will create the ATMOS flux team data product using observations from the remote 
flux stations and central observatory at the MOSAiC drifting ice campaign in 2019-2020.

** This code is a work in progress ** I'm doing updates in another branch so the current code checked in here might not represent the state of the art changes. Consider this the 'stable' repository and I will check in my changes periodically here. 

## Code description: 

There are three components to the code. The file that does the actual processing, including QC, data ingest, and writing of files ("create_Daily_*_NetCDF.py"). The file that defines the variables that will be written to disk and their attributes ("*_variable_definitions.py). And a library of useful homebrewed functions ("functions_library.py"), the place where general functions that are used for data processing are located, such as functions that turn observations into turbulent fluxes, etc, et al. Depending on what you're looking for, you should look in one of these three files.

We also provide a "devour_data_example.py" that should help quickstart  looking at the data files we are producing. It  brings processed data files into a dataframe and prints some examples. This can be provide to collaborators who are interested in looking at our data so they can get moving on their analysis.

## How to look at and use this code: 

### Git tutorial: 

If you're new to git, there are a few ways to look at this code. The simplest way is to download the package zip file from the download button to the top right of this readme  and then open the code files in your favorite text editor. If you're new to python, you would probably like to use [Anaconda](https://docs.anaconda.com/anaconda/user-guide/getting-started/). If you're using Anaconda, you can make a copy of this code by [installing git](https://anaconda.org/conda-forge/git) and then running `git clone http://USERNAME@gitlab.psd.esrl.noaa.gov/mgallagher/mosaic-flux-data.git` while attached to the VPN. The NOAA documentation for this NOAA hosted GitLab page can be found (in the NOAA PSD user docs here)[https://userdocs.psd.esrl.noaa.gov/git]

[A great in depth tutorial on using git and python on the command line can be found at the Earth Lab CU webpage  here](https://www.earthdatascience.org/workshops/setup-earth-analytics-python/)

If you have any questions about running, modifying, or understanding the software, don't hesitate to contact me (Michael Gallagher)[mailto:michael.r.gallagher@noaa.gov]. I'm happy to help with anything. 

### Required software:

If you would like to run and modify the code to process the raw data files, there are a few pieces of software required. You need:

~~~
python  ≥ 3.6
netCDF4 ≥ 1.3.0
numpy   ≥ 1.13.0
pandas  ≥ 0.20 
~~~

These can be installed in Anaconda with the following command:

~~~
conda install -c anaconda pandas netcdf4 numpy
~~~

### Running the data processing:

Once you have the correct software, the data can be processed by running the create netcdf code directly and providing it with the dates you would like to create, i.e. to run over all of leg 1 and leg 2 with verbose feedback: 

~~~
create_Daily_Tower_NetCDF.py -s 20191015 -e 20200301 --verbose
~~~

There is also a bash script that can parallel process the data for you, when run on a server. This can be modified to suit your needs and then run via `./produce_tower_data_parallel.sh`. It was written to run on 8 cores at once so be careful about how you use it.
