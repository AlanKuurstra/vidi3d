"""
This class contains the widgets for user control in the 2D viewer.
"""

import numpy as np
from PyQt4 import QtGui, QtCore
from .. import _Core as _Core
from .. import _DisplayDefinitions as dd


class _ControlWidgetCompare(QtGui.QWidget):
    from .._DisplaySignals import *

    def __init__(self, parent=None, imgShape=None, location=None, locationLabels=None, imageType=None, windowLevel=None, imgVals=None, overlayUsed=False, overlayMinMax=(-np.finfo(float).eps, np.finfo(float).eps)):
        _Core._create_qApp()
        QtGui.QWidget.__init__(self)
        self.parent = parent
        controlLayout = QtGui.QGridLayout(self)
        self.controlLayout = controlLayout
        layoutRowIndex = 0
        #
        # Image Type
        #
        self.currImageType = dd.ImageType.mag

        self.imgTypeIndex = np.zeros(4, dtype=np.int)
        self.imgTypeIndex[dd.ImageType.mag] = 0
        self.imgTypeIndex[dd.ImageType.phase] = 1
        self.imgTypeIndex[dd.ImageType.real] = 2
        self.imgTypeIndex[dd.ImageType.imag] = 3

        self.imageTypeLookup = np.zeros(4, dtype=np.int)
        self.imageTypeLookup[0] = dd.ImageType.mag
        self.imageTypeLookup[1] = dd.ImageType.phase
        self.imageTypeLookup[2] = dd.ImageType.real
        self.imageTypeLookup[3] = dd.ImageType.imag

        label = QtGui.QLabel()
        label.setText("View")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.imgType = QtGui.QComboBox()
        self.imgType.addItem("Magnitude")
        self.imgType.addItem("Phase")
        self.imgType.addItem("Real")
        self.imgType.addItem("Imaginary")
        self.imgType.setCurrentIndex(self.imgTypeIndex[self.currImageType])
        controlLayout.addWidget(self.imgType, layoutRowIndex, 0)
        layoutRowIndex = layoutRowIndex + 1

        #
        # Window/Level
        #
        wlLayout = QtGui.QHBoxLayout()
        wlSpinboxLayout = QtGui.QGridLayout()
        self.currWindow = 0.0
        self.currLevel = 0.0
        self.window = QtGui.QDoubleSpinBox()
        self.window.setDecimals(3)
        self.window.setMaximum(1.7 * 10**308)
        self.window.setMaximumWidth(80)
        self.level = QtGui.QDoubleSpinBox()
        self.level.setDecimals(3)
        self.level.setMaximum(1.7 * 10**308)
        self.level.setMinimum(-1.7 * 10**308)
        self.level.setMaximumWidth(80)
        label = QtGui.QLabel()
        label.setText("W")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)

        wlSpinboxLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        wlSpinboxLayout.addWidget(self.window, 0, 1)

        label = QtGui.QLabel()
        label.setText("L")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        wlSpinboxLayout.addWidget(label, 1, 0, alignment=QtCore.Qt.AlignRight)
        wlSpinboxLayout.addWidget(self.level, 1, 1)
        wlLayout.addLayout(wlSpinboxLayout)
        wlbutton = QtGui.QPushButton("Default W/L")
        wlLayout.addWidget(wlbutton)
        self.controlLayout.addLayout(
            wlLayout, layoutRowIndex, 0, alignment=QtCore.Qt.AlignLeft)
        layoutRowIndex = layoutRowIndex + 1

        #
        # Location
        #
        locationLayout = QtGui.QGridLayout()
        self.location = list(np.array(location).copy())
        self.xcontrol = QtGui.QSpinBox()
        self.xcontrol.setMinimum(0)
        self.xcontrol.setMaximum(imgShape[0] - 1)
        self.xcontrol.setValue(location[0])
        self.ycontrol = QtGui.QSpinBox()
        self.ycontrol.setMinimum(0)
        self.ycontrol.setMaximum(imgShape[1] - 1)
        self.ycontrol.setValue(location[1])
        self.zcontrol = QtGui.QSpinBox()
        self.zcontrol.setMinimum(0)
        self.zcontrol.setMaximum(imgShape[2] - 1)
        self.zcontrol.setValue(location[2])
        self.tcontrol = QtGui.QDoubleSpinBox()
        self.tcontrol.setDecimals(0)
        self.tcontrol.setMaximum(imgShape[3] - 1)
        self.tcontrol.setValue(0)

        if locationLabels is None:
            locationLabels = ["X", "Y", "Z", "T"]

        label = QtGui.QLabel()
        label.setText(locationLabels[0])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locationLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        locationLayout.addWidget(self.xcontrol, 0, 1)

        label = QtGui.QLabel()
        label.setText(locationLabels[1])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locationLayout.addWidget(label, 0, 2, alignment=QtCore.Qt.AlignRight)
        locationLayout.addWidget(self.ycontrol, 0, 3)

        label = QtGui.QLabel()
        label.setText(locationLabels[2])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locationLayout.addWidget(label, 0, 4, alignment=QtCore.Qt.AlignRight)
        locationLayout.addWidget(self.zcontrol, 0, 5)

        temporalLayout = QtGui.QGridLayout()

        label = QtGui.QLabel()
        label.setText(locationLabels[3])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        temporalLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        temporalLayout.addWidget(self.tcontrol, 0, 1)

        self.controlLayout.addLayout(
            locationLayout, layoutRowIndex, 0, alignment=QtCore.Qt.AlignLeft)
        layoutRowIndex = layoutRowIndex + 1
        self.controlLayout.addLayout(
            temporalLayout, layoutRowIndex, 0, alignment=QtCore.Qt.AlignLeft)
        layoutRowIndex = layoutRowIndex + 1
        
        
        #
        # Movie Controls
        #
        movieLayout = QtGui.QVBoxLayout()
        intervalLayout = QtGui.QGridLayout()
        
        label = QtGui.QLabel()
        label.setText("Interval")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        intervalLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
                
        #initFps = 20
        #movieFpsMin = .5  # fps
        #movieFpsMax = 200
        
        initFps = 50
        movieFpsMin = 1  # fps
        movieFpsMax = 1000
        
        #numberOfStepsBetweenMovieSliderIntegers = 100
        self.numberOfStepsBetweenMovieSliderIntegers = 1
        
        movieSliderMin = movieFpsMin * self.numberOfStepsBetweenMovieSliderIntegers
        movieSliderMax = movieFpsMax * self.numberOfStepsBetweenMovieSliderIntegers
        self.movieFpsSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.movieFpsSlider.setMinimum(movieSliderMin)
        self.movieFpsSlider.setMaximum(movieSliderMax)
        self.movieFpsSlider.setValue(
            initFps * self.numberOfStepsBetweenMovieSliderIntegers)
        self.movieFpsSpinbox = QtGui.QDoubleSpinBox()
        self.movieFpsSpinbox.setMinimum(movieFpsMin)
        self.movieFpsSpinbox.setMaximum(movieFpsMax)
        self.movieFpsSpinbox.setValue(initFps)
        
        intervalLayout.addWidget(self.movieFpsSlider, 0, 1)
        intervalLayout.addWidget(self.movieFpsSpinbox, 0, 2)
        
        frameControlLayout = QtGui.QGridLayout()        
        label = QtGui.QLabel()
        label.setText("Goto frame:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.movieFrameSpinbox = QtGui.QSpinBox()
        self.movieFrameSpinbox.setMinimum(0)
        self.movieFrameSpinbox.setMaximum(imgShape[-1] - 1)
        self.movieGotoFrameButton = QtGui.QPushButton("Go")        
        frameControlLayout.addWidget(label,0,0)
        frameControlLayout.addWidget(self.movieFrameSpinbox,0,1)
        frameControlLayout.addWidget(self.movieGotoFrameButton,0,2)
        
        movieLayout.addLayout(intervalLayout)
        movieLayout.addLayout(frameControlLayout)
        
        movieWidget = QtGui.QGroupBox()
        movieWidget.setTitle('Movie Control')
        movieWidget.setLayout(movieLayout)
        movieWidget.setStyleSheet("\
                          QGroupBox {\
                          border: 1px solid gray;\
                          border-radius: 9px;\
                          margin-top: 0.5em;} \
                          \
                          QGroupBox::title {\
                          subcontrol-origin: margin;\
                          left: 10px;\
                          padding: 0 3px 0 3px;}")
        self.movieWidget = movieWidget
        self.movieWidget.setEnabled(False)
        controlLayout.addWidget(movieWidget, layoutRowIndex, 0)
        layoutRowIndex = layoutRowIndex + 1
        
        #
        # ROI Analysis
        #
        roiLayout = QtGui.QVBoxLayout()
        clearROIButton = QtGui.QPushButton("Clear ROI")
        roiLayout.addWidget(clearROIButton)
        #layoutRowIndex = layoutRowIndex+1
        roiAvgTimecourseButton = QtGui.QPushButton("Avg Timecourse")
        roiLayout.addWidget(roiAvgTimecourseButton)
        #layoutRowIndex = layoutRowIndex+1
        roi1VolHistogramButton = QtGui.QPushButton("1 Vol Histogram")
        roiLayout.addWidget(roi1VolHistogramButton)
        #layoutRowIndex = layoutRowIndex+1
        # numBinsWidget=QtGui.QWidget(self)
        numBinsLayout = QtGui.QHBoxLayout()
        label = QtGui.QLabel()
        label.setText("# of Bins")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        numBinsLayout.addWidget(label)
        self.numBins = QtGui.QSpinBox()
        self.numBins.setMinimum(1)
        self.numBins.setValue(10)
        numBinsLayout.addWidget(self.numBins)
        # numBinsWidget.setLayout(numBinsLayout)
        #controlLayout.addWidget(numBinsWidget,layoutRowIndex, 1)
        roiLayout.addLayout(numBinsLayout)
        #layoutRowIndex = layoutRowIndex + 1

        roiAnalysisWidget = QtGui.QGroupBox()
        roiAnalysisWidget.setTitle('ROI Analysis')
        roiAnalysisWidget.setLayout(roiLayout)
        roiAnalysisWidget.setStyleSheet("\
                          QGroupBox {\
                          border: 1px solid gray;\
                          border-radius: 9px;\
                          margin-top: 0.5em;} \
                          \
                          QGroupBox::title {\
                          subcontrol-origin: margin;\
                          left: 10px;\
                          padding: 0 3px 0 3px;}")
        self.roiAnalysisWidget = roiAnalysisWidget
        self.roiAnalysisWidget.setEnabled(False)
        controlLayout.addWidget(roiAnalysisWidget, layoutRowIndex, 0)
        layoutRowIndex = layoutRowIndex + 1

        #
        # Overlay Thresholding
        #
        def setMinMaxValue(widget, MinMaxValue):
            widget.setMinimum(MinMaxValue[0])
            widget.setMaximum(MinMaxValue[1])
            widget.setValue(MinMaxValue[2])

        overlayThresholdLayout = QtGui.QGridLayout()
        self.lowerThreshSpinbox = QtGui.QDoubleSpinBox()
        self.upperThreshSpinbox = QtGui.QDoubleSpinBox()
        self.lowerThreshSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.upperThreshSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.upperThreshSlider.setInvertedAppearance(True)
        self.numberOfStepsBetweenIntegers = 100
        sliderMinMaxLowerThresh = list(
            np.array(overlayMinMax) * self.numberOfStepsBetweenIntegers)
        sliderMinMaxUpperThresh = list(np.array(overlayMinMax)[
                                       ::-1] * -1 * self.numberOfStepsBetweenIntegers)
        setMinMaxValue(self.lowerThreshSpinbox, overlayMinMax + [0, ])
        setMinMaxValue(self.upperThreshSpinbox, overlayMinMax + [0, ])
        setMinMaxValue(self.lowerThreshSlider, sliderMinMaxLowerThresh + [0, ])
        setMinMaxValue(self.upperThreshSlider, sliderMinMaxUpperThresh + [0, ])

        overlayThresholdLayout.addWidget(self.lowerThreshSpinbox, 0, 1)
        overlayThresholdLayout.addWidget(self.lowerThreshSlider, 0, 0)
        overlayThresholdLayout.addWidget(self.upperThreshSlider, 1, 0)
        overlayThresholdLayout.addWidget(self.upperThreshSpinbox, 1, 1)

        if overlayUsed:
            #controlLayout.addLayout(overlayThresholdLayout,layoutRowIndex, 1)
            pass
        layoutRowIndex = layoutRowIndex + 1

        overlayThresholdWidget = QtGui.QGroupBox()
        overlayThresholdWidget.setTitle('Overlay Thresholding')
        overlayThresholdWidget.setLayout(overlayThresholdLayout)
        overlayThresholdWidget.setStyleSheet("\
                          QGroupBox {\
                          border: 1px solid gray;\
                          border-radius: 9px;\
                          margin-top: 0.5em;} \
                          \
                          QGroupBox::title {\
                          subcontrol-origin: margin;\
                          left: 10px;\
                          padding: 0 3px 0 3px;}")
        self.overlayThresholdWidget = overlayThresholdWidget
        controlLayout.addWidget(overlayThresholdWidget, layoutRowIndex, 0)
        layoutRowIndex = layoutRowIndex + 1

        #
        # Display Image Values
        #
        imgValsLayout = QtGui.QGridLayout()
        self.imgValLabels = []
        if imgVals is not None:
            numImgs = len(imgVals)
            for imNum in range(numImgs):
                label = QtGui.QLabel()
                label.setText(str(imgVals[imNum][0]) + ":")
                imgValsLayout.addWidget(
                    label, imNum, 0, alignment=QtCore.Qt.AlignRight)
                label = QtGui.QLabel()
                label.setText('%.3e' % (imgVals[imNum][1]))
                self.imgValLabels.append(label)
                imgValsLayout.addWidget(
                    label, imNum, 1, alignment=QtCore.Qt.AlignLeft)
        tmp = QtGui.QGroupBox()
        tmp.setTitle('Image Values')
        tmp.setLayout(imgValsLayout)

        controlLayout.addWidget(tmp, layoutRowIndex, 0)
        layoutRowIndex = layoutRowIndex + 1

        # controlLayout.addWidget(QtGui.QLabel(),layoutRowIndex,0)
        #layoutRowIndex = layoutRowIndex+1

        controlLayout.setRowStretch(layoutRowIndex, 10)

        QtCore.QObject.connect(self.imgType, QtCore.SIGNAL(
            "currentIndexChanged(int)"), self.ImageTypeChanged)
        QtCore.QObject.connect(self.window, QtCore.SIGNAL(
            "valueChanged(double)"), self.windowChanged)
        QtCore.QObject.connect(self.level, QtCore.SIGNAL(
            "valueChanged(double)"), self.levelChanged)
        QtCore.QObject.connect(wlbutton, QtCore.SIGNAL(
            "clicked()"), self.windowLevelToDefaultPushed)

        QtCore.QObject.connect(self.xcontrol, QtCore.SIGNAL(
            "valueChanged(int)"), self.xLocationChanged)
        QtCore.QObject.connect(self.ycontrol, QtCore.SIGNAL(
            "valueChanged(int)"), self.yLocationChanged)
        QtCore.QObject.connect(self.zcontrol, QtCore.SIGNAL(
            "valueChanged(int)"), self.zLocationChanged)
        QtCore.QObject.connect(self.tcontrol, QtCore.SIGNAL(
            "valueChanged(double)"), self.changeTcontrol)

        QtCore.QObject.connect(clearROIButton, QtCore.SIGNAL(
            "clicked()"), self.clearROIPushed)
        QtCore.QObject.connect(roiAvgTimecourseButton, QtCore.SIGNAL(
            "clicked()"), self.roiAvgTimecoursePushed)
        QtCore.QObject.connect(roi1VolHistogramButton, QtCore.SIGNAL(
            "clicked()"), self.roi1VolHistogramButtonPushed)

        QtCore.QObject.connect(self.lowerThreshSlider, QtCore.SIGNAL(
            "valueChanged(int)"), self.lowerThreshSliderChanged)
        QtCore.QObject.connect(self.upperThreshSlider, QtCore.SIGNAL(
            "valueChanged(int)"), self.upperThreshSliderChanged)
        QtCore.QObject.connect(self.lowerThreshSpinbox, QtCore.SIGNAL(
            "valueChanged(double)"), self.lowerThreshSpinBoxChanged)
        QtCore.QObject.connect(self.upperThreshSpinbox, QtCore.SIGNAL(
            "valueChanged(double)"), self.upperThreshSpinBoxChanged)

        QtCore.QObject.connect(self.movieFpsSlider, QtCore.SIGNAL(
            "valueChanged(int)"), self.movieFpsSliderChanged)
        QtCore.QObject.connect(self.movieFpsSpinbox, QtCore.SIGNAL(
            "valueChanged(double)"), self.movieFpsSpinBoxChanged)
        
        QtCore.QObject.connect(self.movieGotoFrameButton, QtCore.SIGNAL(
            "clicked()"), self.movieGotoFrame)

    def xLocationChanged(self, x):
        if x != self.location[0]:
            self.location[0] = x
            self.signalLocationChange.emit(self.location[0], self.location[1])

    def yLocationChanged(self, y):
        if y != self.location[1]:
            self.location[1] = y
            self.signalLocationChange.emit(self.location[0], self.location[1])

    def zLocationChanged(self, z):
        if z != self.location[2]:
            self.location[2] = z
            self.signalZLocationChange.emit(self.location[2])

    def ImageTypeChanged(self, index):
        newImageType = self.imageTypeLookup[index]
        if newImageType != self.currImageType:
            self.currImageType = newImageType
            self.signalImageTypeChange.emit(newImageType)

    def windowChanged(self, value):
        if value != self.currWindow:
            self.currWindow = value
            self.signalWindowLevelChange.emit(self.currWindow, self.currLevel)

    def levelChanged(self, value):
        if value != self.currLevel:
            self.currLevel = value
            self.signalWindowLevelChange.emit(self.currWindow, self.currLevel)

    def windowLevelToDefaultPushed(self):
        self.signalWindowLevelReset.emit()

    def SetImageType(self, newImageType):
        if newImageType != self.currImageType:
            self.currImageType = newImageType
            self.imgType.setCurrentIndex(self.imgTypeIndex[self.currImageType])

    def ChangeLocation(self, x, y):
        self.location[0] = x
        self.location[1] = y
        self.xcontrol.setValue(x)
        self.ycontrol.setValue(y)

    def ChangeZLocation(self, z):
        self.location[2] = z
        self.zcontrol.setValue(z)

    def ChangeWindowLevel(self, newIntensityWindow, newIntensityLevel):
        self.currWindow = newIntensityWindow
        self.currLevel = newIntensityLevel
        self.level.setValue(newIntensityLevel)
        self.window.setValue(newIntensityWindow)

    def ChangeImgVals(self, newVals):
        for i in range(len(newVals)):
            self.imgValLabels[i].setText('%.3e' % (newVals[i]))

    def changeTcontrol(self, value):
        if self.tcontrol.hasFocus():
            self.signalTLocationChange.emit(value)

    def clearROIPushed(self):
        self.signalROIClear.emit()

    def roiAvgTimecoursePushed(self):
        self.signalROIAvgTimecourse.emit()

    def roi1VolHistogramButtonPushed(self):
        self.signalROI1VolHistogram.emit(self.numBins.value())

    def lowerThreshSliderChanged(self, lowerThresh):
        self.lowerThreshSpinbox.setValue(
            float(lowerThresh) / self.numberOfStepsBetweenIntegers)
        if lowerThresh > -self.upperThreshSlider.value():
            self.upperThreshSlider.setValue(-lowerThresh)

    def upperThreshSliderChanged(self, upperThresh):
        upperThresh = -upperThresh
        self.upperThreshSpinbox.setValue(
            float(upperThresh) / self.numberOfStepsBetweenIntegers)
        if upperThresh < self.lowerThreshSlider.value():
            self.lowerThreshSlider.setValue(upperThresh)

    def lowerThreshSpinBoxChanged(self, lowerThresh):
        self.lowerThreshSlider.setValue(
            int(lowerThresh * self.numberOfStepsBetweenIntegers))
        if lowerThresh > self.upperThreshSpinbox.value():
            self.upperThreshSpinbox.setValue(lowerThresh)
        self.signalOverlayLowerThreshChange.emit(
            lowerThresh, self.upperThreshSpinbox.value())

    def upperThreshSpinBoxChanged(self, upperThresh):
        # self.upperThreshSlider.setValue(self.upperThreshSlider.maximum-int(upperThresh*self.numberOfStepsBetweenIntegers))
        # if upperThresh<self.lowerThreshSpinbox.value():
        #    self.lowerThreshSpinbox.setValue(upperThresh)
        self.signalOverlayUpperThreshChange.emit(
            self.lowerThreshSpinbox.value(), upperThresh)

    def movieFpsSliderChanged(self, Fps):        
        self.movieFpsSpinbox.setValue(
            float(Fps) / self.numberOfStepsBetweenMovieSliderIntegers)            

    def movieFpsSpinBoxChanged(self, Fps):
        interval = Fps#1.0 / Fps * 1e3  # in ms
        # self.parent.imagePanelToolbarsList[0].tmp.event_source.interval=interval
        self.movieFpsSlider.setValue(int(Fps*self.numberOfStepsBetweenMovieSliderIntegers))
        self.signalMovieIntervalChange.emit(interval)
        # self.parent.imagePanelToolbarsList[0].tmp.timer.interval=interval
    def movieGotoFrame(self):
        frame=self.movieFrameSpinbox.value()
        self.signalMovieGotoFrame.emit(frame)
