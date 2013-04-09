#!/bin/bash

REPOMAIL="root@localhost"
MAILTO="root@localhost"

# Getting all sources list & upgrading system packages
apt-get update && apt-get upgrade -y && apt-get autoremove -y

if [ ! -f "/root/.ssh/id_rsa.pub" ]; then
    # Ssh key generator
    echo
    ssh-keygen -t rsa -f ~/.ssh/id_rsa -P "" -C $REPOMAIL -y
    echo
    echo 'Are you copied key?' && read && echo 'OK'
    echo
fi

# Basic packages
echo 'Installing basic packages ...'

declare -A PACKAGES
PACKAGES=(
    [apache]="apache2 apache2-mpm-prefork libapache2-mod-rpaf apache2-utils"
    [apache-security]="libapache-mod-security libapache2-mod-evasive"
    [nginx]="nginx nginx-common nginx-full"
    [mysql]="mysql-server mysql-client libmysqlclient-dev"
    [python]="libapache2-mod-python libapache2-mod-wsgi python-dev python python-mysqldb python-django python-redis python-imaging uwsgi-plugin-python python-virtualenv ipython uwsgi libxml2-dev libxslt-dev"
    [php5]="libapache2-mod-php5 php5-dev php5 php5-cli php5-common php5-suhosin php-pear php5-mhash php5-ming php5-pspell php5-recode php5-snmp php5-tidy php5-xmlrpc php5-xsl php5-imap php5-mysql php5-curl php5-sqlite php5-mcrypt php5-imagick php5-gd phpmyadmin php5-xdebug php5-memcached php5-memcache php-apc php5-fpm"
    [ruby]="libapache2-mod-ruby libapache2-mod-passenger ruby rails build-essential ruby1.8-dev rubygems libfcgi-dev nodejs libsqlite3-dev libmysql-ruby rubygems"
    [ftp]="vsftpd libpam-mysql ftp libpam-ldap lftp"
    [caches]="redis-server memcached"
    [compilators]="gcc g++ make pkg-config devscripts shtool"
    [cvs]="git-core subversion mercurial"
    [archivators]="zip unzip unrar-free p7zip-full"
    [protection]="iptables xtables-addons-common fail2ban"
    [utils]="tcpdump bash-completion mc ssl-cert links wget rsync nano locate screen ssh rlwrap encfs sqlite3 tree curl"
    [sphinx]="sphinxsearch"
    [dns]="bind9 dnsutils"
    [mail]="exim4-config"
    [ssh-server]="openssh-server openssh-client"
)

CONTAINER=""

read -p "> Install all LAMP packages? You can choice 'n', if you want to select packages. [y/n] " yn

case $yn in
[Yy]* )
    for service in "${!PACKAGES[@]}"; do
        CONTAINER="$CONTAINER ${PACKAGES[$service]}"
    done
;;
* )
    if [ "${#PACKAGES[*]}" -ne 0 ]; then
        for service in "${!PACKAGES[@]}"; do
            read -p ">> Install \"$service\" packages? [y/n] " yn
            case $yn in
             [Yy]* )
                CONTAINER="$CONTAINER ${PACKAGES[$service]}"
            ;;
            esac
        done
    fi
;;
esac

apt-get install -y $CONTAINER --force-yes

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

read -p "> Reconfigure exim4-config? [y/n] " yn
case $yn in
[Yy]* )
    dpkg-reconfigure exim4-config
;;
esac

read -p "> Install .bashrc or .zhsrc? [y/n] " yn
case $yn in
[Yy]* )
    ahc -m install -s shell
;;
esac

# Git protection
if [ -z "`cat /etc/apache2/apache2.conf|grep '.git'`" ]; then
    echo "Options -Indexes" >> /etc/apache2/apache2.conf
    echo '<Directory ~ "\.git">' >> /etc/apache2/apache2.conf
    echo '        Order allow,deny' >> /etc/apache2/apache2.conf
    echo '        Deny from all' >> /etc/apache2/apache2.conf
    echo '</Directory>' >> /etc/apache2/apache2.conf
fi

if [ -z "`cat /etc/sysctl.conf|grep 'net.ipv6.conf.all.disable_ipv6'`" ]; then
    echo 'net.ipv6.conf.all.disable_ipv6 = 1' >> /etc/sysctl.conf
    echo 'net.ipv6.conf.default.disable_ipv6 = 1' >> /etc/sysctl.conf
    echo 'net.ipv6.conf.lo.disable_ipv6 = 1' >> /etc/sysctl.conf
fi

sysctl -p >& /dev/null

if [ -z "`dpkg -l vsftpd | grep 2.3.2`" ]; then
    echo "VSFTP will be re-install."
    apt-get purge vsftpd -y
    #http://security.ubuntu.com/ubuntu/pool/main/v/vsftpd/vsftpd_2.3.2-3ubuntu4.1_i386.deb
    wget http://security.ubuntu.com/ubuntu/pool/main/v/vsftpd/vsftpd_2.3.2-3ubuntu4.1_amd64.deb -O /tmp/vsftpd.deb
    dpkg -i /tmp/vsftpd.deb
    echo "vsftpd hold" | dpkg --set-selections
fi

if [ ! -f "/var/lib/locales/supported.d/en" ] || [ -z "`cat /var/lib/locales/supported.d/en|grep en_US.UTF-8`" ]; then
    echo "en_US.UTF-8 UTF-8" >> /var/lib/locales/supported.d/en
fi

if [ -z "$LANG" ]; then
    locale-gen en_US.UTF-8 >& /dev/null
    echo "LANG=en_US.UTF-8" >> /etc/environment
    echo "LC_ALL=en_US.UTF-8" >> /etc/environment
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
fi

CONFIGS_LIST="apache2_ssl nginx_ssl ftp bind mysql firewall nginx_proxy certs sendmail mail jira confluence web"

read -p "> Do you want to install ahc services configuration? [y/n] " yn
case $yn in
[Yy]* )
    for conf in $CONFIGS_LIST; do
        read -p ">> Install \"$conf\"? [y/n] " yn
        case $yn in
         [Yy]* )
            ahc -m install -s $conf
        ;;
        esac

    done
;;
esac

exit 0
