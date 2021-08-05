"""
Common defnitions used throughout vidi3d.
Map integers to words for readable code.
"""


class ImageDisplayType:
    real, imag, mag, phase = range(4)


class PlotColours:
    # kelly colours without black or white, repeats after 20
    colours = ['#F3C300', '#875692', '#F38400', '#A1CAF1',
               '#BE0032', '#C2B280', '#848482', '#008856',
               '#E68FAC', '#0067A5', '#F99379', '#604E97',
               '#F6A600', '#B3446C', '#DCD300', '#882D17',
               '#8DB600', '#654522', '#E25822', '#2B3D26',  # end
               '#F3C300', '#875692', '#F38400', '#A1CAF1',
               '#BE0032', '#C2B280', '#848482', '#008856',
               '#E68FAC', '#0067A5', '#F99379', '#604E97',
               '#F6A600', '#B3446C', '#DCD300', '#882D17',
               '#8DB600', '#654522', '#E25822', '#2B3D26',
               ]


roi_color = '#00ff00'
