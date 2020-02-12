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

# # Table of contents
# - [import Modules](###import-modules)
# - [functions](###functions)
# - [combine files](###combine-files)
# - [select data](###select-data)
# - [plot data](###plot-data)

# ### import Modules

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
import scipy.stats as st
import panel as pn


# ### functions

# +
def combine_pvalues_ufunc(arr):
    _, pv = combine_pvalues(arr, method = 'stouffer')
    return pv
def get_standardized_values(arr):
    v=arr/np.nanmax(arr, axis=None)
    return v

x=np.arange(1.0,11.0,1)
x[1]=None
y=get_standardized_values(x)
z=max(y)
z
# -

# ### combine files
# - [creating-a-dataset](http://xarray.pydata.org/en/stable/data-structures.html#creating-a-dataset)
# - [transforming-a-dataset](http://xarray.pydata.org/en/stable/data-structures.html#transforming-datasets)

invar = 'zmnoy'
infiles = sorted(glob.glob(f'zmnoy_files/{invar}*.nc'))
ds_xa = xr.open_mfdataset(infiles, concat_dim='ens', combine = 'nested')# Open multiple files as a single dataset
#ds_xa

# ### select data

# +
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
month_names = ['January', 'February','March','April','May','June','July','Aug','Sep','Oct','Nov','Dec']
ds_sel = ds_xa.sel().rename({'lat': 'x', 'plev': 'y'}) #rename lat to x and pressure level to y
ds_sel['coefs'].attrs['units'] = '%' #ds_sel['coefs'] only takes the coefs of the dataset
ds_sel['ens'] = ens_ls

ds_sel['month']=np.arange(1,13,1) #ds_sel
ds_mean=ds_sel.mean('ens')#reduce one dimension by average "ens"

temp = xr.apply_ufunc(combine_pvalues_ufunc, ds_sel['p_values'], input_core_dims=[['ens']], \
               output_core_dims = [[]], vectorize = True, dask = 'allowed')
ds_sel['coefs']=xr.apply_ufunc(get_standardized_values,ds_sel['coefs'],input_core_dims=[['x', 'y']],output_core_dims=[['x', 'y']],vectorize = True, dask = 'allowed')
ds_mean['coefs']=xr.apply_ufunc(get_standardized_values,ds_sel['coefs'],input_core_dims=[['x', 'y']],output_core_dims=[['x', 'y']],vectorize = True, dask = 'allowed')

# -

# ### plot data
# [QuadMesh](http://holoviews.org/reference/elements/bokeh/QuadMesh.html)
#
# [Contours](http://holoviews.org/reference/elements/bokeh/Contours.html)
#
# [multi-dimensional dictionary of HoloViews objects](http://holoviews.org/reference/containers/bokeh/HoloMap.html)
#
# [Widget](https://hvplot.holoviz.org/user_guide/Widgets.html)

# +
pv_opts = dict(width=300, colorbar = False, logy = True, cmap = ['black', 'gray'], levels=[0.01,0.05])
co_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, tools = ['hover'], frame_width = f_width)

coefs_mean = ds_mean['coefs'].hvplot.quadmesh('x','y',**co_opts).redim.range(coefs=(-1.0,1.0)).opts(opts.QuadMesh(title='Average', invert_yaxis=True))
coefs = ds_sel['coefs'].hvplot.quadmesh('x','y',**co_opts).redim.range(coefs=(-1.0,1.0)).opts(opts.QuadMesh(title='Model', invert_yaxis=True))

pv_mean = temp.hvplot.contour('x','y',**pv_opts)
pv = ds_sel['p_values'].hvplot.contour('x','y',**pv_opts)

layout=hv.Layout(coefs*pv+coefs_mean*pv_mean).cols(1)
layout
# -

#hv.help(hv.Contours)

