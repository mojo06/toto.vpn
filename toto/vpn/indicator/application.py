'''
Created on Aug 24, 2014

@author: chris
'''
import sys
import time
import logging
import appindicator
import gtk
import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop

from toto.vpn.constants import *
from .status import *


class Application:

   def __init__(self):
      self.__logger = logging.getLogger('Application')
      self.__logger.info("Starting...")
      # Base state
      self.__status = STATUS_UNKNOWN
      self.__active = None
      self.__if_parent_up = None
      self.__if_vpn_up = None
      self.__vpn_connecting = None
      self.__message = "..."
      # UI
      self.__init_ui()
      self.__update_ui()
      # Connection to DBUS objects
      self.__init_watcher()
      self.__init_keeper()

   ########## Initialization ##########
   
   def __init_ui(self):
      self.__logger.debug('__init_ui')
      self.__indicator = appindicator.Indicator("debian-doc-menu", "", appindicator.CATEGORY_APPLICATION_STATUS)
      self.__indicator.set_icon_theme_path(ICON_THEME_PATH)
      self.__indicator.set_status(appindicator.STATUS_ACTIVE)
      self.__menu = gtk.Menu()
      self.__indicator.set_menu(self.__menu)
      # item parent status
      self.__item_if_parent = gtk.CheckMenuItem("Parent")
      self.__item_if_parent.set_sensitive(False)
      self.__item_if_parent.show()
      self.__menu.append(self.__item_if_parent)
      # item VPN status
      self.__item_if_vpn = gtk.CheckMenuItem("VPN")
      self.__item_if_vpn.set_sensitive(False)
      self.__item_if_vpn.show()
      self.__menu.append(self.__item_if_vpn)
      # item message
      self.__item_message = gtk.MenuItem()
      self.__item_message.set_sensitive(False)
      self.__item_message.show()
      self.__menu.append(self.__item_message)
      # separator
      separator = gtk.SeparatorMenuItem()
      separator.show()
      self.__menu.append(separator)
      # item active
      self.__item_active = gtk.CheckMenuItem("Active")
      self.__item_active.connect("toggled", self.__on_active)
      self.__item_active.show()
      self.__menu.append(self.__item_active)
      # separator
      separator = gtk.SeparatorMenuItem()
      separator.show()
      self.__menu.append(separator)
      # item quit
      self.__item_quit = gtk.MenuItem("Quit")
      self.__item_quit.connect("activate", self.__on_quit)
      self.__item_quit.show()
      self.__menu.append(self.__item_quit)
   
   def __init_watcher(self):
      self.__logger.debug('__init_watcher')
      attempt = 0
      done = False
      bus = dbus.SessionBus()
      while (not done) and (attempt < 3):
         try:
            attempt += 1
            proxy = bus.get_object(DBUS_SVC_NAME_WATCHER, DBUS_OBJ_PATH_WATCHER)
            self.__watcher = dbus.Interface(proxy, dbus_interface=DBUS_INT_NAME_WATCHER)
            # Gets current parent/vpn status
            parent_up = self.__watcher.is_if_parent_up()
            vpn_up = self.__watcher.is_if_vpn_up()
            self.__on_watcher_state_changed(parent_up, vpn_up)
            # Connects to status changed events
            self.__watcher.connect_to_signal('state_changed', self.__on_watcher_state_changed)
         except Exception as e:
            self.__logger.warning('Attempt(%s) to initialize watcher failed: %s' % (attempt, e))
            time.sleep(DBUS_RETRY_DELAY)
         else:
            done = True
      if not done:
         self.__logger.error('Failed to initialize watcher')
   
   def __init_keeper(self):
      self.__logger.debug('__init_keeper')
      attempt = 0
      done = False
      bus = dbus.SessionBus()
      while (not done) and (attempt < 3):
         try:
            attempt += 1
            proxy = bus.get_object(DBUS_SVC_NAME_KEEPER, DBUS_OBJ_PATH_KEEPER)
            self.__keeper = dbus.Interface(proxy, dbus_interface=DBUS_INT_NAME_KEEPER)
            # Gets current parent/vpn status
            connecting = self.__keeper.is_connecting()
            self.__on_keeper_state_changed(connecting)
            # Connects to status changed events
            self.__keeper.connect_to_signal('state_changed', self.__on_keeper_state_changed)
         except Exception as e:
            self.__logger.warning("Attempt(%s) to initialize keeper failed: %s" % (attempt, e))
            time.sleep(DBUS_RETRY_DELAY)
         else:
            done = True
      if not done:
         self.__logger.error('Failed to initialize keeper')
   
   ##########
   
   def __activate(self):
      if self.__active == False:
         self.__logger.info("Activation")
         self.__active = True
         self.__keeper.activate()
         self.__update_ui()
   
   def __deactivate(self):
      if self.__active == True:
         self.__logger.info("Deactivation")
         self.__active = False
         self.__keeper.deactivate()
         self.__update_ui()
   
   def __set_status(self, status):
      self.__logger.debug('__set_status(%s)' % status)
      assert isinstance(status, Status)
      if (status != self.__status):
         self.__logger.info("Status changed to %s" % status)
         self.__status = status
         self.__update_ui()
         return True
      return False
         
   def __update_ui(self):
      self.__logger.debug('__update_ui')
      # Status menu items
      self.__item_if_parent.set_active(self.__if_parent_up == True)
      self.__item_if_vpn.set_active(self.__if_vpn_up == True)
      self.__item_message.set_label(self.__message)
      # active check menu items
      if (self.__active == None):
         self.__item_active.set_sensitive(False)
         self.__item_active.set_active(False)
      else:
         self.__item_active.set_sensitive(True)
         self.__item_active.set_active(self.__active)
      # app icon
      if (self.__active):
         self.__indicator.set_icon(self.__status.get_icon())
      else:
         self.__indicator.set_icon(STATUS_UNKNOWN.get_icon())
   
   def __on_watcher_state_changed(self, parent_up, vpn_up):
      self.__logger.debug('__on_watcher_state_changed(%s, %s)' % (parent_up, vpn_up))
      self.__if_parent_up = parent_up
      self.__if_vpn_up = vpn_up
      # Activation on first VPN status received
      if (self.__active == None):
         self.__active = True
      # Updates status
      self.__update_status()
   
   def __on_keeper_state_changed(self, connecting):
      self.__logger.debug('__on_keeper_state_changed(%s)' % connecting)
      self.__vpn_connecting = connecting
      self.__update_status()
   
   def __update_status(self):
      self.__logger.debug('__update_status')
      if not self.__active:
         new_status = STATUS_UNKNOWN
      if not self.__if_parent_up:
         new_status = STATUS_PARENT_KO 
      elif self.__if_vpn_up:
         new_status = STATUS_CONNECTED
      elif self.__vpn_connecting:
         new_status = STATUS_CONNECTING
      else:
         new_status = STATUS_VPN_KO
      changed = self.__set_status(new_status)
   
   ########## Menus event handlers ##########
   
   def __on_active(self, widget, data=None):
      self.__logger.debug('__on_active')
      if (self.__item_active.get_active()):
         self.__activate()
      else:
         self.__deactivate()
   
   def __on_quit(self, widget, data=None):
      self.__logger.debug('__on_quit')
      ##self.__deactivate()
      sys.exit(0)


if __name__ == "__main__":   
   # Allows gobject.idle_add for UI modification
   gobject.threads_init()
   
   DBusGMainLoop(set_as_default=True)
   
   # Initializes the indicator and runs it
   indicator = Application()
   
   gtk.main()