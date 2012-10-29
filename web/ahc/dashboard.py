# -*- encoding: utf-8 -*-

from grappelli.dashboard import modules, Dashboard

class CustomIndexDashboard(Dashboard):

	def init_with_context(self, context):

		self.children.append(modules.ModelList(
			u'Host Control',
			column=1,
			models=(
				'ahc.models.*',
				#'preferences.models.*'
			)
		))

		self.children.append(modules.ModelList(
			u'Users',
			column=1,
			collapsible=True,
			models=(
				'django.contrib.auth.models.User',
				'django.contrib.auth.models.Group',
			),
		))

		self.children.append(modules.RecentActions(
			u'Recent Actions',
			limit=13,
			collapsible=False,
			column=3,
		))
