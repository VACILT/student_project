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
hv.extension('bokeh')

from ipywebrtc.webrtc import VideoRecorder, WidgetStream

# # Data loading

invar = 'zmnoy'
infiles = sorted(glob.glob(f'zmnoy_files/{invar}*.nc'))
ds_xa = xr.open_mfdataset(infiles, concat_dim='ens', combine = 'nested')# Open multiple files as a single dataset
ds_xa

sel_reg = 'f107'
sel_month = 1
month_names = ['January', 'February','March','April','May','June','July','Sep','Oct','Nov','Dec']
sel_dict = dict(reg = sel_reg, month = sel_month)
ds_sel = ds_xa.sel(**sel_dict).rename({'lat': 'x', 'plev': 'y'})
ds_sel['coefs'].attrs['units'] = '%'
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds_sel['ens'] = range(4)
#ds_sel

# +
ds = hv.Dataset(ds_sel[['coefs']], kdims = ['ens', 'x', 'y'])
vmax = 40
vmin = -vmax
f_width = 300
im_opts = dict(cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = f_width)

im = ds.to(hv.HeatMap, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**im_opts)
im2 = ds.aggregate(['x','y'], np.mean).to(hv.HeatMap, ['x', 'y'])
im2 = im2.redim.range(coefs=(vmin,vmax)).opts(**im_opts)

# +
# Declare Tap stream with quadmesh as source and initial values
posxy = hv.streams.DoubleTap(source=im, x=0.0, y=1000.0)
def tap_histogram(x, y):
    return hv.Curve(ds.select(x=x, y=y), kdims='ens',
                   label='lat: %s°, plev: %shPa' % (x, y))

tap_dmap = hv.DynamicMap(tap_histogram, streams=[posxy])


# -

def combine_pvalues_ufunc(arr):
    _, pv = combine_pvalues(arr, method = 'stouffer')
    return pv


# +
hvc_opts = dict(width=300,  colorbar = False, \
                                     logy = True, cmap = ['black'], \
                                               levels=[0.01,0.05])


temp = xr.apply_ufunc(combine_pvalues_ufunc, ds_sel['p_values'], input_core_dims=[['ens']], \
               output_core_dims = [[]], vectorize = True, dask = 'allowed')

imgs_pv=ds_sel['p_values'].hvplot.contour(**hvc_opts)
imgs_pv2 = temp.hvplot.contour(**hvc_opts)
# -

first_panel = im
second_panel = (tap_dmap).relabel('Tap')
second_row = ((im2).relabel('Model average (p-values combined using Z-score)'))
(((first_panel + second_panel).opts(
    opts.Curve(width=400, framewise=True), 
    )+second_row).cols(2)
)


