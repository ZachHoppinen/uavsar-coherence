import numpy as np
import pandas as pd
idx = pd.IndexSlice
import xarray as xr

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from itertools import product

from tqdm import tqdm

def clean_snotel(df):
    # convert inches to meters
    df['swe'] = df['SWE'] * 0.0254
    df['sd'] = df['SNOWDEPTH'] * 0.0254
    # convert F to C
    df['temp'] = (df['AVG AIR TEMP'] - 32) * 5/9
    df = df.drop(['SWE', 'SWE_units', 'SNOWDEPTH', 'SNOWDEPTH_units', 'AVG AIR TEMP', 'AVG AIR TEMP_units'], axis = 1)
    return df

def MetersToDecimalDegrees(meters, latitude):
    # https://stackoverflow.com/questions/25237356/convert-meters-to-decimal-degrees
    return meters / (111.32 * 1000 * np.cos(latitude * (np.pi / 180)))

dss= {fp.stem.replace('_v2', ''): xr.open_dataset(fp) for fp in sorted(list(Path('/Users/rdcrlzh1/Documents/uavsar-coherence/uavsar').glob('*_v2.nc')))}


snotels = {fp.stem: {cf.stem:pd.read_csv(cf, comment='#', index_col=0, parse_dates=True) for cf in fp.glob('*.csv')} for fp in Path('/Users/rdcrlzh1/Documents/uavsar-coherence/data/snotel/').rglob('*') if fp.stem in dss.keys()}
snotels = {k: {k_s: clean_snotel(v_s) for k_s, v_s in v.items()} for k, v in snotels.items()}
state_abbr = {'Colorado':'CO', 'Idaho': 'ID', 'California':'CA', 'New Mexico': 'NM', 'Utah': 'UT', 'Montana': 'MT'}
state_abbr = {v: k for k, v in state_abbr.items()}
snotel_list = pd.read_csv('/Users/rdcrlzh1/Documents/uavsar-coherence/data/snotel/snotel-list.csv', index_col=['State', 'ID'])
snotel_list.index = snotel_list.index.set_levels(snotel_list.index.levels[1].str.replace('\t', ''), level=1)

outfp = Path('/Users/rdcrlzh1/Documents/uavsar-coherence/data/snotel').joinpath('snotel_uavsar_diffs_v2.csv')
diffs = pd.DataFrame(index = pd.MultiIndex(levels=[[],[],[],[],[], []], codes=[[],[],[],[],[],[]], names = ['site', 't1', 't2', 'snotel', 'pol', 'heading']), columns = ['cor', 'days', 'temp_diff', 'swe_diff', 'sd_diff', 'swe_t1', 'swe_t2', 'sd_t1', 'sd_t2', 'temp_t1','temp_t2'])
for stem, ds in dss.items():
    if stem not in snotels.keys(): continue
    print(stem)
    loc_snotels = snotels[stem]
    for t1, t2, pol, heading in tqdm(product(ds.time1.values, ds.time2.values, ds.pol.values, ds.heading.values)):
        if (~ds['cor'].sel(time1 = t1, time2 = t2, pol = pol, heading = heading).isnull()).sum() == 0: continue
        img = ds.sel(time1 = t1, time2 = t2, pol = pol, heading = heading)
        cor = img['cor']
        for snotel_id, snotel_data in loc_snotels.items():
            sid, state, network = snotel_id.split(':')
            snotel_meta = snotel_list.loc[(state_abbr[state], sid)]
            lat, long = snotel_meta['Latitude'], snotel_meta['Longitude']
            # calculate decimal degrees for 50 meters to buffer 100 m box at this latitude
            tol_50m = MetersToDecimalDegrees(50, lat)
            t2, t1 = [pd.to_datetime(d, utc = True) for d in [t2, t1]]
            # coherence for 100 meter box centered on snotel
            diffs.loc[(stem, t1, t2, snotel_id, pol, heading), 'cor'] = cor.sel(x = slice(long - tol_50m, long + tol_50m), y = slice(lat + tol_50m, lat - tol_50m)).values.mean()
            # incidence angle for same area
            diffs.loc[(stem, t1, t2, snotel_id, pol, heading), 'inc'] = img['inc'].sel(x = slice(long - tol_50m, long + tol_50m), y = slice(lat + tol_50m, lat - tol_50m)).values.mean()
            diffs.loc[(stem, t1, t2, snotel_id, pol, heading), 'tree_perc'] = img['tree_perc'].sel(x = slice(long - tol_50m, long + tol_50m), y = slice(lat + tol_50m, lat - tol_50m)).values.mean()
            diffs.loc[(stem, t1, t2, snotel_id, pol, heading), 'land_cover'] = img['land_cover'].sel(x = long, y = lat, method = 'nearest').values
            diffs.loc[(stem, t1, t2, snotel_id, pol, heading), 'n'] = int(cor.sel(x = slice(long - tol_50m, long + tol_50m), y = slice(lat + tol_50m, lat - tol_50m)).count().values)
          

            diffs.loc[(stem, t1, t2, snotel_id, pol, heading), 'days'] = (t2 - t1).days
            rows = snotel_data.iloc[snotel_data.index.get_indexer([t1, t2], method='nearest')]
            for col in ['swe', 'sd', 'temp']:
                diffs.loc[(stem, t1, t2, snotel_id, pol, heading), f'{col}_diff'] = np.round(rows.iloc[1][col] - rows.iloc[0][col], 4)
                diffs.loc[(stem, t1, t2, snotel_id, pol, heading), f'{col}_t1'] = np.round(rows.iloc[0][col], 4)
                diffs.loc[(stem, t1, t2, snotel_id, pol, heading), f'{col}_t2'] = np.round(rows.iloc[1][col], 4)

diffs.to_csv(outfp)