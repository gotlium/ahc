#from preferences.models import Preferences
from ConfigParser import RawConfigParser
from django.db import models
from ahc.validators import validate_ssh_key

from ahc.fields import DirectoryPathField


TYPES = (
    ('django', 'django',),
    ('python', 'python',),
    ('php', 'php',),
    ('ruby', 'ruby'),
    ('ror', 'ror'),
)

SERVERS = (
    ('apache', 'apache',),
    ('nginx', 'nginx',),
)

MODS = (
    ('default', 'default'),
    ('wsgi', 'wsgi'),
)

config = RawConfigParser()
config.read('../configs.cfg')
external_ip = config.get('main', 'external_ip')
if external_ip == '192.168.0.1':
    external_ip = ""


class DatesModel(models.Model):
    created = models.DateTimeField('Created', auto_now=False,
                                   auto_now_add=True, editable=False)
    updated = models.DateTimeField('Updated', auto_now=True,
                                   auto_now_add=True, editable=False)

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
    ssl_certs = models.BooleanField('Client-side SSL', default=False)
    username = models.CharField('Login', blank=True, null=True, max_length=16)
    password = models.CharField('Password', blank=True, null=True,
                                max_length=16)
    status = models.BooleanField('availability status', default=True,
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


class SSL(DatesModel):
    email = models.EmailField('Email', unique=True)
    password = models.CharField('Client password', blank=True, null=True,
                                max_length=6)
    p12 = models.FileField('Client certificate', upload_to='certs',
                           blank=True, null=True)
    host = models.ForeignKey(Host, editable=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Client-side SSL'
        verbose_name_plural = 'Client-side SSL'


class GitUser(DatesModel):
    email = models.EmailField('Email', unique=True)
    ssh_key = models.TextField('SSH Public Key', validators=[validate_ssh_key])

    class Meta:
        ordering = ['-id']
        verbose_name = 'Git Jail User'
        verbose_name_plural = 'Git Jail Users'

    def __unicode__(self):
        return self.email


class JAIL(DatesModel):
    host = models.ForeignKey(Host, editable=False)
    user = models.ForeignKey(GitUser, verbose_name='Git Jail user')
    folder = models.CharField('Folder', max_length=250)

    def __unicode__(self):
        return '%s - %s - %s' % (self.host, self.user, self.folder)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Git-Jail User'
        verbose_name_plural = 'Git Jail'


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
