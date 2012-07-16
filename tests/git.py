__author__ = 'gotlium'

from unittest import TestCase
import os

class GitTestCase(TestCase):

	domains = {
		0: {
			'host': 'git.dev', 'type': 'php'
		},
		1: {
			'host': 'sub.git.dev', 'type': 'php'
		},
		2: {
			'host': 'djgit.dev', 'type': 'django'
		},
		3: {
			'host': 'sub.djgit.dev', 'type': 'django'
		}
	}

	def __addRepository(self, host_name, action='a'):
		execution_code = os.system('ahc -m git -%s %s 1> /dev/null' %\
								   (action, host_name))
		self.assertEquals(execution_code, 0)

	def __delRepository(self, host_name):
		self.__addRepository(host_name, 'd')


	def __addHost(self, host_name, type='php', action='a'):
		execution_code = os.system('ahc -m apache -t %s -%s %s -y 1> /dev/null' %\
								   (type, action, host_name))
		self.assertEquals(execution_code, 0)

	def __delHost(self, host_name, type='php'):
		self.__addHost(host_name, type, 'd')

	def __add(self, key):
		data = self.domains[key]
		self.__addHost(data['host'], data['type'])
		self.__addRepository(data['host'])

	def __del(self, key):
		data = self.domains[key]
		self.__delRepository(data['host'])
		self.__delHost(data['host'], data['type'])


	def test_a_add_git_domain(self):
		self.__add(0)

	def test_b_add_git_sub_domain(self):
		self.__add(1)

	def test_c_add_git_domain(self):
		self.__add(2)

	def test_d_add_git_sub_domain(self):
		self.__add(3)


	def test_e_del_git_sub_domain(self):
		self.__del(1)

	def test_f_del_git_domain(self):
		self.__del(0)

	def test_g_del_git_sub_domain(self):
		self.__del(3)

	def test_h_del_git_domain(self):
		self.__del(2)
