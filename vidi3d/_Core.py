"""
Core functions for setting up the viewers.  Creating the qApp event loop and 
a global dictionary of viewer objects.
"""
from PyQt4 import QtGui, QtCore


def _create_qApp():
    """
    Only one qApp can exist at a time, so check before creating one.
    """
    if QtGui.QApplication.startingUp():
        global qApp
        app = QtGui.QApplication.instance()
        if app is None:
            qApp = QtGui.QApplication([" "])
            QtCore.QObject.connect(qApp, QtCore.SIGNAL("lastWindowClosed()"),
                                   qApp, QtCore.SLOT("quit()"))
        else:
            qApp = app


def _storeViewer(viewer):
    _checkViewerListExists()
    global _viewerList
    viewerCount = 0
    while(1):
        viewerCount += 1
        if not viewerCount in _viewerList:
            _viewerList[viewerCount] = viewer
            break
    return viewerCount


def _checkViewerListExists():
    global _viewerList
    try:
        _viewerList
    except NameError:
        _viewerList = {}
