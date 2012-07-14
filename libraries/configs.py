__author__ = 'gotlium'

from ConfigParser import RawConfigParser

class Configs(object):

	def loadConfigs(self):
		self.config = RawConfigParser()
		self.config.read('configs.cfg')
		for section in self.config.sections():
			sectionAttr = {}
			for item in self.config.items(section):
				sectionAttr[item[0]] = item[1]
			self.__setattr__(section, sectionAttr)
