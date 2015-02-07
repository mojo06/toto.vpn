'''
Created on Aug 27, 2014

@author: chris
'''
from .constants import *

class Status(object):
	
	def __init__(self, ident, string, icon):
		self.__id = ident
		self.__str = string
		self.__icon = icon
	
	def get_icon(self):
		return self.__icon
	
	def __eq__(self, other):
		if other:
			return self.__id == other.__id
		return False
	
	def __ne__(self, other):
		if other:
			return self.__id != other.__id
		return True

	def __str__(self):
		return self.__str
	
	def __repr__(self):
		return "<Status (%s, %s, %s)>" % (self.__id, self.__str, self.__icon)
	
	
STATUS_UNKNOWN = Status(0, "unknown", ICON_STATUS_WHITE)
STATUS_CONNECTED = Status(1, "connected", ICON_STATUS_GREEN)
STATUS_VPN_KO =  Status(2, "vpn_ko", ICON_STATUS_RED)
STATUS_PARENT_KO = Status(3, "parent_ko", ICON_STATUS_PURPLE)
STATUS_CONNECTING = Status(4, "connecting", ICON_STATUS_ORANGE)