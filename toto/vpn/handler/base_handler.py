'''
Created on Sep 1, 2014

@author: chris
'''
import time
import logging
import dbus.service

from toto.vpn.constants import *


class BaseHandler(dbus.service.Object):
	'''
	Base class for handlers. Methods to implement in subclasses are:
	- _handle_vpn_status_initialized()
	- _handle_vpn_status_changed()
	'''

	def __init__(self, bus_name, object_path, logger_name):
		dbus.service.Object.__init__(self, bus_name, object_path)
		self._logger = logging.getLogger('Keeper')
		self.__watcher = None
		self.__parent_up = None
		self.__vpn_up = None
		
	def is_parent_up(self):
		return self.__parent_up
	
	def is_vpn_up(self):
		return self.__vpn_up
		
	def _init_watcher(self):
		self._logger.debug('init_watcher')
		attempt = 0
		done = False
		bus = dbus.SessionBus()
		while (not done) and (attempt < 3):
			try:
				attempt += 1
				proxy = bus.get_object(DBUS_SVC_NAME_WATCHER, DBUS_OBJ_PATH_WATCHER)
				self.__watcher = dbus.Interface(proxy, dbus_interface=DBUS_INT_NAME_WATCHER)
				# Saves the current parent/vpn status
				self.__parent_up = self.__watcher.is_if_parent_up()
				self.__vpn_up = self.__watcher.is_if_vpn_up()
				# Calls the subclass method
				self._handle_vpn_state_initialized()
				# Connects to status changed events
				self.__watcher.connect_to_signal('state_changed', self.__on_watcher_state_changed)
			except Exception as e:
				self._logger.warning('Attempt(%s) to initialize watcher failed: %s' % (attempt, e))
				time.sleep(DBUS_RETRY_DELAY)
			else:
				done = True
		if not done:
			self._logger.error('Failed to initialize watcher')
	
	def __on_watcher_state_changed(self, parent_up, vpn_up):
		self._logger.debug('__on_watcher_state_changed(%s, %s)' % (parent_up, vpn_up))
		# Saves the VPN status
		self.__parent_up = parent_up
		self.__vpn_up = vpn_up
		# Calls the subclass method
		self._handle_vpn_state_changed()
		