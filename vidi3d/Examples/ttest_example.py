#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 16:42:04 2017

@author: akuurstr
"""

import vidi3d as v
import numpy as np
from generatePhantom import generateFmriPhantom
import scipy.stats as stats
import statsmodels.sandbox.stats.multicomp


def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)


def ttest(img1, img2, mask):
    tmap, pmap = stats.ttest_ind(img1, img2, axis=-1, equal_var=False)
    # multiple comparison correction
    pmap[np.isnan(pmap)] = 0
    tmp = pmap.ravel()
    tmp_mask = mask.ravel()
    _, tmp[tmp_mask] = statsmodels.sandbox.stats.multicomp.fdrcorrection0(
        tmp[tmp_mask])
    pmap_corr = tmp.reshape(pmap.shape)
    return tmap, pmap_corr


#
# IMPORT DATA
#
tr = 1  # s
nVols = 100
task = np.zeros(nVols)
task[int(nVols / 2):] = 1
img, boldSignal, roi = generateFmriPhantom(task, tr=tr, SNR=35)
restImg = img[..., :int(nVols / 2)]
activationImg = img[..., int(nVols / 2):]
imgAvg = img.mean(axis=-1)
phantomMask = np.abs(imgAvg) > 0.1

#
# PREPROCESSING
#

#
# RANDOM EFFECTS ANALYSIS
#

print "random effects analysis on ROI (mean as summary value):"
mask = phantomMask * roi
mean1 = restImg[mask].mean(axis=-1)
mean2 = activationImg[mask].mean(axis=-1)
t, p = stats.ttest_ind(mean1, mean2, equal_var=False)
print "difference in means: ", mean1.mean() - mean2.mean()
print "p value: ", p
print "coehn's d: ", cohen_d(mean1, mean2)

#
# VOXELWISE T-TEST
#
tmap, pmap = ttest(activationImg, restImg, phantomMask)
# v.compare2d(img,overlay=(tmap,pmap),overlayColormap=('seismic','Reds'),subplotTitles=('tmap','pmap'))
v.compare2d(img, overlay=(tmap), overlayColormap=(
    'seismic'), subplotTitles='tmap')
v.compare2d(img, overlay=(pmap), overlayColormap=(
    'seismic'), subplotTitles='pmap')
