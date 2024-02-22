import numpy as np
import pandas as pd
import xarray as xr
import rioxarray as rio

# from uavsar_pytools.convert.tiff_conversion import read_annotation 

import matplotlib.pyplot as plt

from pathlib import Path

from tqdm import tqdm

out_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar/')
sites = list(out_dir.glob('*.nc'))

for site in sites:
    print(site)

da = xr.open_dataarray('/Users/rdcrlzh1/Desktop/dem/Oliktok.tif')
geom = da.rio.reproject('EPSG:4326').rio.bounds()
dem = py3dep.get_dem(geom, 30)