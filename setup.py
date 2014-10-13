#!/usr/bin/python2
#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages

setup(
   name='toto.vpn',
   version='1.0',
   packages=find_packages(),
   package_data={
      'toto.vpn.indicator': ['images/*.png'],
   },
   author = 'chris',
   author_email = 'christophe.tomasini@gmail.com',
   description = 'VPN stuff...',
   license = 'to kill',
   keywords = 'VPN'
)
