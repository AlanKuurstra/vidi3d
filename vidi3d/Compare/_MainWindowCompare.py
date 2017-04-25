"""
Sets up the main window for the 2d viewer. This includes creating MpImage, MpPlot,
ControlWidget2D.  Also connections are made between QT signals sent by other
classes and functions within this class.
"""
import numpy as np
from PyQt4 import QtCore,QtGui
from .. import _Core as _Core
from .._NavigatorToolbar import NavigationToolbar
from .. import _MplImage as _MplImage
from .. import _MplPlot as _MplPlot
from .. import _DisplayDefinitions as dd  
import _ControlWidgetCompare
import matplotlib.pyplot as plt
from matplotlib import path

class _MainWindow(QtGui.QMainWindow):     
    def __init__(self,complexIm, pixdim=None, interpolation='bicubic', origin='lower', subplotTitles=None, locationLabels=None, maxNumInRow=None, colormap=None):                
        _Core._create_qApp()  
        super(_MainWindow,self).__init__() 
        self.setWindowTitle('Compare Viewer')      
        self.viewerNumber=0
        self.complexIm = complexIm         
        if self.complexIm.ndim == 4:
            self.complexIm = self.complexIm[:,:,:,:,np.newaxis]  
        numImages = self.complexIm.shape[4]

        #initLocation=[int(complexIm.shape[0]/2),int(complexIm.shape[1]/2)]
        self.loc=[int(complexIm.shape[0]/2),int(complexIm.shape[1]/2),int(complexIm.shape[2]/2),0]
        #initLocation=self.loc
        
        imageType=dd.ImageType.mag                
        if pixdim!=None:
            aspect=np.float(pixdim[1])/pixdim[0]
        else:
            aspect='equal'
        self.pixdim=pixdim
        
        #
        # give each image a colormap
        #        
        if colormap != None and type(colormap) != list:
            tmp=colormap
            colormap=[]
            for i in range(numImages):
                colormap.append(tmp)
        elif colormap == None:
            colormap=[]
            for i in range(numImages):
                colormap.append(None)
            
                
                
        
        #
        # give each image a label
        #
        if type(subplotTitles) is tuple:
            subplotTitles=list(subplotTitles)
        if type(subplotTitles) is list and len(subplotTitles)==1:
            subplotTitles=subplotTitles[0]
        elif type(subplotTitles) is list and len(subplotTitles)!=numImages:
            subplotTitles=None        
        if numImages==1 and subplotTitles is None:
            subplotTitles=[""]
        elif numImages==1 and type(subplotTitles) is str:
            subplotTitles=[subplotTitles]
        elif numImages>1 and type(subplotTitles) is str:
            prefix=subplotTitles
            subplotTitles=[]
            for imIndex in range(numImages):
                subplotTitles.append(prefix+str(imIndex))
        elif numImages>1 and type(subplotTitles) is list:
            pass
        else:
            subplotTitles=[]
            for imIndex in range(numImages):
                subplotTitles.append("Image "+str(imIndex)) 
        self.subplotTitles = subplotTitles
        #
        # Set up Controls
        #        
        self.controls = _ControlWidgetCompare._ControlWidgetCompare(imgShape=complexIm.shape, location=self.loc, imageType=imageType, locationLabels=locationLabels,imgVals=zip(subplotTitles,np.zeros(len(subplotTitles)))) 
        
        #
        # Set up image panels
        #   
        self.imagePanels=QtGui.QWidget(self)
        colors=dd.PlotColours.colours
        
        
        self.imagePanelsList = []
        self.imagePanelToolbarsList=[]
        if locationLabels is None:
            locationLabels = ["X", "Y","Z","T"]
        for imIndex in range(numImages):
            labels= [{'color': 'r', 'textLabel': locationLabels[0]},{'color': 'b', 'textLabel': locationLabels[1]},{'color': colors[imIndex], 'textLabel': subplotTitles[imIndex]}]                             
            self.imagePanelsList.append(_MplImageSlice(complexImage=self.complexIm[:,:,self.loc[2],self.loc[3],imIndex], aspect=aspect,sliceNum=self.loc[2],maxSliceNum=self.complexIm.shape[2],interpolation=interpolation, origin=origin, location=self.loc[:2], imageType=imageType, locationLabels=labels, colormap=colormap[imIndex], parent=self))                            
            self.imagePanelToolbarsList.append(NavigationToolbar(self.imagePanelsList[imIndex],self.imagePanelsList[imIndex]))
            self.imagePanelsList[-1].NavigationToolbar=self.imagePanelToolbarsList[-1]
        """
        # Synchronize the starting window/leveling to agree with the first panel        
        for imIndex in range(1,numImages):            
            self.imagePanelsList[imIndex].intensityLevelCache=self.imagePanelsList[0].intensityLevelCache
            self.imagePanelsList[imIndex].intensityWindowCache=self.imagePanelsList[0].intensityWindowCache
        self.ChangeWindowLevel(self.imagePanelsList[0].intensityWindowCache[imageType],self.imagePanelsList[0].intensityLevelCache[imageType])
        """
        imLayout = QtGui.QGridLayout()
        if maxNumInRow is None:
            maxNumInRow=int(np.sqrt(numImages)+1-1e-10)
        for imIndex in range(numImages):            
            imLayout.addWidget(self.imagePanelToolbarsList[imIndex],2*np.floor(imIndex/maxNumInRow),imIndex%maxNumInRow)
            imLayout.addWidget(self.imagePanelsList[imIndex],2*np.floor(imIndex/maxNumInRow)+1,imIndex%maxNumInRow)
        self.imagePanels.setLayout(imLayout)
        
        #
        #Set up ROI
        #
        self.ROIData=roiData()
        
        #
        # Set up plots
        #
        self.plotsPanel=QtGui.QWidget(self)           
        #self.xPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[:,initLocation[1],self.loc[2],:], title=locationLabels[0], dataType=imageType,colors=colors,initMarkerPosn=initLocation[1])
        #self.yPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[initLocation[0],:,self.loc[2],:], title=locationLabels[1], dataType=imageType,colors=colors,initMarkerPosn=initLocation[0])
        self.xPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[:,self.loc[1],self.loc[2],self.loc[3],:], title=locationLabels[0], dataType=imageType,colors=colors,initMarkerPosn=self.loc[1])
        self.yPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[self.loc[0],:,self.loc[2],self.loc[3],:], title=locationLabels[1], dataType=imageType,colors=colors,initMarkerPosn=self.loc[0])
        self.zPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[self.loc[0],self.loc[1],:,self.loc[3],:], title=locationLabels[2], dataType=imageType,colors=colors,initMarkerPosn=self.loc[2])
        self.tPlotPanel=_MplPlot._MplPlot(complexData=self.complexIm[self.loc[0],self.loc[1],self.loc[2],:,:], title=locationLabels[3], dataType=imageType,colors=colors,initMarkerPosn=self.loc[3])
        plotsLayout=QtGui.QVBoxLayout()        
        plotsLayout.addWidget(self.xPlotPanel)        
        plotsLayout.addWidget(self.yPlotPanel)
        plotsLayout.addWidget(self.zPlotPanel)
        plotsLayout.addWidget(self.tPlotPanel)
        self.plotsPanel.setLayout(plotsLayout)
        
        #make each section resizeable using a splitter                     
        splitter=QtGui.QSplitter(QtCore.Qt.Horizontal)        
        splitter.addWidget(self.controls)
        splitter.addWidget(self.imagePanels)
        splitter.addWidget(self.plotsPanel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        
                
        self.setCentralWidget(splitter) #used when inheriting from QMainWindow
        #self.statusBar().showMessage('Ready')         
        
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
        self.controls.signalWindowLevelReset.connect(self.SetWindowLevelToDefault)
        self.controls.signalTLocationChange.connect(self.onTChange)        
        self.controls.signalROIClear.connect(self.clearROI)        
        self.controls.signalROIAvgTimecourse.connect(self.plotROIAvgTimeseries)
        self.controls.signalROI1VolHistogram.connect(self.plotROI1VolHistogram)
        
        #connect all z changes to each other
        for imagePanel in self.imagePanelsList:
            imagePanel.signalZLocationChange.connect(self.onZChange)            
         
        # Connect from imagePanel       
        for currImagePanel in self.imagePanelsList:
            currImagePanel.signalLocationChange.connect(self.ChangeLocation)
            currImagePanel.signalWindowLevelChange.connect(self.ChangeWindowLevel)        
        
        # Connect from imagePanel toolbars
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            currimagePanelToolbar.signalROIStart.connect(self.startNewROI)            
            currimagePanelToolbar.signalROIChange.connect(self.updateROI)
            currimagePanelToolbar.signalROIEnd.connect(self.endROI)
            currimagePanelToolbar.signalROICancel.connect(self.cancelROI)
                
    def ChangeImageType(self, imageType):
        self.controls.SetImageType(imageType)
        self.xPlotPanel.showDataTypeChange(imageType)
        self.yPlotPanel.showDataTypeChange(imageType)        
        self.zPlotPanel.showDataTypeChange(imageType)
        self.tPlotPanel.showDataTypeChange(imageType)   

        for currImagePanel in self.imagePanelsList:
            currImagePanel.showImageTypeChange(imageType)        
          
    def ChangeWindowLevel(self, newIntensityWindow,newIntensityLevel):
        self.controls.ChangeWindowLevel(newIntensityWindow,newIntensityLevel)
        numImages = len(self.imagePanelsList)
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showWindowLevelChange(newIntensityWindow,newIntensityLevel)
            
    def SetWindowLevelToDefault(self):
        self.controls.ChangeWindowLevel(0,0)
        
        for currImagePanel in self.imagePanelsList:
            currImagePanel.showSetWindowLevelToDefault()
            
    def updatePlots(self):
        self.xPlotPanel.showComplexDataAndMarkersChange(self.complexIm[:,self.loc[1],self.loc[2],self.loc[3],:],self.loc[0])
        self.yPlotPanel.showComplexDataAndMarkersChange(self.complexIm[self.loc[0],:,self.loc[2],self.loc[3],:],self.loc[1])
        self.zPlotPanel.showComplexDataAndMarkersChange(self.complexIm[self.loc[0],self.loc[1],:,self.loc[3],:],self.loc[2])
        self.tPlotPanel.showComplexDataAndMarkersChange(self.complexIm[self.loc[0],self.loc[1],self.loc[2],:,:],self.loc[3])
        
    def ChangeLocation(self, x, y ):  
        self.loc[:2]=[x,y]
        self.controls.ChangeLocation(x, y)
        self.updatePlots()        
        numImages = len(self.imagePanelsList)
        imgVals=[]
        for imIndex in range(numImages):
            self.imagePanelsList[imIndex].showLocationChange([x,y])
            imgVals.append(self.imagePanelsList[imIndex].locationVal)
        self.controls.ChangeImgVals(imgVals)

    def keyPressEvent(self,event):
        #print event.text() #this one can tell when shift is being held down
        key=event.key()
        if key==77:
            self.ChangeImageType(dd.ImageType.mag)
        elif key==80:
            self.ChangeImageType(dd.ImageType.phase)
        elif key==82:
            self.ChangeImageType(dd.ImageType.real)
        elif key==73:
            self.ChangeImageType(dd.ImageType.imag)     
        event.ignore()
    
    def setViewerNumber(self,number):
        self.viewerNumber=number
        
    def closeEvent(self,event):   
        if self.viewerNumber:
            del  _Core._viewerList[self.viewerNumber]
        
    def onZChange(self,newz):        
        prevz=self.loc[2]
        self.loc[2]=newz
        self.controls.ChangeZLocation(newz)
        
        drawingEngaged=False        
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            if currimagePanelToolbar.roiDrawingEngaged:
                drawingEngaged=True
                currimagePanelToolbar.roiDrawingEngaged=False     
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
            imagePanel.sliceNum=newz        
        for imgIndx in range(len(self.imagePanelsList)):
            self.imagePanelsList[imgIndx].showComplexImageChange(self.complexIm[:,:,self.loc[2],self.loc[3],imgIndx])        
        self.updatePlots()
        
        
                        
    def onTChange(self,value):
        #clip to valid locations?
        #value = np.minimum(np.maximum(value+0.5, 0), self.raw.shape[2]-1)      
        self.loc[3]=value 
        for imIndex in range(len(self.imagePanelsList)):            
            self.imagePanelsList[imIndex].showComplexImageChange(self.complexIm[:,:,self.loc[2],self.loc[3],imIndex])        
        self.updatePlots()
   
    def updateROI(self,x,y):
        currentROIverts=self.ROIData.verts[self.loc[2]][-1]
        currentROIverts.append((x, y))        
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            #self.canvas.restore_region(self.background)   
            currentLine=currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]][-1]
            currentLine.set_data(zip(*currentROIverts))         
            self.drawROI(currimagePanelToolbar)
            
    def drawROI(self,imagePanelToolbar):        
        if imagePanelToolbar._ROIactive:
                #do we need to draw all these lines?
                for currentLine in imagePanelToolbar.roiLines.mplLineObjects[self.loc[2]]:
                    imagePanelToolbar.ax.draw_artist(currentLine)            
                imagePanelToolbar.canvas.blit(imagePanelToolbar.ax.bbox)
        
    def startNewROI(self,x,y):        
        self.ROIData.startNewLassoData(x,y,self.loc[2])       
        for currimagePanelToolbar in self.imagePanelToolbarsList:            
            currimagePanelToolbar.roiLines.startNewLassoLine(x,y,self.loc[2])
            if currimagePanelToolbar._ROIactive:
                currentline=currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]][-1]
                currimagePanelToolbar.ax.add_line(currentline)
    def endROI(self): 
        currentROIverts=self.ROIData.verts[self.loc[2]][-1]
        currentROIverts.append(currentROIverts[0])
        for currimagePanelToolbar in self.imagePanelToolbarsList:
            #self.canvas.restore_region(self.background)
            currentLine=currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]][-1]
            currentLine.set_data(zip(*currentROIverts))        
            self.drawROI(currimagePanelToolbar)
    def cancelROI(self):        
        for currimagePanelToolbar in self.imagePanelToolbarsList:            
                currentline=currimagePanelToolbar.roiLines.mplLineObjects[self.loc[2]].pop()
                if currimagePanelToolbar._ROIactive:
                    currimagePanelToolbar.ax.lines.remove(currentline)
                    currimagePanelToolbar.canvas.draw()
        self.ROIData.verts[self.loc[2]].pop()
    
    def getROIMask(self):
        mask=np.zeros(self.complexIm.shape[:-2],dtype='bool')
        for z in self.ROIData.verts:
            for contour in self.ROIData.verts[z]:
                mypath=path.Path(contour)
                tmp=mypath.contains_points(list(np.ndindex(self.complexIm.shape[:2])))
                tmp=tmp.reshape(self.complexIm.shape[:2])                
                mask[...,z]=np.logical_or(mask[...,z], tmp) 
        return mask
    def applyImageType(self,data,imageType):
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
        mask=self.getROIMask()                  
        data=(self.complexIm[...,0],mask[...,np.newaxis])
        concat = np.empty(data[0].shape+(len(data),),dtype='complex')
        for i in range(len(data)):
            concat[:,:,:,:,i]=data[i]
        data=concat
        viewer=_MainWindow(data,pixdim=self.pixdim,interpolation='none')
        
    def plotROIAvgTimeseries(self):        
        mask=self.getROIMask()
        imageType=self.imagePanelsList[0]._imageType
        fig=None
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar=self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data=self.complexIm[...,index]                
                data=self.applyImageType(data,imageType)                 
                avgTimeseries=data[mask].mean(axis=0)
                avgTimeseries=avgTimeseries+np.finfo(float).eps
                avgTimeseries=(avgTimeseries-avgTimeseries[0])/avgTimeseries[0]*100
                if fig==None:
                    fig=plt.figure()
                plt.plot(avgTimeseries,dd.PlotColours.colours[index],label=self.subplotTitles[index])
        plt.legend()
        plt.xlabel("Volume")
        plt.ylabel("Average Signal")
    def plotROI1VolHistogram(self,numBins):
        mask=self.getROIMask()
        imageType=self.imagePanelsList[0]._imageType
        dataList=[]
        colorList=[]
        labelList=[]
        fig=False
        for index in range(len(self.imagePanelToolbarsList)):
            currimagePanelToolbar=self.imagePanelToolbarsList[index]
            if currimagePanelToolbar._ROIactive:
                data=self.complexIm[...,index]
                data=self.applyImageType(data,imageType)
                dataList.append(data[...,self.loc[3]][mask])
                colorList.append(dd.PlotColours.colours[index])
                labelList.append(self.subplotTitles[index])
                #y,binEdges,_=plt.hist(data[...,self.loc[3]][mask],bins=numBins,color=dd.PlotColours.colours[index], alpha=0.04)
                #bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
                #plt.plot(bincenters,y,'-',marker="s",color=dd.PlotColours.colours[index], label=self.subplotTitles[index])
                fig=True
        if fig:
            plt.figure()
            plt.hist(dataList,bins=numBins,color=colorList,label=labelList)
            plt.legend()
            
        
    def clearROI(self):
        self.ROIData.verts={}
        for currimagePanelToolbar in self.imagePanelToolbarsList:                                   
            if currimagePanelToolbar._ROIactive:
                z=self.loc[2]
                if z in currimagePanelToolbar.roiLines.mplLineObjects:
                    for currentLine in currimagePanelToolbar.roiLines.mplLineObjects[z]:
                        currimagePanelToolbar.ax.lines.remove(currentLine)
            currimagePanelToolbar.roiLines.mplLineObjects={}
            currimagePanelToolbar.canvas.draw()
            currimagePanelToolbar.canvas.blit(currimagePanelToolbar.ax.bbox)
        
class roiData():    
    def __init__(self):
        self.verts={}        
    def startNewLassoData(self,x,y,z):
        if z in self.verts:
            self.verts[z].append([(x,y),])            
        else:
            self.verts[z]=[[(x,y),],]        


            
class _MplImageSlice(_MplImage._MplImage):    
    def __init__(self,sliceNum=0,maxSliceNum=0,*args,**keywords):
        super(_MplImageSlice,self).__init__(*args,**keywords)
        self.sliceNum=sliceNum
        self.maxSliceNum=maxSliceNum
    def wheelEvent(self,event):        
        if event.delta()>0:
            clipVal=np.minimum(np.maximum(self.sliceNum+1, 0), self.maxSliceNum-1)                
        else:
            clipVal=np.minimum(np.maximum(self.sliceNum-1, 0), self.maxSliceNum-1)        
        self.signalZLocationChange.emit(clipVal)    
        
    
  
        
        
        
