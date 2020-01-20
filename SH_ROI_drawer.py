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
#from ipywebrtc.webrtc import VideoRecorder, WidgetStream

from ipywebrtc.webrtc import VideoRecorder, WidgetStream

# # Data loading

invar = 'zmnoy'
infiles = sorted(glob.glob(f'zmnoy_files/{invar}*.nc'))
ds_xa = xr.open_mfdataset(infiles, concat_dim='ens', combine = 'nested')# Open multiple files as a single dataset
ds_xa

# +
#a=xr.open_dataset(infiles[0]) #Data Inspection
#a.var
#a.coords
#a.attrs
#a.coords['lat']    #show one specific coordinate
#a.coords['plev']
#a.coefs   
#a.sel(lat=0, plev=1.00e+03,reg='intercept', month=1)
# -

sel_reg = 'f107'
sel_month = 1
month_names = ['January', 'February','March','April','May','June','July','Sep','Oct','Nov','Dec']
sel_dict = dict(reg = sel_reg, month = sel_month)
ds_sel = ds_xa.sel(**sel_dict).rename({'lat': 'x', 'plev': 'y'})
ds_sel['coefs'].attrs['units'] = '%'
ens_ls = ['WACCM_r1', 'WACCM_r2', 'WACCM_r3', 'SOCOL']
ds_sel['ens'] = range(4)
ds_sel

ds = hv.Dataset(ds_sel[['coefs']], kdims = ['ens', 'x', 'y'])
vmax = 40
vmin = -vmax
f_width = 300
hvc_opts = dict(logy = True, cmap = 'RdBu_r', symmetric=True, colorbar = True, \
                tools = ['hover'], invert_yaxis=True, frame_width = f_width)
im = ds.to(hv.QuadMesh, ['x', 'y'], dynamic=True).redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)
im2 = ds.aggregate(['x','y'], np.mean).to(hv.QuadMesh, ['x', 'y'], dynamic=True)
im2 = im2.redim.range(coefs=(vmin,vmax)).opts(**hvc_opts)

# +
polys = hv.Polygons([])
box_stream = streams.BoxEdit(source=polys)

def roi_curves(data):
    if not data or not any(len(d) for d in data.values()):
        return hv.NdOverlay({0: hv.Curve([], 'ens', 'coefs')})
    
    curves = {}
    data = zip(data['x0'], data['x1'], data['y0'], data['y1'])
    for i, (x0, x1, y0, y1) in enumerate(data):
        selection = ds.select(x=(x0, x1), y=(y1, y0)) # swap y0 and y1 when inverted y-axis
        curves[i] = hv.Spread(selection.aggregate('ens', np.mean, np.std))
    return hv.NdOverlay(curves)

hlines = hv.HoloMap({i: hv.VLine(i, label = ens_name ) for i, ens_name in enumerate(ens_ls)}, 'ens')
dmap = hv.DynamicMap(roi_curves, streams=[box_stream]).redim.range(ens=(0,3.5))


# -

def combine_pvalues_ufunc(arr):
    _, pv = combine_pvalues(arr, method = 'stouffer')
    return pv


# +
hvc_opts = dict(groupby=['ens'], width=300, dynamic=True, \
                                         x = 'x', y = 'y',  colorbar = False, \
                                      logy = True, cmap = ['black', 'gray'], \
                                                levels=[0.01,0.05])

imgs_pv = ds_sel['p_values'].hvplot.contour(**hvc_opts)
temp = xr.apply_ufunc(combine_pvalues_ufunc, ds_sel['p_values'], input_core_dims=[['ens']], \
               output_core_dims = [[]], vectorize = True, dask = 'allowed')

hvc_opts = dict(width=300, dynamic=True, \
                                         x = 'x', y = 'y',  colorbar = False, \
                                      logy = True, cmap = ['black', 'gray'], \
                                                levels=[0.01,0.05])
imgs_pv2 = temp.hvplot.contour(**hvc_opts)
# -

hl = hv.HLine(0).opts(color = 'gray', line_dash = 'dotted')
dmap = dmap.opts(xticks=[(i, ens_name) for i,ens_name in enumerate(ens_ls)])
first_panel = im * imgs_pv * polys
second_panel = (dmap * hl * hlines).relabel('ROI drawer')
hv_div = hv.Div(f"""<h1>{invar} response to {sel_reg} for {month_names[sel_month-1]}</h1>""")
second_row = ((im2*imgs_pv2).relabel('Model average (p-values combined using Z-score)')+hv_div)
layout = ((first_panel + second_panel).opts(
    opts.Curve(width=400, framewise=True), 
    opts.Polygons(fill_alpha=0.2, line_color='green', fill_color ='green'), 
    opts.VLine(color='black'))+second_row).cols(2)

# recorder = VideoRecorder(filename='test', format='mp4', codecs='vp9')
# recorder.recording = True
# layout

layout

renderer = hv.renderer('bokeh')
doc = renderer.server_doc(layout)
doc.title = 'HoloViews App'
