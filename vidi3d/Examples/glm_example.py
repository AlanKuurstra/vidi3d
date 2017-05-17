#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 14:49:46 2017

@author: akuurstr
"""
import vidi3d as v
import numpy as np
import random
from generatePhantom import generateFmriPhantom

#
# IMPORT DATA
#
tr = 1  # s
nVols = 100
task = np.zeros(nVols)
activations = np.array(random.sample(range(int(nVols / 10)), 3)) * 10
task[activations] = 1
img, boldSignal, roi = generateFmriPhantom(task, tr=tr, SNR=35)

#
# PREPROCESSING
#

#
# GLM
#
imgReshape = img.reshape((np.prod(img.shape[:-1]), img.shape[-1])).T
DesignMtx = np.ones((len(task), 2))
DesignMtx[:, 0] = boldSignal
coeffMaps, _, _, _ = np.linalg.lstsq(DesignMtx, imgReshape)
coeffMaps = coeffMaps.T.reshape(img.shape[:-1] + (DesignMtx.shape[-1],))
activationMap = coeffMaps[..., 0]

v.compare2d(img, overlay=activationMap,
            windowTitle="GLM example", overlayColormap='seismic')

#
# STATS
#
