"""
Core functions for setting up the viewers.  Creating the qApp event loop and 
a global dictionary of viewer objects.
"""
from collections import Iterable

import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtWidgets, QtCore

# Only one qApp can exist at a time, so check before creating one.
app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([" "])
    app.quitOnLastWindowClosed()

_open_viewers = {}


def start_viewer(viewer, block, window_title=None):
    if block:
        if window_title is not None:
            viewer.setWindowTitle(window_title)
        QtWidgets.qApp.exec_()
        return
    else:
        # this is noisy, so suppress the stdout.
        plt.ion()
        viewer_num = store_viewer(viewer)
        viewer.set_viewer_number(viewer_num)

        if window_title is None:
            viewer.setWindowTitle('Viewer ' + str(viewer_num))
        else:
            viewer.setWindowTitle(window_title)
        return viewer


def store_viewer(viewer):
    global _open_viewers
    viewer_count = 0
    while True:
        viewer_count += 1
        if viewer_count not in _open_viewers:
            _open_viewers[viewer_count] = viewer
            break
    return viewer_count


def close(num=None):
    """
    Close a Viewer.

    close('all') closes all figures

    close(num) closes viewer number num
    """
    global _open_viewers
    if isinstance(num, int):
        if num <= len(_open_viewers) and num in _open_viewers:
            _open_viewers[num].close()
    elif isinstance(num, str) and num.lower() == 'all':
        _open_viewers.clear()
    else:
        raise ValueError(f'argument {num} not a valid viewer index')


def pause(length_ms):
    """
    Pause for length_ms milliseconds.

    Viewers will be updated and displayed, and the GUI event loop will run during the pause.
    """

    loop = QtCore.QEventLoop()
    timer = QtCore.QTimer()
    timer.singleShot(length_ms, loop.quit)
    loop.exec_()


def split_array(array, axis=-1, index_list=None):
    """
    Split a higher dimensional array into a list of lower dimensional arrays.
    Useful for splitting a 3d image into a list of 2d slices passed to compare2d.

    """
    if index_list is None:
        index_list = np.arange(0, array.shape[axis])
    tmp = np.take(array, index_list, axis=axis)
    return np.split(tmp, tmp.shape[axis], axis=axis)


def to_list(input_data):
    if isinstance(input_data, (np.ndarray, str)) or not isinstance(input_data, Iterable):
        input_data = [input_data, ]
    return list(input_data)
