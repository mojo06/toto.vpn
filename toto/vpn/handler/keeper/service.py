#!/usr/bin/env python
'''
Created on Aug 22, 2014

@author: chris
'''
import logging
import gobject
import dbus;
from dbus.mainloop.glib import DBusGMainLoop

from toto.vpn.constants import *
import toto.vpn.util.configuration as configuration
from .keeper import Keeper


if __name__ == '__main__':
   logger = logging.getLogger('keeper')
   try:
      config = configuration.read_config()
      logger.debug("Configuration: %s" % config)
   except Exception as e:
      logger.error('Failed to load configuration: %s' % e)
   
   DBusGMainLoop(set_as_default=True)
   bus = dbus.SessionBus();
   bus_name = dbus.service.BusName(DBUS_SVC_NAME_KEEPER, bus=bus)
   keeper = Keeper(bus_name, DBUS_OBJ_PATH_KEEPER, config)
   loop = gobject.MainLoop()
   loop.run()
