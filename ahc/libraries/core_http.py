__author__ = 'gotlium'

import os
import re
import crypt

from helpers import *
from fs import *
from path import HostPath


class CoreHttp(HostPath):
    methods = ('add', 'delete', 'enable', 'disable',)

    def __init__(self, base, web_server='apache2'):
        self.web_server = web_server
        self.base = base
        self.type = base.options.type
        if not base.options.type:
            self.type = self.base.main['default_type']
        self.config = base.__getattribute__(self.web_server)
        checkInstall(self.config)


    def __getattr__(self, method):
        def find_method(*args, **kwargs):
            getattr(self, '_%s' % method)(*args, **kwargs)

        return find_method

    def __install_virtual_env(self, root, project, is_django=True):
        system_by_code(
            'cd %s && mkdir venv && virtualenv --no-site-packages '
            '--prompt="(%s)" venv' % (root, project)
        )
        if is_django:
            system_by_code(
                'cd %s && source venv/bin/activate && pip install django && '
                'deactivate' % root
            )
        if self.base.options.venv and not self.base.options.wsgi and \
                        self.base.options.module == 'nginx':
            system_by_code(
                'cd %s && source venv/bin/activate && pip install flup && '
                'deactivate' % root
            )
        return system("find %s/venv/ -type d -name 'site-packages'" % root)[0]

    def __createBasicAuthFile(self, filename, user, password):
        user = user.strip()
        password = password.strip()
        return putFile(filename, "%s:%s" % (user, crypt.crypt(password,
                                                              password)))

    def __authTemplate(self, project_root):
        filename = '%s/.htpasswd' % self.project_root
        if self.base.options.auth:
            login, password = self.base.options.auth.split(':')
            if self.__createBasicAuthFile(filename, login, password):
                if self.web_server == 'nginx':
                    return getTemplate('nginx-auth') % {'filename': filename}
                else:
                    return getTemplate('apache2-auth') % {'filename': filename}
            else:
                info_message('Warning: Password not created!', 'white')
        return ""

    def __getTemplate(self, template, ext='conf'):
        if self.base.options.venv and not self.base.options.wsgi and \
                        self.base.options.module == 'apache':
            filename = 'templates/%s-%s-mod_python-venv.%s' % \
                       (self.web_server, template, ext)
            if not fileExists(filename):
                error_message('VirtualEnv not supported for current type!')
            return getFile(filename)
        elif self.base.options.wsgi:
            filename = 'templates/%s-%s-wsgi.%s' % \
                       (self.web_server, template, ext)
            if not fileExists(filename):
                error_message('WSGI not supported for current type!')
            return getFile(filename)
        return getFile('templates/%s-%s.%s' % \
                       (self.web_server, template, ext))

    def __optimizationTemplate(self):
        if self.base.options.optimize and self.web_server == 'apache2':
            return getTemplate('apache2-static-tune')
        return ""

    def __setSocketAndPidPath(self, host_name):
        host_name = host_name.replace('.', '_')
        self.run_dir = '/var/run/%s' % self.web_server
        if not fileExists(self.run_dir):
            os.mkdir(self.run_dir)
        self.project_name = host_name
        self.socket_path = '%s/%s.sock' % (self.run_dir, host_name)
        self.pid_path = '%s/%s.pid' % (self.run_dir, host_name)

    def __setup_standard(self, host_name, data, files):
        ext = {
            'python': 'py',
            'php': 'php',
            'ruby': 'rb'
        }
        if self.type in ext.keys():
            ext = ext[self.type]
            index_file = '%s/index.%s' % (data['website_dir'], ext)
        else:
            error_message('Type not supported!')
        self.project_root = data['website_dir']
        project = self.__get_project_name(host_name)
        venv = ""
        if self.base.options.venv:
            venv = self.__install_virtual_env(
                self.project_root, host_name, False
            )
            if self.base.options.module == 'apache':
                if self.base.options.wsgi:
                    venv = ":%s" % venv
                else:
                    putFile('%s/%s.py' % (self.project_root, project), """
activate_this = '%s/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from index import *
					""" % self.project_root)
        config = {
            'port': self.config['port'],
            'hostname': host_name,
            'root': data['website_dir'],
            'ssl_section': '',
            'venv': venv,
            'project': project,
            'optimize': self.__optimizationTemplate(),
            'socket_path': self.socket_path,
            'pid_path': self.pid_path,
            'basic_auth': self.__authTemplate(self.project_root)
        }
        if fileExists(files['host_file']):
            error_message('Host "%s" file is used!' % files['host_file'])
        if not putFile(files['host_file'],
                       self.__getTemplate(self.type) % config):
            system_by_code("Error, when trying to save host file!")
        if int(self.base.main['use_ssl']) == 1:
            if fileExists(files['ssl_host_file']):
                error_message('Host file is used!')
            config['port'] = self.config['ssl_port']
            config['ssl_section'] = self.ssl_template
            if not putFile(files['ssl_host_file'],
                           self.__getTemplate(self.type) % config):
                system_by_code("Error, when trying to save ssl host file!")
        if not putFile(index_file,
                       self.__getTemplate(self.type, ext) % config):
            system_by_code("Error, when trying to save example file!")
        os.chmod(index_file, 0777)

    def _setup_php(self, host_name, data, files):
        self.__setup_standard(host_name, data, files)

    def _setup_ruby(self, host_name, data, files):
        if self.web_server == 'nginx':
            error_message('Type not supported!')
        self.__setup_standard(host_name, data, files)

    def _setup_python(self, host_name, data, files):
        self.__setup_standard(host_name, data, files)

    def _setup_ror(self, host_name, data, files):
        if self.web_server == 'nginx':
            error_message('Type is not supported!')
        self.project_root = data['website_dir']
        bin = self.base.main['bin_rails']
        config = {
            'port': self.config['port'],
            'hostname': host_name,
            'root': '%s/public' % self.project_root,
            'ssl_section': '',
            'projects_dir': self.base.main['projects_directory'],
            'optimize': self.__optimizationTemplate(),
            'socket_path': self.socket_path,
            'pid_path': self.pid_path,
            'basic_auth': self.__authTemplate(self.project_root)
        }

        if not putFile(files['host_file'],
                       self.__getTemplate(self.type) % config):
            system_by_code("Error, when trying to save host file!")
        if int(self.base.main['use_ssl']) == 1:
            config['port'] = self.config['ssl_port']
            config['ssl_section'] = self.ssl_template
            if not putFile(files['ssl_host_file'],
                           self.__getTemplate(self.type) % config):
                system_by_code("Error, when trying to save example file!")
        system_by_code('cd %s && %s www' % (data['domain_dir'], bin))
        try:
            uid = int(self.base.main['useruid'])
            os.chown(self.project_root, uid, uid)
        except:
            error_message("Can't change permissions to directory!")


    def __get_project_name(self, host_name):
        project = host_name.replace('-', '_').replace('.', '_')
        return re.sub('([^a-z0-9_])+', '', project)

    def _setup_django(self, host_name, data, files):
        self.project_root = data['website_dir']
        bin = self.base.main['bin_django_admin']
        project = self.__get_project_name(host_name)

        if fileExists('/tmp/new_django_project'):
            system_by_code('rm -rf /tmp/new_django_project')
        system_by_code('cd /tmp/ && %s startproject new_django_project' % bin)
        system_by_code('mv /tmp/new_django_project/* %s/' % self.project_root)

        venv = ""
        if self.base.options.venv:
            venv = self.__install_virtual_env(self.project_root, project)
            if self.base.options.module == 'apache':
                if self.base.options.wsgi:
                    venv = ":%s" % venv
                else:
                    putFile('%s/%s.py' % (self.project_root, project), """
activate_this = '%s/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from django.core.handlers.modpython import handler
					""" % self.project_root)

        config = {
            'port': self.config['port'],
            'hostname': host_name,
            'root': self.project_root,
            'project_name': project,
            'ssl_section': '',
            'venv': venv,
            'projects_dir': self.base.main['projects_directory'],
            'optimize': self.__optimizationTemplate(),
            'socket_path': self.socket_path,
            'pid_path': self.pid_path,
            'basic_auth': self.__authTemplate(self.project_root)
        }

        if not putFile(files['host_file'],
                       self.__getTemplate(self.type) % config):
            system_by_code("Error, when trying to save host file!")
        if int(self.base.main['use_ssl']) == 1:
            config['port'] = self.config['ssl_port']
            config['ssl_section'] = self.ssl_template
            if not putFile(files['ssl_host_file'],
                           self.__getTemplate(self.type) % config):
                system_by_code("Error, when trying to save example file!")

    def __mainDomainInstall(self, host_name):
        base_domain = '.'.join(host_name.split('.')[1:])
        data = self.getHostData(base_domain)
        if not fileExists(data['website_dir']):
            self.add(base_domain)
            info_message('')

    def __siteSetActive(self, host_name='', isActive=True):
        info = self.getHostFiles(host_name, self.type, self.web_server)
        if isActive:
            host_cmd = 'ln -s %s %s' % (
                info['host_file'], info['enable_host_file'])
            ssl_host_cmd = 'ln -s %s %s' % (
                info['ssl_host_file'], info['enable_ssl_host_file'])
            action = 'add'
        else:
            host_cmd = 'rm -rf %s' % info['enable_host_file']
            ssl_host_cmd = 'rm -rf %s' % info['enable_ssl_host_file']
            action = 'del'

        isHost(host_name)

        system_by_code(host_cmd)
        if int(self.base.main['use_ssl']) == 1:
            system_by_code(ssl_host_cmd)
        if self.web_server == 'nginx':
            service_restart(self.config['init'])
        else:
            service_restart(self.config['init'], 'reload')

        if not hosts(action, host_name):
            error_message("Error, when trying to change hosts data!")

    def _add(self, host_name):
        if not hasattr(self, '_setup_%s' % self.type):
            error_message("Please, check your command line arguments!")

        isHost(host_name)
        data = self.getHostData(host_name)
        files = self.getHostFiles(host_name, self.type, self.web_server)
        if data['is_subdomain']:
            self.__mainDomainInstall(host_name)

        if fileExists(data['website_dir']):
            error_message('Website "%s" is exists!' % host_name)

        os.mkdir(data['domain_dir'], 0755)
        os.mkdir(data['website_dir'], 0755)

        self.__setSocketAndPidPath(host_name)
        method = self.__getattribute__('_setup_%s' % self.type)
        method(host_name, data, files)
        self.__siteSetActive(host_name, True)
        try:
            uid = int(self.base.main['useruid'])
            os.chown(data['domain_dir'], uid, uid)
            if fileExists(data['website_dir']):
                os.chown(data['website_dir'], uid, uid)
            os.system('find %s -type f|xargs chmod 0644' % self.project_root)
            os.system('find %s -type f|xargs chmod 0755' % self.project_root)
        except:
            error_message("Can't change permissions to directory!")

        info_message('Site successfully added.')
        info_message(
            'For check http use this command:\n\tlinks http://%s:%s/' % \
            (host_name, self.config['port'])
        )
        if self.base.main['use_ssl']:
            info_message(
                'For check https use this command:\n\tlinks https://%s:%s/' % \
                (host_name, self.config['ssl_port'])
            )

    def _delete(self, host_name):
        isHost(host_name)
        data = self.getHostData(host_name)
        files = self.getHostFiles(host_name, self.type, self.web_server)
        domain_dir = data['domain_dir']

        if not fileExists(domain_dir):
            error_message('Projects directory not exists!')

        self.__setSocketAndPidPath(host_name)
        self.__siteSetActive(host_name, False)

        if fileExists(files['host_file']):
            delFile(files['host_file'])

        if fileExists(files['ssl_host_file']):
            delFile(files['ssl_host_file'])

        if self.base.options.yes:
            msg = 'y'
        else:
            msg = raw_input("Remove project folder '%s'? (Yes/No)" % host_name)
        if str(msg).lower() in ('y', 'yes'):
            os.system("rm -r %s" % domain_dir)

        info_message("Project '%s' successfully removed." % host_name)

    def _enable(self, host_name):
        self.__setSocketAndPidPath(host_name)
        self.__siteSetActive(host_name, True)
        info_message('"%s" - enabled.' % host_name)

    def _disable(self, host_name):
        self.__setSocketAndPidPath(host_name)
        self.__siteSetActive(host_name, False)
        info_message('"%s" - disabled.' % host_name)
