"""
Sets up the main window for the 4D viewer. This includes creating MpImage4D, MpPlot,
ControlWidget4D.  Also connections are made between QT signals sent by other
classes and functions within this class.
"""

from PyQt4 import QtGui, QtCore
from .. import _Core as _Core
from .. import _DisplayDefinitions as dd
from . import _MplImage4D
from . import _ControlWidget4D


class _MainWindow(QtGui.QMainWindow):
    def __init__(self, complexIm3, pixdim, interpolation='bicubic', initLocation=None, imageType=dd.ImageType.mag):
        _Core._create_qApp()
        super(_MainWindow, self).__init__()
        if initLocation is None:
            initLocation = [complexIm3.shape[0] / 2,
                            complexIm3.shape[1] / 2, complexIm3.shape[2] / 2, 0]

        self.setWindowTitle('Imshow Viewer')
        self.viewerNumber = 0
        self.imagePanel4D = _MplImage4D._MplImage4D(
            complexIm3, pixdim, interpolation, initLocation, imageType, parent=self)
        self.controls = _ControlWidget4D._ControlWidget4D(
            complexIm3.shape, initLocation, imageType, parent=self)

        mprWidget = QtGui.QWidget()
        layoutmpr = QtGui.QGridLayout()
        layoutmpr.addWidget(self.controls, 1, 0)
        layoutmpr.addWidget(self.imagePanel4D.xsliceNav, 2, 0)
        layoutmpr.addWidget(self.imagePanel4D.xslice, 3, 0)
        layoutmpr.addWidget(self.imagePanel4D.ysliceNav, 0, 1)
        layoutmpr.addWidget(self.imagePanel4D.yslice, 1, 1)
        layoutmpr.addWidget(self.imagePanel4D.zsliceNav, 2, 1)
        layoutmpr.addWidget(self.imagePanel4D.zslice, 3, 1)
        mprWidget.setLayout(layoutmpr)

        plotsWidget = QtGui.QWidget()
        layoutplots = QtGui.QVBoxLayout()
        layoutplots.addWidget(self.imagePanel4D.xplot)
        layoutplots.addWidget(self.imagePanel4D.yplot)
        layoutplots.addWidget(self.imagePanel4D.zplot)
        layoutplots.addWidget(self.imagePanel4D.tplot)
        plotsWidget.setLayout(layoutplots)

        splitter = QtGui.QSplitter()
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
        self.controls.signalImageTypeChange.connect(
            self.imagePanel4D.onImageTypeChange)
        """self.controls.signalImageCmapChanged.connect(self.imagePanel4D.CMapChanged)"""

        # when cursor moves, update lines
        self.imagePanel4D.zslice.signalXLocationChange.connect(
            self.imagePanel4D.onXChange)
        self.imagePanel4D.zslice.signalYLocationChange.connect(
            self.imagePanel4D.onYChange)
        self.imagePanel4D.zslice.signalZLocationChange.connect(
            self.imagePanel4D.onZChange)

        self.imagePanel4D.xslice.signalXLocationChange.connect(
            self.imagePanel4D.onXChange)
        self.imagePanel4D.xslice.signalYLocationChange.connect(
            self.imagePanel4D.onYChange)
        self.imagePanel4D.xslice.signalZLocationChange.connect(
            self.imagePanel4D.onZChange)

        self.imagePanel4D.yslice.signalXLocationChange.connect(
            self.imagePanel4D.onXChange)
        self.imagePanel4D.yslice.signalYLocationChange.connect(
            self.imagePanel4D.onYChange)
        self.imagePanel4D.yslice.signalZLocationChange.connect(
            self.imagePanel4D.onZChange)

        # when cursor moves, update controls
        self.imagePanel4D.xslice.signalXLocationChange.connect(
            self.controls.onXChange)
        self.imagePanel4D.xslice.signalYLocationChange.connect(
            self.controls.onYChange)
        self.imagePanel4D.xslice.signalZLocationChange.connect(
            self.controls.onZChange)

        self.imagePanel4D.yslice.signalXLocationChange.connect(
            self.controls.onXChange)
        self.imagePanel4D.yslice.signalYLocationChange.connect(
            self.controls.onYChange)
        self.imagePanel4D.yslice.signalZLocationChange.connect(
            self.controls.onZChange)

        self.imagePanel4D.zslice.signalXLocationChange.connect(
            self.controls.onXChange)
        self.imagePanel4D.zslice.signalYLocationChange.connect(
            self.controls.onYChange)
        self.imagePanel4D.zslice.signalZLocationChange.connect(
            self.controls.onZChange)

        # when right button pressed, update window/level of images
        self.imagePanel4D.xslice.signalWindowLevelChange.connect(
            self.imagePanel4D.onWindowLevelChange)
        self.imagePanel4D.yslice.signalWindowLevelChange.connect(
            self.imagePanel4D.onWindowLevelChange)
        self.imagePanel4D.zslice.signalWindowLevelChange.connect(
            self.imagePanel4D.onWindowLevelChange)

        # when right button pressed, update window/level controls
        self.imagePanel4D.xslice.signalWindowLevelChange.connect(
            self.controls.onWindowLevelChange)
        self.imagePanel4D.yslice.signalWindowLevelChange.connect(
            self.controls.onWindowLevelChange)
        self.imagePanel4D.zslice.signalWindowLevelChange.connect(
            self.controls.onWindowLevelChange)

        # when location control changes, update lines
        self.controls.signalXLocationChange.connect(
            self.imagePanel4D.onXChange)
        self.controls.signalYLocationChange.connect(
            self.imagePanel4D.onYChange)
        self.controls.signalZLocationChange.connect(
            self.imagePanel4D.onZChange)
        self.controls.signalTLocationChange.connect(
            self.imagePanel4D.onTChange)
        # self.controls.signalTavgRadChange.connect(self.imagePanel4D.onTavgRadChange)

        # when window/level control changes, update images
        self.controls.signalWindowLevelChange.connect(
            self.imagePanel4D.onWindowLevelChange)

        # when window/level reset pressed, update images and control
        self.controls.signalWindowLevelReset.connect(
            self.controls.onWindowLevelReset)
        self.controls.signalWindowLevelReset.connect(
            self.imagePanel4D.onWindowLevelReset)

    def keyPressEvent(self, event):
        key = event.key()
        if key == 77:
            self.imagePanel4D.onImageTypeChange(dd.ImageType.mag)
            self.controls.onImageTypeChange(dd.ImageType.mag)
        elif key == 80:
            self.imagePanel4D.onImageTypeChange(dd.ImageType.phase)
            self.controls.onImageTypeChange(dd.ImageType.phase)
        elif key == 82:
            self.imagePanel4D.onImageTypeChange(dd.ImageType.real)
            self.controls.onImageTypeChange(dd.ImageType.real)
        elif key == 73:
            self.imagePanel4D.onImageTypeChange(dd.ImageType.imag)
            self.controls.onImageTypeChange(dd.ImageType.imag)
        event.ignore()

    def setViewerNumber(self, number):
        self.viewerNumber = number

    def closeEvent(self, event):
        if self.viewerNumber:
            del _Core._viewerList[self.viewerNumber]
