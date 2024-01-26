from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkb, wkt
from shapely.geometry import box, Polygon

import rioxarray as rxa

import matplotlib.pyplot as plt

from datetime import datetime

from metloom.pointdata import SnotelPointData, CDECPointData
from metloom.variables import SnotelVariables, CdecStationVariables

fig_dir = Path('/bsuhome/zacharykeskinen/uavsar-coherence/figures/snotels')

uavsar_dir = Path('/bsuhome/zacharykeskinen/scratch/coherence/uavsar')

uavsars = list(uavsar_dir.glob('*'))
uavsars = [u for u in uavsars if u != 'tmp']
uavsars = {u: list(u.glob('*.cor.grd.tiff'))[0] for u in uavsars if len(list(u.glob('*.cor.grd.tiff'))) > 0}
for u, v in uavsars.items():
    print(rxa.open_rasterio(v))
# uavsars = {'_'.join(fp.stem.split('_')[:2]):rxa.open_rasterio(v) for fp, v in uavsars.items()}
# bounds = gpd.GeoDataFrame(uavsars.values(), index = uavsars.keys(), columns = ['geometry'])
# bounds = bounds.set_crs('EPSG:4326')
# print(bounds)

# bounds_fp = Path('/bsuhome/zacharykeskinen/uavsar-coherence/data/uavsar-bounds/snowex-uavsar-bounds-v2.shp')
# bounds = gpd.read_file(bounds_fp)
# _drop_z = lambda geom: wkb.loads(wkb.dumps(geom, output_dimension=2))
# bounds.geometry = bounds.geometry.transform(_drop_z)

# https://www.nrcs.usda.gov/wps/portal/wcc/home/quicklinks/stateSnowPrograms#version=167&\
# elements=W,D&networks=!SCAN,SNTLT,OTHER,SNOW&states=!&counties=!&hucs=&minElevation=&\
# maxElevation=&elementSelectType=all&activeOnly=true&activeForecastPointsOnly=false&hucLabels=\
# false&hucIdLabels=false&hucParameterLabels=true&stationLabels=&overlays=&hucOverlays=2&basinOpacity=\
# 75&basinNoDataOpacity=25&basemapOpacity=100&maskOpacity=0&mode=stations&openSections=dataElement,\
# parameter,date,basin,options,elements,location,networks,stationList&controlsOpen=true&popup=&popupMulti=&\
# popupBasin=&base=esriNgwm&displayType=inventory&basinType=6&dataElement=WTEQ&depth=-8&parameter=PCTMED&\
# frequency=DAILY&duration=I&customDuration=&dayPart=E&year=2024&month=1&day=25&monthPart=E&forecastPubMonth=1&\
# forecastPubDay=1&forecastExceedance=50&useMixedPast=true&seqColor=1&divColor=7&scaleType=D&scaleMin=&scaleMax=&\
# referencePeriodType=POR&referenceBegin=1991&referenceEnd=2020&minimumYears=20&hucAssociations=true&lat=40.00&lon=-99.00&zoom=4.0
"""
snotels = pd.read_csv('/bsuhome/zacharykeskinen/uavsar-coherence/data/snotel/snotel-list.csv')
snotels = gpd.GeoDataFrame(snotels, geometry=gpd.points_from_xy(snotels.Longitude, snotels.Latitude), crs='epsg:4326')

fig, ax= plt.subplots()
snotels.plot(ax = ax, markersize = 1)
bounds.plot(ax = ax, color = 'red', zorder = 1e3)

intersect = snotels.sjoin(bounds, how = 'inner')
intersect = intersect.set_crs('EPSG:4326')

cdec = False
if cdec:
    vrs = [
        CdecStationVariables.SWE,
        CdecStationVariables.SNOWDEPTH,
        CdecStationVariables.TEMPAVG
    ]
    points = CDECPointData.points_from_geometry(bounds, vrs, snow_courses=False)
    df = points.to_dataframe()
    df.geometry = df.geometry.transform(_drop_z)
    df = df.set_crs('EPSG:4326')
    print(df)

    intersect = gpd.GeoDataFrame(pd.concat([df, intersect], ignore_index = True))

intersect.plot(ax = ax, color = 'green', zorder = 1e4, markersize = 5)

ax.set_xlim(-125, -105)
ax.set_ylim(33, 48)
plt.savefig(fig_dir.joinpath('snotel_uavsar.png'))
"""