"""
Class to show movies of an fmri slice. Currently unused.
"""
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtGui
import core
from matplotlib.animation import ArtistAnimation
from signals import Signals


class _MplAnimation(Signals, FigureCanvas, ArtistAnimation):

    def __init__(self, movieArray, figure=None, aspect='equal', parent=None, interpolation='none', origin='lower', colormap=None, vmin=None, vmax=None, interval=50, blit=True):
        #
        # Qt related initialization
        #
        core.create_qapp()
        self.parent = parent

        if figure is not None:
            self.fig = figure

            self.axes = self.fig.add_axes([.1, .05, .8, .8])
            self.axes.xaxis.set_visible(False)
            self.axes.yaxis.set_visible(False)
            self.axes.patch.set_facecolor('black')
        else:
            self.fig = mpl.figure.Figure()
            FigureCanvas.__init__(self, self.fig)
            FigureCanvas.setSizePolicy(
                self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            FigureCanvas.updateGeometry(self)
            self.axes = self.fig.add_axes([.1, .05, .8, .8])
            if origin != 'upper' and origin != 'lower':
                print("origin parameter not understood, defaulting to 'lower'")
                origin = 'lower'
            #self.title=self.axes.text(0.5, 1.08, currLabels[2]['textLabel'],horizontalalignment='center',fontsize=18,transform = self.axes.transAxes)
            self.axes.xaxis.set_visible(False)
            self.axes.yaxis.set_visible(False)
            self.axes.patch.set_facecolor('black')

        self.imshowList = []
        for i in range(movieArray.shape[-1]):
            frame = self.axes.imshow(movieArray[..., i].T, aspect=aspect, interpolation=interpolation,
                                     origin=origin, cmap=colormap, vmin=vmin, vmax=vmax, animated=True)
            self.imshowList.append([frame])

        ArtistAnimation.__init__(self, self.fig, self.imshowList,
                                 interval=interval, blit=blit, repeat=True, repeat_delay=0)
        self.fig.canvas.draw()  # gets rid of the clipping in the background

    #==================================================================
    # functions related to Qt
    #==================================================================
    def sizeHint(self):
        return QtCore.QSize(450, 450)
