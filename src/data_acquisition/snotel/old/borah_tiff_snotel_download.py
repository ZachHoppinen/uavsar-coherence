from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkb, wkt
from shapely.geometry import box, Polygon

import rioxarray as rxa

import matplotlib.pyplot as plt

from tqdm import tqdm

from datetime import datetime

from metloom.pointdata import SnotelPointData, CDECPointData
from metloom.variables import SnotelVariables, CdecStationVariables

from rasterio import features
def vectorize_valid(fp):
    img = rxa.open_rasterio(fp).squeeze('band')
    img = ~img.isnull()
    img = img.astype('uint8')
    mask = img == 1
    coords = list((features.shapes(img, mask = mask)))[0][0]['coordinates'][0]
    xy_coords = [(img.x[int(x)-1].values.ravel()[0], img.y[int(y)-1].values.ravel()[0]) for x, y in coords]
    return Polygon(xy_coords)

print('Starting...')
home_dir = Path('/Users/rdcrlzh1/Documents/uavsar-coherence/')
fig_dir = home_dir.joinpath('figures', 'snotels')

uavsar_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar')
uavsar_dir = home_dir.joinpath('uavsar')

# get list of uavsars directories
uavsars = list(uavsar_dir.glob('*_full.nc'))
# remove tmp dir
uavsars = [u for u in uavsars if u != 'tmp']
# get location and flight direction for key and first coherence tiff as value of dictionary
uavsars = {u.stem.replace('_full', '').split('_')[0]: list(u.glob('*.cor.grd.tiff'))[0] for u in uavsars if len(list(u.glob('*.cor.grd.tiff'))) > 0}
# convert rasterio image to valid geometry polygon

uavsars = {u: vectorize_valid(v) for u, v in tqdm(uavsars.items())}
# convert to geodataframe
bounds = gpd.GeoDataFrame(uavsars.values(), index = uavsars.keys(), columns = ['geometry'])
bounds = bounds.set_crs('EPSG:4326')

# bounds_fp = Path('/bsuhome/zacharykeskinen/uavsar-coherence/data/uavsar-bounds/snowex-uavsar-bounds-v2.shp')
# bounds = gpd.read_file(bounds_fp)
# _drop_z = lambda geom: wkb.loads(wkb.dumps(geom, output_dimension=2))
# bounds.geometry = bounds.geometry.transform(_drop_z)

# https://www.nrcs.usda.gov/wps/portal/wcc/home/quicklinks/stateSnowPrograms#version=167&elements=W,D&networks=!SCAN,SNTLT,OTHER,SNOW&states=!&counties=!&hucs=&minElevation=&maxElevation=&elementSelectType=all&activeOnly=true&activeForecastPointsOnly=false&hucLabels=false&hucIdLabels=false&hucParameterLabels=true&stationLabels=&overlays=&hucOverlays=2&basinOpacity=75&basinNoDataOpacity=25&basemapOpacity=100&maskOpacity=0&mode=stations&openSections=dataElement,parameter,date,basin,options,elements,location,networks,stationList&controlsOpen=true&popup=&popupMulti=&popupBasin=&base=esriNgwm&displayType=inventory&basinType=6&dataElement=WTEQ&depth=-8&parameter=PCTMED&frequency=DAILY&duration=I&customDuration=&dayPart=E&year=2024&month=1&day=25&monthPart=E&forecastPubMonth=1&forecastPubDay=1&forecastExceedance=50&useMixedPast=true&seqColor=1&divColor=7&scaleType=D&scaleMin=&scaleMax=&referencePeriodType=POR&referenceBegin=1991&referenceEnd=2020&minimumYears=20&hucAssociations=true&lat=40.00&lon=-99.00&zoom=4.0

snotels = pd.read_csv(home_dir.joinpath('data', 'snotel', 'snotel-list.csv'))
snotels = gpd.GeoDataFrame(snotels, geometry=gpd.points_from_xy(snotels.Longitude, snotels.Latitude), crs='epsg:4326')

fig, ax= plt.subplots()
snotels.plot(ax = ax, markersize = 1)
bounds.plot(ax = ax, color = 'red', zorder = 1e3, aspect=1)

intersect = snotels.sjoin(bounds, how = 'inner')
intersect = intersect.set_crs('EPSG:4326')

# cdec = False
# if cdec:
#     vrs = [
#         CdecStationVariables.SWE,
#         CdecStationVariables.SNOWDEPTH,
#         CdecStationVariables.TEMPAVG
#     ]
#     points = CDECPointData.points_from_geometry(bounds, vrs, snow_courses=False)
#     df = points.to_dataframe()
#     df.geometry = df.geometry.transform(_drop_z)
#     df = df.set_crs('EPSG:4326')
#     print(df)

#     intersect = gpd.GeoDataFrame(pd.concat([df, intersect], ignore_index = True))

intersect.plot(ax = ax, color = 'green', zorder = 1e4, markersize = 5, aspect = 1)

ax.set_xlim(-125, -105)
ax.set_ylim(33, 48)
plt.savefig(fig_dir.joinpath('snotel_uavsar.png'))

snotel_data_dir = home_dir.joinpath('data', 'snotel')
intersect.to_file(snotel_data_dir.joinpath('uavsar-snotels.shp'))

state_abbr = {'Colorado':'CO', 'Idaho': 'ID', 'California':'CA', 'New Mexico': 'NM', 'Utah': 'UT', 'Montana': 'MT'}
intersect = gpd.read_file(snotel_data_dir.joinpath('uavsar-snotels.shp'))

vrs = [
        SnotelVariables.SWE,
        SnotelVariables.SNOWDEPTH,
        SnotelVariables.TEMPAVG
    ]

for i, r in tqdm(intersect.iterrows(), total = len(intersect)):
    snotel_id = f"{r['ID'].strip()}:{state_abbr[r['State']]}:SNTL"
    snotel_point = SnotelPointData(snotel_id, f"{r['index_righ']}")
    df = snotel_point.get_daily_data(datetime(2019, 10, 1), datetime(2022, 6, 1), vrs)
    if type(df) == gpd.GeoDataFrame:
        snotel_data_dir.joinpath(r['index_righ']).mkdir(exist_ok = True)
        df.to_csv(snotel_data_dir.joinpath(r['index_righ'], f"{r['ID'].strip()}:{state_abbr[r['State']]}:SNTL.csv"))