#-- coding: utf-8 --#
__author__ = 'gotlium'


import os
import json
import shutil

from libraries.path import HostPath
from libraries.helpers import *


class Git_jail(HostPath):

	methods = ('add', 'delete', 'enable', 'disable', 'list')

	def __init__(self, base):
		self.base = base
		self.db_dir = self.base.git['jail_repositories']
		self.db_file = '%s/%s' % (self.db_dir, 'users.db')
		self.authorized_keys = '/home/git/.ssh/authorized_keys'
		self.data = {}
		self.__makeDir()
		self.__loadData()
		self.__checkUser()
		self.__checkBin()

	def __checkUser(self):
		if os.system('id git >& /dev/null') != 0:
			os.system('useradd -m -U -r -s /bin/bash -d /home/git git')
			os.system('chown git:git /home/git/ -R')
			os.system("su -l git -c 'ssh-keygen -t rsa'")

	def __checkBin(self):
		if not fileExists(self.base.git['bin_shell']):
			putFile(
				self.base.git['bin_shell'],
				getTemplate('git-shell-enforce-directory', 'py')
			)
			os.system('chmod +x %s' % self.base.git['bin_shell'])

	def __loadData(self):
		if fileExists(self.db_file):
			self.data = json.loads(getFile(self.db_file))

	def __saveData(self):
		putFile(self.db_file, json.dumps(self.data))

	def __makeDir(self, dir=None):
		dir = dir if dir else self.db_dir
		if not fileExists(dir):
			os.makedirs(dir, 0755)

	def __userExists(self, email):
		isEmail(email)
		if email not in self.data.keys():
			error_message('User not found!')

	def add(self, email):
		public_key = self.base.options.password
		isEmail(email)
		isPublicKey(public_key)

		if email in self.data.keys():
			error_message('User already exists!')

		user_dir = '%s/%s' % (self.db_dir, email)
		self.__makeDir(user_dir)

		self.data[email] = {
			'key': public_key,
			'dir': user_dir,
		}
		info_message('added successful!')

		line = 'command="%(bin_shell)s %(dir)s",no-port-forwarding,' \
			   'no-X11-forwarding,no-agent-forwarding,no-pty %(key)s'
		config = {}
		config.update(self.base.git)
		config.update(self.data[email])
		putFile(self.authorized_keys, line % config, 'a')

		info_message('Successful!')

	def delete(self, email):
		isEmail(email)
		self.__userExists(email)

		if fileExists(self.data[email]['dir']):
			shutil.rmtree(self.data[email]['dir'])

		del self.data[email]

		lines = []
		for line in getFileArr(self.authorized_keys):
			if line and email not in line:
				lines.append(line)
		putFile(self.authorized_keys, '\n'.join(lines))

		info_message('Successful!')

	def list(self, t):
		for email, data in self.data.items():
			info_message('*'*100, 'blue')
			info_message(email, 'lightgreen')
			for k,v in data.items():
				info_message('%s:' % k.upper(), 'bold')
				info_message(v, 'white')

			projects = os.listdir(data['dir'])
			if len(projects):
				info_message('Projects:', 'bold')
				for f in projects:
					info_message(
						'\tgit@%s:%s' % (self.base.main['external_ip'], f),
						'white'
					)
				info_message('*'*100, 'blue')

	def enable(self, folder):
		host_name = self.base.options.ip
		email = self.base.options.user
		isHost(host_name)
		self.__userExists(email)

		data = self.getHostData(host_name)
		website_dir = data['website_dir']
		full_path = '%s/%s' % (website_dir, folder)
		full_path_git = '%s/.git' % full_path
		repository = '%s/%s.git' % (self.data[email]['dir'], host_name)
		real_repository = '%s/%s.git' % (self.base.git['repositories'], host_name)
		user_hook = '%s/hooks/post-receive' % repository
		repo_hooks = '%s/.git/hooks' % website_dir

		self.__makeDir(repository)
		os.system('cd %s && git init --bare' % repository)
		putFile(
			'%s/.gitignore' % full_path,
			getTemplate('git-jail-gitignore-default')
		)
		os.system(
			'cd %s && git init && git remote add origin %s && git add . && '
			'git commit -am "Initial commit" && git push origin master' % (
			full_path, repository)
		)

		templates = {
			user_hook: 'git-jail-post-receive-user-repo',
			'%s/post-commit' % repo_hooks: 'git-jail-post-commit-repo',
			'%s/post-receive' % repo_hooks: 'git-jail-post-receive-repo',
			'%s/hooks/post-receive' % real_repository: 'git-jail-post-receive-real-repo',
		}

		for f,t in templates.items():
			putFile(f, getTemplate(t) % locals())
			os.system('chmod +x %s' % f)

		info_message('Successful!')

	def disable(self, folder):
		host_name = self.base.options.ip
		email = self.base.options.user
		isHost(host_name)
		self.__userExists(email)
		data = self.getHostData(host_name)
		website_dir = data['website_dir']
		repository = '%s/%s.git' % (self.data[email]['dir'], host_name)
		real_repository = '%s/%s.git' % (self.base.git['repositories'], host_name)
		user_hook = '%s/hooks/post-receive' % repository
		repo_hooks = '%s/.git/hooks' % website_dir

		os.unlink(user_hook)
		os.unlink('%s/post-commit' % repo_hooks)
		os.unlink('%s/post-receive' % repo_hooks)
		os.unlink('%s/hooks/post-receive' % real_repository)
		shutil.rmtree(repository)

		# todo: перезаписать в основном репозитории post-receive на оригинал, для деплоя

		info_message('Successful!')

	def __del__(self):
		self.__saveData()
