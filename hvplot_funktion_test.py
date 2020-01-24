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
#from scipy.stats import combine_pvalues
#hv.extension('bokeh')
#from ipywebrtc.webrtc import VideoRecorder, WidgetStream

# ### combine files
# - [creating-a-dataset](http://xarray.pydata.org/en/stable/data-structures.html#creating-a-dataset)
# - [transforming-a-dataset](http://xarray.pydata.org/en/stable/data-structures.html#transforming-datasets)

invar = 'zmnoy'
infiles = sorted(glob.glob(f'zmnoy_files/{invar}*.nc'))
ds_xa = xr.open_mfdataset(infiles, concat_dim='ens', combine = 'nested')# Open multiple files as a single dataset
#ds_xa

# ### select data

sel_reg = 'f107'
sel_month = 1
month_names = ['January', 'February','March','April','May','June','July','Sep','Oct','Nov','Dec']
sel_dict = dict(reg = sel_reg, month = sel_month)          #set two dims to a fixed value
ds_sel = ds_xa.sel(**sel_dict).rename({'lat': 'x', 'plev': 'y'}) #rename lat to x and pressure level to y
ds_sel['coefs'].attrs['units'] = '%' #ds_sel['coefs'] only takes the coefs of the dataset
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds_sel['ens'] = range(4)
#ds_sel

# ### plot data
# [QuadMesh](http://holoviews.org/reference/elements/bokeh/QuadMesh.html)

# +
ds = hv.Dataset(ds_sel[['coefs']], kdims = ['ens', 'x', 'y'])#
print(ds_sel[['coefs']])

vmax = 40
vmin = -vmax
f_width = 300
hvc_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = f_width)#initialize options data for axis
im = ds.to(hv.QuadMesh, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)
im2 = ds.aggregate(['x','y'], np.mean).to(hv.QuadMesh, ['x', 'y'], dynamic=True)
print(coefs)
#im2 = im2.redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)

#im2
# -


