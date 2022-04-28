# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='GrismGUI',
    version='0.1.0',
    description='A calibration and analysis GUI for miniature grism images',
    long_description=readme,
    author='Will Golay',
    author_email='wgolay30@gmail.com',
    url='',
    license=license)