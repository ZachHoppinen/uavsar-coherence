import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio

# from uavsar_pytools.convert.tiff_conversion import read_annotation 

import matplotlib.pyplot as plt

from pathlib import Path

from tqdm import tqdm

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures')
out_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/gis')
tiff_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/tiffs')

site = 'stlake'
fps = [fp for fp in list(tiff_dir.glob('*')) if site in fp.stem]

for d in tqdm(fps):
    ann = pd.read_csv(list(d.glob('*.csv'))[0], index_col = 0)
    t1, t2 = ann.loc['value', 'start time of acquisition for pass 1'], ann.loc['value', 'start time of acquisition for pass 2']
    t1, t2 = pd.to_datetime(t1).round('d'), pd.to_datetime(t2).round('d')
    if t1.year != 2021: continue
    # heading = ann.loc['value', 'peg heading']
    heading = d.stem.split('_')[1][:3]
    if heading != '091': continue

    concats = []
    for fp in d.glob('*.cor.grd.tiff'):
        pol = fp.stem.split('_')[-2][4:]
        da = xr.open_dataarray(fp).squeeze('band', drop = True).expand_dims(pol = [pol])
        if len(concats) != 0: da = da.rio.reproject_match(concats[0])
        concats.append(da)
    ds = xr.concat(concats, 'pol').sel(pol = ['VV', 'VH', 'HH'])
    ds.rio.to_raster(out_dir.joinpath(f'{pd.to_datetime(t1).date()}_{pd.to_datetime(t2).date()}.tif'))
