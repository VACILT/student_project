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

import numpy as np
import holoviews as hv
from holoviews import opts
from holoviews import streams
import xarray as xr
import hvplot.xarray
import glob
from pathlib import Path
from scipy.stats import combine_pvalues
import panel as pn
from itertools import cycle
hv.extension('bokeh')

# ### Data loading
# Loading all files from the /data library. Combine them by adding new dimensions
# - per = Period of Survey
# - var = The considered variable
# - ens = the choosen model

# +
infiles_period = sorted(glob.glob(f'data/*1960-2099*.nc'))
infiles_new = sorted(glob.glob(f'data/*2011-2099*.nc'))
infiles_old = sorted(glob.glob(f'data/*1960-2010*.nc'))

cascade_infiles = [[infiles_period[0:4], infiles_period[4:8],infiles_period[8:12],infiles_period[12:16]], \
[infiles_new[0:4], infiles_new[4:8],infiles_new[8:12],infiles_new[12:16]], \
[infiles_old[0:4], infiles_old[4:8],infiles_old[8:12],infiles_old[12:16]]]

ds = xr.open_mfdataset(cascade_infiles, concat_dim=['per','var','ens'], combine = 'nested')
ds['ens'] = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds['var'] = ['zmnoy','zmo3','zmta','zmua']
ds['per'] = ['1960-2099','2011-2099','1960-2010']
# -

# ## select data here ...

sel_reg = 'f107'     #'CO2EQ', 'EESC', 'ENSO', 'QBO30', 'QBO50', 'eep_for_noy_and_o3',
                     #'epp_for_t_and_u', 'f107', 'intercept', 'spe_for_noy_and_o3',
                     #'spe_for_t_and_u'
sel_month = 1 
sel_per ='1960-2099' #'1960-2099','2011-2099','1960-2010'
sel_var = 'zmnoy'    #'zmnoy','zmo3','zmta','zmua'
plot_var = '1'       # 0 for Tapplot, 1 for Roi-drawer

# ## ... or use input-fuction to request certain plot

sel_reg = input('Choose your regressor: ')
sel_per = input('Choose your period: ')
sel_var = input('Choose your variable: ')
plot_var = input('Type "0" for Tap-plot or "1" for ROI-drawer: ')

# ## rearange/ rename dataset

sel_dict = dict(reg = sel_reg, month = sel_month, per=sel_per, var=sel_var)
ds_sel = ds.sel(**sel_dict).rename({'lat': 'x', 'plev': 'y'})
ds_sel['coefs'].attrs['units'] = '%'
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
month_names = ['January', 'February','March','April','May','June','July','Sep','Oct','Nov','Dec']
ds_sel['ens'] = range(4)
#ds_sel

# ## define Tap-plot
# We used the holoviews streams.Tap-function to track taps on the quadmesh plot. Out of that, we created a curve comparing the different models on one certain location.

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
graph = ds_sel['coefs'].hvplot.quadmesh(x = 'x', y = 'y').opts(**graph_opts)

hv_div = hv.Div(f"""<h1>{sel_var} response to {sel_reg} for {month_names[sel_month-1]}</h1>""")
taps = []
stream = hv.streams.Tap(source=graph, x=np.nan, y=np.nan)

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
        temp = ds_sel.sel(x=x,y=y, method = 'nearest')
        temp2 = temp['coefs'].where(temp['p_values'] < 0.05) # mark stat. sign. values
        second_column = temp['coefs'].hvplot(width = 300) * temp2.hvplot.scatter(c='k')
    else:
        second_column = pn.Spacer(name='Series Graph')
    return pn.Column(first_column, second_column)
    
pn.Column(pn.Row(graph*taps_graph,hv_div), location)
# -

# ## Define Roi-Drawer
# add a function to define a box edition tool

# +
polys = hv.Polygons([])
box_stream = streams.BoxEdit(source=polys)

def roi_curves(data):
    if not data or not any(len(d) for d in data.values()):
        return hv.NdOverlay({0: hv.Curve([], 'ens', 'coefs')})
    
    curves = {}
    data = zip(data['x0'], data['x1'], data['y0'], data['y1'])
    for i, (x0, x1, y0, y1) in enumerate(data):
        selection = dataset.select(x=(x0, x1), y=(y1, y0)) # swap y0 and y1 when inverted y-axis
        curves[i] = hv.Spread(selection.aggregate('ens', np.mean, np.std))
    return hv.NdOverlay(curves)

hlines = hv.HoloMap({i: hv.VLine(i, label = ens_name ) for i, ens_name in enumerate(ens_ls)}, 'ens')
dmap = hv.DynamicMap(roi_curves, streams=[box_stream]).redim.range(ens=(0,3.5))


# -

# add a function to calculate combined p-values

def combine_pvalues_ufunc(arr):
    _, pv = combine_pvalues(arr, method = 'stouffer')
    return pv


# Due to the overlapping of coefs and pvalues map, the significance of the values is proofen. 

# +
### define datasets
dataset = hv.Dataset(ds_sel[['coefs']], kdims = ['ens', 'x', 'y'])
temp = xr.apply_ufunc(combine_pvalues_ufunc, ds_sel['p_values'], input_core_dims=[['ens']], \
               output_core_dims = [[]], vectorize = True, dask = 'allowed')

vmax = 40
vmin = -vmax
f_width = 300

### options dictionary
hvc_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = f_width)

p_opts = dict(width=300, dynamic=True, \
                                         x = 'x', y = 'y',  colorbar = False, \
                                      logy = True, cmap = ['black', 'gray'], levels=[0.01,0.05])

### Coefs as Quadmesh
im = dataset.to(hv.QuadMesh, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)
im2 = dataset.aggregate(['x','y'], np.mean).to(hv.QuadMesh, ['x', 'y'], dynamic=True)
im2 = im2.redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)

### p-values as contours

imgs_pv = ds_sel['p_values'].hvplot.contour(**p_opts)
imgs_pv2 = temp.hvplot.contour(**p_opts)

### ROI-Drawer
hl = hv.HLine(0).opts(color = 'gray', line_dash = 'dotted')
dmap = dmap.opts(xticks=[(i, ens_name) for i,ens_name in enumerate(ens_ls)])

### Layout
first_panel = im* imgs_pv * polys
second_panel = (dmap * hl * hlines).relabel('ROI drawer')
second_row = ((im2*imgs_pv2).relabel('Model average (p-values combined using Z-score)')+hv_div)
layout = ((first_panel + second_panel).opts(
    opts.Curve(width=400, framewise=True), 
    opts.Polygons(fill_alpha=0.2, line_color='green', fill_color ='green'), 
    opts.VLine(color='black'))+second_row).cols(2)
layout
