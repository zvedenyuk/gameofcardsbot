# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('GoC')
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(asctime)s %(levelname)-7s %(funcName)15s:%(lineno)3d ☄️  %(message)s',"%d.%m %H:%M:%S")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
logger.setLevel(logging.DEBUG)

def fir(u):
	try:
		with open(u, 'r') as f:
			return f.read()
	except: return ""
def fiw(u,s):
	with open(u, 'w') as f:
		f.write(s)
def fia(u,s):
	with open(u, 'a') as f:
		f.write(s)
