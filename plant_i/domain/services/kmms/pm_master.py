from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PMService():

    def __init__(self):
        return

    def get_pm_master_list(self, keyword, equDept, equLoc, pmDept, pmType, applyYn, cycleType, sDay, eday, isMyTask, isLegal):
        items = []
        dic_param = {'keyword': keyword,'equDept': equDept,'equLoc': equLoc,'pmDept': pmDept,'pmType': pmType,'applyYn': applyYn,'cycleType': cycleType,'sDay': sDay,'eday': eday,'isMyTask': isMyTask,'isLegal': isLegal}

        sql = ''' 
         SELECT 
               a.pm_pk
             , a.pm_no , a.pm_nm 
             , ve.equip_pk
             , ve.equ_code, ve.equ_name
             , ve.import_rank
             , ve.mng_dept_id
             , ve.mng_dept_nm
             , d.id
             , d."Name" as exec_dept 
             , ve.loc_id
             , l.loc_nm as equ_location
             , au.first_name as pm_manager
             , c."Name" as pm_type 
             , c2."Name" as cycle_type 
         FROM pm a
 	        inner join (
                 SELECT e.id AS equip_pk,
                    e."Code" AS equ_code,
                    e."Name" AS equ_name,
                    c."Name" AS import_rank,
                    e.del_yn,
                    case when e.environ_equip_yn = 'Y' then 'Y' else 'N' end environ_equip_yn,
                    e."AssetYN",
                    e."Depart_id" AS mng_dept_id,
                    mng."Name" AS mng_dept_nm,
                    e.loc_pk AS loc_id,
                    l.loc_nm
                   FROM equ e
                     JOIN dept mng ON e."Depart_id" = mng.id
                     JOIN location l ON e.loc_pk = l.id
                     LEFT JOIN code c ON c."Code"::text = e.import_rank::text AND c."CodeGroupCode"::text = 'IMPORT_RANK'::text
                  WHERE e.del_yn::text = 'N'::text
             ) ve on a.equip_pk = ve.equip_pk        
 	        inner join dept d on a.dept_pk  = d.id 	     
            inner join auth_user au on a.pm_user_pk  = au.id  	
 	        inner join "location" l on ve.loc_id = l.id  	        
            left join code c on a.pm_type = c."Code" and c."CodeGroupCode" = 'PM_TYPE'
			left join code c2 on a.cycle_type = c2."Code" and c2."CodeGroupCode" = 'CYCLE_TYPE'
         WHERE 1 = 1
        '''
        if keyword:
            sql += ''' 
            AND a."pm_nm" like CONCAT('%%', %(keyword)s, '%%')
            '''
        if equDept:
            sql += ''' 
            AND ve.mng_dept_id = %(equDept)s
            '''
        if equLoc:
            sql += ''' 
            AND ve.loc_id = %(equLoc)s
            '''
        if pmDept:
            sql += ''' 
            AND a.dept_pk = %(pmDept)s
            '''
        if pmType:
            sql += ''' 
            AND a.pm_type = %(pmType)s
            '''
        if applyYn:
            sql += ''' 
            AND a.use_yn = %(applyYn)s
            '''

        if cycleType:
            sql += ''' 
            AND a.cycle_type = %(cycleType)s
            '''

        # if sDay:
        #     sql += ''' 
        #     AND exc.id = %(sDay)s
        #     '''

        # if eday:
        #     sql += ''' 
        #     AND exc.id = %(eday)s
        #     '''

        if isMyTask:
            sql += ''' 
            AND a."pm_user_pk" = %(isMyTask)s
            '''
        if isLegal:
            sql += ''' 
            AND ve."environ_equip_yn" = %(isLegal)s
            '''
        sql += ''' 
            ORDER BY a.pm_no
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
            raise ex

        return items

    def get_pm_sch_list(self, keyword, equDept, equLoc, pmDept, pmType, applyYn, cycleType, sDay, eday, isMyTask, isLegal):
        items = []
        dic_param = {'keyword': keyword,'equDept': equDept,'equLoc': equLoc,'pmDept': pmDept,'pmType': pmType,'applyYn': applyYn,'cycleType': cycleType,'sDay': sDay,'eday': eday,'isMyTask': isMyTask,'isLegal': isLegal}

        sql = ''' 
         WITH cte AS (
            SELECT                
                t.pm_pk,
                TO_CHAR(t.plan_start_dt, 'YYYYMMDD') AS pm_plan_dt,
                TO_CHAR(t.plan_start_dt, 'YYYY-MM-DD') AS pm_plan_dt_label,
                p.pm_nm,
                p.per_number,
                p.cycle_type,
                ct."Name" AS cycle_type_nm,  -- 변경됨
                e."Code" as equip_cd,
                e."Name" as equip_nm,
                e."environ_equip_yn",
                ed."Name" as dept_nm,
                wd."Name" AS wo_dept_nm,  -- 변경됨
                t.work_order_pk,
                t.work_order_no,
                p.pm_no,
                t.start_dt,
                t.end_dt,
                t.plan_start_dt,
                t.plan_end_dt,
                t.work_title,
                ws."Name" AS wo_status_nm,  -- 변경됨
                ws."Code" AS wo_status,  -- 변경됨
                pt."Code" AS pm_type,  -- 변경됨
                pt."Name" AS pm_type_nm,  -- 변경됨
                fn_user_nm(pmu.first_name, cast(pmu.is_active as varchar)) AS pm_user_nm,  -- 변경됨
                fn_user_nm(wou.first_name, cast(wou.is_active as varchar)) AS wo_user_nm,  -- 변경됨
                t.work_charger_pk,
                t.dept_pk,
        --        fn_get_dept_team_pk(t.dept_pk) AS dept_team_pk,
                t.dept_pk AS dept_team_pk,
                p.dept_pk AS rqst_dept_pk,  -- 변경됨
                ec.equip_category_desc,
                (SELECT "Name" FROM code WHERE "CodeGroupCode" = 'EQUIPMENT_PROCESS' AND "Code" = e.process_cd) AS process_nm,  -- 변경됨
                (SELECT "Name" FROM code WHERE "CodeGroupCode" = 'EQUIP_SYSTEM' AND "Code" = e.system_cd) AS system_nm  -- 변경됨
            FROM work_order t
            INNER JOIN work_order_approval woa ON t.work_order_approval_pk = woa.work_order_approval_pk
            INNER JOIN code ws ON t.wo_status = ws."Code" AND ws."CodeGroupCode" = 'WO_STATUS'  -- 변경됨
            INNER JOIN equ e ON t.equip_pk = e.id  -- 변경됨
            INNER JOIN location l ON e.loc_pk = l.id 
            LEFT JOIN equip_category ec ON e.equip_category_id = ec.equip_category_id
            LEFT OUTER JOIN dept ed ON e."Depart_id"  = ed.id  -- 변경됨
            LEFT OUTER JOIN dept wd ON t.dept_pk = wd.id  -- 변경됨
            LEFT OUTER JOIN dept rd ON t.req_dept_pk = rd.id  -- 변경됨
            LEFT OUTER JOIN auth_user wcu ON t.work_charger_pk = wcu.id  -- 변경됨
            LEFT OUTER JOIN pm p ON t.pm_pk = p.pm_pk
            LEFT OUTER JOIN code ct ON p.cycle_type = ct."Code" AND ct."CodeGroupCode" = 'CYCLE_TYPE'  -- 변경됨
            LEFT OUTER JOIN code pt ON p.pm_type = pt."Code" AND pt."CodeGroupCode" = 'PM_TYPE'  -- 변경됨
            LEFT OUTER JOIN auth_user pmu ON p.pm_user_pk = pmu.id  -- 변경됨
            LEFT OUTER JOIN auth_user wou ON t.WORK_CHARGER_PK = wou.id  -- 변경됨
            LEFT OUTER JOIN code wsc ON t.work_src_cd = wsc."Code" AND wsc."CodeGroupCode" = 'WORK_SRC'  -- 변경됨    
            LEFT OUTER JOIN code wt ON t.wo_type = wt."Code" AND wt."CodeGroupCode" = 'WO_TYPE'  -- 변경됨  
            LEFT OUTER JOIN equ ue ON e.UP_EQUIP_PK = ue.id  -- 변경됨
            LEFT OUTER JOIN code av ON av."Code" = e.first_asset_status AND av."CodeGroupCode" = 'ASSET_VAL_STATUS'  -- 변경됨   
            WHERE 1 = 1
            AND t.site_id = '1'
            --AND t.work_charger_pk = ISNULL(%(isMyTask)s, t.work_charger_pk)                   
            AND t.wo_status IN ('WOS_CM', 'WOS_AP')
            AND t.pm_pk IS NOT NULL
            AND pt."Code" = 'PM_TYPE_TBM'  -- 변경됨
            -- AND (
            --    t.plan_start_dt >= TO_DATE(REPLACE('2024-12-06', '-', ''), 'YYYYMMDD')
            --     AND t.plan_start_dt <= TO_DATE(REPLACE('2025-05-31', '-', ''), 'YYYYMMDD')
            --)
        )
        SELECT *
        FROM (
            TABLE cte
            ORDER BY plan_start_dt ASC
            --LIMIT 30 OFFSET (1-1) * 30
        ) sub
        RIGHT JOIN (SELECT COUNT(*) FROM cte) c(total_rows) ON TRUE
        WHERE total_rows != 0  
         
            '''
        if keyword:
            sql += ''' 
            AND a."pm_nm" like CONCAT('%%', %(keyword)s, '%%')
            '''
        if equDept:
            sql += ''' 
            AND ve.mng_dept_id = %(equDept)s
            '''
        if equLoc:
            sql += ''' 
            AND ve.loc_id = %(equLoc)s
            '''
        if pmDept:
            sql += ''' 
            AND a.dept_pk = %(pmDept)s
            '''
        if pmType:
            sql += ''' 
            AND a.pm_type = %(pmType)s
            '''
        if applyYn:
            sql += ''' 
            AND a.use_yn = %(applyYn)s
            '''

        if cycleType:
            sql += ''' 
            AND a.cycle_type = %(cycleType)s
            '''

        # if sDay:
        #     sql += ''' 
        #     AND exc.id = %(sDay)s
        #     '''

        # if eday:
        #     sql += ''' 
        #     AND exc.id = %(eday)s
        #     '''


        # if isLegal:
        #     sql += ''' 
        #     AND "environ_equip_yn" = %(isLegal)s
        #     '''
        sql += ''' 
            ORDER BY COALESCE(NULLIF(work_order_no, ''), '0')::INTEGER DESC
            '''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
            raise ex

        return items

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
            pl.job_class_pk, jc.nm as job_class_nm,
            pl.work_hr, pl.pm_pk	
        FROM pm_labor pl
	        inner join pm on pm.pm_pk = pl.pm_pk
	        left join job_class jc on pl.job_class_pk = jc.job_class_pk
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
        SELECT pmt.id, pmt.mat_pk, pmt.pm_pk,
	        m."Code" as mat_cd, m."Name" as mat_nm, pmt.amt, m."BasicUnit" as unit
        FROM pm_mtrl pmt
	        inner join pm on pm.pm_pk = pmt.pm_pk
	        left join material m on pmt.mat_pk = m.id
        where pmt.pm_pk = %(id)s
        '''   
        try:
            items = DbUtil.get_rows(sql, {'id':id})     
                
        except Exception as ex:
            LogWriter.add_dblog('error','PMService.get_pm_mtrl_detail', ex)
            raise ex

        return items

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
            LogWriter.add_dblog('error','PMService.get_equip_modal', ex)
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
            fn_user_nm(au."first_name", cast(au.is_active as VARCHAR)) AS user_nm,	-- 담당자
            COUNT(*) OVER() AS total_rows	-- 전체 행 수 추가
        FROM work_order t
            INNER JOIN work_order_approval woa ON t.work_order_approval_pk = woa.work_order_approval_pk
            INNER JOIN pm p ON t.pm_pk = p.pm_pk
            INNER JOIN code ws ON t.wo_status = ws."Code" AND ws."CodeGroupCode" = 'WO_STATUS'
            LEFT JOIN auth_user au ON p.pm_user_pk = au.id
        WHERE t.PM_PK = %(pm_pk)s
            --AND t.site_id = '1'
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
	         , coalesce(wo."_creater_nm", fn_user_nm(cu.first_name, case when cu.is_active then 'Y' else 'N' end)) as changer_nm
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
	        , coalesce(woh.changer_nm, fn_user_nm(cu.first_name, case when cu.is_active then 'Y' else 'N' end)) as changer_nm
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

    def get_work_order_summary(self, work_order_pk):
        items = []
        dic_param = {'work_order_pk':work_order_pk}

        sql = ''' 
              select 		
				t.work_order_pk
				, t.work_order_no
				, t.work_title
				, t.work_text
				, t.work_order_sort
				, t.req_dept_pk
				, rd."Name" as req_dept_nm
				, t.dept_pk
				, wd."Name" as dept_nm
				, t.work_charger_pk
				, wcu."Name" as work_charger_nm
				, mt."Code" as maint_type_cd
				, mt."Name" as maint_type_nm
				, ws."Code" as wo_status
				, ws."Name" as wo_status_nm
				, t.plan_start_dt
				, t.plan_end_dt
				, t.start_dt
				, t.end_dt
				, t.want_dt
				, t.equip_pk
				, e."Code" as equip_cd
				, e."Name" as equip_nm
				, ed.id as equip_dept_pk
				, ed."Name" as equip_dept_nm
				, to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
				, t.pm_pk
				, p.pm_no
				, p.pm_nm
				, pt."Name"                        AS pm_type_nm
				, p.work_text as pm_work_text
				, t.chk_rslt_pk
				, l.loc_nm
				, t.req_info
				, t.wo_type
				, t.rqst_insp_yn
				, t.rqst_dpr_yn
				, wt."Name" as wo_type_nm
				, t.breakdown_dt
				, t.breakdown_hr
				, wsc."Code" as work_src_cd
				, wsc."Name" as work_src_nm
				, t.tot_cost
				, t.mtrl_cost
				, t.labor_cost
				, t.outsourcing_cost
				, t.etc_cost
		        , t.problem_cd
		        , wp."Name" as problem_nm
		        , t.cause_cd
		        , wc."Name" as cause_nm
		        , t.remedy_cd
		        , wr."Name" as remedy_nm
				, prj.proj_cd
				, prj.proj_nm
				, t.wo_file_grp_cd
				, t.pm_req_type
				, t.appr_line
				, t.appr_line_next
				, t.work_order_approval_pk
				, woa.reg_dt
				, woa.rqst_dt
				, woa.rqst_user_nm
				, woa.cancel_dt
				, woa.cancel_user_nm
				, woa.accept_dt
				, woa.appr_dt
				, woa.finish_dt
				, substring(t.appr_line, 1,2) as wo_start_type
				, fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
				, t._created
				, e.environ_equip_yn
				, e."Status" as equip_stauts_cd
				, e.import_rank
				, e.up_equip_pk
				, ue."Name" AS up_equip_name
				, ec.equip_category_id
        		, ec.remark
				, e.equip_class_path
				, e.equip_class_desc
				, av."Name" as first_asset_status
				, av."Code" as first_asset_status_cd
				, fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
				, (select "Name" from code where "CodeGroupCode" = 'EQUIPMENT_PROCESS' and "Code" = e.process_cd) as process_nm
				, (select "Name" from code where "CodeGroupCode" = 'EQUIP_SYSTEM' and "Code" = e.system_cd) as system_nm
				, l2.loc_nm as up_loc_nm
				, woa.cancel_reason
                , t._creater_nm
		from work_order t
			inner join work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
			inner join code mt on t.maint_type_cd = mt."Code" and mt."CodeGroupCode" = 'MAINT_TYPE'
			inner join code ws on t.wo_status = ws."Code" and ws."CodeGroupCode" = 'WO_STATUS'
			inner join equ e on t.equip_pk = e.id
			inner join location l on e.loc_pk = l.id
            left join location l2 on l.up_loc_pk = l2.id
			left join equip_category ec on e.equip_category_id = ec.equip_category_id
			left outer join dept ed on e."Depart_id"  = ed.id
			left outer join dept wd on t.dept_pk = wd.id
			left outer join dept rd on t.req_dept_pk = rd.id
			left outer join user_profile wcu on t.work_charger_pk = wcu."User_id"
            left outer join code wp on t.problem_cd = wp."Code" and wp."CodeGroupCode" = 'PC'
	        left outer join code wc on t.cause_cd = wc."Code" and wc."CodeGroupCode" = 'CC'
	        left outer join code wr on t.remedy_cd = wr."Code" and wr."CodeGroupCode" = 'RC'
			left outer join pm p on t.pm_pk = p.pm_pk
			left outer join code ct on p.cycle_type = ct."Code" and ct."CodeGroupCode" = 'CYCLE_TYPE'
			left outer join code pt on p.pm_type  = pt."Code" and pt."CodeGroupCode" = 'PM_TYPE'
			left outer join user_profile pmu on p.pm_user_pk = pmu."User_id"
			left outer join user_profile wou on t.work_charger_pk = wou."User_id"
			left outer join code wsc on t.work_src_cd = wsc."Code" and wsc."CodeGroupCode" = 'WORK_SRC'
			left outer join project prj on t.proj_cd = prj.proj_cd
			left outer join user_profile woarqstu on woa.rqst_user_pk = woarqstu."User_id"			
			left outer join code wt on t.wo_type = wt."Code" and wt."CodeGroupCode" = 'WO_TYPE'
			left outer join equ ue on e.UP_EQUIP_PK  = ue.id
			left outer join code av on av."Code" = e.first_asset_status and av."CodeGroupCode" = 'ASSET_VAL_STATUS'

		where 1 = 1
		AND t.work_order_pk =  %(work_order_pk)s
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



