'''
Created on Aug 27, 2014

@author: chris
'''
import os

path = os.path.abspath(__file__)
indicator_path = os.path.dirname(path)

ICON_THEME_PATH = os.path.join(indicator_path, 'images')
ICON_STATUS_WHITE = "vpn-status-white"
ICON_STATUS_GREEN = "vpn-status-green"
ICON_STATUS_RED = "vpn-status-red"
ICON_STATUS_PURPLE = "vpn-status-purple"
ICON_STATUS_ORANGE = "vpn-status-orange"
