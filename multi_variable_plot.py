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

import xarray as xr
from pathlib import Path
import glob
import holoviews as hv
from holoviews import opts
import hvplot.xarray

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
# -

ds


co_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, tools = ['hover'], frame_width = 300)
coefs = ds['coefs'].hvplot.quadmesh('lat','plev',**co_opts).opts(opts.QuadMesh(title='Model', invert_yaxis=True))
coefs
