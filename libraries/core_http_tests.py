__author__ = 'gotlium'


import unittest
from configs import Configs
import grab
from grab.error import GrabNetworkError, GrabConnectionError
import os
from time import sleep


class CoreHttpTestCase(unittest.TestCase, Configs):

	php_domains = (
		'1st-php.dev', 'st-php.dev', 'php.dev',
	)
	php_sub_domains = (
		'sub-1.1st-php.dev', 'sub-a1.php.dev', 'sub.php.dev',
	)

	python_domains = (
		'1st-python.dev', 'st-python.dev', 'python.dev',
	)
	python_sub_domains = (
		'sub-1.1st-python.dev', 'sub-a1.python.dev', 'sub.python.dev',
	)

	django_domains = (
		'1st-django.dev', 'a-django.dev', 'b-django.dev',
		'django.dev', 'st1-django.dev', 'st1-1django.dev',
	)
	django_sub_domains = (
		'sub-1.1st-django.dev', 'sub-a1.django.dev', 'sub.django.dev',
	)

	django_domains_wsgi = (
		'django-wsgi.dev', 'django-1wsgi.dev'
	)

	django_domains_venv = (
		'django-venv.dev', '1a-django-venv.dev'
	)

	django_domains_wsgi_venv = (
		'django-wv.dev', '1a-django-wv.dev'
	)

	python_domains_wsgi = (
		'python-wsgi.dev', '1a-python-wsgi.dev'
	)

	python_domains_venv = (
		'python-venv.dev', '1a-python-venv.dev'
	)

	python_domains_wsgi_venv = (
		'python-wv.dev', 'a-python-wv.dev'
	)

	web_server = 'apache'


	def setUp(self):
		self.loadConfigs()
		sleep(5)

	def __getPage(self, url, hammer_mode=True):
		g = grab.Grab()
		g.setup(connect_timeout=1, timeout=3)
		g.setup(hammer_mode=hammer_mode, hammer_timeouts=(
			(3, 5), (5, 7), (7, 9), (15, 20), (50, 60)
		))
		g.go(url)
		return g.response

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
				search(request.body, content), -1
			)
			self.assertEquals(request.code, 200)

	def _checkHostNotFound(self, host):
		urls = self.__getUrls(host)
		for url in urls:
			with self.assertRaises(GrabNetworkError):
				try:
					self.__getPage(url, hammer_mode=False)
				except GrabConnectionError:
					raise GrabNetworkError('Connection error')

	def _addHost(self, type, host_name, flags='', action='a', cmd_ad_opt=''):
		execution_code = os.system(
			'ahc -m %s -t %s -%s %s %s %s -y 1> /dev/null' % \
				  (self.web_server, type, action, host_name, flags, cmd_ad_opt)
		)
		self.assertEquals(execution_code, 0)

	def _delHost(self, type, host_name, flags='', cmd_ad_opt=''):
		self._addHost(type, host_name, flags, 'd', cmd_ad_opt)

	def _enableHost(self, type, host_name, flags='', cmd_ad_opt=''):
		self._addHost(type, host_name, flags, 'e', cmd_ad_opt)

	def _disableHost(self, type, host_name, flags='', cmd_ad_opt=''):
		self._addHost(type, host_name, flags, 'f', cmd_ad_opt)


	def _add_host_test(self, type, domains, check_line, cmd_ad_opt=""):
		for domain in domains:
			self._addHost(type, domain, cmd_ad_opt)
			self._checkHostFound(domain, check_line)

	def _disable_host_test(self, type, domains, cmd_ad_opt=""):
		for domain in domains:
			self._disableHost(type, domain, cmd_ad_opt)
			self._checkHostNotFound(domain)

	def _enable_host_test(self, type, domains, check_line, cmd_ad_opt=""):
		for domain in domains:
			self._enableHost(type, domain, cmd_ad_opt)
			self._checkHostFound(domain, check_line)

	def _remove_host_test(self, type, domains, cmd_ad_opt=""):
		for domain in domains:
			self._delHost(type, domain, cmd_ad_opt)
			self._checkHostNotFound(domain)


	def test_a_add_php_host(self):
		self._add_host_test(
			'php', self.php_domains, 'PHP:Hello, World!'
		)

	def test_a_add_python_host(self):
		self._add_host_test(
			'python', self.python_domains, 'Python:Hello, World!'
		)

	def test_a_add_django_host(self):
		self._add_host_test(
			'django', self.django_domains, "It worked!"
		)

	def test_b_add_php_sub_domain(self):
		self._add_host_test(
			'php', self.php_sub_domains, 'PHP:Hello, World!'
		)

	def test_b_add_python_sub_domain(self):
		self._add_host_test(
			'python', self.python_sub_domains, 'Python:Hello, World!'
		)

	def test_b_add_django_sub_domain(self):
		self._add_host_test(
			'django', self.django_sub_domains, "It worked!"
		)


	def test_c_disable_php_host(self):
		self._disable_host_test(
			'php', self.php_domains
		)

	def test_c_disable_python_host(self):
		self._disable_host_test(
			'python', self.python_domains
		)

	def test_c_disable_django_host(self):
		self._disable_host_test(
			'django', self.django_domains
		)


	def test_d_disable_php_sub_host(self):
		self._disable_host_test(
			'php', self.php_sub_domains
		)

	def test_d_disable_python_sub_host(self):
		self._disable_host_test(
			'python', self.python_sub_domains
		)

	def test_d_disable_django_sub_host(self):
		self._disable_host_test(
			'django', self.django_sub_domains
		)


	def test_e_enable_php_host(self):
		self._enable_host_test(
			'php', self.php_domains, 'PHP:Hello, World!'
		)

	def test_e_enable_python_host(self):
		self._enable_host_test(
			'python', self.python_domains, 'Python:Hello, World!'
		)

	def test_e_enable_django_host(self):
		self._enable_host_test(
			'django', self.django_domains, "It worked!"
		)


	def test_f_enable_php_sub_host(self):
		self._enable_host_test(
			'php', self.php_sub_domains, 'PHP:Hello, World!'
		)

	def test_f_enable_python_sub_host(self):
		self._enable_host_test(
			'python', self.python_sub_domains, 'Python:Hello, World!'
		)

	def test_f_enable_django_sub_host(self):
		self._enable_host_test(
			'django', self.django_sub_domains, "It worked!"
		)


	def test_g_remove_php_sub_domain(self):
		self._remove_host_test(
			'php', self.php_sub_domains
		)

	def test_g_remove_python_sub_domain(self):
		self._remove_host_test(
			'python', self.python_sub_domains
		)

	def test_g_remove_django_sub_domain(self):
		self._remove_host_test(
			'django', self.django_sub_domains
		)


	def test_h_remove_php_host(self):
		self._remove_host_test(
			'php', self.php_domains
		)

	def test_h_remove_python_host(self):
		self._remove_host_test(
			'python', self.python_domains
		)

	def test_h_remove_django_host(self):
		self._remove_host_test(
			'django', self.django_domains
		)


	# WSGI
	def test_a_add_django_host_wsgi(self):
		self._add_host_test(
			'django', self.django_domains_wsgi, "It worked!", '-w'
		)

	def test_c_disable_django_host_wsgi(self):
		self._disable_host_test(
			'django', self.django_domains_wsgi, '-w'
		)

	def test_e_enable_django_host_wsgi(self):
		self._enable_host_test(
			'django', self.django_domains_wsgi, "It worked!", '-w'
		)

	def test_h_remove_django_host_wsgi(self):
		self._remove_host_test(
			'django', self.django_domains_wsgi, '-w'
		)


	# Virtual env
	def test_a_add_django_host_venv(self):
		self._add_host_test(
			'django', self.django_domains_venv, "It worked!", '-v'
		)

	def test_c_disable_django_host_venv(self):
		self._disable_host_test(
			'django', self.django_domains_venv, '-v'
		)

	def test_e_enable_django_host_venv(self):
		self._enable_host_test(
			'django', self.django_domains_venv, "It worked!", '-v'
		)

	def test_h_remove_django_host_venv(self):
		self._remove_host_test(
			'django', self.django_domains_venv, '-v'
		)


	# Virtual env + WSGI
	def test_a_add_django_host_wsgi_venv(self):
		self._add_host_test(
			'django', self.django_domains_wsgi_venv, "It worked!", '-v -w'
		)

	def test_c_disable_django_host_wsgi_venv(self):
		self._disable_host_test(
			'django', self.django_domains_wsgi_venv, '-v -w'
		)

	def test_e_enable_django_host_wsgi_venv(self):
		self._enable_host_test(
			'django', self.django_domains_wsgi_venv, "It worked!", '-v -w'
		)

	def test_h_remove_django_host_wsgi_venv(self):
		self._remove_host_test(
			'django', self.django_domains_wsgi_venv, '-v -w'
		)



	# WSGI
	def test_a_add_python_host_wsgi(self):
		self._add_host_test(
			'python', self.python_domains_wsgi, 'PythonWSGI:Hello, World!', '-w'
		)

	def test_c_disable_python_host_wsgi(self):
		self._disable_host_test(
			'python', self.python_domains_wsgi, '-w'
		)

	def test_e_enable_python_host_wsgi(self):
		self._enable_host_test(
			'python', self.python_domains_wsgi,
			'PythonWSGI:Hello, World!', '-w'
		)

	def test_h_remove_python_host_wsgi(self):
		self._remove_host_test(
			'python', self.python_domains_wsgi, '-w'
		)


	# Virtual env
	def test_a_add_python_host_venv(self):
		self._add_host_test(
			'python', self.python_domains_venv,
			'Python:Hello, World!', '-v'
		)

	def test_c_disable_python_host_venv(self):
		self._disable_host_test(
			'python', self.python_domains_venv, '-v'
		)

	def test_e_enable_python_host_venv(self):
		self._enable_host_test(
			'python', self.python_domains_venv,
			'Python:Hello, World!', '-v'
		)

	def test_h_remove_python_host_venv(self):
		self._remove_host_test(
			'python', self.python_domains_venv, '-v'
		)


	# Virtual env + WSGI
	def test_a_add_python_host_wsgi_venv(self):
		self._add_host_test(
			'python', self.python_domains_wsgi_venv,
			'PythonWSGI:Hello, World!', '-v -w'
		)

	def test_c_disable_python_host_wsgi_venv(self):
		self._disable_host_test(
			'python', self.python_domains_wsgi_venv, '-v -w'
		)

	def test_e_enable_python_host_wsgi_venv(self):
		self._enable_host_test(
			'python', self.python_domains_wsgi_venv,
			'PythonWSGI:Hello, World!', '-v -w'
		)

	def test_h_remove_python_host_wsgi_venv(self):
		self._remove_host_test(
			'python', self.python_domains_wsgi_venv, '-v -w'
		)
