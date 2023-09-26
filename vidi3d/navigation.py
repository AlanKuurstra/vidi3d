"""
Base class for MplImage's toolbar. Includes Home, Zoom, Pan, Save from matplotlib.
Implemented buttons for movie playing and ROI drawing.  Movie and ROI send signals
so that the MainWindow can implement logic for movie playing and ROI drawing
"""

import os
# import matplotlib.transforms as transforms
from enum import Enum

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.lines import Line2D

from .definitions import roi_color
from .signals import Signals


class NavigationToolbarSimple(NavigationToolbar2QT):
    toolitems = [item for item in NavigationToolbar2QT.toolitems if item[0] in ['Home', 'Pan', 'Zoom']]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clear()

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                   text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan', 'roi', 'play_movie']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        # w = QtWidgets.QWidget()
        # w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.spacer = self.addWidget(w)


# extend matplotlib.backend_bases._Mode
class _Mode(str, Enum):
    NONE = ""
    PAN = "pan/zoom"
    ZOOM = "zoom rect"
    ROI = 'roi'
    MOVIE = 'movie'

    def __str__(self):
        return self.value

    @property
    def _navigate_mode(self):
        return self.name if self is not _Mode.NONE else None


class NavigationToolbar(Signals, NavigationToolbarSimple):
    # text, tooltip_text, image_file, callback
    toolitems = NavigationToolbarSimple.toolitems + [('Roi',
                                                      'Select an ROI for analysis',
                                                      os.path.join(os.path.dirname(__file__), "icons", "lasso"),
                                                      'roi'),
                                                     ('Movie',
                                                      'Play movie of timeseries',
                                                      os.path.join(os.path.dirname(__file__), "icons", "movie"),
                                                      'play_movie'
                                                      )
                                                     ]

    def __init__(self, canvas, parent, img_index=None):
        super(NavigationToolbar, self).__init__(canvas, parent)

        self.roi_lines = LassoLines()
        self.roi_drawing_engaged = False

        self.ax = self.canvas.axes
        self.img_index = img_index

        self.mode = _Mode.NONE

    def _update_buttons_checked(self):
        super()._update_buttons_checked()
        # sync button checkstates to match active mode
        if 'roi' in self._actions:
            self._actions['roi'].setChecked(self.mode.name == 'ROI')
        if 'play_movie' in self._actions:
            self._actions['play_movie'].setChecked(self.mode.name == 'MOVIE')

    def deactivate_current_mode(self):
        if self.mode.name == 'ROI':
            self.roi_deactivate()
        if self.mode.name == 'MOVIE':
            self.movie_deactivate()

    def clear_axes(self):
        self.canvas.htxt.set_visible(False)
        self.canvas.vtxt.set_visible(False)
        self.canvas.hline.set_visible(False)
        self.canvas.vline.set_visible(False)

    def populate_axes(self):
        self.canvas.htxt.set_visible(True)
        self.canvas.vtxt.set_visible(True)
        self.canvas.hline.set_visible(True)
        self.canvas.vline.set_visible(True)

    def initialize_default(self):
        self.populate_axes()
        self.canvas.blit_image_and_lines()

    def zoom(self, *args):
        self.deactivate_current_mode()
        # intialize and draw
        super().zoom(*args)
        self.initialize_default()

    def pan(self, *args):
        self.deactivate_current_mode()
        # intialize and draw
        super().pan(*args)
        self.initialize_default()

    def roi(self, *args):
        self.deactivate_current_mode()
        if self.mode.name == 'ROI':
            self.mode = _Mode.NONE
            self.initialize_default()
        else:
            self.mode = _Mode.ROI
            self.roi_initialize()

    def roi_initialize(self):
        # intialize and draw
        self._id_roi_press = self.canvas.mpl_connect('button_press_event', self.roi_press)
        self._id_roi_release = self.canvas.mpl_connect('motion_notify_event', self.roi_move)
        self._id_roi_move = self.canvas.mpl_connect('button_release_event', self.roi_release)
        self._update_buttons_checked()

        self.clear_axes()

        z = self.canvas.cursor_loc.z
        if z in self.roi_lines.mpl_line_objects:
            for currentLine in self.roi_lines.mpl_line_objects[z]:
                currentLine.set_visible(True)

        self.canvas.blit_image_and_lines()

        self.sig_roi_init.emit(self.img_index)

    def roi_deactivate(self):
        # use holders different from _idPress because Move and Pan will steal the reference
        self._id_roi_press = self.canvas.mpl_disconnect(self._id_roi_press)
        self._id_roi_release = self.canvas.mpl_disconnect(self._id_roi_release)
        self._id_roi_move = self.canvas.mpl_disconnect(self._id_roi_move)

        z = self.canvas.cursor_loc.z
        if z in self.roi_lines.mpl_line_objects:
            for currentLine in self.roi_lines.mpl_line_objects[z]:
                currentLine.set_visible(False)

        self.signal_roi_destruct.emit(self.img_index)

    def roi_release(self, event):
        if self.mode.name != 'ROI' or not self.roi_drawing_engaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            if self.roi_drawing_engaged:
                self.sig_roi_cancel.emit()
                self.roi_drawing_engaged = False
            return
        self.sig_roi_end.emit(event.xdata, event.ydata)
        self.roi_drawing_engaged = False

    def roi_press(self, event):
        if self.mode.name != 'ROI':
            return
        if event.button != 1:
            if self.roi_drawing_engaged:
                self.sig_roi_cancel.emit()
                self.roi_drawing_engaged = False
            return
        self.sig_roi_start.emit(event.xdata, event.ydata)
        self.roi_drawing_engaged = True

    def roi_move(self, event):
        if self.mode.name != 'ROI' or not self.roi_drawing_engaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            return
        self.sig_roi_change.emit(event.xdata, event.ydata)

    def movie_deactivate(self):
        self.movieText.remove()
        del self.movieText
        # self.canvas.draw()
        # self.canvas.blit(self.canvas.fig.bbox)
        self.sig_movie_destruct.emit(self.img_index)

    def play_movie(self):
        self.deactivate_current_mode()
        if self.mode.name == 'MOVIE':
            self.mode = _Mode.NONE
            self.initialize_default()
        else:
            self.mode = _Mode.MOVIE
            self._update_buttons_checked()

            # intialize and draw
            self.clear_axes()
            axesTransform = self.canvas.img.axes.transAxes
            # axesOffset = transforms.ScaledTranslation(0, .6, self.canvas.img.axes.figure.dpi_scale_trans)
            self.movieText = self.canvas.img.axes.text(1, -.01, '', fontsize=10, transform=axesTransform, ha='right',
                                                       va='top')
            self.canvas.blit_image_and_lines()
            self.sig_movie_init.emit(self.img_index)


class LassoLines:
    def __init__(self):
        self.mpl_line_objects = {}

    def start_new_lasso_line(self, x, y, z):
        self.mpl_line_objects.setdefault(z, []).append(Line2D([x], [y], linestyle='-', color=roi_color, lw=1))
