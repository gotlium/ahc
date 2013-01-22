__author__ = 'gotlium'

from os import getuid, system as osystem, access, W_OK, R_OK
from subprocess import Popen, STDOUT, PIPE
from sys import platform, maxsize, exit
from smtplib import SMTP
from ctypes import CDLL
from math import log
import hashlib
import base64
import struct
import xmpp
import sys
import re

from libraries.fs import getFileArr, getFile, fileExists, putFile

COLORS = {
	'black': "\033[0;30m",
	'red':"\033[0;31m",
	'green':"\033[0;32m",
	'lightgreen':"\033[1;32m",
	'yellow':"\033[0;33m",
	'yellows':"\033[1;33m",
	'blue':"\033[0;34m",
	'white':"\033[1;37m",
	'cyan':"\033[0;36m",
	'close':"\033[0m",
	'bold':"\033[1m",
	'italic':"\033[4m"
}

def error_message(msg):
	#print ("%s%s%s" % (COLORS['red'], msg, COLORS['close']))
	print >> sys.stderr, "%s%s%s" % (COLORS['red'], msg, COLORS['close'])
	exit(1)

def info_message(msg, color='green'):
	print ("%s%s%s" % (COLORS[color], msg, COLORS['close']))

def system(command, as_text=False):
	try:
		if not command: return None
		p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
		result = p.communicate()[0].strip()
		if not result:
			return None
		elif as_text:
			return result
		else:
			return result.split("\n")
	except Exception:
		return None

def isLinux():
	if platform.find('linux') != -1:
		return True
	return False

def isRoot():
	return getuid() == 0

def renameProcess(name, libc = None):
	try:
		if int(log(maxsize, 2)) == 63:
			libc = '/lib/x86_64-linux-gnu/libc.so.6'
			if not fileExists(libc):
				libc = '/lib64/libc.so.6'
				if not fileExists(libc):
					libc = '/lib/libc.so.6'
		else:
			libc = '/lib/i386-linux-gnu/libc.so.6'
			if not fileExists(libc):
				libc = '/lib32/libc.so.6'
				if not fileExists(libc):
					libc = '/lib/libc.so.6'
		if libc:
			CDLL(libc).prctl(15, name, 0, 0, 0)
			return True
	except Exception, msg:
		pass
	return False

def hosts(action='add', host=None, filename='/etc/hosts'):
	if host and fileExists(filename):
		new_data = ''
		for line in getFileArr(filename):
			gh = lambda e: line.split(e)[-1:][0].strip()
			if line and host not in(gh('\t'), gh('www.')):
				new_data += '%s\n' % line.strip()
		if action == 'add':
			new_data += '127.0.0.1\t%s\n' % host
			new_data += '127.0.0.1\twww.%s\n' % host
		if putFile(filename, new_data):
			return True
	return False

def isValidHostname(hostname):
	if len(hostname) > 255:
		return False
	if len(hostname.split('.')) > 3:
		return False
	if hostname[-1:] == ".":
		hostname = hostname[:-1]
	allowed = re.compile("(?!-)[A-Z_\d-]{1,63}(?<!-)$", re.IGNORECASE)
	return all(allowed.match(x) for x in hostname.split("."))

def isValidMail(email):
	email_re = re.compile(
		r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
		r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
		r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
	return True if email_re.match(email) else False

def isValidSshPublicKey(openssh_pubkey):
	type, key_string, comment = openssh_pubkey.split()
	data = base64.decodestring(key_string)
	int_len = 4
	str_len = struct.unpack('>I', data[:int_len])[0]
	return data[int_len:int_len+str_len] == type

def system_by_code(cmd):
	execution_code = osystem(cmd)
	if execution_code is not 0:
		error_message('Execution error! Command: %s' % cmd)

def isHost(host_name):
	if not isValidHostname(host_name):
		error_message('Domain name not valid!')

def isEmail(email):
	if not isValidMail(email):
		error_message('Email address is not a valid!')

def isPublicKey(pub_key):
	try:
		if not isValidSshPublicKey(pub_key):
			error_message('Public keys is not a valid!')
	except:
		error_message('Public keys is not a valid!')

def getTemplate(template, ext='conf'):
	return getFile('templates/%s.%s' % (template, ext))

def isValidIp(ip):
	segments = ip.split('.')
	if len(segments) != 4: return False
	for segment in segments:
		if not segment.isdigit() or int(segment) > 255 or len(segment) > 3:
			return False
	return True

def service_restart(service, action='restart'):
	system_by_code(
		'%s %s >& /dev/null' % (service, action)
	)

def backFile(filename):
	bak_file = filename + '.bak'
	if not fileExists(bak_file):
		system_by_code('cp %s{,.bak}' % filename)

def checkInstall(config, custom_rules=None):
	default_rules = {
		config['bin']: 'Service not installed!',
		config['init']: 'Init file not found!',
		config['config']: 'Config file not found!'
	}
	if custom_rules:
		default_rules.update(custom_rules)
	for key in default_rules.keys():
		if not fileExists(key):
			error_message(default_rules[key])

def is_writable(filename):
	return access(filename, W_OK)

def is_readable(filename):
	return access(filename, R_OK)

from ConfigParser import RawConfigParser

def configs(section):
	config = RawConfigParser()
	config.read('configs.cfg')
	items = {}
	for item in config.items(section):
		items[item[0]] = item[1]
	return items

def xmppMessage(message):
	config = configs('xmpp')
	if int(config['enabled']) > 0:
		jid  = xmpp.protocol.JID(config['user'])
		jabber = xmpp.Client(jid.getDomain(), debug=[])
		jabber.connect(('talk.google.com', 5222))
		jabber.auth(jid.getNode(), config['pass'], config['resource'])
		jabber.sendInitPresence(requestRoster=1)
		for email in config['mail_to'].split(','):
			try:
				jabber.send(xmpp.Message(email, message))
			except:
				pass

def sendmail(subject, message):
	config = configs('smtp')
	if not int(config['enabled']):
		return
	emails = config['mail_to'].split(',')
	message = "From: %s\r\n" % config['from_addr']\
			  + "To: %s\r\n" % emails[0]\
			  + "CC: %s\r\n" % ",".join(emails)\
			  + "Subject: %s\r\n" % subject\
			  + "\r\n"\
			  + message
	mail = SMTP(config['host'], config['port'])
	if config['user']:
		mail.ehlo()
		mail.starttls()
		mail.ehlo()
		mail.login(config['user'], config['pass'])
	mail.sendmail(config['from_addr'], emails, message)
	mail.quit()

def xmppAndMail(subject, message):
	sendmail(subject, message)
	xmppMessage(message)

def md5(email):
	m = hashlib.md5()
	m.update(email)
	return m.hexdigest()

