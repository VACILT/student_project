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
import panel as pn

# - [Heatmap](http://holoviews.org/reference/elements/bokeh/HeatMap.html)
# - [Tap](http://holoviews.org/reference/streams/bokeh/Tap.html)

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

ds_sel=ds.sel(ens='WACCM_r1', per ='1960-2099',var='zmnoy', reg='CO2EQ')
#ds_sel
# -

dataset = hv.Dataset(ds_sel, vdims=('coefs'))

# with @pn.depends() the function is called whenever a value is changing. x and y are the coordinates of the click

# +
hvc_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = 300)
im = dataset.to(hv.QuadMesh, ['lat', 'plev'], dynamic=True).redim.range(coefs=(-40,40)).opts(**hvc_opts)

stream = hv.streams.Tap(source=im, x=0, y=850)

@pn.depends(stream.param.x, stream.param.y)
def plot(x, y):
    return hv.Curve([(i, x/y*i) for i in range(100)])
pn.Row(im, plot)
