'''
Created on Aug 22, 2014

@author: chris
'''
import logging
import gobject
import dbus.service
import netifaces
import subprocess

from toto.vpn.constants import *


class Watcher(dbus.service.Object):
	
	def __init__(self, bus_name, path, config=None):
		dbus.service.Object.__init__(self, bus_name, path)
		self.__logger = logging.getLogger('Watcher')
		self.__set_config(config)
		self.__if_parent_up = False
		self.__if_vpn_up = False
		gobject.timeout_add(self.__config[CFG_WATCHER_POLLING_PERIOD], self.__update_state)
	
	@dbus.service.signal(DBUS_INT_NAME_WATCHER, signature='bb')
	def state_changed(self, if_parent_up, if_vpn_up):
		self.__logger.info('state_changed: (parent_up=%s, vpn_up=%s)' % (if_parent_up, if_vpn_up))
	
	@dbus.service.method(DBUS_INT_NAME_WATCHER, in_signature = '', out_signature = 'b')
	def is_if_parent_up(self):
		return self.__if_parent_up
	
	@dbus.service.method(DBUS_INT_NAME_WATCHER, in_signature = '', out_signature = 'b')
	def is_if_vpn_up(self):
		return self.__if_vpn_up
	
	def __set_config(self, config):
		self.__config = DEFAULT_CFG.copy()
		if isinstance(config, dict):
			if (CFG_IF_PARENT in config) and isinstance(config[CFG_IF_PARENT], basestring):
				self.__config[CFG_IF_PARENT] = config[CFG_IF_PARENT]
			else:
				self.__logger.warning('Using default configuration if_parent')
				
			if (CFG_IF_VPN in config) and isinstance(config[CFG_IF_VPN], basestring):
				self.__config[CFG_IF_VPN] = config[CFG_IF_VPN]
			else:
				self.__logger.warning('Using default configuration if_vpn')

			if (CFG_WATCHER_POLLING_PERIOD in config) and isinstance(config[CFG_WATCHER_POLLING_PERIOD], basestring):
				self.__config[CFG_WATCHER_POLLING_PERIOD] = int(config[CFG_WATCHER_POLLING_PERIOD])
			else:
				self.__logger.warning('Using default configuration ping_host')
				
			if (CFG_WATCHER_PING_HOST in config) and isinstance(config[CFG_WATCHER_PING_HOST], basestring):
				self.__config[CFG_WATCHER_PING_HOST] = config[CFG_WATCHER_PING_HOST]
			else:
				self.__logger.warning('Using default configuration ping_host')
		else:
			self.__logger.warning('No configuration provided, using default')
	
	def __update_state(self):
		self.__logger.debug('__update_state')
		# Saves the current status
		old_parent_up = self.__if_parent_up
		old_vpn_up = self.__if_vpn_up
		# Updates the new status
		if self.__check_if(self.__config[CFG_IF_PARENT]):
			self.__if_parent_up = True
			if self.__check_if(self.__config[CFG_IF_VPN]) == True:
				self.__if_vpn_up = self.__check_ping()
			else:
				self.__if_vpn_up = False
		else:
			self.__if_parent_up = False
			self.__if_vpn_up = False
		# Raises the changed event if needed
		if (self.__if_parent_up != old_parent_up) or (self.__if_vpn_up != old_vpn_up):
			self.state_changed(self.__if_parent_up, self.__if_vpn_up)
		# Required to continue...
		return True
	
	def __check_ping(self):
		'''
		True if the configured host is ping successfully, False otherwise.
		'''
		self.__logger.debug('__check_ping')
		p = subprocess.Popen(['fping', self.__config[CFG_WATCHER_PING_HOST]],
			stdout=subprocess.PIPE,	stderr=subprocess.PIPE)
		out, err = p.communicate()
		
		result = not err and out.strip().endswith('alive')
		if not result:
			self.__logger.info('__check_ping failed: %s' % out.strip())
			
		return result
	
	def __check_if(self, if_name):
		'''
		None if no interface found.
		Otherwise, True if the interface is up, False otherwise
		'''
		self.__logger.debug('__check_if %s' % if_name)
		result = None
		
		if (if_name in netifaces.interfaces()):
			# The interface has been found...
			result = False
			
			# ... Checks if it has an IP address
			try:
				if_data = netifaces.ifaddresses(if_name)
				if netifaces.AF_INET in if_data:
					if_inets = if_data[netifaces.AF_INET]
					if (len(if_inets) > 0):
						if_inet = if_inets[0]
						if ('addr' in if_inet) and if_inet['addr']:
							result = True
			except ValueError:
				self.__logger.debug("Interface %s disappeared" % if_name)
				result = None
			
		return result
	