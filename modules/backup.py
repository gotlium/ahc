__author__ = 'gotlium'


from datetime import datetime
import traceback
import paramiko
import atexit
import signal
import ftplib
import MySQLdb
import re
import os

from libraries.helpers import *


class FTP(object):

	def __init__(self, config):
		self.ftp = ftplib.FTP(config['remote_hostname'])
		self.ftp.login(config['remote_username'], config['remote_password'])
		self.config = config

	def __rmtree(self, directory):
		self.config['directory'] = directory
		cmd = "lftp -e 'rm -r %(directory)s; bye;' -u "\
			  "%(remote_username)s,%(remote_password)s "\
			  "%(remote_protocol)s://%(remote_hostname)s 1> /dev/null" % \
			  self.config
		system_by_code(cmd)

	def get_list(self, directory):
		files = []
		for filename in self.ftp.nlst(directory if directory else '.'):
			files.append(os.path.join(directory, filename))
		return files

	def remove_directories(self, files):
		for f in files:
			try:
				self.ftp.delete(f)
			except:
				self.__rmtree(f)

	def __del__(self):
		self.ftp.close()


class SFTP(object):

	def __init__(self, config):
		self.transport = paramiko.Transport((config['remote_hostname'], 22))
		self.transport.connect(
			username=config['remote_username'],
			password=config['remote_password']
		)
		self.sftp = paramiko.SFTPClient.from_transport(self.transport)
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(
			config['remote_hostname'],
			username=config['remote_username'],
			password=config['remote_password']
		)
		self.config = config

	def __execute_cmd_and_get_stdout(self, cmd):
		stdin, stdout, stderr = self.ssh.exec_command(cmd)
		results = stdout.readlines()
		if len(results)==1:
			results=results[0].strip()
		stdin.close(); stdout.close(); stderr.close()
		return results

	def __rmtree(self, path):
		cmd = 'python -c "import shutil; shutil.rmtree(\'%s\')"' % path
		return self.__execute_cmd_and_get_stdout(cmd)

	def get_list(self, directory):
		files = []
		try:
			for filename in self.sftp.listdir(directory):
				files.append(os.path.join(directory, filename))
		except:
			pass
		return files

	def remove_directories(self, files):
		for f in files:
			try:
				self.sftp.remove(f)
			except:
				self.__rmtree(f)

	def __del__(self):
		self.sftp.close()
		self.transport.close()
		self.ssh.close()


class LOCAL(object):

	def __init__(self, config):
		self.config = config

	def get_list(self, directory):
		if fileExists(directory):
			files = system('ls -1 %s' % directory)
			return ['%s/%s' % (directory, f) for f in files]
		return []

	def remove_directories(self, files):
		for f in files:
			if fileExists(f):
				system_by_code('rm -rf %s' % f)


class LockFile(object):

	def _in_progress(self):
		return fileExists(self.lock_file)

	def _lock(self):
		putFile(self.lock_file, 'backup in progress ...')

	def _unlock(self):
		if fileExists(self.lock_file):
			delFile(self.lock_file)


class Backup(LockFile):

	methods = ('auth',)
	base = None

	def __init__(self, base):
		self.base = base
		self.backup = self.base.backup
		self.date = str(datetime.now().strftime('%d-%m-%y'))
		self.lock_file = '/var/run/ahc-backup.lock'

	def __get_file_list(self, directory):
		self.files = self.connect.get_list(directory)

	def __get_expired(self):
		self.expired = []
		for f in self.files:
			try:
				createtime = datetime.strptime(os.path.basename(f), '%d-%m-%y')
				now = datetime.now()
				delta = now - createtime
				if delta.days >= int(self.backup['remote_expire_days']):
					self.expired.append(f)
			except:
				pass

	def __remove_directories(self):
		if len(self.expired):
			self.connect.remove_directories(self.expired)

	def __build_cmd(self, config, is_directory=False):
		config['exclude'] = ""
		if config['directories_exclude']:
			exclude = config['directories_exclude'].split(',')
			exclude = "--exclude '" + "' --exclude '".join(exclude) + "'"
			config['exclude'] = exclude

		if self.backup['remote_protocol'] in ('ftp', 'sftp'):
			if is_directory:
				ftp_cmd = 'mirror -R %(exclude)s %(local)s %(remote)s; bye;'
			else:
				config['local'] = os.path.basename(config['local'])
				ftp_cmd = 'mput -d ./%(local)s -O %(remote)s; bye;'

			cmd = "cd /tmp && lftp -e '"+ftp_cmd+"' -u "\
				  "%(remote_username)s,%(remote_password)s "\
				  "%(remote_protocol)s://%(remote_hostname)s 1> /dev/null"
			return str(cmd % config)
		else:
			if is_directory:
				config['local'] = '%s/' % config['local']
			config['directory'] = os.path.dirname(config['remote'])
			return str(
				'mkdir -p %(directory)s && rsync -au %(exclude)s %(local)s '
				'%(remote)s 1> /dev/null' % config
			)

	def __sync_directory(self, local):
		name = local.replace('/','_')
		name = re.sub('([^a-z0-9_.])+', '', name)
		remote = '%s/web/%s/%s' % (
			self.backup['remote_directory'], self.date, name
		)
		self.backup['remote'] = remote
		self.backup['local'] = local
		system_by_code(self.__build_cmd(self.backup, True))

	def __sync_db_file(self, local):
		self.backup['remote'] = '%s/db/%s/' % (
			self.backup['remote_directory'], self.date
		)
		self.backup['local'] = local
		system_by_code(self.__build_cmd(self.backup))
		if fileExists(local):
			delFile(local)

	def __dump(self, database):
		self.base.mysql['database'] = database
		cmd = "mysqldump -h %(host)s -u %(user)s -p'%(password)s' " \
			  "--no-create-info=FALSE --order-by-primary=FALSE --force=FALSE" \
			  " --no-data=FALSE --tz-utc=TRUE --flush-privileges=FALSE " \
			  "--compress=TRUE --replace=FALSE --insert-ignore=FALSE " \
			  "--extended-insert=TRUE --quote-names=TRUE --hex-blob=FALSE " \
			  "--complete-insert=FALSE --add-locks=TRUE --disable-keys=TRUE " \
			  "--delayed-insert=FALSE --create-options=TRUE " \
			  "--delete-master-logs=FALSE --comments=TRUE " \
			  "--default-character-set=utf8 --max_allowed_packet=1G " \
			  "--flush-logs=FALSE --dump-date=TRUE --lock-tables=TRUE " \
			  "--allow-keywords=FALSE --events=FALSE --databases --routines "\
			  "%(database)s | gzip -c > /tmp/%(database)s.sql.gz"
		system_by_code(str(cmd) % dict(self.base.mysql))
		return '/tmp/%s.sql.gz' % database

	def __clean_directory(self, directory):
		protocol = self.backup['remote_protocol'].upper()
		self.connect = globals()[protocol](self.backup)
		self.__get_file_list('%s/%s' % (
			self.backup['remote_directory'], directory
		))
		self.__get_expired()
		self.__remove_directories()
		del self.connect

	def _clean(self):
		self.__clean_directory('web')
		self.__clean_directory('db')

	def _check(self):

		if not self.backup['remote_expire_days']:
			error_message('Remote expire days in config file not configured.')
		elif not self.backup['databases'] and not self.backup['directories']:
			error_message('Backup settings is not configured.')
		elif self.backup['remote_protocol'] == 'local':
			if not self.backup['remote_directory']:
				error_message('Directory not set in settings file.')
		elif not self.backup['remote_username'] or not \
				self.backup['remote_password']:
			error_message('Setup your backup settings.')
		elif self.backup['remote_protocol'] not in \
			 	('ftp', 'sftp', 'rsync', 'local'):
			error_message('remote_protocol can be ftp or sftp.')

	def __get_all_databases(self):
		self.db = MySQLdb.connect(
			self.base.mysql['host'], self.base.mysql['user'],
			self.base.mysql['password']
		)
		self.cursor = self.db.cursor()
		self.cursor.execute("SHOW DATABASES;")
		databases = []
		for row in self.cursor.fetchall():
			databases.append(row[0])
		return databases

	def __get_all_webites(self):
		directories = os.listdir(self.base.main['projects_directory'])
		join = os.path.join
		return [
			join(self.base.main['projects_directory'],f) for f in directories
		]

	def _backup_db(self):
		if not self.backup['databases']:
			return
		elif self.backup['databases'] == 'all':
			databases = self.__get_all_databases()
		else:
			databases = self.backup['databases'].split(',')
		for db in databases:
			self.__sync_db_file(self.__dump(db.strip()))

	def _backup_website(self):
		if not self.backup['directories']:
			return
		elif self.backup['databases'] == 'all':
			directories = self.__get_all_webites()
		else:
			directories = self.backup['directories'].split(',')
		for directory in directories:
			self.__sync_directory(directory.strip())

	def _signals_handler(self, signum, frame):
		self._unlock()
		sendmail('Backup handler', 'Process was killed!')
		os._exit(1)

	def _setup_handlers(self):
		signal.signal(signal.SIGTERM, self._signals_handler)
		atexit.register(self._unlock)

	def auth(self, action):
		try:
			if self._in_progress():
				error_message('Already runned!')
				return False
			self._check()
			self._lock()
			self._setup_handlers()
			self._clean()
			if action == 'mysql':
				self._backup_db()
			elif action == 'site':
				self._backup_website()
			else:
				error_msg = 'Error usage! Use params: [mysql|site]'
			self._unlock()
			if 'error_msg' in locals():
				error_message(error_msg)
		except Exception,ex:
			self._unlock()
			message = ex.__str__() + "\r\n" + traceback.format_exc()
			xmppAndMail('Backup errors.', message)
			error_message(message)
