#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:52:31 2017

@author: akuurstr
"""

from vidi3d import compare2d
import numpy as np
import random
from phantom import generate_fmri_phantom
from scipy.signal import correlate

# IMPORT DATA
tr = 1  # s
nVols = 100
task = np.zeros(nVols)
activations = np.array(random.sample(range(int(nVols / 10)), 3)) * 10
task[activations] = 1
img, boldSignal, roi = generate_fmri_phantom(task, tr=tr, SNR=35)

# CROSS CORRELATION
normalized = img - img.mean(axis=-1)[..., np.newaxis]
normalized = normalized / np.linalg.norm(normalized, axis=-1)[..., np.newaxis]
correlation_map = correlate(normalized, boldSignal[np.newaxis, np.newaxis, :], mode='valid')
correlation_map = correlation_map.max(axis=-1)
compare2d(img, overlays=correlation_map, window_title="Cross correlation example", overlay_cmaps='seismic')
