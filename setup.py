# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:17:27 2017

@author: akuurstr
"""

from distutils.core import setup
setup(
  name = 'vidi3d',
  packages = ['vidi3d','vidi3d.Imshow','vidi3d.Compare'],
  package_data={'vidi3d': ['icons/*','Examples/*']},
  version = '1.0.2',
  install_requires = [
  'numpy',
  'PyQt5',
  'matplotlib'],
  description = 'Visualizes 3d NumPy arrays using Matplotlib and PyQt5.',
  author = 'Alan Kuurstra',
  author_email = 'alankuurstra@gmail.com',
  url = 'https://github.com/AlanKuurstra/vidi3d', # use the URL to the github repo
  download_url = 'https://github.com/AlanKuurstra/vidi3d/archive/1.0.2.tar.gz',
  keywords = ['3d', 'image', 'viewer', 'medical', 'numpy'],
  classifiers = [],
)
