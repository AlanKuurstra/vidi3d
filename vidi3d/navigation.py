"""
Base class for MplImage's toolbar. Includes Home, Zoom, Pan, Save from matplotlib.
Implemented buttons for movie playing and ROI drawing.  Movie and ROI send signals
so that the MainWindow can implement logic for movie playing and ROI drawing
"""

import os

import matplotlib.transforms as transforms
from PyQt5 import QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.lines import Line2D

from .definitions import roi_color
from .signals import Signals


class NavigationToolbarSimple(NavigationToolbar2QT):
    def __init__(self, canvas, parent):
        super(NavigationToolbarSimple, self).__init__(canvas, parent)
        self.clear()
        tmp = self.addAction(self._icon('home.png'), 'Home', self.home)
        tmp.setToolTip('Reset original view')
        tmp = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
        tmp.setToolTip('Zoom to rectangle')
        tmp = self.addAction(self._icon('move.png'), 'Pan', self.pan)
        tmp.setToolTip('Pan axes with left mouse, zoom with right')

        w = QtWidgets.QWidget()
        w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.spacer = self.addWidget(w)

        # In order for save to work, need to copy and paste self.save_figure to
        # overload and change the qt_compat._getSaveFileName call to have parameter:
        # options=QtWidgets.QFileDialog.DontUseNativeDialog
        # https://stackoverflow.com/questions/59775385/weird-interaction-between-pycharm-and-pyqt-qfiledialog
        # However, this action isn't very useful.
        # self.addSeparator()
        # tmp = self.addAction(self._icon('filesave.png'), 'Save', self.save_figure)
        # tmp.setToolTip('Save the figure')


class NavigationToolbar(Signals, NavigationToolbarSimple):
    def __init__(self, canvas, parent, img_index=None):
        super(NavigationToolbar, self).__init__(canvas, parent)
        self.roi_widget = QtWidgets.QAction(
            QtGui.QIcon(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "icons", "lasso.png"))), 'ROI')
        self.roi_widget.triggered.connect(self.roi)
        self.insertAction(self.spacer, self.roi_widget)
        self.roi_widget.setToolTip('Select an ROI for analysis')
        self.roi_widget.setCheckable(True)
        self.roi_active = False
        self._id_roi_press = None
        self._id_roi_release = None
        self._id_roi_move = None
        self.roi_lines = LassoLines()
        self.roi_drawing_engaged = False

        self.movie_widget = QtWidgets.QAction(
            QtGui.QIcon(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "icons", "movie.png"))), 'Movie')
        self.movie_widget.triggered.connect(self.play_movie)
        self.insertAction(self.spacer, self.movie_widget)
        self.movie_widget.setToolTip('Play movie of timeseries')
        self.movie_widget.setCheckable(True)
        self._movie_active = False
        self.ax = self.canvas.axes
        self.img_index = img_index

    def roi(self, *args):
        if self.roi_active == True:
            self.roi_active = False
            self.roi_destructor()
        else:
            self.roi_active = True
            self.roi_initialize()

    def roi_initialize(self):
        self._id_roi_press = self.canvas.mpl_connect('button_press_event', self.roi_press)
        self._id_roi_release = self.canvas.mpl_connect('motion_notify_event', self.roi_move)
        self._id_roi_move = self.canvas.mpl_connect('button_release_event', self.roi_release)
        self.roi_widget.setChecked(True)

        z = self.canvas.cursor_loc.z
        if z in self.roi_lines.mpl_line_objects:
            for currentLine in self.roi_lines.mpl_line_objects[z]:
                self.ax.add_line(currentLine)

        self.canvas.axes.lines.remove(self.canvas.vline)
        self.canvas.axes.lines.remove(self.canvas.hline)
        self.canvas.axes.texts.remove(self.canvas.htxt)
        self.canvas.axes.texts.remove(self.canvas.vtxt)

        self.canvas.blit_image_and_lines()
        self.sig_roi_init.emit(self.img_index)

    def roi_destructor(self):
        # use holders different from _idPress because Move and Pan will steal the reference
        self._id_roi_press = self.canvas.mpl_disconnect(self._id_roi_press)
        self._id_roi_release = self.canvas.mpl_disconnect(self._id_roi_release)
        self._id_roi_move = self.canvas.mpl_disconnect(self._id_roi_move)
        self.roi_widget.setChecked(False)

        self.ax.lines.append(self.canvas.hline)
        self.ax.lines.append(self.canvas.vline)
        self.ax.texts.append(self.canvas.htxt)
        self.ax.texts.append(self.canvas.vtxt)

        z = self.canvas.cursor_loc.z
        if z in self.roi_lines.mpl_line_objects:
            for currentLine in self.roi_lines.mpl_line_objects[z]:
                self.ax.lines.remove(currentLine)

        self.canvas.blit_image_and_lines()
        self.signal_roi_destruct.emit(self.img_index)

    def roi_release(self, event):
        if self.mode != '' or self.roi_active == False or not self.roi_drawing_engaged:
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
        if self.mode != '' or self.roi_active == False:
            return
        if event.button != 1:
            if self.roi_drawing_engaged:
                self.sig_roi_cancel.emit()
                self.roi_drawing_engaged = False
            return
        self.sig_roi_start.emit(event.xdata, event.ydata)
        self.roi_drawing_engaged = True

    def roi_move(self, event):
        if self.mode != '' or self.roi_active == False or not self.roi_drawing_engaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            return
        self.sig_roi_change.emit(event.xdata, event.ydata)

    def play_movie(self):
        self._movie_active = not self._movie_active
        if self._movie_active:
            if self.roi_active:
                self.roi()
            self.roi_widget.setDisabled(True)

            self.canvas.axes.texts.remove(self.canvas.htxt)
            self.canvas.axes.texts.remove(self.canvas.vtxt)
            self.canvas.axes.lines.remove(self.canvas.hline)
            self.canvas.axes.lines.remove(self.canvas.vline)

            axesTransform = self.canvas.img.axes.transAxes
            axesOffset = transforms.ScaledTranslation(0, .6, self.canvas.img.axes.figure.dpi_scale_trans)
            self.movieText = self.canvas.img.axes.text(1, -.01, '', fontsize=10, transform=axesTransform, ha='right',
                                                       va='top')

            self.canvas.blit_image_and_lines()
            self.sig_movie_init.emit(self.img_index)

        else:

            self.movieText.remove()
            del self.movieText

            self.canvas.axes.texts.append(self.canvas.htxt)
            self.canvas.axes.texts.append(self.canvas.vtxt)
            self.canvas.axes.lines.append(self.canvas.hline)
            self.canvas.axes.lines.append(self.canvas.vline)

            self.canvas.draw()
            self.canvas.blit(self.canvas.fig.bbox)
            self.roi_widget.setEnabled(True)
            self.sig_movie_destruct.emit(self.img_index)


class LassoLines:
    def __init__(self):
        self.mpl_line_objects = {}

    def start_new_lasso_line(self, x, y, z):
        self.mpl_line_objects.setdefault(z, []).append(Line2D([x], [y], linestyle='-', color=roi_color, lw=1))
