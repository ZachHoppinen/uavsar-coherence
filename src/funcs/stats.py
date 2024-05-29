import numpy as np
import pandas as pd
import xarray as xr

def clean_xs_ys(xs, ys):
    if type(xs) == list: xs = np.array(xs)
    if type(ys) == list: ys = np.array(ys)

    if type(xs) == xr.DataArray: xs = xs.values.ravel()
    if type(ys) == xr.DataArray: ys = ys.values.ravel()
    idx = (~np.isnan(xs)) & (~np.isnan(ys))
    xs, ys = xs[idx], ys[idx]

    return xs, ys


def get_stats(xs, ys, clean = True, bias = False):
    """
    returns rmse, r, len(x)
    """

    if clean:
        xs, ys = clean_xs_ys(xs, ys)

    from sklearn.metrics import mean_squared_error
    rmse = mean_squared_error(xs, ys, squared=False)

    from scipy.stats import pearsonr
    r, p = pearsonr(xs, ys)

    if bias:
        MBE = np.mean(ys - xs)
        return rmse, r, len(xs), MBE

    return rmse, r, len(xs)

from sklearn.linear_model import LinearRegression

def fit_lm(xs, ys):
    if isinstance(xs, pd.Series): xs = xs.values
    if xs.ndim == 1: xs = xs.reshape(-1, 1)
    model = LinearRegression().fit(xs, ys)
    r_sq, intercept, coefficient = model.score(xs, ys), model.intercept_, model.coef_
    if len(coefficient) == 1: coefficient = coefficient[0]

    return r_sq, intercept, coefficient