__author__ = 'gotlium'

from os import path, remove

def fileExists(filename):
	return path.exists(filename)

def putFile(filename, text, mode = 'w'):
	try:
		f = open(filename, mode)
		if text:
			print >> f, text
		f.close()
		return True
	except Exception, msg:
		return False

def delFile(filename):
	try:
		if fileExists(filename):
			remove(filename)
			return True
	except Exception, msg: pass
	return False

def getFile(filename):
	if fileExists(filename):
		return '' . join(open(filename).readlines())
	else:
		return ""

def getFileArr(filename):
	if fileExists(filename):
		return map(lambda x: x.strip(), open(filename).readlines())
	else:
		return ""
