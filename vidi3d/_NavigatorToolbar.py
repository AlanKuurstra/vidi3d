try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2QTAgg
import os
from matplotlib.lines import Line2D
from matplotlib import animation
import matplotlib.pyplot as plt
from PyQt4 import QtCore
import _DisplayDefinitions as dd
import numpy as np
from ._MplAnimation import _MplAnimation
import matplotlib.transforms as transforms


class NavigationToolbar(NavigationToolbar2QTAgg):
    from ._DisplaySignals import *

    def __init__(self, canvas, parent, imgIndex):
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
        # commented lines are still under development
        #a = self.addAction(self.__file__('zoom_to_rect.png'), 'Select', self.selectROI)
        #a.setToolTip('Under development.')
        self.ROIwidget = self.addAction(self._icon(os.path.join(
            os.path.dirname(__file__), "icons/lasso.png")), 'Select', self.roi)
        self.ROIwidget.setToolTip('Select an ROI for analysis')
        self.ROIwidget.setCheckable(True)
        self._ROIactive = False
        self._idROIPress = None
        self._idROIRelease = None
        self._idROIMove = None
        self.roiLines = lassoLines()
        self.roiDrawingEngaged = False

        self.movieWidget = self.addAction(self._icon(os.path.join(
            os.path.dirname(__file__), "icons/movie.png")), 'Select', self.playMovie)
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

        z = self.parent.parent.getCurrentSlice()
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.add_line(currentLine)

        """
        self.parent.vline.remove()
        self.parent.hline.remove()
        self.parent.htxt.remove()
        self.parent.vtxt.remove()
        #"""

        # self.parent.vline.set_visible(False)
        # self.parent.hline.set_visible(False)
        # self.parent.htxt.set_visible(False)
        # self.parent.vtxt.set_visible(False)

        #"""
        self.parent.axes.lines.remove(self.parent.vline)
        self.parent.axes.lines.remove(self.parent.hline)
        self.parent.axes.texts.remove(self.parent.htxt)
        self.parent.axes.texts.remove(self.parent.vtxt)
        #"""

        self.parent.BlitImageAndLines()

        self.signalROIInit.emit(self.imgIndex)

    def roi_destructor(self):
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

        # self.parent.vline.set_visible(True)
        # self.parent.hline.set_visible(True)
        # self.parent.htxt.set_visible(True)
        # self.parent.vtxt.set_visible(True)

        #"""
        self.ax.lines.append(self.parent.hline)
        self.ax.lines.append(self.parent.vline)
        self.ax.texts.append(self.parent.htxt)
        self.ax.texts.append(self.parent.vtxt)
        #"""

        z = self.parent.parent.getCurrentSlice()
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
            # self.parent.signalLocationChange.disconnect(self.parent.parent.ChangeLocation)
            # self.parent.signalWindowLevelChange.disconnect(self.parent.parent.ChangeWindowLevel)
            # self.parent.signalZLocationChange.disconnect(self.parent.parent.onZChange)

            # this stops window leveling
            # self.parent.mpl_disconnect(self.parent._idMove)
            # self.parent.mpl_disconnect(self.parent._idPress)
            # self.parent.mpl_disconnect(self.parent._idRelease)

            # self.oldAxImages=self.parent.img.axes.images
            # self.oldAxLines=self.parent.img.axes.lines
            # self.oldAxTexts=self.parent.img.axes.texts

            # self.parent.axes.images=[]
            # self.parent.axes.lines=[]
            # self.parent.axes.texts=[]

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

            # self.parent.signalZLocationChange.disconnect(self.parent.parent.onZChange)
            # #specific to viewer

            """
            #left mouse
            #scroll mouse
            #don't allow ROI drawing
            z=self.parent.parent.loc[2] #specific to viewer
            print "apply data type"
            complexData = self.parent.parent.complexImList[self.imgIndex][:,:,z,:]#specific to viewer
            imgType=self.parent._imageType
            if imgType == dd.ImageType.mag:
                movieArray = np.abs(complexData)
            elif imgType == dd.ImageType.phase:
                movieArray = np.angle(complexData)
            elif imgType == dd.ImageType.real:
                movieArray = np.real(complexData)
            elif imgType == dd.ImageType.imag:
                movieArray = np.imag(complexData)
            print "done"
            
            
            aspect=self.parent.img.axes.get_aspect()
            interpolation=self.parent.img.get_interpolation()
            origin = self.parent.img.origin
            colormap=self.parent.img.get_cmap()
            vmin,vmax=self.parent.img.get_clim()        
            interval=100 #ms
            blit=True 
            
            self.animationObject=_MplAnimation(movieArray, aspect=aspect, parent=self,\
                          interpolation=interpolation, origin =origin,\
                          colormap=colormap, vmin=vmin, vmax=vmax,\
                          interval=interval, blit=blit, figure=self.parent.fig)
            """

        else:
            """
            self.animationObject.event_source.stop()

            for axesimageList in self.animationObject.imshowList:                
                for axesimage in axesimageList:
                    axesimage.remove()
            del self.animationObject
            """

            # self.parent.axes.images=self.oldAxImages
            # self.parent.axes.lines=self.oldAxLines
            # self.parent.axes.texts=self.oldAxTexts

            self.movieText.remove()
            del self.movieText

            self.parent.axes.texts.append(self.parent.htxt)
            self.parent.axes.texts.append(self.parent.vtxt)
            self.parent.axes.lines.append(self.parent.hline)
            self.parent.axes.lines.append(self.parent.vline)

            self.parent.draw()
            self.parent.blit(self.parent.fig.bbox)
            self.ROIwidget.setEnabled(True)
            # this stopped window leveling
            # self.parent._idMove=self.parent.mpl_connect('motion_notify_event',self.parent.MoveEvent)
            # self.parent._idPress=self.parent.mpl_connect('button_press_event',self.parent.PressEvent)
            # self.parent._idRelease=self.parent.mpl_connect('button_release_event',self.parent.ReleaseEvent)
            self.signalMovieDestruct.emit(self.imgIndex)

            # self.parent.signalZLocationChange.connect(self.parent.parent.onZChange)# specific to viewer
            # self.parent.signalLocationChange.connect(self.parent.parent.ChangeLocation)


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


if __name__ == "__main__":

    from pyview.Viewers import compare3d

    directory = '/cfmm/data/akuurstr/data/Prado/ignore_knockout_mice/BOLD/registerFlash2D_BOLD_60/all/'
    imgloc = directory + 's_20160412_02' + '_flashBold60MC1_to_common.nii.gz'

    import nibabel as nib

    imgobj = nib.load(imgloc)
    pxlsz = imgobj.get_header()['pixdim'][1:5]

    img = imgobj.get_data().transpose(1, 2, 0, 3)
    pxlsz = pxlsz[[1, 2, 0, 3]]

    directory = '/cfmm/data/akuurstr/data/Prado/ignore_knockout_mice/BOLD/registerFlash2D_BOLD_60/all/'
    imgloc = directory + 's_20160412_01' + '_flashBold60MC1_to_common.nii.gz'
    img2 = nib.load(imgloc).get_data().transpose(1, 2, 0, 3)
    directory = '/cfmm/data/akuurstr/data/Prado/ignore_knockout_mice/BOLD/registerFlash2D_BOLD_60/all/'
    imgloc = directory + 's_20160412_03' + '_flashBold60MC1_to_common.nii.gz'
    img3 = nib.load(imgloc).get_data().transpose(1, 2, 0, 3)
    compare3d((img, img2, img3), pixdim=pxlsz, block=False)
