"""
Base class for images shown in the viewers. Instances of this clase are used 
to setup an arbitrary number of 2D images for comparison.  Instances of this
class are also used to show the 3 cross sectional views of a 3D image.
"""
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtGui, QtWidgets
from . import _Core
from . import _DisplayDefinitions as dd
from ._DisplaySignals import SignalsObject

class _MplImage(SignalsObject,FigureCanvas):
    def __init__(self, complexImage, aspect='equal', overlay=None, parent=None, interpolation='none', origin='lower', imageType=None, windowLevel=None, location=None, imgSliceNumber=0, locationLabels=None, colormap=None, overlayColormap=None):
        #
        # Qt related initialization
        #
        _Core._create_qApp()
        self.fig = mpl.figure.Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # the FigureCanvas class doesn't have the option to pass the parent to
        # the __init__() constructer, must set it manually
        self.parent = parent
        #
        # Event related initialization
        #
        self._idMove = self.mpl_connect('motion_notify_event', self.MoveEvent)
        self._idPress = self.mpl_connect('button_press_event', self.PressEvent)
        self._idRelease = self.mpl_connect(
            'button_release_event', self.ReleaseEvent)
        self.leftMousePress = False
        self.middleMousePress = False
        self.rightMousePress = False
        #
        # Internal data initialization
        #
        self.complexImageData = complexImage
        if overlay is None:
            ones = np.ones(complexImage.shape, dtype='bool')
            self.overlayData = np.ma.masked_where(ones, ones)
        else:
            self.overlayData = overlay
        self.location = np.minimum(np.maximum(location, [0, 0]), np.subtract(
            self.complexImageData.shape, 1)).astype(np.int)
        self.imgSliceNumber = imgSliceNumber

        #
        # Initialize objects visualizing the internal data
        #
        if colormap is None:
            self.colormap = mpl.cm.Greys_r
        else:
            self.colormap = colormap

        if overlayColormap is None:
            self.overlayColormap = mpl.cm.Reds
        else:
            self.overlayColormap = overlayColormap

        # labels
        currLabels = [{'color': 'r', 'textLabel': "X"},
                      {'color': 'b', 'textLabel': "Y"},
                      {'color': 'g', 'textLabel': "Z Slice"}]
        if locationLabels is not None:
            currLabels = locationLabels
        # image
        self.fig.patch.set_color(currLabels[2]['color'])
        self.axes = self.fig.add_axes([.1, .05, .8, .8])
        if origin != 'upper' and origin != 'lower':
            print("origin parameter not understood, defaulting to 'lower'")
            origin = 'lower'
        self.img = self.axes.imshow(np.zeros(complexImage.shape).T, aspect=aspect,
                                    interpolation=interpolation, origin=origin, cmap=self.colormap)
        if overlay is not None:
            self.overlay = self.axes.imshow(self.overlayData.T, aspect=aspect,
                                        interpolation=interpolation, origin=origin, alpha=0.3, cmap=self.overlayColormap)
        self._imageType = dd.ImageType.mag
        self.setMplImg()
        self.locationVal = self.img.get_array(
        ).data[self.location[1], self.location[0]]
        self.title = self.axes.text(
            0.5, 1.08, currLabels[2]['textLabel'], horizontalalignment='center', fontsize=18, transform=self.axes.transAxes)
        self.axes.xaxis.set_visible(False)
        self.axes.yaxis.set_visible(False)
        self.axes.patch.set_facecolor('black')
        # cursor lines
        self.hline = self.axes.axhline(
            y=location[1], linewidth=1, color=currLabels[0]['color'])
        self.htxt = self.axes.text(-.5, location[1], currLabels[0]['textLabel'], bbox=dict(
            facecolor='white', alpha=0.7), va='center', ha='right')
        self.vline = self.axes.axvline(
            x=location[0], linewidth=1, color=currLabels[1]['color'])
        self.vtxt = self.axes.text(location[0], -.5, currLabels[1]['textLabel'], bbox=dict(
            facecolor='white', alpha=0.7), va='top', ha='center')

        #
        # Initialize parameters for data visualization
        #
        self.intensityLevelCache = np.zeros(4)
        self.intensityWindowCache = np.ones(4)
        self.intensityLevel = 0.0
        self.intensityWindow = 1.0
        self._imageType = dd.ImageType.mag
        self.enableWindowLevel = True

        self.setWindowLevelToDefault()
        if imageType is None:
            self.showImageTypeChange(dd.ImageType.mag)
        else:
            self.showImageTypeChange(imageType)

    def SaveImage(self, fname):
        img = self.img.get_array()
        cmap = cmap = self.img.get_cmap()
        origin = self.img.origin
        vmin, vmax = self.img.get_clim()

        mpl.pyplot.imsave(fname=fname + '.png', arr=img, cmap=cmap,
                          origin=origin, vmin=vmin, vmax=vmax, format="png")

    #==================================================================
    # slots to deal with mpl mouse events
    #==================================================================
    def PressEvent(self, event):
        # with matplotlib event, button 1 is left, 2 is middle, 3 is right
        if self.fig.canvas.widgetlock.locked():
            return
        if event.button == 1:
            self.leftMousePress = True
        elif event.button == 2:
            self.middleMousePress = True
            img = self.img.get_array()
            cmap = self.img.get_cmap()
            origin = self.img.origin
            vmin, vmax = self.img.get_clim()
            interpolation = self.img.get_interpolation()
            aspect = self.img.axes.get_aspect()
            mpl.pyplot.figure()
            popOutPlot = mpl.pyplot.imshow(
                img, cmap=cmap, origin=origin, vmin=vmin, vmax=vmax, interpolation=interpolation)
            popOutPlot.axes.set_aspect(aspect)
            popOutPlot.axes.xaxis.set_visible(False)
            popOutPlot.axes.yaxis.set_visible(False)
            mpl.pyplot.show()

        elif event.button == 3:
            self.rightMousePress = True

        self.origIntensityWindow = self.intensityWindow
        self.origIntensityLevel = self.intensityLevel
        self.origPointerLocation = [event.x, event.y]
        self.MoveEvent(event)

    def ReleaseEvent(self, event):
        if self.fig.canvas.widgetlock.locked():
            return
        if event.button == 1:
            self.leftMousePress = False
        elif event.button == 2:
            self.middleMousePress = False
        elif event.button == 3:
            self.rightMousePress = False

    def MoveEvent(self, event):
        if self.fig.canvas.widgetlock.locked():
            return
        if (self.rightMousePress and self.enableWindowLevel):
            #"""
            levelScale = 0.001
            windowScale = 0.001

            dLevel = levelScale * \
                float(self.origPointerLocation[1] -
                      event.y) * self.dynamicRange
            dWindow = windowScale * \
                float(
                    event.x - self.origPointerLocation[0]) * self.dynamicRange

            newIntensityLevel = self.origIntensityLevel + dLevel
            newIntensityWindow = self.origIntensityWindow + dWindow
            self.signalWindowLevelChange.emit(
                newIntensityWindow, newIntensityLevel)

        if (self.leftMousePress):
            locationDataCoord = self.axes.transData.inverted().transform([
                event.x, event.y])
            clippedLocation = np.minimum(np.maximum(
                locationDataCoord + 0.5, [0, 0]), np.subtract(self.complexImageData.shape, 1))
            self._signalCursorChange(clippedLocation)

    def _signalCursorChange(self, location):
        self.signalLocationChange.emit(location[0], location[1])

    #==================================================================
    # functions that set internal data
    #==================================================================
    def setComplexImage(self, newComplexImage):
        self.complexImageData = newComplexImage

    def setOverlayImage(self, newOverlayImage):
        self.overlayData = newOverlayImage
        self.overlay.set_data(self.overlayData.T)

    def setLocation(self, newLocation):
        # clipping newLocation to valid locations is done in MoveEvent() before the ChangeLocation signal is emitted
        # however, there could be problems if a control class objec signals a location change that is out of bounds
        #newLocation = np.minimum(np.maximum(newLocation, [0,0]), np.subtract(self.complexImageData.shape,1)).astype(np.int)
        if (int(self.location[0]) != newLocation[0]) or (int(self.location[1]) != newLocation[1]):
            self.location = newLocation
            self.locationVal = self.img.get_array(
            ).data[self.location[1], self.location[0]]

    def setImgSliceNumber(self, newImgSliceNumber):
        self.imgSliceNumber = newImgSliceNumber

    def setImageType(self, imageType):
        self._imageType = imageType
        if imageType == dd.ImageType.mag or imageType == dd.ImageType.imag or imageType == dd.ImageType.real:
            self.setMplImgColorMap(self.colormap)
            self.setWindowLevel(
                self.intensityWindowCache[imageType], self.intensityLevelCache[imageType])
            self.enableWindowLevel = True
        elif imageType == dd.ImageType.phase:
            self.setMplImgColorMap(mpl.cm.hsv)
            self.setWindowLevel(2 * np.pi, 0)
            self.enableWindowLevel = False

    def setWindowLevel(self, newIntensityWindow, newIntensityLevel):
        if self.intensityLevel != newIntensityLevel or self.intensityWindow != newIntensityWindow:
            self.intensityLevel = newIntensityLevel
            self.intensityWindow = max(newIntensityWindow, 0)
            self.intensityLevelCache[self._imageType] = newIntensityLevel
            self.intensityWindowCache[self._imageType] = newIntensityWindow
            vmin = self.intensityLevel - (self.intensityWindow * 0.5)
            vmax = self.intensityLevel + (self.intensityWindow * 0.5)
            self.img.set_clim(vmin, vmax)

    def setWindowLevelToDefault(self):
        maxMag = np.max(np.abs(self.complexImageData))

        self.intensityLevelCache[dd.ImageType.imag] = 0.0
        self.intensityWindowCache[dd.ImageType.imag] = 2.0 * maxMag

        self.intensityLevelCache[dd.ImageType.real] = 0.0
        self.intensityWindowCache[dd.ImageType.real] = 2.0 * maxMag

        self.intensityLevelCache[dd.ImageType.phase] = 0.0
        self.intensityWindowCache[dd.ImageType.phase] = 2.0 * np.pi

        self.intensityLevelCache[dd.ImageType.mag] = maxMag * 0.5
        self.intensityWindowCache[dd.ImageType.mag] = maxMag

        self.setWindowLevel(
            self.intensityWindowCache[self._imageType], self.intensityLevelCache[self._imageType])

    #==================================================================
    # functions that update objects visualizing internal data
    #==================================================================
    def setMplImgColorMap(self, cmap):
        self.img.set_cmap(cmap)

    def setMplImg(self):
        if self._imageType == dd.ImageType.mag:
            intensityImage = np.abs(self.complexImageData)
        elif self._imageType == dd.ImageType.phase:
            intensityImage = np.angle(self.complexImageData)
        elif self._imageType == dd.ImageType.real:
            intensityImage = np.real(self.complexImageData)
        elif self._imageType == dd.ImageType.imag:
            intensityImage = np.imag(self.complexImageData)

        self.dynamicRange = np.float(np.max(intensityImage)) - np.float(np.min(intensityImage))
        self.img.set_data(intensityImage.T)
        # reason for transpose:
        # matplotlib shows 10x20 matrix with height of 10 and width of 20
        # but in our matrix the 10 refers to width and the 20 to height

    def setMplLines(self):
        self.hline.set_ydata([self.location[1], self.location[1]])
        self.vline.set_xdata([self.location[0], self.location[0]])
        self.htxt.set_y(self.location[1])
        self.vtxt.set_x(self.location[0])

    def BlitImageAndLines(self):
        if self.fig._cachedRenderer is not None:
            self.fig.canvas.draw()
            self.blit(self.fig.bbox)
            return
            """    
            if self.NavigationToolbar._ROIactive:                
                self.BlitImageForROIDrawing()
                return
            self.fig.draw_artist(self.fig.patch)
            self.axes.draw_artist(self.title)
            self.axes.draw_artist(self.axes.patch)
            self.axes.draw_artist(self.img)
            self.axes.draw_artist(self.hline)
            self.axes.draw_artist(self.vline) 
            self.axes.draw_artist(self.htxt)
            self.axes.draw_artist(self.vtxt)
            #blit the entire figure instead of axes
            #so when x,y labels are outside axes,they also get repainted
            #self.blit(self.axes.bbox)
            self.blit(self.fig.bbox)
            #"""

    def BlitImageForROIDrawing(self):
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

    #==================================================================
    # convenience functions to change data and update visualizing objects
    #==================================================================
    def showComplexImageChange(self, newComplexImage):
        self.setComplexImage(newComplexImage)
        self.setMplImg()
        self.BlitImageAndLines()

    def showComplexImageAndOverlayChange(self, newComplexImage, newOverlayImage):
        self.setComplexImage(newComplexImage)
        self.setOverlayImage(newOverlayImage)
        self.setMplImg()
        self.BlitImageAndLines()

    def showLocationChange(self, newLocation):
        self.setLocation(newLocation)
        self.setMplLines()
        self.BlitImageAndLines()

    def showImageTypeChange(self, imageType):
        self.setImageType(imageType)
        self.setMplImg()
        self.BlitImageAndLines()

    def showColorMapChange(self, cmap):
        self.setMplImgColorMap(cmap)
        self.BlitImageAndLines()

    def showWindowLevelChange(self, newIntensityWindow, newIntensityLevel):
        self.setWindowLevel(newIntensityWindow, newIntensityLevel)
        self.BlitImageAndLines()

    def showSetWindowLevelToDefault(self):
        self.setWindowLevelToDefault()
        self.BlitImageAndLines()

    def getImgSliceNumber(self):
        return self.imgSliceNumber

    #==================================================================
    # functions related to Qt
    #==================================================================
    def sizeHint(self):
        return QtCore.QSize(450, 450)
