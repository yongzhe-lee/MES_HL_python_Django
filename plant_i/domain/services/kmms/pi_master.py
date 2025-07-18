from configurations import settings
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PIService():

	def __init__(self):
		return

	#점검마스터조회
	#modified by choi : 2025/05/13  파라미터를 dictionary에 넣어서 전달한다
	#                 : 2025/06/02  나중에 inner join으로 바꿀 필요가 있음
	def findAll(self, dcparam):
		items = []

		searchText = dcparam.get('searchText',None)
		equipDeptPk = dcparam.get('equipDeptPk',None)
		locPk = dcparam.get('locPk',None)
		deptPk = dcparam.get('deptPk',None)
		isMyTask = dcparam.get('isMyTask',None)
		environEquipYn = dcparam.get('environEquipYn',None)
		useYn = dcparam.get('useYn',None)
		cycleTypeCd = dcparam.get('cycleTypeCd',None) 
		chkMastNo = dcparam.get('chkMastNo',None)
		startDate = dcparam.get('startDate',None)
		endDate = dcparam.get('endDate',None)

		#이건 뭐지?? 여러 화면에서 조회조건이 들어오는 것 같음
		chkMastNm = dcparam.get('chkMastNm',None)
		chkUserPk= dcparam.get('chkUserPk',None)
		equipPk = dcparam.get('equipPk',None)
		chkMastPk = dcparam.get('chkMastPk',None)
		chkMastPkNot = dcparam.get('chkMastPkNot',None)
		lastChkDateFrom = dcparam.get('lastChkDateFrom',None)
		lastChkDateTo = dcparam.get('lastChkDateTo',None)

		dic_param = {
			'searchText': searchText,
			'equDept': equipDeptPk,
			'equLoc': locPk,
			'deptPk': deptPk,
			'isMyTask': isMyTask,
			'environEquipYn': environEquipYn,
			'useYn':useYn, 
			'cycleTypeCd':cycleTypeCd, 
			'chkMastNo':chkMastNo,
			'startDate':startDate,
			'endDate':endDate
			}

		sql = ''' 
			select t.chk_mast_pk
				, t.chk_mast_nm
				, t.chk_mast_no
				, d.id
				, d."Name"
				, t.chk_user_pk
				, cm_fn_user_nm(cu."Name", cu.del_yn) as chk_user_nm
				, (case when (t.chk_mast_no ~ E'^[0-9]+$') = true then cast(t.chk_mast_no as integer) else 999999 end) as chk_mast_no_sort
				, to_char(t.last_chk_date, 'YYYY-MM-DD') as last_chk_date
				, to_char(t.first_chk_date, 'YYYY-MM-DD') as first_chk_date
				, to_char(t.sched_start_date, 'YYYY-MM-DD') as sched_start_date
				, to_char(t.next_chk_date, 'YYYY-MM-DD') as next_chk_date
				, t.cycle_type as cycle_type_cd
				, ct.code_nm   as cycle_type_nm
				, concat(t.per_number, ct.code_dsc) as cycle_display_nm
				, t.per_number
				, t.work_text
				, COUNT(DISTINCT eci.chk_item_pk) as equip_chk_item_cnt
				, COUNT(DISTINCT e.equip_pk) as chk_equip_item_cnt
				, t.use_yn
				, t.del_yn
				, t.insert_ts
				, t.inserter_id
				, t.inserter_nm
				, t.update_ts
				, t.updater_id
				, t.updater_nm
				, t.daily_report_cd
				, t.daily_report_type_cd
			FROM   cm_equip_chk_mast t
			LEFT OUTER JOIN dept d ON t.dept_pk = d.id
			LEFT OUTER JOIN cm_chk_equip ce on t.chk_mast_pk = ce.chk_mast_pk
			LEFT OUTER JOIN cm_equipment e on ce.equip_pk = e.equip_pk
			LEFT OUTER JOIN user_profile cu on t.chk_user_pk = cu."User_id"
			LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
			LEFT OUTER JOIN cm_equip_chk_item eci on t.chk_mast_pk = eci.chk_mast_pk
			LEFT OUTER JOIN cm_location l on e.loc_pk = l.loc_pk
			LEFT OUTER JOIN dept ed on e.dept_pk = ed.id
		WHERE  t.del_yn = 'N'
		'''        
		if useYn:
			sql += ''' AND t.use_yn = %(useYn)s 
			'''
		if searchText:
			sql += ''' AND (
				UPPER(t.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
			)
			'''
		
		if deptPk and deptPk > 0:
			sql += ''' AND (
					d.id = %(deptPk)s
					OR
					d.id In (select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
				)
			'''
		
		if equipDeptPk and equipDeptPk > 0 :
			sql += ''' AND (
					ed.id = %(equipDeptPk)s
					OR
					ed.id In (select dept_pk from v_dept_path where %(equipDeptPk)s = path_info_pk)
				)
			'''
		if locPk and locPk > 0 :
			sql += ''' AND (
				l.loc_pk = %(locPk)s
				OR
				l.loc_pk In (select loc_pk from (select * from fn_get_loc_path(%(siteId)s)) x where %(locPk)s = path_info_pk)
			)
			'''
		
		if cycleTypeCd :
			sql += '''  AND ct.code_cd = %(cycleTypeCd)s 
			'''
				
		if environEquipYn == 'Y':			
			sql += '''  AND e.environ_equip_yn = %(environEquipYn)s
			'''
		
		if chkMastNo and chkMastNo > 0 :
			sql += '''  AND t.chk_mast_no = %(chkMastNo)s
			'''

		if chkMastNm :			
			sql += '''  AND t.chk_mast_nm = %(chkMastNm)s
			'''
		
		if chkUserPk and chkUserPk > 0 :
			sql += '''  AND cu."User_id" = %(chkUserPk)s
			'''
		
		if equipPk and equipPk > 0 :
			sql += '''  AND e.equip_pk = %(equipPk)s
			'''
		
		if chkMastPk and chkMastPk > 0 :
			sql += '''  AND t.chk_mast_pk = %(chkMastPk)s
			'''
		
		if chkMastPkNot and chkMastPkNot > 0 :
			sql += '''  AND t.chk_mast_pk <> %(chkMastPkNot)s
			'''
		
		if lastChkDateFrom and lastChkDateTo :
			sql += '''  AND date(t.last_chk_date) BETWEEN to_date(%(lastChkDateFrom)s, 'YYYY-MM-DD') AND to_date(%(lastChkDateTo)s, 'YYYY-MM-DD')
			'''

		if startDate and endDate :
			sql += '''  
			AND date(coalesce(t.next_chk_date,cast(cm_fn_get_regular_day(t.sched_start_date::date, t.sched_start_date::date, t.per_number, ct.code_cd) as date)))
				BETWEEN to_date(%(startDate)s, 'YYYY-MM-DD') AND to_date(%(endDate)s, 'YYYY-MM-DD')
			'''

		sql +='''
			GROUP BY t.chk_mast_pk
			, t.chk_mast_nm
			, t.chk_mast_no
			, d.id
			, d."Name"
			, t.chk_user_pk
			, cu."Name"
			, cu.del_yn
			, t.last_chk_date
			, t.first_chk_date
			, t.sched_start_date
			, t.next_chk_date
			, t.cycle_type
			, ct.code_cd
			, ct.code_nm
			, ct.code_dsc
			, t.per_number
			, t.work_text
			, t.use_yn
			, t.del_yn
			, t.insert_ts
			, t.inserter_id
			, t.inserter_nm
			, t.update_ts
			, t.updater_id
			, t.updater_nm
			, t.daily_report_cd
			, t.daily_report_type_cd
		'''
		sql +='''
				order by chk_mast_pk desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
			raise ex

		return items

	#점검 주기 시뮬레이션
	def selectEquipChkScheSimulationCycleByMon(self, deptPk, userPk,calSearchType, fromDate, toDate):
		sql = ''' 
		/* selectEquipChkScheSimulationCycleByMon [equip-check-mast-mapper.xml] */

			with recursive scheview as (
				SELECT t1.chk_mast_pk
					, t1.sched_start_date
					, t1.sched_start_date as curr_date
					, t1.cycle_type
					, t1.per_number
					, d.id as dept_pk
					, d."Name" as dept_nm
					, u."User_id" as user_pk
					, cm_fn_user_nm(u."Name", u.del_yn) as user_nm
					, cm_fn_dateadd(date(t1.sched_start_date), replace(replace(replace(replace(replace(t1.cycle_type, 'CYCLE_TYPE_', ''), 'M', 'month'), 'Y', 'year'), 'W', 'week'), 'D', 'day'), t1.per_number) as next_date
				FROM cm_equip_chk_mast t1
				inner JOIN dept d ON t1.dept_pk = d.id
				inner JOIN user_profile u ON t1.chk_user_pk = u."User_id"
				WHERE t1.use_yn = 'Y' and t1.del_yn = 'N'
					AND t1.cycle_type IN (
						SELECT code_cd
						FROM cm_base_code
						WHERE code_grp_cd = 'CYCLE_TYPE'
					)
				'''

		if deptPk :
			sql += '''  
				AND (
						d.id = %(deptPk)s 
						OR
						d.id In (select dept_pk from v_dept_path where %(deptPk)s  = path_info_pk)
					)
			
			'''

		if userPk :
			sql += '''  AND u."User_id" = %(userPk)s 
			'''

		sql += '''
				
				UNION ALL
				SELECT t2.chk_mast_pk
					, t2.sched_start_date
					, t2.next_date AS next_date
					, t2.cycle_type
					, t2.per_number
					, t2.dept_pk
					, t2.dept_nm
					, t2.user_pk
					, t2.user_nm
					, cm_fn_dateadd(date(t2.next_date), replace(replace(replace(replace(replace(t2.cycle_type, 'CYCLE_TYPE_', ''), 'M', 'month'), 'Y', 'year'), 'W', 'week'), 'D', 'day'), t2.per_number) as next_date
				FROM scheview t2
				WHERE t2.next_date <= to_date(%(toDate)s, 'YYYYMMDD')
			)
			, schelist as (
				SELECT p.chk_mast_pk
						, p.sched_start_date
						, p.sched_start_date AS next_date
						, p.cycle_type
						, p.per_number
						, d.id as dept_pk
						, d."Name" as dept_nm
						, u."User_id" as user_pk
						, u."Name" as user_nm
				FROM cm_equip_chk_mast p
				inner JOIN dept d ON p.dept_pk = d.id
				inner JOIN user_profile u ON p.chk_user_pk = u."User_id"
				WHERE p.use_yn = 'Y' AND p.del_yn = 'N'
				AND p.sched_start_date between to_date(%(fromDate)s, 'YYYYMMDD') and to_date(%(toDate)s, 'YYYYMMDD')
				'''

		if deptPk :
			sql += '''  
				AND (
						d.id = %(deptPk)s 
						OR
						d.id In (select dept_pk from v_dept_path where %(deptPk)s  = path_info_pk)
					)
			
			'''

		if userPk :
			sql += '''  AND u."User_id" = %(userPk)s 
			'''

		sql += '''
				UNION ALL
				SELECT chk_mast_pk
						, sched_start_date
						, next_date
						, cycle_type
						, per_number
						, dept_pk
						, dept_nm
						, user_pk
						, user_nm
				FROM scheview
				WHERE next_date between to_date(%(fromDate)s, 'YYYYMMDD') and to_date(%(toDate)s, 'YYYYMMDD')
			)
			, cte as
			(
				SELECT to_char(next_date, 'YYYY-MM-DD') as sche_dt
						, to_char(next_date, 'YYYY-MM-DD') as sche_dt_label
						, dept_pk
						, dept_nm
						, user_pk
						, user_nm
						, Count(*) AS cnt
				FROM   schelist
				GROUP  BY to_char(next_date, 'YYYY-MM-DD')
							, dept_pk
							, dept_nm
							, user_pk
							, user_nm
			)
			SELECT 
				1 AS id, '' as type ,
				user_nm || ' (' || cnt || '건)' AS title,
				sche_dt::date AS start,         -- 날짜만, time 제거
				sche_dt::date AS "end",         -- 필드명이 예약어라면 쌍따옴표
				true AS isAllDay
			FROM cte
			ORDER BY sche_dt;
			'''
		
		try:
			items = []
			dic_param = {
				'deptPk': deptPk,
				'userPk': userPk,
				'calSearchType': calSearchType,
				'fromDate': fromDate,
				'toDate': toDate,
			}
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
			raise ex

		return items

	def selectEquipChkScheSimulationByMon(self, calDeptPk, calChkUserPk,calSearchType):
		sql = ''' 
			/* selectEquipChkScheSimulationByMon [equip-check-mast-mapper.xml] */

				select to_char(t.sched_start_date ,'YYYYMMDD') as sche_dt
				, to_char(t.sched_start_date,'YYYY-MM-DD') as sche_dt_label
				, d.id
				, d."Name"
				, cu."User_id"
				, cm_fn_user_nm(cu."Name", cu.del_yn) as user_nm
				, count(*) as cnt
			from cm_equip_chk_mast t
			inner join dept d on t.dept_pk = d.id
			inner join user_profile cu on t.chk_user_pk = cu."User_id"
			where 1=1
			--and t.sched_start_date BETWEEN to_date('20250427', 'YYYYMMDD') AND to_date('20250531', 'YYYYMMDD')
			'''

		if calDeptPk :
			sql += '''

					AND (
						d.id = %(calDeptPk)s
						OR
						d.id In (select dept_pk from cm_v_dept_path where calDeptPk = path_info_pk)
					)
		'''

		if calChkUserPk :
			sql += '''
					AND cu."User_id" = %(calChkUserPk)s
			'''

		if calSearchType :
			sql += '''
					AND 1=1
			'''

		sql += '''
			group by t.sched_start_date
			, d.id
			, d."Name"
			, cu."User_id"
			, cu."Name"
			, cu.del_yn
			
			'''

		sql +='''
			ORDER  BY to_char(next_date, 'YYYY-MM-DD')
			'''
		try:
			items = []
			dic_param = {
				'calDeptPk': calDeptPk,
				'calChkUserPk': calChkUserPk,
				'calSearchType': calSearchType,
			}
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
			raise ex

		return items

	# 점검마스터 max 점검번호를 가져온다
	#commented by An : 2025/06/12
	#                : 점검번호 부여 형식 바꾸기로 해서 주석처리 해두겠습니다.
	# def selectMaxEquipChkMastNo(self):
	#     sql = ''' 
	#         select coalesce(MAX((select chk_mast_no
	# 			from (
	# 			    SELECT max(cast(chk_mast_no as integer)) as chk_mast_no
	# 			    FROM cm_equip_chk_mast
	# 			    WHERE (chk_mast_no ~ E'^[0-9]+$') = true
	# 			    --AND site_id = %(siteId}
	# 			) as sub_table
	# 		)) + 1, '1') as max_no
	# 		from cm_equip_chk_mast
	#     '''

	#     try:
	#         dc = {}
	#         result = DbUtil.get_row(sql, dc)
	#     except Exception as ex:
	#         LogWriter.add_dblog('error', 'PMService.selectMaxEquipChkMastNo', ex)
	#         raise ex

	#     return result

	#점검마스터 상세
	#commented by choi : 2025/06/02
	#                  : 나중에 inner join으로 바꿀 필요가 있음
	def get_pi_master_detail(self, chkMastPk):
		
		sql = ''' 
		select t.chk_mast_pk
				, t.chk_mast_nm
				, t.chk_mast_no
				, d.id
				, d."Name"
				, t.chk_user_pk
				, cm_fn_user_nm(cu."Name", cu.del_yn) as chk_user_nm
				, (case when (t.chk_mast_no ~ E'^[0-9]+$') = true then cast(t.chk_mast_no as integer) else 999999 end) as chk_mast_no_sort
				, t.last_chk_date
				, t.first_chk_date
				, t.sched_start_date
				, t.next_chk_date
				, t.cycle_type as cycle_type_cd
				, ct.code_nm   as cycle_type_nm
				, concat(t.per_number, ct.code_dsc) as cycle_display_nm
				, t.per_number
				, t.work_text
				--, COUNT(DISTINCT eci.chk_item_pk) as equip_chk_item_cnt
				--, COUNT(DISTINCT e.equip_pk) as chk_equip_item_cnt
				, t.use_yn
				, t.del_yn
				, t.insert_ts
				, t.inserter_id
				, t.inserter_nm
				, t.update_ts
				, t.updater_id
				, t.updater_nm
				, t.daily_report_cd
				, t.daily_report_type_cd
			FROM   cm_equip_chk_mast t
			--INNER JOIN dept d ON t.dept_pk = d.id
			--INNER JOIN cm_chk_equip ce on t.chk_mast_pk = ce.chk_mast_pk
			--INNER JOIN cm_equipment e on ce.equip_pk = e.equip_pk
			LEFT OUTER JOIN dept d ON t.dept_pk = d.id
			LEFT OUTER JOIN cm_chk_equip ce on t.chk_mast_pk = ce.chk_mast_pk
			LEFT OUTER JOIN cm_equipment e on ce.equip_pk = e.equip_pk
			LEFT OUTER JOIN user_profile cu on t.chk_user_pk = cu."User_id"
			LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
			LEFT OUTER JOIN cm_equip_chk_item eci on t.chk_mast_pk = eci.chk_mast_pk
			LEFT OUTER JOIN cm_location l on e.loc_pk = l.loc_pk
			LEFT OUTER JOIN dept ed on e.dept_pk = ed.id
		WHERE  t.chk_mast_pk = %(chkMastPk)s
		'''

		data = {}
		try:
			items = DbUtil.get_rows(sql, {'chkMastPk':chkMastPk})
			if len(items)>0:
				data = items[0]
		except Exception as ex:
			LogWriter.add_dblog('error','PiService.get_pi_master_detail', ex)
			raise ex

		return data

	def get_pm_modal(self, keyword, dept_pk):
		items = []
		dic_param = {'keyword':keyword, 'dept_pk':dept_pk}

		sql = ''' 
		select * from pm
			left join auth_user au on pm."_creater_id" = au.id 
			left join dept d ON pm."dept_pk" = d.id
			left join equ e on pm.equip_pk = e.id 
		where 1=1
		'''
		
		if keyword:
			sql+=''' 
				AND (UPPER(pm."pm_nm") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
					or UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
					or UPPER(e."Code") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
					)
			'''
		if dept_pk:
			sql+=''' 
			AND UPPER(d.id) LIKE CONCAT('%%',UPPER(%(dept_pk)s),'%%')
			'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error','EquipmentService.get_equip_modal', ex)
			raise ex

		return items

	def get_job_class_list(self):
		items = []        
		sql = ''' 
			SELECT job_class_pk, 
			cd as job_class_cd, 
			nm as job_class_nm, 
			wage_cost
			FROM job_class       
			WHERE 1 = 1 
		'''        
		sql += ''' 
			ORDER BY job_class_pk
			'''

		try:
			items = DbUtil.get_rows(sql)
		except Exception as ex:
			LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
			raise ex

		return items

	#==================점검설비관련====================



	#==================점검항목 관련===================


	#==================작업결과관련====================

	#==================점검 결과 관련====================

	def findAllCheckResult(self, searchText, chkRslt, chkStatus, deptPk, start_date, end_date, chk_legal, chk_my_task, user_pk):
		items = []
		dic_param = {
			'searchText': searchText,
			'chkRslt': chkRslt,
			'chkStatus': chkStatus,
			'deptPk': deptPk,
			'start_date': start_date,
			'end_date': end_date,
			'chk_legal': chk_legal,
			'chk_my_task': chk_my_task,
			'user_pk': user_pk,
		}

		sql = ''' 
		/* searchEquipSchedule [equip-chk-sche-mapper.xml] */

		with cte as (
			SELECT ecs.chk_sche_pk
					, ecs.chk_sche_no
					, ecm.chk_mast_pk
					, ecm.chk_mast_no
					, ecm.chk_mast_nm
					, d."Name"
					, cm_fn_user_nm(cu."Name", cu.del_yn) as chk_user_nm
					, bc.code_nm as chk_status_nm
					, bc.code_cd as chk_status_cd
					, bc.code_cd as chk_status
					, ecm.last_chk_date
					, ecs.chk_sche_dt
					, ecs.chk_dt
					, count(distinct e.equip_pk) as equip_cnt
					, count(distinct eim.chk_item_pk) as item_cnt
					, count(distinct case when ecr.chk_rslt='N' then e.equip_pk else null end) as normal_count
					, count(distinct case when ecr.chk_rslt='A' then e.equip_pk else null end) as fail_count
					, count(distinct case when ecr.chk_rslt='C' then e.equip_pk else null end) as unable_check_count
					, count(distinct case when ecr.chk_rslt_file_grp_cd is not null then e.equip_pk else null end) as result_attach_count
					, count(wo.work_order_no) as wo_count
			FROM cm_equip_chk_sche ecs
			inner join cm_equip_chk_mast ecm on ecs.chk_mast_pk=ecm.chk_mast_pk
			inner join cm_equip_chk_item_mst eim on ecs.chk_sche_pk=eim.chk_sche_pk
			left outer join dept d on ecs.dept_pk=d.id
			left outer join user_profile cu on ecs.chk_user_pk = cu."User_id"
			inner join cm_base_code bc on ecs.chk_status=bc.code_cd and (bc.code_grp_cd='CHK_STATUS')
			inner join cm_equip_chk_rslt ecr on ecs.chk_sche_pk=ecr.chk_sche_pk
			inner join cm_equipment e on ecr.equip_pk=e.equip_pk
			left outer join dept ed on e.dept_pk = ed.id
			left outer join cm_work_order wo on ecr.chk_rslt_pk = wo.chk_rslt_pk 
			-- AND wo.site_id = 'WEZON'
			-- WHERE ecm.site_id = 'WEZON' AND e.site_id = 'WEZON'
			WHERE 1=1
		'''
		if searchText:
			sql += '''
				AND (
					UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR
					UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR
					UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR
					UPPER(ecm.chk_mast_no) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR
					UPPER(cast(ecs.chk_sche_no as text)) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				)
			'''
		if deptPk:
			sql += '''
					AND (
						d.id = %(deptPk)s
						OR
						d.id In (select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
					)
			'''
		if chkStatus:
			sql += '''
				AND ecr.chk_rslt = %(chkRslt)s
			'''
		if chk_legal == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''
		if chk_my_task == 'Y':
			sql += '''
				AND cu."User_id" = %(user_pk)s          
			'''
		sql += '''
					AND (case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_NP' then bc.grp_cd else bc.code_cd end) =
						(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_NP' then 'NP' when coalesce(%(chkStatus)s, '') = '' then bc.code_cd else %(chkStatus)s end)

					AND date(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_Y' then ecs.chk_dt else ecs.chk_sche_dt end) >= to_date(%(start_date)s, 'YYYY-MM-DD')
						and date(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_Y' then ecs.chk_dt else ecs.chk_sche_dt end) <= to_date(%(end_date)s, 'YYYY-MM-DD')

			GROUP BY ecs.chk_sche_pk
					, ecs.chk_sche_no
					, ecm.chk_mast_pk
					, ecm.chk_mast_no
					, ecm.chk_mast_nm
					, d."Name"
					, cu."Name"
					, cu.del_yn
					, bc.code_nm
					, bc.code_cd
					, ecm.last_chk_date
					, ecs.chk_sche_dt
					, ecs.chk_dt
		)
		SELECT *
		FROM (
			table cte

					order by chk_sche_dt DESC 

				-- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by cast(chk_sche_no as INTEGER) desc, cast(chk_mast_no as INTEGER) desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
			items = CommonUtil.res_snake_to_camel(items)
		except Exception as ex:
			LogWriter.add_dblog('error', 'PMService.findAllCheckResult', ex)
			raise ex

		return items

	#==================작업WO관련======================


	#==================점검이상 발행WO 관련======================

	def findAllCheckWoIssued(self, searchText, chkScheNo, deptPk, environEquipYn, equipDeptPk, myRequestYn, workOrderNo, start_date, end_date, user_pk):
		items = []
		dic_param = {
			'searchText': searchText,
			'chkScheNo': chkScheNo,
			'deptPk': deptPk,
			'environEquipYn': environEquipYn,
			'equipDeptPk': equipDeptPk,
			'myRequestYn': myRequestYn,
			'workOrderNo': workOrderNo,
			'deptPk': deptPk,
			'start_date': start_date,
			'end_date': end_date,
			'user_pk': user_pk,
		}

		sql = '''
		/* findAll [work-order-mapper.xml] */

		with cte as (

		select t.work_order_pk
				, t.work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 'WEZON') as business_nm
				, t.work_charger_pk
				, cm_fn_user_nm(wcu."Name", wcu.del_yn) as work_charger_nm
				, mt.code_cd as maint_type_cd
				, mt.code_nm as maint_type_nm
				, ws.code_cd as wo_status_cd
				, ws.code_nm as wo_status_nm
				, t.plan_start_dt
				, t.plan_end_dt
				, t.start_dt
				, t.end_dt
				, t.want_dt
				, t.equip_pk
				, e.equip_cd
				, e.equip_nm
				, ed.id as equip_dept_pk
				, ed."Name" as equip_dept_nm
				, to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
				, t.pm_pk
				, p.pm_no
				, p.pm_nm
				, pt.code_nm                        AS pm_type_nm
				, p.work_text as pm_work_text
				, t.chk_rslt_pk
				, ecs.chk_sche_pk
				, ecs.chk_sche_no
				, ecm.chk_mast_nm
				, ecm.chk_mast_pk
				, ecs.chk_sche_dt
				, l.loc_nm
				, t.req_info
				, t.wo_type
				, t.rqst_insp_yn
				, t.rqst_dpr_yn
				, wt.code_nm as wo_type_nm
				, t.breakdown_dt
				, t.breakdown_min
				, wsc.code_cd as work_src_cd
				, wsc.code_nm as work_src_nm
				, t.tot_cost
				, t.mtrl_cost
				, t.labor_cost
				, t.outside_cost
				, t.etc_cost
				, t.problem_cd
				, wp.reliab_nm as problem_nm
				, t.cause_cd
				, wc.reliab_nm as cause_nm
				, t.remedy_cd
				, wr.reliab_nm as remedy_nm
				, prj.proj_cd
				, prj.proj_nm
				, t.wo_file_grp_cd
				, t.req_info_img_grp_cd
				, t.work_text_img_grp_cd
				, t.pm_req_type
				, t.req_dept_busi_cd
				, t.appr_line
				, t.appr_line_next
				, t.work_order_approval_pk
				, woa.reg_dt
				, woa.rqst_dt
				, woa.rqst_user_nm
				, woarqstd.id as rqst_dept_pk
				, woarqstd."Name" as rqst_dept_nm
				, woa.cancel_dt
				, woa.cancel_user_nm
				, woa.accept_dt
				, woa.appr_dt
				, woa.finish_dt
				, substring(t.appr_line, 1,2) as wo_start_type
				, cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
				, t.insert_ts
				, e.environ_equip_yn
				, e.equip_status as equip_stauts_cd
				, e.import_rank_pk
				, ir.import_rank_cd
				, e.up_equip_pk
				, ue.equip_nm AS up_equip_name
				, ec.equip_category_id
				, ec.equip_category_desc
				, ec.remark
				, e.equip_class_path
				, e.equip_class_desc
				, av.code_nm as first_asset_status
				, av.code_cd as first_asset_status_cd
				, cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
				, (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
				, (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm
				, l.loc_nm
				, es.ex_supplier_nm
				, woa.cancel_reason
				, t.cost_type
				, (select code_nm from cm_base_code where code_cd = t.cost_type and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm

		from cm_work_order t
			inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
			inner join cm_base_code mt on t.maint_type_cd = mt.code_cd and mt.code_grp_cd = 'MAINT_TYPE'
			inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
			inner join cm_equipment e on t.equip_pk = e.equip_pk
			inner join cm_location l on e.loc_pk = l.loc_pk
			left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
			left outer join dept ed on e.dept_pk  = ed.id
			left outer join dept wd on t.dept_pk = wd.id
			left outer join dept rd on t.req_dept_pk = rd.id
			left outer join user_profile wcu on t.work_charger_pk = wcu."User_id"
			left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC' 
			-- and wp.site_id = t.site_id
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC' 
			-- and wc.site_id = t.site_id
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC' 
			-- and wr.site_id = t.site_id
			left outer join cm_pm p on t.pm_pk = p.pm_pk
			left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
			left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
			left outer join user_profile pmu on p.pm_user_pk = pmu."User_id"
			left outer join user_profile wou on t.WORK_CHARGER_PK = wou."User_id"
			left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
			left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
			left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
			left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
			left outer join cm_project prj on t.proj_cd = prj.proj_cd
			left outer join user_profile woarqstu on woa.rqst_user_pk = woarqstu."User_id"
			left outer join dept woarqstd on woarqstu."Depart_id" = woarqstd.id
			left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
			left outer join cm_import_rank ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1

		-- AND t.site_id = 'WEZON'

			-- AND e.site_id = 'WEZON'

		'''
		if workOrderNo:
			sql += '''
			AND t.work_order_no = %(workOrderNo)s
			'''
		else:
			if chkScheNo:
				sql += '''
				AND ecs.chk_sche_no = cast(%(chkScheNo)s as integer)
				'''
			if searchText:
				sql += '''
				AND (
					UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
					OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
					OR UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
				)
				'''
			if equipDeptPk:
				sql += '''
				AND (
					ed.id = %(equipDeptPk)s
					OR
					ed.id In (select dept_pk from cm_v_dept_path where %(equipDeptPk)s = path_info_pk)
				)
				'''
			if deptPk:
				sql += '''
				AND (
					wd.id = %(deptPk)s
					OR
					wd.id IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
				'''
			if environEquipYn == 'Y':
				sql += '''
				AND e.environ_equip_yn = 'Y'
				'''
			if myRequestYn == 'Y':
				sql += '''
				AND woa.rqst_user_pk = %(user_pk)s
				'''
			sql += '''
				AND ws.code_cd <> 'WOS_DL'
			'''
		sql += '''
			AND t.chk_rslt_pk IS NOT NULL

				AND (
					(date(t.start_dt) >= to_date(%(start_date)s, 'YYYY-MM-DD') AND date(t.start_dt) <= to_date(%(end_date)s, 'YYYY-MM-DD'))
					OR
					(date(t.end_dt) >= to_date(%(start_date)s, 'YYYY-MM-DD') AND date(t.end_dt) <= to_date(%(end_date)s, 'YYYY-MM-DD'))
				)

		)
		SELECT *
		FROM (
			table cte

				-- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by pm_no desc, work_order_no desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
			items = CommonUtil.res_snake_to_camel(items)
		except Exception as ex:
			LogWriter.add_dblog('error', 'PMService.findAllCheckWoIssued', ex)
			raise ex

		return items