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
            email = system('git config --global user.email')
            name = system('git config --global user.email')
            if not email:
                os.system('git config --global user.email "root@localhost"')
            if not name:
                os.system('git config --global user.name "root"')

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
            os.system('chown git:git -R %s' % dir)

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
            'projects': {}
        }

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

        for (project, folders) in self.data[email]['projects'].items():
            for folder in folders:
                self.base.options.ip = project
                self.base.options.user = email
                self.disable(folder)

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
            info_message('*' * 100, 'blue')
            info_message(email, 'lightgreen')
            for k, v in data.items():
                if k != 'projects':
                    info_message('%s:' % k.upper(), 'bold')
                    info_message(v, 'white')

            projects = data['projects'].items()
            if len(projects):
                info_message('PROJECTS:', 'bold')
                for project, folders in projects:
                    info_message('\t[%s]' % project, 'bold')

                    info_message(
                        '\t\tRepo: git@%s:%s/{DIR}.git' % (
                            self.base.main['external_ip'], project
                        ),
                        'white'
                    )
                    info_message(
                        '\t\tDirs: %s' % ', '.join(
                            [folder for folder in folders]),
                        'white'
                    )

                info_message('*' * 100, 'blue')

    def enable(self, folder):
        host_name = self.base.options.ip
        email = self.base.options.user
        isHost(host_name)
        self.__userExists(email)

        data = self.getHostData(host_name)
        website_dir = data['website_dir']
        full_path = '%s/%s' % (website_dir, folder)
        full_path_git = '%s/.git' % full_path
        repository = '%s/%s/%s.git' % (
            self.data[email]['dir'], host_name, folder)
        real_repository = '%s/%s.git' % (
            self.base.git['repositories'], host_name)
        user_hook = '%s/hooks/post-receive' % repository
        repo_hooks = '%s/.git/hooks' % website_dir
        origin = md5(email)

        if not fileExists(full_path):
            error_message('Folder %s not exists!' % full_path)

        if not host_name in self.data[email]['projects']:
            self.data[email]['projects'][host_name] = []

        if folder in self.data[email]['projects'][host_name]:
            error_message('Repository already exists for this user!')
        self.data[email]['projects'][host_name].append(folder)

        self.__makeDir(repository)
        os.system('cd %s && git init --bare 1> /dev/null' % repository)
        putFile(
            '%s/.gitignore' % full_path,
            getTemplate('git-jail-gitignore-default')
        )

        os.system(
            'cd %(full_path)s && git init 1> /dev/null && '
            'git remote add %(origin)s %(repository)s && '
            'git add . && '
            'git commit -am "Initial commit" 1> /dev/null && '
            'git push %(origin)s master 1> /dev/null' % locals()
        )

        os.system('chown git:git -R %s' % full_path)
        os.system('chown git:git -R %s' % repository)
        os.system('chown git:git -R %s' % real_repository)
        os.system('chown git:git -R %s/.git' % website_dir)

        '''
        os.system(
            'cd %s; git rm --cached %s; git add ./%s/*' % (
            website_dir, folder, folder
        ))
        '''

        key = hash('%(email)s-%(host_name)s-%(folder)s' % locals())

        templates = {
            user_hook: 'git-jail-post-receive-user-repo',
            '%s/post-commit' % repo_hooks: 'git-jail-post-commit-repo',
            '%s/post-receive' % repo_hooks: 'git-jail-post-receive-repo',
            '%s/hooks/post-receive' % real_repository: 'git-jail-post-receive-real-repo',
        }

        putFile(
            '%s/hooks/post-receive.db' % real_repository,
            '%(website_dir)s;%(full_path)s;.;%(key)s;%(origin)s;' % locals(),
            'a'
        )

        putFile(
            '%s.db' % user_hook,
            '%(full_path)s;%(website_dir)s;./%(folder)s/*;%(key)s;%(origin)s;' % locals(),
            'a'
        )

        putFile(
            '%s/post-receive.db' % repo_hooks,
            '%(full_path)s;%(real_repository)s;%(key)s;%(origin)s;' % locals(),
            'a'
        )

        for f, t in templates.items():
            putFile(f, getTemplate(t) % locals())
            os.system('chmod +x %s' % f)

        info_message('Successful!')

    def __remove_from_db(self, filename, key):
        db = []
        key = ';%s;' % key
        for line in getFileArr(filename):
            if line and key not in line:
                db.append(line)
        putFile(filename, '\n'.join(db))

    def disable(self, folder):
        host_name = self.base.options.ip
        email = self.base.options.user
        isHost(host_name)
        self.__userExists(email)
        data = self.getHostData(host_name)
        website_dir = data['website_dir']
        repository = '%s/%s/%s.git' % (self.data[email]['dir'], host_name,
                                       folder)
        real_repository = '%s/%s.git' % (
            self.base.git['repositories'], host_name)
        repo_hooks = '%s/.git/hooks' % website_dir
        key = hash('%(email)s-%(host_name)s-%(folder)s' % locals())

        self.__remove_from_db(
            '%s/hooks/post-receive.db' % real_repository, key
        )
        self.__remove_from_db(
            '%s/post-receive.db' % repo_hooks, key
        )

        shutil.rmtree(repository)
        shutil.rmtree('%s/%s/.git' % (website_dir, folder))
        self.data[email]['projects'][host_name].remove(folder)
        if not len(self.data[email]['projects'][host_name]):
            del self.data[email]['projects'][host_name]
            shutil.rmtree('%s/%s/' % (self.data[email]['dir'], host_name))

        putFile(
            '%s/hooks/post-receive' % real_repository,
            getTemplate('git-post-receive') % data
        )

        info_message('Successful!')

    def __del__(self):
        self.__saveData()
