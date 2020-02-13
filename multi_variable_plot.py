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
#from scipy.stats import combine_pvalues
#hv.extension('bokeh')
#import scipy.stats as st
#import panel as pn

#

def combine_by_period(var):
    new = '2011-2099'
    old ='1960-2010'
    old_data = sorted(glob.glob(f'zmnoy_full/{var}*{old}*.nc'))
    new_data = sorted(glob.glob(f'zmnoy_full/{var}*{new}*.nc'))
    ds_old = xr.open_mfdataset(old_data, concat_dim='ens', combine = 'nested')
    ds_new = xr.open_mfdataset(new_data, concat_dim='ens', combine = 'nested')
    ds = xr.concat([ds_old, ds_new], 'period')
    ds['period'] =[old,new]
    return(ds)


ds_zmnoy = combine_by_period('zmnoy')
ds_zmo3  = combine_by_period('zmo3')
ds_zmta  = combine_by_period('zmta')
ds_zmua  = combine_by_period('zmua')
ds = xr.concat([ds_zmnoy, ds_zmo3,ds_zmta, ds_zmua], 'vari')
ds['vari'] =['zmnoy','zmo3','zmta','zmua']

co_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, tools = ['hover'], frame_width = 300)
coefs = ds['coefs'].hvplot.quadmesh('lat','plev',**co_opts).redim.range(coefs=(-1.0,1.0)).opts(opts.QuadMesh(title='Model', invert_yaxis=True))

