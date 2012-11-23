__author__ = 'gotlium'

from os import chmod

from libraries.core_http import CoreHttp
from libraries.helpers import *
from libraries.fs import *

class Nginx(CoreHttp):

	fastcgi_run_commands = {
		'php': '/etc/init.d/php5-fpm restart',
		'django': 'cd %(project_root)s && chmod +x ./manage.py && nohup '
				'./manage.py runfcgi method=prefork socket=%(socket_path)s '
				'pidfile=%(pid_path)s >& /dev/null &',
		'django-venv': 'cd %(project_root)s && source venv/bin/activate && '
				'chmod +x ./manage.py && nohup '
				'./manage.py runfcgi method=prefork socket=%(socket_path)s '
				'pidfile=%(pid_path)s >& /dev/null &',
		'python': 'cd %(project_root)s && chmod +x ./index.py\nnohup '
				  './index.py >& /dev/null &\nPID=$!',
		'python-venv': 'cd %(project_root)s && source venv/bin/activate && '
					'chmod +x ./index.py\nnohup ./index.py >& /dev/null&\nPID=$!'

	}

	uwsgi_module = {
		'django': 'django.core.handlers.wsgi:WSGIHandler()',
		'python': 'index'
	}

	def __init__(self, base, web_server='nginx'):
		CoreHttp.__init__(self, base, web_server)
		self.ssl_template = 'include	%s;' % self.base.nginx['ssl_conf']

	def __getuWSGIHost(self):
		return '%s/%s.ini' % (self.base.uwsgi['sites_available'],
							  self.project_name)
	def __addWebsiteRunnerAndRun(self):
		if self.type == 'php':
			system_by_code('%s restart 1> /dev/null' % \
						   self.base.main['bin_php5_fpm'])
			return

		config = {
			'socket_path': self.socket_path,
			'pid_path': self.pid_path,
			'project_root': self.project_root,
			'project_name': self.project_name,
			'script_name': '%s.init' % self.project_name,
			'run_dir': self.run_dir,
			'root': self.project_root
		}

		if self.base.options.wsgi:
			config['module'] = self.uwsgi_module[self.type]
			if self.base.options.venv:
				putFile(
					self.__getuWSGIHost(),
					getTemplate('nginx-uwsgi-venv-host') % config
				)
			else:
				putFile(
					self.__getuWSGIHost(),
					getTemplate('nginx-uwsgi-host') % config
				)
		else:
			postfix = '-venv' if self.base.options.venv else ''
			cmd = self.fastcgi_run_commands[self.type+postfix] % config
			config['command_to_run'] = cmd
			init_file = '/etc/init.d/%s.init' % self.project_name
			putFile(init_file, getTemplate('nginx-host-runner') % config)
			system_by_code('chmod +x %s' % init_file)

		self.__setActive(True)

	def __delWebsiteRunner(self):
		if self.type == 'php':
			return False
		self.__setActive(False)
		delFile('/etc/init.d/%s.init' % self.project_name)
		delFile(self.__getuWSGIHost())

	def __djangoSettingsFlag(self):
		if self.type == 'django':
			info_message("Set \"FORCE_SCRIPT_NAME = ''\" in your project "
						 "settings.")

	def __setActiveuWSGI(self, flag):
		if flag:
			system_by_code('ln -s %s %s' % (self.__getuWSGIHost(),
											self.base.uwsgi['sites_enabled']))
			if isinstance(self.project_root, str):
				system_by_code('touch %s/touch_for_reload' % self.project_root)
			service_restart(self.base.uwsgi['init'])
		else:
			delFile(
				self.__getuWSGIHost().replace(
					self.base.uwsgi['sites_available'],
					self.base.uwsgi['sites_enabled']
				)
			)

	def __setActiveFastCGI(self, flag):
		if flag:
			action = 'start'
			system_by_code('%s %s.init defaults 1> /dev/null' %\
						   (self.base.main['bin_update_rc_d'], self.project_name))
		else:
			action = 'stop'
			system_by_code('%s -f %s.init remove 1> /dev/null' %\
						   (self.base.main['bin_update_rc_d'], self.project_name))
		init_file = '/etc/init.d/%s.init' % self.project_name
		system_by_code('%(init)s %(action)s' % {
			'init': init_file, 'action': action
		})

	def __setActive(self, flag):
		if self.type != 'php':
			if self.base.options.wsgi:
				self.__setActiveuWSGI(flag)
			else:
				self.__setActiveFastCGI(flag)

	def add(self, host_name):
		self._add(host_name)
		self.__addWebsiteRunnerAndRun()
		self.__djangoSettingsFlag()

	def delete(self, host_name):
		self._delete(host_name)
		self.__delWebsiteRunner()

	def enable(self, host_name):
		self._enable(host_name)
		self.__setActive(True)

	def disable(self, host_name):
		self._disable(host_name)
		self.__setActive(False)
