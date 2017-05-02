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

signalWindowLevelChange = QtCore.pyqtSignal(float, float,name='windowLevelChanged')    
signalWindowLevelReset = QtCore.pyqtSignal(name='windowLevelReset')
signalROIClear = QtCore.pyqtSignal(name='ROIClear')
signalROIAvgTimecourse = QtCore.pyqtSignal(name='ROIAvgTimecourse')
signalROI1VolHistogram = QtCore.pyqtSignal(int,name='ROI1VolHistogram')

signalOverlayLowerThreshChange = QtCore.pyqtSignal(float,float,name="OverlayLowerThreshChanged")
signalOverlayUpperThreshChange = QtCore.pyqtSignal(float,float,name="OverlayUpperThreshChanged")