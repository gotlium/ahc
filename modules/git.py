__author__ = 'gotlium'

from libraries.helpers import *

class Git(object):

	methods = ('add', 'delete',)
	base = None

	def __init__(self, base):
		self.base = base
		if not fileExists(self.base.git['bin']):
			error_message('Git not installed!')

	def add(self, host_name):
		# folder = '/root/repositories'
		# external_ip = '192.168.253.1'
		# cd %(folder)s && mkdir %(host_name)s.git && git init --bare
		# cd project_dir && git init && git remote add origin repository && git pull origin master
		# git remote add origin ssh://root@%(external_ip)s/%(folder)s/%(host_name)s.git
		# git remote add origin ssh://root@127.0.0.1/%(folder)s/%(host_name)s.git
		pass

	def delete(self, host_name):
		pass
