__author__ = 'gotlium'

from helpers import *

class HostPath(object):

	def getHostData(self, host_name):
		host_name = host_name.strip()
		host_name_split = host_name.split('.')
		projects_dir = self.base.main['projects_directory']
		website_folder = self.base.main['website_folder']

		if len(host_name_split) == 2:
			domain_dir = '%s/%s' % (projects_dir, host_name)
			website_dir = "%s/%s" % (domain_dir, website_folder)
			is_subdomain = False
		elif len(host_name_split) == 3:
			base_host = '.' . join(host_name_split[1:])
			domain_dir = '%s/%s/%s' % (projects_dir, base_host, host_name_split[0])
			website_dir = "%s/%s" % (domain_dir, website_folder)
			is_subdomain = True
		else:
			error_message('Host name is not valid!')
		return {
			'domain_dir': domain_dir,
			'website_dir': website_dir,
			'is_subdomain': is_subdomain
		}

	def getHostFiles(self, host_name, host_type, service='apache2'):
		if service not in ('nginx', 'apache2'):
			error_message('Service do not exists!')
		sites_available_dir = self.config['sites_available']
		sites_enabled_dir = self.config['sites_enabled']
		base_name = '%s-%s' % (host_type, host_name)
		ssl_base_name = '%s-%s.ssl' % (host_type, host_name)
		host_file = '%s/%s' % (sites_available_dir, base_name)
		ssl_host_file = '%s/%s' % (sites_available_dir, ssl_base_name)
		enable_host_file = '%s/%s' % (sites_enabled_dir, base_name)
		enable_ssl_host_file = '%s/%s' % (sites_enabled_dir, ssl_base_name)
		return {
			'base_name': base_name,
			'ssl_base_name': ssl_base_name,
			'host_file': host_file,
			'ssl_host_file': ssl_host_file,
			'enable_host_file': enable_host_file,
			'enable_ssl_host_file': enable_ssl_host_file
		}
