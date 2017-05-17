"""
This class controls the interactions between 3 MpImage classes which are used
to show the cross sections through a 4D object.  Using QT signals, it coordinates 
cursor line changes and image changes to match the current viewing location in the 4D object.
"""

from .._NavigationToolbar import NavigationToolbar
from .. import _DisplayDefinitions as dd
from .. import _MplImage as _MplImage
from .. import _MplPlot as _MplPlot
import numpy as np
from PyQt4 import QtCore


class _MplImage4D(QtCore.QObject):
    def __init__(self, complexIm3, pixdim, interpolation, initLocation, imageType, parent=None):
        super(_MplImage4D, self).__init__()

        self.raw = complexIm3
        self.location = initLocation

        if pixdim == None:
            aspz = aspy = aspx = 'equal'
        else:
            aspz = float(pixdim[1]) / pixdim[0]
            aspy = float(pixdim[2]) / pixdim[0]
            aspx = float(pixdim[1]) / pixdim[2]

        labels = [{'color': 'r', 'textLabel': "X"}, {'color': 'b',
                                                     'textLabel': "Y"}, {'color': 'g', 'textLabel': "Z Slice"}]
        self.zslice = _zslice(parent=parent, complexImage=complexIm3[:, :, initLocation[2], initLocation[3]], location=initLocation[0:2], sliceNum=initLocation[2], maxSliceNum=complexIm3.shape[2],
                              imageType=dd.ImageType.mag, locationLabels=labels, aspect=aspz, interpolation=interpolation)  # dpi doesn't affect imshow...cause imshow rescales to figure size
        self.zsliceNav = NavigationToolbar(self.zslice, self.zslice)

        labels = [{'color': 'g', 'textLabel': "X"}, {'color': 'b',
                                                     'textLabel': "Z"}, {'color': 'r', 'textLabel': "Y Slice"}]
        self.yslice = _yslice(parent=parent, complexImage=complexIm3[:, initLocation[1], :, initLocation[3]], location=initLocation[0::2], sliceNum=initLocation[1],
                              maxSliceNum=complexIm3.shape[1], imageType=dd.ImageType.mag, locationLabels=labels, aspect=aspy, interpolation=interpolation)
        self.ysliceNav = NavigationToolbar(self.yslice, self.yslice)

        labels = [{'color': 'r', 'textLabel': "Z"}, {'color': 'g',
                                                     'textLabel': "Y"}, {'color': 'b', 'textLabel': "X Slice"}]
        self.xslice = _xslice(parent=parent, complexImage=complexIm3[initLocation[0], :, :, initLocation[3]].T, location=initLocation[2:0:-1], sliceNum=initLocation[0],
                              maxSliceNum=complexIm3.shape[0],  imageType=dd.ImageType.mag, locationLabels=labels,  aspect=aspx, interpolation=interpolation)
        self.xsliceNav = NavigationToolbar(self.xslice, self.xslice)

        self.xplot = _MplPlot._MplPlot(
            [complexIm3[:, initLocation[1], initLocation[2], initLocation[3]], ], title="X Plot", initMarkerPosn=initLocation[0])
        self.yplot = _MplPlot._MplPlot(
            [complexIm3[initLocation[0], :, initLocation[2], initLocation[3]], ], title="Y Plot", initMarkerPosn=initLocation[1])
        self.zplot = _MplPlot._MplPlot(
            [complexIm3[initLocation[0], initLocation[1], :, initLocation[3]], ], title="Z Plot", initMarkerPosn=initLocation[2])
        self.tplot = _MplPlot._MplPlot(
            [complexIm3[initLocation[0], initLocation[1], initLocation[2], :], ], title="T Plot", initMarkerPosn=initLocation[3])

    def onXChange(self, value):
        # clip to valid locations, this is now done inside _MplImage.MoveEvent() before the ChangeLocation signal is emitted
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[0]-1)
        self.location[0] = value
        self.xslice.sliceNum = value
        self.xslice.onXChange(self.raw[value, :, :, self.location[3]].T)
        self.yslice.onXChange(value)
        self.zslice.onXChange(value)

        self.yplot.showComplexDataAndMarkersChange(
            [self.raw[value, :, self.location[2], self.location[3]], ], self.location[1])
        self.zplot.showComplexDataAndMarkersChange(
            [self.raw[value, self.location[1], :, self.location[3]], ], self.location[2])
        self.tplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    def onYChange(self, value):
        # clip to valid locations, this is now done inside _MplImage.MoveEvent() before the ChangeLocation signal is emitted
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[1]-1)
        self.location[1] = value
        self.yslice.sliceNum = value
        self.xslice.onYChange(value)
        self.yslice.onYChange(self.raw[:, value, :, self.location[3]])
        self.zslice.onYChange(value)

        self.xplot.showComplexDataAndMarkersChange(
            [self.raw[:, value, self.location[2], self.location[3]], ], self.location[0])
        self.zplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], value, :, self.location[3]], ], self.location[2])
        self.tplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    def onZChange(self, value):
        # clip to valid locations, this is now done inside _MplImage.MoveEvent() before the ChangeLocation signal is emitted
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)
        self.location[2] = value
        self.zslice.sliceNum = value
        self.xslice.onZChange(value)
        self.yslice.onZChange(value)
        self.zslice.onZChange(self.raw[:, :, value, self.location[3]])

        self.xplot.showComplexDataAndMarkersChange(
            [self.raw[:, self.location[1], value, self.location[3]], ], self.location[0])
        self.yplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], :, value, self.location[3]], ], self.location[1])
        self.tplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    def onTChange(self, value):
        # clip to valid locations?
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)
        self.location[3] = value
        self.xslice.onXChange(self.raw[self.location[0], :, :, value, ].T)
        self.yslice.onYChange(self.raw[:, self.location[1], :, value])
        self.zslice.onZChange(self.raw[:, :, self.location[2], value])

        self.xplot.showComplexDataAndMarkersChange(
            [self.raw[:, self.location[1], self.location[2], self.location[3]], ], self.location[0])
        self.yplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], :, self.location[2], self.location[3]], ], self.location[1])
        self.zplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], self.location[1], :, self.location[3]], ], self.location[2])
        self.tplot.showComplexDataAndMarkersChange(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    """
    def CMapChanged(self,index): 
        self.xslice.setColorMap(index)
        self.yslice.setColorMap(index)
        self.zslice.setColorMap(index)
    """

    def onImageTypeChange(self, index):
        self.xslice.showImageTypeChange(index)
        self.yslice.showImageTypeChange(index)
        self.zslice.showImageTypeChange(index)
        self.xplot.showDataTypeChange(index)
        self.yplot.showDataTypeChange(index)
        self.zplot.showDataTypeChange(index)
        self.tplot.showDataTypeChange(index)
        # although the cmaps have already been changed by the _MplImage class,
        # we need to change the control to indicate this...so we will
        # send out a signal to redundantly change the cmaps again
        # if index==dd.ImageType.mag or index == dd.ImageType.imag or index == dd.ImageType.real:
        #    _Core.mySignals.emit(QtCore.SIGNAL('imageCmapChanged'), dd.ImageCMap.gray)
        # elif index==dd.ImageType.phase:
        #    _Core.mySignals.emit(QtCore.SIGNAL('imageCmapChanged'), dd.ImageCMap.hsv)

    def onWindowLevelChange(self, Window, Level):
        self.xslice.showWindowLevelChange(Window, Level)
        self.yslice.showWindowLevelChange(Window, Level)
        self.zslice.showWindowLevelChange(Window, Level)

    def onWindowLevelReset(self):
        self.xslice.showSetWindowLevelToDefault()
        self.yslice.showSetWindowLevelToDefault()
        self.zslice.showSetWindowLevelToDefault()


class _zslice(_MplImage._MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_zslice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def _signalCursorChange(self, location):
        x, y = location
        self.signalXLocationChange.emit(x)
        self.signalYLocationChange.emit(y)

    def wheelEvent(self, event):
        if event.delta() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.signalZLocationChange.emit(clipVal)

    def onXChange(self, x):
        # should this be a get function instead of accessing location directly?
        self.showLocationChange([x, self.location[1]])

    def onYChange(self, y):
        self.showLocationChange([self.location[0], y])

    def onZChange(self, complexImage):
        self.showComplexImageChange(complexImage)


class _yslice(_MplImage._MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_yslice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def _signalCursorChange(self, location):
        x, z = location
        self.signalXLocationChange.emit(x)
        self.signalZLocationChange.emit(z)

    def wheelEvent(self, event):
        if event.delta() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.signalYLocationChange.emit(clipVal)

    def onXChange(self, x):
        self.showLocationChange([x, self.location[1]])

    def onZChange(self, z):
        self.showLocationChange([self.location[0], z])

    def onYChange(self, complexImage):
        self.showComplexImageChange(complexImage)


class _xslice(_MplImage._MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_xslice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def _signalCursorChange(self, location):
        z, y = location
        self.signalZLocationChange.emit(z)
        self.signalYLocationChange.emit(y)

    def wheelEvent(self, event):
        if event.delta() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.signalXLocationChange.emit(clipVal)

    def onZChange(self, z):
        self.showLocationChange([z, self.location[1]])

    def onYChange(self, y):
        self.showLocationChange([self.location[0], y])

    def onXChange(self, complexImage):
        self.showComplexImageChange(complexImage)
