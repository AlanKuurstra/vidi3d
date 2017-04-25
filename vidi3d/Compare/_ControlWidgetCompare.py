"""
This class contains the widgets for user control in the 2D viewer.
"""

import numpy as np
from PyQt4 import QtGui, QtCore
from .. import _Core as _Core
from .. import _DisplayDefinitions as dd  

class _ControlWidgetCompare(QtGui.QWidget):
    from .._DisplaySignals import *
    def __init__(self, imgShape=None, location=None, locationLabels=None, imageType=None, windowLevel=None, imgVals=None):
        _Core._create_qApp()        
        QtGui.QWidget.__init__(self)        

        controlLayout=QtGui.QGridLayout(self)
        self.controlLayout=controlLayout
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
                
        label=QtGui.QLabel()
        label.setText("View")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        self.imgType=QtGui.QComboBox()
        self.imgType.addItem("Magnitude")
        self.imgType.addItem("Phase")
        self.imgType.addItem("Real")
        self.imgType.addItem("Imaginary")
        self.imgType.setCurrentIndex(self.imgTypeIndex[self.currImageType])        
        controlLayout.addWidget(self.imgType, layoutRowIndex, 1)        
        layoutRowIndex = layoutRowIndex + 1
        
        #
        # Window/Level
        #           
        self.currWindow=0.0
        self.currLevel=0.0
        self.window=QtGui.QDoubleSpinBox()                
        self.window.setDecimals(3)
        self.window.setMaximum(1.7*10**308)        
        self.window.setMaximumWidth (70) 
        self.level=QtGui.QDoubleSpinBox()                                
        self.level.setDecimals(3)
        self.level.setMaximum(1.7*10**308)
        self.level.setMinimum(-1.7*10**308)        
        self.level.setMaximumWidth (70) 
        label=QtGui.QLabel()
        label.setText("W")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)

        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)        
        controlLayout.addWidget(self.window, layoutRowIndex, 1)        
        layoutRowIndex = layoutRowIndex+1
        
        label=QtGui.QLabel()
        label.setText("L")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.level, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex+1
        
        wlbutton=QtGui.QPushButton("Default W/L")      
        controlLayout.addWidget(wlbutton, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex+1
        
        
        
        #
        # Location    
        #
        self.location = list(np.array(location).copy())
        self.xcontrol=QtGui.QSpinBox()
        self.xcontrol.setMinimum(0)
        self.xcontrol.setMaximum(imgShape[0]-1)
        self.xcontrol.setValue(location[0])
        self.ycontrol=QtGui.QSpinBox()
        self.ycontrol.setMinimum(0)
        self.ycontrol.setMaximum(imgShape[1]-1)
        self.ycontrol.setValue(location[1])
        self.zcontrol=QtGui.QSpinBox()
        self.zcontrol.setMinimum(0)
        self.zcontrol.setMaximum(imgShape[2]-1)
        self.zcontrol.setValue(location[2])
        self.tcontrol=QtGui.QDoubleSpinBox()
        self.tcontrol.setDecimals(0)
        self.tcontrol.setMaximum(imgShape[3]-1)
        self.tcontrol.setValue(0)       
        
                
        if locationLabels is None:
            locationLabels = ["X", "Y","Z","T"]
        
        label=QtGui.QLabel()
        label.setText(locationLabels[0])
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)       
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.xcontrol, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1
        label=QtGui.QLabel()
        label.setText(locationLabels[1])
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.ycontrol, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1
        label=QtGui.QLabel()
        label.setText(locationLabels[2])
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.zcontrol, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1
        label=QtGui.QLabel()
        label.setText(locationLabels[3])
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        controlLayout.addWidget(label, layoutRowIndex, 0, alignment=QtCore.Qt.AlignRight)
        controlLayout.addWidget(self.tcontrol, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1       
 
        #
        # Display Image Values    
        #
        label=QtGui.QLabel()
        label.setText("Image Values")
        controlLayout.addWidget(label,layoutRowIndex,1)
        layoutRowIndex = layoutRowIndex+1
        
        imgValsLayout=QtGui.QGridLayout()
        self.imgValLabels=[]
        if imgVals is not None:
            numImgs=len(imgVals)            
            for imNum in range(numImgs):                
                    label=QtGui.QLabel()
                    label.setText(str(imgVals[imNum][0])+":")
                    imgValsLayout.addWidget(label,imNum,1)
                    label=QtGui.QLabel()
                    label.setText('%.3e'%(imgVals[imNum][1]))
                    self.imgValLabels.append(label)
                    imgValsLayout.addWidget(label,imNum,2)                    
        
        controlLayout.addLayout(imgValsLayout,layoutRowIndex,1)
        layoutRowIndex = layoutRowIndex+1
        
        controlLayout.addWidget(QtGui.QLabel(),layoutRowIndex,0)
        layoutRowIndex = layoutRowIndex+1
        
        #
        #ROI Analysis
        #
        clearROIButton=QtGui.QPushButton("Clear ROI")      
        controlLayout.addWidget(clearROIButton, layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex+1
        roiAvgTimecourseButton=QtGui.QPushButton("Avg Timecourse")      
        controlLayout.addWidget(roiAvgTimecourseButton, layoutRowIndex, 1)        
        layoutRowIndex = layoutRowIndex+1
        roi1VolHistogramButton=QtGui.QPushButton("1 Vol Histogram")      
        controlLayout.addWidget(roi1VolHistogramButton, layoutRowIndex, 1)        
        layoutRowIndex = layoutRowIndex+1
        
        #numBinsWidget=QtGui.QWidget(self)
        numBinsLayout=QtGui.QHBoxLayout()
        label=QtGui.QLabel()
        label.setText("# of Bins")
        label.setFixedWidth(label.fontMetrics().width(label.text())+5)
        numBinsLayout.addWidget(label)
        self.numBins=QtGui.QSpinBox()
        self.numBins.setMinimum(1)
        self.numBins.setValue(10)        
        numBinsLayout.addWidget(self.numBins)
        #numBinsWidget.setLayout(numBinsLayout)
        #controlLayout.addWidget(numBinsWidget,layoutRowIndex, 1)
        controlLayout.addLayout(numBinsLayout,layoutRowIndex, 1)
        layoutRowIndex = layoutRowIndex + 1

        controlLayout.setRowStretch(layoutRowIndex, 10)
        
        QtCore.QObject.connect(self.imgType, QtCore.SIGNAL("currentIndexChanged(int)"), self.ImageTypeChanged)
        QtCore.QObject.connect(self.window, QtCore.SIGNAL("valueChanged(double)"), self.windowChanged)
        QtCore.QObject.connect(self.level, QtCore.SIGNAL("valueChanged(double)"), self.levelChanged)
        QtCore.QObject.connect(wlbutton, QtCore.SIGNAL("clicked()"), self.windowLevelToDefaultPushed)
        
        
        QtCore.QObject.connect(self.xcontrol, QtCore.SIGNAL("valueChanged(int)"), self.xLocationChanged)
        QtCore.QObject.connect(self.ycontrol, QtCore.SIGNAL("valueChanged(int)"), self.yLocationChanged)
        QtCore.QObject.connect(self.zcontrol, QtCore.SIGNAL("valueChanged(int)"), self.zLocationChanged)
        QtCore.QObject.connect(self.tcontrol, QtCore.SIGNAL("valueChanged(double)"), self.changeTcontrol)        
        
        QtCore.QObject.connect(clearROIButton, QtCore.SIGNAL("clicked()"), self.clearROIPushed)
        QtCore.QObject.connect(roiAvgTimecourseButton, QtCore.SIGNAL("clicked()"), self.roiAvgTimecoursePushed)
        QtCore.QObject.connect(roi1VolHistogramButton, QtCore.SIGNAL("clicked()"), self.roi1VolHistogramButtonPushed)
    
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
            self.signalWindowLevelChange.emit(self.currWindow,self.currLevel)
    def levelChanged(self, value):        
        if value != self.currLevel:
            self.currLevel = value            
            self.signalWindowLevelChange.emit(self.currWindow,self.currLevel)
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
                    
    def ChangeWindowLevel(self, newIntensityWindow,newIntensityLevel):
        self.currWindow=newIntensityWindow
        self.currLevel=newIntensityLevel
        self.level.setValue(newIntensityLevel)
        self.window.setValue(newIntensityWindow)
        
    def ChangeImgVals(self,newVals):
        for i in range(len(newVals)):            
            self.imgValLabels[i].setText('%.3e'%(newVals[i]))            
    def changeTcontrol(self,value):
        if self.tcontrol.hasFocus():            
            self.signalTLocationChange.emit(value)    
    def clearROIPushed(self):        
        self.signalROIClear.emit()
    def roiAvgTimecoursePushed(self):        
        self.signalROIAvgTimecourse.emit()
    def roi1VolHistogramButtonPushed(self):
        self.signalROI1VolHistogram.emit(self.numBins.value())
        
        
