__author__ = 'gotlium'

import MySQLdb
import os
from unittest import TestCase

class MysqlTestCase(TestCase):

	def __dbConnect(self, *args, **kwargs):
		db = MySQLdb.connect(*args, **kwargs)
		db.close()

	def __addUser(self, host_name, user, password, action='a'):
		host_name = host_name.replace('.', '_')
		execution_code = os.system('ahc -m mysql -%s %s -u %s -p %s -y 1> /dev/null' %\
								   (action, host_name, user, password))
		self.assertEquals(execution_code, 0)

	def __delUser(self, host_name, user, password):
		self.__addUser(host_name, user, password, 'd')


	def test_a_add_mysql_db_domain(self):
		self.__addUser('mysql.dev', 'username1', 'password1', 'a')
		self.__dbConnect('127.0.0.1', 'username1', 'password1', 'mysql_dev')

	def test_b_add_mysql_db_sub_domain(self):
		self.__addUser('sub.mysql.dev', 'username2', 'password2', 'a')
		self.__dbConnect('127.0.0.1', 'username2', 'password2', 'sub_mysql_dev')


	def test_c_del_mysql_db_sub_domain(self):
		self.__delUser('sub.mysql.dev', 'username2', 'password2')

	def test_d_del_mysql_db_domain(self):
		self.__delUser('mysql.dev', 'username1', 'password1')
