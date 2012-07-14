__author__ = 'gotlium'

from libraries.core_http import CoreHttp
from libraries.helpers import *
from libraries.fs import *

class Nginx(CoreHttp):

	fastcgi_run_commands = {
		'php': '/etc/init.d/php5-fpm restart',
		'django': 'cd %(project_root)s && chmod +x ./manage.py && nohup ./manage.py runfcgi method=prefork \
socket=%(socket_path)s pidfile=%(pid_path)s >& /dev/null &',
		'python': 'cd %(project_root)s && chmod +x ./index.py\nnohup ./index.py >& /dev/null &\nPID=$!'
	}

	def __init__(self, base, web_server='nginx'):
		CoreHttp.__init__(self, base, web_server)
		self.ssl_template = 'include	%s;' % self.base.nginx['ssl_conf']

	def __addWebsiteRunnerAndRun(self):
		if self.type == 'php':
			system_by_code('%s restart 1> /dev/null' % self.base.main['bin_php5_fpm'])
			return

		config = {
			'socket_path': self.socket_path,
			'pid_path': self.pid_path,
			'project_root': self.project_root,
			'project_name': self.project_name,
			'script_name': '%s.init' % self.project_name,
			'run_dir': self.run_dir
		}

		cmd = self.fastcgi_run_commands[self.type] % config
		config['command_to_run'] = cmd
		init_file = '/etc/init.d/%s.init' % self.project_name
		putFile(init_file, getTemplate('nginx-host-runner') % config)
		system_by_code('chmod +x %s' % init_file)
		self.__setActive(True)

	def __delWebsiteRunner(self):
		self.__setActive(False)
		if self.type == 'php':
			return False
		init_file = '/etc/init.d/%s.init' % self.project_name
		delFile(init_file)

	def __djangoSettingsFlag(self):
		if self.type == 'django':
			info_message("Set FORCE_SCRIPT_NAME = '' in project settings.")

	def __setActive(self, flag):
		if self.type != 'php':

			if flag:
				action = 'start'
				system_by_code('%s %s.init defaults 1> /dev/null' %\
							   (self.base.main['bin_update_rc_d'], self.project_name))
			else:
				action = 'stop'
				system_by_code('%s -f %s.init remove 1> /dev/null' % \
							   (self.base.main['bin_update_rc_d'], self.project_name))
			init_file = '/etc/init.d/%s.init' % self.project_name
			system_by_code('%(init)s %(action)s' % {'init': init_file, 'action': action})

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
