__author__ = 'gotlium'

from unittest import TestCase
import os

class GitTestCase(TestCase):

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

	def __delHost(self, host_name):
		self.__addHost(host_name, action='d')


	def test_a_add_git_domain(self):
		self.__addHost('git.dev')
		self.__addRepository('git.dev')

	def test_b_add_git_sub_domain(self):
		self.__addHost('sub.git.dev')
		self.__addRepository('sub.git.dev')


	def test_c_del_git_sub_domain(self):
		self.__delRepository('sub.git.dev')
		self.__delHost('sub.git.dev')

	def test_d_del_git_domain(self):
		self.__delRepository('git.dev')
		self.__delHost('git.dev')
