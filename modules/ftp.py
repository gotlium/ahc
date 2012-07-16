__author__ = 'gotlium'

import MySQLdb

from libraries.helpers import *
from libraries.fs import *
from libraries.path import HostPath

class Ftp(HostPath):

	methods = ('add', 'delete',)
	base = None

	def __init__(self, base):
		self.base = base
		self.config = self.base.vsftpd
		self.db = MySQLdb.connect(
			self.config['db_host'],
			self.config['db_user'],
			self.config['db_password'],
			self.config['db_name']
		)
		self.cursor = self.db.cursor()
		self.user_config_dir = self.config['user_config_dir']
		checkInstall(self.config, {
			self.user_config_dir: 'User configuration folder do not exists!'
		})

	def __userExists(self, login):
		self.cursor.execute(
			"SELECT `username` FROM `accounts` WHERE `username` = '%s'" % login
		)
		return self.cursor.rowcount

	def __addUserConfig(self, user, folder):
		userFile = '%s/%s' % (self.user_config_dir, user)
		if not putFile(userFile, 'local_root=%s' % folder):
			error_message("Can't save user config!")

	def __delUserConfig(self, user):
		userFile = '%s/%s' % (self.user_config_dir, user)
		if not delFile(userFile):
			error_message("Can't remove user config!")

	def __getFolder(self, host_name):
		data = self.getExistsHostData(host_name)
		folder = data['domain_dir']
		if self.base.options.disable: # where disable = folder
			folder = self.base.options.disable
		return folder


	def add(self, host_name):
		isHost(host_name)
		login = host_name
		password = host_name
		folder = self.__getFolder(host_name)
		if self.base.options.user:
			login = self.base.options.user
		if self.base.options.password:
			password = self.base.options.password

		if fileExists(folder):
			if not self.__userExists(login):
				self.cursor.execute(
					"INSERT INTO `accounts` (`username`, `pass`) \
						VALUES('%s', PASSWORD('%s'))" % (login, password)
				)
				self.__addUserConfig(login, folder)
				info_message(
					"User '%s' successfully added! Password: %s" % (login, password)
				)
				service_restart(self.config['init'])
			else:
				error_message("Login already used!")
		else:
			error_message("Project folder not found!")

	def delete(self, host_name):
		isHost(host_name)
		login = host_name
		if self.base.options.user:
			login = self.base.options.user
		if not self.__userExists(login):
			error_message("User not found!")
		else:
			self.cursor.execute(
				"DELETE FROM `accounts` WHERE `username` = '%s'" % login
			)
			self.__delUserConfig(login)
			info_message("User '%s' - successfully removed." % login)
			service_restart(self.config['init'])

	def __del__(self):
		if self.db:
			self.db.commit()
			self.db.close()
