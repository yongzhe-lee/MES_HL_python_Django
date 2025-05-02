from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PIService():

    def __init__(self):
        return

    #점검조회
    def findAll(self, keyword, equDept, equLoc, pmDept, isMyTask, isLegal,useYn,cycleTypeCd, chkMastNo,startDate,endDate):
        items = []
        dic_param = {'keyword': keyword,'equDept': equDept,'equLoc': equLoc,'pmDept': pmDept,'isMyTask': isMyTask,'isLegal': isLegal,'useYn':useYn, 'cycleTypeCd':cycleTypeCd, 'chkMastNo':chkMastNo,'startDate':startDate,'endDate':endDate}

        sql = ''' 
         select t.chk_mast_pk
	            , t.chk_mast_nm
	            , t.chk_mast_no
	            , d.dept_pk
	            , d.dept_nm
	            , t.chk_user_pk
	            , fn_user_nm(cu.user_nm, cu.del_yn) as chk_user_nm
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
			--INNER JOIN cm_dept d ON t.dept_pk = d.dept_pk
			--INNER JOIN cm_chk_equip ce on t.chk_mast_pk = ce.chk_mast_pk
			--INNER JOIN cm_equipment e on ce.equip_pk = e.equip_pk
            LEFT OUTER JOIN cm_dept d ON t.dept_pk = d.dept_pk
			LEFT OUTER JOIN cm_chk_equip ce on t.chk_mast_pk = ce.chk_mast_pk
			LEFT OUTER JOIN cm_equipment e on ce.equip_pk = e.equip_pk
			LEFT OUTER JOIN cm_user_info cu on t.chk_user_pk = cu.user_pk
			LEFT OUTER JOIN cm_base_code ct ON t.cycle_type = ct.code_cd AND ct.code_grp_cd = 'CYCLE_TYPE'
			LEFT OUTER JOIN cm_equip_chk_item eci on t.chk_mast_pk = eci.chk_mast_pk
			LEFT OUTER JOIN cm_location l on e.loc_pk = l.loc_pk
			LEFT OUTER JOIN cm_dept ed on e.dept_pk = ed.dept_pk
		WHERE  t.del_yn = 'N'
        '''

        '''
        <if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(useYn)">
    		AND t.use_yn = #{useYn}
    	</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(searchText)">
			AND (
				UPPER(t.chk_mast_nm) LIKE CONCAT('%',UPPER(#{searchText}),'%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(#{searchText}),'%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(#{searchText}),'%')
   			)
		</if>
		<if test="deptPk != null and deptPk > 0 ">
			<![CDATA[
				AND (
					d.dept_pk = #{deptPk}
					OR
					d.dept_pk In (select dept_pk from v_dept_path where #{deptPk} = path_info_pk)
				)
			]]>
		</if>
		<if test="equipDeptPk != null and equipDeptPk > 0 ">
			<![CDATA[
				AND (
					ed.dept_pk = #{equipDeptPk}
					OR
					ed.dept_pk In (select dept_pk from v_dept_path where #{equipDeptPk} = path_info_pk)
				)
			]]>
		</if>
		<if test="locPk != null and locPk > 0 ">
			<![CDATA[
				AND (
					l.loc_pk = #{locPk}
					OR
					l.loc_pk In (select loc_pk from (select * from fn_get_loc_path(#{siteId})) x where #{locPk} = path_info_pk)
				)
			]]>
		</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(cycleTypeCd)">
			AND ct.code_cd = #{cycleTypeCd}
		</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(environEquipYn)">
			AND e.environ_equip_yn = #{environEquipYn}
		</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(chkMastNo)">
			AND t.chk_mast_no = #{chkMastNo}
		</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(chkMastNm)">
			AND t.chk_mast_nm = #{chkMastNm}
		</if>
		<if test="chkUserPk != null and chkUserPk > 0 ">
			AND cu.user_pk = #{chkUserPk}
		</if>
		<if test="equipPk != null and equipPk > 0 ">
			AND e.equip_pk = #{equipPk}
		</if>
		<if test="chkMastPk != null and chkMastPk > 0 ">
			AND t.chk_mast_pk = #{chkMastPk}
		</if>
		<if test="chkMastPkNot != null and chkMastPkNot > 0 ">
			<![CDATA[
				AND t.chk_mast_pk <> #{chkMastPkNot}
			]]>
		</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(lastChkDateFrom) and @com.yullin.swing.common.SwingUtil@isNotEmpty(lastChkDateTo)">
			<![CDATA[
				AND date(t.last_chk_date) BETWEEN to_date(#{lastChkDateFrom}, 'YYYY-MM-DD') AND to_date(#{lastChkDateTo}, 'YYYY-MM-DD')
			]]>
		</if>
		<if test="@com.yullin.swing.common.SwingUtil@isNotEmpty(startDate) and @com.yullin.swing.common.SwingUtil@isNotEmpty(endDate)">
			<![CDATA[
				AND date(coalesce(t.next_chk_date,cast(fn_get_regular_day(t.sched_start_date::date, t.sched_start_date::date, t.per_number, ct.code_cd) as date)))
					BETWEEN to_date(#{startDate}, 'YYYY-MM-DD') AND to_date(#{endDate}, 'YYYY-MM-DD')
			]]>
		</if>
        '''
        
        # if keyword:
        #     sql += ''' 
        #     AND a."pm_nm" like CONCAT('%%', %(keyword)s, '%%')
        #     '''
        # if equDept:
        #     sql += ''' 
        #     AND mng.id = %(equDept)s
        #     '''
        # if equLoc:
        #     sql += ''' 
        #     AND l.id = %(equLoc)s
        #     '''
        # if pmDept:
        #     sql += ''' 
        #     AND exc.id = %(pmDept)s
        #     '''
        # if isMyTask:
        #     sql += ''' 
        #     AND a."pm_user_pk" = %(isMyTask)s
        #     '''
        # if isLegal:
        #     sql += ''' 
        #     AND e."environ_equip_yn" = %(isLegal)s
        #     '''
        # sql += ''' 
        #     ORDER BY a.pm_no
        #     '''



        sql +='''
            GROUP BY t.chk_mast_pk
            , t.chk_mast_nm
            , t.chk_mast_no
            , d.dept_pk
            , d.dept_nm
            , t.chk_user_pk
            , cu.user_nm
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


        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.get_pm_master_list', ex)
            raise ex

        return items

    # max 점검번호를 가져온다
    def selectMaxEquipChkMastNo(self):
        sql = ''' 
            select coalesce(MAX((select chk_mast_no
				from (
				    SELECT max(cast(chk_mast_no as integer)) as chk_mast_no
				    FROM cm_equip_chk_mast
				    WHERE (chk_mast_no ~ E'^[0-9]+$') = true
				    --AND site_id = #{siteId}
				) as sub_table
			)) + 1, '1') as max_no
			from cm_equip_chk_mast
        '''

        try:
            dc = {}
            result = DbUtil.get_row(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error', 'PMService.selectMaxEquipChkMastNo', ex)
            raise ex

        return result


    def get_pm_master_detail(self, id):
        sql = ''' 
        SELECT 
               a.pm_pk
             , a.pm_no , a.pm_nm 
             , e.id as equip_pk
             , e."Code" as equ_code, e."Name" as equ_name
             , e.import_rank
             , e."Depart_id" as mng_dept_id
             , mng."Name" as manage_dept
             , exc.id
             , exc."Name" as exec_dept          
             , l.loc_nm as equ_location
             , au.id as pm_manager
             , a.pm_type 
             , a.cycle_type 
         FROM pm a
 	        inner join equ e on a.equip_pk = e.id 
 	        inner join dept mng on e."Depart_id"  = mng.id
 	        inner join dept exc on a.dept_pk  = exc.id 	     
            inner join auth_user au on a.pm_user_pk  = au.id  	
 	        left join "location" l on e.loc_pk = l.id  	        
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



