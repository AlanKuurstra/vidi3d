"""
Base class for MplImage's toolbar. Includes Home, Zoom, Pan, Save from matplotlib.
Implemented buttons for movie playing and ROI drawing.  Movie and ROI send signals
so that the MainWindow can implement logic for movie playing and ROI drawing
"""

try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2QTAgg
import os
from matplotlib.lines import Line2D
import _DisplayDefinitions as dd
import matplotlib.transforms as transforms

class NavigationToolbar(NavigationToolbar2QTAgg):
    from ._DisplaySignals import *
    def __init__(self, canvas, parent, imgIndex=0):
        super(NavigationToolbar, self).__init__(canvas, parent)
        self.clear()
        self.parent = parent
        self.canvas = canvas
        self.ax = parent.axes
        self.imgIndex = imgIndex
        self._idMove = None
        a = self.addAction(self._icon('home.png'), 'Home', self.home)
        a.setToolTip('Reset original view')
        a = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
        a.setToolTip('Zoom to rectangle')
        a = self.addAction(self._icon('move.png'), 'Pan', self.pan)
        a.setToolTip('Pan axes with left mouse, zoom with right')
        
        self.ROIwidget = self.addAction(self._icon(os.path.join(
            os.path.dirname(__file__), "icons/lasso.png")), 'ROI', self.roi)
        self.ROIwidget.setToolTip('Select an ROI for analysis')
        self.ROIwidget.setCheckable(True)
        self._ROIactive = False
        self._idROIPress = None
        self._idROIRelease = None
        self._idROIMove = None
        self.roiLines = lassoLines()
        self.roiDrawingEngaged = False

        self.movieWidget = self.addAction(self._icon(os.path.join(
            os.path.dirname(__file__), "icons/movie.png")), 'Movie', self.playMovie)
        self.movieWidget.setToolTip('Play movie of timeseries')
        self.movieWidget.setCheckable(True)
        self._movieActive = False

        self.addSeparator()
        a = self.addAction(self._icon('filesave.png'), 'Save',
                           self.save_figure)
        a.setToolTip('Save the figure')

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

        z = self.parent.getImgSliceNumber()
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.add_line(currentLine)

        """
        self.parent.vline.remove()
        self.parent.hline.remove()
        self.parent.htxt.remove()
        self.parent.vtxt.remove()
        #"""        
        """
        self.parent.vline.set_visible(False)
        self.parent.hline.set_visible(False)
        self.parent.htxt.set_visible(False)
        self.parent.vtxt.set_visible(False)
        #"""
        #"""
        self.parent.axes.lines.remove(self.parent.vline)
        self.parent.axes.lines.remove(self.parent.hline)
        self.parent.axes.texts.remove(self.parent.htxt)
        self.parent.axes.texts.remove(self.parent.vtxt)
        #"""
        
        self.parent.BlitImageAndLines()
        self.signalROIInit.emit(self.imgIndex)

    def roi_destructor(self):
        #use holders different from _idPress because Move and Pan will steal
        #the reference
        self._idROIPress = self.canvas.mpl_disconnect(self._idROIPress)
        self._idROIRelease = self.canvas.mpl_disconnect(self._idROIRelease)
        self._idROIMove = self.canvas.mpl_disconnect(self._idROIMove)
        self.ROIwidget.setChecked(False)

        """
        self.ax.add_line(self.parent.hline)
        self.ax.add_line(self.parent.vline)        
        self.ax.add_artist(self.parent.htxt)
        self.ax.add_artist(self.parent.vtxt)
        #"""
        """
        self.parent.vline.set_visible(True)
        self.parent.hline.set_visible(True)
        self.parent.htxt.set_visible(True)
        self.parent.vtxt.set_visible(True)
        #"""
        #"""
        self.ax.lines.append(self.parent.hline)
        self.ax.lines.append(self.parent.vline)
        self.ax.texts.append(self.parent.htxt)
        self.ax.texts.append(self.parent.vtxt)
        #"""

        z = self.parent.getImgSliceNumber()
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.lines.remove(currentLine)

        self.parent.BlitImageAndLines()
        self.signalROIDestruct.emit(self.imgIndex)

    def roi_release(self, event):

        if self.mode != '' or self._ROIactive == False or not self.roiDrawingEngaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            if self.roiDrawingEngaged:
                self.signalROICancel.emit()
                self.roiDrawingEngaged = False
            return
        self.signalROIEnd.emit(event.xdata, event.ydata)
        self.roiDrawingEngaged = False

    def roi_press(self, event):

        if self.mode != '' or self._ROIactive == False:
            return
        if event.button != 1:
            if self.roiDrawingEngaged:
                self.signalROICancel.emit()
                self.roiDrawingEngaged = False
            return
        self.signalROIStart.emit(event.xdata, event.ydata)
        self.roiDrawingEngaged = True

    def roi_move(self, event):
        if self.mode != '' or self._ROIactive == False or not self.roiDrawingEngaged:
            return
        if event.button != 1:
            return
        if event.inaxes != self.ax:
            return
        self.signalROIChange.emit(event.xdata, event.ydata)

    def playMovie(self):
        self._movieActive = not self._movieActive
        if self._movieActive:
            if self._ROIactive:
                self.roi()
            self.ROIwidget.setDisabled(True)
            
            self.parent.axes.texts.remove(self.parent.htxt)
            self.parent.axes.texts.remove(self.parent.vtxt)
            self.parent.axes.lines.remove(self.parent.hline)
            self.parent.axes.lines.remove(self.parent.vline)

            axesTransform = self.parent.img.axes.transAxes
            axesOffset = transforms.ScaledTranslation(
                0, .6, self.parent.img.axes.figure.dpi_scale_trans)
            self.movieText = self.parent.img.axes.text(
                0.5, 1, '', fontsize=15, transform=axesTransform + axesOffset, ha='center')
            self.parent.BlitImageAndLines()
            self.signalMovieInit.emit(self.imgIndex)

        else:
            
            self.movieText.remove()
            del self.movieText

            self.parent.axes.texts.append(self.parent.htxt)
            self.parent.axes.texts.append(self.parent.vtxt)
            self.parent.axes.lines.append(self.parent.hline)
            self.parent.axes.lines.append(self.parent.vline)

            self.parent.draw()
            self.parent.blit(self.parent.fig.bbox)
            self.ROIwidget.setEnabled(True)            
            self.signalMovieDestruct.emit(self.imgIndex)

class lassoLines():
    def __init__(self):
        self.mplLineObjects = {}

    def startNewLassoLine(self, x, y, z):
        if z in self.mplLineObjects:
            self.mplLineObjects[z].append(
                Line2D([x], [y], linestyle='-', color=dd.roiColor, lw=1))
        else:
            self.mplLineObjects[z] = [
                Line2D([x], [y], linestyle='-', color=dd.roiColor, lw=1), ]
