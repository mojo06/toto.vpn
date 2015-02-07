'''
Created on Aug 27, 2014

@author: chris
'''

BASE_CONF='/etc/toto.vpn/base.conf'
CFG_IF_PARENT = 'IF_MAIN'
CFG_IF_VPN = 'IF_VPN'
CFG_VPN_CONN_ID = 'VPN_CONN_ID'
CFG_WATCHER_POLLING_PERIOD = 'WATCHER_POLLING_PERIOD'
CFG_WATCHER_PING_HOST = 'WATCHER_PING_HOST'
CFG_KEEPER_RETRY_DELAY = 'KEEPER_RETRY_DELAY'
DEFAULT_CFG = {
   CFG_IF_PARENT: 'wlan0',
   CFG_IF_VPN: 'tun0',
   CFG_VPN_CONN_ID: 'SE-openvpn.ovpn',
   CFG_WATCHER_POLLING_PERIOD: 30000,
   CFG_WATCHER_PING_HOST: 'google.com',
   CFG_KEEPER_RETRY_DELAY: 30000
}


DBUS_RETRY_DELAY = 5

DBUS_SVC_NAME_WATCHER = 'toto.vpn.watcher'
DBUS_OBJ_PATH_WATCHER = '/toto/vpn/watcher/Watcher'
DBUS_INT_NAME_WATCHER = 'toto.vpn.watcher.Watcher'

DBUS_SVC_NAME_KEEPER = 'toto.vpn.keeper'
DBUS_OBJ_PATH_KEEPER = '/toto/vpn/keeper/Keeper'
DBUS_INT_NAME_KEEPER = 'toto.vpn.keper.Keeper'