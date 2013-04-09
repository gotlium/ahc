# -*- coding: utf-8 -*-

__author__ = 'gotlium'

import os
from libraries.helpers import *


class Web():
    methods = ('add',)

    def __init__(self, base):
        base.getPathAndChDir()
        self.get_pid_cmd = "ps aux|grep [p]ython|grep [m]anage.py|grep [" \
                           "runserver]| awk '{print $2}'"

    def add(self, action):
        os.chdir('web/')

        if action == 'start':
            status = -1
            if not fileExists('db.sqlite'):
                os.system('/usr/bin/python manage.py syncdb')
            if not system(self.get_pid_cmd):
                status = os.system(
                    '/usr/bin/nohup /usr/bin/python manage.py runserver '
                    '127.0.0.1:8131 --insecure --noreload >& '
                    '/var/log/ahc-web.log &'
                )
        else:
            status = os.system(
                "%s|xargs kill -9>&/dev/null" % self.get_pid_cmd
            )
        os._exit(0 if status == 0 else -1)
