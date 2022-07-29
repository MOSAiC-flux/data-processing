#!/bin/sh

# MGallagher came across a really weird issue (bug?) where calls to numpy/scipy made in the
# functions_library (grache_fluxcapacitor) were being threaded on all cores of the host computer. But!
# Not only was this not asked for, it seeemed to be *slowing* performance, somehow. This might be
# because the overhead in creating a bunch child processes and then passing the internal program state
# to those children is not worth the relatively short computations made by this function (we only
# process ~8000 data points per function call)? Or it could be that these children aren't doing what
# they say they're doing...
#
# In either case, ditching the numpy/scipy threading speeds up the processing somehow *and* keeps the
# program from thrashing the CPU on shared computational resources.
#
# Also also. These environment variables need to be inherited by the python process. If you set them in os.environ,
# even at the very top of the program before imports, doesn't work. Annoying. 
#
# Thus, if you're running the code from a bash prompt, you need to source this file and then run the code. 
# My workflow looks like this:
#
# tmux new-session -n 'mosaic_run_python'
# source fix_numpy_scipy.sh
# time nice -n 20 ./plot_asfs_lev2_quicklooks.py -v -s 20191005 -e 20201001 -pd ./ -p /Projects/MOSAiC_internal/flux_data_tests/

# just in case... avoids some netcdf nonsense involving the default file locking across mounts
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export HDF5_USE_FILE_LOCKING=1
export HDF5_MPI_OPT_TYPES=1
export HDF5_DEBUG=0

