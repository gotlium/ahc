# -*- coding: utf-8 -*-

__author__ = 'GoTLiuM InSPiRIT <gotlium@gmail.com>'
__date__ = "26.10.12"

from django.contrib import admin

from models import *
from forms import *

class MySQLInline(admin.TabularInline):
	extra = 1
	model = MySQL
	form = MySQLAdminForm


class FTPInline(admin.TabularInline):
	extra = 1
	model = FTP
	form = FTPAdminForm


class DNSInline(admin.TabularInline):
	extra = 1
	model = DNS
	form = DNSAdminForm


class HostAdmin(admin.ModelAdmin):
	fieldsets = [
		('Basic', {'fields': [
			'name'
		],
		}),
		('WebServer', {'fields': [
			'server',
			'server_type',
			'server_module',
			'static',
			'status'
		],
		}),
		('Additionally', {'fields': [
			'git'
		]
		}),
		]
	list_filter = (
		'server', 'server_type', 'server_module', 'status', 'created', 'updated'
	)
	list_display = (
		'name', 'server', 'server_type', 'server_module', 'static', 'status',
		'created', 'updated', 'id'
	)
	list_display_links = ('name', )
	search_fields = ('name', )
	ordering = ('id',)
	list_per_page = 10

	inlines = [MySQLInline, FTPInline, DNSInline]

	def get_readonly_fields(self, request, obj=None):
		if obj is not None:
			return self.readonly_fields + ('name','server',
										   'server_type',
										   'server_module',
										   'static',)
		return self.readonly_fields


admin.site.register(Host, HostAdmin)