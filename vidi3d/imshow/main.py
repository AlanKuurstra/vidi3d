"""
Sets up the main window for the 4D viewer. This includes creating MpImage4D, MpPlot,
ControlWidget4D.  Also connections are made between QT signals sent by other
classes and functions within this class.
"""

from PyQt5 import QtGui, QtCore, QtWidgets
from .. import core as _Core
from .. import definitions as dd
from . import image4d
from . import controls


class _MainWindow(QtWidgets.QMainWindow):
    def __init__(self, complexIm3, pixdim, interpolation='bicubic', initLocation=None, imageType=dd.ImageDisplayType.mag):
        super(_MainWindow, self).__init__()
        if initLocation is None:
            initLocation = [complexIm3.shape[0] / 2,
                            complexIm3.shape[1] / 2, complexIm3.shape[2] / 2, 0]
        initLocation = list(map(int, initLocation))
        self.setWindowTitle('Vidi3d: imshow')
        self.viewerNumber = 0
        self.imagePanel4D = image4d._MplImage4D(
            complexIm3, pixdim, interpolation, initLocation, imageType, parent=self)
        self.controls = controls._ControlWidget4D(
            complexIm3.shape, initLocation, imageType, parent=self)

        mprWidget = QtWidgets.QWidget()
        layoutmpr = QtWidgets.QGridLayout()
        layoutmpr.addWidget(self.controls, 1, 0)
        layoutmpr.addWidget(self.imagePanel4D.xsliceNav, 2, 0)
        layoutmpr.addWidget(self.imagePanel4D.xslice, 3, 0)
        layoutmpr.addWidget(self.imagePanel4D.ysliceNav, 0, 1)
        layoutmpr.addWidget(self.imagePanel4D.yslice, 1, 1)
        layoutmpr.addWidget(self.imagePanel4D.zsliceNav, 2, 1)
        layoutmpr.addWidget(self.imagePanel4D.zslice, 3, 1)
        mprWidget.setLayout(layoutmpr)

        plotsWidget = QtWidgets.QWidget()
        layoutplots = QtWidgets.QVBoxLayout()
        layoutplots.addWidget(self.imagePanel4D.xplot)
        layoutplots.addWidget(self.imagePanel4D.yplot)
        layoutplots.addWidget(self.imagePanel4D.zplot)
        layoutplots.addWidget(self.imagePanel4D.tplot)
        plotsWidget.setLayout(layoutplots)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(mprWidget)
        splitter.addWidget(plotsWidget)

        # used when inheriting from QMainWindow
        self.setCentralWidget(splitter)
        # self.statusBar().showMessage('Ready')

        self.makeConnections()

        self.show()
        self.setFocus()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def makeConnections(self):
        self.controls.sig_img_disp_type_change.connect(
            self.imagePanel4D.onImageTypeChange)
        """self.controls.signalImageCmapChanged.connect(self.imagePanel4D.CMapChanged)"""

        # when cursor moves, update lines
        self.imagePanel4D.zslice.sig_x_change.connect(
            self.imagePanel4D.onXChange)
        self.imagePanel4D.zslice.sig_y_change.connect(
            self.imagePanel4D.onYChange)
        self.imagePanel4D.zslice.sig_z_change.connect(
            self.imagePanel4D.onZChange)

        self.imagePanel4D.xslice.sig_x_change.connect(
            self.imagePanel4D.onXChange)
        self.imagePanel4D.xslice.sig_y_change.connect(
            self.imagePanel4D.onYChange)
        self.imagePanel4D.xslice.sig_z_change.connect(
            self.imagePanel4D.onZChange)

        self.imagePanel4D.yslice.sig_x_change.connect(
            self.imagePanel4D.onXChange)
        self.imagePanel4D.yslice.sig_y_change.connect(
            self.imagePanel4D.onYChange)
        self.imagePanel4D.yslice.sig_z_change.connect(
            self.imagePanel4D.onZChange)

        # when cursor moves, update controls
        self.imagePanel4D.xslice.sig_x_change.connect(
            self.controls.onXChange)
        self.imagePanel4D.xslice.sig_y_change.connect(
            self.controls.onYChange)
        self.imagePanel4D.xslice.sig_z_change.connect(
            self.controls.onZChange)

        self.imagePanel4D.yslice.sig_x_change.connect(
            self.controls.onXChange)
        self.imagePanel4D.yslice.sig_y_change.connect(
            self.controls.onYChange)
        self.imagePanel4D.yslice.sig_z_change.connect(
            self.controls.onZChange)

        self.imagePanel4D.zslice.sig_x_change.connect(
            self.controls.onXChange)
        self.imagePanel4D.zslice.sig_y_change.connect(
            self.controls.onYChange)
        self.imagePanel4D.zslice.sig_z_change.connect(
            self.controls.onZChange)

        # when right button pressed, update window/level of images
        self.imagePanel4D.xslice.sig_window_level_change.connect(
            self.imagePanel4D.onWindowLevelChange)
        self.imagePanel4D.yslice.sig_window_level_change.connect(
            self.imagePanel4D.onWindowLevelChange)
        self.imagePanel4D.zslice.sig_window_level_change.connect(
            self.imagePanel4D.onWindowLevelChange)

        # when right button pressed, update window/level controls
        self.imagePanel4D.xslice.sig_window_level_change.connect(
            self.controls.onWindowLevelChange)
        self.imagePanel4D.yslice.sig_window_level_change.connect(
            self.controls.onWindowLevelChange)
        self.imagePanel4D.zslice.sig_window_level_change.connect(
            self.controls.onWindowLevelChange)

        # when cursor_loc control changes, update lines
        self.controls.sig_x_change.connect(
            self.imagePanel4D.onXChange)
        self.controls.sig_y_change.connect(
            self.imagePanel4D.onYChange)
        self.controls.sig_z_change.connect(
            self.imagePanel4D.onZChange)
        self.controls.sig_t_change.connect(
            self.imagePanel4D.onTChange)
        # self.controls.signalTavgRadChange.connect(self.imagePanel4D.onTavgRadChange)

        # when window/level control changes, update images
        self.controls.sig_window_level_change.connect(
            self.imagePanel4D.onWindowLevelChange)

        # when window/level reset pressed, update images and control
        self.controls.sig_window_level_reset.connect(
            self.controls.onWindowLevelReset)
        self.controls.sig_window_level_reset.connect(
            self.imagePanel4D.onWindowLevelReset)

    def keyPressEvent(self, event):
        key = event.key()
        if key == 77:
            self.imagePanel4D.onImageTypeChange(dd.ImageDisplayType.mag)
            self.controls.onImageTypeChange(dd.ImageDisplayType.mag)
        elif key == 80:
            self.imagePanel4D.onImageTypeChange(dd.ImageDisplayType.phase)
            self.controls.onImageTypeChange(dd.ImageDisplayType.phase)
        elif key == 82:
            self.imagePanel4D.onImageTypeChange(dd.ImageDisplayType.real)
            self.controls.onImageTypeChange(dd.ImageDisplayType.real)
        elif key == 73:
            self.imagePanel4D.onImageTypeChange(dd.ImageDisplayType.imag)
            self.controls.onImageTypeChange(dd.ImageDisplayType.imag)
        event.ignore()

    def setViewerNumber(self, number):
        self.viewerNumber = number

    def closeEvent(self, event):
        if self.viewerNumber:
            del _Core._viewerList[self.viewerNumber]
