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


# ### functions

def combine_pvalues_ufunc(arr, axis):
    _, pc = combine_pvalues(arr, method = 'stouffer')
    return pc


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

ds_sel['month']=np.arange(1,13,1) #ds_sel
ds_mean=ds_sel.mean('ens')#reduce one dimension by average "ens"

ds_mean_ps=ds_sel.assign(log_p=-2*np.log((ds_sel.p_values))) #using the fisher's method to combine p values
ds_mean_ps=ds_mean_ps.sum('ens')
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
vmax = 40
vmin = -vmax
f_width = 300

hvc_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = f_width)

hvc_opts_pv = dict(logy = True, symmetric=True, colorbar = True, invert_yaxis=True, frame_width = f_width) #initialize options data for axis




ds = hv.Dataset(ds_sel[['coefs']], kdims = ['month','reg','ens', 'x', 'y'])
ds_2 = hv.Dataset(ds_mean[['coefs']], kdims = ['month','reg' ,'x', 'y'])
ps = hv.Dataset(ds_sel[['p_values']], kdims = ['month','reg','ens', 'x', 'y']) #crating a hv.dataset for p_values
ps_mean = hv.Dataset(ds_mean_ps[['log_p']], kdims = ['month','reg', 'x', 'y'])  #crating a hv.dataset for p_mean

im_ps=ps.to(hv.QuadMesh, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts_pv) #creating quadmeshplot for p-values
im_mean_ps=ps_mean.to(hv.QuadMesh, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts_pv)



im = ds.to(hv.QuadMesh, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)                                                                                    
                                                                                      
im_pv = hv.operation.contours(im_ps,levels=[0.01,0.05]) #quadmesh to contours_plot

im_mean= ds_2.to(hv.QuadMesh, ['x', 'y'], dynamic=True, label="Average across all ens").redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)

im_mean_pv= hv.operation.contours(im_mean_ps,levels=3)
                                            
layout=hv.Layout(im*im_pv+im_mean*im_mean_pv).cols(1)
layout
# -
hv.help(hv.Contours)

