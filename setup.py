#!/usr/bin/python3
"""Setup
"""
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
from distutils.core import setup

import unittest

version = "0.0.1"

with open('README.md') as f:
    long_description = f.read()

setup(name='ofxstatement-nl-ing',
      version=version,
      author="Gert-Jan Paulissen",
      author_email="gert.jan.paulissen@gmail.com",
      url="https://github.com/gpaulissen/ofxstatement-nl-ing",
      description=("OFXStatement plugin for ING Netherlands"),
      long_description=long_description,
      long_description_content_type='text/markdown',
      license="GPLv3",
      keywords=["ofx", "banking", "statement"],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          'ofxstatement':
          ['ingnl = ofxstatement.plugins.ingnl:IngNlPlugin']
          },
      install_requires=['ofxstatement'],
      extras_require={'test': ["pytest"]},
      include_package_data=True,
      zip_safe=True
      )
