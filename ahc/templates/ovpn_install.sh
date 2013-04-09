#!/bin/bash

# Устанавливаем OpenVPN и IPtables
apt-get update && apt-get -y install openvpn iptables;

# Копируем папку easy-rsa в более удобное место /etc/openvpn
mkdir /etc/openvpn/easy-rsa;
cp -R /usr/share/doc/openvpn/examples/easy-rsa/2.0/* /etc/openvpn/easy-rsa/;
cd /etc/openvpn/easy-rsa;

# Даем файлу настроек openssl правильное имя
cp openssl-1.0.0.cnf openssl.cnf

# Инициализируем переменные
. ./vars

# Очищаем от старых сертификатов и ключей папку keys
./clean-all

# Создаем ключи и сертификаты для сервера. При желании можно изменить параметры
# генерации сертификатов и ключей отредактировав файл vars
./pkitool --initca 		# Создаем Certificate Authority для сервера
./pkitool --server server 	# Создаем сертификат X.509 для сервера
./build-dh			# Создаем ключ Диффи Хельман

# Копируем ключи и сертификаты сервера в /etc/openvpn
cp ./keys/ca.crt /etc/openvpn
cp ./keys/server.crt /etc/openvpn	 
cp ./keys/server.key /etc/openvpn
cp ./keys/dh1024.pem /etc/openvpn	

# Запускаем OpenVPN
service openvpn start

exit
