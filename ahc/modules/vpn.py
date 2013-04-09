__author__ = 'gotlium'

from libraries.helpers import *


class Vpn(object):
    methods = ('add', 'delete',)

    def __init__(self, base):
        self.base = base

    def add(self, client):
        self.base.main.update({'client': client})
        system_by_code(
            'cd /etc/openvpn/easy-rsa && source ./vars && ./build-key %s' %
            client
        )

        info_message('Successful!')
        info_message('*' * 100, 'blue')
        info_message('Download following files:', 'bold')
        info_message('*' * 100, 'blue')
        info_message('/etc/openvpn/easy-rsa/keys/%s.crt' % client)
        info_message('/etc/openvpn/easy-rsa/keys/%s.key' % client)
        info_message('/etc/openvpn/easy-rsa/keys/ca.crt')
        info_message('*' * 100, 'blue')
        info_message('And use this config in your vpn-client:', 'bold')
        info_message('*' * 100, 'blue')
        info_message("""
client
remote %(external_ip)s
port 777
dev tun
proto tcp
ca ca.crt
cert %(client)s.crt
key %(client)s.key
script-security 2 system
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
verb 4
pull
comp-lzo
cipher DES-EDE3-CBC
        """ % self.base.main, 'white')
        info_message('*' * 100, 'blue')

    def delete(self, client):
        system_by_code(
            'cd /etc/openvpn/easy-rsa && source ./vars && '
            './revoke-full %s >& /dev/null' % client
        )
        info_message('Successful!')
