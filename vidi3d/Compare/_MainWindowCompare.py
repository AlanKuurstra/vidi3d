"""
Sets up the main window for the 2d viewer. This includes creating MpImage, MpPlot,
ControlWidget2D.  Also connections are made between QT signals sent by other
classes and functions within this class.
"""
import numpy as np
from PyQt4 import QtCore, QtGui
from .. import _Core as _Core
from .._NavigatorToolbar import NavigationToolbar
from .. import _MplImage as _MplImage
from .. import _MplPlot as _MplPlot
from .. import _DisplayDefinitions as dd
import _ControlWidgetCompare
import matplotlib.pyplot as plt
from matplotlib import path
import matplotlib.animation as animation

#============================================================================
# this matplotlib hack allows text outisde axes bbox to be redrawn during
# animation


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
            # change here
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(
                a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        # ax.figure.canvas.blit(ax.bbox)
        ax.figure.canvas.blit(ax.figure.bbox)


import matplotlib
matplotlib.animation.Animation._blit_draw = _blit_draw
#============================================================================


class _MainWindow(QtGui.QMainWindow):
    def __init__(self, complexImList, pixdim=None, interpolation='bicubic', origin='lower', subplotTitles=None, locationLabels=None, maxNumInRow=None, colormapList=[None, ], overlayList=[None, ], overlayColormapList=[None, ]):
        _Core._create_qApp()
        super(_MainWindow, self).__init__()
        self.setWindowTitle('Compare Viewer')
        self.viewerNumber = 0

        def matchListOfLength1toList2Length(listOfLength1, list2):
            if len(listOfLength1) == 1 and len(list2) > 1:
                tmp = []
                for indx in range(len(list2)):
                    tmp.append(listOfLength1[0])
                listOfLength1 = tmp
            return listOfLength1
        overlayList = matchListOfLength1toList2Length(
            overlayList, complexImList)
        self.overlayList = overlayList
        overlayUsed = False
        overlayMinMax = [-np.finfo('float').eps, np.finfo('float').eps]
        for overlay in overlayList:
            if overlay is not None:
                overlayUsed = True
                currentOverlayMin = overlay.min()
                currentOverlayMax = overlay.max()
                if currentOverlayMin < overlayMinMax[0]:
                    overlayMinMax[0] = currentOverlayMin
                if currentOverlayMax > overlayMinMax[1]:
                    overlayMinMax[1] = currentOverlayMax

        complexImList = matchListOfLength1toList2Length(
            complexImList, overlayList)
        colormapList = matchListOfLength1toList2Length(
            colormapList, complexImList)
        overlayColormapList = matchListOfLength1toList2Length(
            overlayColormapList, overlayList)
        self.complexImList = complexImList
        numImages = len(complexImList)
        complexIm = complexImList[0]

        # initLocation=[int(complexIm.shape[0]/2),int(complexIm.shape[1]/2)]
        self.loc = [int(complexIm.shape[0] / 2),
                    int(complexIm.shape[1] / 2), int(complexIm.shape[2] / 2), 0]
        # initLocation=self.loc

        imageType = dd.ImageType.mag
        if pixdim != None:
            aspect = np.float(pixdim[1]) / pixdim[0]
        else:
            aspect = 'equal'
        self.pixdim = pixdim

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
        self.controls = _ControlWidgetCompare._ControlWidgetCompare(imgShape=complexIm.shape, location=self.loc, imageType=imageType, locationLabels=locationLabels, imgVals=zip(
            subplotTitles, np.zeros(len(subplotTitles))), overlayUsed=overlayUsed, overlayMinMax=overlayMinMax, parent=self)
        if not overlayUsed:
            self.controls.overlayThresholdWidget.setEnabled(False)
        #
        # Set up image panels
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
                self.imagePanelsList.append(_MplImageSlice(complexImage=self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]], aspect=aspect, sliceNum=self.loc[2], maxSliceNum=complexIm.shape[2], interpolation=interpolation, origin=origin,
                                                           location=self.loc[:2], imageType=imageType, locationLabels=labels, colormap=colormapList[imIndex], parent=self, overlay=overlayList[imIndex][:, :, self.loc[2]], overlayColormap=overlayColormapList[imIndex]))
            else:
                self.imagePanelsList.append(_MplImageSlice(complexImage=self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]], aspect=aspect, sliceNum=self.loc[2], maxSliceNum=complexIm.shape[
                                            2], interpolation=interpolation, origin=origin, location=self.loc[:2], imageType=imageType, locationLabels=labels, colormap=colormapList[imIndex], parent=self))
            self.imagePanelToolbarsList.append(NavigationToolbar(
                self.imagePanelsList[imIndex], self.imagePanelsList[imIndex], imIndex))
            self.imagePanelsList[-1].NavigationToolbar = self.imagePanelToolbarsList[-1]
        """
        # Synchronize the starting window/leveling to agree with the first panel        
        for imIndex in range(1,numImages):            
            self.imagePanelsList[imIndex].intensityLevelCache=self.imagePanelsList[0].intensityLevelCache
            self.imagePanelsList[imIndex].intensityWindowCache=self.imagePanelsList[0].intensityWindowCache
        self.ChangeWindowLevel(self.imagePanelsList[0].intensityWindowCache[imageType],self.imagePanelsList[0].intensityLevelCache[imageType])
        """
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
        numFrames = complexImList[0].shape[-1]
        initFPS = self.controls.movieFpsSpinbox.value()
        initInterval = 1.0 / initFPS * 1e3
        self.moviePlayer = animation.FuncAnimation(self.imagePanelsList[0].fig, self.movieUpdate, frames=range(
            numFrames), interval=initInterval, blit=True, repeat_delay=0)

        #
        # Set up plots
        #
        self.plotsPanel = QtGui.QWidget(self)
        #self.xPlotPanel=_MplPlot._MplPlot(complexData=complexIm[:,initLocation[1],self.loc[2],:], title=locationLabels[0], dataType=imageType,colors=colors,initMarkerPosn=initLocation[1])
        #self.yPlotPanel=_MplPlot._MplPlot(complexData=complexIm[initLocation[0],:,self.loc[2],:], title=locationLabels[1], dataType=imageType,colors=colors,initMarkerPosn=initLocation[0])
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
        # Connect from controls
        self.controls.signalImageTypeChange.connect(self.ChangeImageType)
        self.controls.signalLocationChange.connect(self.ChangeLocation)
        self.controls.signalZLocationChange.connect(self.onZChange)
        self.controls.signalWindowLevelChange.connect(self.ChangeWindowLevel)
        self.controls.signalWindowLevelReset.connect(
            self.SetWindowLevelToDefault)
        self.controls.signalTLocationChange.connect(self.onTChange)
        self.controls.signalROIClear.connect(self.clearROI)
        self.controls.signalROIAvgTimecourse.connect(self.plotROIAvgTimeseries)
        self.controls.signalROI1VolHistogram.connect(self.plotROI1VolHistogram)
        self.controls.signalMovieIntervalChange.connect(
            self.changeMovieInterval)

        self.controls.signalOverlayLowerThreshChange.connect(
            self.thresholdOverlay)
        self.controls.signalOverlayUpperThreshChange.connect(
            self.thresholdOverlay)
        self.controls.signalMovieGotoFrame.connect(
            self.movieGotoFrame)

        # connect all z changes to each other
        for imagePanel in self.imagePanelsList:
            imagePanel.signalZLocationChange.connect(self.onZChange)

        # Connect from imagePanel
        for currImagePanel in self.imagePanelsList:
            currImagePanel.signalLocationChange.connect(self.ChangeLocation)
            currImagePanel.signalWindowLevelChange.connect(
                self.ChangeWindowLevel)

        # Connect from imagePanel toolbars
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

    def getCurrentSlice(self):
        return self.loc[2]

    def ChangeImageType(self, imageType):
        self.controls.SetImageType(imageType)
        self.xPlotPanel.showDataTypeChange(imageType)
        self.yPlotPanel.showDataTypeChange(imageType)
        self.zPlotPanel.showDataTypeChange(imageType)
        self.tPlotPanel.showDataTypeChange(imageType)

        for currImagePanel in self.imagePanelsList:
            currImagePanel.showImageTypeChange(imageType)

    def ChangeWindowLevel(self, newIntensityWindow, newIntensityLevel):
        self.controls.ChangeWindowLevel(newIntensityWindow, newIntensityLevel)
        numImages = len(self.imagePanelsList)
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showWindowLevelChange(
                newIntensityWindow, newIntensityLevel)

    def SetWindowLevelToDefault(self):
        self.controls.ChangeWindowLevel(0, 0)

        for currImagePanel in self.imagePanelsList:
            currImagePanel.showSetWindowLevelToDefault()

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

    def ChangeLocation(self, x, y):
        self.loc[:2] = [x, y]
        self.controls.ChangeLocation(x, y)
        self.updatePlots()
        numImages = len(self.imagePanelsList)
        imgVals = []
        for imIndex in range(numImages):
            # if not self.imagePanelToolbarsList[imIndex]._movieActive:
            self.imagePanelsList[imIndex].showLocationChange([x, y])
            imgVals.append(self.imagePanelsList[imIndex].locationVal)
        self.controls.ChangeImgVals(imgVals)

    def keyPressEvent(self, event):
        # print event.text() #this one can tell when shift is being held down
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

    def setViewerNumber(self, number):
        self.viewerNumber = number

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
            imagePanel.sliceNum = newz
        for imgIndx in range(len(self.imagePanelsList)):
            # if self.overlayList[imgIndx] is not None:
            #    self.imagePanelsList[imgIndx].showComplexImageAndOverlayChange(self.complexImList[imgIndx][:,:,self.loc[2],self.loc[3]],self.overlayList[imgIndx][:,:,self.loc[2]])
            # else:
            #    self.imagePanelsList[imgIndx].showComplexImageChange(self.complexImList[imgIndx][:,:,self.loc[2],self.loc[3]])
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

    def updateROI(self, x, y):
        currentROIverts = self.ROIData.verts[self.loc[2]][-1]
        currentROIverts.append((x, y))
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            # self.canvas.restore_region(self.background)
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
            # self.canvas.restore_region(self.background)
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

    def displayROI(self):
        mask = self.getROIMask()
        data = (self.complexIm[..., 0], mask[..., np.newaxis])
        concat = np.empty(data[0].shape + (len(data),), dtype='complex')
        for i in range(len(data)):
            concat[:, :, :, :, i] = data[i]
        data = concat
        viewer = _MainWindow(data, pixdim=self.pixdim, interpolation='none')

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
                avgTimeseries = avgTimeseries + np.finfo(float).eps
                avgTimeseries = (
                    avgTimeseries - avgTimeseries[0]) / avgTimeseries[0] * 100
                if fig == None:
                    fig = plt.figure()
                plt.plot(
                    avgTimeseries, dd.PlotColours.colours[index], label=self.subplotTitles[index])
        plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Average Signal")

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
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:
                z = self.loc[2]
                if z in currimagePanelToolbar.roiLines.mplLineObjects:
                    for currentLine in currimagePanelToolbar.roiLines.mplLineObjects[z]:
                        currimagePanelToolbar.ax.lines.remove(currentLine)
            currimagePanelToolbar.roiLines.mplLineObjects = {}
            currimagePanelToolbar.canvas.draw()
            currimagePanelToolbar.canvas.blit(currimagePanelToolbar.ax.bbox)

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

    def movieUpdate(self, frame):
        z = self.loc[2]
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
            self.moviePlayer.event_source.start()
        self.imagePanelToolbarsList[imgIndex].parent.signalLocationChange.disconnect(
            self.ChangeLocation)

    def destructMovie(self, imgIndex):
        atLeastOneActive = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._movieActive:
                atLeastOneActive = True
        if not atLeastOneActive:
            self.controls.movieWidget.setEnabled(False)
            self.moviePlayer.event_source.stop()
        self.imagePanelToolbarsList[imgIndex].parent.signalLocationChange.connect(
            self.ChangeLocation)        
        self.imagePanelsList[imgIndex].showComplexImageChange(
                self.complexImList[imgIndex][:, :, self.loc[2], self.loc[3]])

    def changeMovieInterval(self, interval):
        self.moviePlayer.event_source.interval = interval
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
class roiData():
    def __init__(self):
        self.verts = {}

    def startNewLassoData(self, x, y, z):
        if z in self.verts:
            self.verts[z].append([(x, y), ])
        else:
            self.verts[z] = [[(x, y), ], ]


class _MplImageSlice(_MplImage._MplImage):
    def __init__(self, sliceNum=0, maxSliceNum=0, *args, **keywords):
        super(_MplImageSlice, self).__init__(*args, **keywords)
        self.sliceNum = sliceNum
        self.maxSliceNum = maxSliceNum

    def wheelEvent(self, event):
        if event.delta() > 0:
            clipVal = np.minimum(np.maximum(
                self.sliceNum + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.sliceNum - 1, 0), self.maxSliceNum - 1)
        self.signalZLocationChange.emit(clipVal)
