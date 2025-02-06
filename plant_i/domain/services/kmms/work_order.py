from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class WorkOrderService():

    def __init__(self):
        return

    def get_work_order_list(self, keyword, req_dept, _creater_id):
        items = []
        dic_param = {'keyword': keyword, 'req_dept': req_dept, '_creater_id': _creater_id}

        sql = ''' 
        SELECT 
            *
        FROM work_order a
        WHERE 1 = 1  
        '''
        if keyword:
            sql += ''' 
            AND a."work_title" like CONCAT('%%', %(keyword)s, '%%')
            '''
        if req_dept:
            sql += ''' 
            AND a."req_dept" = %(req_dept)s
            '''
        if _creater_id:
            sql += ''' 
            AND a."_creater_id" = %(_creater_id)s
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

