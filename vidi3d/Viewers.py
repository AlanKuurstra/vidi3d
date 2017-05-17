"""
This module contains all the functions a user needs to call and control the
behaviour of the viewers.
"""
import matplotlib as mpl
# mpl.use('Qt4Agg')
import matplotlib.pyplot as plt
# plt.ion()
from PyQt4 import QtGui, QtCore
import _Core as _Core
import Imshow._MainWindow4D
import Compare._MainWindowCompare
import numpy as np


def _startViewer(viewer, block, windowTitle=None):
    if block:
        if windowTitle is not None:
            viewer.setWindowTitle(windowTitle)
        QtGui.qApp.exec_()
        return
    else:
        viewerNum = _Core._storeViewer(viewer)
        viewer.setViewerNumber(viewerNum)

        if windowTitle is None:
            viewer.setWindowTitle('Viewer ' + str(viewerNum))
        else:
            viewer.setWindowTitle(windowTitle)

        return viewer


def imshow3d(data, pixdim=None, interpolation='none', block=True):
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
    viewer : `Imshow._MainWindow4D`

    """

    if data.ndim == 3:
        data = data[..., np.newaxis]
    viewer = Imshow._MainWindow4D._MainWindow(
        data, pixdim, interpolation=interpolation)
    if not block:
        viewer.imagePanel3D.raw = np.copy(viewer.imagePanel3D.raw)
        # if the viewer is run as not blocking, then the underlying data
        # can change later on in the script and effect the results shown
        # in the viewer.  Therefore, we must make a copy.  If you have a
        # large data set and don't want to wait for the copy or can't afford
        # the memory, then you should run the viewer with block=True
    return _startViewer(viewer, block)


def compare2d(data, pixdim=None, interpolation='none', origin='lower', windowTitle=None, subplotTitles=None, block=True, locationLabels=None, maxNumInRow=None, colormap=None, overlay=None, overlayColormap=None):
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

    windowTitle : string, optional, default: None
        The title to display on the viewer window.  

    subplotTitles : strings, optional, default: None
        A list of subplot titles. The number of titles must match the number
        of subplots otherwise default behaviour will be used. 

    block : boolean, optional, default: False
        If true, block execution of further code until all viewers are closed.

    locationLabels : strings, optional, default: None
        A list of cursor line labels. If None, use "X" and "Y".     

    maxNumInRow : integer, optional, default: None
        The maximum number of images to display in a row. 

    colormap : `~matplotlib.colors.Colormap`, optional, default: cm.Greys_r

    overlay : array_like, shape (x, y)
        Optional overlay.  Useful for viewing masks and parameter maps.

    overlayColormap : `~matplotlib.colors.Colormap`, optional, default: cm.Reds

    Returns
    --------
    viewer : `Compare._MainWindowCompare`
    """
    data = convertToListIfNecessary(data)
    colormap = convertToListIfNecessary(colormap)
    overlay = convertToListIfNecessary(overlay)
    overlayColormap = convertToListIfNecessary(overlayColormap)

    for img in data:
        assert img.shape == data[0].shape
    if data[0].ndim == 2:
        for indx in range(len(data)):
            data[indx] = data[indx][..., np.newaxis, np.newaxis]
    elif data[0].ndim == 3:
        for indx in range(len(data)):
            data[indx] = data[indx][..., np.newaxis, :]
    ndim = 0
    for i in range(max(len(data), len(overlay))):
        try:
            ndim = overlay[i].ndim
        except:
            pass
    if ndim == 2:
        for indx in range(len(overlay)):
            try:
                overlay[indx] = overlay[indx][..., np.newaxis]
            except:
                pass

    viewer = Compare._MainWindowCompare._MainWindow(data, pixdim=pixdim, interpolation=interpolation, origin=origin, subplotTitles=subplotTitles,
                                                    locationLabels=locationLabels, maxNumInRow=maxNumInRow, colormapList=colormap, overlayList=overlay, overlayColormapList=overlayColormap)
    return _startViewer(viewer, block, windowTitle)


def compare3d(data, pixdim=None, interpolation='none', origin='lower', windowTitle=None, subplotTitles=None, block=True, locationLabels=None, maxNumInRow=None, colormap=None, overlay=None, overlayColormap=None):
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

    windowTitle : string, optional, default: None
        The title to display on the viewer window.  

    subplotTitles : strings, optional, default: None
        A list of subplot titles. The number of titles must match the number
        of subplots otherwise default behaviour will be used. 

    block : boolean, optional, default: False
        If true, block execution of further code until all viewers are closed.

    locationLabels : strings, optional, default: None
        A list of cursor line labels. If None, use "X" and "Y".     

    maxNumInRow : integer, optional, default: None
        The maximum number of images to display in a row. 

    colormap : `~matplotlib.colors.Colormap`, optional, default: cm.Greys_r

    overlay : array_like, shape (x, y, z)
        Optional overlay.  Useful for viewing masks and parameter maps.

    overlayColormap : `~matplotlib.colors.Colormap`, optional, default: cm.Reds

    Returns
    --------
    viewer : `Compare._MainWindowCompare`
    """
    data = convertToListIfNecessary(data)
    colormap = convertToListIfNecessary(colormap)
    overlay = convertToListIfNecessary(overlay)
    overlayColormap = convertToListIfNecessary(overlayColormap)

    for img in data:
        assert img.shape == data[0].shape
    if data[0].ndim == 3:
        for indx in range(len(data)):
            data[indx] = data[indx][..., np.newaxis]
    viewer = Compare._MainWindowCompare._MainWindow(data, pixdim=pixdim, interpolation=interpolation, origin=origin, subplotTitles=subplotTitles,
                                                    locationLabels=locationLabels, maxNumInRow=maxNumInRow, colormapList=colormap, overlayList=overlay, overlayColormapList=overlayColormap)
    return _startViewer(viewer, block, windowTitle)


def toList(array, axis=-1, step=1):
    """
    Split a higher dimensional array into a list of lower dimensional arrays.
    Useful for splitting a 3d image into a list of 2d slices passed to compare2d.

    """
    slicesToGet = np.arange(0, array.shape[axis], step)
    tmp = np.take(array, slicesToGet, axis=axis)
    return np.split(tmp, tmp.shape[axis], axis=axis)


def convertToListIfNecessary(inputData):
    if type(inputData) != list and type(inputData) != tuple:
        inputData = [inputData, ]
    elif type(inputData) == tuple:
        inputData = list(inputData)
    return inputData


def close(num=None):
    """
    Close a Viewer.

    close('all') closes all figures

    close(num) closes viewer number num
    """
    _Core._checkViewerListExists()
    if type(num) is int:
        if num <= len(_Core._viewerList) and _Core._viewerList.has_key(num):
            _Core._viewerList[num].close()
    if num.lower() == 'all':
        _Core._viewerList.clear()


def pause(pauseTime):
    """
    Pause for pauseTime milliseconds.

    Viewers will be updated and displayed, and the GUI event loop will run during the pause.
    """

    # pause time is in milliseconds
    loop = QtCore.QEventLoop()
    timer = QtCore.QTimer()
    timer.singleShot(pauseTime, loop.quit)
    loop.exec_()
