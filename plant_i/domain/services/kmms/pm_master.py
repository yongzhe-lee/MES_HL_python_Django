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
             , a.pm_no , a.pm_name 
             , ve.equ_id
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
                 SELECT e.id AS equ_id,
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
             ) ve on a.equ_id = ve.equ_id        
 	        inner join dept d on a.dept_id  = d.id 	     
            inner join auth_user au on a.pm_user_id  = au.id  	
 	        inner join "location" l on ve.loc_id = l.id  	        
            left join code c on a.pm_type = c."Code" and c."CodeGroupCode" = 'PM_TYPE'
			left join code c2 on a.cycle_type = c2."Code" and c2."CodeGroupCode" = 'CYCLE_TYPE'
         WHERE 1 = 1
        '''
        if keyword:
            sql += ''' 
            AND a."pm_name" like CONCAT('%%', %(keyword)s, '%%')
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
            AND a.dept_id = %(pmDept)s
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
            AND a."pm_user_id" = %(isMyTask)s
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

    def get_pm_master_detail(self, id):
        sql = ''' 
        SELECT 
               a.pm_pk
             , a.pm_no , a.pm_name 
             , e.id as equ_id
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
             , a.sch_start_dt
         FROM pm a
 	        inner join equ e on a.equ_id = e.id 
 	        inner join dept mng on e."Depart_id"  = mng.id
 	        inner join dept exc on a.dept_id  = exc.id 	     
            inner join auth_user au on a.pm_user_id  = au.id  	
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

    def get_pm_modal(self, keyword, dept_id):
        items = []
        dic_param = {'keyword':keyword, 'dept_id':dept_id}

        sql = ''' 
        select * from pm
	        left join auth_user au on pm."_creater_id" = au.id 
	        left join dept d ON pm."dept_id" = d.id
	        left join equ e on pm.equ_id = e.id 
        where 1=1
        '''
        
        if keyword:
            sql+=''' 
                AND (UPPER(pm."pm_name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
                    or UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
        	        or UPPER(e."Code") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
        )
            '''
        if dept_id:
            sql+=''' 
            AND UPPER(d.id) LIKE CONCAT('%%',UPPER(%(dept_id)s),'%%')
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

