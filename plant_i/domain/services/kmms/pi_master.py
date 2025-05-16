from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PIService():

    def __init__(self):
        return

    #점검마스터조회
    #modified by choi : 2025/05/13  파라미터를 dictionary에 넣어서 전달한다
    #def findAll(self, keyword, equDept, equLoc, pmDept, isMyTask, isLegal,useYn,cycleTypeCd, chkMastNo,startDate,endDate):
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
					d.dept_pk = %(deptPk)s
					OR
					d.dept_pk In (select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
				)
            '''
		
        if equipDeptPk and equipDeptPk > 0 :
            sql += ''' AND (
					ed.dept_pk = %(equipDeptPk)s
					OR
					ed.dept_pk In (select dept_pk from v_dept_path where %(equipDeptPk)s = path_info_pk)
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
            sql += '''  AND cu.user_pk = %(chkUserPk)s
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
            AND date(coalesce(t.next_chk_date,cast(fn_get_regular_day(t.sched_start_date::date, t.sched_start_date::date, t.per_number, ct.code_cd) as date)))
				BETWEEN to_date(%(startDate)s, 'YYYY-MM-DD') AND to_date(%(endDate)s, 'YYYY-MM-DD')
            '''

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

    # 점검마스터 max 점검번호를 가져온다
    def selectMaxEquipChkMastNo(self):
        sql = ''' 
            select coalesce(MAX((select chk_mast_no
				from (
				    SELECT max(cast(chk_mast_no as integer)) as chk_mast_no
				    FROM cm_equip_chk_mast
				    WHERE (chk_mast_no ~ E'^[0-9]+$') = true
				    --AND site_id = %(siteId}
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



    #==================점검설비관련====================




    #==================점검항목관련====================

