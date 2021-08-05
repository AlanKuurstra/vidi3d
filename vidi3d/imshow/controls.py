"""
This class contains the widgets for user control in the 4D viewer.
"""
import numpy as np
from PyQt5 import QtWidgets

from ..signals import Signals


class _ControlWidget4D(Signals, QtWidgets.QWidget):
    def __init__(self,
                 image_shape,
                 cursor_loc,
                 display_type):
        super(_ControlWidget4D, self).__init__()
        self.image_shape = image_shape
        control_layout = QtWidgets.QVBoxLayout(self)

        # Display type
        disp_type_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("Display Type")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.display_type = QtWidgets.QComboBox()

        # todo: better way of mapping combo box index to display type
        # the order of these have to match DisplayDefinitions class
        # consider changing that class to a dictionary to use here
        self.display_type.addItem("Real")
        self.display_type.addItem("Imaginary")
        self.display_type.addItem("Magnitude")
        self.display_type.addItem("Phase")

        self.display_type.setCurrentIndex(display_type)

        self.display_type.currentIndexChanged.connect(self.change_display_type)
        disp_type_layout.addWidget(label)
        disp_type_layout.addWidget(self.display_type)

        # window/level
        self.wl_layout = QtWidgets.QHBoxLayout()
        self.window = QtWidgets.QDoubleSpinBox()
        self.window.setMaximumWidth(70)
        self.window.setDecimals(3)
        self.window.setMaximum(1.7 * 10 ** 308)
        self.window.valueChanged.connect(self.change_window)
        self.level = QtWidgets.QDoubleSpinBox()
        self.level.setMaximumWidth(70)
        self.level.setDecimals(3)
        self.level.setMaximum(1.7 * 10 ** 308)
        self.level.setMinimum(-1.7 * 10 ** 308)
        self.level.setValue(np.floor(self.window.value() / 2))
        self.level.valueChanged.connect(self.change_level)
        label = QtWidgets.QLabel()
        label.setText("window")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.wl_layout.addWidget(label)
        self.wl_layout.addWidget(self.window)
        label = QtWidgets.QLabel()
        label.setText("level")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.wl_layout.addWidget(label)
        self.wl_layout.addWidget(self.level)
        button = QtWidgets.QPushButton("Default")
        button.clicked.connect(self.reset_wl)
        self.wl_layout.addWidget(button)

        # Coordinates
        cursor_layout = QtWidgets.QHBoxLayout()
        self.xcontrol = QtWidgets.QDoubleSpinBox()
        self.xcontrol.setDecimals(0)
        self.xcontrol.setMaximum(self.image_shape[0] - 1)
        self.xcontrol.setValue(cursor_loc.x)
        self.xcontrol.valueChanged.connect(self.change_x_control)
        self.ycontrol = QtWidgets.QDoubleSpinBox()
        self.ycontrol.setDecimals(0)
        self.ycontrol.setMaximum(self.image_shape[1] - 1)
        self.ycontrol.setValue(cursor_loc.y)
        self.ycontrol.valueChanged.connect(self.change_y_control)
        self.zcontrol = QtWidgets.QDoubleSpinBox()
        self.zcontrol.setDecimals(0)
        self.zcontrol.setMaximum(self.image_shape[2] - 1)
        self.zcontrol.setValue(cursor_loc.z)
        self.zcontrol.valueChanged.connect(self.change_z_control)
        self.tcontrol = QtWidgets.QDoubleSpinBox()
        self.tcontrol.setDecimals(0)
        self.tcontrol.setMaximum(self.image_shape[3] - 1)
        self.tcontrol.setValue(cursor_loc.t)
        self.tcontrol.valueChanged.connect(self.change_t_control)

        label = QtWidgets.QLabel()
        label.setText("X")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        cursor_layout.addWidget(label)
        cursor_layout.addWidget(self.xcontrol)
        label = QtWidgets.QLabel()
        label.setText("Y")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        cursor_layout.addWidget(label)
        cursor_layout.addWidget(self.ycontrol)
        label = QtWidgets.QLabel()
        label.setText("Z")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        cursor_layout.addWidget(label)
        cursor_layout.addWidget(self.zcontrol)
        label = QtWidgets.QLabel()
        label.setText("volume")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        cursor_layout.addWidget(label)
        cursor_layout.addWidget(self.tcontrol)

        control_layout.addLayout(disp_type_layout)
        control_layout.addLayout(cursor_layout)
        # this makes control_widget widget the parent of all wl_layout's widgets
        control_layout.addLayout(self.wl_layout)
        control_layout.addStretch()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    # todo: slot naming convention?
    # Relay slots (ie. emit a new signal)
    def change_display_type(self, index):
        self.sig_img_disp_type_change.emit(index)

    def change_window(self, value):
        if self.window.hasFocus():
            self.sig_window_level_change.emit(value, self.level.value())

    def change_level(self, value):
        if self.level.hasFocus():
            self.sig_window_level_change.emit(self.window.value(), value)

    def change_x_control(self, value):
        if self.xcontrol.hasFocus():
            self.sig_x_change.emit(value)

    def change_y_control(self, value):
        if self.ycontrol.hasFocus():
            self.sig_y_change.emit(value)

    def change_z_control(self, value):
        if self.zcontrol.hasFocus():
            self.sig_z_change.emit(value)

    def change_t_control(self, value):
        if self.tcontrol.hasFocus():
            self.sig_t_change.emit(value)

    def reset_wl(self):
        self.sig_window_level_reset.emit()

    # update control dials when settings are updated without controls (ie. mouse movement or button presses)
    def on_x_change(self, value):
        self.xcontrol.setValue(value)

    def on_y_change(self, value):
        self.ycontrol.setValue(value)

    def on_z_change(self, value):
        self.zcontrol.setValue(value)

    def on_display_type_change(self, index):
        self.display_type.setCurrentIndex(index)

    def on_cmap_change(self, index):
        self.colorMap.setCurrentIndex(index)

    def on_window_level_change(self, windowValue, levelValue):
        self.window.setValue(windowValue)
        self.level.setValue(levelValue)

    def on_window_level_reset(self):
        self.window.setValue(0.0)
        self.level.setValue(0.0)
