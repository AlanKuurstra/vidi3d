# vidi3d
Visualizes 3D NumPy arrays using Matplotlib and PyQt4.

### Installation and Requirements

The following libraries are required:

- [Python 3](https://www.python.org/)
- [Numpy](http://www.numpy.org/): General purpose array-processing package.
- [Matplotlib](https://matplotlib.org/):  Python plotting package .
- [PyQt4](https://www.riverbankcomputing.com/software/pyqt/): Python bindings for Qt application framework.

To install, use: pip install vidi3d.

The software can also be found at [https://github.com/AlanKuurstra/vidi3d](https://github.com/AlanKuurstra/vidi3d).  

Note that PyQt4 must be installed manually:  
ubuntu: apt-get install python-qt4  
mac   : brew install cartr/qt4/pyqt@4 --with-python --without-python@2
win   : https://stackoverflow.com/questions/22640640/how-to-install-pyqt4-on-windows-using-pip

### Usage

    import vidi3d as v
    # compare a list of 2d images (an additional temporal dimension is optional)
    v.compare2d(listOf2dImages) 
    # compare a list of 3d images (an additional temporal dimension is optional)
    v.compare3d(listOf3dImages) 


Some simple examples can be found in the `Examples/` folder.
