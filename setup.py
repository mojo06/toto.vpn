#!/usr/bin/python2
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
   name='toto.vpn',
   version='1.1',
   packages=find_packages(),
   package_data={
      '': ['ez_setup.py'],
      'toto.vpn.indicator': ['images/*.png'],
   },
   scripts=[
    'scripts/install_dependencies.sh',
    'scripts/deploy_configuration.sh'],
      
   author = 'chris',
   author_email = 'christophe.tomasini@gmail.com',
   description = 'VPN stuff...',
   license = 'GNU GPL 2.0',
   keywords = 'VPN'
)
