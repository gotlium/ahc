__author__ = 'gotlium'

import unittest
from configs import Configs
from human_curl.exceptions import CurlError
import human_curl as hurl
import os
from time import sleep

class CoreHttpTestCase(unittest.TestCase, Configs):

	php_domain = 'php.dev'
	php_sub_domain = 'sub.php.dev'

	python_domain = 'python.dev'
	python_sub_domain = 'sub.python.dev'

	django_domain = 'django.dev'
	django_sub_domain = 'sub.django.dev'

	web_server = 'apache'

	def setUp(self):
		self.loadConfigs()
		sleep(3)

	def __getPage(self, url):
		return hurl.get(url, timeout=1.0, allow_redirects=True)

	def __getProtocols(self):
		protocols = ['http']
		if int(self.main['use_ssl']):
			protocols.append('https')
		return protocols

	def __getUrls(self, host):
		urls = []
		web_server = self.web_server
		if self.web_server == 'apache':
			web_server = 'apache2'
		ports = {
			'http': getattr(self, web_server)['port'],
			'https': getattr(self, web_server)['ssl_port'],
		}
		for protocol in self.__getProtocols():
			urls.append('%s://%s:%s' % (protocol, host, ports[protocol]))
			urls.append('%s://www.%s:%s' % (protocol, host, ports[protocol]))
		return urls

	def _checkHostFound(self, host, content):
		urls = self.__getUrls(host)
		for url in urls:
			request = self.__getPage(url)
			search = lambda str, search: str.lower().find(search.lower())
			self.assertNotEquals(
				search(request.headers['server'], self.web_server), -1
			)
			self.assertNotEquals(
				search(request.content, content), -1
			)
			self.assertEquals(request.status_code, 200)

	def _checkHostNotFound(self, host):
		urls = self.__getUrls(host)
		for url in urls:
			with self.assertRaises(CurlError):
				self.__getPage(url)

	def _addHost(self, type, host_name, flags='', action='a'):
		execution_code = os.system('ahc -m %s -t %s -%s %s %s -y 1> /dev/null' % \
				  (self.web_server, type, action, host_name, flags))
		self.assertEquals(execution_code, 0)

	def _delHost(self, type, host_name, flags=''):
		self._addHost(type, host_name, flags, 'd')

	def _enableHost(self, type, host_name, flags=''):
		self._addHost(type, host_name, flags, 'e')

	def _disableHost(self, type, host_name, flags=''):
		self._addHost(type, host_name, flags, 'f')


	def test_a_add_php_host(self):
		self._addHost('php', self.php_domain)
		self._checkHostFound(self.php_domain, 'PHP:Hello, World!')

	def test_a_add_python_host(self):
		self._addHost('python', self.python_domain)
		self._checkHostFound(self.python_domain, 'Python:Hello, World!')

	def test_a_add_django_host(self):
		self._addHost('django', self.django_domain)
		self._checkHostFound(self.django_domain, "It worked!")


	def test_b_add_php_sub_domain(self):
		self._addHost('php', self.php_sub_domain)
		self._checkHostFound(self.php_sub_domain, 'PHP:Hello, World!')

	def test_b_add_python_sub_domain(self):
		self._addHost('python', self.python_sub_domain)
		self._checkHostFound(self.python_sub_domain, 'Python:Hello, World!')

	def test_b_add_django_sub_domain(self):
		self._addHost('django', self.django_sub_domain)
		self._checkHostFound(self.django_sub_domain, "It worked!")


	def test_c_disable_php_host(self):
		self._disableHost('php', self.php_domain)
		self._checkHostNotFound(self.php_domain)

	def test_c_disable_python_host(self):
		self._disableHost('python', self.python_domain)
		self._checkHostNotFound(self.python_domain)

	def test_c_disable_django_host(self):
		self._disableHost('django', self.django_domain)
		self._checkHostNotFound(self.django_domain)


	def test_d_disable_php_sub_host(self):
		self._disableHost('php', self.php_sub_domain)
		self._checkHostNotFound(self.php_sub_domain)

	def test_d_disable_python_sub_host(self):
		self._disableHost('python', self.python_sub_domain)
		self._checkHostNotFound(self.python_sub_domain)

	def test_d_disable_django_sub_host(self):
		self._disableHost('django', self.django_sub_domain)
		self._checkHostNotFound(self.django_sub_domain)


	def test_e_enable_php_host(self):
		self._enableHost('php', self.php_domain)
		self._checkHostFound(self.php_domain, 'PHP:Hello, World!')

	def test_e_enable_python_host(self):
		self._enableHost('python', self.python_domain)
		self._checkHostFound(self.python_domain, 'Python:Hello, World!')

	def test_e_enable_django_host(self):
		self._enableHost('django', self.django_domain)
		self._checkHostFound(self.django_domain, "It worked!")


	def test_f_enable_php_sub_host(self):
		self._enableHost('php', self.php_sub_domain)
		self._checkHostFound(self.php_sub_domain, 'PHP:Hello, World!')

	def test_f_enable_python_sub_host(self):
		self._enableHost('python', self.python_sub_domain)
		self._checkHostFound(self.python_sub_domain, 'Python:Hello, World!')

	def test_f_enable_django_sub_host(self):
		self._enableHost('django', self.django_sub_domain)
		self._checkHostFound(self.django_sub_domain, "It worked!")


	def test_g_remove_php_sub_domain(self):
		self._delHost('php', self.php_sub_domain)
		self._checkHostNotFound(self.php_sub_domain)

	def test_g_remove_python_sub_domain(self):
		self._delHost('python', self.python_sub_domain)
		self._checkHostNotFound(self.python_sub_domain)

	def test_g_remove_django_sub_domain(self):
		self._delHost('django', self.django_sub_domain)
		self._checkHostNotFound(self.django_sub_domain)


	def test_h_remove_php_host(self):
		self._delHost('php', self.php_domain)
		self._checkHostNotFound(self.php_domain)

	def test_h_remove_python_host(self):
		self._delHost('python', self.python_domain)
		self._checkHostNotFound(self.python_domain)

	def test_h_remove_django_host(self):
		self._delHost('django', self.django_domain)
		self._checkHostNotFound(self.django_domain)
