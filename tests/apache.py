__author__ = 'gotlium'

from libraries.core_http_tests import CoreHttpTestCase

class ApacheTestCase(CoreHttpTestCase):
	web_server = 'apache'

	ruby_domain = 'ruby.dev'
	ruby_sub_domain = 'sub.ruby.dev'

	ror_domain = 'ror.dev'
	ror_sub_domain = 'sub.ror.dev'

	def test_a_add_ruby_host(self):
		self._addHost('ruby', self.ruby_domain)
		self._checkHostFound(self.ruby_domain, 'Ruby:Hello')

	def test_a_add_ror_host(self):
		self._addHost('ror', self.ror_domain)
		self._checkHostFound(self.ror_domain, "Ruby on Rails")


	def test_b_add_ruby_sub_domain(self):
		self._addHost('ruby', self.ruby_sub_domain)
		self._checkHostFound(self.ruby_sub_domain, 'Ruby:Hello')

	def test_b_add_ror_sub_domain(self):
		self._addHost('ror', self.ror_sub_domain)
		self._checkHostFound(self.ror_sub_domain, "Ruby on Rails")


	def test_c_disable_ruby_host(self):
		self._disableHost('ruby', self.ruby_domain)
		self._checkHostNotFound(self.ruby_domain)

	def test_c_disable_ror_host(self):
		self._disableHost('ror', self.ror_domain)
		self._checkHostNotFound(self.ror_domain)


	def test_d_disable_ruby_sub_host(self):
		self._disableHost('ruby', self.ruby_sub_domain)
		self._checkHostNotFound(self.ruby_sub_domain)

	def test_d_disable_ror_sub_host(self):
		self._disableHost('ror', self.ror_sub_domain)
		self._checkHostNotFound(self.ror_sub_domain)


	def test_e_enable_ruby_host(self):
		self._enableHost('ruby', self.ruby_domain)
		self._checkHostFound(self.ruby_domain, 'Ruby:Hello')

	def test_e_enable_ror_host(self):
		self._enableHost('ror', self.ror_domain)
		self._checkHostFound(self.ror_domain, "Ruby on Rails")


	def test_f_enable_ruby_sub_host(self):
		self._enableHost('ruby', self.ruby_sub_domain)
		self._checkHostFound(self.ruby_sub_domain, 'Ruby:Hello')

	def test_f_enable_ror_sub_host(self):
		self._enableHost('ror', self.ror_sub_domain)
		self._checkHostFound(self.ror_sub_domain, "Ruby on Rails")


	def test_g_remove_ruby_sub_domain(self):
		self._delHost('ruby', self.ruby_sub_domain)
		self._checkHostNotFound(self.ruby_sub_domain)

	def test_g_remove_ror_sub_domain(self):
		self._delHost('ror', self.ror_sub_domain)
		self._checkHostNotFound(self.ror_sub_domain)


	def test_h_remove_ruby_host(self):
		self._delHost('ruby', self.ruby_domain)
		self._checkHostNotFound(self.ruby_domain)

	def test_h_remove_ror_host(self):
		self._delHost('ror', self.ror_domain)
		self._checkHostNotFound(self.ror_domain)

	'''
	def test_f_add_php_host_with_protection(self):
		pass

	def test_f_add_ruby_host_with_protection(self):
		pass

	def test_f_add_ror_host_with_protection(self):
		pass


	def test_d_add_php_host_with_optimization(self):
		pass

	def test_e_add_ruby_host_with_optimization(self):
		pass

	def test_f_add_ror_host_with_optimization(self):
		pass


	def test_f_add_php_host_with_optimization_and_protection(self):
		pass

	def test_f_add_ruby_host_with_optimization_and_protection(self):
		pass

	def test_f_add_ror_host_with_optimization_and_protection(self):
		pass
	'''
