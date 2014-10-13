import os, os.path
import logging


toto_vpn_dir = os.path.expanduser('~/.toto.vpn')
if not os.path.isdir(toto_vpn_dir):
   os.mkdir(toto_vpn_dir)
   
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
   filename=os.path.join(toto_vpn_dir, 'watcher.log'),
   format='%(asctime)s %(message)s',
   level=logging.INFO)
