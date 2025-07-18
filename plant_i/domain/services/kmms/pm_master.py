from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PMService():

    def __init__(self):
        return

    def get_pm_master_list(self, keyword, equDept, equLoc, pmDept, pmType, applyYn, cycleType, sDay, eDay, isMyTask, isLegal):
        tems = []
        dic_param = {'keyword': keyword,'equDept': equDept,'equLoc': equLoc,'pmDept': pmDept,'pmType': pmType,'applyYn': applyYn,'cycleType': cycleType,'sDay': sDay,'eDay': eDay,'isMyTask': isMyTask,'isLegal': isLegal}

        sql = '''
         with cte as (
            SELECT t.pm_pk
                   , t.pm_no
                   , t.pm_nm
                   , e.equip_pk
                   , e.equip_cd
                   , e.equip_nm
                   , e.import_rank_pk
			       , ir.import_rank_cd 				   AS import_rank_nm
                   , d.id
                   , d."Name"
                   , pu."User_id"                        AS pm_user_pk
                   , cm_fn_user_nm(pu."Name", pu.del_yn)                        AS pm_user_nm
                   , (case when (t.pm_no ~ E'^[0-9]+$') = true then cast(t.pm_no as integer) else 999999 end) as pm_no_sort
                   , pt.code_cd                        AS pm_type_cd
                   , pt.code_nm                        AS pm_type_nm
                   , ct.code_cd                        AS cycle_type_cd
                   , ct.code_nm                        AS cycle_type_nm
                   , Concat(t.per_number, ct.code_dsc) AS cycle_display_nm
                   , t.per_number
                   , t.last_work_dt
                   , t.sched_start_dt
                   , t.first_work_dt
	               , t.next_chk_date
                   , t.work_text
                   , t.work_expect_hr
                   , t.use_yn
                   , t.del_yn
                   , t.insert_ts
                   , t.inserter_id
                   , t.inserter_nm
                   , t.update_ts
                   , t.updater_id
                   , t.updater_nm
		           , eqd."Name" as mdept_nm
			       , l.loc_nm
		           , ec.equip_category_desc
				    , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
				    , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm

		    FROM   cm_pm t
		           INNER JOIN cm_equipment e ON t.equip_pk = e.equip_pk
		           INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
		           LEFT OUTER JOIN dept d ON t.dept_pk = d.id
		           LEFT OUTER JOIN cm_base_code pt ON t.pm_type = pt.code_cd AND pt.code_grp_cd = 'PM_TYPE'
		           LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
		           LEFT OUTER JOIN user_profile pu ON t.pm_user_pk = pu."User_id"
		           LEFT OUTER JOIN dept eqd ON e.dept_pk = eqd.id
			       LEFT OUTER JOIN cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
				    left outer join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
		    WHERE  t.del_yn = 'N'
    		    AND t.use_yn = 'Y'
            '''
        if keyword:
            sql += '''
            AND (
				UPPER(t.pm_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR
				UPPER(t.pm_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
   			)
            '''
        if cycleType:
            sql += '''
            AND ct.code_cd = %(cycleType)s
            '''
        if pmType:
            sql += '''
            AND pt.code_cd =  %(pmType)s
            '''
        if isLegal:
            sql += '''
            AND e.environ_equip_yn =  %(isLegal)s
            '''
        if equDept: #관리부서
            sql += '''
            AND (
					eqd.id = %(equDept)s
					OR
					eqd.id In (select dept_pk from cm_v_dept_path where %(equDept)s = path_info_pk)
				)
            '''
        if pmDept: #실행부서
            sql += '''
            AND (
					d.id = %(pmDept)s
					OR
					d.id In (select dept_pk from cm_v_dept_path where %(pmDept)s = path_info_pk)
				)
            '''
        if equLoc: #설비위치
            sql += '''
            AND (
					l.loc_pk = %(equLoc)s
				)
            '''
        if isMyTask: #나의 담당건
            sql += '''
            AND pu."User_id" = %(isMyTask)s
            '''
        if applyYn:
            sql += '''
            AND t.use_yn = %(applyYn)s
            '''
        if sDay and eDay:
            sql += '''
            AND date(coalesce(t.next_chk_date,cast(cm_fn_get_regular_day(t.sched_start_dt::date, t.sched_start_dt::date, t.per_number, ct.code_cd) as date)))
					BETWEEN to_date(%(sDay)s, 'YYYY-MM-DD') AND to_date(%(eDay)s, 'YYYY-MM-DD')
            '''

        sql += '''
		)
        SELECT *
            , CAST(cm_fn_get_work_day(to_char(cm_fn_get_last_pm_date(sub.pm_pk), 'YYYY-MM-DD')) AS timestamp) as next_chk_date

            , (select count(*)
                 from cm_work_order wo
 				where wo.pm_pk = sub.pm_pk
			   ) as wo_count

		FROM (
			table cte  order by pm_no_sort ASC
		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
            raise ex

        return items

    def findAllPm(self, keyword, equDept, equLoc, pmDept, pmType, woStatus, sDay, eDay, equCategory, isMyTask, isLegal):
        items = []
        dic_param = {'keyword': keyword,'equDept': equDept,'equLoc': equLoc,'pmDept': pmDept,'pmType': pmType, 'woStatus': woStatus, 'sDay': sDay,'eDay': eDay,'equCategory': equCategory, 'isMyTask': isMyTask,'isLegal': isLegal}

        sql = '''
        with cte as (

		        select t.pm_pk
			        , to_char(t.plan_start_dt, 'YYYYMMDD') as pm_plan_dt
			        , to_char(t.plan_start_dt, 'YYYY-MM-DD') as pm_plan_dt_label
			        , p.pm_nm
			        , p.per_number
			        , p.cycle_type
			        , ct.code_nm as cycle_type_nm
			        , e.equip_cd
			        , e.equip_nm
			        , ed."Name"
			        , wd."Name"   AS wo_dept_nm
			        , t.work_order_pk
			        , t.work_order_no
			        , p.pm_no
			        , t.start_dt
			        , t.end_dt
			        , t.plan_start_dt
			        , t.plan_end_dt
			        , t.work_title
			        , ws.code_nm as wo_status_nm
			        , ws.code_cd as wo_status
			        , pt.code_cd as pm_type
			        , pt.code_nm as pm_type_nm
			        , cm_fn_user_nm(pmu."Name", pmu.del_yn) as pm_user_nm
                    , cm_fn_user_nm(wou."Name", wou.del_yn) as wo_user_nm
                    , t.work_charger_pk
                    , t.dept_pk
                    , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
                    , woarqstd.id as rqst_dept_pk
			        , ec.equip_category_desc
			        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
			        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm

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
				UPPER(p.pm_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(p.pm_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
			)
            '''
        if equDept:
            sql += '''
            AND (
					ed.id = %(equDept)s
					OR
					ed.id In (select dept_pk from cm_v_dept_path where %(equDept)s = path_info_pk)
				)
            '''
        if equLoc:
            sql += '''
            AND (
					l.loc_pk = %(equLoc)s
                    OR
                    l.loc_pk IN ( select loc_pk from (select * from cm_fn_get_loc_path(1)) x where %(equLoc)s = path_info_pk)
				)
            '''
        if pmDept:
            sql += '''
            AND (
					wd.id = %(pmDept)s
					OR
					wd.id In (select dept_pk from cm_v_dept_path where %(pmDept)s = path_info_pk)
				)
            '''
        if pmType:
            sql += '''
                AND pt.code_cd = %(pmType)s
            '''

        finalStatuses = []
        if woStatus:
            woStatusList = [s.strip() for s in woStatus.split(',') if s.strip()]
            finalStatuses = [f'{s.replace("0", "")}' for s in woStatusList]
            formattedStatus = ', '.join(f"'{status}'" for status in finalStatuses)
            sql += f'''
                AND t.wo_status IN ( {formattedStatus} )
            '''
        else:
            sql += '''
                AND t.wo_status IN ( 'WOS_CM', 'WOS_AP', 'WOS_CL' )
            '''
        if equCategory:
            sql += '''
                AND ec.equip_category_id = %(equCategory)s
            '''
        if sDay and eDay:
            sql += '''
			AND (
				t.plan_start_dt >= to_date(REPLACE(%(sDay)s, '-', ''), 'YYYYMMDD') AND t.plan_start_dt <= to_date(REPLACE(%(eDay)s, '-', ''), 'YYYYMMDD')
			)
            '''
        if isMyTask:
            sql += '''
            AND t.work_charger_pk = %(isMyTask)s
            '''
        if isLegal:
            sql += '''
            AND e.environ_equip_yn =  %(isLegal)s
            '''

        sql += '''
			AND t.pm_pk IS NOT NULL
                )
		    SELECT *
		    FROM (
			    table cte order by plan_start_dt ASC
		    ) sub
		    RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		    WHERE total_rows != 0

            '''

        sql += '''
            order by work_order_no desc
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.findAllPm', ex)
            raise ex

        return items

    def pm_work_findAll(self, keyword, srchPmNo, srchWoNo, pmType, equDept, pmDept, sDay, eDay, srchEquCategory, isNotFinished, isLegal):
        items = []
        dic_param = {'keyword': keyword,'srchPmNo': srchPmNo,'srchWoNo': srchWoNo, 'pmType': pmType,'equDept': equDept,'pmDept': pmDept,'sDay': sDay,'eDay': eDay, 'srchEquCategory': srchEquCategory,'isNotFinished': isNotFinished,'isLegal': isLegal}

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
            --				, cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
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
				UPPER(p.pm_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(p.pm_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
			)
            '''
        if srchPmNo:
            sql += '''
            AND p.pm_no = %(srchPmNo)s
            '''
        if srchWoNo:
            sql += '''
            AND t.work_order_no = %(srchWoNo)s
            '''
        if pmType:
            sql += '''
            AND pt.code_cd = %(pmType)s
            '''
        if equDept:
            sql += '''
            AND (
				ed.id = %(equDept)s
				OR
				ed.id IN ( select dept_pk from cm_v_dept_path where %(equDept)s = path_info_pk)
			)
            '''
        if pmDept:
            sql += '''
            AND (
				wd.id = %(pmDept)s
				OR
				wd.id IN ( select dept_pk from cm_v_dept_path where %(pmDept)s = path_info_pk)
			)
            '''
        if sDay and eDay:
            sql += '''
            AND (
				t.plan_start_dt >= to_date(REPLACE(%(sDay)s, '-', ''), 'YYYYMMDD') AND t.plan_start_dt <= to_date(REPLACE(%(eDay)s, '-', ''), 'YYYYMMDD')
			)
            '''
        if srchEquCategory:
            sql += '''
            AND ec.equip_category_id = %(srchEquCategory)s
            '''
        if isNotFinished == 'Y':
            sql += '''
            AND t.wo_status NOT IN ('WOS_RW', 'WOS_DL', 'WOS_CM', 'WOS_CL')
            '''
        if isLegal == 'Y':
            sql += '''
            AND e.environ_equip_yn = %(isLegal)s
            '''

        sql += '''
            )
		    SELECT *
		    FROM ( table cte order by plan_start_dt ASC  ) sub
		    RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		    WHERE total_rows != 0
            order by pm_no desc, cast(work_order_no as INTEGER) desc
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.pm_work_findAll', ex)
            raise ex

        return items

    def get_pm_master_findOne(self, id):
        sql = '''
                SELECT t.pm_pk
               , t.pm_no
               , t.pm_nm
               , e.equip_pk
               , e.equip_cd
               , e.equip_nm
               , d.id
               , d."Name"
               , pu."User_id"                        AS pm_user_pk
               , cm_fn_user_nm(pu."Name", pu.del_yn)                        AS pm_user_nm
               , (case when (t.pm_no ~ E'^[0-9]+$') = true then cast(t.pm_no as integer) else 999999 end) as pm_no_sort
               , pt.code_cd                        AS pm_type_cd
               , pt.code_nm                        AS pm_type_nm
               , ct.code_cd                        AS cycle_type_cd
               , ct.code_nm                        AS cycle_type_nm
               , Concat(t.per_number, ct.code_dsc) AS cycle_display_nm
               , t.per_number
               , t.last_work_dt
               , t.sched_start_dt
               , t.first_work_dt

		        , coalesce(t.next_chk_date
       			        , CAST(cm_fn_get_work_day(to_char(cm_fn_get_last_pm_date(t.pm_pk), 'YYYY-MM-DD')) AS timestamp)) as next_chk_date

               , cm_fn_get_work_day(to_char(cm_fn_get_last_pm_date(t.pm_pk), 'YYYY-MM-DD')) as next_chk_date
               , t.work_text
               , t.work_expect_hr
               , t.use_yn
               , t.del_yn
               , t.insert_ts
               , t.inserter_id
               , t.inserter_nm
               , t.update_ts
               , t.updater_id
               , t.updater_nm
               , t.dept_pk

        FROM   cm_pm t
               INNER JOIN cm_equipment e ON t.equip_pk = e.equip_pk
               INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
               LEFT OUTER JOIN dept d ON t.dept_pk = d.id
               LEFT OUTER JOIN cm_base_code pt ON t.pm_type = pt.code_cd AND pt.code_grp_cd = 'PM_TYPE'
               LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
               LEFT OUTER JOIN user_profile pu ON t.pm_user_pk = pu."User_id"
               LEFT OUTER JOIN dept eqd ON e.dept_pk = eqd.id
	           LEFT OUTER JOIN cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
		        left outer join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
        WHERE  t.del_yn = 'N'

        AND t.pm_pk = %(id)s

        '''
        data = {}
        try:
            items = DbUtil.get_rows(sql, {'id':id})
            if len(items)>0:
                data = items[0]
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_master_detail', ex)
            raise ex

        return data

    def get_pm_master_detail(self, id):
        sql = '''
        SELECT
               a.pm_pk
             , a.pm_no , a.pm_nm
             , e.id as equip_pk
             , e."Code" as equ_code, e."Name" as equ_name
             , c."Name" as import_rank
             , e."Depart_id" as mng_dept_id
             , mng."Name" as manage_dept
             , exc.id
             , exc."Name" as exec_dept
             , l.loc_nm as equ_location
             , au.id as pm_manager
             , a.work_expect_hr
             , a.pm_type
             , a.cycle_type
             , c2."Name" as "Status"
             , a.per_number
             , a.work_text
             , case when environ_equip_yn = 'Y' then 'Y' else 'N' end environ_equip_yn
             , a.sched_start_dt
         FROM pm a
 	        inner join equ e on a.equip_pk = e.id
 	        inner join dept mng on e."Depart_id"  = mng.id
 	        inner join dept exc on a.dept_pk  = exc.id
            inner join auth_user au on a.pm_user_pk  = au.id
 	        left join "location" l on e.loc_pk = l.id
            left join code c on e.import_rank = c."Code" and c."CodeGroupCode" = 'IMPORT_RANK'
            left join code c2 on e."Status" = c2."Code" and c2."CodeGroupCode" = 'EQU_STATUS'
         WHERE
            a.pm_pk = %(id)s
        '''
        data = {}
        try:
            items = DbUtil.get_rows(sql, {'id':id})
            if len(items)>0:
                data = items[0]
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_master_detail', ex)
            raise ex

        return data

    def get_pm_labor_detail(self, id):
        sql = '''
        SELECT pl.id,
            pl.job_class_pk, jc.job_class_nm,
            pl.work_hr, pl.pm_pk
        FROM cm_pm_labor pl
            inner join cm_pm on cm_pm.pm_pk = pl.pm_pk
            left join cm_job_class jc on pl.job_class_pk = jc.job_class_pk    
        where pl.pm_pk = %(id)s
        '''
        try:
            items = DbUtil.get_rows(sql, {'id':id})

        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_labor_detail', ex)
            raise ex

        return items

    def get_pm_mtrl_detail(self, id):
        sql = '''
        SELECT pmt.id, pmt.mtrl_pk as mat_pk, pmt.pm_pk,
            m.mtrl_cd as mat_cd, m.mtrl_nm as mat_nm, pmt.amt, cbc.code_nm as unit
        FROM cm_pm_mtrl pmt
            inner join cm_pm on cm_pm.pm_pk = pmt.pm_pk
            left join cm_material m on pmt.mtrl_pk = m.mtrl_pk
            left join cm_base_code cbc on m.amt_unit_pk = cbc.code_pk
        where pmt.pm_pk = %(id)s
        '''
        try:
            items = DbUtil.get_rows(sql, {'id':id})

        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_mtrl_detail', ex)
            raise ex

        return items

    # def get_pm_modal(self, keyword, dept_pk):
    #     items = []
    #     dic_param = {'keyword':keyword, 'dept_pk':dept_pk}

    #     sql = '''
    #     select * from pm
	   #      left join auth_user au on pm."_creater_id" = au.id
	   #      left join dept d ON pm."dept_pk" = d.id
	   #      left join equ e on pm.equip_pk = e.id
    #     where 1=1
    #     '''

    #     if keyword:
    #         sql+='''
    #             AND (UPPER(pm."pm_nm") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
    #                 or UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
    #     	        or UPPER(e."Code") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
    #     )
    #         '''
    #     if dept_pk:
    #         sql+='''
    #         AND UPPER(d.id) LIKE CONCAT('%%',UPPER(%(dept_pk)s),'%%')
    #         '''

    #     try:
    #         items = DbUtil.get_rows(sql, dic_param)
    #     except Exception as ex:
    #         LogWriter.add_dblog('error','PMService.get_equip_modal', ex)
    #         raise ex

    #     return items

    def get_pm_findSel(self, searchText, deptPk, pmUserPk):
        items = []
        dic_param = {'searchText':searchText, 'deptPk':deptPk, 'pmUserPk': pmUserPk}

        sql = '''
        /* findAll [pm-mapper.xml] */
        with cte as (
        SELECT t.pm_pk
               , t.pm_no
               , t.pm_nm
               , e.equip_pk
               , e.equip_cd
               , e.equip_nm
               , e.import_rank_pk
			   , ir.import_rank_cd 				   AS import_rank_nm
               , d.id
               , d."Name"
               , pu."User_id"                        AS pm_user_pk
               , cm_fn_user_nm(pu."Name", pu.del_yn)                        AS pm_user_nm
               , (case when (t.pm_no ~ E'^[0-9]+$') = true then cast(t.pm_no as integer) else 999999 end) as pm_no_sort
               , pt.code_cd                        AS pm_type_cd
               , pt.code_nm                        AS pm_type_nm
               , ct.code_cd                        AS cycle_type_cd
               , ct.code_nm                        AS cycle_type_nm
               , Concat(t.per_number, ct.code_dsc) AS cycle_display_nm
               , t.per_number
               , t.last_work_dt
               , t.sched_start_dt
               , t.first_work_dt
	           , t.next_chk_date
               , t.work_text
               , t.work_expect_hr
               , t.use_yn
               , t.del_yn
               , t.insert_ts
               , t.inserter_id
               , t.inserter_nm
               , t.update_ts
               , t.updater_id
               , t.updater_nm
		       , eqd."Name" as mdept_nm
			   , l.loc_nm
		       , ec.equip_category_desc
				, (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
				, (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm

		FROM   cm_pm t
		       INNER JOIN cm_equipment e ON t.equip_pk = e.equip_pk
		       INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
		       LEFT OUTER JOIN dept d ON t.dept_pk = d.id
		       LEFT OUTER JOIN cm_base_code pt ON t.pm_type = pt.code_cd AND pt.code_grp_cd = 'PM_TYPE'
		       LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
		       LEFT OUTER JOIN user_profile pu ON t.pm_user_pk = pu."User_id"
		       LEFT OUTER JOIN dept eqd ON e.dept_pk = eqd.id
			   LEFT OUTER JOIN cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
				left outer join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
		WHERE  t.del_yn = 'N'
    		AND t.use_yn = 'Y'
            '''

        if searchText:
            sql += '''
			AND (
				UPPER(t.pm_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
				OR
				UPPER(t.pm_no) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
   			)
               '''

        if deptPk:
            sql += '''

				AND (
					d.id = %(deptPk)s
					OR
					d.id In (select dept_pk from cm_v_dept_path where 1 = path_info_pk)
				)
               '''

        sql += '''
		)
        SELECT *
            , CAST(cm_fn_get_work_day(to_char(cm_fn_get_last_pm_date(sub.pm_pk), 'YYYY-MM-DD')) AS timestamp) as next_chk_date

            , (select count(*)
                 from cm_work_order wo
 				where wo.pm_pk = sub.pm_pk
			   ) as wo_count

		FROM (
			table cte
		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0

        '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_findSel', ex)
            raise ex

        return items

    def get_pm_wo(self, pm_pk):
        items = []
        dic_param = {'pm_pk':pm_pk}

        sql = '''
        SELECT
            t.work_order_no,				-- WO 번호
            woa.reg_dt, 					-- WO 생성일
            ws."Code" AS wo_status_cd,
            ws."Name" AS wo_status_nm,  	-- WO 상태
            t.plan_start_dt, 				-- 작업계획일
            t.end_dt, 						-- 작업완료일
            p.pm_user_pk,
            cm_fn_user_nm(au."first_name", cast(au.is_active as VARCHAR)) AS user_nm,	-- 담당자
            COUNT(*) OVER() AS total_rows	-- 전체 행 수 추가
        FROM work_order t
            INNER JOIN work_order_approval woa ON t.work_order_approval_pk = woa.work_order_approval_pk
            INNER JOIN pm p ON t.pm_pk = p.pm_pk
            INNER JOIN code ws ON t.wo_status = ws."Code" AND ws."CodeGroupCode" = 'WO_STATUS'
            LEFT JOIN auth_user au ON p.pm_user_pk = au.id
        WHERE t.PM_PK = %(pm_pk)s
        ORDER BY t.end_dt DESC	-- 작업 완료일 정렬
        ;
        '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_wo', ex)
            raise ex

        return items

    def get_work_order_hist(self, work_order_pk):
        items = []
        dic_param = {'work_order_pk':work_order_pk}

        sql = '''
        SELECT 1 as work_order_hist_pk
	         , wo.work_order_pk
	         , wo.work_order_no
	         , '작성(생성)' as after_status_nm
	         , to_char(wo."_created", 'YYYY-MM-DD')  as change_ts
	         , coalesce(wo."_creater_nm", cm_fn_user_nm(cu.first_name, case when cu.is_active then 'Y' else 'N' end)) as changer_nm
	         , '' AS change_reason
        from work_order wo
        inner join auth_user cu on wo."_creater_id" = cu.id
        where wo.work_order_pk = %(work_order_pk)s
        UNION ALL
        SELECT woh.id as work_order_hist_pk
	        , woh.work_order_pk
	        , wo.work_order_no
	        , aws."Name" as after_status_nm
	        , to_char(woh.change_ts, 'YYYY-MM-DD') as change_ts
	        , coalesce(woh.changer_nm, cm_fn_user_nm(cu.first_name, case when cu.is_active then 'Y' else 'N' end)) as changer_nm
	        , woh.change_reason
        from work_order_hist woh
        inner join code aws on woh.after_status = aws."Code" and aws."CodeGroupCode" = 'WO_STATUS'
        inner join auth_user cu on woh.changer_pk = cu.id
        inner join work_order wo on woh.work_order_pk = wo.work_order_pk
        where woh.work_order_pk = %(work_order_pk)s
        order by change_ts desc, work_order_hist_pk desc
        ;
        '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_wo', ex)
            raise ex

        return items

    def pm_work_findOne(self, work_order_pk):
        items = []
        dic_param = {'work_order_pk':work_order_pk}

        sql = '''
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
		    left outer join user_profile woarqstu on woa.rqst_user_pk = woarqstu."User_id"
		    left outer join dept woarqstd on woarqstu."Depart_id" = woarqstd.id
		    left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
		    left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
		    left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
		    left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
		    left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
		    left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
	    where 1 = 1

	    AND t.work_order_pk = %(work_order_pk)s
            ;
        '''

        try:
            items = DbUtil.get_row(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_wo', ex)
            raise ex

        return items

    def get_job_class_list(self):
        items = []
        sql = '''
            SELECT job_class_pk, job_class_cd, job_class_nm, wage_cost
            FROM cm_job_class
            WHERE 1 = 1
        '''
        sql += '''
            ORDER BY job_class_nm
            '''

        try:
            items = DbUtil.get_rows(sql)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
            raise ex

        return items

    def do_pm_schedule(self, site_id=None, sche_type=None, start_date=None, end_date=None, pm_chk_lists=None):
        if pm_chk_lists is None:
            pm_chk_lists = []  # ✅ None 방지 (기본값 추가)

        exec_cnt = 0
        for pm_pk in pm_chk_lists:
            try:
                pm_pk = int(pm_pk)
            except ValueError:
                LogWriter.add_dblog('error', 'make_pm_schedule', f"Invalid pm_pk: {pm_pk}")
                continue

            dc = {
                'scheType': sche_type,
                'startDate': start_date,
                'endDate': end_date,
                'siteId': site_id,
                'pmPk': pm_pk
            }

            try:
                result = DbUtil.call_function('fn_make_schedule_pm', dc)
                return_value = result.get('p_exec_cnt') if result else None

                if return_value is not None:
                    exec_cnt += int(return_value)

            except Exception as ex:
                LogWriter.add_dblog('error', 'make_pm_schedule', ex)
                raise ex

        return exec_cnt

    def executeMakeSchedulePm(self, sche_type, pm_pk_list, start_date, end_date):
        sql = '''
                select cm_fn_make_schedule_pm(%(sche_type)s
                , %(pm_pk)s
                , to_date(%(start_date)s, 'YYYYMMDD')
                , to_date(%(end_date)s, 'YYYYMMDD')
                , '1')
        '''
        results = []
        try:
            for pm_pk in pm_pk_list:
                params = {
                    'sche_type': sche_type,
                    'pm_pk': pm_pk,
                    'start_date': start_date.replace('-', ''),
                    'end_date': end_date.replace('-', '')
                }
                items = DbUtil.get_rows(sql, params)
                if items:
                    results.append(items[0])
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.executeMakeSchedulePm', ex)
            raise ex

        return results
