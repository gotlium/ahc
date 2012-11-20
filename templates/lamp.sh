#!/bin/bash

REPOMAIL="root@localhost"
MAILTO="root@localhost"

# Getting all sources list & upgrading system packages
apt-get update && apt-get upgrade -y

# Ssh key generator
echo
ssh-keygen -t rsa -C $REPOMAIL
cat /root/.ssh/id_rsa.pub
echo 'Are you copied key?' && read && echo 'OK'
echo

# Basic packages
echo 'Installing basic packages ...'
apt-get install -y apache2 apache2-mpm-prefork apache2-utils libapache2-mod-python \
libapache2-mod-php5 php5 php5-cli php5-common php-pear php5-mhash php5-ming \
php5-pspell php5-recode php5-snmp php5-tidy php5-xmlrpc php5-xsl php5-imap \
php5-mysql php5-curl php5-sqlite php5-mcrypt php5-imagick php5-gd phpmyadmin \
ssl-cert python python-mysqldb vsftpd libpam-mysql links php5-dev memcached \
zip php5-memcache php5-xdebug php5-memcached php5-memcache php-apc git-core mc nginx \
ssh gcc g++ make tcpdump bash-completion ftp vpnc pkg-config devscripts \
unrar-free p7zip-full fail2ban subversion sqlite3 wget rsync nano zip unzip \
iptables xtables-addons-common shtool memcached locate mysql-server mysql-client \
exim4-config sphinxsearch redis-server python-django php5-fpm libpam-ldap \
libapache2-mod-ruby libapache2-mod-passenger encfs screen python-redis python-imaging \
python-dev libxml2-dev libxslt-dev libapache2-mod-wsgi libapache2-mod-rpaf \
uwsgi uwsgi-plugin-python python-virtualenv bind9 lftp

echo 'packages installed.'
sleep 3
echo

# Deleting nginx default config & remove nginx from autostart directories
rm -f rm /etc/nginx/sites-enabled/default && update-rc.d -f nginx remove
/etc/init.d/nginx stop >& /dev/null

# Fail2ban configs
cat /etc/fail2ban/jail.conf | replace 'action = %(action_)s' 'action = %(action_mw)s' | \
    replace 'destemail = root@localhost' "destemail = $MAILTO" > /tmp/jail.conf && \
    mv /tmp/jail.conf /etc/fail2ban/jail.conf && /etc/init.d/fail2ban restart

# Log cheker config
cat /etc/logcheck/logcheck.conf | \
    replace 'SENDMAILTO="logcheck"' "SENDMAILTO=\"$MAILTO\""  > /tmp/logcheck.conf && \
    mv /tmp/logcheck.conf /etc/logcheck/logcheck.conf

# Apache restarting
a2enmod ssl rewrite setenvif php5 headers env expires deflate >& /dev/null
/etc/init.d/apache2 restart >& /dev/null
ufw disable >& /dev/null

# Bash
/etc/init.d/sysstat restart >& /dev/null

# Reconfiguring exim
# dpkg-reconfigure exim4-config

# Git protection
echo "Options -Indexes" >> /etc/apache2/apache2.conf
echo '<Directory ~ "\.git">' >> /etc/apache2/apache2.conf
echo '        Order allow,deny' >> /etc/apache2/apache2.conf
echo '        Deny from all' >> /etc/apache2/apache2.conf
echo '</Directory>' >> /etc/apache2/apache2.conf

echo 'net.ipv6.conf.all.disable_ipv6 = 1' >> /etc/sysctl.conf
echo 'net.ipv6.conf.default.disable_ipv6 = 1' >> /etc/sysctl.conf
echo 'net.ipv6.conf.lo.disable_ipv6 = 1' >> /etc/sysctl.conf

sysctl -p >& /dev/null

#http://security.ubuntu.com/ubuntu/pool/main/v/vsftpd/vsftpd_2.3.2-3ubuntu4.1_i386.deb
#http://security.ubuntu.com/ubuntu/pool/main/v/vsftpd/vsftpd_2.3.2-3ubuntu4.1_amd64.deb
