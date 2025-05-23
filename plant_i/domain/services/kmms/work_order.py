from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class WorkOrderService():

	def __init__(self):
		return

	def get_work_order_list(self, keyword, req_dept):
		items = []
		dic_param = {'keyword': keyword, 'req_dept': req_dept}
        
		sql = '''
		with cte as (

		select t.work_order_pk
				, t.work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd.dept_nm as req_dept_nm
				, rd.tpm_yn as req_dept_tpm_yn
				, t.dept_pk
				, wd.dept_nm as dept_nm
				, cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				, cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 'WEZON') as business_nm
				, t.work_charger_pk
				, cm_fn_user_nm(wcu.user_nm, wcu.del_yn) as work_charger_nm
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
				, ed.dept_pk as equip_dept_pk
				, ed.dept_nm as equip_dept_nm
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
				, woarqstd.dept_pk as rqst_dept_pk
				, woarqstd.dept_nm as rqst_dept_nm
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
			left outer join cm_dept ed on e.dept_pk  = ed.dept_pk
			left outer join cm_dept wd on t.dept_pk = wd.dept_pk
			left outer join cm_dept rd on t.req_dept_pk = rd.dept_pk
			left outer join cm_user_info wcu on t.work_charger_pk = wcu.user_pk
			left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC'
			left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC'
			left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC'
			left outer join cm_pm p on t.pm_pk = p.pm_pk
			left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
			left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
			left outer join cm_user_info pmu on p.pm_user_pk = pmu.user_pk
			left outer join cm_user_info wou on t.WORK_CHARGER_PK = wou.user_pk
			left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
			left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
			left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
			left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
			left outer join cm_project prj on t.proj_cd = prj.proj_cd
			left outer join cm_user_info woarqstu on woa.rqst_user_pk = woarqstu.user_pk
			left outer join cm_dept woarqstd on woarqstu.dept_pk = woarqstd.dept_pk
			left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
			left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
			left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
			left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
		where 1 = 1
		'''

		if 0 == 1:
			sql += '''
            AND t.problem_cd = 'ARLK'

            AND t.cause_cd = 'CC04'

			AND woa.rqst_user_nm = 'tttttttt'

			AND substring(t.appr_line, 1, 2) = 'RQ'

			AND t.wo_type NOT IN (

		        	'PM'

			)

			AND t.wo_status NOT IN (

		        	'NOTHING'

			)

			AND t.wo_status IN (

		        	'WOS_OC'

			)

			AND (
				wd.dept_pk = 25
				OR
				wd.dept_pk IN ( select dept_pk from cm_v_dept_path where 25 = path_info_pk)
			)

			AND (
				rd.dept_pk = 23
				OR
				rd.dept_pk IN ( select dept_pk from cm_v_dept_path where 23 = path_info_pk)
			)

			AND (
				UPPER(t.work_title) LIKE CONCAT('%',UPPER(CAST('testttt' as text)),'%')
				OR UPPER(t.work_text) LIKE CONCAT('%',UPPER(CAST('testttt' as text)),'%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(CAST('testttt' as text)),'%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(CAST('testttt' as text)),'%')

					OR UPPER(t.work_order_no) LIKE CONCAT('%',UPPER(CAST('testttt' as text)),'%')

			)

    		AND mt.code_cd = 'MAINT_TYPE_PM'

			 AND (
			 	(date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date('2025-04-08', 'YYYY-MM-DD')
			 		AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date('2025-05-29', 'YYYY-MM-DD'))
			 	OR
			 	(date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
								when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date('2025-04-08', 'YYYY-MM-DD')
			 		AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date('2025-05-29', 'YYYY-MM-DD'))
			)

			AND coalesce(t.rqst_dpr_yn, 'N') = 'N'

			'''

		sql += '''
		)
		SELECT *
		FROM (
			table cte

	             order by rqst_dt DESC
	                , 
	                    work_order_sort DESC 

	            limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
		'''

		try:
			items = DbUtil.get_rows(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderService.get_work_order_list', ex)
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

