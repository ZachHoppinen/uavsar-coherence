from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxa0

from rasterio.enums import Resampling

import matplotlib.pyplot as plt

model_dir = Path('~/scratch/coherence/model').expanduser()
dss = {fp: xr.open_dataset(fp, decode_coords="all") for fp in Path('~/scratch/coherence/uavsar').expanduser().glob('*_full.nc')}

model_dic = {20:'uticam', 15: 'rockmt', 6: 'fraser', 13: 'peeler', 9: 'irnton', 8: 'grmesa', 4: 'alamos', 19: 'stlake', \
            10: 'lowman', 17: 'silver', 3: 'sierra', 0: 'donner', 1: 'dorado'}

model_dic = {v: k for k, v in model_dic.items()}

for fp, ds in dss.items():
    stem = fp.stem.replace('_full', '')
    for var, var_name in zip(['snod', 'smlt', 'swed'], ['model_sd', 'model_melt', 'model_swe']):
        model_fps = list(model_dir.rglob(f'*{var}.nc'))
        model_fp = [fp for fp in model_fps if model_dic[stem] == int(fp.parent.stem)]
        assert len(model_fp) == 1
        model_fp == model_fp[0]
        model = xr.open_dataset(model_fp[0], decode_coords="all")
        model = model.rename({'date':'model_time'}).rio.reproject_match(ds, resampling = Resampling.bilinear) # .rio.write_crs('EPSG:4326')
        ds[var_name] = model[var]
    ds.drop_vars('band').to_netcdf(fp.parent.joinpath(stem + '_v2.nc'))