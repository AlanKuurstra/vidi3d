#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 14:49:46 2017

@author: akuurstr
"""
import random

import numpy as np

from phantom import generate_fmri_phantom
from vidi3d import compare2d

# IMPORT DATA
tr = 1  # s
nVols = 100
task = np.zeros(nVols)
activations = np.array(random.sample(range(int(nVols / 10)), 3)) * 10
task[activations] = 1
img, bold_signal, roi = generate_fmri_phantom(task, tr=tr, SNR=35)

# GLM
img_reshape = img.reshape((np.prod(img.shape[:-1]), img.shape[-1])).T
design_mtx = np.ones((len(task), 2))
design_mtx[:, 0] = bold_signal
coeff_maps, _, _, _ = np.linalg.lstsq(design_mtx, img_reshape)
coeff_maps = coeff_maps.T.reshape(img.shape[:-1] + (design_mtx.shape[-1],))
activation_map = coeff_maps[..., 0]

compare2d(img, overlays=activation_map, window_title="GLM example", overlay_cmaps='seismic')
