"""
This module contains all the functions a user needs to call and control the
behaviour of the viewers.
"""
import matplotlib.pyplot as plt

plt.ion()
from .core import start_viewer, to_list
from vidi3d.imshow.main import Imshow3d as Imshow3d
from vidi3d.compare.main import Compare as Compare
import numpy as np


def imshow3d(data,
             pixdim=None,
             interpolation='none',
             block=True):
    """
    A viewer that displays cross sections of a 3D image.

    Parameters
    -----------
    data : array_like, shape (x, y, z) 
        The data to be displayed. 

    pixdim : list of voxel sizes for each dimesion. For nifti files this
             can be found using: nib.load(imgloc).get_header()['pixdim'][1:4]

    interpolation : string, optional, default: 'none'
        Acceptable values are 'none', 'nearest', 'bilinear', 'bicubic',
        'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
        'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc',
        'lanczos'

        If `interpolation` is 'none', then no interpolation is performed
        on the Agg, ps and pdf backends. Other backends will fall back to
        'nearest'. 

    block : boolean, optional, default: False
        If true, block execution of further code until all viewers are closed. 

    Returns
    --------
    viewer : `imshow._MainWindow4D`

    """

    if data.ndim == 3:
        data = data[..., np.newaxis]
    viewer = Imshow3d(data, pixdim, interpolation=interpolation)
    if not block:
        viewer.image4d.complex_image = np.copy(viewer.image4d.complex_image)
        # if the viewer is run as not blocking, then the underlying data
        # can change later on in the script and effect the results shown
        # in the viewer.  Therefore, we must make a copy.  If you have a
        # large data set and don't want to wait for the copy or can't afford
        # the memory, then you should run the viewer with block=True
    return start_viewer(viewer, block)


def compare2d(data,
              pixdim=None,
              interpolation='none',
              origin='lower',
              window_title=None,
              subplot_titles=None,
              block=True,
              location_labels=None,
              max_in_row=None,
              cmaps=None,
              overlays=None,
              overlay_cmaps=None):
    """
    A viewer that displays multiple 2D images for comparison.

    Parameters
    -----------
    data : array_like, shape (x, y[, t])
        The data to be displayed. Can be a single 2d image f(x,y[,t]) or a list of
        2d images [f1(x,y[,t]),f2(x,y[,t]),...,fn(x,y[,t])].

    pixdim : list of voxel sizes for each dimesion. For nifti files this
             can be found using: nib.load(imgloc).get_header()['pixdim'][1:3]

    interpolation : string, optional, default: 'none'
        Acceptable values are 'none', 'nearest', 'bilinear', 'bicubic',
        'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
        'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc',
        'lanczos'

        If `interpolation` is 'none', then no interpolation is performed
        on the Agg, ps and pdf backends. Other backends will fall back to
        'nearest'.       

    origin : ['upper' | 'lower'], optional, default: None
        Place the [0,0] index of the array in the upper left or lower left
        corner of the axes. If None, default to rc `image.origin`.

    window_title : string, optional, default: None
        The title to display on the viewer window.  

    subplot_titles : strings, optional, default: None
        A list of subplot titles. The number of titles must match the number
        of subplots otherwise default behaviour will be used. 

    block : boolean, optional, default: False
        If true, block execution of further code until all viewers are closed.

    location_labels : strings, optional, default: None
        A list of cursor line labels. If None, use "X" and "Y".     

    max_in_row : integer, optional, default: None
        The maximum number of images to display in a row. 

    cmaps : `~matplotlib.colors.Colormap`, optional, default: cm.Greys_r

    overlays : array_like, shape (x, y)
        Optional overlays.  Useful for viewing masks and parameter maps.

    overlay_cmaps : `~matplotlib.colors.Colormap`, optional, default: cm.Reds

    Returns
    --------
    viewer : `compare._MainWindowCompare`
    """
    data = to_list(data)
    cmaps = to_list(cmaps)
    overlays = to_list(overlays)
    overlay_cmaps = to_list(overlay_cmaps)
    subplot_titles = to_list(subplot_titles)

    for img in data:
        assert img.shape == data[0].shape
    if data[0].ndim == 2:
        for indx in range(len(data)):
            data[indx] = data[indx][..., np.newaxis, np.newaxis]
    elif data[0].ndim == 3:
        for indx in range(len(data)):
            data[indx] = data[indx][..., np.newaxis, :]
    ndim = 0
    for i in range(max(len(data), len(overlays))):
        try:
            ndim = overlays[i].ndim
        except:
            pass
    if ndim == 2:
        for indx in range(len(overlays)):
            try:
                overlays[indx] = overlays[indx][..., np.newaxis]
            except:
                pass
    viewer = Compare(data,
                     pixdim=pixdim,
                     interpolation=interpolation,
                     origin=origin,
                     subplot_titles=subplot_titles,
                     location_labels=location_labels,
                     max_in_row=max_in_row,
                     cmaps=cmaps,
                     overlays=overlays,
                     overlay_cmaps=overlay_cmaps)

    return start_viewer(viewer, block, window_title)


def compare3d(data,
              pixdim=None,
              interpolation='none',
              origin='lower',
              window_title=None,
              subplot_titles=None,
              block=True,
              location_labels=None,
              max_in_row=None,
              cmaps=None,
              overlays=None,
              overlay_cmaps=None,
              mmb_callback=None,
              ):
    """
    A viewer that displays multiple 3D images for comparison.

    Parameters
    -----------
    data : array_like, shape (x, y, z[, t])
        The data to be displayed. Can be a single 2d image f(x,y,z[,t]) or a list of
        3d images [f1(x,y,z[,t]),f2(x,y,z[,t]),...,fn(x,y,z[,t])].

    pixdim : list of voxel sizes for each dimesion. For nifti files this
             can be found using: nib.load(imgloc).get_header()['pixdim'][1:4]

    interpolation : string, optional, default: 'none'
        Acceptable values are 'none', 'nearest', 'bilinear', 'bicubic',
        'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
        'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc',
        'lanczos'

        If `interpolation` is 'none', then no interpolation is performed
        on the Agg, ps and pdf backends. Other backends will fall back to
        'nearest'.       

    origin : ['upper' | 'lower'], optional, default: None
        Place the [0,0] index of the array in the upper left or lower left
        corner of the axes. If None, default to rc `image.origin`.

    window_title : string, optional, default: None
        The title to display on the viewer window.  

    subplot_titles : strings, optional, default: None
        A list of subplot titles. The number of titles must match the number
        of subplots otherwise default behaviour will be used. 

    block : boolean, optional, default: False
        If true, block execution of further code until all viewers are closed.

    location_labels : strings, optional, default: None
        A list of cursor line labels. If None, use "X" and "Y".     

    max_in_row : integer, optional, default: None
        The maximum number of images to display in a row. 

    cmap : `~matplotlib.colors.Colormap`, optional, default: cm.Greys_r

    overlays : array_like, shape (x, y, z)
        Optional overlays.  Useful for viewing masks and parameter maps.

    overlay_cmap : `~matplotlib.colors.Colormap`, optional, default: cm.Reds

    Returns
    --------
    viewer : `compare._MainWindowCompare`
    """
    data = to_list(data)
    cmaps = to_list(cmaps)
    overlays = to_list(overlays)
    overlay_cmaps = to_list(overlay_cmaps)
    subplot_titles = to_list(subplot_titles)

    for img in data:
        assert img.shape == data[0].shape
    if data[0].ndim == 3:
        for indx in range(len(data)):
            data[indx] = data[indx][..., np.newaxis]
    viewer = Compare(data,
                     pixdim=pixdim,
                     interpolation=interpolation,
                     origin=origin,
                     subplot_titles=subplot_titles,
                     location_labels=location_labels,
                     max_in_row=max_in_row,
                     cmaps=cmaps,
                     overlays=overlays,
                     overlay_cmaps=overlay_cmaps,
                     mmb_callback=mmb_callback,
                     )
    return start_viewer(viewer, block, window_title)
