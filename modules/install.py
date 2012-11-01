__author__ = 'gotlium'

from socket import gethostname
import MySQLdb
import getpass, pwd
import os

from libraries.helpers import *
from libraries.apache import CertificateGenerator

class Install(object):

	def __init__(self, base):
		self.base = base
		self.methods = ('service',)

	def __getMySQLPassword(self):
		if not self.base.mysql['password']:
			password = getpass.getpass("Root password: ")
		else:
			password = self.base.mysql['password']
		return password

	def certs(self):
		cert = CertificateGenerator(self.base)
		if cert.createDatabase():
			info_message('"Apache SSL Certs Protection" was successfully installed.')

	def shell(self):
		home = os.getenv('HOME')
		shell = os.getenv('SHELL')
		if shell.find('/bash') != -1:
			configuration = getTemplate('bashrc')
			filename = '%s/.bashrc' % home
		elif shell.find('/zsh') != -1:
			configuration = getTemplate('zshrc')
			filename = '%s/.zshrc' % home
		else:
			error_message('Sorry, your shell not supported!')
		if fileExists(filename):
			backFile(filename)
		putFile(filename, configuration)
		os.system('. %s' % filename)
		info_message('Shell config for "%s" successfully installed.' % shell)

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

		password = self.__getMySQLPassword()

		try:
			db = MySQLdb.connection(
				self.base.mysql['host'], self.base.mysql['user'], password
			)
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

		pam_configuration = {
			'db_user': db_user, 'db_password': db_password, 'db_name': db_name
		}
		putFile(pam_config, getTemplate('vsftpd-pam-auth') % pam_configuration)

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
		system_by_code('chmod 0777 %s' % sendmail_bin)
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

	def confluence(self):
		domain = None
		ip = None

		if fileExists(self.base.apache2['sites_available'] +
					  '/confluence.conf'):
			error_message('Confluence was installed!')

		for i in range(3):
			input = raw_input('Enter basic domain name: ')
			if isValidHostname(input):
				domain = input
				break
		if not domain:
			error_message('Domain name is not valid!')

		for i in range(3):
			input = raw_input('Enter server external ip-address: ')
			if isValidIp(input):
				ip = input
				break
		if not ip:
			error_message('IP-address is not valid!')

		conf = {
			'domain': domain,
			'ip': ip,
			'port': self.base.apache2['port']
		}

		info_message("Use the following port 8090 in Jira.", 'cyan')

		template = getTemplate('apache2-confluence') % conf
		system_by_code('%s proxy >& /dev/null' % self.base.apache2['bin_a2enmod'])
		system_by_code('%s proxy_http >& /dev/null' % self.base.apache2['bin_a2enmod'])
		os.chdir('/usr/src/')

		system_by_code( 'http://www.atlassian.com/software/confluence/downloads/'
						'binary/atlassian-confluence-4.3.1-x64.bin')
		system_by_code('chmod +x atlassian-confluence-4.3.1-x64.bin')
		os.system('./atlassian-confluence-4.3.1-x64.bin')

		putFile(
			self.base.apache2['sites_available'] + '/confluence.conf', template
		)
		system_by_code(
			'%s confluence.conf >& /dev/null' % self.base.apache2['bin_a2ensite']
		)
		service_restart(
			self.base.apache2['init'], 'reload'
		)
		system_by_code('ahc -m bind -a confluence.%(domain)s -i %(ip)s >& '
					   '/dev/null' % conf)

		info_message("Use this credentials, on Confluence installation "
					 "interface:")
		system_by_code('ahc -m mysql -a confluence -u confluence -p random')

		info_message("Access to Confluence: http://confluence.%(domain)s/" % conf)

	def jira(self):
		domain = None
		ip = None

		if fileExists(self.base.apache2['sites_available'] + '/jira.conf'):
			error_message('Jira was installed!')

		for i in range(3):
			input = raw_input('Enter basic domain name: ')
			if isValidHostname(input):
				domain = input
				break
		if not domain:
			error_message('Domain name is not valid!')

		for i in range(3):
			input = raw_input('Enter server external ip-address: ')
			if isValidIp(input):
				ip = input
				break
		if not ip:
			error_message('IP-address is not valid!')

		conf = {
			'domain': domain,
			'ip': ip,
			'port': self.base.apache2['port']
		}

		info_message("Use the following port 8000 in Jira.", 'cyan')

		template = getTemplate('apache2-jira') % conf
		system_by_code('%s proxy >& /dev/null' % self.base.apache2['bin_a2enmod'])
		system_by_code('%s proxy_http >& /dev/null' % self.base.apache2['bin_a2enmod'])
		os.chdir('/usr/src/')

		system_by_code('wget http://www.atlassian.com/software/jira/downloads'
						'/binary/atlassian-jira-5.1.6-x64.bin')
		system_by_code('chmod +x atlassian-jira-5.1.6-x64.bin')
		os.system('./atlassian-jira-5.1.6-x64.bin')

		putFile(
			self.base.apache2['sites_available'] + '/jira.conf', template
		)
		system_by_code(
			'%s jira.conf >& /dev/null' % self.base.apache2['bin_a2ensite']
		)
		service_restart(
			self.base.apache2['init'], 'reload'
		)
		system_by_code('ahc -m bind -a jira.%(domain)s -i %(ip)s >& '
					   '/dev/null' % conf)

		info_message("Use this credentials, on Jira installation interface:")
		system_by_code('ahc -m mysql -a jira -u jira -p random')

		info_message("Access to Jira: http://jira.%(domain)s/" % conf)

	def mail(self):
		password = self.__getMySQLPassword()

		try:
			db = MySQLdb.connection(
				self.base.mysql['host'], self.base.mysql['user'], password
			)
		except Exception:
			db = MySQLdb.connection(
				self.base.mysql['host'], self.base.mysql['user'], ''
			)
		except Exception, msg:
			error_message(msg)

		db.query("SET PASSWORD FOR root@localhost=PASSWORD('');")

		answer = raw_input('Clear all data if exists [y/N]? ')
		if answer.lower() in ('y', 'yes'):
			db.query("DROP DATABASE IF EXISTS amavisd;")
			db.query("DROP DATABASE IF EXISTS cluebringer;")
			db.query("DROP DATABASE IF EXISTS iredadmin;")
			db.query("DROP DATABASE IF EXISTS roundcubemail;")
			db.query("DROP DATABASE IF EXISTS vmail;")

			system_by_code('rm -rf /etc/postfix/*.[0-9]*[0-9]*[0-9]*[0-9]*[0-9]*[0-9]')
			system_by_code('rm -rf /etc/dovecot/*.[0-9]*[0-9]*[0-9]*[0-9]*[0-9]*[0-9]')
			system_by_code('rm -rf /etc/spamassassin/*.[0-9]*[0-9]*[0-9]*[0-9]*[0-9]*[0-9]')
			system_by_code(
				'rm -rf %s/*/*.[0-9]*[0-9]*[0-9]*[0-9]*[0-9]*[0-9]' % self.base.apache2['etc']
			)
			system_by_code('rm -rf /usr/src/iRedMail-*')

		db.close()

		hostname = self.base.mail['hostname']
		ip_address = '127.0.0.1'
		putFile('/etc/hostname', hostname)
		putFile('/etc/hosts', '%s\t%s\tmail' % (ip_address, hostname), 'a')
		system_by_code('hostname %s' % hostname)

		if gethostname() != hostname:
			error_message("Can't set hostname!")

		os.chdir('/usr/src/')
		system_by_code('wget https://bitbucket.org/zhb/iredmail/downloads/iRedMail-0.8.2.tar.bz2')
		system_by_code('tar jxvf iRedMail-0.8.2.tar.bz2')
		os.chdir('/usr/src/iRedMail-0.8.2/pkgs/')
		system_by_code('/bin/bash get_all.sh')
		os.chdir('/usr/src/iRedMail-0.8.2/')

		info_message('INSTRUCTION: ', 'cyan')
		info_message('Default mail storage path: /var/vmail')
		info_message('Backend for mail accounts: MySQL')
		info_message('Disable DKIM signing/verification')
		info_message('Disable AWSTATS')
		info_message('Disable Fail2ban')
		info_message('Disable firewall rules provided by iRedMail')

		raw_input('Are you remember all? Press enter for next step.')

		system_by_code('/bin/bash iRedMail.sh')

		self.base.getPathAndChDir()

		if not putFile(
			'/etc/apache2/conf.d/iredadmin.conf',
			getTemplate('mail-apache2-iredadmin')
		):
			error_message("Can't write apache2->iredadmin config!")

		postfixConf = '/etc/postfix/main.cf'
		comments = [
			'content_filter', 'smtpd_end_of_data_restrictions',
			'smtp-amavis_destination_recipient_limit',
			'smtpd_recipient_restrictions', 'mailbox_size_limit'
		]
		postfix = getFile(postfixConf)
		for comment in comments:
			postfix = postfix.replace(comment, '# %s' % comment)
		postfix += "\nsmtpd_recipient_restrictions = permit_mynetworks, reject_unauth_destination\n"
		postfix += "\nmailbox_size_limit = 10240000\n"
		if not putFile(postfixConf, postfix):
			error_message("Can't write postfix config!")

		dovecotConf = '/etc/dovecot/dovecot.conf'
		dovecot = getFile(dovecotConf)
		dovecot = dovecot.replace(
			'disable_plaintext_auth = yes', 'disable_plaintext_auth = no'
		)
		dovecot = dovecot.replace(
			'ssl = required', 'ssl = yes'
		)
		if not putFile(dovecotConf, dovecot):
			error_message("Can't write dovecot config!")

		system_by_code(
			'rm -rf %s/*/*.[0-9]*[0-9]*[0-9]*[0-9]*[0-9]*[0-9]' % self.base.apache2['etc']
		)

		if fileExists(self.base.firewall['bin']):
			system_by_code('%s restart' % self.base.firewall['bin'])

		system_by_code('/etc/init.d/postfix restart >& /dev/null')
		system_by_code('/etc/init.d/dovecot stop >& /dev/null')
		system_by_code('/etc/init.d/dovecot start >& /dev/null')
		system_by_code('%s restart >& /dev/null' % self.base.apache2['init'])

		info_message('All basic config for working with mail is set.')

	def web(self):
		configuration = getTemplate('web-runner')
		init = '/etc/init.d/ahc-web'

		if fileExists(init):
			error_message('Web application already installed.')

		for i in range(3):
			input = raw_input('Enter basic domain name: ')
			if isValidHostname(input):
				domain = input
				break
		if not domain:
			error_message('Domain name is not valid!')

		for i in range(3):
			input = raw_input('Enter server external ip-address: ')
			if isValidIp(input):
				ip = input
				break
		if not ip:
			error_message('IP-address is not valid!')

		conf = {
			'domain': domain,
			'ip': ip,
			'port': self.base.apache2['port']
		}

		template = getTemplate('web-apache') % conf
		system_by_code('%s proxy >& /dev/null' % self.base.apache2['bin_a2enmod'])
		system_by_code('%s proxy_http >& /dev/null' % self.base.apache2['bin_a2enmod'])

		putFile(
			self.base.apache2['sites_available'] + '/ahc-web.conf', template
		)
		system_by_code(
			'%s ahc-web.conf >& /dev/null' % self.base.apache2['bin_a2ensite']
		)
		service_restart(
			self.base.apache2['init'], 'restart'
		)
		system_by_code('ahc -m bind -a ahc.%(domain)s -i %(ip)s >& '
					   '/dev/null' % conf)

		hosts('add', "ahc.%(domain)s" % conf)

		putFile(init, configuration)
		os.system('chmod +x %s' % init)
		os.system('update-rc.d ahc-web defaults >& /dev/null')
		os.system('cd web/ && pip install -r requirements.txt && cd -')

		os.system('%s start' % init)

		info_message("Access to ahc: http://ahc.%(domain)s/" % conf)

		info_message('Web application was successfully installed.')

	def vpn(self):
		pass
		'''
		config to /etc/openvpn/server.conf
		cd  /usr/share/doc/openvpn/examples/easy-rsa/2.0
		bash
		. ./vars
		./clean-all
		./build-ca
		./build-key-server server
		./build-dh
		cp ca.crt /etc/openvpn/ca.crt
		cp server.crt /etc/openvpn/server.crt
		cp dh1024.pem /etc/openvpn/dh1024.pem
		cp server.key /etc/openvpn/server.key
		'''