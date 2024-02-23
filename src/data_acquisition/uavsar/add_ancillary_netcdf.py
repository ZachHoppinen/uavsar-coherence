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

# from contextlib import suppress
# with suppress(KeyError): 

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures')

trees = xr.open_dataarray('/bsuhome/zacharykeskinen/scratch/coherence/trees/nlcd/nlcd_2016_treecanopy_2019_08_31.img').squeeze('band', drop =  True)
lc = xr.open_dataarray('/bsuhome/zacharykeskinen/scratch/coherence/land-cover/nlcd_2019_land_cover_l48_20210604.img').squeeze('band', drop =  True)

out_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/')
sites = sorted(list(out_dir.glob('*.nc')))

for site in sites:
    # if site.stem != 'lowman': continue
    print(site)
    
    ds = xr.open_dataset(site)
    ds = ds.rio.write_crs('epsg:4326')

    ## Adding in DEM
    geom = ds.rio.bounds()
    ds['dem'] = py3dep.get_dem(geom, 30).drop_vars('spatial_ref').rio.write_crs('EPSG:4326').rio.reproject_match(ds)

    ## Adding in lidar
    lidar_abbrev = {'stlake': 'USUTLC', 'silver': 'USIDRC', 'lowman': ['USIDDC', 'USIDMC', 'USIDBS'], 'grmesa': 'USCOGM', 'fraser': 'USCOFR', 'rockmt': 'USCOCP'}
    # note we are overwritting one of the VH if there are two. But we only need one measurement of VH
    VHs = {fp.stem.split('_')[4]:fp for fp in Path('/bsuhome/zacharykeskinen/scratch/coherence/lidar').glob('*VH*.tif')}
    # here we grab snow depth specifically
    SDs = {'_'.join(fp.stem.split('_')[4:6]):fp for fp in Path('/bsuhome/zacharykeskinen/scratch/coherence/lidar').glob('*SD*.tif')}

    if site.stem != 'lowman' and site.stem in lidar_abbrev.keys():
        vh_fp = VHs[lidar_abbrev[site.stem]]
        date = vh_fp.stem.split('_')[5]
        vh = xr.open_dataarray(vh_fp).squeeze('band', drop = True).rio.reproject_match(ds['dem']) #.expand_dims(time = [pd.to_datetime(date)])
        ds['vh'] = vh.where((vh < 100) & (vh > 0))

        try:
            sd_fps = [value for key, value in SDs.items() if lidar_abbrev[site.stem] in key]
            if len(sd_fps) == 0: raise KeyError
            sds = []
            for sd_fp in sd_fps:
                date = sd_fp.stem.split('_')[5]
                sd = xr.open_dataarray(sd_fp).squeeze('band', drop = True).rio.reproject_match(ds['dem']).expand_dims(time = [pd.to_datetime(date)])
                sd = sd.where((sd > 0) & (sd < 30))
                sds.append(sd)

            if len(sds) == 1: sd = sds[0]
            else: sd = xr.concat(sds, 'time')

            ds['sd'] = sd

        except KeyError: pass

    elif site.stem == 'lowman':
        lowman_lidars = {'vh': [], 'sd': []}
        for lidar_name in lidar_abbrev[site.stem]:
            lowman_lidars['vh'].append(VHs[lidar_name])
            lowman_lidars['sd'].extend([value for key, value in SDs.items() if lidar_name in key])
        for i, fp in enumerate(lowman_lidars['vh']):
            vh_sub = xr.open_dataarray(fp).squeeze('band', drop = True).rio.reproject_match(ds['dem'])
            vh_sub = vh_sub.where((vh_sub > 0) & (vh_sub < 100))
            if i == 0: vh = vh_sub
            else: vh = vh.combine_first(vh_sub)

        for i, fp in enumerate(lowman_lidars['sd']):
            date = pd.to_datetime(fp.stem.split('_')[5])
            sub = xr.open_dataarray(fp).squeeze('band', drop = True).rio.reproject_match(ds['dem']).expand_dims(time = [pd.to_datetime(f'{date.year}-{date.month:02d}-01')])
            sub = sub.where((sub > 0) & (sub < 30))
            if i == 0: sd = sub
            else: sd = sd.combine_first(sub)
        ds['sd'] = sd

    else:
        print('no lidar')

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

    lc_clip = lc.rio.clip_box(*img_bds, crs = 'EPSG:4326')
    # reproject and mask out areas where the interpolation led to artifacts
    lc_clip = lc_clip.rio.reproject_match(ds['dem'])
    # add to dataset
    ds['land_cover'] = lc_clip

    ## Adding in plots

    ds['dem'].plot()
    plt.savefig(fig_dir.joinpath('dems', site.stem+'_dem.png'))
    plt.close()

    ds['tree_perc'].plot()
    plt.savefig(fig_dir.joinpath('trees', site.stem+'_trees.png'))
    plt.close()

    ds['land_cover'].plot()
    plt.savefig(fig_dir.joinpath('land-cover', site.stem+'_lc.png'))
    plt.close()

    if 'sd' in ds.data_vars:
        for t in ds.time:
            if (~ds['sd'].sel(time = t).isnull()).sum == 0: continue
            ds['sd'].sel(time = t).plot()
            plt.savefig(fig_dir.joinpath('sd', site.stem+f'{t.values}_sd.png'))
            plt.close()
    
    if 'vh' in ds.data_vars:
        ds['vh'].plot()
        plt.savefig(fig_dir.joinpath('vh', site.stem+'_vh.png'))
        plt.close()

    print(ds)
    print(ds.dims)
    print(ds.coords)
    print(ds.encoding)

    ds = ds.drop_vars('band').drop_vars('spatial_ref')
    
    ds.to_netcdf(site.parent.joinpath(site.stem + '_full.nc'), encoding = {'x': {'dtype':'int16'}, 'y': {'dtype':'int16'}})