__author__ = 'gotlium'

from unittest import TestCase
import os

class SendmailTestCase(TestCase):

	def __exec(self, cmd):
		execution_code = os.system('%s 1> /dev/null' % cmd)
		self.assertEquals(execution_code, 0)

	def test_a_install_domain(self):
		self.__exec('ahc -m install -s sendmail')

	def test_b_sendmail_domain(self):
		self.__exec('php -r \'mail("root@localhost", "test", "hello, world!");\'')
