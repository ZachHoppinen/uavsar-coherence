#!/bin/bash
#SBATCH -J tau_calc # job name
#SBATCH -o /bsuhome/zacharykeskinen/uavsar-coherence/logs/%x-%j.log # output and error file name (%j expands to jobID)
#SBATCH -n 8 # total number of tasks requested
#SBATCH -N 1 # number of nodes you want to run on
#SBATCH -p bsudfq # queue (partition)
#SBATCH -t 24:00:00 # run time (hh:mm:ss) - 1 minute in this example.

echo "Starting."

eval "$(conda shell.bash hook)"
conda activate proj

echo "Activated environment.."

python -u /bsuhome/zacharykeskinen/uavsar-coherence/src/data_acquisition/tau/calc_taus.py

echo "Done"