__author__ = 'gotlium'

import MySQLdb
import getpass, pwd

from libraries.helpers import *
from libraries.apache import CertificateGenerator

class Install(object):

	def __init__(self, base):
		self.base = base
		self.methods = ('service',)

	def certs(self):
		cert = CertificateGenerator(self.base)
		if cert.createDatabase():
			info_message('"Apache SSL Certs Protection" was successfully installed.')

	def bashrc(self):
		configuration = getTemplate('bashrc')
		backFile('/root/.bashrc')
		putFile('/root/.bashrc', configuration)

	def mysql(self):
		mysql_config = self.base.mysql['config']
		if not fileExists(mysql_config):
			error_message('MySQL config not found!')
		elif not fileExists(self.base.mysql['bin']):
			error_message('MySQL not installed!')
		backFile(mysql_config)
		system_by_code('cp -f templates/mysql.conf %s' % mysql_config)
		service_restart(self.base.mysql['init'])
		info_message('MySQL config was installed.')
		info_message('Server successfully restarted.')

	def nginx_proxy(self):
		if not fileExists(self.base.nginx['config']):
			error_message('Nginx config not found!')
		elif not fileExists(self.base.nginx['bin']):
			error_message('Nginx not installed!')
		def_srv_conf = '%s/default' % self.base.nginx['sites_available']
		nginx_config = self.base.nginx['config']
		backFile(self.base.nginx['config'])
		if fileExists(def_srv_conf):
			backFile(def_srv_conf)

		if not putFile(nginx_config, getTemplate('nginx-proxy')):
			error_message("Can't overwrite nginx configuration file!")
		if not putFile(def_srv_conf, getTemplate('nginx-proxy-host')):
			error_message("Can't overwrite nginx website configuration!")

		info_message('Now "nginx" installed as proxy for "apache2".')
		info_message('Please, change "apache2" ports to "8080".')
		info_message('After switch "apache2" port in ahc config.')
		info_message('Restart your "apache2" and "nginx" webservers.')

	def lighttpd(self):
		config = {
			'projects_directory': self.base.main['projects_directory'],
			'website_folder': self.base.main['website_folder'],
		}
		backFile(self.base.lighttpd['config'])
		if not putFile(self.base.lighttpd['simple_vhost'], getTemplate('lighttpd-vhost') % config):
			error_message("Can't save lighttpd vhost configuration!")
		if not putFile(self.base.lighttpd['config'], getTemplate('lighttpd')):
			error_message("Can't overwrite lighttpd configuration!")
		info_message('Lighttpd config was installed.')

	def apache2_ssl(self):
		ssl_dir = self.base.apache2['ssl_dir']
		bin_make_ssl = self.base.main['bin_make_ssl']
		ssl_file = self.base.apache2['ssl_file']
		ssleay_config = self.base.main['ssleay_config']
		if not fileExists(ssl_dir):
			system_by_code('mkdir -p %s' % ssl_dir)
		if fileExists(bin_make_ssl):
			if fileExists(ssl_file):
				error_message('SSL certificate already installed!')
			system_by_code("%s %s %s" % (bin_make_ssl, ssleay_config, ssl_file))
			if not fileExists(ssl_file):
				error_message('Certificate is not installed!')
			service_restart(self.base.apache2['init'])
			info_message('SSL certificate successfully installed.')
		else:
			error_message('Command "%s" not found!' % bin_make_ssl)

	def nginx_ssl(self):
		ssl_dir = self.base.nginx['ssl_dir']
		ssl_file_pem = self.base.nginx['ssl_file_pem']
		ssl_file_key = self.base.nginx['ssl_file_key']
		if not fileExists(ssl_dir):
			system_by_code('mkdir -p %s' % ssl_dir)
		if fileExists(ssl_file_pem) or fileExists(ssl_file_key):
			error_message('SSL certificate already installed!')
		ssl_conf = self.base.nginx['ssl_conf']
		system_by_code('cd %s && %s req -new -x509 -days 9999 -nodes -subj \
/C=RU/O=Localhosy/CN=localhost/emailAddress=root@localhost -out %s -keyout %s' % \
			(ssl_dir, self.base.main['bin_openssl'], ssl_file_pem, ssl_file_key)
		)
		config = {
			'ssl_file_pem':	ssl_file_pem,
			'ssl_file_key':	ssl_file_key,
		}
		template = getTemplate('nginx-ssl') % config
		if not putFile(ssl_conf, template):
			error_message('Certificate is not installed!')
		info_message('SSL certificate successfully installed.')

	def ftp(self):
		if not fileExists(self.base.vsftpd['bin']):
			error_message('Vsftpd not installed!')

		if not self.base.mysql['password']:
			password = getpass.getpass("Root password: ")
		else:
			password = self.base.mysql['password']

		try:
			db = MySQLdb.connection(self.base.mysql['host'], self.base.mysql['user'], password)
		except Exception, msg:
			error_message(msg)

		db_user = self.base.vsftpd['db_user']
		db_password = self.base.vsftpd['db_password']
		db_name = self.base.vsftpd['db_name']
		config = self.base.vsftpd['config']
		pam_config = self.base.vsftpd['pam_config']

		db.query('CREATE DATABASE %s;' % db_name)
		db.query(
			"GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP ON \
					%s.* TO '%s'@'localhost' IDENTIFIED BY '%s';" %\
			(db_name, db_user, db_password)
		)
		db.query(
			"GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP ON \
					%s.* TO '%s'@'127.0.0.1' IDENTIFIED BY '%s';" %\
			(db_name, db_user, db_password)
		)
		db.query('FLUSH PRIVILEGES;')
		db.query('USE %s;' % db_name)
		db.query("""
			  CREATE TABLE `accounts` (
				`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,
				`username` VARCHAR( 30 ) NOT NULL ,
				`pass` VARCHAR( 50 ) NOT NULL ,
				UNIQUE (`username`)
			  ) ENGINE = MYISAM ;
		""")
		db.close()

		if fileExists(config):
			backFile(config)
		if fileExists(pam_config):
			backFile(pam_config)

		template_config = {
			'uid': str(pwd.getpwuid(int(self.base.main['useruid']))[0]),
			'projects_directory': self.base.main['projects_directory'],
			'user_config_dir': self.base.vsftpd['user_config_dir'],
		}
		configuration = getTemplate('vsftpd') % template_config
		putFile(config, configuration)

		putFile(pam_config, "\
auth required pam_mysql.so user=%(db_user)s passwd=%(db_password)s host=127.0.0.1 db=%(db_name)s \
table=accounts usercolumn=username passwdcolumn=pass crypt=2\n\
account required pam_mysql.so user=%(db_user)s passwd=%(db_password)s host=127.0.0.1 db=%(db_name)s \
table=accounts usercolumn=username passwdcolumn=pass crypt=2\
		" % {'db_user': db_user, 'db_password': db_password, 'db_name': db_name})

		user_config_dir = self.base.vsftpd['user_config_dir']
		if not fileExists(user_config_dir):
			system_by_code('mkdir -p %s' % user_config_dir)

		service_restart(self.base.vsftpd['init'])
		info_message('FTP config was installed.')
		info_message('Server successfully restarted.')

	def bind(self):
		zones_file = self.base.bind9['zones']
		config_file = self.base.bind9['config']
		if not fileExists(self.base.bind9['bin']):
			error_message('Bind not installed!')
		elif not fileExists(zones_file):
			if not putFile(zones_file,''):
				error_message("Can't touch zones file!")
		zones_template = '\ninclude "%s";\n' % self.base.bind9['zones']
		if not re.findall(zones_file, getFile(config_file)):
			backFile(config_file)
			if not putFile(config_file, zones_template, 'a'):
				error_message("Can't add zones file template to bind configuration!")
		else:
			error_message("Bind config already installed!")
		service_restart(self.base.bind9['init'])
		service_restart(self.base.bind9['bin_rndc'], 'reload')
		info_message("Bind default config was successfully installed.")

	def firewall(self):
		firewall_bin = self.base.firewall['bin']
		if fileExists(firewall_bin):
			error_message('Firewall already installed!')
		system_by_code('cp templates/fw.conf %s' % firewall_bin)
		system_by_code('chmod +x %s' % firewall_bin)
		system_by_code('%s rc.fw defaults 1> /dev/null' % self.base.main['bin_update_rc_d'])
		service_restart(firewall_bin)
		info_message('Firewall was successfully installed.')

	def sendmail(self):
		sendmail_bin = self.base.sendmail['bin']
		if fileExists(sendmail_bin):
			error_message('Sendmail already installed!')
		template_config = {
			'new_mail_path': self.base.sendmail['new_mail_path'],
			'mail_path': self.base.sendmail['mail_path'],
		}
		configuration = getTemplate('sendmail') % template_config
		putFile(sendmail_bin, configuration)
		system_by_code('mkdir -p %s' % self.base.sendmail['new_mail_path'])
		system_by_code('chmod 0777 -R %s' % self.base.sendmail['mail_path'])
		system_by_code('chmod +x %s' % sendmail_bin)
		info_message('Sendmail was successfully installed.')

	def all(self):
		not_callable = ('service', 'all', 'base', 'methods')
		methods = [x for x in dir(self) if not x.startswith('__') and x not in not_callable]
		for method in methods:
			info_message('[%s]' % method, 'white')
			getattr(self, method)()
			info_message('')

	def lamp(self):
		system_by_code('/bin/bash "./templates/lamp.sh"')
		info_message('LAMP successfully installed.')

	def service(self, service):
		methods = [x for x in dir(self) if not x.startswith('__')]
		if service in methods:
			method = getattr(self, service)
			method()
		else:
			error_message('Service do not supported!')
