__author__ = 'gotlium'


from unittest import TestCase
import os
import shutil

from libraries.configs import Configs


# todo: access to one folder with different users
# todo: working with branches
class Git_jailTestCase(TestCase, Configs):

	domain = 'example.com'
	user = 'git-jail@example.com'

	def __loadPaths(self):
		self.project_dir = '%s/%s' % (self.main['projects_directory'], self.domain)
		self.templates_dir = '%s/www/templates' % self.project_dir
		self.repository = '%s/%s' % (self.git['jail_repositories'], self.user)
		self.user_project_dir = '%s/%s/' % (self.repository, self.domain)
		self.base_repository = '%s/%s.git' % (self.git['repositories'], self.domain)

	def setUp(self):
		self.loadConfigs()
		self.__loadPaths()

	def test_a_addProject(self):
		self.assertEqual(os.system('ahc -m apache -t php -a %s >& /dev/null' % self.domain), 0)
		self.assertTrue(os.path.exists(self.project_dir))
		self.assertEqual(os.mkdir(self.templates_dir), None)
		self.assertEqual(open('%s/date.html' % self.templates_dir, 'w').close(), None)


	def test_b_createRepo(self):
		git_repository = self.git['repositories']
		self.assertEqual(os.system('ahc -m git -a %s >& /dev/null' % self.domain), 0)
		self.assertTrue(os.path.exists('%s/www/.git' % self.project_dir))
		self.assertTrue(os.path.exists('%s/%s.git' % (git_repository, self.domain)))
		os.system('ssh-copy-id -i ~/.ssh/id_rsa root@127.0.0.1 1> /dev/null')
		self.assertEqual(os.system('cd %s/www && git add . && git commit -am "initial commit" >& /dev/null' % self.project_dir), 0)
		self.assertEqual(os.system('cd %s/www && git push origin master >& /dev/null' % self.project_dir), 0)

	def test_c_createSystemUser(self):
		self.assertEqual(os.system('useradd -m -U -r -s /bin/bash -d /home/git-jail git-jail >& /dev/null'), 0)
		self.assertEqual(os.system('id git-jail >& /dev/null'), 0)
		self.assertEqual(os.mkdir('/home/git-jail/.ssh/'), None)
		self.assertEqual(os.system('ssh-keygen -t rsa -f /home/git-jail/.ssh/id_rsa -P "" >& /dev/null'), 0)
		self.assertEqual(os.system('chown git-jail:git-jail -R /home/git-jail/ >& /dev/null'), 0)
		key = ''.join(open('/home/git-jail/.ssh/id_rsa.pub').readlines())
		self.assertTrue(len(key) > 0)
		self.assertEqual(os.system("ahc -m git_jail -a %s -p '%s' >& /dev/null" % (self.user, key)), 0)

	def test_d_grantAccess(self):
		self.assertEqual(os.system('ahc -m git_jail -i %s -e templates -u %s >& /dev/null' % (self.domain, self.user)), 0)
		path_to_check = [
			self.repository, self.user_project_dir,
			'%s/templates.git' % self.user_project_dir,
			'%s/.git' % self.templates_dir,
			"%s/templates.git/hooks/post-receive" % self.user_project_dir,
			"%s/templates.git/hooks/post-receive.db" % self.user_project_dir,
			"%s/hooks/post-receive" % self.base_repository,
			"%s/hooks/post-receive.db" % self.base_repository,
			"%s/www/.git/hooks/post-receive" % self.project_dir,
			"%s/www/.git/hooks/post-receive.db" % self.project_dir,
			"%s/www/.git/hooks/post-commit" % self.project_dir
		]
		key = hash('%s-%s-%s' % (self.user, self.domain, 'templates'))
		for path in path_to_check:
			self.assertTrue(os.path.exists(path))
			if path.endswith('.db'):
				text = '' . join(open(path).readlines())
				self.assertTrue(';%s;' % key in text)

	def test_e_cloneSubRepo(self):
		self.assertEqual(os.system("su git-jail -c 'ssh-keyscan -t rsa,dsa 127.0.0.1 2>&1 > ~/.ssh/known_hosts'"), 0)
		self.assertEqual(os.system("su git-jail -c 'cd /tmp && git clone git@127.0.0.1:%s/templates.git /tmp/templates' >& /dev/null" % self.domain), 0)
		self.assertTrue(os.path.exists('/tmp/templates/.git'))

	def test_f_cloneMainRepo(self):
		self.assertEqual(os.system("ssh-keyscan -t rsa,dsa 127.0.0.1 2>&1 > ~/.ssh/known_hosts"), 0)
		self.assertEqual(os.system("cd /tmp && git clone ssh://root@127.0.0.1/home/git/repositories/%s.git /tmp/main >& /dev/null" % self.domain), 0)

	def __checkCommit(self, filename):
		self.assertEqual(os.system('cd %s/www && git log --pretty="%%s" -1 --name-only | grep %s >& /dev/null' % (self.project_dir, filename)), 0)
		self.assertEqual(os.system('cd %s && git log --pretty="%%s" -1 --name-only | grep %s >& /dev/null' % (self.templates_dir, filename)), 0)

	def test_g_commitToSubRepo(self):
		self.assertEqual(os.system("su git-jail -c 'cd /tmp/templates/ && echo `date` > date1.html && git add date1.html && env -i GIT_COMMITTER_EMAIL='root@localhost' GIT_AUTHOR_EMAIL='root@localhost' GIT_AUTHOR_NAME='root' GIT_COMMITTER_NAME='root' git commit -am date1 >& /dev/null && git push origin master >& /dev/null'"), 0)
		self.__checkCommit('date1.html')
		self.assertEqual(os.system('cd %s && echo `date` > date2.html && git add date2.html && git commit -am date2 >& /dev/null && git push origin master >& /dev/null' % self.templates_dir), 0)
		self.__checkCommit('date2.html')

	def test_h_commitToRepo(self):
		self.assertEqual(os.system('cd %s/www && echo `date` > templates/date3.html && git add templates/date3.html && git commit -am date3 >& /dev/null && git push origin master >& /dev/null' % self.project_dir), 0)
		self.__checkCommit('date3.html')

	def test_i_removeUserRepo(self):
		self.assertEqual(os.system('ahc -m git_jail -i %s -f templates -u %s >& /dev/null' % (self.domain, self.user)), 0)
		self.assertFalse(os.path.exists('%s/templates.git' % self.user_project_dir))

	def test_j_removeUser(self):
		self.assertEqual(os.system('ahc -m git_jail -d %s >& /dev/null' % self.user), 0)
		self.assertFalse(os.path.exists(self.user_project_dir))

	def test_k_removeRepo(self):
		self.assertEqual(os.system('ahc -m git -d %s -y >& /dev/null' % self.domain), 0)
		self.assertFalse(os.path.exists('%s/%s.git' % (self.git['repositories'], self.domain)))

	def test_l_delProject(self):
		self.assertEqual(os.system('ahc -m apache -t php -d %s -y >& /dev/null' % self.domain), 0)
		self.assertFalse(os.path.exists(self.project_dir))

	def test_m_delUser(self):
		self.assertEqual(os.system('userdel -r git-jail'), 0)
		self.assertFalse(os.path.exists('/home/git-jail'))

	def test_n_cleanAll(self):
		self.assertEqual(shutil.rmtree('/tmp/templates/'), None)
		self.assertEqual(shutil.rmtree('/tmp/main/'), None)
