try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2QTAgg
import os
from matplotlib.lines import Line2D
from PyQt4 import QtCore
import _DisplayDefinitions as dd



class NavigationToolbar(NavigationToolbar2QTAgg):        
    signalROIChange = QtCore.pyqtSignal(float, float)        
    signalROIStart = QtCore.pyqtSignal(float, float)        
    signalROIEnd = QtCore.pyqtSignal(float, float)
    signalROICancel = QtCore.pyqtSignal()
    def __init__(self,canvas,parent):        
        super(NavigationToolbar,self).__init__(canvas,parent)        
        self.clear()          
        self.parent=parent
        self.canvas=canvas
        self.ax=parent.axes
        self._idMove=None
        a = self.addAction(self._icon('home.png'), 'Home', self.home)
        a.setToolTip('Reset original view')   
        a = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
        a.setToolTip('Zoom to rectangle')
        a = self.addAction(self._icon('move.png'), 'Pan', self.pan)
        a.setToolTip('Pan axes with left mouse, zoom with right') 
        #commented lines are still under development        
        #a = self.addAction(self.__file__('zoom_to_rect.png'), 'Select', self.selectROI)
        #a.setToolTip('Under development.')
        self.ROIwidget = self.addAction(self._icon(os.path.join(os.path.dirname(__file__), "icons/lasso.png")), 'Select', self.roi)
        self.ROIwidget.setToolTip('Select ROI for analysis')
        self.ROIwidget.setCheckable(True)
        self._ROIactive=False
        self._idROIPress=None
        self._idROIRelease=None
        self._idROIMove=None        
        self.roiLines=lassoLines()
        self.roiDrawingEngaged=False
        
        self.addSeparator()
        a = self.addAction(self._icon('filesave.png'), 'Save',
                self.save_figure)
        a.setToolTip('Save the figure')
    
    
    def roi(self,*args):        
        if self._ROIactive == True:
            self._ROIactive = False
            self.roi_deconstruct()
        else:
            self._ROIactive = True
            self.roi_initialize()
        
    def roi_initialize(self):
        
        self._idROIPress=self.canvas.mpl_connect('button_press_event', self.roi_press)        
        self._idROIRelease=self.canvas.mpl_connect('motion_notify_event', self.roi_move)
        self._idROIMove=self.canvas.mpl_connect('button_release_event', self.roi_release)        
        self.ROIwidget.setChecked(True)                     
        self.parent.signalLocationChange.disconnect(self.parent.parent.ChangeLocation)
        
        z=self.parent.parent.loc[2]   
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.add_line(currentLine)
        
        self.parent.vline.remove()
        self.parent.hline.remove()
        self.parent.htxt.remove()
        self.parent.vtxt.remove()
        
        #self.parent.BlitImageForROIDrawing()
        self.parent.BlitImageAndLines()
        
    def roi_deconstruct(self):
        
        self._idROIPress=self.canvas.mpl_disconnect(self._idROIPress)
        self._idROIRelease=self.canvas.mpl_disconnect(self._idROIRelease)
        self._idROIMove=self.canvas.mpl_disconnect(self._idROIMove)        
        self.ROIwidget.setChecked(False)
        self.parent.signalLocationChange.connect(self.parent.parent.ChangeLocation)
        
        self.ax.add_line(self.parent.hline)
        self.ax.add_line(self.parent.vline)
        self.ax.texts.append(self.parent.htxt)
        self.ax.texts.append(self.parent.vtxt)        
        
        z=self.parent.parent.loc[2]   
        if z in self.roiLines.mplLineObjects:
            for currentLine in self.roiLines.mplLineObjects[z]:
                self.ax.lines.remove(currentLine)               
        
        self.parent.BlitImageAndLines()
        
        
    def roi_release(self,event):    
        
        if self.mode != '' or self._ROIactive==False or not self.roiDrawingEngaged:
            return  
        if event.button != 1:            
            return
        if event.inaxes != self.ax:
            if self.roiDrawingEngaged:
                self.signalROICancel.emit()
                self.roiDrawingEngaged=False
            return
        self.signalROIEnd.emit(event.xdata, event.ydata)
        self.roiDrawingEngaged=False
    def roi_press(self,event): 
        
        if self.mode != '' or self._ROIactive==False:
            return         
        if event.button != 1:
            if self.roiDrawingEngaged:
                self.signalROICancel.emit()
                self.roiDrawingEngaged=False
            return
        self.signalROIStart.emit(event.xdata, event.ydata)
        self.roiDrawingEngaged=True
                
    def roi_move(self,event):                
        if self.mode != '' or self._ROIactive==False or not self.roiDrawingEngaged:
            return 
        if event.button != 1:            
            return
#        if self.current_roi.verts is None:
#            return
        if event.inaxes != self.ax:
            return
        self.signalROIChange.emit(event.xdata,event.ydata)       
        
        
class lassoLines():
    def __init__(self):        
        self.mplLineObjects={}        
    def startNewLassoLine(self,x,y,z):
        if z in self.mplLineObjects:
            self.mplLineObjects[z].append(Line2D([x], [y], linestyle='-', color=dd.roiColor, lw=1))
        else:
            self.mplLineObjects[z]=[Line2D([x], [y], linestyle='-', color=dd.roiColor, lw=1),]    
        
             
    
    
  
if __name__=="__main__":

    from pyview.Viewers import compare3d
    
    directory='/cfmm/data/akuurstr/data/Prado/ignore_knockout_mice/BOLD/registerFlash2D_BOLD_60/all/'
    imgloc=directory+'s_20160412_02'+'_flashBold60MC1_to_common.nii.gz'
    
    import nibabel as nib
    
    imgobj=nib.load(imgloc)
    pxlsz=imgobj.get_header()['pixdim'][1:5]
    
    img=imgobj.get_data().transpose(1,2,0,3)
    pxlsz=pxlsz[[1,2,0,3]]
    
    directory='/cfmm/data/akuurstr/data/Prado/ignore_knockout_mice/BOLD/registerFlash2D_BOLD_60/all/'
    imgloc=directory+'s_20160412_01'+'_flashBold60MC1_to_common.nii.gz'
    img2=nib.load(imgloc).get_data().transpose(1,2,0,3)
    directory='/cfmm/data/akuurstr/data/Prado/ignore_knockout_mice/BOLD/registerFlash2D_BOLD_60/all/'
    imgloc=directory+'s_20160412_03'+'_flashBold60MC1_to_common.nii.gz'
    img3=nib.load(imgloc).get_data().transpose(1,2,0,3)
    compare3d((img,img2,img3),pixdim=pxlsz,block=False)
