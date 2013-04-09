__author__ = 'gotlium'

import os
from unittest import TestCase

from libraries.helpers import system


class BindTestCase(TestCase):
    def __addHost(self, sub_domain=False, ip_address='127.0.0.1', action='a'):
        host_name = 'bind.dev'
        if sub_domain:
            host_name = 'sub.bind.dev'
        execution_code = os.system(
            'ahc -m bind -%s %s -i %s -y 1> /dev/null' % (
                action, host_name, ip_address))
        self.assertEquals(execution_code, 0)

    def __delHost(self, sub_domain=False):
        self.__addHost(sub_domain=sub_domain, action='d')

    def __checkFound(self, sub_domain=False):
        host_name = 'bind.dev'
        if sub_domain:
            host_name = 'sub.bind.dev'
        arr = system('nslookup %s 127.0.0.1' % host_name)
        self.assertTrue(len(arr) > 0)

    def test_a_add_bind_host(self):
        self.__addHost()
        self.__checkFound()

    def test_b_add_bind_sub_domain(self):
        self.__addHost(sub_domain=True)
        self.__checkFound(sub_domain=True)

    def test_c_del_bind_sub_domain(self):
        self.__delHost(sub_domain=True)

    def test_d_del_bind_host(self):
        self.__delHost()
