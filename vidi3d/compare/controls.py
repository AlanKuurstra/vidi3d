"""
This class contains the widgets for user control in the compare viewer.
"""

from copy import deepcopy

import numpy as np
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ..definitions import ImageDisplayType
from ..signals import Signals


class CompareControlWidget(Signals, QtWidgets.QWidget):
    def __init__(self,
                 img_shape=None,
                 location=None,
                 location_labels=None,
                 img_vals=None,
                 overlay_range=[-np.finfo('float').max / 2, np.finfo('float').max / 2]
                 ):
        QtWidgets.QWidget.__init__(self)
        control_layout = QtWidgets.QGridLayout(self)
        self.control_layout = control_layout
        layout_row_index = 0

        # Display Type
        self.display_type_val = ImageDisplayType.mag

        label = QtWidgets.QLabel()
        label.setText("View")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.display_type = QtWidgets.QComboBox()
        self.display_type.addItem("Magnitude")
        self.display_type.addItem("Phase")
        self.display_type.addItem("Real")
        self.display_type.addItem("Imaginary")

        # todo: better way of mapping combo box index to display type
        self.combo_index_to_display_type = {
            0: ImageDisplayType.mag,
            1: ImageDisplayType.phase,
            2: ImageDisplayType.real,
            3: ImageDisplayType.imag,
        }
        self.display_type_to_combo_index = {v: k for k, v in self.combo_index_to_display_type.items()}

        self.display_type.setCurrentIndex(self.display_type_to_combo_index[self.display_type_val])
        control_layout.addWidget(self.display_type, layout_row_index, 0)
        layout_row_index = layout_row_index + 1

        # window/level
        wl_layout = QtWidgets.QHBoxLayout()
        wl_spinbox_layout = QtWidgets.QGridLayout()
        self.window_val = 0.0
        self.level_val = 0.0
        self.window = QtWidgets.QDoubleSpinBox()
        self.window.setDecimals(3)
        self.window.setMaximum(1.7 * 10 ** 308)
        self.window.setMaximumWidth(80)
        self.level = QtWidgets.QDoubleSpinBox()
        self.level.setDecimals(3)
        self.level.setMaximum(1.7 * 10 ** 308)
        self.level.setMinimum(-1.7 * 10 ** 308)
        self.level.setMaximumWidth(80)
        label = QtWidgets.QLabel()
        label.setText("W")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)

        wl_spinbox_layout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        wl_spinbox_layout.addWidget(self.window, 0, 1)

        label = QtWidgets.QLabel()
        label.setText("L")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        wl_spinbox_layout.addWidget(label, 1, 0, alignment=QtCore.Qt.AlignRight)
        wl_spinbox_layout.addWidget(self.level, 1, 1)
        wl_layout.addLayout(wl_spinbox_layout)
        self.wlbutton = QtWidgets.QPushButton("Default W/L")
        wl_layout.addWidget(self.wlbutton)
        self.control_layout.addLayout(
            wl_layout, layout_row_index, 0, alignment=QtCore.Qt.AlignLeft)
        layout_row_index = layout_row_index + 1

        # Coordinate Controls
        location_layout = QtWidgets.QGridLayout()
        self.location = deepcopy(location)
        self.xcontrol = QtWidgets.QSpinBox()
        self.xcontrol.setMinimum(0)
        self.xcontrol.setMaximum(img_shape[0] - 1)
        self.xcontrol.setValue(location.x)
        self.ycontrol = QtWidgets.QSpinBox()
        self.ycontrol.setMinimum(0)
        self.ycontrol.setMaximum(img_shape[1] - 1)
        self.ycontrol.setValue(location.y)
        self.zcontrol = QtWidgets.QSpinBox()
        self.zcontrol.setMinimum(0)
        self.zcontrol.setMaximum(img_shape[2] - 1)
        self.zcontrol.setValue(location.z)
        self.tcontrol = QtWidgets.QDoubleSpinBox()
        self.tcontrol.setDecimals(0)
        self.tcontrol.setMaximum(img_shape[3] - 1)
        self.tcontrol.setValue(location.t)

        if location_labels is None:
            location_labels = ["X", "Y", "Z", "T"]

        label = QtWidgets.QLabel()
        label.setText(location_labels[0])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        location_layout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        location_layout.addWidget(self.xcontrol, 0, 1)

        label = QtWidgets.QLabel()
        label.setText(location_labels[1])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        location_layout.addWidget(label, 0, 2, alignment=QtCore.Qt.AlignRight)
        location_layout.addWidget(self.ycontrol, 0, 3)

        label = QtWidgets.QLabel()
        label.setText(location_labels[2])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        location_layout.addWidget(label, 0, 4, alignment=QtCore.Qt.AlignRight)
        location_layout.addWidget(self.zcontrol, 0, 5)

        time_layout = QtWidgets.QHBoxLayout()  # QtWidgets.QGridLayout()

        label = QtWidgets.QLabel()
        label.setText(location_labels[3])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        time_layout.addWidget(label, alignment=QtCore.Qt.AlignRight)
        time_layout.addWidget(self.tcontrol)  # , 0, 1)
        time_layout.addStretch(1)
        label = QtWidgets.QLabel()
        label.setText("Lock 1D Plots:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.lock_plots_checkbox = QtWidgets.QCheckBox()
        time_layout.addWidget(label, alignment=QtCore.Qt.AlignRight)
        time_layout.addWidget(self.lock_plots_checkbox, alignment=QtCore.Qt.AlignLeft)

        self.control_layout.addLayout(location_layout, layout_row_index, 0, alignment=QtCore.Qt.AlignLeft)
        layout_row_index = layout_row_index + 1
        self.control_layout.addLayout(time_layout, layout_row_index, 0, alignment=QtCore.Qt.AlignLeft)
        layout_row_index = layout_row_index + 1

        # Movie Controls
        movie_layout = QtWidgets.QVBoxLayout()
        interval_layout = QtWidgets.QGridLayout()

        label = QtWidgets.QLabel()
        label.setText("interval")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        interval_layout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)

        init_interval = 1000  # ms
        movie_interval_min = 100
        movie_interval_max = 5000

        self.num_steps_bw_movie_slider_ints = 1

        movie_slider_min = movie_interval_min * self.num_steps_bw_movie_slider_ints
        movie_slider_max = movie_interval_max * self.num_steps_bw_movie_slider_ints
        self.movie_interval_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.movie_interval_slider.setMinimum(movie_slider_min)
        self.movie_interval_slider.setMaximum(movie_slider_max)
        self.movie_interval_slider.setValue(init_interval * self.num_steps_bw_movie_slider_ints)
        self.movie_interval_spinbox = QtWidgets.QSpinBox()
        self.movie_interval_spinbox.setMinimum(1)
        self.movie_interval_spinbox.setMaximum(movie_interval_max)
        self.movie_interval_spinbox.setValue(init_interval)
        self.movie_pause_button = QtWidgets.QPushButton("||")
        self.movie_pause_button.setCheckable(True)
        self.movie_pause_button.setFixedWidth(40)

        interval_layout.addWidget(self.movie_interval_slider, 0, 1)
        interval_layout.addWidget(self.movie_interval_spinbox, 0, 2)
        interval_layout.addWidget(self.movie_pause_button, 0, 3)

        frame_control_layout = QtWidgets.QGridLayout()
        label = QtWidgets.QLabel()
        label.setText("Goto frame:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.movie_frame_spinbox = QtWidgets.QSpinBox()
        self.movie_frame_spinbox.setMinimum(0)
        self.movie_frame_spinbox.setMaximum(img_shape[-1] - 1)
        self.movie_goto_frame_button = QtWidgets.QPushButton("Go")
        frame_control_layout.addWidget(label, 0, 0)
        frame_control_layout.addWidget(self.movie_frame_spinbox, 0, 1)
        frame_control_layout.addWidget(self.movie_goto_frame_button, 0, 2)

        movie_layout.addLayout(interval_layout)
        movie_layout.addLayout(frame_control_layout)

        movie_widget = QtWidgets.QGroupBox()
        movie_widget.setTitle('Movie Control')
        movie_widget.setLayout(movie_layout)
        movie_widget.setStyleSheet("\
                          QGroupBox {\
                          border: 1px solid gray;\
                          border-radius: 9px;\
                          margin-top: 0.5em;} \
                          \
                          QGroupBox::title {\
                          subcontrol-origin: margin;\
                          left: 10px;\
                          padding: 0 3px 0 3px;}")
        self.movie_widget = movie_widget
        self.movie_widget.setEnabled(False)
        control_layout.addWidget(movie_widget, layout_row_index, 0)
        layout_row_index = layout_row_index + 1

        # ROI Analysis
        roi_layout = QtWidgets.QVBoxLayout()
        tmp = QtWidgets.QHBoxLayout()
        self.delete_last_roi_button = QtWidgets.QPushButton("Delete Last")
        self.delete_last_roi_button.setToolTip("Delete last drawn ROI")
        self.clear_roi_button = QtWidgets.QPushButton("Clear All")
        self.clear_roi_button.setToolTip("Delete all drawn ROIs")
        tmp.addWidget(self.delete_last_roi_button)
        tmp.addWidget(self.clear_roi_button)
        roi_layout.addLayout(tmp)

        tmp = QtWidgets.QHBoxLayout()
        self.roi_avg_timecourse_button = QtWidgets.QPushButton("Avg")
        self.roi_avg_timecourse_button.setToolTip("Plot average timecourse")
        self.roi_psc_timecourse_button = QtWidgets.QPushButton("PSC")
        self.roi_psc_timecourse_button.setToolTip("Plot percent signal change timecourse")
        tmp.addWidget(self.roi_avg_timecourse_button)
        tmp.addWidget(self.roi_psc_timecourse_button)
        roi_layout.addLayout(tmp)

        tmp = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("# of Bins")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        tmp.addWidget(label)
        self.num_bins = QtWidgets.QSpinBox()
        self.num_bins.setMinimum(1)
        self.num_bins.setValue(10)
        tmp.addWidget(self.num_bins)
        self.roi_1Vol_histogram_button = QtWidgets.QPushButton("Hist")
        self.roi_1Vol_histogram_button.setToolTip("Plot 1 volume histogram")
        tmp.addWidget(self.roi_1Vol_histogram_button)
        roi_layout.addLayout(tmp)

        roi_analysis_widget = QtWidgets.QGroupBox()
        roi_analysis_widget.setTitle('ROI Analysis')
        roi_analysis_widget.setLayout(roi_layout)
        roi_analysis_widget.setStyleSheet("\
                          QGroupBox {\
                          border: 1px solid gray;\
                          border-radius: 9px;\
                          margin-top: 0.5em;} \
                          \
                          QGroupBox::title {\
                          subcontrol-origin: margin;\
                          left: 10px;\
                          padding: 0 3px 0 3px;}")
        self.roi_analysis_widget = roi_analysis_widget
        self.roi_analysis_widget.setEnabled(False)
        control_layout.addWidget(roi_analysis_widget, layout_row_index, 0)
        layout_row_index = layout_row_index + 1

        # Overlay Thresholding
        def set_min_max_value(widget, minmax_value):
            widget.setMinimum(minmax_value[0])
            widget.setMaximum(minmax_value[1])
            widget.setValue(minmax_value[2])

        overlay_layout = QtWidgets.QVBoxLayout()
        # thresholding
        overlay_threshold_layout = QtWidgets.QGridLayout()
        self.lower_thresh_spinbox = QtWidgets.QDoubleSpinBox()
        self.upper_thresh_spinbox = QtWidgets.QDoubleSpinBox()
        self.lower_thresh_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.upper_thresh_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.upper_thresh_slider.setInvertedAppearance(True)
        overlay_diff = (np.float(overlay_range[1]) - overlay_range[0])
        mant, exp = ('%.5e' % overlay_diff).split('e')
        if np.double(mant) < 5.0:
            exp = int(exp)
        else:
            exp = int(exp) + 1
        exp = exp - 2
        stepsize = 10 ** exp

        # add extra to min and max
        self.overlay_minmax = overlay_range
        self.overlay_minmax[0] -= stepsize
        self.overlay_minmax[1] += stepsize
        overlay_diff = (self.overlay_minmax[1] - self.overlay_minmax[0])

        self.overlay_slider_minmax = [-np.iinfo('int32').max / 2, np.iinfo('int32').max / 2]
        self.overlay_slider_to_float = float(overlay_diff) / (
                    self.overlay_slider_minmax[1] - self.overlay_slider_minmax[0])
        init_slider_value = 0
        init_spin_box_value = self.overlay_minmax[0] + self.overlay_slider_to_float * (
                    float(init_slider_value) - self.overlay_slider_minmax[0])
        set_min_max_value(self.lower_thresh_spinbox, overlay_range + [init_spin_box_value, ])
        self.lower_thresh_spinbox.setSingleStep(stepsize)
        set_min_max_value(self.upper_thresh_spinbox, overlay_range + [init_spin_box_value, ])
        self.upper_thresh_spinbox.setSingleStep(stepsize)
        if exp < 0:
            self.lower_thresh_spinbox.setDecimals(np.abs(exp))
            self.upper_thresh_spinbox.setDecimals(np.abs(exp))
        else:
            self.lower_thresh_spinbox.setDecimals(2)
            self.upper_thresh_spinbox.setDecimals(2)
        set_min_max_value(self.lower_thresh_slider, self.overlay_slider_minmax + [0, ])
        set_min_max_value(self.upper_thresh_slider, self.overlay_slider_minmax + [0, ])

        overlay_threshold_layout.addWidget(self.lower_thresh_spinbox, 0, 1)
        overlay_threshold_layout.addWidget(self.lower_thresh_slider, 0, 0)
        overlay_threshold_layout.addWidget(self.upper_thresh_slider, 1, 0)
        overlay_threshold_layout.addWidget(self.upper_thresh_spinbox, 1, 1)

        # invert
        overlay_invert_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("Invert Mask:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.overlay_invert_checkbox = QtWidgets.QCheckBox()
        overlay_invert_layout.addWidget(label)
        overlay_invert_layout.addWidget(self.overlay_invert_checkbox)

        # alpha
        overlay_alpha_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("Alpha")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.overlay_alpha_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.overlay_alpha_spinbox = QtWidgets.QDoubleSpinBox()
        alpha_min = 0
        alpha_max = 1
        alpha_init = 0.5
        self.alpha_spinbox_step = 0.01
        alpha_slider_min = 0
        alpha_slider_max = np.ceil(alpha_max / self.alpha_spinbox_step)
        alpha_slider_init = int(alpha_init / self.alpha_spinbox_step)
        set_min_max_value(self.overlay_alpha_slider, [alpha_slider_min, alpha_slider_max, alpha_slider_init])
        set_min_max_value(self.overlay_alpha_spinbox, [alpha_min, alpha_max, alpha_init])
        self.overlay_alpha_spinbox.setSingleStep(self.alpha_spinbox_step)
        self.overlay_alpha_spinbox.setDecimals(2)
        overlay_alpha_layout.addWidget(label, alignment=QtCore.Qt.AlignRight)
        overlay_alpha_layout.addWidget(self.overlay_alpha_slider)
        overlay_alpha_layout.addWidget(self.overlay_alpha_spinbox)

        # overlays layout
        overlay_layout.addLayout(overlay_threshold_layout)
        overlay_layout.addLayout(overlay_invert_layout)
        overlay_layout.addLayout(overlay_alpha_layout)

        overlay_threshold_widget = QtWidgets.QGroupBox()
        overlay_threshold_widget.setTitle('Overlay Thresholding')
        overlay_threshold_widget.setLayout(overlay_layout)
        overlay_threshold_widget.setStyleSheet("\
                          QGroupBox {\
                          border: 1px solid gray;\
                          border-radius: 9px;\
                          margin-top: 0.5em;} \
                          \
                          QGroupBox::title {\
                          subcontrol-origin: margin;\
                          left: 10px;\
                          padding: 0 3px 0 3px;}")
        self.overlay_threshold_widget = overlay_threshold_widget
        control_layout.addWidget(overlay_threshold_widget, layout_row_index, 0)
        layout_row_index = layout_row_index + 1

        # Display Image Values
        img_vals_layout = QtWidgets.QGridLayout()
        self.img_val_labels = []
        if img_vals is not None:
            num_imgs = len(img_vals)
            for indx in range(num_imgs):
                label = QtWidgets.QLabel()
                label.setText(str(img_vals[indx][0]) + ":")
                img_vals_layout.addWidget(label, indx, 0, alignment=QtCore.Qt.AlignRight)
                label = QtWidgets.QLabel()
                label.setText('%.5e' % (img_vals[indx][1]))
                self.img_val_labels.append(label)
                img_vals_layout.addWidget(label, indx, 1, alignment=QtCore.Qt.AlignLeft)
        tmp = QtWidgets.QGroupBox()
        tmp.setTitle('Image Values')
        tmp.setLayout(img_vals_layout)

        control_layout.addWidget(tmp, layout_row_index, 0)
        layout_row_index = layout_row_index + 1

        self.make_connections()

        control_layout.setRowStretch(layout_row_index, 10)

    def make_connections(self):
        self.display_type.currentIndexChanged.connect(self.display_type_changed)
        self.window.valueChanged.connect(self.window_changed)
        self.level.valueChanged.connect(self.level_changed)
        self.wlbutton.clicked.connect(self.window_level_to_default_pushed)

        self.xcontrol.valueChanged.connect(self.x_location_changed)
        self.ycontrol.valueChanged.connect(self.y_location_changed)
        self.zcontrol.valueChanged.connect(self.z_location_changed)
        self.tcontrol.valueChanged.connect(self.change_t_control)
        self.lock_plots_checkbox.clicked.connect(self.lock_plots_checkbox_pushed)

        self.delete_last_roi_button.clicked.connect(self.delete_last_roi_pushed)
        self.clear_roi_button.clicked.connect(self.clear_roi_pushed)
        self.roi_avg_timecourse_button.clicked.connect(self.roi_avg_timecourse_pushed)
        self.roi_psc_timecourse_button.clicked.connect(self.roi_psc_timecourse_pushed)
        self.roi_1Vol_histogram_button.clicked.connect(self.roi_1Vol_histogram_button_pushed)

        self.lower_thresh_slider.valueChanged.connect(self.lower_thresh_slider_changed)
        self.upper_thresh_slider.valueChanged.connect(self.upper_thresh_slider_changed)
        self.lower_thresh_spinbox.valueChanged.connect(self.lower_thresh_spinbox_changed)
        self.upper_thresh_spinbox.valueChanged.connect(self.upper_thresh_spinbox_changed)
        self.overlay_invert_checkbox.clicked.connect(self.overlay_invert_pushed)
        self.overlay_alpha_slider.valueChanged.connect(self.overlay_alpha_slider_changed)
        self.overlay_alpha_spinbox.valueChanged.connect(self.overlay_alpha_spinbox_changed)

        self.movie_interval_slider.valueChanged.connect(self.movie_interval_slider_changed)
        self.movie_interval_spinbox.valueChanged.connect(self.movie_interval_spinbox_changed)
        self.movie_goto_frame_button.clicked.connect(self.movie_goto_frame)
        self.movie_pause_button.clicked.connect(self.movie_pause)

    def quiet_set_value(self, control, value):
        control.blockSignals(True)
        control.setValue(value)
        control.blockSignals(False)

    # todo: slot naming convention?
    # todo: these should be relays simiar to imshow/controls.py, Compare() object should do all the work
    # todo: is the block if x != self.location.x really necessary? (does it stop an infinite signal_loop, or is it for efficiency...to stop an another assignment of x)
    def x_location_changed(self, x):
        # todo: loc set multiple times: changes location then signals cursor_change, which is connected to Compare.change_location, which calls controls.change_location both of which set and read the cursor causing a minmanx operation
        if x != self.location.x:
            self.location.x = x
            self.sig_cursor_change.emit(self.location.x, self.location.y)

    def y_location_changed(self, y):
        if y != self.location.y:
            self.location.y = y
            self.sig_cursor_change.emit(self.location.x, self.location.y)

    def z_location_changed(self, z):
        if z != self.location.z:
            self.location.z = z
            self.sig_z_change.emit(self.location.z)

    def display_type_changed(self, index):
        new_display_type = self.combo_index_to_display_type[index]
        if new_display_type != self.display_type_val:
            self.display_type_val = new_display_type
            self.sig_img_disp_type_change.emit(new_display_type)

    def window_changed(self, value):
        if value != self.window_val:
            self.window_val = value
            self.sig_window_level_change.emit(self.window_val, self.level_val)

    def level_changed(self, value):
        if value != self.level_val:
            self.level_val = value
            self.sig_window_level_change.emit(self.window_val, self.level_val)

    def window_level_to_default_pushed(self):
        self.sig_window_level_reset.emit()

    def set_display_type(self, new_display_type):
        if new_display_type != self.display_type_val:
            self.display_type_val = new_display_type
            self.display_type.setCurrentIndex(self.display_type_to_combo_index[self.display_type_val])

    # todo: perhaps all the change_ slots should just worry about adjusting the visual display and not affect the internal data objects...in fact the self.window and self.value attributes can be removed and we can get the values from the spinbox, and the self.loc object is shared and should be changed by Compare slots, not be Controls slots.
    def change_location(self, x, y):
        # # todo: loc set multiple times: location already changed by Compare.change_location and Controls.x_location_changed
        self.location.x = x
        self.location.y = y
        self.xcontrol.setValue(x)
        self.ycontrol.setValue(y)

    def change_z_location(self, z):
        self.location.z = z
        self.zcontrol.setValue(z)

    def change_window_level(self, new_window, new_level):
        self.window_val = new_window
        self.level_val = new_level
        self.level.setValue(new_level)
        self.window.setValue(new_window)

    def change_img_vals(self, newVals):
        for i in range(len(newVals)):
            self.img_val_labels[i].setText('%.3e' % (newVals[i]))

    def change_t_control(self, value):
        if self.tcontrol.hasFocus():
            self.sig_t_change.emit(value)

    def lock_plots_checkbox_pushed(self):
        self.sig_lock_plots_change.emit()

    def delete_last_roi_pushed(self):
        self.sig_roi_del_last.emit()

    def clear_roi_pushed(self):
        self.sig_roi_clear.emit()

    def roi_avg_timecourse_pushed(self):
        self.sig_roi_avg_timecourse.emit()

    def roi_psc_timecourse_pushed(self):
        self.sig_roi_psc_timecourse.emit()

    def roi_1Vol_histogram_button_pushed(self):
        self.sig_roi_1vol_histogram.emit(self.num_bins.value())

    def lower_thresh_slider_changed(self, lower_thresh):
        self.lower_thresh_spinbox.setValue(self.overlay_minmax[0] + self.overlay_slider_to_float * (
                    float(lower_thresh) - self.overlay_slider_minmax[0]))
        if lower_thresh > -self.upper_thresh_slider.value():
            self.upper_thresh_slider.setValue(-lower_thresh)

    def upper_thresh_slider_changed(self, upper_thresh):
        upper_thresh = -upper_thresh
        self.upper_thresh_spinbox.setValue(self.overlay_minmax[0] + self.overlay_slider_to_float * (
                    float(upper_thresh) - self.overlay_slider_minmax[0]))
        if upper_thresh < self.lower_thresh_slider.value():
            self.lower_thresh_slider.setValue(upper_thresh)

    def lower_thresh_spinbox_changed(self, lower_thresh):
        sliderVal = self.overlay_slider_minmax[0] + int(
            (lower_thresh - self.overlay_minmax[0]) / self.overlay_slider_to_float)
        self.quiet_set_value(self.lower_thresh_slider, sliderVal)

        if lower_thresh > self.upper_thresh_spinbox.value():
            self.quiet_set_value(self.upper_thresh_slider, -sliderVal)
            self.quiet_set_value(self.upper_thresh_spinbox, lower_thresh)

        self.sig_overlay_lower_thresh_change.emit(lower_thresh, self.upper_thresh_spinbox.value())

    def upper_thresh_spinbox_changed(self, upper_thresh):
        slider_val = self.overlay_slider_minmax[0] + int(
            (upper_thresh - self.overlay_minmax[0]) / self.overlay_slider_to_float)
        self.quiet_set_value(self.upper_thresh_slider, -slider_val)
        if upper_thresh < self.lower_thresh_spinbox.value():
            self.quiet_set_value(self.lower_thresh_slider, slider_val)
            self.quiet_set_value(self.lower_thresh_spinbox, upper_thresh)

        self.sig_overlay_upper_thresh_change.emit(self.lower_thresh_spinbox.value(), upper_thresh)

    def overlay_invert_pushed(self):
        self.sig_overlay_upper_thresh_change.emit(self.lower_thresh_spinbox.value(), self.upper_thresh_spinbox.value())

    def overlay_alpha_slider_changed(self, value):
        self.overlay_alpha_spinbox.setValue(float(value) * self.alpha_spinbox_step)

    def overlay_alpha_spinbox_changed(self, value):
        sliderVal = int(value / self.alpha_spinbox_step)
        self.quiet_set_value(self.overlay_alpha_slider, sliderVal)
        self.sig_overlay_alpha_change.emit(value)

    def movie_interval_slider_changed(self, interval):
        self.movie_interval_spinbox.setValue(float(interval) / self.num_steps_bw_movie_slider_ints)

    def movie_interval_spinbox_changed(self, interval):
        self.movie_interval_slider.blockSignals(True)
        self.quiet_set_value(self.movie_interval_slider, int(interval * self.num_steps_bw_movie_slider_ints))
        self.sig_movie_interval_change.emit(interval)

    def movie_goto_frame(self):
        frame = self.movie_frame_spinbox.value()
        self.sig_movie_goto_frame.emit(frame)

    def movie_pause(self):
        self.sig_movie_pause.emit()
