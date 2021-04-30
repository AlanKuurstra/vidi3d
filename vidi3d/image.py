"""
Base class for images shown in the viewers. Instances of this clase are used 
to setup an arbitrary number of 2D images for comparison.  Instances of this
class are also used to show the 3 cross sectional views of a 3D image.
"""
import matplotlib as mpl
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from . import definitions as dd
from .signals import Signals
from .definitions import Coordinates


class MplImage(Signals, FigureCanvas):
    def __init__(self,
                 complex_image,
                 aspect='equal',
                 overlay=None,
                 parent=None,
                 interpolation='none',
                 origin='lower',
                 display_type=None,
                 window_level=None,
                 location=None,
                 imgSliceNumber=0,
                 locationLabels=None,
                 cmap=None,
                 overlay_cmap=None):
        self.fig = mpl.figure.Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        # can't set parent in FigureCanvas __init__, set it manually
        #self.parent = parent


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
            self.overlay_data = np.ma.masked_where(ones, ones)
        else:
            self.overlay_data = overlay
        self.cursor_loc = Coordinates(*np.minimum(np.maximum(location, [0, 0]), np.subtract(self.complex_image_data.shape, 1)))
        self.imgSliceNumber = imgSliceNumber

        # Initialize objects visualizing the internal data
        if cmap is None:
            self.colormap = mpl.cm.Greys_r
        else:
            self.colormap = cmap

        if overlay_cmap is None:
            self.overlayColormap = mpl.cm.Reds
        else:
            self.overlayColormap = overlay_cmap

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


        self.img = self.initialize_image(np.zeros(complex_image.shape), aspect=aspect,interpolation=interpolation, origin=origin, cmap=self.colormap)
        if overlay is not None:
            self.overlay = self.axes.imshow(self.overlayData.T, aspect=aspect,
                                            interpolation=interpolation, origin=origin, alpha=0.3,
                                            cmap=self.overlayColormap)
        self._imageType = dd.ImageDisplayType.mag
        self.setMplImg()
        self.cursor_val = self.get_image_value(self.cursor_loc)
        self.title = self.axes.text(
            0.5, 1.08, currLabels[2]['textLabel'], horizontalalignment='center', fontsize=18,
            transform=self.axes.transAxes)
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


        # Initialize parameters for data visualization
        self.intensityLevelCache = np.zeros(4)
        self.intensityWindowCache = np.ones(4)
        self.intensityLevel = 0.0
        self.intensityWindow = 1.0
        self._imageType = dd.ImageDisplayType.mag
        self.enableWindowLevel = True

        self.setWindowLevelToDefault()
        if display_type is None:
            self.showImageTypeChange(dd.ImageDisplayType.mag)
        else:
            self.showImageTypeChange(display_type)

    def initialize_image(self, X, *args, **kwargs):
        # this class uses coordinates complex_image[x,y]
        # we would like x (first dimension) to be on horizontal axis
        # imshow visualizes matrices where first column is rows (vertical axis)
        # therefore, we must transpose the data
        return self.axes.imshow(X.T, *args, **kwargs)

    def get_image_value(self, coordinates):
        return self.img.get_array().data[coordinates.y, coordinates.x]


    def save(self, fname):
        img = self.img.get_array()
        cmap = self.img.get_cmap()
        origin = self.img.origin
        vmin, vmax = self.img.get_clim()
        mpl.pyplot.imsave(fname=fname + '.png', arr=img, cmap=cmap, origin=origin, vmin=vmin, vmax=vmax, format="png")

    # Methods for mouse event slots
    def mouse_press(self, event):
        # with matplotlib event, button 1 is left, 2 is middle, 3 is right
        if self.fig.canvas.widgetlock.locked():
            return
        if event.button == 1:
            self.left_mouse_press = True
        elif event.button == 2:
            self.middle_mouse_press = True
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
            self.right_mouse_press = True

        self.origIntensityWindow = self.intensityWindow
        self.origIntensityLevel = self.intensityLevel
        self.origPointerLocation = [event.x, event.y]
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
        if (self.right_mouse_press and self.enableWindowLevel):
            # """
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

        if (self.left_mouse_press):
            locationDataCoord = self.axes.transData.inverted().transform([event.x, event.y])
            clippedLocation = np.minimum(np.maximum(locationDataCoord + 0.5, [0, 0]), np.subtract(self.complex_image_data.shape, 1))
            self.emit_cursor_change(clippedLocation)

    def emit_cursor_change(self, location):
        self.signalLocationChange.emit(location[0], location[1])


    # Methods that set internal data
    def set_complex_image(self, new_image):
        self.complex_image_data = new_image

    def set_overlay(self, new_overlay):
        self.overlayData = new_overlay
        self.overlay.set_data(self.overlayData.T)

    def set_cursor_loc(self, new_loc):
        # clipping new_loc to valid locations is done in mouse_move() before the ChangeLocation signal is emitted
        # however, there could be problems if a control class objec signals a cursor_loc change that is out of bounds
        # new_loc = np.minimum(np.maximum(new_loc, [0,0]), np.subtract(self.complex_image_data.shape,1)).astype(np.int)
        new_loc = Coordinates(*new_loc)
        if self.cursor_loc != new_loc:
            self.cursor_loc = new_loc
            self.cursor_val = self.get_image_value(self.cursor_loc)

    def setImgSliceNumber(self, newImgSliceNumber):
        self.imgSliceNumber = newImgSliceNumber

    def setImageType(self, imageType):
        self._imageType = imageType
        if imageType == dd.ImageDisplayType.mag or imageType == dd.ImageDisplayType.imag or imageType == dd.ImageDisplayType.real:
            self.setMplImgColorMap(self.colormap)
            self.setWindowLevel(
                self.intensityWindowCache[imageType], self.intensityLevelCache[imageType])
            self.enableWindowLevel = True
        elif imageType == dd.ImageDisplayType.phase:
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
        maxMag = np.max(np.abs(self.complex_image_data))

        self.intensityLevelCache[dd.ImageDisplayType.imag] = 0.0
        self.intensityWindowCache[dd.ImageDisplayType.imag] = 2.0 * maxMag

        self.intensityLevelCache[dd.ImageDisplayType.real] = 0.0
        self.intensityWindowCache[dd.ImageDisplayType.real] = 2.0 * maxMag

        self.intensityLevelCache[dd.ImageDisplayType.phase] = 0.0
        self.intensityWindowCache[dd.ImageDisplayType.phase] = 2.0 * np.pi

        self.intensityLevelCache[dd.ImageDisplayType.mag] = maxMag * 0.5
        self.intensityWindowCache[dd.ImageDisplayType.mag] = maxMag

        self.setWindowLevel(
            self.intensityWindowCache[self._imageType], self.intensityLevelCache[self._imageType])

    # ==================================================================
    # functions that update objects visualizing internal data
    # ==================================================================
    def setMplImgColorMap(self, cmap):
        self.img.set_cmap(cmap)

    def setMplImg(self):
        if self._imageType == dd.ImageDisplayType.mag:
            intensityImage = np.abs(self.complex_image_data)
        elif self._imageType == dd.ImageDisplayType.phase:
            intensityImage = np.angle(self.complex_image_data)
        elif self._imageType == dd.ImageDisplayType.real:
            intensityImage = np.real(self.complex_image_data)
        elif self._imageType == dd.ImageDisplayType.imag:
            intensityImage = np.imag(self.complex_image_data)

        self.dynamicRange = np.float(np.max(intensityImage)) - np.float(np.min(intensityImage))
        self.img.set_data(intensityImage.T)
        # reason for transpose:
        # matplotlib shows 10x20 matrix with height of 10 and width of 20
        # but in our matrix the 10 refers to width and the 20 to height

    def setMplLines(self):
        self.hline.set_ydata([self.cursor_loc.y, self.cursor_loc.y])
        self.vline.set_xdata([self.cursor_loc.x, self.cursor_loc.x])
        self.htxt.set_y(self.cursor_loc.y)
        self.vtxt.set_x(self.cursor_loc.x)

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

    # ==================================================================
    # convenience functions to change data and update visualizing objects
    # ==================================================================
    def showComplexImageChange(self, newComplexImage):
        self.set_complex_image(newComplexImage)
        self.setMplImg()
        self.BlitImageAndLines()

    def showComplexImageAndOverlayChange(self, newComplexImage, newOverlayImage):
        self.set_complex_image(newComplexImage)
        self.set_overlay(newOverlayImage)
        self.setMplImg()
        self.BlitImageAndLines()

    def showLocationChange(self, newLocation):
        self.set_cursor_loc(newLocation)
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

    # ==================================================================
    # functions related to Qt
    # ==================================================================
    def sizeHint(self):
        return QtCore.QSize(450, 450)
