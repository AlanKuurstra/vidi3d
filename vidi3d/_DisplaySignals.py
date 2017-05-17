"""
QT event signals.
"""
from PyQt4 import QtCore

signalImageTypeChange = QtCore.pyqtSignal(int, name='imageTypeChanged')
signalImageCmapChange = QtCore.pyqtSignal(int, name='imageCmapChanged')

signalXLocationChange = QtCore.pyqtSignal(int, name='xLocationChanged')
signalYLocationChange = QtCore.pyqtSignal(int, name='yLocationChanged')
signalZLocationChange = QtCore.pyqtSignal(int, name='zLocationChanged')
signalTLocationChange = QtCore.pyqtSignal(int, name='tLocationChanged')
signalLocationChange = QtCore.pyqtSignal(int, int)

signalWindowLevelChange = QtCore.pyqtSignal(
    float, float, name='windowLevelChanged')
signalWindowLevelReset = QtCore.pyqtSignal(name='windowLevelReset')

signalROIInit = QtCore.pyqtSignal(int, name='ROIInit')
signalROIDestruct = QtCore.pyqtSignal(int, name='ROIDestruct')
signalROIDeleteLast = QtCore.pyqtSignal(name='ROIDeleteLast')
signalROIClear = QtCore.pyqtSignal(name='ROIClear')
signalROIChange = QtCore.pyqtSignal(float, float)
signalROIStart = QtCore.pyqtSignal(float, float)
signalROIEnd = QtCore.pyqtSignal(float, float)
signalROICancel = QtCore.pyqtSignal()
signalROIAvgTimecourse = QtCore.pyqtSignal(name='ROIAvgTimecourse')
signalROIPSCTimecourse = QtCore.pyqtSignal(name='ROIPSCTimecourse')
signalROI1VolHistogram = QtCore.pyqtSignal(int, name='ROI1VolHistogram')

signalMovieGotoFrame = QtCore.pyqtSignal(int, name='MovieGotoFrame')
signalMoviePause = QtCore.pyqtSignal(name='MoviePause')
signalMovieInit = QtCore.pyqtSignal(int, name='MovieInit')
signalMovieDestruct = QtCore.pyqtSignal(int, name='MovieDestruct')
signalMovieIntervalChange = QtCore.pyqtSignal(
    int, name='MovieIntervalChanged')

signalOverlayLowerThreshChange = QtCore.pyqtSignal(
    float, float, name="OverlayLowerThreshChanged")
signalOverlayUpperThreshChange = QtCore.pyqtSignal(
    float, float, name="OverlayUpperThreshChanged")
signalOverlayAlphaChange = QtCore.pyqtSignal(float, name="OverlayAlphaChanged")

signalLockPlotsChange = QtCore.pyqtSignal(name='lockPlotsChnaged')
