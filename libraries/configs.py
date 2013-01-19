__author__ = 'gotlium'

from ConfigParser import RawConfigParser
from helpers import fileExists

class Configs(object):

	def loadConfig(self):
		if fileExists('configs-local.cfg'):
			self.config.read('configs-local.cfg')
		else:
			self.config.read('configs.cfg')

	def loadConfigs(self):
		self.config = RawConfigParser()
		self.loadConfig()
		for section in self.config.sections():
			sectionAttr = {}
			for item in self.config.items(section):
				sectionAttr[item[0]] = item[1]
			self.__setattr__(section, sectionAttr)
