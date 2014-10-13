'''
Created on Aug 22, 2014

@author: chris
'''
import logging
import gobject
import dbus.service
import NetworkManager as nm

from toto.vpn.constants import *
from toto.vpn.handler.base_handler import BaseHandler


class Keeper(BaseHandler):
   
   def __init__(self, bus_name, object_path, config=None):
      BaseHandler.__init__(self, bus_name, object_path, 'Keeper')
      # Default values
      self.__active = True
      self.__connecting = False
      self.__vpn_aconn = None
      # Initializations: config and timer if needed
      self.__init_config(config)
      # Initializes the watcher's connection
      self._init_watcher()
   
   ##### DBUS interface #####
   
   @dbus.service.signal(DBUS_INT_NAME_KEEPER, signature='b')
   def state_changed(self, connecting):
      self._logger.info('state_changed(connecting=%s)' % connecting)
   
   @dbus.service.method(DBUS_INT_NAME_KEEPER, in_signature = '', out_signature = 'b')
   def is_active(self):
      return self.__active
   
   @dbus.service.method(DBUS_INT_NAME_KEEPER, in_signature = '', out_signature = 'b')
   def is_connecting(self):
      return self.__connecting
   
   @dbus.service.method(DBUS_INT_NAME_KEEPER, in_signature = '', out_signature = '')
   def activate(self):
      if not self.__active:
         self._logger.debug('activate')
         self.__active = True
         # Following the activation, Will connect the VPN if needed
         if self.is_parent_up() and not self.is_vpn_up():
            self.__begin_connect_vpn()
   
   @dbus.service.method(DBUS_INT_NAME_KEEPER, in_signature = '', out_signature = '')
   def deactivate(self):
      if self.__active:
         self._logger.debug('deactivate')
         self.__active = False
         self.__set_connecting(False)
   
   ##### Implementation of BaseHandler #####
   
   def _handle_vpn_state_initialized(self):
      self._logger.debug('_handle_vpn_state_initialized')
      # Launches the connection process if needed
      if self.is_parent_up() and not self.is_vpn_up():
         self.__begin_connect_vpn()
   
   def _handle_vpn_state_changed(self):
      self._logger.debug('_handle_vpn_state_changed')
      # Launches the reconnection process if needed
      if self.is_parent_up() and not self.is_vpn_up():
         self.__begin_connect_vpn()
      else:
         self.__set_connecting(False)
   
   ##### Internal methods #####
            
   def __init_config(self, config):
      self.__config = DEFAULT_CFG.copy()
      if isinstance(config, dict):
         if (CFG_IF_PARENT in config) and isinstance(CFG_IF_PARENT, basestring):
            self.__config[CFG_IF_PARENT] = config[CFG_IF_PARENT]
         else:
            self._logger.warning('Using default configuration %s=%s' % (CFG_IF_PARENT, self.__config[CFG_IF_PARENT]))
            
         if (CFG_IF_VPN in config) and isinstance(CFG_IF_VPN, basestring):
            self.__config[CFG_IF_VPN] = config[CFG_IF_VPN]
         else:
            self._logger.warning('Using default configuration %s=%s' % (CFG_IF_VPN, self.__config[CFG_IF_VPN]))
         
         if (CFG_VPN_CONN_ID in config) and isinstance(CFG_VPN_CONN_ID, basestring):
            self.__config[CFG_VPN_CONN_ID] = config[CFG_VPN_CONN_ID]
         else:
            self._logger.warning('Using default configuration %s=%s' % (CFG_VPN_CONN_ID, self.__config[CFG_VPN_CONN_ID]))
            
         if (CFG_KEEPER_RETRY_DELAY in config) and isinstance(CFG_KEEPER_RETRY_DELAY, basestring):
            self.__config[CFG_KEEPER_RETRY_DELAY] = int(config[CFG_KEEPER_RETRY_DELAY])
         else:
            self._logger.warning('Using default configuration %s=%s' % (CFG_KEEPER_RETRY_DELAY, self.__config[CFG_KEEPER_RETRY_DELAY]))
      else:
         self._logger.warning('No configuration provided, using default')
         
   def __begin_connect_vpn(self):
      if self.__active and not self.__connecting:
         self._logger.debug('__begin_connect_vpn')
         # Step 1: deactivate any zombie VPN connection
         self.__deactivate_vpn_connection() 
         # Step 2: launches the (re)connection process
         self.__set_connecting(True)
         gobject.timeout_add(self.__config[CFG_KEEPER_RETRY_DELAY], self.__try_connect_vpn)
   
   def __try_connect_vpn(self):
      # Only triggers a connection if the parent connection is up and the VPN connection is down
      if self.__active and self.__connecting:
         self._logger.debug('__try_connect_vpn')
         # Requests to activate the VPN connection
         self.__activate_vpn_connection()
         # Will retry until watcher notifies VPN is ok...
         return True
      return False
   
   def __set_connecting(self, connecting):
      if (connecting != self.__connecting):
         self.__vpn_aconn = None
         self.__connecting = connecting
         self.state_changed(connecting)
   
   def __activate_vpn_connection(self):
      '''
      Requests NM to activate the configured VPN connection.
      '''
      if self.__vpn_aconn:
         try:
            if self.__vpn_aconn.VpnState == nm.NM_VPN_CONNECTION_STATE_ACTIVATED:
               self._logger.info("VPN %s connected" % self.__config[CFG_VPN_CONN_ID])
               self.__vpn_aconn = None
            else:
               self._logger.info("VPN %s connecting" % self.__config[CFG_VPN_CONN_ID])
            # Nothing more to do for this loop...
            return
         except:
            self._logger.info("VPN %s connection failed" % self.__config[CFG_VPN_CONN_ID])
            self.__vpn_aconn = None
      
      # Finds the connection object corresponding to the configured VPN connection id
      vpn_conn = None
      settings_conns = nm.Settings.ListConnections()
      for conn in settings_conns:
         config = conn.GetSettings()['connection']
         if (config['type'] == 'vpn') and (config['id'] == self.__config[CFG_VPN_CONN_ID]):
            vpn_conn = conn;
            break
      
      # If found, requests NM to activate the VPN connection
      if vpn_conn:
         self._logger.info('Requesting to activate VPN connection %s' % self.__config[CFG_VPN_CONN_ID])
         aconn = nm.NetworkManager.ActivateConnection(vpn_conn, '/', '/')
         self.__vpn_aconn = nm.VPNConnection(aconn.object_path)
      else:
         self._logger.warning('No VPN connection %s found in NetworkManager' % self.__config[CFG_VPN_CONN_ID])
   
   def __deactivate_vpn_connection(self):
      '''
      If an active VPN connection is found, it is deactivated.
      Note: at this point, the active VPN connection is probably already dead (but NM apparently does not know).
      '''
      active_conns = nm.NetworkManager.ActiveConnections
      for active_conn in active_conns:
         if active_conn.Vpn:
            self._logger.info('Deactivating zombie VPN connection')
            nm.NetworkManager.DeactivateConnection(active_conn)
   