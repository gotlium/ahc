__author__ = 'gotlium'

from unittest import TestLoader, TextTestRunner
import os
import re

from libraries.helpers import *


class Test(object):
    def __init__(self, base):
        self.methods = ('service',)
        self.ucfirst = lambda s: s[0].upper() + s[1:]

    def __loadTest(self, service):
        try:
            importedModule = __import__(
                'tests.%s' % service.lower(), fromlist="tests"
            )
            module_class = getattr(
                importedModule, self.ucfirst(service) + 'TestCase'
            )
        except:
            error_message('Test not found!')
        suite = TestLoader().loadTestsFromTestCase(module_class)
        TextTestRunner(verbosity=2).run(suite)

    def __loadAllTests(self):
        for file in os.listdir('tests/'):
            if re.match('^.*?\.py$', file):
                if file != '__init__.py':
                    module, ext = file.split('.')
                    info_message("*" * 80, 'blue')
                    info_message("> %s" % self.ucfirst(module), 'green')
                    info_message("*" * 80, 'blue')
                    self.__loadTest(module)
                    info_message("")

    def service(self, service):
        if service == 'all':
            self.__loadAllTests()
        else:
            self.__loadTest(service)
