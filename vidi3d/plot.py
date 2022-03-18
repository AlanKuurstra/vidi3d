"""
Base class for plots shown in the viewers. Instances of this class are used
to show the plot along MpImage cursor lines.
"""
import matplotlib as mpl
import numpy as np
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

from .definitions import ImageDisplayType, PlotColours
from .helpers import apply_display_type


class MplPlot(FigureCanvas):
    def __init__(self,
                 complex_data,
                 display_type=None,
                 init_marker=None,
                 colors=None,
                 title=None):
        # Qt related initialization
        self.fig = mpl.figure.Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setMinimumSize(200, 200)
        FigureCanvas.updateGeometry(self)

        # Event related initialization
        self.mpl_connect('button_press_event', self.press_event)

        # Internal data initialization
        self.set_complex_data(complex_data)
        if display_type is None:
            self.set_display_type(ImageDisplayType.mag)
        else:
            self.set_display_type(display_type)
        self.set_marker_posn(init_marker)

        # Initialize objects visualizing the internal data
        self.colors = colors
        if self.colors is None:
            self.colors = PlotColours.colours
        # 1d plot
        self.axes = self.fig.add_subplot(111)
        if title is not None:
            self.axes.set_title(title)
        # disable plot autoscale
        self.lockPlot = False
        # zoom functionality
        self.toolbar = NavigationToolbar2QT(self, self)
        self.toolbar.hide()
        self.toolbar.zoom()
        # initialize lines and markers
        self.create_lines()
        self.create_markers()

    # todo: slot naming convention?
    # Methods for mouse event slots
    def press_event(self, event):
        # with matplotlib event, button 1 is left, 2 is middle, 3 is right
        if event.button == 2:
            self.toolbar.home()

    # Methods that set internal data
    def set_complex_data(self, new_complex_data):
        self.complex_data = new_complex_data

    def set_display_type(self, display_type):
        self.display_type = display_type

    def set_marker_posn(self, new_marker_posn):
        self.marker_posn = np.minimum(np.maximum(new_marker_posn, 0), self.complex_data[0].shape[0] - 1)

    # Methods updating objects that visualize internal data
    def set_lines(self):
        for indx in range(len(self.complex_data)):
            self.lines[indx][0].set_ydata(apply_display_type(self.complex_data[indx], self.display_type))
        if not self.lockPlot:
            self.axes.relim()
            # self.axes.set_ylim(auto=True)
            # self.axes.autoscale_view(scalex=False)
            self.axes.autoscale(axis='y')

    def set_markers(self):
        if self.marker_posn is not None:
            for plot_num in range(len(self.complex_data)):
                self.markers[plot_num][0].set_data(self.marker_posn, apply_display_type(
                    self.complex_data[plot_num][self.marker_posn], self.display_type))

    def create_lines(self):
        self.lines = []
        for indx in range(len(self.complex_data)):
            self.lines.append(
                self.axes.plot(apply_display_type(self.complex_data[indx], self.display_type), self.colors[indx]))
        self.axes.set_xlim(0, self.complex_data[0].shape[0] - 1 + np.finfo('float').eps)

    def create_markers(self):
        if self.marker_posn is not None:
            self.markers = []
            for plot_num in range(len(self.complex_data)):
                self.markers.append(self.axes.plot(self.marker_posn, apply_display_type(
                    self.complex_data[plot_num][self.marker_posn], self.display_type), 'kx'))

    def draw_lines_and_markers(self):
        self.draw()

    # Convenience methods
    def show_data_type_change(self, index):
        self.set_display_type(index)
        # set_markers() must occur before set_lines()
        # set_lines contains the autoscaling of the axes and the if the marker
        # is not set before the autoscaling, then it will scale to old data
        self.set_markers()
        self.set_lines()
        self.draw_lines_and_markers()

    def show_complex_data_change(self, new_complex_data):
        self.set_complex_data(new_complex_data)
        self.set_lines()
        self.set_markers()
        self.draw_lines_and_markers()

    def show_complex_data_and_markers_change(self, new_complex_data, new_marker_posn):
        self.set_complex_data(new_complex_data)
        self.set_marker_posn(new_marker_posn)
        self.set_lines()
        self.set_markers()
        self.draw_lines_and_markers()

    # Methods related to Qt
    def sizeHint(self):
        return QtCore.QSize(300, 183)
