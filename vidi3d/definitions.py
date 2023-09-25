"""
Common defnitions used throughout vidi3d.
Map integers to words for readable code.
"""
import numpy as np


class ImageDisplayType:
    real, imag, mag, phase = range(4)


class PlotColours:
    # kelly's 22 colors of maximum contrast without black or white
    colours = ['#F3C300', '#875692', '#F38400', '#A1CAF1',
               '#BE0032', '#C2B280', '#848482', '#008856',
               '#E68FAC', '#0067A5', '#F99379', '#604E97',
               '#F6A600', '#B3446C', '#DCD300', '#882D17',
               '#8DB600', '#654522', '#E25822', '#2B3D26',
               ]

    def __init__(self, ncolours=20):
        nrandom = ncolours - len(PlotColours.colours)
        random_colours = []
        if nrandom > 0:
            np.random.seed(5)
            random_colours = [list(np.squeeze(x)) for x in
                              np.split(np.random.uniform(0, 1, size=nrandom * 3).reshape(nrandom, 3), nrandom)]
        self.colours = PlotColours.colours + random_colours


roi_color = '#00ff00'
