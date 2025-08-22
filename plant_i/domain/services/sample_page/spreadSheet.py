from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class SpreadSheetService():
	def __init__(self):
		return

	def read(self):
		items = []	

		sql = ''' 
            SELECT t.proj_pk
		       , t.proj_nm
		       , t.proj_cd
		       , t.plan_start_dt
		       , t.plan_end_dt
		       , t.manager_id
		       , cm_fn_user_nm(ui."Name", 'N') as user_nm
		       , t.proj_purpose
		       , coalesce(t.proj_tot_cost, 0) as proj_tot_cost
		       , t.status
		       , bc.code_nm as status_nm
		       , t.factory_pk
		       , t.insert_ts
		       , t.update_ts
		       , t.inserter_id
		       , t.updater_id
		    FROM   cm_project t
		    left join user_profile ui on t.manager_id = cast(ui."User_id" as integer)
		    left join cm_base_code bc on UPPER(t.status) = upper(bc.code_cd) 
            and upper(bc.code_grp_cd) = 'PRJ_STATUS'
		    where 1=1
			order by t.proj_pk
            '''

		dc = {}
		items = DbUtil.get_rows(sql, dc)
		if items is None:
			items = []

		return items

	def getDateHeader(self):
		items = []	

		sql = ''' 
            select data_ymd from dummy_date where data_ymd > to_char(now(), 'yyyy-mm-dd') order by data_ymd limit 7;
            '''

		dc = {}
		items = DbUtil.get_rows(sql, dc)
		if items is None:
			items = []

		return items
