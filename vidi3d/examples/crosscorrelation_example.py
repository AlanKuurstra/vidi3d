#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:52:31 2017

@author: akuurstr
"""

import vidi3d as v
import numpy as np
import random
from generatePhantom import generateFmriPhantom
from scipy.signal import correlate

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
# CROSS CORRELATION
#
normalized = img - img.mean(axis=-1)[..., np.newaxis]
normalized = normalized / np.linalg.norm(normalized, axis=-1)[..., np.newaxis]
correlationMap = correlate(
    normalized, boldSignal[np.newaxis, np.newaxis, :], mode='valid')
correlationMap = correlationMap.max(axis=-1)
v.compare2d(img, overlay=correlationMap,
            windowTitle="Cross correlation example", overlayColormap='seismic')
