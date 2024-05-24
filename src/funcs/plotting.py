
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
    # colors = {'Water/Wetlands': 'Blues', 'Developed': 'Reds', 'Barren': 'Paired', 'Forests': 'Greens', 'Shrubs/Grass': 'Set3', 'Cultivated': 'spring', 'Perennial Snow': 'Pastel1'}
    colors = {'Water/Wetlands': 'Blues', 'Developed': 'Reds', 'Barren': 'Paired', 'Forests': 'Greens', 'Shrubs/Grass': 'Set3', 'Perennial Snow': 'Pastel1'}

    # lc = ds['land_cover']
    # https://www.mrlc.gov/data/legends/national-land-cover-database-class-legend-and-description
    # 11 = open water, and 90+ is wetlands
    lc.where((lc == 11) | (lc >= 90)).plot(ax = ax, add_colorbar=False, vmin = 0, vmax = 1, cmap = 'Blues')
    if lc.where((lc == 11) | (lc >= 90)).count() == 0: del colors['Water/Wetlands']
    # developed land
    lc.where((lc >= 21 ) & (lc <= 24)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'Reds')
    if lc.where((lc >= 21 ) & (lc <= 24)).count() == 0: del colors['Developed']
    # barren
    lc.where(lc == 31).plot(ax = ax, add_colorbar=False, vmin = 0, vmax = 1, cmap = 'Paired')
    if lc.where(lc == 31).count() == 0: del colors['Barren']
    # forests
    lc.where((lc >= 41 ) & (lc <= 43)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'Greens')
    if lc.where((lc >= 41 ) & (lc <= 43)).count() == 0: del colors['Forests']
    # shrubs/grassland
    lc.where((lc == 52 ) | (lc == 71)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'Set3')
    if lc.where((lc == 52 ) | (lc == 71)).count() == 0: del colors['Shrubs/Grass']
    # Cultivated
    lc.where((lc == 81 ) | (lc == 82)).plot(ax = ax, add_colorbar = False, vmin = 0, vmax = 1, cmap = 'spring')
    if lc.where((lc == 81 ) | (lc == 82)).count() == 0: del colors['Cultivated']
    # perrenial snow/ice
    lc.where(lc == 12).plot(ax = ax, add_colorbar=False, vmin = 0, vmax = 1, cmap = 'Pastel1')
    if lc.where(lc == 12).count() == 0: del colors['Perennial Snow']


    cms = plt.colormaps
    patches = []
    # for color, label in zip([cms['Blues'], cms['Reds'], cms['Paired'], cms['Greens'], cms['Set3'], cms['spring'], cms['Pastel1']],\
        # ['Water/Wetlands', 'Developed', 'Barren', 'Forests', 'Shrubs/Grass', 'Cultivated', 'Perennial Snow']):
    for label, color in colors.items():
        color = cms[color]
        patches.append(mpatches.Patch(color=color(1000), label=label))
    ax.legend(handles=patches)

def add_text(s, ax, loc):
    """
    s: string
    ax: matplotlib axis
    loc: string of 'upper right', 'upper left', 'lower right', 'lower left'
    """
    locs = {'upper right': {'xy': (0.99, 0.99), 'va': 'top', 'ha': 'right'}, 'upper left': {'xy': (0.01, 0.99), 'va': 'top', 'ha': 'left'}, 'lower left': {'xy': (0.01, 0.01), 'va': 'bottom', 'ha': 'left'}, 'lower right': {'xy': (0.99, 0.01), 'va': 'bottom', 'ha': 'right'}}
    assert loc in locs.keys(), f'loc must be in set of : {locs.keys()}'
    fontdic = locs[loc]
    ax.text(*fontdic['xy'], s, va = fontdic['va'], ha = fontdic['ha'], transform= ax.transAxes)

def add_interval(ax, xdata, ydata, caps="  ", color = 'grey'):
    """
    https://stackoverflow.com/questions/52743119/line-end-styles-in-matplotlib
    """
    line = ax.add_line(mpl.lines.Line2D(xdata, ydata, color = color))
    anno_args = {
        'ha': 'center',
        'va': 'center',
        'size': 14,
        'color': line.get_color()
    }
    a0 = ax.annotate(caps[0], xy=(xdata[0], ydata[0]), **anno_args)
    a1 = ax.annotate(caps[1], xy=(xdata[1], ydata[1]), **anno_args)
    return (line,(a0,a1))