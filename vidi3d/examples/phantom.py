#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 13:37:52 2017

@author: akuurstr
"""
import numpy as np

from simulation import phantom


def generate_fmri_phantom(task, SNR=30, tr=1.5, boldSignalChange=0.05):
    n = len(task)
    # phantom
    shepp_logan = phantom()
    roi = (shepp_logan > 0.29) * (shepp_logan < 0.3)
    signal_level = shepp_logan[roi].mean()
    shepp_logan = np.repeat(shepp_logan[..., np.newaxis], n, axis=-1)

    # noise
    sigma = signal_level / SNR
    noise = sigma * np.random.randn(*shepp_logan.shape)
    noisey_phantom = shepp_logan + noise

    # hrf
    # (from http://kendrickkay.net/GLMdenoise/doc/GLMdenoise/utilities/getcanonicalhrf.html)
    hrf = [0, 0.0314738742235483, 0.132892311247317, 0.312329209862644, 0.441154423620173,
           0.506326320948033, 0.465005683404153, 0.339291735120426, 0.189653785392583,
           0.0887497190889423, 0.0269546540274463, -
           0.00399259325523179, -0.024627314416849,
           -0.0476309054781231, -0.0550487226952204, -
           0.0533213710918957, -0.0543354934559645,
           -0.053251015547776, -0.0504861257190311, -
           0.0523878049128595, -0.0480250705100501,
           -0.0413692129609857, -0.0386230204112975, -
           0.0309582779400724, -0.0293100898508089,
           -0.0267610584328128, -0.0231531738458546, -
           0.0248940860170463, -0.0256090744971939,
           -0.0245258893783331, -0.0221593630969677, -
           0.0188920336851537, -0.0205456587473883,
           -0.0230804062250214, -0.0255724832493459, -
           0.0200646133809936, -0.0101145804661655,
           -0.014559191655812]
    hrf = np.interp(np.arange(len(task)) * tr, range(len(hrf)), hrf)

    # fmri phantom
    bold_signal = np.convolve(task, hrf, 'full')[:len(task)]
    bold_signal = bold_signal / bold_signal.max() * signal_level * boldSignalChange
    fmri_phantom = noisey_phantom + np.repeat(roi[..., np.newaxis], n, axis=-1) * bold_signal
    return fmri_phantom, bold_signal, roi
