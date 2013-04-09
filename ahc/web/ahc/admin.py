# -*- coding: utf-8 -*-

__author__ = 'GoTLiuM InSPiRIT <gotlium@gmail.com>'
__date__ = "26.10.12"

#from preferences.admin import PreferencesAdmin
from django.contrib import admin

from ahc.models import (Host, DNS, FTP, MySQL, SSL, JAIL, GitUser)
from ahc.forms import (
    MySQLAdminForm, FTPAdminForm, DNSAdminForm, SSLAdminForm, JAILAdminForm
)


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


class SSLInline(admin.TabularInline):
    extra = 1
    model = SSL
    form = SSLAdminForm


class JAILInline(admin.TabularInline):
    extra = 1
    model = JAIL
    form = JAILAdminForm


class HostAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic', {'fields': ['name']}),
        ('Auth', {'fields': ['username', 'password']}),
        ('WebServer', {'fields': ['server', 'server_type', 'server_module',
                                  'ssl_certs', 'static', 'status']}),
        ('Additionally', {'fields': ['git']}),
    ]
    list_filter = (
        'server', 'server_type', 'server_module', 'status', 'created',
        'updated'
    )
    list_display = (
        'name', 'server', 'server_type', 'server_module', 'static', 'status',
        'created', 'updated', 'id'
    )
    list_display_links = ('name', )
    search_fields = ('name', )
    ordering = ('id',)
    list_per_page = 10

    inlines = [MySQLInline, FTPInline, DNSInline, SSLInline, JAILInline]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields + (
                'name', 'server', 'server_type', 'server_module',
                'static', 'ssl_certs', 'username', 'password',
            )
        return self.readonly_fields


'''
class PreferencesAdmin(PreferencesAdmin):
    exclude = ('sites',)
    form = PreferencesAdminForm

    def add_view(self, *args, **kwargs):
        return self.changelist_view(*args, **kwargs)
'''

admin.site.register(Host, HostAdmin)
admin.site.register(GitUser)
#admin.site.register(AhcPreferences, PreferencesAdmin)
