"""
Sets up the main window for the compare viewer. Creates MplImage, MplPlot, 
and ControlWidget objects and connects their Qt Signals to local functions.
"""
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore, QtWidgets
from matplotlib import path

from . import controls
from .. import core as _Core
from .. import definitions as dd
from .. import image as _MplImage
from .. import plot as _MplPlot
from ..navigation import NavigationToolbar


class Compare(QtWidgets.QMainWindow):
    def __init__(self,
                 complex_im_list,
                 pixdim=None,
                 interpolation='bicubic',
                 origin='lower',
                 subplot_titles=None,
                 location_labels=None,
                 max_in_row=None,
                 cmaps=[None, ],
                 overlays=[None, ],
                 overlay_cmaps=[None, ]):
        super().__init__()
        self.setWindowTitle('Vidi3d: compare')
        self.viewerNumber = 0

        #
        # 'Broadcast' input lists of different lengths
        #
        def matchListOfLength1toSecondListsLength(listOfLength1, list2):
            if len(listOfLength1) == 1 and len(list2) > 1:
                tmp = []
                for indx in range(len(list2)):
                    tmp.append(listOfLength1[0])
                listOfLength1 = tmp
            return listOfLength1

        self.overlayList = matchListOfLength1toSecondListsLength(
            overlays, complex_im_list)
        overlayUsed = False

        overlayMinMax = [-1, 1]
        for overlay in self.overlayList:
            if overlay is not None:
                overlayUsed = True
                overlayMinMax = [overlay.min(), overlay.max()]
                break
        if overlayUsed:
            for overlay in self.overlayList:
                if overlay is not None:
                    currentOverlayMin = overlay.min()
                    currentOverlayMax = overlay.max()
                    if currentOverlayMin < overlayMinMax[0]:
                        overlayMinMax[0] = currentOverlayMin
                    if currentOverlayMax > overlayMinMax[1]:
                        overlayMinMax[1] = currentOverlayMax

        self.complexImList = matchListOfLength1toSecondListsLength(
            complex_im_list, self.overlayList)
        cmaps = matchListOfLength1toSecondListsLength(
            cmaps, self.complexImList)
        overlay_cmaps = matchListOfLength1toSecondListsLength(
            overlay_cmaps, self.overlayList)

        #
        # a few image parameters
        #
        numImages = len(self.complexImList)
        complexImShape = self.complexImList[0].shape
        imageType = dd.ImageDisplayType.mag
        if pixdim is not None:
            aspect = np.float(pixdim[1]) / pixdim[0]
        else:
            aspect = 'equal'
        self.pixdim = pixdim

        #
        # intial cursor cursor_loc
        #
        self.loc = [int(complexImShape[0] / 2),
                    int(complexImShape[1] / 2), int(complexImShape[2] / 2), 0]

        #
        # give each image a label
        #
        if type(subplot_titles) is tuple:
            subplot_titles = list(subplot_titles)
        if type(subplot_titles) is list and len(subplot_titles) == 1:
            subplot_titles = subplot_titles[0]
        elif type(subplot_titles) is list and len(subplot_titles) != numImages:
            subplot_titles = None
        if numImages == 1 and subplot_titles is None:
            subplot_titles = [""]
        elif numImages == 1 and type(subplot_titles) is str:
            subplot_titles = [subplot_titles]
        elif numImages > 1 and type(subplot_titles) is str:
            prefix = subplot_titles
            subplot_titles = []
            for imIndex in range(numImages):
                subplot_titles.append(prefix + str(imIndex))
        elif numImages > 1 and type(subplot_titles) is list:
            pass
        else:
            subplot_titles = []
            for imIndex in range(numImages):
                subplot_titles.append("Image " + str(imIndex))
        self.subplotTitles = subplot_titles

        #
        # Set up Controls
        #
        self.controls = controls._ControlWidgetCompare(imgShape=complexImShape, location=self.loc, imageType=imageType,
                                                       locationLabels=location_labels, imgVals=list(zip(
                subplot_titles, np.zeros(len(subplot_titles)))), overlayUsed=overlayUsed, overlayMinMax=overlayMinMax,
                                                       parent=self)
        if not overlayUsed:
            self.controls.overlayThresholdWidget.setEnabled(False)
        #
        # Set up image panels and toolbars
        #
        self.imagePanels = QtWidgets.QWidget(self)
        colors = dd.PlotColours.colours
        self.imagePanelsList = []
        self.imagePanelToolbarsList = []
        if location_labels is None:
            location_labels = ["X", "Y", "Z", "T"]
        for imIndex in range(numImages):
            labels = [{'color': 'r', 'textLabel': location_labels[0]}, {'color': 'b', 'textLabel': location_labels[1]}, {
                'color': colors[imIndex], 'textLabel': subplot_titles[imIndex]}]
            if self.overlayList[imIndex] is not None:
                self.imagePanelsList.append(
                    _MplImageSlice(complexImage=self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]],
                                   aspect=aspect,
                                   imgSliceNumber=self.loc[2],
                                   maxSliceNum=complexImShape[2],
                                   interpolation=interpolation,
                                   origin=origin,
                                   location=self.loc[:2],
                                   imageType=imageType,
                                   locationLabels=labels,
                                   colormap=cmaps[imIndex],
                                   parent=self,
                                   overlay=self.overlayList[imIndex][:, :, self.loc[2]],
                                   overlayColormap=overlay_cmaps[imIndex]))
            else:
                self.imagePanelsList.append(
                    _MplImageSlice(complex_image=self.complexImList[imIndex][:, :, self.loc[2], self.loc[3]],
                                   aspect=aspect,
                                   slice_num=self.loc[2],
                                   maxSliceNum=complexImShape[2],
                                   interpolation=interpolation,
                                   origin=origin,
                                   cursor_loc=self.loc[:2],
                                   display_type=imageType,
                                   cursor_labels=labels,
                                   cmap=cmaps[imIndex],
                                   # parent=self,
                                   ))
            self.imagePanelToolbarsList.append(NavigationToolbar(
                self.imagePanelsList[imIndex], self.imagePanelsList[imIndex], imIndex))
            self.imagePanelsList[-1].NavigationToolbar = self.imagePanelToolbarsList[-1]
        #
        # Layout image panels in a grid
        #
        self.imLayout = QtWidgets.QGridLayout()
        imLayout = self.imLayout
        if max_in_row is None:
            max_in_row = int(np.sqrt(numImages) + 1 - 1e-10)
        for imIndex in range(numImages):
            imLayout.addWidget(self.imagePanelToolbarsList[imIndex], 2 * np.floor(
                imIndex / max_in_row), imIndex % max_in_row)
            imLayout.addWidget(self.imagePanelsList[imIndex], 2 * np.floor(
                imIndex / max_in_row) + 1, imIndex % max_in_row)
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
        # initInterval = initFPS#1.0 / initFPS * 1e3
        self.moviePlayer = FuncAnimationCustom(self.imagePanelsList[0].fig, self.movieUpdate, frames=range(
            numFrames), interval=initInterval, blit=True, repeat_delay=0)
        self.currentMovieFrame = 0

        #
        # Set up plots
        #
        self.plotsPanel = QtWidgets.QWidget(self)
        self.plotsPanelList = []
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
            complexDataList=xPlotDataList, title=location_labels[0], dataType=imageType, colors=colors,
            initMarkerPosn=self.loc[1])
        self.plotsPanelList.append(self.xPlotPanel)
        self.yPlotPanel = _MplPlot._MplPlot(
            complexDataList=yPlotDataList, title=location_labels[1], dataType=imageType, colors=colors,
            initMarkerPosn=self.loc[0])
        self.plotsPanelList.append(self.yPlotPanel)
        self.zPlotPanel = _MplPlot._MplPlot(
            complexDataList=zPlotDataList, title=location_labels[2], dataType=imageType, colors=colors,
            initMarkerPosn=self.loc[2])
        self.plotsPanelList.append(self.zPlotPanel)
        self.tPlotPanel = _MplPlot._MplPlot(
            complexDataList=tPlotDataList, title=location_labels[3], dataType=imageType, colors=colors,
            initMarkerPosn=self.loc[3])
        self.plotsPanelList.append(self.tPlotPanel)
        plotsLayout = QtWidgets.QVBoxLayout()
        plotsLayout.addWidget(self.xPlotPanel)
        plotsLayout.addWidget(self.yPlotPanel)
        plotsLayout.addWidget(self.zPlotPanel)
        plotsLayout.addWidget(self.tPlotPanel)
        self.plotsPanel.setLayout(plotsLayout)

        # make each section resizeable using a splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
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
        self.controls.sig_img_disp_type_change.connect(self.ChangeImageType)
        self.controls.sig_cursor_change.connect(self.ChangeLocation)
        self.controls.sig_z_change.connect(self.onZChange)
        self.controls.sig_lock_plots_change.connect(self.updatePlotLock)
        self.controls.sig_window_level_change.connect(self.ChangeWindowLevel)
        self.controls.sig_window_level_reset.connect(
            self.SetWindowLevelToDefault)
        self.controls.sig_t_change.connect(self.onTChange)
        self.controls.sig_roi_clear.connect(self.clearROI)
        self.controls.sig_roi_del_last.connect(self.deleteLastROI)
        self.controls.sig_roi_avg_timecourse.connect(self.plotROIAvgTimeseries)
        self.controls.sig_roi_psc_timecourse.connect(self.plotROIPSCTimeseries)
        self.controls.sig_roi_1vol_histogram.connect(self.plotROI1VolHistogram)
        self.controls.sig_movie_interval_change.connect(
            self.changeMovieInterval)
        self.controls.sig_movie_pause.connect(self.pauseMovie)
        self.controls.sig_movie_goto_frame.connect(
            self.movieGotoFrame)
        self.controls.sig_overlay_lower_thresh_change.connect(
            self.thresholdOverlay)
        self.controls.sig_overlay_upper_thresh_change.connect(
            self.thresholdOverlay)
        self.controls.sig_overlay_alpha_change.connect(self.setOverlayAlpha)

        # Connect signals from imagePanel
        for currImagePanel in self.imagePanelsList:
            currImagePanel.sig_cursor_change.connect(self.ChangeLocation)
            currImagePanel.sig_window_level_change.connect(
                self.ChangeWindowLevel)
            currImagePanel.sig_z_change.connect(self.onZChange)

        # Connect signals from imagePanel toolbars
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            currimagePanelToolbar.sig_roi_init.connect(self.initializeROI)
            currimagePanelToolbar.signal_roi_destruct.connect(self.destructROI)
            currimagePanelToolbar.sig_roi_start.connect(self.startNewROI)
            currimagePanelToolbar.sig_roi_change.connect(self.updateROI)
            currimagePanelToolbar.sig_roi_end.connect(self.endROI)
            currimagePanelToolbar.sig_roi_cancel.connect(self.cancelROI)
            currimagePanelToolbar.sig_movie_init.connect(self.initializeMovie)
            currimagePanelToolbar.sig_movie_destruct.connect(
                self.destructMovie)

    def setViewerNumber(self, number):
        self.viewerNumber = number

    # ==================================================================
    # slots dealing with image appearance
    # ==================================================================

    def ChangeImageType(self, imageType):
        self.controls.SetImageType(imageType)
        self.xPlotPanel.showDataTypeChange(imageType)
        self.yPlotPanel.showDataTypeChange(imageType)
        self.zPlotPanel.showDataTypeChange(imageType)
        self.tPlotPanel.showDataTypeChange(imageType)

        for currImagePanel in self.imagePanelsList:
            currImagePanel.show_display_type_change(imageType)

    def keyPressEvent(self, event):
        key = event.key()
        if key == 77:
            self.ChangeImageType(dd.ImageDisplayType.mag)
        elif key == 80:
            self.ChangeImageType(dd.ImageDisplayType.phase)
        elif key == 82:
            self.ChangeImageType(dd.ImageDisplayType.real)
        elif key == 73:
            self.ChangeImageType(dd.ImageDisplayType.imag)
        event.ignore()

    def ChangeWindowLevel(self, newIntensityWindow, newIntensityLevel):
        self.controls.ChangeWindowLevel(newIntensityWindow, newIntensityLevel)
        for currImagePanel in self.imagePanelsList:
            currImagePanel.show_window_level_change(
                newIntensityWindow, newIntensityLevel)

    def SetWindowLevelToDefault(self):
        self.controls.ChangeWindowLevel(0, 0)
        for currImagePanel in self.imagePanelsList:
            currImagePanel.show_set_window_level_to_default()

    # ==================================================================
    # slots dealing with a cursor_loc change
    # ==================================================================
    def ChangeLocation(self, x, y):
        self.loc[:2] = [x, y]
        self.controls.ChangeLocation(x, y)
        self.updatePlots()
        numImages = len(self.imagePanelsList)
        imgVals = []
        for imIndex in range(numImages):
            self.imagePanelsList[imIndex].show_cursor_loc_change([x, y])
            imgVals.append(self.imagePanelsList[imIndex].cursor_val)
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
            imagePanel.set_slice_num(newz)
        for imgIndx in range(len(self.imagePanelsList)):
            self.imagePanelsList[imgIndx].show_complex_image_change(
                self.complexImList[imgIndx][:, :, self.loc[2], self.loc[3]])
            self.thresholdOverlay(self.controls.lowerThreshSpinbox.value(
            ), self.controls.upperThreshSpinbox.value())
        self.updatePlots()

    def onTChange(self, value):
        # clip to valid locations?
        # value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)
        self.loc[3] = value
        for imIndex in range(len(self.imagePanelsList)):
            self.imagePanelsList[imIndex].show_complex_image_change(
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

    def updatePlotLock(self):
        lockPlots = self.controls.lockPlotsCheckbox.isChecked()
        for currPlot in self.plotsPanelList:
            currPlot.lockPlot = lockPlots

    # ==================================================================
    # slots for ROI tool
    # ==================================================================
    def initializeROI(self, imgIndex):
        self.controls.roiAnalysisWidget.setEnabled(True)
        if self.imagePanelToolbarsList[imgIndex].canvas.receivers(
                self.imagePanelToolbarsList[imgIndex].canvas.sig_cursor_change) > 0:
            self.imagePanelToolbarsList[imgIndex].canvas.sig_cursor_change.disconnect(self.ChangeLocation)

    def destructROI(self, imgIndex):
        atLeastOneActive = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._ROIactive:
                atLeastOneActive = True
        if not atLeastOneActive:
            self.controls.roiAnalysisWidget.setEnabled(False)
        self.imagePanelToolbarsList[imgIndex].canvas.sig_cursor_change.connect(
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
        if imageType == dd.ImageDisplayType.mag:
            data = np.abs(data)
        elif imageType == dd.ImageDisplayType.phase:
            data = np.angle(data)
        elif imageType == dd.ImageDisplayType.real:
            data = np.real(data)
        elif imageType == dd.ImageDisplayType.imag:
            data = np.imag(data)
        return data

    def plotROIAvgTimeseries(self):
        mask = self.getROIMask()
        imageType = self.imagePanelsList[0].display_type
        fig = None
        num_active_plots = 0
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar = self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data = self.complexImList[index]
                data = self.applyImageType(data, imageType)
                avgTimeseries = data[mask].mean(axis=0)
                if fig == None:
                    fig = plt.figure()
                plt.plot(avgTimeseries, dd.PlotColours.colours[index], label=self.subplotTitles[index])
                num_active_plots += 1
        if not (num_active_plots <= 1 and self.subplotTitles[index] == ""):
            plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Average Signal")
        plt.show()

    def plotROIPSCTimeseries(self):
        mask = self.getROIMask()
        imageType = self.imagePanelsList[0].display_type
        fig = None
        num_active_plots = 0
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
                num_active_plots += 1
        if not (num_active_plots <= 1 and self.subplotTitles[index] == ""):
            plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Percent Signal Change")
        plt.show()

    def plotROI1VolHistogram(self, numBins):
        mask = self.getROIMask()
        imageType = self.imagePanelsList[0].display_type
        dataList = []
        colorList = []
        labelList = []
        fig = False
        num_active_plots = 0
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar = self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data = self.complexImList[index]
                data = self.applyImageType(data, imageType)
                dataList.append(data[..., self.loc[3]][mask])
                colorList.append(dd.PlotColours.colours[index])
                labelList.append(self.subplotTitles[index])
                # y,binEdges,_=plt.hist(data[...,self.loc[3]][mask],bins=numBins,color=dd.PlotColours.colours[index], alpha=0.04)
                # bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
                # plt.plot(bincenters,y,'-',marker="s",color=dd.PlotColours.colours[index], label=self.subplot_titles[index])
                fig = True
                num_active_plots += 1
        if fig:
            plt.figure()
            plt.hist(dataList, bins=numBins, color=colorList, label=labelList)
            if not (num_active_plots <= 1 and self.subplotTitles[index] == ""):
                plt.legend()
        plt.show()

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

    # ==================================================================
    # slots for overlay thresholding
    # ==================================================================
    def thresholdOverlay(self, lowerThresh, upperThresh):
        for imgIndx in range(len(self.imagePanelsList)):
            if self.overlayList[imgIndx] is not None:
                overlay = self.overlayList[imgIndx][:, :, self.loc[2]]
                lowerThreshMask = overlay >= lowerThresh
                upperThreshMask = overlay <= upperThresh
                mask = (lowerThreshMask * upperThreshMask).astype('bool')
                if self.controls.overlayInvertCheckbox.isChecked():
                    mask = np.invert(mask)
                thresholded = np.ma.masked_where(mask, overlay)
                self.imagePanelsList[imgIndx].set_overlay(thresholded)
                self.imagePanelsList[imgIndx].blit_image_and_lines()

    def setOverlayAlpha(self, value):
        for currImagePanel in self.imagePanelsList:
            currImagePanel.overlay.set_alpha(value)
            currImagePanel.blit_image_and_lines()

    # ==================================================================
    # slots for movie tool
    # ==================================================================
    def movieUpdate(self, frame):
        z = self.loc[2]
        self.currentMovieFrame = frame
        imageType = self.imagePanelsList[0].display_type
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
            self.moviePlayer.moviePaused = False
            if not self.moviePlayer.moviePaused:
                self.moviePlayer.event_source.start()

        if self.imagePanelToolbarsList[imgIndex].canvas.receivers(
                self.imagePanelToolbarsList[imgIndex].canvas.sig_cursor_change) > 0:
            self.imagePanelToolbarsList[imgIndex].canvas.sig_cursor_change.disconnect(self.ChangeLocation)
        if self.overlayList[imgIndex] is not None:
            self.imagePanelsList[imgIndex].overlay.set_visible(False)
        self.moviePlayer._draw_next_frame(self.currentMovieFrame, True)

    def destructMovie(self, imgIndex):
        atLeastOneActive = False
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar._movieActive:
                atLeastOneActive = True
        if not atLeastOneActive:
            self.controls.movieWidget.setEnabled(False)
            self.moviePlayer.event_source.stop()
            self.moviePlayer.moviePaused = True
        self.imagePanelToolbarsList[imgIndex].canvas.sig_cursor_change.connect(
            self.ChangeLocation)
        if self.overlayList[imgIndex] is not None:
            self.imagePanelsList[imgIndex].overlay.set_visible(True)
        self.imagePanelsList[imgIndex].show_complex_image_change(
            self.complexImList[imgIndex][:, :, self.loc[2], self.loc[3]])

    def changeMovieInterval(self, interval):
        self.moviePlayer._interval = interval

    def pauseMovie(self):
        self.moviePlayer.moviePaused = self.controls.moviePauseButton.isChecked()
        if self.moviePlayer.moviePaused:
            self.moviePlayer.event_source.stop()
        else:
            self.moviePlayer.event_source.start()

    def movieGotoFrame(self, frame):
        newFrameSeq = self.moviePlayer.new_frame_seq()
        for i in range(frame):
            next(newFrameSeq)
        self.moviePlayer.frame_seq = newFrameSeq
        self.moviePlayer._draw_next_frame(frame, True)

    def closeEvent(self, event):
        self.moviePlayer.event_source.stop()
        if self.viewerNumber:
            del _Core._viewerList[self.viewerNumber]
        event.accept()


# ==================================================================
# other classes
# ==================================================================

class roiData():
    def __init__(self):
        self.verts = {}

    def startNewLassoData(self, x, y, z):
        if z in self.verts:
            self.verts[z].append([(x, y), ])
        else:
            self.verts[z] = [[(x, y), ], ]


class _MplImageSlice(_MplImage.MplImage):
    def __init__(self, maxSliceNum=0, *args, **keywords):
        super(_MplImageSlice, self).__init__(*args, **keywords)
        self.maxSliceNum = maxSliceNum

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            clipVal = np.minimum(np.maximum(
                self.get_slice_num() + 1, 0), self.maxSliceNum - 1)
        else:
            clipVal = np.minimum(np.maximum(
                self.get_slice_num() - 1, 0), self.maxSliceNum - 1)
        self.sig_z_change.emit(clipVal)


class FuncAnimationCustom(animation.FuncAnimation):
    def __init__(self, *args, **keywords):
        animation.FuncAnimation.__init__(self, *args, **keywords)
        self.moviePaused = True

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
        # AK: ADDED A CHECK FOR MOVIE PAUSE
        if not self.moviePaused:
            self.event_source.start()

    def _end_redraw(self, evt):
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(None, False)
        # AK: ADDED A CHECK FOR MOVIE PAUSE
        if not self.moviePaused:
            self.event_source.start()
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._on_resize)

    def _blit_draw(self, artists):
        # Handles blitted drawing, which renders only the artists given instead
        # of the entire figure.
        updated_ax = {a.axes for a in artists}
        # Enumerate artists to cache axes' backgrounds. We do not draw
        # artists yet to not cache foreground from plots with shared axes
        for ax in updated_ax:
            # If we haven't cached the background for the current view of this
            # axes object, do so now. This might not always be reliable, but
            # it's an attempt to automate the process.
            cur_view = ax._get_view()
            view, bg = self._blit_cache.get(ax, (object(), None))
            if cur_view != view:
                # AK: CHANGED SO WE CAN SEE FRAME TEXT BOX REDRAWN
                # self._blit_cache[ax] = (
                #     cur_view, ax.figure.canvas.copy_from_bbox(ax.bbox))
                self._blit_cache[ax] = (
                    cur_view, ax.figure.canvas.copy_from_bbox(ax.figure.bbox))
        # Make a separate pass to draw foreground.
        for a in artists:
            a.axes.draw_artist(a)
        # After rendering all the needed artists, blit each axes individually.
        for ax in updated_ax:
            # AK: CHANGED SO WE CAN SEE FRAME TEXT BOX REDRAWN
            # ax.figure.canvas.blit(ax.bbox)
            ax.figure.canvas.blit(ax.figure.bbox)

    def _on_resize(self, *args):
        # On resize, we need to disable the resize event handling so we don't
        # get too many events. Also stop the animation events, so that
        # we're paused. Reset the cache and re-init. Set up an event handler
        # to catch once the draw has actually taken place.
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self.event_source.stop()
        self._blit_cache.clear()
        # AK: REMOVE THIS LINE SO A RESET FRAME SEQUENCE ISN'T DRAWN WHEN RESIZING
        # self._init_draw()
        self._resize_id = self._fig.canvas.mpl_connect('draw_event',
                                                       self._end_redraw)
