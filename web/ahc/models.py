#from preferences.models import Preferences
from ConfigParser import RawConfigParser
from django.db import models

from fields import DirectoryPathField


TYPES = (
	('django','django',),
	('python','python',),
	('php','php',),
	('ruby','ruby'),
	('ror','ror'),
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
	username = models.CharField('Login', blank=True, null=True, max_length=16)
	password = models.CharField('Password', blank=True, null=True, max_length=16)
	status = models.BooleanField('availability status', default = True,
		db_index=True)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Host'
		verbose_name_plural = 'Hosts'

	def __unicode__(self):
		return self.name


class MySQL(DatesModel):
	db_name = models.CharField('DB name', max_length=16, unique=True)
	db_user = models.CharField('Username', max_length=16)
	db_pass = models.CharField('Password', max_length=16)
	host = models.ForeignKey(Host, editable=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'MySQL account'
		verbose_name_plural = 'MySQL'


class FTP(DatesModel):
	ftp_user = models.CharField('Username', max_length=16, unique=True)
	ftp_pass = models.CharField('Password', max_length=16)
	folder = DirectoryPathField('Folder', max_length=250, blank=True,
		path='/srv/projects/', default="")
	host = models.ForeignKey(Host, editable=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Ftp account'
		verbose_name_plural = 'FTP'


class DNS(DatesModel):
	domain = models.CharField('Domain', max_length=50, unique=True)
	ip_address = models.IPAddressField('IP-address', default=external_ip)
	host = models.ForeignKey(Host, editable=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Dns record'
		verbose_name_plural = 'DNS'

'''
class AhcPreferences(Preferences):
	__module__ = 'preferences.models'

	#apache2_ssl = models.BooleanField('Apache SSL', default=False)
	#nginx_ssl = models.BooleanField('Nginx SSL', default=False)
	ftp = models.BooleanField('FTP', default=False)
	bind = models.BooleanField('Bind', default=False)
	#mysql = models.BooleanField('MySQL', default=False)
	firewall = models.BooleanField('Firewall', default=False)
	#nginx_proxy = models.BooleanField('Nginx as proxy', default=False)
	sendmail = models.BooleanField('Sendmail stub', default=False)
	#mail = models.BooleanField('Webmail', default=False)
	shell = models.BooleanField('Shell', default=False)
	#jira = models.BooleanField('Jira', default=False)
	#confluence = models.BooleanField('Confluence', default=False)

	class Meta:
		ordering = ['-id']
		verbose_name = 'Preferences'
		verbose_name_plural = 'Preferences'
'''