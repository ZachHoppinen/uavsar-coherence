
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

import matplotlib.patches as mpatches

def plt_lc(lc, ax):
    # lc = ds['land_cover']
    # https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description
    # 11 = open water, and 90+ is wetlands
    lc.where((lc == 11) | (lc >= 90)).plot(ax = ax, add_colorbar=False, vmin = 0, vmax = 1, cmap = 'Blues')
    # developed land
    lc.where((lc >= 21 ) & (lc <= 24)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'Reds')
    # barren
    lc.where(lc == 31).plot(ax = ax, add_colorbar=False, vmin = 0, vmax = 1, cmap = 'Paired')
    # forests
    lc.where((lc >= 41 ) & (lc <= 43)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'Greens')
    # shrubs/grassland
    lc.where((lc == 52 ) | (lc == 71)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'Set3')
    # Cultivated
    lc.where((lc == 81 ) | (lc == 82)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'spring')
    # perrenial snow/ice
    lc.where(lc == 12).plot(ax = ax, add_colorbar=False, vmin = 0, vmax = 1, cmap = 'Pastel1')

    cms = plt.colormaps
    patches = []
    for color, label in zip([cms['Blues'], cms['Reds'], cms['Paired'], cms['Greens'], cms['Set3'], cms['spring'], cms['Pastel1']],\
        ['Water/Wetlands', 'Developed', 'Barren', 'Forests', 'Shrubs/Grass', 'Cultivated', 'Perennial Snow']):
        patches.append(mpatches.Patch(color=color(1000), label=label))
    ax.legend(handles=patches)

def add_text(s, ax, loc):
    locs = {'upper right': {'xy': (0.99, 0.99), 'va': 'top', 'ha': 'right'}, 'upper left': {'xy': (0.01, 0.99), 'va': 'top', 'ha': 'left'}, 'lower left': {'xy': (0.01, 0.01), 'va': 'bottom', 'ha': 'left'}, 'lower right': {'xy': (0.99, 0.01), 'va': 'bottom', 'ha': 'right'}}
    assert loc in locs.keys(), f'loc must be in set of : {locs.keys()}'
    fontdic = locs[loc]
    ax.text(*fontdic['xy'], s, va = fontdic['va'], ha = fontdic['ha'], transform= ax.transAxes)