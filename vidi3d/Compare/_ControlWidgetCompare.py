"""
This class contains the widgets for user control in the compare viewer.
"""

import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from .. import _Core as _Core
from .. import _DisplayDefinitions as dd
from .._DisplaySignals import Signals
from PyQt5 import QtCore

class _ControlWidgetCompare(Signals, QtWidgets.QWidget):
    def __init__(self, parent=None, imgShape=None, location=None, locationLabels=None, imageType=None, windowLevel=None, imgVals=None, overlayUsed=False, overlayMinMax=[-np.finfo('float').max / 2, np.finfo('float').max / 2]):
        _Core._create_qApp()
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        controlLayout = QtWidgets.QGridLayout(self)
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

        label = QtWidgets.QLabel()
        label.setText("View")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.imgType = QtWidgets.QComboBox()
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
        wlLayout = QtWidgets.QHBoxLayout()
        wlSpinboxLayout = QtWidgets.QGridLayout()
        self.currWindow = 0.0
        self.currLevel = 0.0
        self.window = QtWidgets.QDoubleSpinBox()
        self.window.setDecimals(3)
        self.window.setMaximum(1.7 * 10**308)
        self.window.setMaximumWidth(80)
        self.level = QtWidgets.QDoubleSpinBox()
        self.level.setDecimals(3)
        self.level.setMaximum(1.7 * 10**308)
        self.level.setMinimum(-1.7 * 10**308)
        self.level.setMaximumWidth(80)
        label = QtWidgets.QLabel()
        label.setText("W")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)

        wlSpinboxLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        wlSpinboxLayout.addWidget(self.window, 0, 1)

        label = QtWidgets.QLabel()
        label.setText("L")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        wlSpinboxLayout.addWidget(label, 1, 0, alignment=QtCore.Qt.AlignRight)
        wlSpinboxLayout.addWidget(self.level, 1, 1)
        wlLayout.addLayout(wlSpinboxLayout)
        self.wlbutton = QtWidgets.QPushButton("Default W/L")
        wlLayout.addWidget(self.wlbutton)
        self.controlLayout.addLayout(
            wlLayout, layoutRowIndex, 0, alignment=QtCore.Qt.AlignLeft)
        layoutRowIndex = layoutRowIndex + 1

        #
        # Location Controls
        #
        locationLayout = QtWidgets.QGridLayout()
        self.location = list(np.array(location).copy())
        self.xcontrol = QtWidgets.QSpinBox()
        self.xcontrol.setMinimum(0)
        self.xcontrol.setMaximum(imgShape[0] - 1)
        self.xcontrol.setValue(location[0])
        self.ycontrol = QtWidgets.QSpinBox()
        self.ycontrol.setMinimum(0)
        self.ycontrol.setMaximum(imgShape[1] - 1)
        self.ycontrol.setValue(location[1])
        self.zcontrol = QtWidgets.QSpinBox()
        self.zcontrol.setMinimum(0)
        self.zcontrol.setMaximum(imgShape[2] - 1)
        self.zcontrol.setValue(location[2])
        self.tcontrol = QtWidgets.QDoubleSpinBox()
        self.tcontrol.setDecimals(0)
        self.tcontrol.setMaximum(imgShape[3] - 1)
        self.tcontrol.setValue(0)

        if locationLabels is None:
            locationLabels = ["X", "Y", "Z", "T"]

        label = QtWidgets.QLabel()
        label.setText(locationLabels[0])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locationLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)
        locationLayout.addWidget(self.xcontrol, 0, 1)

        label = QtWidgets.QLabel()
        label.setText(locationLabels[1])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locationLayout.addWidget(label, 0, 2, alignment=QtCore.Qt.AlignRight)
        locationLayout.addWidget(self.ycontrol, 0, 3)

        label = QtWidgets.QLabel()
        label.setText(locationLabels[2])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        locationLayout.addWidget(label, 0, 4, alignment=QtCore.Qt.AlignRight)
        locationLayout.addWidget(self.zcontrol, 0, 5)

        temporalLayout = QtWidgets.QHBoxLayout()  # QtWidgets.QGridLayout()

        label = QtWidgets.QLabel()
        label.setText(locationLabels[3])
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        # , 0, 0, alignment=QtCore.Qt.AlignRight)
        temporalLayout.addWidget(label, alignment=QtCore.Qt.AlignRight)
        temporalLayout.addWidget(self.tcontrol)  # , 0, 1)
        temporalLayout.addStretch(1)
        label = QtWidgets.QLabel()
        label.setText("Lock 1D Plots:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.lockPlotsCheckbox = QtWidgets.QCheckBox()
        # , 0, 3, alignment=QtCore.Qt.AlignRight)
        temporalLayout.addWidget(label, alignment=QtCore.Qt.AlignRight)
        # , 0, 4, alignment=QtCore.Qt.AlignLeft)
        temporalLayout.addWidget(
            self.lockPlotsCheckbox, alignment=QtCore.Qt.AlignLeft)

        self.controlLayout.addLayout(
            locationLayout, layoutRowIndex, 0, alignment=QtCore.Qt.AlignLeft)
        layoutRowIndex = layoutRowIndex + 1
        self.controlLayout.addLayout(
            temporalLayout, layoutRowIndex, 0, alignment=QtCore.Qt.AlignLeft)
        layoutRowIndex = layoutRowIndex + 1

        #
        # Movie Controls
        #
        movieLayout = QtWidgets.QVBoxLayout()
        intervalLayout = QtWidgets.QGridLayout()

        label = QtWidgets.QLabel()
        label.setText("Interval")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        intervalLayout.addWidget(label, 0, 0, alignment=QtCore.Qt.AlignRight)

        """        
        initFps = 20
        movieFpsMin = .5  # fps
        movieFpsMax = 200
        
        self.numberOfStepsBetweenMovieSliderIntegers = 100
        
        movieSliderMin = movieFpsMin * self.numberOfStepsBetweenMovieSliderIntegers
        movieSliderMax = movieFpsMax * self.numberOfStepsBetweenMovieSliderIntegers
        self.movieFpsSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.movieFpsSlider.setMinimum(movieSliderMin)
        self.movieFpsSlider.setMaximum(movieSliderMax)
        self.movieFpsSlider.setValue(
            initFps * self.numberOfStepsBetweenMovieSliderIntegers)
        self.movieFpsSpinbox = QtWidgets.QDoubleSpinBox()
        self.movieFpsSpinbox.setMinimum(movieFpsMin)
        self.movieFpsSpinbox.setMaximum(movieFpsMax)
        self.movieFpsSpinbox.setValue(initFps)
        """

        initInterval = 1000  # ms
        movieIntervalMin = 100
        movieIntervalMax = 5000

        self.numberOfStepsBetweenMovieSliderIntegers = 1

        movieSliderMin = movieIntervalMin * self.numberOfStepsBetweenMovieSliderIntegers
        movieSliderMax = movieIntervalMax * self.numberOfStepsBetweenMovieSliderIntegers
        self.movieIntervalSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.movieIntervalSlider.setMinimum(movieSliderMin)
        self.movieIntervalSlider.setMaximum(movieSliderMax)
        self.movieIntervalSlider.setValue(
            initInterval * self.numberOfStepsBetweenMovieSliderIntegers)
        self.movieIntervalSpinbox = QtWidgets.QSpinBox()
        self.movieIntervalSpinbox.setMinimum(1)
        self.movieIntervalSpinbox.setMaximum(movieIntervalMax)
        self.movieIntervalSpinbox.setValue(initInterval)
        self.moviePauseButton = QtWidgets.QPushButton("||")
        self.moviePauseButton.setCheckable(True)
        self.moviePauseButton.setFixedWidth(40)

        intervalLayout.addWidget(self.movieIntervalSlider, 0, 1)
        intervalLayout.addWidget(self.movieIntervalSpinbox, 0, 2)
        intervalLayout.addWidget(self.moviePauseButton, 0, 3)

        frameControlLayout = QtWidgets.QGridLayout()
        label = QtWidgets.QLabel()
        label.setText("Goto frame:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.movieFrameSpinbox = QtWidgets.QSpinBox()
        self.movieFrameSpinbox.setMinimum(0)
        self.movieFrameSpinbox.setMaximum(imgShape[-1] - 1)
        self.movieGotoFrameButton = QtWidgets.QPushButton("Go")
        frameControlLayout.addWidget(label, 0, 0)
        frameControlLayout.addWidget(self.movieFrameSpinbox, 0, 1)
        frameControlLayout.addWidget(self.movieGotoFrameButton, 0, 2)

        movieLayout.addLayout(intervalLayout)
        movieLayout.addLayout(frameControlLayout)

        movieWidget = QtWidgets.QGroupBox()
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
        roiLayout = QtWidgets.QVBoxLayout()
        tmp = QtWidgets.QHBoxLayout()
        self.deleteLastROIButton = QtWidgets.QPushButton("Delete Last")
        self.deleteLastROIButton.setToolTip("Delete last drawn ROI")
        self.clearROIButton = QtWidgets.QPushButton("Clear All")
        self.clearROIButton.setToolTip("Delete all drawn ROIs")
        tmp.addWidget(self.deleteLastROIButton)
        tmp.addWidget(self.clearROIButton)
        roiLayout.addLayout(tmp)

        tmp = QtWidgets.QHBoxLayout()
        self.roiAvgTimecourseButton = QtWidgets.QPushButton("Avg")
        self.roiAvgTimecourseButton.setToolTip("Plot average timecourse")
        self.roiPSCTimecourseButton = QtWidgets.QPushButton("PSC")
        self.roiPSCTimecourseButton.setToolTip(
            "Plot percent signal change timecourse")
        tmp.addWidget(self.roiAvgTimecourseButton)
        tmp.addWidget(self.roiPSCTimecourseButton)
        roiLayout.addLayout(tmp)

        tmp = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("# of Bins")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        tmp.addWidget(label)
        self.numBins = QtWidgets.QSpinBox()
        self.numBins.setMinimum(1)
        self.numBins.setValue(10)
        tmp.addWidget(self.numBins)
        self.roi1VolHistogramButton = QtWidgets.QPushButton("Hist")
        self.roi1VolHistogramButton.setToolTip("Plot 1 volume histogram")
        tmp.addWidget(self.roi1VolHistogramButton)
        roiLayout.addLayout(tmp)

        roiAnalysisWidget = QtWidgets.QGroupBox()
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

        overlayLayout = QtWidgets.QVBoxLayout()
        # thresholding
        overlayThresholdLayout = QtWidgets.QGridLayout()
        self.lowerThreshSpinbox = QtWidgets.QDoubleSpinBox()
        self.upperThreshSpinbox = QtWidgets.QDoubleSpinBox()
        self.lowerThreshSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.upperThreshSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.upperThreshSlider.setInvertedAppearance(True)
        overlayDiff = (np.float(overlayMinMax[1]) - overlayMinMax[0])
        mant, exp = ('%.5e' % overlayDiff).split('e')
        if np.double(mant) < 5.0:
            exp = int(exp)
        else:
            exp = int(exp) + 1
        exp = exp - 2
        stepsize = 10**(exp)

        # add extra to min and max
        self.overlayMinMax = overlayMinMax
        self.overlayMinMax[0] -= stepsize
        self.overlayMinMax[1] += stepsize
        overlayDiff = (self.overlayMinMax[1] - self.overlayMinMax[0])
        """
        self.numberOfStepsBetweenIntegers = max(1/stepsize,1)
        sliderMinMaxLowerThresh = list(
            np.array(overlayMinMax) * self.numberOfStepsBetweenIntegers)
        sliderMinMaxUpperThresh = list(np.array(overlayMinMax)[
                                       ::-1] * -1 * self.numberOfStepsBetweenIntegers)
        """

        self.overlaySliderMinMax = [-np.iinfo('int32').max / 2,
                                    np.iinfo('int32').max / 2]
        self.overlaySliderToFloat = float(overlayDiff) / \
            (self.overlaySliderMinMax[1] - self.overlaySliderMinMax[0])
        initSliderValue = 0
        initSpinBoxValue = self.overlayMinMax[0] + self.overlaySliderToFloat * (
            float(initSliderValue) - self.overlaySliderMinMax[0])
        setMinMaxValue(self.lowerThreshSpinbox,
                       overlayMinMax + [initSpinBoxValue, ])
        self.lowerThreshSpinbox.setSingleStep(stepsize)
        setMinMaxValue(self.upperThreshSpinbox,
                       overlayMinMax + [initSpinBoxValue, ])
        self.upperThreshSpinbox.setSingleStep(stepsize)
        if exp < 0:
            self.lowerThreshSpinbox.setDecimals(np.abs(exp))
            self.upperThreshSpinbox.setDecimals(np.abs(exp))
        else:
            self.lowerThreshSpinbox.setDecimals(2)
            self.upperThreshSpinbox.setDecimals(2)
        setMinMaxValue(self.lowerThreshSlider,
                       self.overlaySliderMinMax + [0, ])
        setMinMaxValue(self.upperThreshSlider,
                       self.overlaySliderMinMax + [0, ])

        overlayThresholdLayout.addWidget(self.lowerThreshSpinbox, 0, 1)
        overlayThresholdLayout.addWidget(self.lowerThreshSlider, 0, 0)
        overlayThresholdLayout.addWidget(self.upperThreshSlider, 1, 0)
        overlayThresholdLayout.addWidget(self.upperThreshSpinbox, 1, 1)

        # invert
        overlayInvertLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("Invert Mask:")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.overlayInvertCheckbox = QtWidgets.QCheckBox()
        overlayInvertLayout.addWidget(label)
        overlayInvertLayout.addWidget(self.overlayInvertCheckbox)

        # alpha
        overlayAlphaLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText("Alpha")
        label.setFixedWidth(label.fontMetrics().width(label.text()) + 5)
        self.overlayAlphaSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.overlayAlphaSpinbox = QtWidgets.QDoubleSpinBox()
        alphaMin = 0
        alphaMax = 1
        alphaInit = 0.5
        self.alphaSpinboxStep = 0.01
        alphaSliderMin = 0
        alphaSliderMax = np.ceil(alphaMax / self.alphaSpinboxStep)
        alphaSliderInit = int(alphaInit / self.alphaSpinboxStep)
        setMinMaxValue(self.overlayAlphaSlider, [
                       alphaSliderMin, alphaSliderMax, alphaSliderInit])
        setMinMaxValue(self.overlayAlphaSpinbox, [
                       alphaMin, alphaMax, alphaInit])
        self.overlayAlphaSpinbox.setSingleStep(self.alphaSpinboxStep)
        self.overlayAlphaSpinbox.setDecimals(2)
        overlayAlphaLayout.addWidget(label, alignment=QtCore.Qt.AlignRight)
        overlayAlphaLayout.addWidget(self.overlayAlphaSlider)
        overlayAlphaLayout.addWidget(self.overlayAlphaSpinbox)

        # overlay layout
        overlayLayout.addLayout(overlayThresholdLayout)
        overlayLayout.addLayout(overlayInvertLayout)
        overlayLayout.addLayout(overlayAlphaLayout)

        overlayThresholdWidget = QtWidgets.QGroupBox()
        overlayThresholdWidget.setTitle('Overlay Thresholding')
        overlayThresholdWidget.setLayout(overlayLayout)
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
        imgValsLayout = QtWidgets.QGridLayout()
        self.imgValLabels = []
        if imgVals is not None:
            numImgs = len(imgVals)
            for imNum in range(numImgs):
                label = QtWidgets.QLabel()
                label.setText(str(imgVals[imNum][0]) + ":")
                imgValsLayout.addWidget(
                    label, imNum, 0, alignment=QtCore.Qt.AlignRight)
                label = QtWidgets.QLabel()
                label.setText('%.5e' % (imgVals[imNum][1]))
                self.imgValLabels.append(label)
                imgValsLayout.addWidget(
                    label, imNum, 1, alignment=QtCore.Qt.AlignLeft)
        tmp = QtWidgets.QGroupBox()
        tmp.setTitle('Image Values')
        tmp.setLayout(imgValsLayout)

        controlLayout.addWidget(tmp, layoutRowIndex, 0)
        layoutRowIndex = layoutRowIndex + 1

        self.makeConnections()

        controlLayout.setRowStretch(layoutRowIndex, 10)

    def makeConnections(self):
        self.imgType.currentIndexChanged.connect(self.ImageTypeChanged)
        self.window.valueChanged.connect(self.windowChanged)
        self.level.valueChanged.connect(self.levelChanged)
        self.wlbutton.clicked.connect(self.windowLevelToDefaultPushed)

        self.xcontrol.valueChanged.connect(self.xLocationChanged)
        self.ycontrol.valueChanged.connect(self.yLocationChanged)
        self.zcontrol.valueChanged.connect(self.zLocationChanged)
        self.tcontrol.valueChanged.connect(self.changeTcontrol)
        self.lockPlotsCheckbox.clicked.connect(self.lockPlotsCheckboxPushed)

        self.deleteLastROIButton.clicked.connect(self.deleteLastROIPushed)
        self.clearROIButton.clicked.connect(self.clearROIPushed)
        self.roiAvgTimecourseButton.clicked.connect(self.roiAvgTimecoursePushed)
        self.roiPSCTimecourseButton.clicked.connect(self.roiPSCTimecoursePushed)
        self.roi1VolHistogramButton.clicked.connect(self.roi1VolHistogramButtonPushed)

        self.lowerThreshSlider.valueChanged.connect(self.lowerThreshSliderChanged)
        self.upperThreshSlider.valueChanged.connect(self.upperThreshSliderChanged)
        self.lowerThreshSpinbox.valueChanged.connect(self.lowerThreshSpinBoxChanged)
        self.upperThreshSpinbox.valueChanged.connect(self.upperThreshSpinBoxChanged)
        self.overlayInvertCheckbox.clicked.connect(self.overlayInvertPushed)
        self.overlayAlphaSlider.valueChanged.connect(self.overlayAlphaSliderChanged)
        self.overlayAlphaSpinbox.valueChanged.connect(self.overlayAlphaSpinBoxChanged)

        self.movieIntervalSlider.valueChanged.connect(self.movieIntervalSliderChanged)
        self.movieIntervalSpinbox.valueChanged.connect(self.movieIntervalSpinBoxChanged)
        self.movieGotoFrameButton.clicked.connect(self.movieGotoFrame)
        self.moviePauseButton.clicked.connect(self.moviePause)


    def blockedSetValue(self, control, value):
        control.blockSignals(True)
        control.setValue(value)
        control.blockSignals(False)

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

    def lockPlotsCheckboxPushed(self):
        self.signalLockPlotsChange.emit()

    def deleteLastROIPushed(self):
        self.signalROIDeleteLast.emit()

    def clearROIPushed(self):
        self.signalROIClear.emit()

    def roiAvgTimecoursePushed(self):
        self.signalROIAvgTimecourse.emit()

    def roiPSCTimecoursePushed(self):
        self.signalROIPSCTimecourse.emit()

    def roi1VolHistogramButtonPushed(self):
        self.signalROI1VolHistogram.emit(self.numBins.value())

    def lowerThreshSliderChanged(self, lowerThresh):
        self.lowerThreshSpinbox.setValue(
            self.overlayMinMax[0] + self.overlaySliderToFloat * (float(lowerThresh) - self.overlaySliderMinMax[0]))
        if lowerThresh > -self.upperThreshSlider.value():
            self.upperThreshSlider.setValue(-lowerThresh)

        """
        self.lowerThreshSpinbox.setValue(
            float(lowerThresh) / self.numberOfStepsBetweenIntegers)
    
        if lowerThresh > -self.upperThreshSlider.value():
            self.upperThreshSlider.setValue(-lowerThresh)
        """

    def upperThreshSliderChanged(self, upperThresh):
        upperThresh = -upperThresh
        self.upperThreshSpinbox.setValue(
            self.overlayMinMax[0] + self.overlaySliderToFloat * (float(upperThresh) - self.overlaySliderMinMax[0]))
        if upperThresh < self.lowerThreshSlider.value():
            self.lowerThreshSlider.setValue(upperThresh)

        """
        upperThresh = -upperThresh
        self.upperThreshSpinbox.setValue(
            float(upperThresh) / self.numberOfStepsBetweenIntegers)
        if upperThresh < self.lowerThreshSlider.value():
            self.lowerThreshSlider.setValue(upperThresh)
        """

    def lowerThreshSpinBoxChanged(self, lowerThresh):
        sliderVal = self.overlaySliderMinMax[0] + int(
            (lowerThresh - self.overlayMinMax[0]) / self.overlaySliderToFloat)
        self.blockedSetValue(self.lowerThreshSlider, sliderVal)

        if lowerThresh > self.upperThreshSpinbox.value():
            self.blockedSetValue(self.upperThreshSlider, -sliderVal)
            self.blockedSetValue(self.upperThreshSpinbox, lowerThresh)
        """
        self.blockedSetValue(self.lowerThreshSlider,int(lowerThresh * self.numberOfStepsBetweenIntegers))
        
        if lowerThresh > self.upperThreshSpinbox.value():
            self.blockedSetValue(self.upperThreshSlider,int(-lowerThresh * self.numberOfStepsBetweenIntegers))
            self.blockedSetValue(self.upperThreshSpinbox,lowerThresh)     
        """
        self.signalOverlayLowerThreshChange.emit(
            lowerThresh, self.upperThreshSpinbox.value())

    def upperThreshSpinBoxChanged(self, upperThresh):
        sliderVal = self.overlaySliderMinMax[0] + int(
            (upperThresh - self.overlayMinMax[0]) / self.overlaySliderToFloat)
        self.blockedSetValue(self.upperThreshSlider, -sliderVal)
        if upperThresh < self.lowerThreshSpinbox.value():
            self.blockedSetValue(self.lowerThreshSlider, sliderVal)
            self.blockedSetValue(self.lowerThreshSpinbox, upperThresh)
        """         
        self.blockedSetValue(self.upperThreshSlider, -int(upperThresh*self.numberOfStepsBetweenIntegers))
        if upperThresh<self.lowerThreshSpinbox.value():            
            self.blockedSetValue(self.lowerThreshSlider, int(upperThresh*self.numberOfStepsBetweenIntegers))
            self.blockedSetValue(self.lowerThreshSpinbox, upperThresh)
        """
        self.signalOverlayUpperThreshChange.emit(
            self.lowerThreshSpinbox.value(), upperThresh)

    def overlayInvertPushed(self):
        self.signalOverlayUpperThreshChange.emit(
            self.lowerThreshSpinbox.value(), self.upperThreshSpinbox.value())

    def overlayAlphaSliderChanged(self, value):
        self.overlayAlphaSpinbox.setValue(float(value) * self.alphaSpinboxStep)

    def overlayAlphaSpinBoxChanged(self, value):
        sliderVal = int(value / self.alphaSpinboxStep)
        self.blockedSetValue(self.overlayAlphaSlider, sliderVal)
        self.signalOverlayAlphaChange.emit(value)

    def movieIntervalSliderChanged(self, Interval):
        self.movieIntervalSpinbox.setValue(
            float(Interval) / self.numberOfStepsBetweenMovieSliderIntegers)

    def movieIntervalSpinBoxChanged(self, Interval):
        interval = Interval  # 1.0 / Fps * 1e3 # in ms
        self.movieIntervalSlider.blockSignals(True)
        self.blockedSetValue(self.movieIntervalSlider, int(
            Interval * self.numberOfStepsBetweenMovieSliderIntegers))
        self.signalMovieIntervalChange.emit(interval)

    def movieGotoFrame(self):
        frame = self.movieFrameSpinbox.value()
        self.signalMovieGotoFrame.emit(frame)

    def moviePause(self):
        self.signalMoviePause.emit()
