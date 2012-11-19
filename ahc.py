#!/usr/bin/env python

"""ahc.py: Apache Host Control.

Package for manage virtual hosts in Apache2/Nginx/MySQL5/Vsftpd/Bind9.
"""

__author__ = 'GoTLiuM InSPiRIT <gotlium@gmail.com>'
__copyright__ = 'Copyright 2012, GoTLiuM InSPiRiT <gotlium@gmail.com>'
__license__ = "GPL"
__version_info__ = (1, 3, 0)
__version__ = ".".join(map(str, __version_info__))
__maintainer__ = "GoTLiuM InSPiRIT"
__email__ = "gotlium@gmail.com"
__status__ = "Production"
__date__ = "09.07.12"

from optparse import OptionParser
import traceback
from os import path, chdir
from libraries.configs import Configs

from libraries.helpers import *

class Ahc(Configs):

	def __init__(self):
		self.getPathAndChDir()
		self.loadConfigs()
		self.loadParser()
		self.loadModule()

	def getPathAndChDir(self):
		self.base_dir = path.dirname(path.abspath( __file__ ))
		chdir(self.base_dir)

	def loadParser(self):
		parser = self.parser = OptionParser(prog="ahc", version=__version__)
		parser.add_option("-a", "--add", dest="add", metavar="HOSTNAME")
		parser.add_option("-d", "--del", dest="delete", metavar="HOSTNAME")
		parser.add_option("-m", "--module", dest="module",
			help="apache, nginx, mysql, ftp, bind, test", metavar="MODULE")
		parser.add_option("-t", "--type", dest="type",
			help="django, python, php, ruby, ror", metavar="TYPE")
		parser.add_option("-e", "--enable", dest="enable", metavar="HOSTNAME")
		parser.add_option("-f", "--forbid", dest="disable", metavar="HOSTNAME")
		parser.add_option("-u", "--user", dest="user", metavar="USERNAME")
		parser.add_option("-p", "--password", dest="password", metavar="PASSWORD")
		parser.add_option("-s", "--service", dest="service",
			help="apache2_ssl, nginx_ssl, mysql, ftp, bind, firewall, \
					nginx_proxy, certs, lighttpd, shell, sendmail, mail, all",
					metavar="SERVICE")
		parser.add_option("-i", "--ip", dest="ip", metavar="IP-ADDRESS")
		parser.add_option("-o", "--optimize", action="store_true", dest="optimize")
		parser.add_option("-x", "--protect", action="store_true", dest="protection")
		parser.add_option("-l", "--list", action="store_true", dest="list")
		parser.add_option("-y", "--yes", action="store_true", dest="yes")
		parser.add_option("-w", "--wsgi", action="store_true", dest="wsgi")
		parser.add_option("-b", "--basic-auth", dest="auth",
			metavar="USER:PASS")
		try:
			(self.options, args) = self.parser.parse_args()
		except Exception, msg:
			error_message(msg)

	def loadModule(self):
		if self.options.module is None:
			error_message("Module is not set!")
		module = self.options.module
		try:
			importedModule = __import__(
				'modules.%s' % module.lower(), fromlist="modules"
			)
			ucfirst = lambda s: s[0].upper() + s[1:]
			module_class = getattr(importedModule, ucfirst(module))
		except Exception:
			error_message('Module not found!')
		self.loadAction(module_class(self))

	def loadAction(self, mclass):
		options = vars(self.options)
		for method in mclass.methods:
			if method in options.keys():
				if options[method] is not None:
					call = getattr(mclass, method)
					call(options[method])
					break
		if 'call' not in locals():
			error_message('Specified action for current module is not defined!')

if __name__ == "__main__":
	if not isLinux():
		error_message("Only for Linux!")
	elif not isRoot():
		error_message("Root access required! Login as root.")
	else:
		renameProcess('ahc')
	try:
		Ahc()
	except Exception, msg:
		message = "%s\n%s" % (msg.__str__(), traceback.format_exc())
		info_message(
			'\nCritical error! Please send the message with this problem to maintainer.\n', 'red'
		)
		info_message(message, 'white')
