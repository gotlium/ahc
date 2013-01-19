__author__ = 'gotlium'

from unittest import TestCase
import os

from libraries.configs import Configs


class SendmailTestCase(TestCase, Configs):

	def __exec(self, cmd):
		execution_code = os.system('%s 1> /dev/null' % cmd)
		self.assertEquals(execution_code, 0)

	def setUp(self):
		self.loadConfigs()

	def test_a_sendmail_install(self):
		self.__exec('ahc -m install -s sendmail')

	def test_b_sendmail_send(self):
		self.__exec('/usr/bin/php -r \'mail("root@localhost", "test", "hello, world!");\'')

	def test_c_sendmail_send(self):
		self.assertEqual(os.unlink(self.sendmail['bin']), None)
