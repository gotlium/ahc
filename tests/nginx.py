__author__ = 'gotlium'

from libraries.core_http_tests import CoreHttpTestCase

class NginxTestCase(CoreHttpTestCase):
	web_server = 'nginx'

