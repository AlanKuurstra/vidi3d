"""
QT event signals.
"""
from PyQt5 import QtCore


class Signals:
    sig_img_disp_type_change = QtCore.pyqtSignal(int)
    sig_img_cmap_change = QtCore.pyqtSignal(int)

    sig_x_change = QtCore.pyqtSignal(int)
    sig_y_change = QtCore.pyqtSignal(int)
    sig_z_change = QtCore.pyqtSignal(int)
    sig_t_change = QtCore.pyqtSignal(int)
    sig_cursor_change = QtCore.pyqtSignal(int, int)

    sig_window_level_change = QtCore.pyqtSignal(float, float)
    sig_window_level_reset = QtCore.pyqtSignal()

    sig_roi_init = QtCore.pyqtSignal(int)
    signal_roi_destruct = QtCore.pyqtSignal(int)
    sig_roi_del_last = QtCore.pyqtSignal()
    sig_roi_clear = QtCore.pyqtSignal()
    sig_roi_change = QtCore.pyqtSignal(float, float)
    sig_roi_start = QtCore.pyqtSignal(float, float)
    sig_roi_end = QtCore.pyqtSignal(float, float)
    sig_roi_cancel = QtCore.pyqtSignal()
    sig_roi_avg_timecourse = QtCore.pyqtSignal()
    sig_roi_psc_timecourse = QtCore.pyqtSignal()
    sig_roi_1vol_histogram = QtCore.pyqtSignal(int)

    sig_movie_goto_frame = QtCore.pyqtSignal(int)
    sig_movie_pause = QtCore.pyqtSignal()
    sig_movie_init = QtCore.pyqtSignal(int)
    sig_movie_destruct = QtCore.pyqtSignal(int)
    sig_movie_interval_change = QtCore.pyqtSignal(int)

    sig_overlay_lower_thresh_change = QtCore.pyqtSignal(float, float)
    sig_overlay_upper_thresh_change = QtCore.pyqtSignal(float, float)
    sig_overlay_alpha_change = QtCore.pyqtSignal(float)

    sig_lock_plots_change = QtCore.pyqtSignal()
