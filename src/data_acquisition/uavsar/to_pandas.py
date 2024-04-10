from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
import seaborn as sns

import sys
sys.path.append('../../funcs')
from xarray_tools import find_cor_ts

dss = {fp.stem: xr.open_dataset(fp) for fp in Path('~/scratch/coherence/uavsar').expanduser().glob('*_tau.nc')}

for pol in ['VV', 'HH', 'VH', 'HV']:
    print(pol)
    res = pd.DataFrame()
    for stem, ds in dss.items():
        times = find_cor_ts(ds)
        print(stem)
        for heading, t1, t2 in times:
            df = ds.sel(heading = heading, time1 = t1, time2 = t2).drop_vars(['curvefit_covariance','model_sd','model_swe','model_melt']).drop_dims(['cov_i', 'cov_j','model_time']).sel(param = 'tau', pol = pol).to_dataframe()
            df = df.dropna(subset = ['cor'])
            df['site'] = stem.replace('_tau', '')
            res = pd.concat([df, res])
    res.to_parquet(Path(f'~/scratch/coherence/uavsar/{pol}.parq').expanduser())