from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkb, wkt

import matplotlib.pyplot as plt

from datetime import datetime

from metloom.pointdata import SnotelPointData
from metloom.variables import SnotelVariables

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures/snotels')

bounds_fp = Path('/bsuhome/zacharykeskinen/uavsar-coherence/data/uavsar-bounds/snowex-uavsar-bounds-v2.shp')
bounds = gpd.read_file(bounds_fp)
_drop_z = lambda geom: wkb.loads(wkb.dumps(geom, output_dimension=2))
bounds.geometry = bounds.geometry.transform(_drop_z)

snotels = pd.read_csv('/bsuhome/zacharykeskinen/uavsar-coherence/data/snotel/snotel-list.csv')
snotels = gpd.GeoDataFrame(snotels, geometry=gpd.points_from_xy(snotels.Longitude, snotels.Latitude), crs='epsg:4326')

fig, ax= plt.subplots()
snotels.plot(ax = ax, markersize = 1)
bounds.plot(ax = ax, color = 'red', zorder = 1e3)

intersect = snotels.sjoin(bounds, how = 'inner')
intersect.plot(ax = ax, color = 'green', zorder = 1e4)
print(intersect)

ax.set_xlim(-125, -105)
ax.set_ylim(33, 48)
plt.savefig(fig_dir.joinpath('snotel_uavsar.png'))