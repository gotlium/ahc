rm -rf /etc/apache2/sites-*/*
rm -rf /etc/nginx/sites-*/*
rm -rf /srv/projects/*
rm -rf /root/repositories/
rm -rf /etc/rc*.d/*.init
rm -rf /etc/init.d/*.init
rm -rf /var/run/nginx/*
rm -f /usr/sbin/sendmail

mysql -p'password' -e 'DELETE FROM vsftpd.accounts;'

killall -9 python

/etc/init.d/apache2 stop
sleep 3
/etc/init.d/apache2 start

/etc/init.d/nginx stop
sleep 3
/etc/init.d/nginx start
sleep 3
reset
