"""
This class control_widget the interactions between 3 MpImage classes which are used
to show the cross sections through a 4D object.  Using QT signals, it coordinates 
cursor line changes and image changes to match the current viewing cursor_loc in the 4D object.
"""

from ..navigation import NavigationToolbarSimple as NavigationToolbar
from .. import definitions as dd
from .. import image as _MplImage
from .. import plot as _MplPlot
import numpy as np
from PyQt5 import QtCore


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
        self.zslice = _zslice(complex_image=complexIm3[:, :, initLocation[2], initLocation[3]], cursor_loc=initLocation[0:2], slice_num=initLocation[2], maxSliceNum=complexIm3.shape[2],
                              display_type=dd.ImageDisplayType.mag, cursor_labels=labels, aspect=aspz, interpolation=interpolation)  # dpi doesn't affect imshow...cause imshow rescales to figure size
        self.zsliceNav = NavigationToolbar(self.zslice, self.zslice)

        labels = [{'color': 'g', 'textLabel': "X"}, {'color': 'b',
                                                     'textLabel': "Z"}, {'color': 'r', 'textLabel': "Y Slice"}]
        self.yslice = _yslice(complex_image=complexIm3[:, initLocation[1], :, initLocation[3]], cursor_loc=initLocation[0::2], slice_num=initLocation[1],
                              maxSliceNum=complexIm3.shape[1], display_type=dd.ImageDisplayType.mag, cursor_labels=labels, aspect=aspy, interpolation=interpolation)
        self.ysliceNav = NavigationToolbar(self.yslice, self.yslice)

        labels = [{'color': 'r', 'textLabel': "Z"}, {'color': 'g',
                                                     'textLabel': "Y"}, {'color': 'b', 'textLabel': "X Slice"}]
        self.xslice = _xslice(complex_image=complexIm3[initLocation[0], :, :, initLocation[3]].T, cursor_loc=initLocation[2:0:-1], slice_num=initLocation[0],
                              maxSliceNum=complexIm3.shape[0], display_type=dd.ImageDisplayType.mag, cursor_labels=labels, aspect=aspx, interpolation=interpolation)
        self.xsliceNav = NavigationToolbar(self.xslice, self.xslice)

        self.xplot = _MplPlot.MplPlot(
            [complexIm3[:, initLocation[1], initLocation[2], initLocation[3]], ], title="X Plot", init_marker=initLocation[0])
        self.yplot = _MplPlot.MplPlot(
            [complexIm3[initLocation[0], :, initLocation[2], initLocation[3]], ], title="Y Plot", init_marker=initLocation[1])
        self.zplot = _MplPlot.MplPlot(
            [complexIm3[initLocation[0], initLocation[1], :, initLocation[3]], ], title="Z Plot", init_marker=initLocation[2])
        self.tplot = _MplPlot.MplPlot(
            [complexIm3[initLocation[0], initLocation[1], initLocation[2], :], ], title="T Plot", init_marker=initLocation[3])


    def onXChange(self, value):
        # clip to valid locations, this is now done inside MplImage.mouse_move() before the change_location signal is emitted
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[0]-1)
        self.location[0] = value
        self.xslice.sliceNum = value
        self.xslice.onXChange(self.raw[value, :, :, self.location[3]].T)
        self.yslice.onXChange(value)
        self.zslice.onXChange(value)

        self.yplot.show_complex_data_and_markers_change(
            [self.raw[value, :, self.location[2], self.location[3]], ], self.location[1])
        self.zplot.show_complex_data_and_markers_change(
            [self.raw[value, self.location[1], :, self.location[3]], ], self.location[2])
        self.tplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    def onYChange(self, value):
        # clip to valid locations, this is now done inside MplImage.mouse_move() before the change_location signal is emitted
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[1]-1)
        self.location[1] = value
        self.yslice.sliceNum = value
        self.xslice.onYChange(value)
        self.yslice.onYChange(self.raw[:, value, :, self.location[3]])
        self.zslice.onYChange(value)

        self.xplot.show_complex_data_and_markers_change(
            [self.raw[:, value, self.location[2], self.location[3]], ], self.location[0])
        self.zplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], value, :, self.location[3]], ], self.location[2])
        self.tplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    def onZChange(self, value):
        # clip to valid locations, this is now done inside MplImage.mouse_move() before the change_location signal is emitted
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)
        self.location[2] = value
        self.zslice.sliceNum = value
        self.xslice.onZChange(value)
        self.yslice.onZChange(value)
        self.zslice.onZChange(self.raw[:, :, value, self.location[3]])

        self.xplot.show_complex_data_and_markers_change(
            [self.raw[:, self.location[1], value, self.location[3]], ], self.location[0])
        self.yplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], :, value, self.location[3]], ], self.location[1])
        self.tplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    def onTChange(self, value):
        # clip to valid locations?
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)
        self.location[3] = value
        self.xslice.onXChange(self.raw[self.location[0], :, :, value, ].T)
        self.yslice.onYChange(self.raw[:, self.location[1], :, value])
        self.zslice.onZChange(self.raw[:, :, self.location[2], value])

        self.xplot.show_complex_data_and_markers_change(
            [self.raw[:, self.location[1], self.location[2], self.location[3]], ], self.location[0])
        self.yplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], :, self.location[2], self.location[3]], ], self.location[1])
        self.zplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], self.location[1], :, self.location[3]], ], self.location[2])
        self.tplot.show_complex_data_and_markers_change(
            [self.raw[self.location[0], self.location[1], self.location[2], :], ], self.location[3])

    """
    def CMapChanged(self,index): 
        self.xslice.setColorMap(index)
        self.yslice.setColorMap(index)
        self.zslice.setColorMap(index)
    """

    def onImageTypeChange(self, index):
        self.xslice.show_display_type_change(index)
        self.yslice.show_display_type_change(index)
        self.zslice.show_display_type_change(index)
        self.xplot.show_data_type_change(index)
        self.yplot.show_data_type_change(index)
        self.zplot.show_data_type_change(index)
        self.tplot.show_data_type_change(index)
        # although the cmaps have already been changed by the MplImage class,
        # we need to change the control to indicate this...so we will
        # send out a signal to redundantly change the cmaps again
        # if index==dd.ImageDisplayType.mag or index == dd.ImageDisplayType.imag or index == dd.ImageDisplayType.real:
        #    core.mySignals.emit(QtCore.SIGNAL('imageCmapChanged'), dd.ImageCMap.gray)
        # elif index==dd.ImageDisplayType.phase:
        #    core.mySignals.emit(QtCore.SIGNAL('imageCmapChanged'), dd.ImageCMap.hsv)

    def onWindowLevelChange(self, Window, Level):
        self.xslice.show_window_level_change(Window, Level)
        self.yslice.show_window_level_change(Window, Level)
        self.zslice.show_window_level_change(Window, Level)

    def onWindowLevelReset(self):
        self.xslice.show_set_window_level_to_default()
        self.yslice.show_set_window_level_to_default()
        self.zslice.show_set_window_level_to_default()


class _zslice(_MplImage.MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_zslice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def emit_cursor_change(self, location):
        x = location.x
        y = location.y
        self.sig_x_change.emit(x)
        self.sig_y_change.emit(y)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.sig_z_change.emit(clipVal)

    def onXChange(self, x):
        # should this be a get function instead of accessing cursor_loc directly?
        self.show_cursor_loc_change([x, self.cursor_loc.y])

    def onYChange(self, y):
        self.show_cursor_loc_change([self.cursor_loc.x, y])

    def onZChange(self, complexImage):
        self.show_complex_image_change(complexImage)


class _yslice(_MplImage.MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_yslice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def emit_cursor_change(self, location):
        x = location.x
        z = location.y
        self.sig_x_change.emit(x)
        self.sig_z_change.emit(z)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.sig_y_change.emit(clipVal)

    def onXChange(self, x):
        self.show_cursor_loc_change([x, self.cursor_loc.y])

    def onZChange(self, z):
        self.show_cursor_loc_change([self.cursor_loc.x, z])

    def onYChange(self, complexImage):
        self.show_complex_image_change(complexImage)


class _xslice(_MplImage.MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_xslice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def emit_cursor_change(self, location):
        z = location.x
        y = location.y
        self.sig_z_change.emit(z)
        self.sig_y_change.emit(y)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.sig_x_change.emit(clipVal)

    def onZChange(self, z):
        self.show_cursor_loc_change([z, self.cursor_loc.y])

    def onYChange(self, y):
        self.show_cursor_loc_change([self.cursor_loc.x, y])

    def onXChange(self, complexImage):
        self.show_complex_image_change(complexImage)
