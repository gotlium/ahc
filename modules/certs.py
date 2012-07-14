__author__ = 'gotlium'

from libraries.apache import CertificateGenerator
from libraries.helpers import info_message, error_message

class Certs(CertificateGenerator):

	methods = ('add', 'delete', 'list',)
	base = None
	type = None

	def __init__(self, base):
		CertificateGenerator.__init__(self, base)
		self.base = base
		self.type = base.options.type

	def add(self, email):
		try:
			data = self.addClient(email)
			if data:
				info_message('Certificate for "%s" was successfully installed.' % email)
				info_message('User password: %s' % data['password'], 'white')
				info_message('User certificate file: %s' % data['certfile'], 'white')
			else:
				error_message("Can't add new user!")
		except Exception, msg:
			error_message(msg)

	def delete(self, email):
		try:
			if not self.delClient(email):
				error_message("Can't revoke user certificate!")
			info_message('Certificate for "%s" was successfully revoked.' % email)
		except Exception, msg:
			error_message(msg)

	def _gf(self, txt, max = 16):
		return '%*s' % (max, txt)

	def list(self, host):
		try:
			clients = self.getClients()
			max_mail = max(map(len, [r['email'] for r in clients.values()]))
			print(
				'%s\t%s\t%s\t%s\t%s\t%s' % \
				('Serial', 'Status', self._gf('Email', max_mail),
				 self._gf('Expiration'), self._gf('Revocation'), 'Certfile')
			)
			for i, row in clients.items():
				email = self._gf(row['email'], max_mail)
				expiration = self._gf(row['expiration'])
				revocation = self._gf(row['revocation'])
				print (
					'%s\t%s\t%s\t%s\t%s\t%s' % \
					(row['serial'], row['status'], email,
					 expiration, revocation, row['certfile']
				))
		except Exception, msg:
			error_message(msg)
