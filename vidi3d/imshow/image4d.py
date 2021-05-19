"""
This class control_widget the interactions between 3 MpImage classes which are used
to show the cross sections through a 4D object.  Using QT signals, it coordinates 
cursor line changes and image changes to match the current viewing cursor_loc in the 4D object.
"""

import numpy as np
from PyQt5 import QtCore

from ..definitions import SliceCoord
from ..image import MplImage
from ..navigation import NavigationToolbarSimple as NavigationToolbar
from ..plot import MplPlot


class Image4D(QtCore.QObject):
    def __init__(self,
                 complex_image,
                 cursor_loc,
                 display_type,
                 pixdim,
                 interpolation,
                 ):
        super(Image4D, self).__init__()

        self.complex_image = complex_image
        img_shape = complex_image.shape
        self.cursor_loc = cursor_loc

        if pixdim is None:
            aspect_z = aspect_y = aspect_x = 'equal'
        else:
            aspect_z = float(pixdim[1]) / pixdim[0]
            aspect_y = float(pixdim[2]) / pixdim[0]
            aspect_x = float(pixdim[1]) / pixdim[2]

        # dpi doesn't affect imshow because imshow rescales to figure size
        labels = [{'color': 'r', 'textLabel': "X"}, {'color': 'b', 'textLabel': "Y"},
                  {'color': 'g', 'textLabel': "Z Slice"}]
        self.zslice = ZSlice(complex_image=complex_image[:, :, cursor_loc.z, cursor_loc.t],
                             cursor_loc=SliceCoord(cursor_loc.x, cursor_loc.y),
                             slice_num=cursor_loc.z,
                             max_slice_num=img_shape[2],
                             display_type=display_type,
                             cursor_labels=labels,
                             aspect=aspect_z,
                             interpolation=interpolation)
        self.z_nav = NavigationToolbar(self.zslice, self.zslice)

        labels = [{'color': 'g', 'textLabel': "X"}, {'color': 'b', 'textLabel': "Z"},
                  {'color': 'r', 'textLabel': "Y Slice"}]
        self.yslice = YSlice(complex_image=complex_image[:, cursor_loc.y, :, cursor_loc.t],
                             cursor_loc=SliceCoord(cursor_loc.x, cursor_loc.z),
                             slice_num=cursor_loc.y,
                             max_slice_num=img_shape[1],
                             display_type=display_type,
                             cursor_labels=labels,
                             aspect=aspect_y,
                             interpolation=interpolation)
        self.y_nav = NavigationToolbar(self.yslice, self.yslice)

        labels = [{'color': 'r', 'textLabel': "Z"}, {'color': 'g', 'textLabel': "Y"},
                  {'color': 'b', 'textLabel': "X Slice"}]
        self.xslice = XSlice(complex_image=complex_image[cursor_loc.x, :, :, self.cursor_loc.t].T,
                             cursor_loc=SliceCoord(cursor_loc.z, cursor_loc.y),
                             slice_num=cursor_loc.x,
                             max_slice_num=img_shape[0],
                             display_type=display_type,
                             cursor_labels=labels,
                             aspect=aspect_x,
                             interpolation=interpolation)
        self.x_nav = NavigationToolbar(self.xslice, self.xslice)

        self.xplot = MplPlot([complex_image[:, cursor_loc.y, cursor_loc.z, cursor_loc.t], ],
                             title="X Plot",
                             init_marker=cursor_loc.x)
        self.yplot = MplPlot([complex_image[cursor_loc.x, :, cursor_loc.z, cursor_loc.t], ],
                             title="Y Plot",
                             init_marker=cursor_loc.y)
        self.zplot = MplPlot([complex_image[cursor_loc.x, cursor_loc.y, :, cursor_loc.t], ],
                             title="Z Plot",
                             init_marker=cursor_loc.z)
        self.tplot = MplPlot([complex_image[cursor_loc.x, cursor_loc.y, cursor_loc.z, :], ],
                             title="T Plot",
                             init_marker=cursor_loc.t)

    def update_plots(self):
        self.xplot.show_complex_data_and_markers_change(
            [self.complex_image[:, self.cursor_loc.y, self.cursor_loc.z, self.cursor_loc.t], ], self.cursor_loc.x)
        self.yplot.show_complex_data_and_markers_change(
            [self.complex_image[self.cursor_loc.x, :, self.cursor_loc.z, self.cursor_loc.t], ], self.cursor_loc.y)
        self.zplot.show_complex_data_and_markers_change(
            [self.complex_image[self.cursor_loc.x, self.cursor_loc.y, :, self.cursor_loc.t], ], self.cursor_loc.z)
        self.tplot.show_complex_data_and_markers_change(
            [self.complex_image[self.cursor_loc.x, self.cursor_loc.y, self.cursor_loc.z, :], ], self.cursor_loc.t)

    # todo: slot naming convention?
    def on_x_change(self, value):
        # todo: figure out clipping
        # clip to valid locations, this is now done inside MplImage.mouse_move() before the change_location signal is emitted
        # value = np.minimum(np.maximum(value+0.5, 0), self.complex_image.shape[0]-1)
        self.cursor_loc.x = value
        self.xslice.slice_num = value
        self.xslice.on_x_change(self.complex_image[value, :, :, self.cursor_loc.t].T)
        self.yslice.on_x_change(value)
        self.zslice.on_x_change(value)

        self.update_plots()

    def on_y_change(self, value):
        # todo: figure out clipping
        # clip to valid locations, this is now done inside MplImage.mouse_move() before the change_location signal is emitted
        # value = np.minimum(np.maximum(value+0.5, 0), self.complex_image.shape[1]-1)
        self.cursor_loc.y = value
        self.yslice.slice_num = value
        self.xslice.on_y_change(value)
        self.yslice.on_y_change(self.complex_image[:, value, :, self.cursor_loc.t])
        self.zslice.on_y_change(value)

        self.update_plots()

    def on_z_change(self, value):
        # todo: figure out clipping
        # clip to valid locations, this is now done inside MplImage.mouse_move() before the change_location signal is emitted
        # value = np.minimum(np.maximum(value+0.5, 0), self.complex_image.shape[2]-1)
        self.cursor_loc.z = value
        self.zslice.slice_num = value
        self.xslice.on_z_change(value)
        self.yslice.on_z_change(value)
        self.zslice.on_z_change(self.complex_image[:, :, value, self.cursor_loc.t])

        self.update_plots()

    def on_t_change(self, value):
        # todo: figure out clipping
        # clip to valid locations?
        # value = np.minimum(np.maximum(value+0.5, 0), self.complex_image.shape[2]-1)
        self.cursor_loc.t = value
        self.xslice.on_x_change(self.complex_image[self.cursor_loc.x, :, :, value, ].T)
        self.yslice.on_y_change(self.complex_image[:, self.cursor_loc.y, :, value])
        self.zslice.on_z_change(self.complex_image[:, :, self.cursor_loc.z, value])

        self.update_plots()

    def on_display_type_change(self, index):
        self.xslice.show_display_type_change(index)
        self.yslice.show_display_type_change(index)
        self.zslice.show_display_type_change(index)
        self.xplot.show_data_type_change(index)
        self.yplot.show_data_type_change(index)
        self.zplot.show_data_type_change(index)
        self.tplot.show_data_type_change(index)

    def on_window_level_change(self, window, level):
        self.xslice.show_window_level_change(window, level)
        self.yslice.show_window_level_change(window, level)
        self.zslice.show_window_level_change(window, level)

    def on_window_level_reset(self):
        self.xslice.show_set_window_level_to_default()
        self.yslice.show_set_window_level_to_default()
        self.zslice.show_set_window_level_to_default()


class ZSlice(MplImage):
    def __init__(self, slice_num=0, max_slice_num=0, *args, **keywords):
        super(ZSlice, self).__init__(*args, **keywords)
        self.slice_num = slice_num
        self.max_slice_num = max_slice_num

    def emit_cursor_change(self, location):
        x = location.x
        y = location.y
        self.sig_x_change.emit(x)
        self.sig_y_change.emit(y)

    def wheelEvent(self, event):
        # todo: figure out clipping
        if event.angleDelta().y() > 0:
            clip_val = np.minimum(np.maximum(self.slice_num + 1, 0), self.max_slice_num - 1)
        else:
            clip_val = np.minimum(np.maximum(self.slice_num - 1, 0), self.max_slice_num - 1)
        self.sig_z_change.emit(clip_val)

    # todo: slot naming convention?
    def on_x_change(self, x):
        # should this be a get function instead of accessing cursor_loc directly?
        self.show_cursor_loc_change([x, self.cursor_loc.y])

    def on_y_change(self, y):
        self.show_cursor_loc_change([self.cursor_loc.x, y])

    def on_z_change(self, complex_image):
        self.show_complex_image_change(complex_image)


class YSlice(MplImage):
    def __init__(self, slice_num=0, max_slice_num=0, *args, **keywords):
        super(YSlice, self).__init__(*args, **keywords)
        self.slice_num = slice_num
        self.max_slice_num = max_slice_num

    def emit_cursor_change(self, location):
        x = location.x
        z = location.y
        self.sig_x_change.emit(x)
        self.sig_z_change.emit(z)

    def wheelEvent(self, event):
        # todo: figure out clipping
        if event.angleDelta().y() > 0:
            clip_val = np.minimum(np.maximum(self.slice_num + 1, 0), self.max_slice_num - 1)
        else:
            clip_val = np.minimum(np.maximum(self.slice_num - 1, 0), self.max_slice_num - 1)
        self.sig_y_change.emit(clip_val)

    # todo: slot naming convention?
    def on_x_change(self, x):
        self.show_cursor_loc_change([x, self.cursor_loc.y])

    def on_z_change(self, z):
        self.show_cursor_loc_change([self.cursor_loc.x, z])

    def on_y_change(self, complex_image):
        self.show_complex_image_change(complex_image)


class XSlice(MplImage):
    def __init__(self, slice_num=0, max_slice_num=0, *args, **keywords):
        super(XSlice, self).__init__(*args, **keywords)
        self.slice_num = slice_num
        self.max_slice_num = max_slice_num

    def emit_cursor_change(self, location):
        z = location.x
        y = location.y
        self.sig_z_change.emit(z)
        self.sig_y_change.emit(y)

    def wheelEvent(self, event):
        # todo: figure out clipping
        if event.angleDelta().y() > 0:
            clip_val = np.minimum(np.maximum(self.slice_num + 1, 0), self.max_slice_num - 1)
        else:
            clip_val = np.minimum(np.maximum(self.slice_num - 1, 0), self.max_slice_num - 1)
        self.sig_x_change.emit(clip_val)

    # todo: slot naming convention?
    def on_z_change(self, z):
        self.show_cursor_loc_change([z, self.cursor_loc.y])

    def on_y_change(self, y):
        self.show_cursor_loc_change([self.cursor_loc.x, y])

    def on_x_change(self, complex_image):
        self.show_complex_image_change(complex_image)
