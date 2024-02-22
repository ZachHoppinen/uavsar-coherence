import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio

import py3dep
from pyproj import Transformer


# from uavsar_pytools.convert.tiff_conversion import read_annotation 

import matplotlib.pyplot as plt

from pathlib import Path

from tqdm import tqdm

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures')

trees = xr.open_dataarray('/bsuhome/zacharykeskinen/scratch/coherence/trees/nlcd/nlcd_2016_treecanopy_2019_08_31.img').squeeze('band', drop =  True)
lc = xr.open_dataarray('/bsuhome/zacharykeskinen/scratch/coherence/land-cover/nlcd_2019_land_cover_l48_20210604.img').squeeze('band', drop =  True)

out_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/')
sites = list(out_dir.glob('*.nc'))

for site in sites:
    ds = xr.open_dataset(site)
    ds = ds.rio.write_crs('epsg:4326')

    ## Adding in DEM
    geom = ds.rio.bounds()
    ds['dem'] = py3dep.get_dem(geom, 30).drop_vars('spatial_ref').rio.write_crs('EPSG:4326').rio.reproject_match(ds)

    ## Adding in trees
    # find bounds in this datasets crs to clip it before reprojecting
    # https://pyproj4.github.io/pyproj/stable/api/transformer.html
    transformer = Transformer.from_crs("epsg:4326","epsg:5070", always_xy = True)

    img_bds = ds.rio.bounds()
    img_bds = [img_bds[0] - 1, img_bds[1] - 1, img_bds[2] + 1, img_bds[3] + 1]
    bds = list(transformer.transform(*img_bds[:2]))
    bds.extend(list(transformer.transform(*img_bds[2:])))
    # clip big raster to our area
    tree_perc = trees.rio.clip_box(*bds)
    # reproject and mask out areas where the interpolation led to artifacts
    tree_perc = tree_perc.rio.reproject_match(ds['dem'])
    tree_perc = tree_perc.where((tree_perc >= 0) & (tree_perc < 100)) # percentage bounds 0-100
    # add to dataset
    ds['tree_perc'] = tree_perc

    ## Adding in landcover
    # transformer = Transformer.from_crs("epsg:4326","epsg:7030", always_xy = True)
    # bds = list(transformer.transform(*img_bds[:2]))
    # bds.extend(list(transformer.transform(*img_bds[2:])))

    # print(lc.spatial_ref.attrs['crs_wkt'])
    lc_clip = lc.rio.clip_box(*img_bds, crs = 'EPSG:4326')
    # reproject and mask out areas where the interpolation led to artifacts
    lc_clip = lc_clip.rio.reproject_match(ds['dem'])
    # add to dataset
    ds['land_cover'] = lc_clip


    # print((~ds['tree_perc'].isnull()).sum())
    # print((~ds['dem'].isnull()).sum())

    ds['dem'].plot()
    plt.savefig(fig_dir.joinpath('dems', site.stem+'_dem.png'))
    plt.close()

    ds['tree_perc'].plot()
    plt.savefig(fig_dir.joinpath('trees', site.stem+'_trees.png'))
    plt.close()

    ds['land_cover'].plot()
    plt.savefig(fig_dir.joinpath('land-cover', site.stem+'_lc.png'))
    plt.close()

    
    # ds.to_netcdf(site.parent.joinpath(site.stem + '_full.nc'))