
from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class CmSiteConfigService():
	def __init__(self):
		return

	def read(self, site):
		items = []
		dic_param = {'site': site}

		sql = ''' 
			SELECT site, proc_opts, sche_opts, ext_opts, svc_opts, user_policy
			FROM cm_site_config
			WHERE site = %(site)s
			;
			'''

		try:
			items = DbUtil.get_row(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'SiteConfig.read', ex)
			raise ex

		return items
