from pathlib import Path

import numpy as np
import pandas as pd

import rioxarray as rxa

import matplotlib.pyplot as plt

import skgstat as skg

from tqdm import tqdm

from itertools import product

np.random.seed(42)

print('Starting...')
home_dir = Path('/Users/rdcrlzh1/Documents/uavsar-coherence/')
home_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/')
fig_dir = home_dir.joinpath('figures', 'variograms')

uavsar_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/tiffs/')

# get list of uavsars directories
uavsars = sorted(list(uavsar_dir.glob('*')))
# remove tmp dir
uavsars = [u for u in uavsars if u != 'tmp']
# get location and flight direction for key and first coherence tiff as value of dictionary
uavsars = {u.stem: list(u.glob('*.cor.grd.tiff'))[0] for u in uavsars if len(list(u.glob('*.cor.grd.tiff'))) > 0}

n = 1000
fig, ax = plt.subplots()
for i, (uavsar, fp) in tqdm(enumerate(uavsars.items()), total = len(uavsars)):
    if i == 1: break
    img = rxa.open_rasterio(fp).squeeze('band', drop = True)
    img = img.rio.write_crs('EPSG:4326').rio.reproject(dst_crs = img.rio.estimate_utm_crs())
    img = img.where((img > 0) & (img < 1))
    img = img.sel(x = slice(img.x.mean() - 1000, img.x.mean() + 1000), y = slice(img.y.mean() +1000, img.y.mean() - 1000))
    img = img.dropna('x', how = 'all').dropna('y', how = 'all')
    coords = list(product(np.random.choice(img.x, 100), np.random.choice(img.y, 100)))
    values = np.array([img.sel(x = x, y = y).values for x, y in coords]).ravel()
    coords = np.array(coords)[~np.isnan(values)]
    values = values[~np.isnan(values)]
    
    print(len(values))
    print(img.std().values)
    fig_sub, ax_sub = plt.subplots()
    img.plot(ax = ax_sub)
    ax_sub.scatter(coords[:, 0], coords[:, 1], marker = 'x', s = 1, color = 'black')
    fig_sub.savefig(fig_dir.joinpath(f'test_img_{uavsar}.png'))

    V = skg.Variogram(coords, values, bin_func = 'scott', use_nugget = True, model = 'exponential', ) # maxlag = 20000, n_lags = 100,
    V.plot(axes = ax, grid = False, show = False, hist = False)
    # V.distance_difference_plot()

# [l.set_color("black") for l in ax.get_lines()]
# [l.set_linestyle('--') for l in ax.get_lines()[1::2]]
# [l.set_visible(False) for l in ax.get_lines()[::2]]
fig.savefig(fig_dir.joinpath('test.png'))