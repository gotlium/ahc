# -*- coding: utf-8 -*-

__author__ = 'GoTLiuM InSPiRiT <gotlium@gmail.com>'
__copyright__ = 'Copyright 2012, GoTLiuM InSPiRiT <gotlium@gmail.com>'

from smtplib import SMTP
import shutil
import os

from libraries.path import HostPath
from libraries.helpers import *


MAIL_FROM = 'ruslan@askarov.org'
MAIL_TO = ['gotlium@gmail.com']
MAIL_SUBJECT = 'New project information'

SERVER_IP = '109.236.82.142'
DB_DATA = ('root', 'metallica')
APACHE_AUTH = ('admin', 'admin')
messages = []


class Installator(HostPath):
    def __init__(self, base):
        self.base = base
        self.messages = []


    def __ahc(self, module, action, host_name, cmd=""):
        format = '/usr/bin/ahc -m %s -%s %s %s'
        args = (module, action, host_name, cmd)
        result = system(format % args, True)
        self.messages.append(result)
        print result
        return result

    def __clear_hostname(self, hostname):
        project = hostname.replace('.', '_').replace('-', '_')
        return re.sub('([^a-z])+', '', project)


    def _uninstall_bind(self):
        self.__ahc('bind', 'd', self.sandbox, '-i %s' % SERVER_IP)

    def _uninstall_apache(self):
        self.__ahc('apache', 'd', self.hostname, '-t django -y')

    def _uninstall_mysql(self):
        self.__ahc('mysql', 'd', self.hostname_cleared,
                   '-u %s -p %s -y' % DB_DATA)

    def _uninstall_git(self):
        self.__ahc('git', 'd', self.hostname)

    def _uninstall_ftp(self):
        self.__ahc(
            'ftp', 'd', self.hostname, '-u %s -p random' % \
                                       self.project_cleared
        )

    def _uninstall_nginx(self):
        sites_available = '%s/%s' % (
            self.base.nginx['sites_available'], self.hostname
        )
        sites_enabled = '%s/%s' % (
            self.base.nginx['sites_enabled'], self.hostname
        )
        delFile(sites_available)
        delFile(sites_enabled)


    def _install_bind(self):
        self.__ahc('bind', 'a', self.sandbox, '-i %s' % SERVER_IP)

    def _install_apache(self):
        self.__ahc('apache', 'a', self.hostname, '-t django -b %s:%s' \
                                                 % APACHE_AUTH)

    def _install_mysql(self):
        self.__ahc('mysql', 'a', self.hostname_cleared,
                   '-u %s -p %s' % DB_DATA)

    def _install_git(self):
        self.__ahc('git', 'a', self.hostname)
        os.system('git add .')
        os.system('git commit -am "Initial commit"')
        os.system('git push origin master')

    def _install_ftp(self):
        self.__ahc(
            'ftp', 'a', self.hostname, '-u %s -p random' % \
                                       self.project_cleared
        )

    def _install_nginx(self):
        config = """
server {
	listen   80;
        server_name %(server_name)s;

    location / {
    	proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    	#proxy_cookie_domain %(server_name)s %(real_name)s;
        #proxy_redirect http://%(server_name)s http://%(real_name)s;
    }
}
		""" % {
            'server_name': self.sandbox,
            'real_name': self.hostname
        }
        sites_available = '%s/%s' % (
            self.base.nginx['sites_available'], self.hostname
        )
        sites_enabled = '%s/%s' % (
            self.base.nginx['sites_enabled'], self.hostname
        )
        putFile(sites_available, config)
        system('ln -s %s %s' % (sites_available, sites_enabled))

    def _install_engine(self):
        data = self.getHostData(self.hostname)
        website_dir = data['website_dir']
        os.chdir(website_dir)
        for f in os.listdir(website_dir):
            if f == '.htpasswd' or f == 'www':
                continue
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.unlink(f)
        os.system('rm -rf .git')
        os.system('git init')
        os.system('git remote add origin %s/shop.git' % self.base.git[
            'repositories'])
        os.system('git pull origin master')
        os.system('rm -rf .git')
        os.system('mkdir -p assets/media/images/')
        os.system('chown www-data:www-data -R assets/')
        os.system('mkdir -p static/{images,scripts,style}')
        os.chdir('static')
        os.system(
            'ln -s /usr/local/lib/python2.7/dist-packages/grappelli/static/admin ./')
        os.system(
            'ln -s /usr/local/lib/python2.7/dist-packages/grappelli/static/grappelli ./')
        if os.path.exists(
                '/usr/local/lib/python2.7/dist-packages/oscar/static/oscar'):
            os.system(
                'ln -s /usr/local/lib/python2.7/dist-packages/oscar/static/oscar ./')
        else:
            os.system(
                'ln -s /usr/local/lib/python2.7/dist-packages/django_oscar-0.5_pre_alpha-py2.7.egg/oscar/static/oscar ./')
        os.system(
            'ln -s /usr/local/lib/python2.7/dist-packages/tinymce/static/tiny_mce ./')

        os.system('chown www-data:www-data -R ../static/')

        os.chdir(website_dir)
        settings = getFile('settings.py')
        db_settings = """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '%(name)s',
        'USER': '%(user)s',
        'PASSWORD': '%(password)s',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
		""" % {
            'name': self.hostname_cleared,
            'user': DB_DATA[0],
            'password': DB_DATA[1]
        }
        new_settings = re.sub('DATABASES = {(.*?)}', db_settings, settings,
                              flags=re.DOTALL | re.MULTILINE)
        putFile('settings.py', new_settings)

        os.system('rm -rf .git')

        os.system(
            'mysql -p%s %s < db.sql' % (DB_DATA[1], self.hostname_cleared))
        #os.system('rm db.sql')
        os.system('python manage.py syncdb')
        os.system('mkdir whoosh_index/')
        os.system('python manage.py rebuild_index')

        os.system('chown www-data:www-data whoosh_index/')

        # templates update
        os.system('mv templates/ current_templates/')
        os.system(
            'cp -R /usr/local/lib/python2.7/dist-packages/django_oscar*.egg/oscar/templates/oscar/ templates/')
        os.system('cp -R current_templates/* templates/')
        os.system('rm -rf current_templates')

        service_restart(self.base.apache2['init'], 'reload')
        service_restart(self.base.nginx['init'])

    def _send_credentials(self):
        try:
            message = "From: %s\r\n" % MAIL_FROM \
                      + "To: %s\r\n" % MAIL_TO[0] \
                      + "Subject: %s\r\n" % MAIL_SUBJECT \
                      + "\r\n" \
                      + '\n--------\n'.join(self.messages)
            mail = SMTP('localhost')
            mail.sendmail(MAIL_FROM, MAIL_TO, message)
            mail.quit()
        except:
            error_message("Error: unable to send email")

    def _init_vars(self, hostname):
        self.hostname = hostname
        self.hostname_cleared = self.__clear_hostname(hostname)[0:16]
        self.project = self.hostname.split('.')[0]
        self.project_cleared = self.__clear_hostname(self.project)
        self.sandbox = '%s.askarov.org' % self.project_cleared

    def add(self, hostname):
        self._init_vars(hostname)
        self._install_apache()
        self._install_nginx()
        self._install_mysql()
        self._install_bind()
        self._install_engine()
        self._install_git()
        self._install_ftp()
        self._send_credentials()

    def remove(self, hostname):
        self._init_vars(hostname)
        self._uninstall_mysql()
        self._uninstall_bind()
        self._uninstall_git()
        self._uninstall_ftp()
        self._uninstall_apache()
        self._uninstall_nginx()

    def move(self, hostname):
        pass


class Shop(HostPath):
    methods = ('add', 'delete', 'move')
    base = None

    def __init__(self, base):
        self.base = base
        self.installator = Installator(base)

    def add(self, host_name):
        self.installator.add(host_name)

    def delete(self, host_name):
        self.installator.remove(host_name)

    def move(self, host_name):
        self.installator.move(host_name)
