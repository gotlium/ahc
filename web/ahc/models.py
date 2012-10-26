from ConfigParser import RawConfigParser
from django.db import models

from fields import DirectoryPathField


TYPES = (
	('django','django',),
	('python','python',),
	('php','php',),
)

SERVERS = (
	('apache','apache',),
	('nginx','nginx',),
)

MODS = (
	('default','default'),
	('wsgi', 'wsgi'),
)

config = RawConfigParser()
config.read('../configs.cfg')
external_ip = config.get('git', 'external_ip')
if external_ip == '192.168.0.1':
	external_ip = ""


class DatesModel(models.Model):
	created = models.DateTimeField('Created', auto_now = False,
		auto_now_add = True, editable=False)
	updated = models.DateTimeField('Updated', auto_now = True,
		auto_now_add = True, editable=False)

	class Meta:
		abstract = True


class Host(DatesModel):
	name = models.CharField('Name', max_length=50, unique=True)
	server = models.CharField('Webserver', choices=SERVERS, max_length=6,
		default='apache')
	server_type = models.CharField('Type', choices=TYPES, max_length=6,
		default='django')
	server_module = models.CharField('Module', choices=MODS, max_length=7,
		default='default')
	static = models.BooleanField('Static tune', default=True)
	git = models.BooleanField('GIT repository', default=True)
	status = models.BooleanField('availability status', default = True, db_index=True)

	class Meta:
		verbose_name = 'Host'
		verbose_name_plural = 'Hosts'

	def __unicode__(self):
		return self.name


class MySQL(DatesModel):
	db_name = models.CharField('DB name', max_length=16, unique=True)
	db_user = models.CharField('DB username', max_length=16)
	db_pass = models.CharField('DB password', max_length=16)
	host = models.ForeignKey(Host, editable=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'MySQL account'
		verbose_name_plural = 'MySQL'


class FTP(DatesModel):
	ftp_user = models.CharField('FTP username', max_length=16, unique=True)
	ftp_pass = models.CharField('FTP password', max_length=16)
	folder = DirectoryPathField('Folder', max_length=250, blank=True,
		path='/srv/projects/', default="")
	host = models.ForeignKey(Host, editable=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Ftp account'
		verbose_name_plural = 'FTP'


class DNS(DatesModel):
	domain = models.CharField('Name', max_length=50, unique=True)
	ip_address = models.IPAddressField('IP address', default=external_ip)
	host = models.ForeignKey(Host, editable=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Dns record'
		verbose_name_plural = 'DNS'
