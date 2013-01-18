# -*- coding: utf-8 -*-

import os

from django import forms
from django.db import models


class ImagesDirField(forms.ChoiceField):
	def __init__(self, path, match=None, recursive=False, required=False,
				 widget=None, label=None, initial=None, help_text=None,
				 short=False,
				 *args, **kwargs):
		self.path, self.match, self.recursive = path, match, recursive
		super(ImagesDirField, self).__init__(choices=(), required=required,
			widget=widget, label=label, initial=initial, help_text=help_text,
			*args, **kwargs)

		if self.required:
			self.choices = []
		else:
			self.choices = [("", "---------")]

		slice_slashes = path.count('/') + 2
		folders = []
		for root, dirs, files in sorted(os.walk(self.path)):
			for f in dirs:
				if self.match is None or self.match_re.search(f):
					f = os.path.join(root, f)
					lf = f.lower()
					if lf.find('.git') == -1 and lf.find('cache') == -1:
						if not short:
							dirname = (f, f.replace(path, "", 1).replace("\\", "/"))
						else:
							domain = f.replace(path, '').split('/')[0]
							f = '/'.join(f.split('/')[slice_slashes:slice_slashes+3])
							if f:
								dirname = (f, '%s - %s' % (domain,f))
							else:
								dirname = ('', '')
						if os.path.islink(f):
							continue
						if f not in folders:
							self.choices.append(
								dirname
							)
							folders.append(f)
		self.widget.choices = self.choices


class DirectoryPathField(models.Field):
	description = "Field Gets Paths List for Images"

	def __init__(self, verbose_name=None, name=None, path="", match=None,
				 recursive=False, **kwargs):
		self.path, self.match, self.recursive = path, match, recursive
		kwargs['max_length'] = kwargs.get('max_length', 250)
		self.short = kwargs.pop('short', False)
		models.Field.__init__(self, verbose_name, name, **kwargs)

	def formfield(self, **kwargs):
		defaults = {
			'path': self.path,
			'match': self.match,
			'short': self.short,
			'recursive': self.recursive,
			'form_class': ImagesDirField,
		}
		defaults.update(kwargs)
		return super(DirectoryPathField, self).formfield(**defaults)

	def get_internal_type(self):
		return "CharField"
