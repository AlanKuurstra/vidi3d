"""
Base class for MplImage's toolbar. Includes Home, Zoom, Pan, Save from matplotlib.
Implemented buttons for movie playing and ROI drawing.  Movie and ROI send signals
so that the MainWindow can implement logic for movie playing and ROI drawing
"""

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbarSuper
import os
from matplotlib.lines import Line2D
from . import definitions as dd
import matplotlib.transforms as transforms
from .signals import Signals
from PyQt5 import QtWidgets

class NavigationToolbarSimple(NavigationToolbarSuper):
    def __init__(self, canvas, parent):
        super(NavigationToolbarSimple, self).__init__(canvas, parent)
        self.clear()
        a = self.addAction(self._icon('home.png'), 'Home', self.home)
        a.setToolTip('Reset original view')
        a = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
        a.setToolTip('Zoom to rectangle')
        a = self.addAction(self._icon('move.png'), 'Pan', self.pan)
        a.setToolTip('Pan axes with left mouse, zoom with right')

        w = QtWidgets.QWidget()
        w.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.spacer = self.addWidget(w)

        # In order for save to work, need to copy and paste self.save_figure to
        # overload and change the qt_compat._getSaveFileName call to have parameter:
        # options=QtWidgets.QFileDialog.DontUseNativeDialog
        # https://stackoverflow.com/questions/59775385/weird-interaction-between-pycharm-and-pyqt-qfiledialog
        # However, this action isn't very useful.
        # self.addSeparator()
        # a = self.addAction(self._icon('filesave.png'), 'Save',
        #                    self.save_figure)
        # a.setToolTip('Save the figure')

from PyQt5 import QtCore, QtGui
from matplotlib.backends.backend_qt5agg import _setDevicePixelRatio
from matplotlib.backends.qt_compat import _devicePixelRatioF

class NavigationToolbar(Signals, NavigationToolbarSimple):
    def __init__(self, canvas, parent, imgIndex=None):
        super(NavigationToolbar, self).__init__(canvas, parent)
        self.ROIwidget = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "icons","lasso.png"))),
                                           'ROI')
        self.ROIwidget.triggered.connect(self.roi)
        self.insertAction(self.spacer, self.ROIwidget)
        self.ROIwidget.setToolTip('Select an ROI for analysis')
        self.ROIwidget.setCheckable(True)
        self._ROIactive = False
        self._idROIPress = None
        self._idROIRelease = None
        self._idROIMove = None
        self.roiLines = lassoLines()
        self.roiDrawingEngaged = False

        self.movieWidget = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "icons","movie.png"))),
                                           'Movie')
        self.movieWidget.triggered.connect(self.playMovie)
        self.insertAction(self.spacer, self.movieWidget)
        self.movieWidget.setToolTip('Play movie of timeseries')
        self.movieWidget.setCheckable(True)
        self._movieActive = False
        self.ax = self.canvas.axes
        self.imgIndex = imgIndex

    def roi(self, *args):
        if self._ROIactive == True:
            self._ROIactive = False
            self.roi_destructor()
        else:
            self._ROIactive = True
            self.roi_initialize()

    def roi_initialize(self):
        self._idROIPress = self.canvas.mpl_connect(
            'button_press_event', self.roi_press)
        self._idROIRelease = self.canvas.mpl_connect(
            'motion_notify_event', self.roi_move)
        self._idROIMove = self.canvas.mpl_connect(
            'button_release_event', self.roi_release)
        self.ROIwidget.setChecked(True)

        z = self.canvas.get_slice_num()
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.add_line(currentLine)

        self.canvas.axes.lines.remove(self.canvas.vline)
        self.canvas.axes.lines.remove(self.canvas.hline)
        self.canvas.axes.texts.remove(self.canvas.htxt)
        self.canvas.axes.texts.remove(self.canvas.vtxt)

        self.canvas.blit_image_and_lines()
        self.sig_roi_init.emit(self.imgIndex)

    def roi_destructor(self):
        # use holders different from _idPress because Move and Pan will steal
        # the reference
        self._idROIPress = self.canvas.mpl_disconnect(self._idROIPress)
        self._idROIRelease = self.canvas.mpl_disconnect(self._idROIRelease)
        self._idROIMove = self.canvas.mpl_disconnect(self._idROIMove)
        self.ROIwidget.setChecked(False)

        self.ax.lines.append(self.canvas.hline)
        self.ax.lines.append(self.canvas.vline)
        self.ax.texts.append(self.canvas.htxt)
        self.ax.texts.append(self.canvas.vtxt)

        z = self.canvas.get_slice_num()
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.lines.remove(currentLine)

        self.canvas.blit_image_and_lines()
        self.signal_roi_destruct.emit(self.imgIndex)

    def roi_release(self, event):

        if self.mode != '' or self._ROIactive == False or not self.roiDrawingEngaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            if self.roiDrawingEngaged:
                self.sig_roi_cancel.emit()
                self.roiDrawingEngaged = False
            return
        self.sig_roi_end.emit(event.xdata, event.ydata)
        self.roiDrawingEngaged = False

    def roi_press(self, event):

        if self.mode != '' or self._ROIactive == False:
            return
        if event.button != 1:
            if self.roiDrawingEngaged:
                self.sig_roi_cancel.emit()
                self.roiDrawingEngaged = False
            return
        self.sig_roi_start.emit(event.xdata, event.ydata)
        self.roiDrawingEngaged = True

    def roi_move(self, event):
        if self.mode != '' or self._ROIactive == False or not self.roiDrawingEngaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            return
        self.sig_roi_change.emit(event.xdata, event.ydata)

    def playMovie(self):
        self._movieActive = not self._movieActive
        if self._movieActive:
            if self._ROIactive:
                self.roi()
            self.ROIwidget.setDisabled(True)

            self.canvas.axes.texts.remove(self.canvas.htxt)
            self.canvas.axes.texts.remove(self.canvas.vtxt)
            self.canvas.axes.lines.remove(self.canvas.hline)
            self.canvas.axes.lines.remove(self.canvas.vline)

            axesTransform = self.canvas.img.axes.transAxes
            axesOffset = transforms.ScaledTranslation(
                0, .6, self.canvas.img.axes.figure.dpi_scale_trans)
            self.movieText = self.canvas.img.axes.text(
                1, -.01, '', fontsize=10, transform=axesTransform, ha='right', va='top')

            self.canvas.blit_image_and_lines()
            self.sig_movie_init.emit(self.imgIndex)

        else:

            self.movieText.remove()
            del self.movieText

            self.canvas.axes.texts.append(self.canvas.htxt)
            self.canvas.axes.texts.append(self.canvas.vtxt)
            self.canvas.axes.lines.append(self.canvas.hline)
            self.canvas.axes.lines.append(self.canvas.vline)

            self.canvas.draw()
            self.canvas.blit(self.canvas.fig.bbox)
            self.ROIwidget.setEnabled(True)
            self.sig_movie_destruct.emit(self.imgIndex)


class lassoLines():
    def __init__(self):
        self.mplLineObjects = {}

    def startNewLassoLine(self, x, y, z):
        if z in self.mplLineObjects:
            self.mplLineObjects[z].append(
                Line2D([x], [y], linestyle='-', color=dd.roi_color, lw=1))
        else:
            self.mplLineObjects[z] = [
                Line2D([x], [y], linestyle='-', color=dd.roi_color, lw=1), ]
