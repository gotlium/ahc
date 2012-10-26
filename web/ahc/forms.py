from django import forms
import os


class AbstractAdminForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AbstractAdminForm, self).__init__(*args, **kwargs)
		if getattr(self.instance, self.check_field):
			for field in self.fields.keys():
				self.fields[field].widget.attrs['readonly'] = 'readonly'


class MySQLAdminForm(AbstractAdminForm):
	check_field = 'db_name'


class FTPAdminForm(AbstractAdminForm):
	check_field = 'ftp_user'


class DNSAdminForm(AbstractAdminForm):
	check_field = 'domain'

