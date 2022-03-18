"""
Sets up the main window for the 4D viewer. This includes creating MpImage4D, MpPlot,
ControlWidget4D.  Also connections are made between QT signals sent by other
classes and functions within this class.
"""

from PyQt5 import QtCore, QtWidgets

from . import controls
from . import image4d
from .. import core
from ..coordinates import XYZTCoord
from ..definitions import ImageDisplayType


class Imshow3d(QtWidgets.QMainWindow):
    def __init__(self,
                 complex_image,
                 background_threshold=0.05,
                 pixdim=None,
                 interpolation='bicubic',
                 ):
        super(Imshow3d, self).__init__()
        self.setWindowTitle('Vidi3d: imshow3d')
        self.viewer_number = 0

        img_shape = complex_image.shape
        cursor_loc = XYZTCoord(img_shape, int(img_shape[0] / 2), int(img_shape[1] / 2), int(img_shape[2] / 2), 0)
        display_type = ImageDisplayType.mag

        self.image4d = image4d.Image4D(complex_image,
                                       background_threshold,
                                       cursor_loc,
                                       display_type,
                                       pixdim,
                                       interpolation,
                                       )
        self.controls = controls._ControlWidget4D(img_shape,
                                                  cursor_loc,
                                                  display_type)
        image4d_widget = QtWidgets.QWidget()
        image4d_layout = QtWidgets.QGridLayout()
        image4d_layout.addWidget(self.controls, 1, 0)
        image4d_layout.addWidget(self.image4d.x_nav, 2, 0)
        image4d_layout.addWidget(self.image4d.xslice, 3, 0)
        image4d_layout.addWidget(self.image4d.y_nav, 0, 1)
        image4d_layout.addWidget(self.image4d.yslice, 1, 1)
        image4d_layout.addWidget(self.image4d.z_nav, 2, 1)
        image4d_layout.addWidget(self.image4d.zslice, 3, 1)
        image4d_widget.setLayout(image4d_layout)

        plots_widget = QtWidgets.QWidget()
        plots_layout = QtWidgets.QVBoxLayout()
        plots_layout.addWidget(self.image4d.xplot)
        plots_layout.addWidget(self.image4d.yplot)
        plots_layout.addWidget(self.image4d.zplot)
        plots_layout.addWidget(self.image4d.tplot)
        plots_widget.setLayout(plots_layout)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(image4d_widget)
        splitter.addWidget(plots_widget)

        # used when inheriting from QMainWindow
        self.setCentralWidget(splitter)
        # self.statusBar().showMessage('Ready')

        self.make_connections()

        self.show()
        self.setFocus()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def make_connections(self):
        self.controls.sig_img_disp_type_change.connect(self.image4d.on_display_type_change)

        # when cursor moves, update lines
        self.image4d.zslice.sig_x_change.connect(self.image4d.on_x_change)
        self.image4d.zslice.sig_y_change.connect(self.image4d.on_y_change)
        self.image4d.zslice.sig_z_change.connect(self.image4d.on_z_change)

        self.image4d.xslice.sig_x_change.connect(self.image4d.on_x_change)
        self.image4d.xslice.sig_y_change.connect(self.image4d.on_y_change)
        self.image4d.xslice.sig_z_change.connect(self.image4d.on_z_change)

        self.image4d.yslice.sig_x_change.connect(self.image4d.on_x_change)
        self.image4d.yslice.sig_y_change.connect(self.image4d.on_y_change)
        self.image4d.yslice.sig_z_change.connect(self.image4d.on_z_change)

        # when cursor moves, update control_widget
        self.image4d.xslice.sig_x_change.connect(self.controls.on_x_change)
        self.image4d.xslice.sig_y_change.connect(self.controls.on_y_change)
        self.image4d.xslice.sig_z_change.connect(self.controls.on_z_change)

        self.image4d.yslice.sig_x_change.connect(self.controls.on_x_change)
        self.image4d.yslice.sig_y_change.connect(self.controls.on_y_change)
        self.image4d.yslice.sig_z_change.connect(self.controls.on_z_change)

        self.image4d.zslice.sig_x_change.connect(self.controls.on_x_change)
        self.image4d.zslice.sig_y_change.connect(self.controls.on_y_change)
        self.image4d.zslice.sig_z_change.connect(self.controls.on_z_change)

        # when right button pressed, update window/level of images
        self.image4d.xslice.sig_window_level_change.connect(self.image4d.on_window_level_change)
        self.image4d.yslice.sig_window_level_change.connect(self.image4d.on_window_level_change)
        self.image4d.zslice.sig_window_level_change.connect(self.image4d.on_window_level_change)

        # when right button pressed, update window/level control_widget
        self.image4d.xslice.sig_window_level_change.connect(self.controls.on_window_level_change)
        self.image4d.yslice.sig_window_level_change.connect(self.controls.on_window_level_change)
        self.image4d.zslice.sig_window_level_change.connect(self.controls.on_window_level_change)

        # when cursor_loc control changes, update lines
        self.controls.sig_x_change.connect(self.image4d.on_x_change)
        self.controls.sig_y_change.connect(self.image4d.on_y_change)
        self.controls.sig_z_change.connect(self.image4d.on_z_change)
        self.controls.sig_t_change.connect(self.image4d.on_t_change)

        # when window/level control changes, update images
        self.controls.sig_window_level_change.connect(self.image4d.on_window_level_change)

        # when window/level reset pressed, update images and control
        self.controls.sig_window_level_reset.connect(self.controls.on_window_level_reset)
        self.controls.sig_window_level_reset.connect(self.image4d.on_window_level_reset)

    def keyPressEvent(self, event):
        key = event.key()
        if key == 77:
            self.image4d.on_display_type_change(ImageDisplayType.mag)
            self.controls.on_display_type_change(ImageDisplayType.mag)
        elif key == 80:
            self.image4d.on_display_type_change(ImageDisplayType.phase)
            self.controls.on_display_type_change(ImageDisplayType.phase)
        elif key == 82:
            self.image4d.on_display_type_change(ImageDisplayType.real)
            self.controls.on_display_type_change(ImageDisplayType.real)
        elif key == 73:
            self.image4d.on_display_type_change(ImageDisplayType.imag)
            self.controls.on_display_type_change(ImageDisplayType.imag)
        event.ignore()

    def set_viewer_number(self, number):
        self.viewer_number = number

    def closeEvent(self, event):
        if self.viewer_number:
            del core._open_viewers[self.viewer_number]
