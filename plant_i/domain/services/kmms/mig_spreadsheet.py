from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class SpreadSheetService():
	def __init__(self):
		return

	def read_dept(self):
		items = []	

		sql = ''' 
            SELECT
                pk,
                action_type,
                dept_cd,
                dept_nm,
                up_dept_cd,
                up_dept_nm,
                business_yn,
                team_yn,
                tpm_yn,
                cc_cd,
                site_id,
                user_id,
                insert_ts,
                msg
            FROM
                cm_mig_dept;
            '''

		dc = {}
		items = DbUtil.get_rows(sql, dc)
		if items is None:
			items = []

		return items

	def migrate_dept(self):
		items = []

		sql = ''' 
			/* execute [mig-dept-mapper.xml] */
			CALL cm_prc_mig_dept(0)
			;
			'''

		try:
			items = DbUtil.sp_exec(sql)
			items = items['dataTable'][0]['r_count']

		except Exception as ex:
			LogWriter.add_dblog('error', 'SpreadSheetService.migrate_dept', ex)
			raise ex

		return items

	def read_user_info(self):
		items = []	

		sql = ''' 
            SELECT pk, action_type, login_id, user_nm, user_password, dept_cd, dept_nm, role_cd, user_mail, user_phone, emp_no, job_pos, allow_login, leader_yn, retire_yn, site_id, user_id, insert_ts, msg
			FROM cm_mig_user;
            '''

		dc = {}
		items = DbUtil.get_rows(sql, dc)
		if items is None:
			items = []

		return items

