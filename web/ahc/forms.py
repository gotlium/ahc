from django import forms


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


class SSLAdminForm(AbstractAdminForm):
	check_field = 'email'

class JAILAdminForm(AbstractAdminForm):
	check_field = 'folder'

'''
class PreferencesAdminForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(PreferencesAdminForm, self).__init__(*args, **kwargs)
		if self.instance and self.instance.pk:
			for field, value in self.fields.items():
				if getattr(self.instance, field) == True:
					self.fields[field].widget.attrs['disabled'] = True

	def clean(self):
		cleaned_data = self.cleaned_data
		if self.instance and self.instance.pk:
			for k,v in cleaned_data.items():
				if getattr(self.instance, k) == True:
					cleaned_data[k] = True
		return cleaned_data
'''