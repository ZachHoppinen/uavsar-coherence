import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio

# from uavsar_pytools.convert.tiff_conversion import read_annotation 

import matplotlib.pyplot as plt

from pathlib import Path

from tqdm import tqdm

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures')

uavsars = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/tiffs').rglob('*.cor.grd.tiff')
uavsars = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar').rglob('*.cor.grd.tiff')

uavsars = {u.stem: u for u in sorted(uavsars)}

out_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/')

import math
def decimal_degree_to_meters(lat1, lon1, lat2, lon2):  # generally used geo measurement function
    """
    https://stackoverflow.com/questions/639695/how-to-convert-latitude-or-longitude-to-meters
    """
    R = 6378.137 # Radius of earth in KM
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000; # meters

for site in np.unique([k.split('_')[0] for k in uavsars.keys()]):
    if out_dir.joinpath(site + '.nc').exists(): continue
    print(site)
    dss = {value: xr.open_dataarray(value).squeeze('band', drop = True) for key, value in uavsars.items() if site in key.lower()}
    concat_dss = []
    
    headings = {}
    for i, (fp, ds) in tqdm(enumerate(dss.items()), total = len(dss)):

        ann = pd.read_csv(list(fp.parent.glob('*.csv'))[0], index_col = 0)
        
        t1, t2 = ann.loc['value', 'start time of acquisition for pass 1'], ann.loc['value', 'start time of acquisition for pass 2']
        # round to day to match heading dates
        t1, t2 = pd.to_datetime(t1).round('d'), pd.to_datetime(t2).round('d')
        # heading = ann.loc['value', 'peg heading']
        heading = int(fp.stem.split('_')[1][:3])
        if heading not in headings: headings[heading] = fp

        pol = fp.stem.split('_')[-2][4:]

        lat_ddeg, lon_ddeg = float(ann.loc['value', 'grd_phs.row_mult']), float(ann.loc['value', 'grd_phs.col_mult'])
        lat, lon = float(ann.loc['value', 'grd_mag.row_addr']), float(ann.loc['value', 'grd_mag.col_addr'])

        row_res, col_res = decimal_degree_to_meters(lat, lon, lat + lat_ddeg,lon), decimal_degree_to_meters(lat, lon, lat,lon +lon_ddeg)

        row_multi_to30, col_multi_to30 = round(30/ row_res), round(30/col_res)

        ds = ds.coarsen(x = col_multi_to30, y = row_multi_to30, boundary = 'pad').mean()
        if i != 0:
            ds = ds.rio.reproject_match(concat_dss[0])
        
        ds = ds.expand_dims(heading = [heading])
        ds = ds.expand_dims(time1 = [t1])
        ds = ds.expand_dims(time2 = [t2])
        ds = ds.expand_dims(pol = [pol])

        ds.attrs['lat_looks'] = row_multi_to30
        ds.attrs['lon_looks'] = col_multi_to30

        concat_dss.append(ds) # .chunk()

    ds = xr.combine_by_coords(concat_dss).rename({'band_data': 'cor'})
    ds = ds.where((ds > 0) & (ds < 1))
    
    incs = []
    for heading, fp in headings.items():
        inc = xr.open_dataarray(list(fp.parent.glob('*.inc.tiff'))[0]).squeeze('band', drop = True)
        inc = inc.rio.reproject_match(concat_dss[0]).expand_dims(heading = [heading])
        inc = inc.where((inc < 100) & (inc > -100))
        incs.append(inc)
    
    ds['inc'] = xr.concat(incs, 'heading')
    
    for heading in ds.heading.values:
        ds['inc'].sel(heading = heading).plot()
        plt.savefig(fig_dir.joinpath('inc', site + '_' + str(heading) +'_inc.png'))
        plt.close()

    ds = ds.dropna('x', how = 'all').dropna('y', how = 'all')

    ds['time1'] = pd.to_datetime(ds.time1)
    ds['time2'] = pd.to_datetime(ds.time2)

    from itertools import product
    for t1, t2 in product(ds.time1, ds.time2):
        if (~ds['cor'].sel(time1 = t1, time2 = t2).isel(heading = 0, pol = 0).isnull()).sum() == 0: continue
        
        ds['cor'].sel(time1 = t1, time2 = t2).isel(heading = 0, pol = 0).plot()
        plt.savefig(fig_dir.joinpath('coherence', site + '_cor.png'))
        plt.close()
        break

    print(ds)

    from dask.diagnostics import ProgressBar

    out_file = out_dir.joinpath(site + '.nc')
    ds.to_netcdf(out_file)
    # write_job = ds.to_netcdf(out_file, compute=False)
    # with ProgressBar():
        # print(f"Writing to {out_file}")
        # write_job.compute()