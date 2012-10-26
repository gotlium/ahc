# -*- coding: utf-8 -*-

__author__ = 'gotlium'

import os
from libraries.helpers import *

class Web():
	methods = ('add',)

	def __init__(self, base):
		base.getPathAndChDir()

	def add(self, action):
		os.chdir('web/')

		if action == 'start':
			os.system('/usr/bin/python manage.py syncdb')
			os.system(
				'/usr/bin/nohup /usr/bin/python manage.py runserver '
				'127.0.0.1:8131 --insecure --noreload >& /var/log/ahc-web.log &'
			)
			info_message('Started ..')
		else:
			os.system("ps aux|grep [p]ython|grep [m]anage.py|grep ["
					  "runserver]| awk '{print $2}'|xargs kill -9>&/dev/null"
			)
			info_message('Stopped ..')
