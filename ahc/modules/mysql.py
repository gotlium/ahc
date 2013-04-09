__author__ = 'gotlium'

import getpass

import MySQLdb

from libraries.password import random_password
from libraries.helpers import *


class Mysql(object):
    methods = ('add', 'delete',)
    base = None

    def __init__(self, base):
        self.base = base
        self.config = self.base.mysql
        if not self.config['password']:
            password = getpass.getpass("Root password: ")
        else:
            password = self.config['password']
        self.db = MySQLdb.connect(
            self.config['host'], self.config['user'], password
        )
        self.cursor = self.db.cursor()
        checkInstall(self.config)

    def __getDbName(self, host_name):
        host_name = host_name.split('.')
        return '_'.join(host_name)

    def __getLogin(self, host_name):
        login = host_name
        if self.base.options.user:
            login = self.base.options.user
        if len(login) > 16:
            info_message('Username truncated to 16 characters.', 'lightgreen')
            return login[:16]
        return login

    def add(self, host_name):
        isHost(host_name)
        login = self.__getLogin(host_name)
        password = host_name
        if self.base.options.password:
            password = self.base.options.password
            if password == 'random':
                password = random_password()
        database = self.__getDbName(host_name)
        try:
            self.cursor.execute(
                "CREATE DATABASE `%s` CHARACTER SET utf8 "
                "COLLATE utf8_general_ci;" % database)
            self.cursor.execute(
                "GRANT ALL ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s';" % (
                    database, login, password)
            )
            self.cursor.execute(
                "GRANT ALL ON %s.* TO '%s'@'127.0.0.1' IDENTIFIED BY '%s';" % (
                    database, login, password)
            )
            self.cursor.execute(
                "GRANT ALL ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s';" % (
                    database, login, password)
            )
            self.cursor.execute('FLUSH PRIVILEGES;')
        except Exception, msg:
            error_message(msg)
        info_message('Database successfully created.')
        info_message('Database: %s' % database, 'white')
        info_message('Login: %s' % login, 'white')
        info_message('Password: %s' % password, 'white')

    def delete(self, host_name):
        isHost(host_name)
        database = self.__getDbName(host_name)
        login = self.__getLogin(host_name)

        try:
            self.cursor.execute(
                "REVOKE ALL ON %s.* FROM '%s'@'%%';" % (database, login)
            )
            self.cursor.execute(
                "REVOKE ALL ON %s.* FROM '%s'@'127.0.0.1';" % (database, login)
            )
            self.cursor.execute(
                "REVOKE ALL ON %s.* FROM '%s'@'localhost';" % (database, login)
            )
            self.cursor.execute('FLUSH PRIVILEGES;')

            self.cursor.execute("SHOW GRANTS FOR '%s'@'%%';" % login)
            rows = self.cursor.fetchall()
            if len(rows) < 2:
                self.cursor.execute("DROP USER '%s'@'%%';" % login)
                self.cursor.execute("DROP USER '%s'@'127.0.0.1';" % login)
                self.cursor.execute("DROP USER '%s'@'localhost';" % login)
                self.cursor.execute('FLUSH PRIVILEGES;')
        except Exception, msg:
            print msg
            error_message("User not found!")

        if self.base.options.yes:
            msg = 'y'
        else:
            msg = raw_input("Remove database '%s'?!(Yes/No) " % database)
        if str(msg).lower() in ('y', 'yes'):
            self.cursor.execute('DROP DATABASE IF EXISTS `%s`;' % database)
        info_message('Database successfully removed.')

    def __del__(self):
        if self.db:
            self.db.commit()
            self.db.close()
