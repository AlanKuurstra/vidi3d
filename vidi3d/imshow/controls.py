"""
This class contains the widgets for user control in the 4D viewer.
"""
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from .. import core as _Core
from ..signals import Signals

class _ControlWidget4D(Signals,QtWidgets.QWidget):
    def __init__(self, image4DShape, initLocation, imageType, parent=None):
        super(_ControlWidget4D, self).__init__()
        self.image4DShape = image4DShape
        controlLayout = QtWidgets.QVBoxLayout(self)

        #
        # Image Type
        #
        imTypeLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("Image Type")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.imgType = QtWidgets.QComboBox()
        # the order of these have to match DisplayDefinitions class...consider changing that class to a dictionary
        # to use here
        self.imgType.addItem("Real")
        self.imgType.addItem("Imaginary")
        self.imgType.addItem("Magnitude")
        self.imgType.addItem("Phase")
        self.imgType.setCurrentIndex(imageType)

        self.imgType.currentIndexChanged.connect(self.changeImageType)
        imTypeLayout.addWidget(label)
        imTypeLayout.addWidget(self.imgType)

        #
        # Window/Level
        #
        self.wlLayout = QtWidgets.QHBoxLayout()
        self.window = QtWidgets.QDoubleSpinBox()
        self.window.setMaximumWidth(70)
        self.window.setDecimals(3)
        self.window.setMaximum(1.7 * 10**308)
        self.window.valueChanged.connect(self.changeWindow)
        self.level = QtWidgets.QDoubleSpinBox()
        self.level.setMaximumWidth(70)
        self.level.setDecimals(3)
        self.level.setMaximum(1.7 * 10**308)
        self.level.setMinimum(-1.7 * 10**308)
        self.level.setValue(np.floor(self.window.value() / 2))
        self.level.valueChanged.connect(self.changeLevel)
        label = QtWidgets.QLabel()
        label.setText("Window")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.wlLayout.addWidget(label)
        self.wlLayout.addWidget(self.window)
        label = QtWidgets.QLabel()
        label.setText("Level")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.wlLayout.addWidget(label)
        self.wlLayout.addWidget(self.level)
        button = QtWidgets.QPushButton("Default")
        button.clicked.connect(self.reset_wl)
        self.wlLayout.addWidget(button)

        #
        # Coordinates
        #
        locLayout = QtWidgets.QHBoxLayout()
        self.xcontrol = QtWidgets.QDoubleSpinBox()
        self.xcontrol.setDecimals(0)
        self.xcontrol.setMaximum(self.image4DShape[0] - 1)
        self.xcontrol.setValue(initLocation[0])
        self.xcontrol.valueChanged.connect(self.changeXcontrol)
        self.ycontrol = QtWidgets.QDoubleSpinBox()
        self.ycontrol.setDecimals(0)
        self.ycontrol.setMaximum(self.image4DShape[1] - 1)
        self.ycontrol.setValue(initLocation[1])
        self.ycontrol.valueChanged.connect(self.changeYcontrol)
        self.zcontrol = QtWidgets.QDoubleSpinBox()
        self.zcontrol.setDecimals(0)
        self.zcontrol.setMaximum(self.image4DShape[2] - 1)
        self.zcontrol.setValue(initLocation[2])
        self.zcontrol.valueChanged.connect(self.changeZcontrol)

        self.tcontrol = QtWidgets.QDoubleSpinBox()
        self.tcontrol.setDecimals(0)
        self.tcontrol.setMaximum(self.image4DShape[3] - 1)
        self.tcontrol.setValue(initLocation[3])
        self.tcontrol.valueChanged.connect(self.changeTcontrol)

        self.tavgradcontrol = QtWidgets.QDoubleSpinBox()
        self.tavgradcontrol.setDecimals(0)
        self.tavgradcontrol.setMaximum(min(self.image4DShape[:-1]) - 1)
        self.tavgradcontrol.setValue(0)
        self.tavgradcontrol.valueChanged.connect(self.changeTavgRadcontrol)

        label = QtWidgets.QLabel()
        label.setText("X")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locLayout.addWidget(label)
        locLayout.addWidget(self.xcontrol)
        label = QtWidgets.QLabel()
        label.setText("Y")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locLayout.addWidget(label)
        locLayout.addWidget(self.ycontrol)
        label = QtWidgets.QLabel()
        label.setText("Z")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locLayout.addWidget(label)
        locLayout.addWidget(self.zcontrol)
        label = QtWidgets.QLabel()
        label.setText("volume")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locLayout.addWidget(label)
        locLayout.addWidget(self.tcontrol)
        label = QtWidgets.QLabel()
        label.setText("t_avg rad")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        # locLayout.addWidget(label)
        # locLayout.addWidget(self.tavgradcontrol)

        controlLayout.addLayout(imTypeLayout)
        """controlLayout.addLayout(cMapLayout)"""
        controlLayout.addLayout(locLayout)
        # this makes the controls widget the parent of all wlLayout's widgets
        controlLayout.addLayout(self.wlLayout)
        controlLayout.addStretch()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)

    # signals to emit when a control panel dial is changed
    def changeImageType(self, index):
        self.sig_img_disp_type_change.emit(index)

    def changeWindow(self, value):
        if self.window.hasFocus():
            self.sig_window_level_change.emit(value, self.level.value())

    def changeLevel(self, value):
        if self.level.hasFocus():
            self.sig_window_level_change.emit(self.window.value(), value)

    def changeXcontrol(self, value):
        if self.xcontrol.hasFocus():
            self.sig_x_change.emit(value)

    def changeYcontrol(self, value):
        if self.ycontrol.hasFocus():
            self.sig_y_change.emit(value)

    def changeZcontrol(self, value):
        if self.zcontrol.hasFocus():
            self.sig_z_change.emit(value)

    def changeTcontrol(self, value):
        if self.tcontrol.hasFocus():
            self.sig_t_change.emit(value)

    def changeTavgRadcontrol(self, value):
        if self.tavgradcontrol.hasFocus():
            self.signalTavgRadChange.emit(value)

    def reset_wl(self):
        self.sig_window_level_reset.emit()

    # slots to update control dials when settings are changed
    # using mechanisms other than the control panel
    def onXChange(self, value):
        self.xcontrol.setValue(value)

    def onYChange(self, value):
        self.ycontrol.setValue(value)

    def onZChange(self, value):
        self.zcontrol.setValue(value)

    def onImageTypeChange(self, index):
        self.imgType.setCurrentIndex(index)

    def onImageCMapChange(self, index):
        self.colorMap.setCurrentIndex(index)

    def onWindowLevelChange(self, windowValue, levelValue):
        self.window.setValue(windowValue)
        self.level.setValue(levelValue)

    def onWindowLevelReset(self):
        self.window.setValue(0.0)
        self.level.setValue(0.0)
