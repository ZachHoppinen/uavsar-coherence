#!/bin/bash
#SBATCH -J create_coherence_netcdf # job name
#SBATCH -o /bsuhome/zacharykeskinen/uavsar-coherence/logs/%x-%j.log # output and error file name (%j expands to jobID)
#SBATCH -n 1 # total number of tasks requested
#SBATCH -N 1 # number of nodes you want to run on
#SBATCH -p bsudfq # queue (partition)
#SBATCH -t 0-06:00:00 # run time (hh:mm:ss) - 3 hours

echo "Starting."

eval "$(conda shell.bash hook)"
conda activate coherence

echo "Activated environment.."

python -u /bsuhome/zacharykeskinen/uavsar-coherence/src/data_acquisition/uavsar/make_netcdf.py
python -u /bsuhome/zacharykeskinen/uavsar-coherence/src/data_acquisition/uavsar/add_ancillary_netcdf.py

echo "Done"