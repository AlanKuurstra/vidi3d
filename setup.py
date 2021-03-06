import os

import setuptools

GITHUB_REF = os.getenv('GITHUB_REF')
version = GITHUB_REF.replace('refs/tags/', '') if (GITHUB_REF and GITHUB_REF.startswith('refs/tags/')) else '1.0.3'
setuptools.setup(
    name='vidi3d',
    version=version,
    author='Alan Kuurstra',
    author_email='alankuurstra@gmail.com',
    description='Visualizes 3d/4d NumPy arrays using Matplotlib and PyQt5.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/AlanKuurstra/vidi3d',
    packages=['vidi3d', 'vidi3d.Imshow', 'vidi3d.Compare'],
    package_data={'vidi3d': ['icons/*', 'Examples/*']},
    install_requires=[
        'numpy',
        'PyQt5',
        'matplotlib'],
    keywords=['3d', 'image', 'viewer', 'medical', 'numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    python_requires='>=3',
)
