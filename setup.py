""" Setup personal packages for import statements """
from setuptools import setup, find_packages

setup(name='migrate_helper_scripts', version='1.0', packages=find_packages(),
      install_requires=['sh'])
