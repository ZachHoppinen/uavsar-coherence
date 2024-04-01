from itertools import product
def find_cor_ts(ds, main_pol = 'VV'):
    times = []
    for heading, t1, t2 in product(ds.heading.values, ds.time1.values, ds.time2.values):
        if (~ds['cor'].sel(time1 = t1, time2 = t2, heading = heading, pol = main_pol).isnull()).sum() == 0: continue
        times.append([heading, t1,t2])
    return times