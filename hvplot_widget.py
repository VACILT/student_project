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
import panel as pn


# ### functions

def combine_pvalues_ufunc(arr):
    _, pv = combine_pvalues(arr, method = 'stouffer')
    return pv


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
sel_dict = dict()          #set two dims to a fixed value
ds_sel = ds_xa.sel().rename({'lat': 'x', 'plev': 'y'}) #rename lat to x and pressure level to y
ds_sel['coefs'].attrs['units'] = '%' #ds_sel['coefs'] only takes the coefs of the dataset
ds_sel['ens'] = ens_ls

ds_sel['month']=month_names #ds_sel
ds_mean=ds_sel.mean('ens')#reduce one dimension by average "ens"
ds_sel['coefs']
# -

# ### plot data
# [QuadMesh](http://holoviews.org/reference/elements/bokeh/QuadMesh.html)
#
# [multi-dimensional dictionary of HoloViews objects](http://holoviews.org/reference/containers/bokeh/HoloMap.html)

# +

vmax = 40
vmin = -vmax
f_width = 300
hvc_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = f_width, widgets={'month': pn.widgets.DiscreteSlider})#initialize options data for axis
# -
from bokeh.sampledata.iris import flowers
import hvplot.pandas
ds_sel.hvplot.bivariate(x='x', y='y', width=600, 
                         groupby='species', widgets={'species': pn.widgets.DiscreteSlider})

i=ds_sel['coefs']
ids=hv.Dataset(i)
im3=ids.to(hv.QuadMesh, ['x', 'y'], dynamic=True,).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)
im3

