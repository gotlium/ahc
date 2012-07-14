__author__ = 'gotlium'

from os import mkdir, chdir
import random
import string
from datetime import datetime

from fs import *
from helpers import *

class CertificateGenerator(object):

	client_cert_name = 'client%s.key'
	client_cert_csr = 'client%s.csr'
	client_cert_crt = 'client%s.crt'
	client_cert_p12 = 'client%s.p12'

	def __init__(self, config):
		self.config = config
		for key, val in config.apache_cert.items():
			self.__setattr__(key, val)
		self.openssl = config.main['bin_openssl']

	def __getRand(self, size=6, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for x in range(size))

	def __getSerial(self):
		return getFile("%s/%s" % (self.cert_directory, self.serial)).replace('\n','')

	def __crlGen(self):
		system_by_code('%s ca -gencrl -config %s -out %s >& /dev/null' %
					   (self.openssl, self.config_file, self.crl_certificates))

	def __getDate(self, date=None):
		if not date:
			return ""
		return datetime.\
		strptime(date,"%y%m%d%H%M%SZ").\
		strftime('%Y-%m-%d %H:%M')

	def createDatabase(self):
		if not fileExists(self.cert_directory):
			mkdir(self.cert_directory)

		chdir(self.cert_directory)

		if fileExists(self.dir):
			raise Exception('Already installed!')
		mkdir(self.dir, 700)
		mkdir(self.certs, 700)
		mkdir(self.new_certs_dir, 700)
		mkdir(self.crl, 700)

		putFile(self.database, '')
		putFile(self.serial, '01')
		putFile(self.crlnumber, '01')

		config = """[ ca ]
default_ca	= %s

[ CA_CLIENT ]
dir	= %s
certs	= %s
new_certs_dir	= %s
crl_dir	= %s

database	= %s
serial	= %s
crlnumber	= %s

certificate	= %s
private_key	= %s

default_days	= %s
default_crl_days	= %s
default_md	= %s
policy	= %s

[ %s ]
countryName	= match
stateOrProvinceName	= match
localityName	= match
organizationName	= match
organizationalUnitName	= match
commonName	= match
emailAddress	= supplied
""" % (self.default_ca, self.dir, self.certs, self.new_certs_dir,
		self.crl, self.database, self.serial, self.crlnumber,
		self.certificate, self.private_key, self.default_days,
		self.default_crl_days, self.default_md, self.policy, self.policy)
		putFile(self.config_file, config)
		system_by_code(
			'%s req -new -newkey rsa:1024 -nodes -keyout %s -x509 -days %s -subj \
/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s/emailAddress=%s -out %s >& /dev/null' %
			(self.openssl, self.private_key, self.private_key_days, self.country, self.state, self.locality_name,
			 self.organization_name, self.organizational_unit_name, self.common_name, self.email_address,
			 self.certificate)
		)

		self.__crlGen()
		return True

	def addClient(self, email=None):
		if not email:
			raise Exception('User email cannot be null!')
		elif not fileExists(self.cert_directory):
			raise Exception('Installation folder not found!')

		chdir(self.cert_directory)

		num = self.__getSerial()
		keyout = self.client_cert_name % num
		csr = self.client_cert_csr % num
		crt = self.client_cert_crt % num
		p12 = self.client_cert_p12 % num
		password = self.__getRand()

		system_by_code(
			'%s req -new -newkey rsa:1024 -nodes -keyout %s -subj \
/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s/emailAddress=%s -out %s >& /dev/null' % \
			   (self.openssl, keyout, self.country, self.state, self.locality_name, self.organization_name,
				self.organizational_unit_name, self.common_name, email, csr)
		)

		system_by_code('%s ca -config %s -in %s -out %s -batch >& /dev/null' %
			   (self.openssl, self.config_file, csr, crt))

		if self.__getSerial() == num:
			raise Exception('Certificate file not created!')

		stdout = system('%s verify -CAfile %s %s' % (self.openssl, self.certificate, crt))
		if not len(stdout) or stdout[-1:][0].find(': OK') == -1:
			raise Exception('Error, when trying to verify certificate file!')

		system_by_code('%s pkcs12 -export -in %s -inkey %s -certfile %s -out %s -passout pass:%s >& /dev/null' %
			   (self.openssl, crt, keyout, self.certificate, p12, password))

		return {'password': password, 'certfile': '%s/%s' % (self.cert_directory, crt)}

	def delClient(self, email):
		clients = self.getClients(False)
		if not email:
			raise Exception('User email cannot be null!')
		elif not fileExists(self.cert_directory):
			raise Exception('Installation folder not found!')
		elif email not in clients:
			raise Exception('User not found!')

		chdir(self.cert_directory)

		system_by_code(
			'%s ca -config %s -revoke %s >& /dev/null' % \
			(self.openssl, self.config_file, self.client_cert_crt % clients[email])
		)
		self.__crlGen()
		return True

	def getClients(self, full = True):
		db = getFileArr("%s/%s" % (self.cert_directory, self.database))
		data = {}
		for i, line in enumerate(db):
			status, expiration, revocation, serial, filename, certificate = line.split("\t")
			email = line.split("=")[-1:][0]
			if full:
				data[i] = {
					'status': status,
					'serial': serial,
					'expiration': self.__getDate(expiration),
					'revocation': self.__getDate(revocation),
					'email': email,
					'certfile': '%s/%s' % (self.cert_directory, self.client_cert_crt % serial)
				}
			elif status == 'V':
				data[email] = serial
		return data
