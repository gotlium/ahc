__author__ = 'gotlium'

from unittest import TestCase
from ftplib import FTP
import os

class FtpTestCase(TestCase):

	def __makeConnection(self, user, password):
		ftp = FTP('localhost', user, password, timeout=1)
		self.assertEqual(ftp.nlst()[0], 'www')
		ftp.quit()

	def __addUser(self, host_name, user, password, action='a'):
		execution_code = os.system('ahc -m ftp -%s %s -u %s -p %s -y 1> /dev/null' %\
								   (action, host_name, user, password))
		self.assertEquals(execution_code, 0)

	def __delUser(self, host_name, user, password):
		self.__addUser(host_name, user, password, 'd')


	def __addHost(self, host_name, type='php', action='a'):
		execution_code = os.system('ahc -m apache -t %s -%s %s -y 1> /dev/null' %\
								   (type, action, host_name))
		self.assertEquals(execution_code, 0)

	def __delHost(self, host_name):
		self.__addHost(host_name, action='d')


	def test_a_add_ftp_db_domain(self):
		host = 'ftp.dev'
		user = 'ftp_user1'
		password = 'ftp_password1'

		self.__addHost(host)
		self.__addUser(host, user, password)
		self.__makeConnection(user, password)

	def test_b_add_ftp_db_sub_domain(self):
		host = 'sub.ftp.dev'
		user = 'ftp_user2'
		password = 'ftp_password2'

		self.__addHost(host)
		self.__addUser(host, user, password)
		self.__makeConnection(user, password)


	def test_c_del_ftp_db_sub_domain(self):
		self.__delHost('sub.ftp.dev')
		self.__delUser(
			'sub.ftp.dev', 'ftp_user2', 'ftp_password2'
		)

	def test_d_del_ftp_db_domain(self):
		self.__delHost('ftp.dev')
		self.__delUser(
			'ftp.dev', 'ftp_user1', 'ftp_password1'
		)
