"""
Sets up the main window for the compare viewer. Creates MplImage, MplPlot, 
and a ControlWidget objects and connects their Qt Signals to local functions.
"""
import numpy as np
from PyQt4 import QtCore, QtGui
from .. import _Core as _Core
from .._NavigationToolbar import NavigationToolbar
from .. import _MplImage as _MplImage
from .. import _MplPlot as _MplPlot
from .. import _DisplayDefinitions as dd
import _ControlWidgetCompare
import matplotlib.pyplot as plt
from matplotlib import path
import matplotlib.animation as animation

class _MainWindow(QtGui.QMainWindow):
    def __init__(self, complexImList, pixdim=None, interpolation='bicubic', origin='lower', subplotTitles=None, locationLabels=None, maxNumInRow=None, colormapList=[None, ], overlayList=[None, ], overlayColormapList=[None, ]):
        _Core._create_qApp()
        super(_MainWindow, self).__init__()
        self.setWindowTitle('Compare Viewer')
        self.viewerNumber = 0
        
        #
        #'Broadcast' input lists of different lengths
        #
        def matchListOfLength1toSecondListsLength(listOfLength1, list2):
            if len(listOfLength1) == 1 and len(list2) > 1:
                tmp = []
                for indx in range(len(list2)):
                    tmp.append(listOfLength1[0])
                listOfLength1 = tmp
            return listOfLength1
        self.overlayList = matchListOfLength1toSecondListsLength(
            overlayList, complexImList)
        del overlayList
        overlayUsed = False
        overlayMinMax = [-np.finfo('float').eps, np.finfo('float').eps]
        for overlay in self.overlayList:
            if overlay is not None:
                overlayUsed = True
                currentOverlayMin = overlay.min()
                currentOverlayMax = overlay.max()
                if currentOverlayMin < overlayMinMax[0]:
                    overlayMinMax[0] = currentOverlayMin
                if currentOverlayMax > overlayMinMax[1]:
                    overlayMinMax[1] = currentOverlayMax
        
        self.complexImList = matchListOfLength1toSecondListsLength(
            complexImList, self.overlayList)        
        colormapList = matchListOfLength1toSecondListsLength(
            colormapList, self.complexImList)
        overlayColormapList = matchListOfLength1toSecondListsLength(
            overlayColormapList, self.overlayList)
        
        #
        # a few image parameters
        #        
        numImages = len(self.complexImList)
        complexImShape = self.complexImList[0].shape 
        imageType = dd.ImageType.mag
        if pixdim != None:
            aspect = np.float(pixdim[1]) / pixdim[0]
        else:
            aspect = 'equal'
        self.pixdim = pixdim
        
        #
        # intial cursor location
        # 
        self.loc = [int(complexImShape[0] / 2),
                    int(complexImShape[1] / 2), int(complexImShape[2] / 2), 0]        

        #
        # give each image a label
        #
        if type(subplotTitles) is tuple:
            subplotTitles = list(subplotTitles)
        if type(subplotTitles) is list and len(subplotTitles) == 1:
            subplotTitles = subplotTitles[0]
        elif type(subplotTitles) is list and len(subplotTitles) != numImages:
            subplotTitles = None
        if numImages == 1 and subplotTitles is None:
            subplotTitles = [""]
        elif numImages == 1 and type(subplotTitles) is str:
            subplotTitles = [subplotTitles]
        elif numImages > 1 and type(subplotTitles) is str:
            prefix = subplotTitles
            subplotTitles = []
            for imIndex in range(numImages):
                subplotTitles.append(prefix + str(imIndex))
        elif numImages > 1 and type(subplotTitles) is list:
            pass
        else:
            subplotTitles = []
            for imIndex in range(numImages):
                subplotTitles.append("Image " + str(imIndex))
        self.subplotTitles = subplotTitles

        #
        # Set up Controls
        #
        self.controls = _ControlWidgetCompare._ControlWidgetCompare(imgShape=complexImShape, location=self.loc, imageType=imageType, locationLabels=locationLabels, imgVals=zip(
            subplotTitles, np.zeros(len(subplotTitles))), overlayUsed=overlayUsed, overlayMinMax=overlayMinMax, parent=self)
        if not overlayUsed:
            self.controls.overlayThresholdWidget.setEnabled(False)
        #
        # Set up image panels and toolbars
        #
        self.imagePanels = QtGui.QWidget(self)
        colors = dd.PlotColours.colours
        self.imagePanelsList = []
        self.imagePanelToolbarsList = []
        if locationLabels is None:
            locationLabels = ["X", "Y", "Z", "T"]
        for imIndex in range(numImages):
            labels = [{'color': 'r', 'textLabel': locationLabels[0]}, {'color': 'b', 'textLabel': locationLabels[1]}, {
                'color': colors[imIndex], 'textLabel': subplotTitles[imIndex]}]
            if self.overlayList[imIndex] is not None:
                self.imagePanelsList.append(_MplImageSlice(complexImage=self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]], aspect=aspect, imgSliceNumber=self.loc[2], maxSliceNum=complexImShape[2], interpolation=interpolation, origin=origin,
                                                           location=self.loc[:2], imageType=imageType, locationLabels=labels, colormap=colormapList[imIndex], parent=self, overlay=self.overlayList[imIndex][:, :, self.loc[2]], overlayColormap=overlayColormapList[imIndex]))
            else:
                self.imagePanelsList.append(_MplImageSlice(complexImage=self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]], aspect=aspect, imgSliceNumber=self.loc[2], maxSliceNum=complexImShape[
                                            2], interpolation=interpolation, origin=origin, location=self.loc[:2], imageType=imageType, locationLabels=labels, colormap=colormapList[imIndex], parent=self))
            self.imagePanelToolbarsList.append(NavigationToolbar(
                self.imagePanelsList[imIndex], self.imagePanelsList[imIndex], imIndex))
            self.imagePanelsList[-1].NavigationToolbar = self.imagePanelToolbarsList[-1]
        #
        #Layout image panels in a grid
        #
        self.imLayout = QtGui.QGridLayout()
        imLayout = self.imLayout
        if maxNumInRow is None:
            maxNumInRow = int(np.sqrt(numImages) + 1 - 1e-10)
        for imIndex in range(numImages):
            imLayout.addWidget(self.imagePanelToolbarsList[imIndex], 2 * np.floor(
                imIndex / maxNumInRow), imIndex % maxNumInRow)
            imLayout.addWidget(self.imagePanelsList[imIndex], 2 * np.floor(
                imIndex / maxNumInRow) + 1, imIndex % maxNumInRow)
        self.imagePanels.setLayout(imLayout)

        #
        # Set up ROI
        #
        self.ROIData = roiData()

        #
        # Set up Movie
        #
        numFrames = self.complexImList[0].shape[-1]
        initInterval = self.controls.movieIntervalSpinbox.value()
        #initInterval = initFPS#1.0 / initFPS * 1e3
        self.moviePlayer = FuncAnimationCustom(self.imagePanelsList[0].fig, self.movieUpdate, frames=range(
            numFrames), interval=initInterval, blit=True, repeat_delay=0)               
        self.currentMovieFrame=0        
        

        #
        # Set up plots
        #
        self.plotsPanel = QtGui.QWidget(self)        
        xPlotDataList = []
        yPlotDataList = []
        zPlotDataList = []
        tPlotDataList = []
        for img in self.complexImList:
            xPlotDataList.append(img[:, self.loc[1], self.loc[2], self.loc[3]])
            yPlotDataList.append(img[self.loc[0], :, self.loc[2], self.loc[3]])
            zPlotDataList.append(img[self.loc[0], self.loc[1], :, self.loc[3]])
            tPlotDataList.append(img[self.loc[0], self.loc[1], self.loc[2], :])
        self.xPlotPanel = _MplPlot._MplPlot(
            complexDataList=xPlotDataList, title=locationLabels[0], dataType=imageType, colors=colors, initMarkerPosn=self.loc[1])
        self.yPlotPanel = _MplPlot._MplPlot(
            complexDataList=yPlotDataList, title=locationLabels[1], dataType=imageType, colors=colors, initMarkerPosn=self.loc[0])
        self.zPlotPanel = _MplPlot._MplPlot(
            complexDataList=zPlotDataList, title=locationLabels[2], dataType=imageType, colors=colors, initMarkerPosn=self.loc[2])
        self.tPlotPanel = _MplPlot._MplPlot(
            complexDataList=tPlotDataList, title=locationLabels[3], dataType=imageType, colors=colors, initMarkerPosn=self.loc[3])
        plotsLayout = QtGui.QVBoxLayout()
        plotsLayout.addWidget(self.xPlotPanel)
        plotsLayout.addWidget(self.yPlotPanel)
        plotsLayout.addWidget(self.zPlotPanel)
        plotsLayout.addWidget(self.tPlotPanel)
        self.plotsPanel.setLayout(plotsLayout)

        # make each section resizeable using a splitter
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter = self.splitter
        splitter.addWidget(self.controls)
        splitter.addWidget(self.imagePanels)
        splitter.addWidget(self.plotsPanel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)

        # used when inheriting from QMainWindow
        self.setCentralWidget(splitter)
        # self.statusBar().showMessage('Ready')

        self.makeConnections()        
        
        self.show()
        self.setFocus()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        

    def makeConnections(self):
        # Connect signals from controls
        self.controls.signalImageTypeChange.connect(self.ChangeImageType)
        self.controls.signalLocationChange.connect(self.ChangeLocation)
        self.controls.signalZLocationChange.connect(self.onZChange)
        self.controls.signalWindowLevelChange.connect(self.ChangeWindowLevel)
        self.controls.signalWindowLevelReset.connect(
            self.SetWindowLevelToDefault)
        self.controls.signalTLocationChange.connect(self.onTChange)
        self.controls.signalROIClear.connect(self.clearROI)
        self.controls.signalROIDeleteLast.connect(self.deleteLastROI)
        self.controls.signalROIAvgTimecourse.connect(self.plotROIAvgTimeseries)
        self.controls.signalROIPSCTimecourse.connect(self.plotROIPSCTimeseries)
        self.controls.signalROI1VolHistogram.connect(self.plotROI1VolHistogram)
        self.controls.signalMovieIntervalChange.connect(
            self.changeMovieInterval)
        self.controls.signalMoviePause.connect(self.pauseMovie)
        self.controls.signalOverlayLowerThreshChange.connect(
            self.thresholdOverlay)
        self.controls.signalOverlayUpperThreshChange.connect(
            self.thresholdOverlay)
        self.controls.signalMovieGotoFrame.connect(
            self.movieGotoFrame)

        # Connect signals from imagePanel
        for currImagePanel in self.imagePanelsList:
            currImagePanel.signalLocationChange.connect(self.ChangeLocation)
            currImagePanel.signalWindowLevelChange.connect(
                self.ChangeWindowLevel)
            currImagePanel.signalZLocationChange.connect(self.onZChange)

        # Connect signals from imagePanel toolbars
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            currimagePanelToolbar.signalROIInit.connect(self.initializeROI)
            currimagePanelToolbar.signalROIDestruct.connect(self.destructROI)
            currimagePanelToolbar.signalROIStart.connect(self.startNewROI)
            currimagePanelToolbar.signalROIChange.connect(self.updateROI)
            currimagePanelToolbar.signalROIEnd.connect(self.endROI)
            currimagePanelToolbar.signalROICancel.connect(self.cancelROI)
            currimagePanelToolbar.signalMovieInit.connect(self.initializeMovie)
            currimagePanelToolbar.signalMovieDestruct.connect(
                self.destructMovie)

    def setViewerNumber(self, number):
        self.viewerNumber = number
        
    #==================================================================
    # slots dealing with image appearance
    #==================================================================
        
    def ChangeImageType(self, imageType):
        self.controls.SetImageType(imageType)
        self.xPlotPanel.showDataTypeChange(imageType)
        self.yPlotPanel.showDataTypeChange(imageType)
        self.zPlotPanel.showDataTypeChange(imageType)
        self.tPlotPanel.showDataTypeChange(imageType)

        for currImagePanel in self.imagePanelsList:
            currImagePanel.showImageTypeChange(imageType)

    def keyPressEvent(self, event):        
        key = event.key()
        if key == 77:
            self.ChangeImageType(dd.ImageType.mag)
        elif key == 80:
            self.ChangeImageType(dd.ImageType.phase)
        elif key == 82:
            self.ChangeImageType(dd.ImageType.real)
        elif key == 73:
            self.ChangeImageType(dd.ImageType.imag)
        event.ignore()
        
    def ChangeWindowLevel(self, newIntensityWindow, newIntensityLevel):
        self.controls.ChangeWindowLevel(newIntensityWindow, newIntensityLevel)        
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showWindowLevelChange(
                newIntensityWindow, newIntensityLevel)

    def SetWindowLevelToDefault(self):
        self.controls.ChangeWindowLevel(0, 0)
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showSetWindowLevelToDefault()    
    
    #==================================================================
    # slots dealing with a location change
    #==================================================================    
    def ChangeLocation(self, x, y):
        self.loc[:2] = [x, y]
        self.controls.ChangeLocation(x, y)
        self.updatePlots()
        numImages = len(self.imagePanelsList)
        imgVals = []
        for imIndex in range(numImages):            
            self.imagePanelsList[imIndex].showLocationChange([x, y])
            imgVals.append(self.imagePanelsList[imIndex].locationVal)
        self.controls.ChangeImgVals(imgVals)
        
    def onZChange(self, newz):
        prevz = self.loc[2]
        self.loc[2] = newz
        self.controls.ChangeZLocation(newz)

        drawingEngaged = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar.roiDrawingEngaged:
                drawingEngaged = True
                currimagePanelToolbar.roiDrawingEngaged = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:
                if prevz in currimagePanelToolbar.roiLines.mplLineObjects:
                    for currentLine in currimagePanelToolbar.roiLines.mplLineObjects[prevz]:
                        currimagePanelToolbar.ax.lines.remove(currentLine)
            if drawingEngaged:
                currimagePanelToolbar.roiLines.mplLineObjects[prevz].pop()

        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:
                if newz in currimagePanelToolbar.roiLines.mplLineObjects:
                    for currentLine in currimagePanelToolbar.roiLines.mplLineObjects[newz]:
                        currimagePanelToolbar.ax.add_line(currentLine)

        for imagePanel in self.imagePanelsList:
            imagePanel.setImgSliceNumber(newz)
        for imgIndx in range(len(self.imagePanelsList)):
            self.imagePanelsList[imgIndx].showComplexImageChange(
                self.complexImList[imgIndx][:, :, self.loc[2], self.loc[3]])
            self.thresholdOverlay(self.controls.lowerThreshSpinbox.value(
            ), self.controls.upperThreshSpinbox.value())
        self.updatePlots()

    def onTChange(self, value):
        # clip to valid locations?
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)
        self.loc[3] = value
        for imIndex in range(len(self.imagePanelsList)):
            self.imagePanelsList[imIndex].showComplexImageChange(
                self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]])
        self.updatePlots()
        
    def updatePlots(self):
        xPlotDataList = []
        yPlotDataList = []
        zPlotDataList = []
        tPlotDataList = []
        for img in self.complexImList:
            xPlotDataList.append(img[:, self.loc[1], self.loc[2], self.loc[3]])
            yPlotDataList.append(img[self.loc[0], :, self.loc[2], self.loc[3]])
            zPlotDataList.append(img[self.loc[0], self.loc[1], :, self.loc[3]])
            tPlotDataList.append(img[self.loc[0], self.loc[1], self.loc[2], :])

        self.xPlotPanel.showComplexDataAndMarkersChange(
            xPlotDataList, self.loc[0])
        self.yPlotPanel.showComplexDataAndMarkersChange(
            yPlotDataList, self.loc[1])
        self.zPlotPanel.showComplexDataAndMarkersChange(
            zPlotDataList, self.loc[2])
        self.tPlotPanel.showComplexDataAndMarkersChange(
            tPlotDataList, self.loc[3])       
    
    #==================================================================
    # slots for ROI tool
    #==================================================================
    def initializeROI(self, imgIndex):
        self.controls.roiAnalysisWidget.setEnabled(True)
        self.imagePanelToolbarsList[imgIndex].parent.signalLocationChange.disconnect(
            self.ChangeLocation)

    def destructROI(self, imgIndex):
        atLeastOneActive = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:
                atLeastOneActive = True
        if not atLeastOneActive:
            self.controls.roiAnalysisWidget.setEnabled(False)
        self.imagePanelToolbarsList[imgIndex].parent.signalLocationChange.connect(
            self.ChangeLocation)
        
    def updateROI(self, x, y):
        currentROIverts = self.ROIData.verts[self.loc[2]][-1]
        currentROIverts.append((x, y))
        for currimagePanelToolbar in self.imagePanelToolbarsList:            
            currentLine = currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]][-1]
            currentLine.set_data(zip(*currentROIverts))
            self.drawROI(currimagePanelToolbar)

    def drawROI(self, imagePanelToolbar):
        if imagePanelToolbar._ROIactive:
                # do we need to draw all these lines?
            for currentLine in imagePanelToolbar.roiLines.mplLineObjects[self.loc[2]]:
                imagePanelToolbar.ax.draw_artist(currentLine)
            imagePanelToolbar.canvas.blit(imagePanelToolbar.ax.bbox)

    def startNewROI(self, x, y):
        self.ROIData.startNewLassoData(x, y, self.loc[2])
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            currimagePanelToolbar.roiLines.startNewLassoLine(x, y, self.loc[2])
            if currimagePanelToolbar._ROIactive:
                currentline = currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]][-1]
                currimagePanelToolbar.ax.add_line(currentline)

    def endROI(self):
        currentROIverts = self.ROIData.verts[self.loc[2]][-1]
        currentROIverts.append(currentROIverts[0])
        for currimagePanelToolbar in self.imagePanelToolbarsList:            
            currentLine = currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]][-1]
            currentLine.set_data(zip(*currentROIverts))
            self.drawROI(currimagePanelToolbar)

    def cancelROI(self):
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            currentline = currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]].pop(
            )
            if currimagePanelToolbar._ROIactive:
                currimagePanelToolbar.ax.lines.remove(currentline)
                currimagePanelToolbar.canvas.draw()
        self.ROIData.verts[self.loc[2]].pop()

    def getROIMask(self):
        mask = np.zeros(self.complexImList[0].shape[:-1], dtype='bool')
        for z in self.ROIData.verts:
            for contour in self.ROIData.verts[z]:
                mypath = path.Path(contour)
                tmp = mypath.contains_points(
                    list(np.ndindex(self.complexImList[0].shape[:2])))
                tmp = tmp.reshape(self.complexImList[0].shape[:2])
                mask[..., z] = np.logical_or(mask[..., z], tmp)
        return mask

    def applyImageType(self, data, imageType):
        if imageType == dd.ImageType.mag:
            data = np.abs(data)
        elif imageType == dd.ImageType.phase:
            data = np.angle(data)
        elif imageType == dd.ImageType.real:
            data = np.real(data)
        elif imageType == dd.ImageType.imag:
            data = np.imag(data)
        return data

    def plotROIAvgTimeseries(self):
        mask = self.getROIMask()
        imageType = self.imagePanelsList[0]._imageType
        fig = None
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar = self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data = self.complexImList[index]
                data = self.applyImageType(data, imageType)
                avgTimeseries = data[mask].mean(axis=0)
                if fig == None:
                    fig = plt.figure()
                plt.plot(
                    avgTimeseries, dd.PlotColours.colours[index], label=self.subplotTitles[index])
        plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Average Signal")
        
    def plotROIPSCTimeseries(self):
        mask = self.getROIMask()
        imageType = self.imagePanelsList[0]._imageType
        fig = None
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar = self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data = self.complexImList[index]
                data = self.applyImageType(data, imageType)
                pscTimeseries = data[mask].mean(axis=0)
                pscTimeseries = pscTimeseries + np.finfo(float).eps
                pscTimeseries = (
                    pscTimeseries - pscTimeseries[0]) / pscTimeseries[0] * 100
                if fig == None:
                    fig = plt.figure()
                plt.plot(
                    pscTimeseries, dd.PlotColours.colours[index], label=self.subplotTitles[index])
        plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Percent Signal Change")

    def plotROI1VolHistogram(self, numBins):
        mask = self.getROIMask()
        imageType = self.imagePanelsList[0]._imageType
        dataList = []
        colorList = []
        labelList = []
        fig = False
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar = self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data = self.complexImList[index]
                data = self.applyImageType(data, imageType)
                dataList.append(data[..., self.loc[3]][mask])
                colorList.append(dd.PlotColours.colours[index])
                labelList.append(self.subplotTitles[index])
                #y,binEdges,_=plt.hist(data[...,self.loc[3]][mask],bins=numBins,color=dd.PlotColours.colours[index], alpha=0.04)
                #bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
                #plt.plot(bincenters,y,'-',marker="s",color=dd.PlotColours.colours[index], label=self.subplotTitles[index])
                fig = True
        if fig:
            plt.figure()
            plt.hist(dataList, bins=numBins, color=colorList, label=labelList)
            plt.legend()

    def clearROI(self):
        self.ROIData.verts = {}
        z = self.loc[2]
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:                
                if z in currimagePanelToolbar.roiLines.mplLineObjects:
                    for currentLine in currimagePanelToolbar.roiLines.mplLineObjects[z]:
                        currimagePanelToolbar.ax.lines.remove(currentLine)
            currimagePanelToolbar.roiLines.mplLineObjects = {}
            currimagePanelToolbar.canvas.draw()
            currimagePanelToolbar.canvas.blit(currimagePanelToolbar.ax.bbox)
        
    def deleteLastROI(self):
        z = self.loc[2]
        self.ROIData.verts[z].pop()
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:                
                if z in currimagePanelToolbar.roiLines.mplLineObjects:
                    currentLine = currimagePanelToolbar.roiLines.mplLineObjects[z][-1]
                    currimagePanelToolbar.ax.lines.remove(currentLine)
            currimagePanelToolbar.roiLines.mplLineObjects[z].pop()
            currimagePanelToolbar.canvas.draw()
            currimagePanelToolbar.canvas.blit(currimagePanelToolbar.ax.bbox)


    #==================================================================
    # slots for overlay thresholding
    #==================================================================
    def thresholdOverlay(self, lowerThresh, upperThresh):
        for imgIndx in range(len(self.imagePanelsList)):
            if self.overlayList[imgIndx] is not None:
                overlay = self.overlayList[imgIndx][:, :, self.loc[2]]
                lowerThreshMask = overlay >= lowerThresh
                upperThreshMask = overlay <= upperThresh
                mask = (lowerThreshMask * upperThreshMask).astype('bool')
                thresholded = np.ma.masked_where(mask, overlay)
                self.imagePanelsList[imgIndx].setOverlayImage(thresholded)
                self.imagePanelsList[imgIndx].BlitImageAndLines()

    #==================================================================
    # slots for movie tool
    #==================================================================    
    def movieUpdate(self, frame):                
        z = self.loc[2]
        self.currentMovieFrame=frame
        imageType = self.imagePanelsList[0]._imageType
        artistsToUpdate = []
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar = self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._movieActive:
                newData = self.applyImageType(
                    self.complexImList[index][..., z, frame].T, imageType)
                currimagePanelToolbar.movieText.set_text(
                    "frame: " + str(frame))
                self.imagePanelsList[index].img.set_data(newData)
                artistsToUpdate.append(currimagePanelToolbar.movieText)
                artistsToUpdate.append(self.imagePanelsList[index].img)
        return artistsToUpdate    

    def initializeMovie(self, imgIndex):
        numActive = 0
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._movieActive:
                numActive += 1
        if numActive == 1:
            self.controls.movieWidget.setEnabled(True)            
            self.controls.moviePauseButton.setChecked(False)
            self.moviePlayer.moviePaused=False
            if not self.moviePlayer.moviePaused:
                self.moviePlayer.event_source.start()
        self.imagePanelToolbarsList[imgIndex].parent.signalLocationChange.disconnect(
            self.ChangeLocation)
        self.imagePanelsList[imgIndex].overlay.set_visible(False)
        artistsToUpdate=self.movieUpdate(self.currentMovieFrame)
        #self.imagePanelsList[imgIndex].BlitImageAndLines()        
        self.moviePlayer._blit_draw(artistsToUpdate,self.moviePlayer._blit_cache)        

    def destructMovie(self, imgIndex):
        atLeastOneActive = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._movieActive:
                atLeastOneActive = True
        if not atLeastOneActive:
            self.controls.movieWidget.setEnabled(False)
            self.moviePlayer.event_source.stop()
            self.moviePlayer.moviePaused=True
        self.imagePanelToolbarsList[imgIndex].parent.signalLocationChange.connect(
            self.ChangeLocation)
        self.imagePanelsList[imgIndex].overlay.set_visible(True)        
        self.imagePanelsList[imgIndex].showComplexImageChange(
                self.complexImList[imgIndex][:, :, self.loc[2], self.loc[3]])

    def changeMovieInterval(self, interval):        
        self.moviePlayer.event_source.interval = interval
        
    def pauseMovie(self):
        self.moviePlayer.moviePaused= self.controls.moviePauseButton.isChecked()
        if self.moviePlayer.moviePaused:
            self.moviePlayer.event_source.stop()
        else:            
            self.moviePlayer.event_source.start()
        
    def movieGotoFrame(self,frame):
        newFrameSeq=self.moviePlayer.new_frame_seq()
        for i in range(frame):
            newFrameSeq.next()
        self.moviePlayer.frame_seq=newFrameSeq 
    
    def closeEvent(self, event):
            self.moviePlayer.event_source.stop()
            if self.viewerNumber:
                del _Core._viewerList[self.viewerNumber]
            event.accept()
 

#==================================================================
# other classes
#================================================================== 
           
class roiData():
    def __init__(self):
        self.verts = {}

    def startNewLassoData(self, x, y, z):
        if z in self.verts:
            self.verts[z].append([(x, y), ])
        else:
            self.verts[z] = [[(x, y), ], ]


class _MplImageSlice(_MplImage._MplImage):
    def __init__(self, maxSliceNum=0, *args, **keywords):
        super(_MplImageSlice, self).__init__(*args, **keywords)        
        self.maxSliceNum = maxSliceNum

    def wheelEvent(self, event):
        if event.delta() > 0:
            clipVal = np.minimum(np.maximum(
                self.getImgSliceNumber() + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.getImgSliceNumber() - 1, 0), self.maxSliceNum - 1)
        self.signalZLocationChange.emit(clipVal)

class FuncAnimationCustom(animation.FuncAnimation):
    def __init__(self, *args, **keywords):        
        animation.FuncAnimation.__init__(self,*args, **keywords)   
        self.moviePaused=True     
    def _start(self, *args):
        '''
        Starts interactive animation. Adds the draw frame command to the GUI
        handler, calls show to start the event loop.
        '''
        # First disconnect our draw event handler
        self._fig.canvas.mpl_disconnect(self._first_draw_id)
        self._first_draw_id = None  # So we can check on save

        # Now do any initial draw
        self._init_draw()

        # Add our callback for stepping the animation and
        # actually start the event_source.
        self.event_source.add_callback(self._step)
        #AK: ADDED A CHECK FOR MOVIE PAUSE
        if not self.moviePaused:
            self.event_source.start()        
    def _end_redraw(self, evt):        
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(None, False)    
        #AK: ADDED A CHECK FOR MOVIE PAUSE
        if not self.moviePaused:            
            self.event_source.start()
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._handle_resize)
    def _blit_draw(self, artists, bg_cache):
        # Handles blitted drawing, which renders only the artists given instead
        # of the entire figure.
        updated_ax = []
        for a in artists:
            # If we haven't cached the background for this axes object, do
            # so now. This might not always be reliable, but it's an attempt
            # to automate the process.
            if a.axes not in bg_cache:
                # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
                #AK: CHANGED SO WE CAN SEE FRAME TEXT BOX REDRAWN
                bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(
                    a.axes.figure.bbox)
            a.axes.draw_artist(a)
            updated_ax.append(a.axes)

        # After rendering all the needed artists, blit each axes individually.
        for ax in set(updated_ax):
            #AK: CHANGED SO WE CAN SEE FRAME TEXT BOX REDRAWN
            # ax.figure.canvas.blit(ax.bbox)
            ax.figure.canvas.blit(ax.figure.bbox)
            
    def _handle_resize(self, *args):
        # On resize, we need to disable the resize event handling so we don't
        # get too many events. Also stop the animation events, so that
        # we're paused. Reset the cache and re-init. Set up an event handler
        # to catch once the draw has actually taken place.
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self.event_source.stop()
        self._blit_cache.clear()
        #AK: REMOVE THIS LINE SO THE FIRST FRAME ISN'T DRAWN WHEN RESIZING
        #self._init_draw()
        self._resize_id = self._fig.canvas.mpl_connect('draw_event',
                                                       self._end_redraw)