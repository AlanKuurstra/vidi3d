#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 16:42:04 2017

@author: akuurstr
"""

import numpy as np
import scipy.stats as stats
import statsmodels.sandbox.stats.multicomp

from phantom import generate_fmri_phantom
from vidi3d import compare2d


def cohen_d(x, y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(
        ((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)


def ttest(img1, img2, mask):
    tmap, pmap = stats.ttest_ind(img1, img2, axis=-1, equal_var=False)
    # multiple comparison correction
    pmap[np.isnan(pmap)] = 0
    tmp = pmap.ravel()
    tmp_mask = mask.ravel()
    _, tmp[tmp_mask] = statsmodels.sandbox.stats.multicomp.fdrcorrection0(tmp[tmp_mask])
    pmap_corr = tmp.reshape(pmap.shape)
    return tmap, pmap_corr


# IMPORT DATA
tr = 1  # s
n_vols = 100
task = np.zeros(n_vols)
task[int(n_vols / 2):] = 1
img, bold_signal, roi = generate_fmri_phantom(task, tr=tr, SNR=35)
rest_img = img[..., :int(n_vols / 2)]
activation_img = img[..., int(n_vols / 2):]
img_avg = img.mean(axis=-1)
phantom_mask = np.abs(img_avg) > 0.1

# RANDOM EFFECTS ANALYSIS
print("random effects analysis on ROI (mean as summary value):")
mask = phantom_mask * roi
mean1 = rest_img[mask].mean(axis=-1)
mean2 = activation_img[mask].mean(axis=-1)
t, p = stats.ttest_ind(mean1, mean2, equal_var=False)
print("difference in means: ", mean1.mean() - mean2.mean())
print("p value: ", p)
print("coehn's d: ", cohen_d(mean1, mean2))

# VOXELWISE T-TEST
tmap, pmap = ttest(activation_img, rest_img, phantom_mask)
# compare2d(img,overlays=(tmap,pmap),overlay_cmap=('seismic','Reds'),subplot_titles=('tmap','pmap'))
compare2d(img, overlays=tmap, overlay_cmaps=('seismic'), subplot_titles='tmap')
compare2d(img, overlays=pmap, overlay_cmaps=('seismic'), subplot_titles='pmap')
