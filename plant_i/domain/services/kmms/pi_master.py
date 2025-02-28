from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PIService():

    def __init__(self):
        return

    def get_pi_master_list(self, keyword, equDept, equLoc, pmDept, isMyTask, isLegal):
        items = []
        dic_param = {'keyword': keyword,'equDept': equDept,'equLoc': equLoc,'pmDept': pmDept,'isMyTask': isMyTask,'isLegal': isLegal}

        sql = ''' 
         SELECT 
              chk_pk, chk_no, chk_name, chk_yn, cycle_type, 
              per_number, sch_start_dt, first_work_dt, 
              last_work_dt, next_chk_date, work_text, 
              work_expect_hr, check_type, use_yn, del_yn, 
              "_status", "_created", "_modified", "_creater_id", 
              "_modifier_id", "_creater_nm", "_modifier_nm", 
              chk_user_id, dept_id
         FROM chk_mst a
 	       -- inner join equ e on a.equ_id = e.id 
 	       -- inner join dept mng on e."Depart_id"  = mng.id
 	       -- inner join dept exc on a.dept_id  = exc.id 	     
           -- inner join auth_user au on a.pm_user_id  = au.id  	
 	       -- left join "location" l on e.loc_pk = l.id  	        
         WHERE 1 = 1 
        '''
        # if keyword:
        #     sql += ''' 
        #     AND a."pm_name" like CONCAT('%%', %(keyword)s, '%%')
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
        #     AND a."pm_user_id" = %(isMyTask)s
        #     '''
        # if isLegal:
        #     sql += ''' 
        #     AND e."environ_equip_yn" = %(isLegal)s
        #     '''
        # sql += ''' 
        #     ORDER BY a.pm_no
        #     '''

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
             , e.import_rank_pk
             , e."Depart_id" as mng_dept_id
             , mng."Name" as manage_dept
             , exc.id
             , exc."Name" as exec_dept          
             , l.loc_nm as equ_location
             , au.id as pm_manager
             , a.pm_type 
             , a.cycle_type 
         FROM pm a
 	        inner join equ e on a.equ_id = e.id 
 	        inner join dept mng on e."Depart_id"  = mng.id
 	        inner join dept exc on a.dept_id  = exc.id 	     
            inner join auth_user au on a.pm_user_id  = au.id  	
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

