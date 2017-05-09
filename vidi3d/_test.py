#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May  8 16:16:25 2017

@author: akuurstr
"""
from PyQt4 import QtCore


signalImageCmapChange = QtCore.pyqtSignal(int, name='imageCmapChanged')

signalXLocationChange = QtCore.pyqtSignal(int, name='xLocationChanged')
signalYLocationChange = QtCore.pyqtSignal(int, name='yLocationChanged')
signalZLocationChange = QtCore.pyqtSignal(int, name='zLocationChanged')
signalTLocationChange = QtCore.pyqtSignal(int, name='tLocationChanged')
signalLocationChange = QtCore.pyqtSignal(int, int)
    
signalWindowLevelChange = QtCore.pyqtSignal(float, float,name='windowLevelChanged')    
signalWindowLevelReset = QtCore.pyqtSignal(name='windowLevelReset')

signalROIInitialize = QtCore.pyqtSignal(name='ROIInitialize')
signalROIDestruct = QtCore.pyqtSignal(name='ROIDestruct')
signalROIClear = QtCore.pyqtSignal(name='ROIClear')
signalROIAvgTimecourse = QtCore.pyqtSignal(name='ROIAvgTimecourse')
signalROI1VolHistogram = QtCore.pyqtSignal(int,name='ROI1VolHistogram')

signalMovieInitialize = QtCore.pyqtSignal(name='MovieInitialize')
signalMovieDestruct = QtCore.pyqtSignal(name='MovieDestruct')

signalOverlayLowerThreshChange = QtCore.pyqtSignal(float,float,name="OverlayLowerThreshChanged")
signalOverlayUpperThreshChange = QtCore.pyqtSignal(float,float,name="OverlayUpperThreshChanged")
