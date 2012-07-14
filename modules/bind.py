__author__ = 'gotlium'

from datetime import date

from libraries.helpers import *
from libraries.fs import *

class Bind(object):

	methods = ('add', 'delete',)
	base = None

	def __init__(self, base):
		self.base = base
		self.config = self.base.bind9
		checkInstall(self.config, {
			self.config['bin_rndc']: 'Bind not installed!'
		})

	def __getFile(self, host_name):
		return '%s/%s' % (self.config['etc'], host_name)

	def __addToMyZone(self, host_name):
		config = {
			'hostname': host_name,
			'bind_dir': self.config['etc']
		}
		template = getTemplate('bind9-zone') % config
		return putFile(
			self.config['zones'],
			template,
			'a'
		)

	def __saveZoneAfterCut(self, pattern, zones_file):
		zones = getFile(zones_file)
		new_zones = re.sub(
			pattern, '', zones, 0, re.MULTILINE|re.DOTALL
		)
		return putFile(zones_file, new_zones)

	def __delFromMyZone(self, host_name):
		return self.__saveZoneAfterCut(
			'^zone[\s]\"%s\".*?\}\;$' % host_name,
				self.config['zones']
		)

	def __reloadBind(self):
		service_restart(self.config['init'])
		service_restart(self.config['bin_rndc'], 'reload')

	def __addSubDomain(self, host_name):
		host_name = host_name.split('.')
		sub_domain = host_name[0]
		base_host = '.' . join(host_name[1:])
		zone_file = self.__getFile(base_host)
		if not fileExists(zone_file):
			self.add(base_host)
		elif re.findall(
			r'^%s.*?IN[\s]A[\s]127.0.0.1$' % sub_domain,
			getFile(zone_file), re.MULTILINE|re.DOTALL
		):
			error_message('Subdomain already added!')
		return putFile(zone_file, '%s\t\tIN A %s' %
						(sub_domain, self.base.options.ip), 'a')

	def __delSubDomain(self, host_name):
		host_name = host_name.split('.')
		base_host = '.' . join(host_name[1:])
		sub_domain = host_name[0]
		zone_file = self.__getFile(base_host)
		if not fileExists(zone_file):
			error_message('Zone file not exists!')
		return self.__saveZoneAfterCut(
			'^%s.*?IN[\s]A[\s][0-9.]+$' % sub_domain, zone_file
		)

	def __isSubDomain(self, host_name):
		return len(host_name.split('.')) == 3

	def add(self, host_name):
		isHost(host_name)
		filename = self.__getFile(host_name)
		if not self.base.options.ip:
			error_message("IP address not set!")
		elif not isValidIp(self.base.options.ip):
			error_message("IP not valid!")
		if self.__isSubDomain(host_name):
			if not self.__addSubDomain(host_name):
				error_message("Error, when saving zone configuration!")
		elif fileExists(filename):
			error_message("Zone is exists!")
		else:
			config = {
				'hostname': host_name,
				'hostip': self.base.options.ip,
				'datetime': str(date.today().strftime("%Y%m%d"))
			}
			configuration = getTemplate('bind9') % config
			putFile(filename, configuration)
			if not self.__addToMyZone(host_name):
				error_message("Error, when saving zone configuration!")
		self.__reloadBind()
		info_message("Host successfully added.")

	def delete(self, host_name):
		isHost(host_name)
		filename = self.__getFile(host_name)
		if self.__isSubDomain(host_name):
			if not self.__delSubDomain(host_name):
				error_message("Error, when saving zone configuration!")
		else:
			if not fileExists(filename):
				error_message("Zone is not exists!")
			delFile(filename)
			if not self.__delFromMyZone(host_name):
				error_message("Error, when saving zone configuration!")
		self.__reloadBind()
		info_message("Host successfully removed.")
