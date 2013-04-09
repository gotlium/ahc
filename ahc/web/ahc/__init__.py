from subprocess import Popen, STDOUT, PIPE
import shutil
import os

from django.db.models import signals
from django.conf import settings

from ahc.web.ahc.models import *


def host_after_add(sender, instance, created, **kwargs):
    if created:
        cmd = 'ahc -m %s -t %s -a %s' % (
            instance.server, instance.server_type, instance.name
        )
        if instance.static:
            cmd += ' -o'
        if instance.ssl_certs:
            cmd += ' -x'
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
        cmd = 'ahc -m bind -a %s -i %s' % (
            instance.domain, instance.ip_address)
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


def ssl_after_add(sender, instance, created, **kwargs):
    if created:
        config = RawConfigParser()
        config.read('../configs.cfg')
        db_folder = config.get('apache_cert', 'cert_directory')
        domain = instance.host.name
        if not os.path.exists('%s/%s' % (db_folder, domain)):
            os.system('ahc -m install -s certs -i %s' % domain)
        try:
            cmd = 'ahc -m certs -a %s -i %s' % (instance.email, domain)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            data = p.communicate()[0].strip().split('\n')
            certificate = data[2].split(':')[1].strip().split('.p12')[
                              0] + '.p12'
            new_path = 'certs/%s' % os.path.basename(certificate)
            instance.password = data[1].split(':')[1].strip()
            instance.p12 = new_path
            instance.save()
            shutil.copy(certificate, '%s/%s' % (settings.MEDIA_ROOT, new_path))
            server = instance.host.server.replace('apache', 'apache2')
            os.system('/etc/init.d/%s restart' % server)
        except:
            instance.delete()


def git_user_after_add(sender, instance, created, **kwargs):
    if created:
        cmd = "ahc -m git_jail -a %s -p '%s'" % (
            instance.email, instance.ssh_key
        )
        os.system(cmd)


def git_jail_after_add(sender, instance, created, **kwargs):
    if created:
        cmd = "ahc -m git_jail -i %s -e %s -u %s" % (
            instance.host.name, instance.folder, instance.user.email
        )
        os.system(cmd)


def mysql_after_delete(sender, instance, **kwargs):
    cmd = 'ahc -m mysql -d %s -u %s -p %s -y' % (
        instance.db_name, instance.db_user, instance.db_pass
    )
    os.system(cmd)


def ssl_after_delete(sender, instance, **kwargs):
    cmd = 'ahc -m certs -d %s -i %s' % (instance.email, instance.host.name)
    if instance.p12:
        os.unlink('%s/%s' % (settings.MEDIA_ROOT, instance.p12))
    server = instance.host.server.replace('apache', 'apache2')
    os.system(cmd)
    os.system('/etc/init.d/%s restart' % server)


def git_user_after_delete(sender, instance, **kwargs):
    os.system("ahc -m git_jail -d %s" % instance.email)


def git_jail_after_delete(sender, instance, **kwargs):
    cmd = "ahc -m git_jail -i %s -f %s -u %s" % (
        instance.host.name, instance.folder, instance.user.email
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
signals.post_save.connect(
    ssl_after_add, SSL, dispatch_uid="ahc.__init__"
)
signals.post_save.connect(
    git_user_after_add, GitUser, dispatch_uid="ahc.__init__"
)
signals.post_save.connect(
    git_jail_after_add, JAIL, dispatch_uid="ahc.__init__"
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
signals.post_delete.connect(
    ssl_after_delete, SSL, dispatch_uid="ahc.__init__"
)
signals.post_delete.connect(
    git_user_after_delete, GitUser, dispatch_uid="ahc.__init__"
)
signals.post_delete.connect(
    git_jail_after_delete, JAIL, dispatch_uid="ahc.__init__"
)

signals.pre_save.connect(
    after_save_bool, Host, dispatch_uid="ahc.__init__"
)
