'''
Created on Oct 10, 2014

@author: chris
'''
from ..constants import *


def read_config():
   '''
   Reads the toto.vpn configuration file as a dict.
   '''
   config = {}
   with open(BASE_CONF) as f:
      for line in f:
         line = line.strip()
         if line and not line.startswith('#'):
            k, v = line.split('=', 1)
            config[k.strip()] = v.strip().strip('"')
   return config


if __name__ == '__main__':
   try:
      config = read_config()
   except Exception as e:
      print 'Failed to read configuration: %s' % e
