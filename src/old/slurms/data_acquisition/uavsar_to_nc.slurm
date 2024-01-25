#!/bin/bash
#SBATCH -J uavsar_to_nc # job name
#SBATCH -o /bsuhome/zacharykeskinen/uavsar-coherence/logs/%x-%j.log # output and error file name (%j expands to jobID)
#SBATCH -n 1 # total number of tasks requested
#SBATCH -N 1 # number of nodes you want to run on
#SBATCH -p bsudfq # queue (partition)
#SBATCH -t 24:00:00 # run time (hh:mm:ss) - 1 minute in this example.

echo "Starting."

eval "$(conda shell.bash hook)"
conda activate coherence

echo "Activated environment.."

python -u /bsuhome/zacharykeskinen/uavsar-coherence/src/data_acquisition/uavsar/uavsar_to_nc.py

echo "Done"