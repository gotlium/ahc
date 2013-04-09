__author__ = 'gotlium'

from libraries.core_http import CoreHttp
from libraries.helpers import getTemplate
from libraries.apache import CertificateGenerator


class Apache(CoreHttp):
    def __init__(self, base, web_server='apache2'):
        CoreHttp.__init__(self, base, web_server)
        self.__setSslTemplate()

    def __setSslTemplate(self):
        if self.base.options.protection:
            self.base.options.ip = self.base.options.add
            generator = CertificateGenerator(self.base)

            config = {}
            config.update(self.base.apache2)
            config.update(self.base.main)
            config.update(generator.config.apache_cert)

            self.ssl_template = getTemplate('apache2-ssl-cert') % config
        else:
            self.ssl_template = "SSLEngine On\n\tSSLCertificateFile %s" % \
                                self.config['ssl_file']
