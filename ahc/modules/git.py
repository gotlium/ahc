__author__ = 'gotlium'

from libraries.path import HostPath
from libraries.helpers import *


class Git(HostPath):
    methods = ('add', 'delete',)
    base = None

    def __init__(self, base):
        self.base = base
        if not fileExists(self.base.git['bin']):
            error_message('Git not installed!')

    def add(self, host_name):
        data = self.getHostData(host_name)
        website_dir = data['website_dir']

        if not fileExists(website_dir):
            error_message('Website is not installed!')

        repository = '%s/%s.git' % (self.base.git['repositories'], host_name)
        post_receive = '%s/hooks/post-receive' % repository
        external_ip = self.base.main['external_ip']

        if fileExists(repository):
            error_message(
                'File exists! Enter another hostname, or remove old repository!')
        system_by_code('mkdir -p %s' % repository)

        system_by_code('cd %s && git init --bare 1> /dev/null' % repository)

        if fileExists('%s/.git' % website_dir):
            system_by_code('cd %s && git remote rm origin' % website_dir)
        system_by_code(
            'cd %s && git init 1> /dev/null && git remote add origin %s' % \
            (website_dir, repository)
        )

        putFile(post_receive, getTemplate('git-post-receive') % data)
        system_by_code('chmod +x %s' % post_receive)

        remote = "\tgit remote add origin ssh://root@%s%s"
        info_message('*' * 100, 'blue')
        info_message('Successful!')
        info_message('*' * 100, 'blue')
        info_message('Use:', 'bold')
        info_message('\t"ssh-copy-id root@%s"' % external_ip)
        info_message('OR', 'yellow')
        info_message('\t"ssh-copy-id root@%s" on your host.' % host_name)
        info_message('*' * 100, 'blue')
        info_message('Add remote repository with following command:', 'white')
        info_message(remote % (external_ip, repository))
        info_message('OR', 'yellow')
        info_message(remote % (host_name, repository))
        info_message('*' * 100, 'blue')
        info_message(
            'Create ".git/hooks/post-commit" in your local repository with code below:',
            'white')
        info_message('#!/bin/sh')
        info_message('git push origin master')
        info_message('*' * 100, 'blue')

    def delete(self, host_name):
        data = self.getHostData(host_name)
        website_dir = data['website_dir']
        repository = '%s/%s.git' % (self.base.git['repositories'], host_name)

        if fileExists(repository):
            system_by_code('rm -rf %s' % repository)

        if fileExists('%s/.git' % website_dir):
            system_by_code('cd %s && git remote rm origin' % website_dir)

        info_message('Successful!')
