#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging

def CallFunction(func):
	def wrapper(*args, **kwargs):
		logging.debug(func.__name__ + ":\tcall" + str(args) + str(kwargs))
		result = func(*args, **kwargs)
		logging.debug(func.__name__ + ":\treturn " + str(result))
		return result
	return wrapper