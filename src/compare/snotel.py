import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt

from pathlib import Path

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures')

snotels = Path('/bsuhome/zacharykeskinen/scratch/coherence/snotels').rglob('*.csv')
uavsars = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/')