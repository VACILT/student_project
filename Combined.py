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

# # Tap-plot
# ## Interactive visualizations of N-dimensional meteorological data
#
# This Notebook let you explore meteorological data in an interactive way. Just run the code and use the dashboard created at the bottom! You may tap on points of interest in the Quadmesh-plot, to show a plot comparing different ensemble members.

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
import param
hv.extension('bokeh')

# ### Data loading
# Loading all files from the /data library. Combine them by adding new dimensions
# - per = Period of Survey
# - var = The considered variable
# - ens = the choosen ensemble members

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

# ## rearange/ rename dataset

ds_sel = ds.rename({'lat': 'x', 'plev': 'y'})
ds_sel['coefs'].attrs['units'] = '%'
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
month_names = ['January', 'February','March','April','May','June','July','August','September','October','November','December']
ds_sel['ens'] = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds_sel['month'] = np.arange(1,13,1)


# ## Define Tap-plot
# We used the holoviews streams Tap-function to track taps on the quadmesh plot. Out of that, we created a curve comparing the different models on one certain location.

def create_taps_graph(x, y):

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


# ## Creating widgets
# Widgets provide us precise control over parameter values. Widgets will render and sync their state in the notebook.
# They can easely be manipulated and the callbacks can be used by using the .value function. 

# +
month_selec =  pn.widgets.IntSlider(name='Month', value=1, start=1, end=12)

ens_selec   =  pn.widgets.RadioBoxGroup(name='Ens', options=['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL'], inline=True)

reg_selec   =  pn.widgets.Select(name='Regressor', options=['CO2EQ', 'EESC', 'ENSO', 'QBO30', 'QBO50', 'eep_for_noy_and_o3',
       'epp_for_t_and_u', 'f107', 'intercept', 'spe_for_noy_and_o3',
       'spe_for_t_and_u'])

per_selec   =  pn.widgets.RadioBoxGroup(name='Period', options=['1960-2099', '2011-2099', '1960-2010'], inline=True)

var_selec   =  pn.widgets.RadioBoxGroup(name='Variable', options=['zmnoy', 'zmo3', 'zmta', 'zmua'], inline=True)
reset_button = pn.widgets.Button(name='Reset on next tap', button_type='success')
# -

# ## Adding p-values
# Overlaying the coefs with associated p-values, shows the area of confidence. This is done by the .contour() function.

# +
hvc_opts = dict(frame_width=400, dynamic=True, \
                                         x = 'x', y = 'y',  colorbar = False, \
                                      logy = True, symmetric=True, cmap = ['black', 'gray'], \
                                                levels=[0.01,0.05],ylim=(1000,0.1), legend=False)

imgs_pv = ds_sel['p_values'].hvplot.contour(**hvc_opts)
# -

# ## Create Quadmesh, Tap-stream
# - Creating a Heatmap-like plot to show a value depending on pressure-level and latitude
#
# - Create a stream to track clicks on the Quadmesh

# +
#creating Quadmesh
graph_opts = dict(cmap = 'RdBu_r', symmetric=True, logy = True, colorbar = False, \
                ylim=(1000,0.1), active_tools=['pan'],title='Tap to compare ens', toolbar="below", frame_width=400)

graph = ds_sel['coefs'].hvplot.quadmesh(x = 'x', y = 'y' ).opts(**graph_opts)

# creating Tap
taps = []
stream = hv.streams.Tap(source=graph, x=np.nan, y=np.nan)
tap_stream = hv.streams.Tap(transient=True)
tap_stream.source = graph
taps_graph = hv.DynamicMap(    
                create_taps_graph,
                streams=[tap_stream])
# -

# ## Combine
#
# The locations() function gives us a combinded, self updating panel. Whenever a parameter changes the function is called.
#
# - a string showing the currently chosen parameters is created
# - the dimensions on the Quadmesh ares set
# - the Widgets are getting combined to a box
# - The Tap-plot is created
# - everything in combined in rows and columns
#

# +
x_list=[]
y_list=[]
curve_list=[]

@pn.depends(stream.param.x, stream.param.y, month_sel=month_selec.param.value,
            reg_sel=reg_selec.param.value, per_sel=per_selec.param.value,
            ens_sel=ens_selec.param.value, var_sel=var_selec.param.value)
def location(x, y, month_sel, reg_sel, per_sel, ens_sel, var_sel):

    first_column = pn.pane.Markdown(f'#### Click at {x:.2f}, {y:.2f}</br> <b>{var_sel}</b> response to <b>{reg_sel}</b> in <b>{month_names[month_sel-1]}</b></br> choosen period: <b>{per_sel}</b></br> choosen model: <b>{ens_sel}</b>', style={'font-family': "calibri",'color':"green"})
    hv_panel[1][0][0].value=per_sel
    hv_panel[1][0][1].value=var_sel
    hv_panel[1][0][2].value=ens_sel
    hv_panel[1][0][3].value=month_sel
    hv_panel[1][0][4].value=reg_sel
    box = pn.WidgetBox(var_selec, per_selec, reg_selec, month_selec, ens_selec,reset_button, width=390)   
        
    if np.nan not in [x,y]:

        temp3=ds_sel.sel(month=month_sel, reg=reg_sel, per=per_sel, var=var_sel)
        temp = temp3.sel(x=x,y=y, method = 'nearest')
        if (temp['coefs']['x'].values) not in x_list:
            x_list.append(float(temp['coefs']['x'].values))
        if (temp['coefs']['y'].values) not in y_list:
            y_list.append(float(temp['coefs']['y'].values))
        
        temp2 = temp['coefs'].where(temp['p_values'] < 0.05) # mark stat. sign. values
        curve_list.append(temp['coefs'].hvplot(width = 400) * temp2.hvplot.scatter(c='k'))
        
        second_column =  hv.Overlay(curve_list).opts(toolbar=None)
    else:
        second_column = pn.Spacer(name='Series Graph',width=400)
    return pn.Column(first_column, second_column, box)


# -

# ## using Panel dependencies
#
# With Panel it is possible calling functions by change of a parameter. This is done by @pn.depends() or defining a watcher.

# +
@pn.depends(stream.param.x, stream.param.y)
def get_tabs_tabel(x, y):
    table = hv.Table({'X':x_list, 'Y':y_list},['X', 'Y']).opts(bgcolor='red')
    return pn.Column(table)

def reset(arg=None):
    curve_list.clear()
    taps.clear()
    x_list.clear()
    y_list.clear()

reset_button.param.watch(reset, 'clicks')
# -

# ## Panel, Gridspec 
# Creating a Panel object to overlay the Quadmesh, the p-values and the map of taps.
#
# "The GridSpec layout allows arranging multiple Panel objects in a grid using a simple API to assign objects to individual grid cells or to a grid span." ([source](https://panel.holoviz.org/reference/layouts/GridSpec.html))

# +
#  adding panel to gain control over widgets
hv_panel = pn.panel(graph*imgs_pv*taps_graph)
#hv_panel.pprint()

gspec = pn.GridSpec(width=800, height=600, margin=5)
gspec[0:10, 0] = hv_panel[0]
gspec[0:13, 1] = location
gspec[11, 0] = get_tabs_tabel

gspec
# -

