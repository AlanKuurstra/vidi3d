# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:17:27 2017

@author: akuurstr
"""

from distutils.core import setup
setup(
  name = 'vidi3d',
  packages = ['vidi3d'],
  version = '0.1',
  install_requires = [
  'numpy',
  #'PyQt4', #no PyQt4 in pipy
  'matplotlib'],
  description = 'Visualizes 3d and 4d NumPy arrays using Matplotlib and PyQt4.',
  author = 'Alan Kuurstra',
  author_email = 'alankuurstra@gmail.com',
  url = 'https://github.com/AlanKuurstra/vidi3d', # use the URL to the github repo
  download_url = 'https://github.com/AlanKuurstra/vidi3d/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['3d', 'image', 'viewer', 'medical', 'numpy'],
  classifiers = [],
)