from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class PMService():

    def __init__(self):
        return

    def get_pm_master_list(self, keyword):
        items = []
        dic_param = {'keyword': keyword}

        sql = ''' 
         SELECT 
             a.pm_no , a.pm_name 
             , e."Code" as equ_code, e."Name" as equ_name
             , e.import_rank_pk
             , d."Name" as exec_dept
             , d2."Name" as manage_dept
             , l.loc_nm as equ_location
             , au.first_name as pm_manager
             , a.pm_type 
             , a.cycle_type 
         FROM pm a
 	        left join equ e on a.equ_id = e.id 
 	        left join dept d on a.dept_id  = d.id
 	        left join dept d2 on e."Depart_id"  = d2.id
 	        left join "location" l on e.loc_pk = l.id 
 	        left join auth_user au on a.pm_user_id  = au.id  	
         WHERE 1 = 1  
        '''
        if keyword:
            sql += ''' 
            AND a."pm_name" like CONCAT('%%', %(keyword)s, '%%')
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
            pm_pk 
            , pm_no 
            , pm_name
            , pm_type 
            , work_expect_hr 
            , pm.dept_id
            , d."Name" as dept_name
            , pm.pm_user_id
            , au.first_name 
            , work_text
        FROM pm
            left join auth_user au on pm."_creater_id" = au.id 
            left join dept d ON pm."dept_id" = d.id
            left join equ e on pm.equ_id = e.id
        WHERE
            pm.pm_pk = %(id)s
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

