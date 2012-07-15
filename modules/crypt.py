__author__ = 'gotlium'

from getpass import getpass
from os.path import basename, dirname
from os import chown

from libraries.encfs import EncFS
from libraries.helpers import *

class Crypt(object):

	methods = ('add',)

	def __init__(self, base):
		self.base = base
		if not fileExists(self.base.encfs['bin']):
			error_message('EncFS not installed!')
		elif not fileExists(self.base.encfs['bin_fusermount']):
			error_message('Fuse not installed!')

	def add(self, action):
		if not self.base.encfs['password']:
			self.base.encfs['password'] = getpass("Root password: ")
		path = self.base.main['projects_directory']
		crypt = "%s/.%s" % (dirname(path), basename(path))
		try:
			e = EncFS(crypt, path, self.base.encfs)
			if not e.encrypt():
				if action in ('m', 'mount'):
					e.mount()
					info_message('Mounted.')
				elif action in ('e', 'encrypt'):
					e.mount()
					info_message('Encrypted.')
				elif action in ('d', 'decrypt'):
					e.decrypt()
					info_message('Decrypted.')
				else:
					e.umount()
					info_message('Unmounted.')
				system_by_code('chmod 0755 %s' % path)
				if fileExists(crypt):
					system_by_code('chmod 0755 %s' % crypt)
				try:
					uid = int(self.base.main['useruid'])
					chown(path, uid, uid)
				except Exception:
					error_message("Can't change permissions to directory!")
			else:
				info_message('Mount point was successfully created!')
		except Exception, msg:
			error_message(msg)
