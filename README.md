# vidi3d
Visualizes 3D/4D NumPy arrays using Matplotlib and PyQt5.

### Installation and Requirements

The following libraries are required:

- [Python 3](https://www.python.org/)
- [Numpy](http://www.numpy.org/): General purpose array-processing package.
- [Matplotlib](https://matplotlib.org/):  Python plotting package .
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/): Python bindings for Qt application framework.

To install, use: pip3 install vidi3d.

The software can also be found at [https://github.com/AlanKuurstra/vidi3d](https://github.com/AlanKuurstra/vidi3d).  

### Usage

    import vidi3d as v
    # compare a list of 2d images (an additional temporal dimension is optional)
    v.compare2d(listOf2dImages) 
    # compare a list of 3d images (an additional temporal dimension is optional)
    v.compare3d(listOf3dImages) 


Some simple examples can be found in the `Examples/` folder.
