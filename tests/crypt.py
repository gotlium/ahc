__author__ = 'gotlium'

from unittest import TestCase
import os

class CryptTestCase(TestCase):

	def __exec(self, action):
		execution_code = os.system('ahc -m crypt -a %s 1> /dev/null' % action)
		self.assertEquals(execution_code, 0)

	def test_a_install_domain(self):
		self.__exec('e')

	def test_b_unmount_domain(self):
		self.__exec('u')

	def test_c_mount_domain(self):
		self.__exec('m')

	def test_d_decrypt_domain(self):
		self.__exec('d')
