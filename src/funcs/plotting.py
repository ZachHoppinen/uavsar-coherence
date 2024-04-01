
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

def map_grid_clean(axes, x_tick_n = 3, y_tick_n = 4, ylabel = 'Latitude [°]', xlabel = 'Longitude [°]', rows_1d = True):
    if type(axes) == mpl.axes._axes.Axes: axes = np.array([axes])
    
    for ax in axes.ravel():
        ax.ticklabel_format(axis = 'both', style = 'plain', useOffset = False)
        ax.xaxis.set_major_locator(plt.MaxNLocator(x_tick_n))
        ax.yaxis.set_major_locator(plt.MaxNLocator(y_tick_n))
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    if len(axes.shape) == 2:
        for ax in axes[:, 1:].ravel(): ax.set_ylabel(''); ax.set_yticks([])
        for ax in axes[:-1, :].ravel(): ax.set_xlabel(''); ax.set_xticks([])
    elif len(axes.shape) == 1 and axes[0].get_gridspec().ncols > 1:
        for ax in axes[1:]: ax.set_ylabel(''); ax.set_yticks([])
    elif len(axes.shape) == 1 and axes[0].get_gridspec().nrows > 1:
        for ax in axes[:-1]: ax.set_xlabel(''); ax.set_xticks([])
