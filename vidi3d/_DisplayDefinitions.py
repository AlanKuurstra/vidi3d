"""
Common defnitions used throughout vidi3d.
Map integers to words for readable code.
"""


class ImageType:
    real, imag, mag, phase = range(4)


class ImageCMap:
    gray, hsv = range(2)
# ran out of creativity after 8 colours and just started repeating existing colours.
# If the comparison viewer has more than 8 images, consider adding different
# colours.


class PlotColours:
    #kelly colours without black or white
    colours = ['#F3C300', '#875692', '#F38400', '#A1CAF1',
               '#BE0032', '#C2B280', '#848482', '#008856',
               '#E68FAC', '#0067A5', '#F99379', '#604E97',
               '#F6A600', '#B3446C', '#DCD300', '#882D17',
               '#8DB600', '#654522', '#E25822', '#2B3D26']
roiColor = '#00ff00'
