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

import pandas as pd
from pathlib import Path
import glob
import numpy as np
import holoviews as hv
from holoviews import opts
import hvplot.xarray
hv.extension('bokeh')
import xarray as xr

# - [Heatmap](http://holoviews.org/reference/elements/bokeh/HeatMap.html)
# - [Tap](http://holoviews.org/reference/streams/bokeh/Tap.html)

# +
infiles_period = sorted(glob.glob(f'zmnoy_full/*1960-2099*.nc'))
infiles_new = sorted(glob.glob(f'zmnoy_full/*2011-2099*.nc'))
infiles_old = sorted(glob.glob(f'zmnoy_full/*1960-2010*.nc'))

cascade_infiles = [[infiles_period[0:4], infiles_period[4:8],infiles_period[8:12],infiles_period[12:16]], \
[infiles_new[0:4], infiles_new[4:8],infiles_new[8:12],infiles_new[12:16]], \
[infiles_old[0:4], infiles_old[4:8],infiles_old[8:12],infiles_old[12:16]]]

ds = xr.open_mfdataset(cascade_infiles, concat_dim=['per','var','ens'], combine = 'nested')
ds['ens'] = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds['var'] = ['zmnoy','zmo3','zmta','zmua']
ds['per'] = ['1960-2099','2011-2099','1960-2010']

ds_sel=ds.sel(ens='WACCM_r1', per ='1960-2099',var='zmnoy', reg='CO2EQ')
#ds_sel

# +
dataset = hv.Dataset(ds_sel, vdims=('coefs'))

# Declare HeatMap
heatmap = hv.HeatMap(dataset.aggregate(['lat', 'plev'], np.mean),
                     label='select location')
# Declare Tap stream with heatmap as source and initial values
posxy = hv.streams.DoubleTap(source=heatmap, x=0.0, y=1000.0)


# +
# Define function to compute histogram based on tap location
def tap_histogram(x, y):
    return hv.Curve(dataset.select(lat=x, plev=y), kdims='month',
                   label='lat: %s°, plev: %shPa' % (x, y))

tap_dmap = hv.DynamicMap(tap_histogram, streams=[posxy])

(heatmap + tap_dmap).opts(
    opts.Curve(framewise=True, height=500, line_color='black', width=375, yaxis='right'),
     opts.HeatMap(cmap='RdBu_r', fontsize={'xticks': '6pt'}, height=500,
                 tools=['hover'], width=500, xrotation=90,invert_xaxis=True, invert_yaxis=True)
)
# -

hv.help(hv.HeatMap)



