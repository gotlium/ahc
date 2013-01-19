__author__ = 'gotlium'


from libraries.core_http_tests import CoreHttpTestCase


class ApacheTestCase(CoreHttpTestCase):
	web_server = 'apache'

	ruby_domains = (
		'1st-ruby.dev', '1st_ruby.dev', 'st-ruby.dev', 'st_ruby.dev', 'ruby.dev',
	)
	ruby_sub_domains = (
		'sub-1.1st-ruby.dev', 'sub1.1st_ruby.dev', 'sub_1a.st-ruby.dev',
		'sub-1.st_ruby.dev', 'sub-a1.ruby.dev', 'sub.ruby.dev',
	)

	ror_domains = (
		'1st-ror.dev', '2st_ror.dev', 'a-ror.dev', 'b-ror.dev',
		'ror.dev', 'st1-ror.dev', 'st1-1ror.dev',
	)
	ror_sub_domains = (
		'sub-1.1st-ror.dev', 'sub1.1st_ror.dev', 'sub_1a.st-ror.dev',
		'sub-1.st_ror.dev', 'sub-a1.ror.dev', 'sub.ror.dev',
	)

	'''

	def test_a_add_ruby_host(self):
		self._add_host_test(
			'ruby', self.ruby_domains, 'Ruby:Hello'
		)

	def test_a_add_ror_host(self):
		self._add_host_test(
			'ror', self.ror_domains, "Ruby on Rails"
		)

	def test_b_add_ruby_sub_domains(self):
		self._add_host_test(
			'ruby', self.ruby_sub_domains, 'Ruby:Hello'
		)

	def test_b_add_ror_sub_domains(self):
		self._add_host_test(
			'ror', self.ror_sub_domains, "Ruby on Rails"
		)


	def test_c_disable_ruby_host(self):
		self._disable_host_test(
			'ruby', self.ruby_domains
		)

	def test_c_disable_ror_host(self):
		self._disable_host_test(
			'ror', self.ror_domains
		)

	def test_d_disable_ruby_sub_host(self):
		self._disable_host_test(
			'ruby', self.ruby_sub_domains
		)

	def test_d_disable_ror_sub_host(self):
		self._disable_host_test(
			'ror', self.ror_sub_domains
		)


	def test_e_enable_ruby_host(self):
		self._enable_host_test(
			'ruby', self.ruby_domains, 'Ruby:Hello'
		)

	def test_e_enable_ror_host(self):
		self._enable_host_test(
			'ror', self.ror_domains, "Ruby on Rails"
		)


	def test_f_enable_ruby_sub_host(self):
		self._enable_host_test(
			'ruby', self.ruby_sub_domains, 'Ruby:Hello'
		)

	def test_f_enable_ror_sub_host(self):
		self._enable_host_test(
			'ror', self.ror_sub_domains, "Ruby on Rails"
		)


	def test_g_remove_ruby_sub_domains(self):
		self._remove_host_test(
			'ruby', self.ruby_sub_domains
		)

	def test_g_remove_ror_sub_domains(self):
		self._remove_host_test(
			'ror', self.ror_sub_domains
		)

	def test_h_remove_ruby_host(self):
		self._remove_host_test(
			'ruby', self.ruby_domains
		)

	def test_h_remove_ror_host(self):
		self._remove_host_test(
			'ror', self.ror_domains
		)
	'''


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
