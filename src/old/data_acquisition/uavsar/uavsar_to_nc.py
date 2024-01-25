from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rxa

from datetime import datetime

img_dir = Path('/bsuhome/zacharykeskinen/scratch/data/uavsar/images')
outdir = Path('/bsuhome/zacharykeskinen/scratch/data/uavsar/coherence')

# for each location directory
for loc_dir in img_dir.glob('*'):

    print(loc_dir)
    # prepare to load cors into this 
    cors = []
    incs = []
    
    # get flight directions
    flight_dirs = np.unique( [d.stem.split('_')[1][:3] for d in loc_dir.glob('*_grd')])
    for flight_direction in flight_dirs:
        print(flight_direction)

        flight_dir_inc = None

        out_nc = outdir.joinpath(f"{loc_dir.stem.replace(', ','-')}_{flight_direction}_VV.nc")
        if Path(out_nc).exists():
            continue

        # for each image pair directory
        for pair_dir in loc_dir.glob(f'*_{flight_direction}*_grd'):

            # snag incidence angle file
            inc_fp = next(pair_dir.glob('*.inc.tiff'))

            # snag annotation file 
            ann = pd.read_csv(next(pair_dir.glob('*.csv')), index_col = 0)

            for tiff_fp in pair_dir.glob('*cor.grd.tiff'):

                if not flight_dir_inc:
                    # prep and append incidence angle raster
                    inc = rxa.open_rasterio(inc_fp)
                    inc = inc.squeeze('band')
                    inc = inc.coarsen(x = 6, boundary = 'pad').mean().coarsen(y = 6, boundary = 'pad').mean()
                
                polarization = tiff_fp.stem.split('_')[-2][4:]

                if polarization != 'VV':
                    continue

                # open image
                cor = rxa.open_rasterio(tiff_fp)
                
                # remove band as a dimension
                cor = cor.squeeze('band')

                # get metadata frome annotation file or names
                t1 = pd.to_datetime(ann.loc['value', 'start time of acquisition for pass 1']).to_datetime64()
                t2 = pd.to_datetime(ann.loc['value', 'start time of acquisition for pass 2']).to_datetime64()

                rlooks = int(ann.loc['value', 'number of looks in range'])
                alooks = int(ann.loc['value', 'number of looks in azimuth'])

                # add flight 1,2, direction as dimensions
                cor = cor.expand_dims(time = [t1])
                cor = cor.assign_coords(flight2 = ('time', [t2]))

                # coarsen from ~ 5m to ~ 30m
                cor = cor.coarsen(x = 6, boundary = 'pad').mean().coarsen(y = 6, boundary = 'pad').mean()
                rlooks *= 6
                alooks *= 6

                # save appropriate number of looks
                cor.attrs['azimuth_looks'] = alooks
                cor.attrs['range_looks'] = rlooks

                # reproject all to match first image
                if cors:
                    cor = cor.rio.reproject_match(cors[0])

                # append this to our list of coherences
                cors.append(cor)
        
        if len(cors) > 1:
            ds = xr.concat(cors, dim = 'time', combine_attrs = 'identical')
            ds = ds.to_dataset(name = 'vv_coh', promote_attrs = True)
            ds['inc'] = inc.rio.reproject_match(cors[0])

            ds.to_netcdf(out_nc)