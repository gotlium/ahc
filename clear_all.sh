#!/bin/bash
#
# Copyright (C) 2012 GoTLiuM InSPiRiT <gotlium@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

clear

read -p "Are you sure? [y/n] " yn
case $yn in
[Yy]* )
	rm -rf /etc/apache2/sites-*/*
	rm -rf /etc/nginx/sites-*/*
	rm -rf /srv/projects/*
	rm -rf /root/repositories/*
	rm -rf /etc/rc*.d/*.init
	rm -rf /etc/init.d/*.init
	rm -rf /var/run/nginx/*
	rm -f /usr/sbin/sendmail

	read -s -p "Enter MySQL root password: " mysqlpasswd
	if [ -z "$mysqlpasswd" ]; then
		mysqlpasswd="password"
	fi
	mysql -p"$mysqlpasswd" -e 'DELETE FROM vsftpd.accounts;'
	echo

	killall -9 python >& /dev/null

	/etc/init.d/apache2 stop
	sleep 3
	/etc/init.d/apache2 start

	/etc/init.d/nginx stop
	sleep 3
	/etc/init.d/nginx start
	sleep 3

	find ./ \( -name '*.pyc' -or -name '*.pyo' \) -delete

	reset
;;
[Nn]* )
	exit
;;
* )
	echo "Please answer yes or no."
;;
esac
