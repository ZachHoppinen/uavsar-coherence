from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

import sys
sys.path.append('../../funcs/')
from taus import fit_coh_decay_model, decorrelation_temporal_model
from xarray_tools import find_cor_ts

for fp in Path('~/scratch/coherence/uavsar/').glob('*_v3.nc'):
    print(fp)
    if fp.parent.joinpath(fp.stem + '_tau.nc').exists(): continue
    ds = xr.open_dataset(fp)
    ds = ds.assign_coords(delta_t = (ds.time2 - ds.time1).dt.days)
    if 'VV' not in ds.pol: continue
    ts = find_cor_ts(ds)
    concats = []
    for heading, t1, t2 in ts:
        da = ds['cor'].sel(heading = heading, time1 = t1, time2 = t2)
        da = da.expand_dims(delta_t = [pd.Timedelta((t2 - t1)).days], heading = [heading])
        concats.append(da)
    dts = xr.concat(concats, 'delta_t')
    tau = dts.curvefit(coords = dts.delta_t, func = decorrelation_temporal_model, reduce_dims = 'delta_t', p0 = {'gamma_inf' : 0.3, 'tau': 5}, bounds={"gamma_inf": (0, 0.6)}, kwargs = {'maxfev': 5000})
    # how to interpert covariance matrix:
    # https://www.quora.com/How-do-you-interpret-the-estimated-covariance-of-the-parameters-for-a-nonlinear-regression-equation-returned-by-the-curve_fit-function-from-SciPy#:~:text=In%20nonlinear%20regression%2C%20the%20curve_fit,covariance%20matrix%20for%20the%20parameters.
    ds = xr.merge([ds, tau])
    ds.to_netcdf(fp.parent.joinpath(fp.stem + '_tau.nc'))
