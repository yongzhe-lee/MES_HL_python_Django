from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class KmmsService():
	def __init__(self):
		return

	def execScheduler(self):
		items = []
		dic_param = {}

		sql = ''' 
			CALL public.cm_prc_job_pm_schedule(0);
			CALL public.cm_prc_job_insp_schedule(0);
			'''
		try:
			items = DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'SchedulerService.scheduler', ex)
			raise ex

		return items
