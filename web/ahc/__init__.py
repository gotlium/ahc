from django.db.models import signals
import os

from models import *

def host_after_add(sender, instance, created, **kwargs):
	if created:
		cmd = 'ahc -m %s -t %s -a %s' % (
			instance.server, instance.server_type, instance.name
		)
		if instance.static:
			cmd += ' -o'
		if instance.username and instance.password:
			cmd += ' -b %s:%s' % (instance.username, instance.password)
		os.system(cmd)

		if instance.git:
			os.system('ahc -m git -a %s' % instance.name)

def host_after_delete(sender, instance, **kwargs):
	cmd = 'ahc -m %s -t %s -d %s -y' % (
		instance.server, instance.server_type, instance.name
	)
	os.system(cmd)


def dns_after_add(sender, instance, created, **kwargs):
	if created:
		cmd = 'ahc -m bind -a %s -i %s' % (instance.domain, instance.ip_address)
		os.system(cmd)

def dns_after_delete(sender, instance, **kwargs):
	cmd = 'ahc -m bind -d %s -i %s' % (instance.domain, instance.ip_address)
	os.system(cmd)


def ftp_after_add(sender, instance, created, **kwargs):
	if created:
		cmd = 'ahc -m ftp -a %s -u %s -p %s' % (
			instance.host.name, instance.ftp_user, instance.ftp_pass
		)
		if instance.folder:
			cmd += ' -f %s' % instance.folder
		os.system(cmd)

def ftp_after_delete(sender, instance, **kwargs):
	cmd = 'ahc -m ftp -d %s -u %s -p %s' % (
		instance.host.name, instance.ftp_user, instance.ftp_pass
	)
	if instance.folder:
		cmd += ' -f %s' % instance.folder
	os.system(cmd)


def mysql_after_add(sender, instance, created, **kwargs):
	if created:
		cmd = 'ahc -m mysql -a %s -u %s -p %s' % (
		instance.db_name, instance.db_user, instance.db_pass
		)
		os.system(cmd)

def mysql_after_delete(sender, instance, **kwargs):
	cmd = 'ahc -m mysql -d %s -u %s -p %s -y' % (
		instance.db_name, instance.db_user, instance.db_pass
	)
	os.system(cmd)


def git_after_save(instance, current):
	if current.git != instance.git:
		if not instance.git:
			os.system('ahc -m git -d %s' % instance.name)
		else:
			os.system('ahc -m git -a %s' % instance.name)

def host_after_save(instance, current):
	if current.status != instance.status:
		if not instance.status:
			cmd = 'ahc -m %s -t %s -f %s -y' % (
				instance.server, instance.server_type, instance.name
			)
		else:
			cmd = 'ahc -m %s -t %s -e %s -y' % (
				instance.server, instance.server_type, instance.name
			)
		os.system(cmd)

def after_save_bool(sender, instance, *args, **kwargs):
	if instance.pk:
		current = Host.objects.get(pk=instance.pk)
		git_after_save(instance, current)
		host_after_save(instance, current)


signals.post_save.connect(
	host_after_add, Host, dispatch_uid="ahc.__init__"
)
signals.post_save.connect(
	dns_after_add, DNS, dispatch_uid="ahc.__init__"
)
signals.post_save.connect(
	ftp_after_add, FTP, dispatch_uid="ahc.__init__"
)
signals.post_save.connect(
	mysql_after_add, MySQL, dispatch_uid="ahc.__init__"
)

signals.post_delete.connect(
	host_after_delete, Host, dispatch_uid="ahc.__init__"
)
signals.post_delete.connect(
	mysql_after_delete, MySQL, dispatch_uid="ahc.__init__"
)
signals.pre_delete.connect(
	ftp_after_delete, FTP, dispatch_uid="ahc.__init__"
)
signals.post_delete.connect(
	dns_after_delete, DNS, dispatch_uid="ahc.__init__"
)

signals.pre_save.connect(
	after_save_bool, Host, dispatch_uid="ahc.__init__"
)
