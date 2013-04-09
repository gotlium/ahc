__author__ = 'gotlium'

from unittest import TestCase
from ftplib import FTP
import os


class FtpTestCase(TestCase):
    datas = {
        0: {
            'host': 'ftp.dev', 'user': 'ftp_user1',
            'password': 'ftp_password1', 'type': 'php'
        },
        1: {
            'host': 'sub.ftp.dev', 'user': 'ftp_user2',
            'password': 'ftp_password2', 'type': 'php'
        },
        2: {
            'host': 'djftp.dev', 'user': 'ftp_user3',
            'password': 'ftp_password3', 'type': 'django'
        },
        3: {
            'host': 'sub.djftp.dev', 'user': 'ftp_user4',
            'password': 'ftp_password4', 'type': 'django'
        }
    }

    def __makeConnection(self, user, password):
        ftp = FTP('localhost', user, password, timeout=1)
        self.assertTrue('www' in ftp.nlst())
        ftp.quit()

    def __addUser(self, host_name, user, password, action='a'):
        execution_code = os.system(
            'ahc -m ftp -%s %s -u %s -p %s -y 1> /dev/null' % (
                action, host_name, user, password))
        self.assertEquals(execution_code, 0)

    def __delUser(self, host_name, user, password):
        self.__addUser(host_name, user, password, 'd')

    def __addHost(self, host_name, type='php', action='a'):
        execution_code = os.system(
            'ahc -m apache -t %s -%s %s -y 1> /dev/null' % (
                type, action, host_name))
        self.assertEquals(execution_code, 0)

    def __delHost(self, host_name, type):
        self.__addHost(host_name, type, 'd')

    def __add(self, key):
        data = self.datas[key]
        self.__addHost(data['host'], data['type'])
        self.__addUser(data['host'], data['user'], data['password'])
        self.__makeConnection(data['user'], data['password'])

    def __del(self, key):
        data = self.datas[key]
        self.__delHost(data['host'], data['type'])
        self.__delUser(
            data['host'], data['user'], data['password']
        )

    def test_a_add_ftp_db_domain(self):
        self.__add(0)

    def test_b_add_ftp_db_sub_domain(self):
        self.__add(1)

    def test_c_add_ftp_db_domain(self):
        self.__add(2)

    def test_d_add_ftp_db_sub_domain(self):
        self.__add(3)

    def test_e_del_ftp_db_sub_domain(self):
        self.__del(1)

    def test_f_del_ftp_db_domain(self):
        self.__del(0)

    def test_g_del_ftp_db_sub_domain(self):
        self.__del(3)

    def test_h_del_ftp_db_domain(self):
        self.__del(2)
