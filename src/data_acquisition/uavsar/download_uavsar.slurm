#!/bin/bash
#SBATCH -J download_uavsar # job name
#SBATCH -o /bsuhome/zacharykeskinen/uavsar-coherence/logs/%x-%j.log # output and error file name (%j expands to jobID)
#SBATCH -n 15 # total number of tasks requested
#SBATCH -N 1 # number of nodes you want to run on
#SBATCH -p cryogars # queue (partition)
#SBATCH -t 0-12:00:00 # run time (hh:mm:ss) - 2 days.

echo "Starting."

eval "$(conda shell.bash hook)"
conda activate coherence

echo "Activated environment.."

python -u /bsuhome/zacharykeskinen/uavsar-coherence/src/data_acquisition/uavsar/download_uavsar.py

echo "Done"