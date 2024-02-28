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
uavsars = list(uavsar_dir.glob('*')) # sorted
import random
random.shuffle(uavsars)
# remove tmp dir
uavsars = [u for u in uavsars if u != 'tmp']
# get location and flight direction for key and first coherence tiff as value of dictionary
uavsars = {u.stem: list(u.glob('*.cor.grd.tiff'))[0] for u in uavsars if len(list(u.glob('*.cor.grd.tiff'))) > 0}

n = 1000
fig, axes = plt.subplots(2, 1)
locs = []
for i, (uavsar, fp) in tqdm(enumerate(uavsars.items()), total = len(uavsars)):
    if uavsar.split('_')[0] in locs: continue
    locs.append(uavsar.split('_')[0])
    # if i == 2: break
    img = rxa.open_rasterio(fp).squeeze('band', drop = True)
    img = img.rio.write_crs('EPSG:4326').rio.reproject(dst_crs = img.rio.estimate_utm_crs())
    img = img.where((img > 0) & (img < 1))
    # crop out center 5km
    img = img.sel(x = slice(img.x.mean() - 2500, img.x.mean() + 2500), y = slice(img.y.mean() +2500, img.y.mean() - 2500))
    img = img.dropna('x', how = 'all').dropna('y', how = 'all')
    coords = list(product(np.random.choice(img.x, 100), np.random.choice(img.y, 100)))
    values = np.array([img.sel(x = x, y = y).values for x, y in coords]).ravel()
    coords = np.array(coords)[~np.isnan(values)]
    values = values[~np.isnan(values)]
    
    # print(len(values))
    # print(img.std().values)

    # if not fig_dir.joinpath('sampling', f'sampling_{uavsar}.png').exists():
    #     fig_sub, ax_sub = plt.subplots()
    #     img.plot(ax = ax_sub)
    #     ax_sub.scatter(coords[:, 0], coords[:, 1], marker = 'x', s = 1, color = 'black')
    #     fig_sub.savefig(fig_dir.joinpath('sampling', f'sampling_{uavsar}.png'))
    #     plt.close(fig_sub)
    # res = '100m'
    # if not fig_dir.joinpath('coarsen', f'{uavsar}_coarsen_{res}.png').exists():
    #     for (coarsen_x, coarsen_y), res in zip([(1,1), (2,2),(4,4),(6,6), (10,10), (20,20)], ['5m', '10m', '20m', '30m', '50m', '100m']):
    #         fig_sub, ax_sub = plt.subplots()
    #         img.coarsen(x = coarsen_x, y= coarsen_y, boundary = 'trim').mean().plot(ax = ax_sub)
    #         ax_sub.set_title(f'Resolution = {res}')
    #         fig_sub.savefig(fig_dir.joinpath('coarsen', f'{uavsar}_coarsen_{res}.png'))
    #         plt.close(fig_sub)


    V = skg.Variogram(coords, values, n_lags = 300, bin_func = 'uniform', use_nugget = True, model = 'exponential', maxlag = 1000) # maxlag = 20000, n_lags = 100,
    V.plot(axes = axes[0], grid = False, show = False, hist = False)
    V = skg.Variogram(coords, values, n_lags = 300, bin_func = 'uniform', use_nugget = True, model = 'exponential', maxlag = 100) # maxlag = 20000, n_lags = 100,
    V.plot(axes = axes[1], grid = False, show = False, hist = False)
    # V.distance_difference_plot()

# import matplotlib.patches as patches
# rect = patches.Rectangle((ax.get_ylim()[1], 0.1), 0.01, 0.01, linewidth=1, edgecolor='black', facecolor='none')
# axes[0].add_patch(rect)
axes[0].set_xlabel('')
axes[0].set_xlabel('Lag [m]')

for ax in axes:
    [l.set_color("black") for l in ax.get_lines()]
    [l.set_linestyle('--') for l in ax.get_lines()[1::2]]
    [l.set_visible(False) for l in ax.get_lines()[::2]]
    ax.axvline(30)

fig.savefig(fig_dir.joinpath('test.png'))