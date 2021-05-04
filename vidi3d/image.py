"""
Base class for images shown in the viewers. Instances of this class are used
to setup an arbitrary number of 2D images for comparison.  Instances of this
class are also used to show the 3 cross sectional views of a 3D image.
"""
import matplotlib as mpl
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .definitions import Coordinates, ImageDisplayType
from .signals import Signals


class MplImage(Signals, FigureCanvas):
    def __init__(self,
                 complex_image,
                 aspect='equal',
                 overlay=None,
                 interpolation='none',
                 origin='lower',
                 display_type=None,
                 cursor_loc=None,
                 slice_num=0,
                 cursor_labels=None,
                 cmap=None,
                 overlay_cmap=None):
        self.fig = mpl.figure.Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # can't set parent in FigureCanvas __init__, set it manually
        # self.parent = parent

        # Event related initialization
        self._idMove = self.mpl_connect('motion_notify_event', self.mouse_move)
        self._idPress = self.mpl_connect('button_press_event', self.mouse_press)
        self._idRelease = self.mpl_connect('button_release_event', self.mouse_release)
        self.left_mouse_press = False
        self.middle_mouse_press = False
        self.right_mouse_press = False

        # Internal data initialization
        self.complex_image_data = complex_image
        if overlay is None:
            ones = np.ones(complex_image.shape, dtype='bool')
            overlay = np.ma.masked_where(ones, ones)

        if isinstance(cursor_loc, list):
            cursor_loc = Coordinates(*cursor_loc)
        self.cursor_loc = self.clip_coordinates(cursor_loc)
        self.slice_num = slice_num

        # Initialize objects visualizing the internal data
        self.cmap = cmap if cmap is not None else mpl.cm.Greys_r
        self.overlayColormap = overlay_cmap if overlay_cmap is not None else mpl.cm.Reds

        if cursor_labels is None:
            cursor_labels = [{'color': 'r', 'textLabel': "X"},
                             {'color': 'b', 'textLabel': "Y"},
                             {'color': 'g', 'textLabel': "Z Slice"}]

        # image
        self.fig.patch.set_color(cursor_labels[2]['color'])
        self.axes = self.fig.add_axes([.1, .05, .8, .8])
        self.img = self.initialize_image(np.zeros(complex_image.shape),
                                         aspect=aspect,
                                         interpolation=interpolation,
                                         origin=origin,
                                         cmap=self.cmap)
        if overlay is not None:
            self.overlay = self.initialize_image(overlay,
                                                 aspect=aspect,
                                                 interpolation=interpolation,
                                                 origin=origin,
                                                 alpha=0.3,
                                                 cmap=self.overlayColormap)
        self.display_type = ImageDisplayType.mag
        self.set_mpl_img()
        self.title = self.axes.text(0.5,
                                    1.08,
                                    cursor_labels[2]['textLabel'],
                                    horizontalalignment='center',
                                    fontsize=18,
                                    transform=self.axes.transAxes)
        self.axes.xaxis.set_visible(False)
        self.axes.yaxis.set_visible(False)
        self.axes.patch.set_facecolor('black')
        # cursor lines
        self.hline = self.axes.axhline(y=cursor_loc.y,
                                       linewidth=1,
                                       color=cursor_labels[0]['color'])
        self.htxt = self.axes.text(-.5,
                                   cursor_loc.y,
                                   cursor_labels[0]['textLabel'],
                                   bbox={'facecolor': 'white', 'alpha': 0.7},
                                   va='center',
                                   ha='right')
        self.vline = self.axes.axvline(x=cursor_loc.x,
                                       linewidth=1,
                                       color=cursor_labels[1]['color'])
        self.vtxt = self.axes.text(cursor_loc.x, -.5,
                                   cursor_labels[1]['textLabel'],
                                   bbox={'facecolor': 'white', 'alpha': 0.7},
                                   va='top',
                                   ha='center')

        # Initialize parameters for data visualization
        # window level attributes need to be cleaned up
        self.intensity_level_cache = np.zeros(4)
        self.intensity_window_cache = np.ones(4)
        self.intensity_level = None
        self.intensity_window = None
        self.wl_orig_window = None
        self.wl_orig_level = None
        self.wl_orig_event_coord = None
        self.img_dynamic_range = None
        self.enable_window_level = True

        self.set_window_level_to_default()
        if display_type is None:
            self.show_display_type_change(ImageDisplayType.mag)
        else:
            self.show_display_type_change(display_type)

    def initialize_image(self, img, *args, **kwargs):
        # this class uses coordinates complex_image[x,y]
        # we would like x (first dimension) to be on horizontal axis
        # imshow visualizes matrices where first column is rows (vertical axis)
        # therefore, we must transpose the data
        return self.axes.imshow(img.T, *args, **kwargs)

    def get_image_value(self, coord):
        return self.img.get_array().data[coord.y, coord.x]

    def clip_coordinates(self, coord):
        coord.x = np.minimum(np.maximum(coord.x, 0), self.complex_image_data.shape[0] - 1)
        coord.y = np.minimum(np.maximum(coord.y, 0), self.complex_image_data.shape[1] - 1)
        return coord

    @property
    def cursor_val(self):
        return self.get_image_value(self.cursor_loc)

    def save(self, fname):
        vmin, vmax = self.img.get_clim()
        mpl.pyplot.imsave(fname=fname + '.png',
                          arr=self.img.get_array(),
                          cmap=self.img.get_cmap(),
                          origin=self.img.origin,
                          vmin=vmin,
                          vmax=vmax,
                          format="png")

    # Methods for mouse event slots
    def mouse_press(self, event):
        # with matplotlib event, button 1 is left, 2 is middle, 3 is right
        if self.fig.canvas.widgetlock.locked():
            return
        if event.button == 1:
            self.left_mouse_press = True
        elif event.button == 2:
            self.middle_mouse_press = True
            vmin, vmax = self.img.get_clim()
            mpl.pyplot.figure()
            popout_figure = mpl.pyplot.imshow(self.img.get_array(),
                                              cmap=self.img.get_cmap(),
                                              origin=self.img.origin,
                                              aspect=self.img.axes.get_aspect(),
                                              vmin=vmin,
                                              vmax=vmax,
                                              interpolation=self.img.get_interpolation())
            popout_figure.axes.xaxis.set_visible(False)
            popout_figure.axes.yaxis.set_visible(False)
            mpl.pyplot.show()

        elif event.button == 3:
            self.right_mouse_press = True
            self.wl_orig_window = self.intensity_window
            self.wl_orig_level = self.intensity_level
            self.wl_orig_event_coord = Coordinates(*[event.x, event.y])
        self.mouse_move(event)

    def mouse_release(self, event):
        if self.fig.canvas.widgetlock.locked():
            return
        if event.button == 1:
            self.left_mouse_press = False
        elif event.button == 2:
            self.middle_mouse_press = False
        elif event.button == 3:
            self.right_mouse_press = False

    def mouse_move(self, event):
        if self.fig.canvas.widgetlock.locked():
            return
        if self.right_mouse_press and self.enable_window_level:
            level_scale = 0.001
            window_scale = 0.001
            d_level = level_scale * float(self.wl_orig_event_coord.y - event.y) * self.img_dynamic_range
            d_window = window_scale * float(event.x - self.wl_orig_event_coord.x) * self.img_dynamic_range
            new_intensity_level = self.wl_orig_level + d_level
            new_intensity_window = self.wl_orig_window + d_window
            self.sig_window_level_change.emit(new_intensity_window, new_intensity_level)

        if self.left_mouse_press:
            data_coord = self.axes.transData.inverted().transform([event.x, event.y]) + 0.5
            clipped_location = self.clip_coordinates(Coordinates(*data_coord))
            self.emit_cursor_change(clipped_location)

    def emit_cursor_change(self, coord):
        self.sig_cursor_change.emit(coord.x, coord.y)

    # Methods that set internal data
    def set_complex_image(self, new_image):
        self.complex_image_data = new_image

    def set_overlay(self, new_overlay_data):
        # this class uses coordinates complex_image[x,y]
        # we would like x (first dimension) to be on horizontal axis
        # imshow visualizes matrices where first column is rows (vertical axis)
        # therefore, we must transpose the data
        self.overlay.set_data(new_overlay_data.T)

    def set_cursor_loc(self, new_loc):
        # clipping new_loc to valid locations is done in mouse_move() before the ChangeLocation signal is emitted
        # however, there could be problems if a control class objec signals a cursor_loc change that is out of bounds
        # new_loc = np.minimum(np.maximum(new_loc, [0,0]), np.subtract(self.complex_image_data.shape,1)).astype(np.int)
        new_loc = Coordinates(*new_loc)
        if self.cursor_loc != new_loc:
            self.cursor_loc = new_loc

    def set_slice_num(self, new_slice_num):
        self.slice_num = new_slice_num

    def set_display_type(self, display_type):
        self.display_type = display_type
        if display_type == ImageDisplayType.mag or display_type == ImageDisplayType.imag or display_type == ImageDisplayType.real:
            self.set_mpl_img_cmap(self.cmap)
            self.set_window_level(
                self.intensity_window_cache[display_type], self.intensity_level_cache[display_type])
            self.enable_window_level = True
        elif display_type == ImageDisplayType.phase:
            self.set_mpl_img_cmap(mpl.cm.hsv)
            self.set_window_level(2 * np.pi, 0)
            self.enable_window_level = False

    def set_window_level(self, new_window, new_level):
        if self.intensity_level != new_level or self.intensity_window != new_window:
            self.intensity_level = new_level
            self.intensity_window = max(new_window, 0)
            self.intensity_level_cache[self.display_type] = new_level
            self.intensity_window_cache[self.display_type] = new_window
            vmin = self.intensity_level - (self.intensity_window * 0.5)
            vmax = self.intensity_level + (self.intensity_window * 0.5)
            self.img.set_clim(vmin, vmax)

    def set_window_level_to_default(self):
        self.intensity_level_cache[ImageDisplayType.imag] = self.default_level(self.complex_image_data.imag)
        self.intensity_window_cache[ImageDisplayType.imag] = self.get_dynamic_range(self.complex_image_data.imag)

        self.intensity_level_cache[ImageDisplayType.real] = self.default_level(self.complex_image_data.real)
        self.intensity_window_cache[ImageDisplayType.real] = self.get_dynamic_range(self.complex_image_data.real)

        self.intensity_level_cache[ImageDisplayType.phase] = 0.0
        self.intensity_window_cache[ImageDisplayType.phase] = 2.0 * np.pi

        self.intensity_level_cache[ImageDisplayType.mag] = self.default_level(np.abs(self.complex_image_data))
        self.intensity_window_cache[ImageDisplayType.mag] = self.get_dynamic_range(np.abs(self.complex_image_data))

        self.set_window_level(self.intensity_window_cache[self.display_type],
                              self.intensity_level_cache[self.display_type])

    # Methods updating objects that visualize internal data
    def set_mpl_img_cmap(self, cmap):
        self.img.set_cmap(cmap)

    @staticmethod
    def get_dynamic_range(img):
        valid_values = img[np.logical_and(np.isfinite(img), np.abs(img).astype(bool))]
        if valid_values.size == 0:
            return 1

        # not very robust
        # dynamic_range = np.float(np.max(valid_values)) - np.float(np.min(valid_values))

        # remove outliers and use 3*stdv for dynamic range
        median = np.median(valid_values)
        stdv_prev = np.inf
        stdv = valid_values.std()
        max_iter = 25
        count=0

        while np.abs((stdv_prev-stdv)/stdv) > 0.1 and count < max_iter:
            valid_values = valid_values[np.abs(valid_values - median) < 3 * stdv]
            median = np.median(valid_values)
            stdv_prev = stdv
            stdv = valid_values.std()
            count+=1

        return 3 * stdv

    @staticmethod
    def default_level(img):
        valid_values = img[np.logical_and(np.isfinite(img), np.abs(img).astype(bool))]
        if valid_values.size == 0:
            return 0
        # default_level = valid_values.mean() # biased
        default_level = np.median(valid_values)
        return default_level


    def set_mpl_img(self):
        intensity_image = None
        if self.display_type == ImageDisplayType.mag:
            intensity_image = np.abs(self.complex_image_data)
        elif self.display_type == ImageDisplayType.phase:
            intensity_image = np.angle(self.complex_image_data)
        elif self.display_type == ImageDisplayType.real:
            intensity_image = np.real(self.complex_image_data)
        elif self.display_type == ImageDisplayType.imag:
            intensity_image = np.imag(self.complex_image_data)

        self.img_dynamic_range = self.get_dynamic_range(intensity_image)
        # this class uses coordinates complex_image[x,y]
        # we would like x (first dimension) to be on horizontal axis
        # imshow visualizes matrices where first column is rows (vertical axis)
        # therefore, we must transpose the data
        self.img.set_data(intensity_image.T)

    def set_mpl_lines(self):
        self.hline.set_ydata([self.cursor_loc.y, self.cursor_loc.y])
        self.vline.set_xdata([self.cursor_loc.x, self.cursor_loc.x])
        self.htxt.set_y(self.cursor_loc.y)
        self.vtxt.set_x(self.cursor_loc.x)

    def blit_image_and_lines(self):
        if self.fig._cachedRenderer is not None:
            self.fig.canvas.draw()
            self.blit(self.fig.bbox)
            return

    def blit_image_for_roi_drawing(self):
        # not using this function anymore, just always draw the entire canvas
        if self.fig._cachedRenderer is not None:
            self.fig.draw_artist(self.fig.patch)
            self.axes.draw_artist(self.title)
            self.axes.draw_artist(self.axes.patch)
            self.axes.draw_artist(self.img)
            z = self.sliceNum
            if z in self.NavigationToolbar.roiLines.mplLineObjects:
                for currentLine in self.NavigationToolbar.roiLines.mplLineObjects[z]:
                    self.axes.draw_artist(currentLine)
            self.blit(self.fig.bbox)

    # Convenience methods to change data and update visualizing objects
    def show_complex_image_change(self, new_complex_image):
        self.set_complex_image(new_complex_image)
        self.set_mpl_img()
        self.blit_image_and_lines()

    def show_complex_image_and_overlay_change(self, new_complex_image, new_overlay_data):
        self.set_complex_image(new_complex_image)
        self.set_overlay(new_overlay_data)
        self.set_mpl_img()
        self.blit_image_and_lines()

    def show_cursor_loc_change(self, new_cursor_loc):
        self.set_cursor_loc(new_cursor_loc)
        self.set_mpl_lines()
        self.blit_image_and_lines()

    def show_display_type_change(self, display_type):
        self.set_display_type(display_type)
        self.set_mpl_img()
        self.blit_image_and_lines()

    def show_cmap_change(self, cmap):
        self.set_mpl_img_cmap(cmap)
        self.blit_image_and_lines()

    def show_window_level_change(self, new_window, new_level):
        self.set_window_level(new_window, new_level)
        self.blit_image_and_lines()

    def show_set_window_level_to_default(self):
        self.set_window_level_to_default()
        self.blit_image_and_lines()

    def get_slice_num(self):
        return self.slice_num

    # Methods related to Qt
    def sizeHint(self):
        return QtCore.QSize(450, 450)
