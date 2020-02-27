# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] toc=true
# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Data-loading" data-toc-modified-id="Data-loading-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Data loading</a></span></li></ul></div>
# -

import numpy as np
import holoviews as hv
from holoviews import opts
from holoviews import streams
import xarray as xr
import hvplot.xarray
import glob
from scipy.stats import combine_pvalues
import pandas as pd
import panel as pn
from itertools import cycle
hv.extension('bokeh')

# # Data loading

invar = 'zmnoy'
infiles =  sorted(glob.glob(f'zmnoy_files/{invar}*.nc'))
ds_xa = xr.open_mfdataset(infiles, concat_dim='ens', combine = 'nested')# Open multiple files as a single dataset
#ds_xa

sel_reg = 'f107'
sel_month = 1
month_names = ['January', 'February','March','April','May','June','July','Sep','Oct','Nov','Dec']
sel_dict = dict(reg = sel_reg, month = sel_month)
ds_sel = ds_xa.sel(**sel_dict).rename({'lat': 'x', 'plev': 'y'})
ds_sel['coefs'].attrs['units'] = '%'
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds_sel['ens'] = ens_ls#range(4)
#ds_sel

# +
def create_taps_graph(x, y):
    """
    from: https://github.com/intake/xrviz/blob/master/xrviz/dashboard.py#L369
    """
    colors = ['#60fffc', '#6da252', '#ff60d4', '#ff9400', '#f4e322',
                  '#229cf4', '#af9862', '#629baf', '#7eed5a', '#e29ec8',
                  '#ff4300']
    color_pool = cycle(colors)
    color = next(iter(color_pool))
    print(color)
    if None not in [x, y]:
        taps.append((x, y, color))

    tapped_map = hv.Points(taps, vdims=['z'])
    tapped_map.opts(color='z', marker='triangle', line_color='black',
                    size=8)
    
    return tapped_map
    
    

# +
graph_opts = dict(cmap = 'RdBu_r', symmetric=True, logy = True, colorbar = True, \
                width = 400, ylim=(1000,0.1), active_tools=['wheel_zoom', 'pan'])
sel_data = ds_sel
graph = sel_data['coefs'].hvplot.quadmesh(x = 'x', y = 'y').opts(**graph_opts)


points = graph#hv.Points([])
taps = []
stream = hv.streams.Tap(source=points, x=np.nan, y=np.nan)

tap_stream = hv.streams.Tap(transient=True)
tap_stream.source = graph
taps_graph = hv.DynamicMap(
                create_taps_graph,
                streams=[tap_stream])




@pn.depends(stream.param.x, stream.param.y)
def location(x, y):
    """
    from: https://discourse.holoviz.org/t/example-of-using-holoviews-tapstream-with-panel/166/3
    """
    first_column = pn.pane.Str(f'Click at {x:.2f}, {y:.2f}')
    if np.nan not in [x,y]:
        temp = sel_data.sel(x=x,y=y, method = 'nearest')
        temp2 = temp['coefs'].where(temp['p_values'] < 0.05) # mark stat. sign. values
        second_column = temp['coefs'].hvplot(width = 300) * temp2.hvplot.scatter(c='k')
    else:
        second_column = pn.Spacer(name='Series Graph')
    return pn.Column(first_column, second_column)
    
pn.Row(graph*taps_graph, location) # 
