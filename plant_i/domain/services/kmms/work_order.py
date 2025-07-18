from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class WorkOrderService():

	def __init__(self):
		return

	# 작업요청
	def get_my_work_request_list(self, keyword, req_dept, rqst_user_nm, start_dt, end_dt, wo_status, maint_type_cd, dept_pk, problem_cd, cause_cd, srch_wo_no_only, srch_my_req_only, srch_environ_equip_only, srch_non_del_only, current_user_id):
		items = []
		dic_param = {'keyword': keyword, 'req_dept': req_dept, 'rqst_user_nm': rqst_user_nm, 'start_dt': start_dt, 'end_dt': end_dt, 'wo_status': wo_status, 'maint_type_cd': maint_type_cd, 'dept_pk': dept_pk, 'problem_cd': problem_cd, 'cause_cd': cause_cd, 'srch_wo_no_only': srch_wo_no_only, 'srch_my_req_only': srch_my_req_only, 'srch_environ_equip_only': srch_environ_equip_only, 'srch_non_del_only': srch_non_del_only, 'current_user_id': current_user_id}

		sql = '''
		with cte as (

		select t.work_order_pk
				, COALESCE(t.work_order_no, '임시저장') AS work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''

		if keyword:
			if srch_wo_no_only == 'Y':
				sql += '''
					AND t.work_order_no = %(keyword)s
				'''
			else:
				sql += '''
					AND (
					UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

						OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					)
				'''
		if req_dept:
			sql += '''
				AND (
				rd.id = %(req_dept)s
				OR
				rd.id IN ( select dept_pk from cm_v_dept_path where %(req_dept)s = path_info_pk)
				)
			'''
		if rqst_user_nm:
			sql += '''
				AND woa.rqst_user_nm = %(rqst_user_nm)s
			'''
		if wo_status:
			sql += '''
				AND t.wo_status IN (

		        	%(wo_status)s

				)
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if start_dt and end_dt:
			sql += '''
				AND (
			 	(date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
			 	OR
			 	(date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
				)
			'''
		if problem_cd:
			sql += '''
				AND t.problem_cd = %(problem_cd)s
			'''
		if cause_cd:
			sql += '''
				AND t.cause_cd = %(cause_cd)s
			'''
		if srch_my_req_only == 'Y':
			sql += '''
				AND woa.rqst_user_pk = %(current_user_id)s
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''
		if srch_non_del_only == 'Y':
			sql += '''
				AND t.wo_status NOT IN (

		        	'NOTHING'
					,
		        	'WOS_DL'
				)
			'''
		else:
			sql += '''
				AND t.wo_status NOT IN (

		        	'NOTHING'

				)
			'''

			# 작업지시 등록에 wo_type 추가하면 아래 sql에 추가하기

			# AND t.wo_type NOT IN (

		 #        	'PM'

			# )
		sql += '''			
			AND coalesce(t.rqst_dpr_yn, 'N') = 'N'
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by pm_no desc, work_order_no desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_list', ex)
			raise ex

		return items

	# 작업요청 승인
	def get_work_request_approval_list(self, keyword, req_dept, rqst_user_nm, start_dt, end_dt, maint_type_cd, dept_pk, problem_cd, cause_cd, srch_wo_no_only, srch_environ_equip_only):
		items = []
		dic_param = {'keyword': keyword, 'req_dept': req_dept, 'rqst_user_nm': rqst_user_nm, 'start_dt': start_dt, 'end_dt': end_dt, 'maint_type_cd': maint_type_cd, 'dept_pk': dept_pk, 'problem_cd': problem_cd, 'cause_cd': cause_cd, 'srch_wo_no_only': srch_wo_no_only, 'srch_environ_equip_only': srch_environ_equip_only}

		sql = '''
		with cte as (

		select t.work_order_pk
				, COALESCE(t.work_order_no, '임시저장') AS work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS' and ws.code_cd = 'WOS_RQ'
			inner join cm_equipment e on t.equip_pk = e.equip_pk
			inner join cm_location l on e.loc_pk = l.loc_pk
			left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
			left outer join dept ed on e.dept_pk  = ed.id
			left outer join dept wd on t.dept_pk = wd.id
			left outer join dept rd on t.req_dept_pk = rd.id
			left outer join user_profile wcu on t.work_charger_pk = wcu."User_id"
			left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC'
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1

		'''
		if keyword:
			if srch_wo_no_only == 'Y':
				sql += '''
					AND t.work_order_no = %(keyword)s
				'''
			else:
				sql += '''
					AND (
					UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

						OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
					)
				'''
		if req_dept:
			sql += '''
				AND (
				rd.id = %(req_dept)s
				OR
				rd.id IN ( select dept_pk from cm_v_dept_path where %(req_dept)s = path_info_pk)
				)
			'''
		if rqst_user_nm:
			sql += '''
				AND woa.rqst_user_nm = %(rqst_user_nm)s
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if start_dt and end_dt:
			sql += '''
				AND (
			 	(date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
			 	OR
			 	(date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
				)
			'''
		if problem_cd:
			sql += '''
				AND t.problem_cd = %(problem_cd)s
			'''
		if cause_cd:
			sql += '''
				AND t.cause_cd = %(cause_cd)s
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''

			# 작업지시 등록에 wo_type 추가하면 아래 sql에 추가하기
			# AND t.wo_type NOT IN (

		 #        	'PM'

			# )

			# AND t.wo_status NOT IN (

		 #        	'WOS_DL'
			# 	 ,
		 #        	'WOS_CL'
			# 	 ,
		 #        	'WOS_RW'

			# )

			# AND t.wo_status IN (

		 #        	'WOS_RQ'
			# 	 ,
		 #        	'WOS_RJ'

			# )

		sql += '''


			AND coalesce(t.rqst_dpr_yn, 'N') = 'N'
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by pm_no desc, work_order_no desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_request_approval_list', ex)
			raise ex

		return items

	# 작업지시 승인
	def get_work_order_approval_list(self, keyword, req_dept, start_dt, end_dt, maint_type_cd, dept_pk, srch_environ_equip_only, wos_type):
		items = []
		dic_param = {'keyword': keyword, 'req_dept': req_dept, 'start_dt': start_dt, 'end_dt': end_dt, 'maint_type_cd': maint_type_cd, 'dept_pk': dept_pk, 'srch_environ_equip_only': srch_environ_equip_only, 'wos_type': wos_type}

		sql = '''
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
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS' and ws.code_cd = 'WOS_OC'
			inner join cm_equipment e on t.equip_pk = e.equip_pk
			inner join cm_location l on e.loc_pk = l.loc_pk
			left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
			left outer join dept ed on e.dept_pk  = ed.id
			left outer join dept wd on t.dept_pk = wd.id
			left outer join dept rd on t.req_dept_pk = rd.id
			left outer join user_profile wcu on t.work_charger_pk = wcu."User_id"
			left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC'
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''
		if keyword:
			sql += '''
				AND (
				UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

					OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				)
			'''
		if req_dept:
			sql += '''
				AND (
				rd.id = %(req_dept)s
				OR
				rd.id IN ( select dept_pk from cm_v_dept_path where %(req_dept)s = path_info_pk)
				)
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if start_dt and end_dt:
			sql += '''
				AND (
			 	(date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
			 	OR
			 	(date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
				)
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''
		if wos_type == 'WOS_OC': #승인할 대상
			sql += '''
				AND t.wo_status  IN (

		        	%(wos_type)s

				)
			'''
		elif wos_type == 'WOS_AP': #반려할 대상
			sql += '''
				AND t.wo_status  IN (

		        	%(wos_type)s

				)
				AND t.wo_type = 'WO'
			'''
		sql += '''
			AND t.wo_status NOT IN (

		        	'WOS_DL'
				 ,
		        	'WOS_CL'
				 ,
		        	'WOS_RW'

			)

			AND coalesce(t.rqst_dpr_yn, 'N') = 'N'
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by pm_no desc, work_order_no desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_approval_list', ex)
			raise ex

		return items

	# 작업지시 관리
	def get_work_order_management_list(self, keyword, req_dept, srch_date, start_dt, end_dt, wos_status_list, wo_type, maint_type_cd, dept_pk, problem_cd, srch_wo_no_only, srch_my_work_only, srch_environ_equip_only, current_user_id):
		items = []
		dic_param = {'keyword': keyword, 'req_dept': req_dept, 'srch_date': srch_date, 'start_dt': start_dt, 'end_dt': end_dt, 'wos_status_list': wos_status_list, 'wo_type' : wo_type, 'maint_type_cd': maint_type_cd, 'dept_pk': dept_pk, 'problem_cd': problem_cd, 'srch_wo_no_only': srch_wo_no_only, 'srch_my_work_only': srch_my_work_only, 'srch_environ_equip_only': srch_environ_equip_only, 'current_user_id': current_user_id}

		sql = '''
		/* findAllD [work-order-mapper.xml] */

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
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, '1') as business_nm
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
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC' 
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC' 
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
			left outer join user_profile woarqstu on woa.rqst_user_pk = woarqstu."Depart_id"
			left outer join dept woarqstd on woarqstu."Depart_id" = woarqstd.id
			left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1    

            AND t.WO_TYPE = 'WO'

            AND t.wo_status NOT IN (

                    'WOS_RQ'
                 ,  
                    'WOS_RB'
                 ,  
                    'WOS_RJ'

            )

            AND t.wo_status IN (

                    'WOS_AP'
                 ,  
                    'WOS_CM'
                 ,  
                    'WOS_OC'
                 ,  
                    'WOS_CL'

            )

            AND t.wo_type = 'WO'

             

            AND coalesce(t.rqst_dpr_yn, 'N') = 'N'

        )
        SELECT *
        FROM (
            table cte

                 order by rqst_dt ASC                    , 
                        work_order_sort ASC 


        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_management_list', ex)
			raise ex

		return items

	# WO사후등록
	def get_post_work_management_list(self, keyword, post_wo_status, req_dept, start_dt, end_dt, maint_type_cd, dept_pk, srch_my_work_only, srch_environ_equip_only, current_user_id):
		items = []
		dic_param = {'keyword': keyword, 'post_wo_status': post_wo_status, 'req_dept': req_dept, 'start_dt': start_dt, 'end_dt': end_dt, 'maint_type_cd': maint_type_cd, 'dept_pk': dept_pk, 'srch_my_work_only': srch_my_work_only, 'srch_environ_equip_only': srch_environ_equip_only, 'current_user_id': current_user_id}

		sql = '''
		with cte as (

		select t.work_order_pk
				, COALESCE(t.work_order_no, '임시저장') AS work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''
		if keyword:
			sql += '''
				AND (
				UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR wcu."Name" LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

					OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				)
			'''
		if req_dept:
			sql += '''
				AND (
				rd.id = %(req_dept)s
				OR
				rd.id IN ( select dept_pk from cm_v_dept_path where %(req_dept)s = path_info_pk)
				)
			'''
		if post_wo_status == '10':
			sql += '''
				AND (t.wo_status = 'WOS_RW' AND t.end_dt IS NULL)
			'''
		elif post_wo_status == '20':
			sql += '''
				AND (t.wo_status = 'WOS_RW' AND t.end_dt IS NOT NULL)
			'''
		elif post_wo_status == '30':
			sql += '''
				AND t.wo_status = 'WOS_CL'
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if start_dt and end_dt:
			sql += '''
				AND (
			 	(date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
			 	OR
			 	(date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
			 		AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
				)
			'''
		if srch_my_work_only == 'Y':
			sql += '''
				AND t.work_charger_pk = %(current_user_id)s
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''

		sql += '''
			AND t.wo_status IN (

		        	'WOS_RW'
				 ,
		        	'WOS_DL'
				 ,
		        	'WOS_CL'

			)
			AND coalesce(t.rqst_dpr_yn, 'N') = 'N'
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		order by pm_no desc, work_order_no desc
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_post_work_management_list', ex)
			raise ex

		return items

	# WO 작업이력 조회
	def get_work_order_hist_list(self, keyword, wo_type, wo_status, srch_date, start_dt, end_dt, maint_type_cd, loc_pk, dept_pk, problem_cd, cause_cd, remedy_nm, srch_end_date_only, srch_environ_equip_only, factory_id):
		items = []
		dic_param = {'keyword': keyword, 'wo_type': wo_type, 'wo_status': wo_status, 'srch_date': srch_date, 'start_dt': start_dt, 'end_dt': end_dt, 'maint_type_cd': maint_type_cd, 'loc_pk': loc_pk, 'dept_pk': dept_pk, 'problem_cd': problem_cd, 'cause_cd': cause_cd, 'remedy_nm': remedy_nm, 'srch_end_date_only': srch_end_date_only, 'srch_environ_equip_only': srch_environ_equip_only, 'factory_id': factory_id}

		sql = '''
		with cte as (

		select t.work_order_pk
				, COALESCE(t.work_order_no, '임시저장') AS work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''
		if keyword:
			sql += '''
				AND (
				UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR wcu."Name" LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR woarqstu.USER_NM LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

                    OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				)
			'''
		if wo_type:
			sql += '''
				AND t.WO_TYPE = %(wo_type)s
			'''
		if wo_status:
			sql += '''
				AND t.wo_status IN (

		        	%(wo_status)s

				)
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if loc_pk:
			sql += '''
				AND (
                l.loc_pk = %(loc_pk)s
                OR
                l.loc_pk IN ( select loc_pk from (select * from cm_fn_get_loc_path(%(factory_id)s)) as loc_path where %(loc_pk)s = path_info_pk)
				)
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if problem_cd:
			sql += '''
				AND t.problem_cd = %(problem_cd)s
			'''
		if cause_cd:
			sql += '''
				AND t.cause_cd = %(cause_cd)s
			'''
		if remedy_nm:
			sql += '''
				AND t.remedy_nm = %(remedy_nm)s
			'''
		if srch_end_date_only == 'Y':
			if start_dt and end_dt:
				sql += '''
					AND (
						(date(t.end_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.end_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
					)
				'''
		else:
			if srch_date:
				if srch_date == "DATE_TYPE_WORK" and start_dt and end_dt:
					sql += '''
						AND (
                			(
								(date(t.start_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.start_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
								OR
								(date(t.end_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.end_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
							)
						)
					'''
				elif srch_date == "DATE_TYPE_PLAN" and start_dt and end_dt:
					sql += '''
						AND (
							(
                    			(date(t.plan_start_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.plan_start_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
								OR
								(date(t.plan_end_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.plan_end_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
							)
						)
					'''
				elif srch_date == "DATE_TYPE_REQ" and start_dt and end_dt:
					sql += '''
						AND (
							(
								(date(woa.rqst_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(woa.rqst_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
								OR
								(date(woa.rqst_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(woa.rqst_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
							)
						)
					'''
				elif srch_date == "DATE_TYPE_HOPE" and start_dt and end_dt:
					sql += '''
						AND (
							(
								(date(t.want_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.want_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
								OR
								(date(t.want_dt) >= to_date(%(start_dt)s, 'YYYY-MM-DD') AND date(t.want_dt) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
							)
						)
				'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''
		sql += '''
		    AND t.wo_status NOT IN (

                    'WOS_RW'

            )
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_hist_list', ex)
			raise ex

		return items


	# 취소된 WO 목록 조회
	def get_work_order_cancel_list(self, keyword, dept_pk, start_dt, end_dt, maint_type_cd, srch_environ_equip_only):
		items = []
		dic_param = {'keyword': keyword, 'dept_pk': dept_pk, 'start_dt': start_dt, 'end_dt': end_dt, 'maint_type_cd': maint_type_cd, 'srch_environ_equip_only': srch_environ_equip_only}

		sql = '''
		with cte as (

		select t.work_order_pk
				, COALESCE(t.work_order_no, '임시저장') AS work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''
		if keyword:
			sql += '''
				AND (
				UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR wcu."Name" LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR woarqstu.USER_NM LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

                    OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				)
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if start_dt and end_dt:
			sql += '''
				AND (
					(date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
						AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
					OR
					(date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date(%(start_dt)s, 'YYYY-MM-DD')
						AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
										when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date(%(end_dt)s, 'YYYY-MM-DD'))
				)
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''
		sql += '''
		    AND t.wo_status NOT IN (

                    'WOS_DL'

            )
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_hist_list', ex)
			raise ex

		return items

	# 미처리 WO 목록
	def get_work_order_pending_list(self, keyword, req_dept, dept_pk, delay_days, maint_type_cd, problem_cd, cause_cd, remedy_nm, srch_environ_equip_only):
		items = []
		dic_param = {'keyword': keyword, 'req_dept': req_dept, 'dept_pk': dept_pk, 'delay_days': delay_days, 'maint_type_cd': maint_type_cd, 'problem_cd': problem_cd, 'cause_cd': cause_cd, 'remedy_nm': remedy_nm, 'srch_environ_equip_only': srch_environ_equip_only	}

		sql = '''
		with cte as (

		select t.work_order_pk
				, COALESCE(t.work_order_no, '임시저장') AS work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd."Name" as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 1) as business_nm
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
				, to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
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
				, to_char(woa.rqst_dt, 'yyyy-MM-dd') as rqst_dt
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
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
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
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''
		if keyword:
			sql += '''
				AND (
				UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')

                    OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				)
			'''
		if req_dept:
			sql += '''
				AND (
				rd.id = %(req_dept)s
				OR
				rd.id IN ( select dept_pk from cm_v_dept_path where %(req_dept)s = path_info_pk)
				)
			'''
		if dept_pk:
			sql += '''
				AND (
				wd.id = %(dept_pk)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(dept_pk)s = path_info_pk)
				)
			'''
		if delay_days:
			sql += '''
				AND fn_datediff(cast(now() as timestamp), t.plan_end_dt) >= cast(%(delay_days)s as integer)
			'''
		if maint_type_cd:
			sql += '''
				AND mt.code_cd = %(maint_type_cd)s
			'''
		if problem_cd:
			sql += '''
				AND t.problem_cd = %(problem_cd)s
			'''
		if cause_cd:
			sql += '''
				AND t.cause_cd = %(cause_cd)s
			'''
		if remedy_nm:
			sql += '''
				AND t.remedy_cd = %(remedy_nm)s
			'''
		if srch_environ_equip_only == 'Y':
			sql += '''
				AND e.environ_equip_yn = 'Y'
			'''
		sql += '''
		    AND t.wo_status NOT IN (

                    'WOS_RW'
				 ,
		        	'WOS_CL'
				 ,
		        	'WOS_DL'

            )
		)
		SELECT *
		FROM (table cte  order by rqst_dt DESC ,    work_order_sort DESC ) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		'''
		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_pending_list', ex)
			raise ex

		return items



	def get_work_order_detail(self, id):
		sql = '''
		SELECT
			*
		FROM work_order a
		WHERE
			a.id = %(id)s
		'''
		data = {}
		try:
			items = DbUtil.get_rows(sql, {'id':id})
			if len(items)>0:
				data = items[0]
		except Exception as ex:
			LogWriter.add_dblog('error','WorkOrderService.get_work_order_detail', ex)
			raise ex

		return data
