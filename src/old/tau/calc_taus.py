"""
Fits the temporal baseline exponential decay function for each pixel of all study sites

Links:
https://docs.xarray.dev/en/stable/generated/xarray.Dataset.curvefit.html

https://github.com/pydata/xarray/blob/6d98dbd644ac264c9c67db78d9a5ae011019b0ec/doc/user-guide/computation.rst#L562

https://github.com/pydata/xarray/pull/4849
"""

from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxa
import dask 

from taus import fit_coh_decay_model, decorrelation_temporal_model

indir = Path('/bsuhome/zacharykeskinen/scratch/data/uavsar/coherence')
outdir = Path('/bsuhome/zacharykeskinen/scratch/data/uavsar/coherence/taus')

for loc_fp in indir.glob('*.nc'):
    try:
        if outdir.joinpath(loc_fp.name.replace(' ', '-')).exists():
            continue
            
        vv_cor = xr.open_dataset(loc_fp)
        vv_cor = vv_cor.drop('band')
        t_delta = pd.to_timedelta(vv_cor.flight2 - vv_cor.time)
        vv_cor['temporal_baseline'] = xr.DataArray(t_delta / pd.to_timedelta('1 day'), coords = {"time": vv_cor.time})
        vv_cor = vv_cor.chunk({'x': 100, 'y': 100})
        res = vv_cor['vv_coh'].curvefit(coords = vv_cor.temporal_baseline, func = decorrelation_temporal_model, reduce_dims = 'time', p0 = {'gamma_inf' : 0.3, 'tau': 5}, bounds={"gamma_inf": (0, 0.6)}, kwargs = {'maxfev': 5000})
        res.to_netcdf(outdir.joinpath(loc_fp.name.replace(' ', '-')))
    except RuntimeError as re:
        print(f'Runtime error for {loc_fp}')
        print(re)
        