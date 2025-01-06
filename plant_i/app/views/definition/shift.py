from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.definition import Shift

def shift(context):
    '''
    /api/definition/shift
    '''
    gparam = context.gparam
    posparam = context.posparam
    
    action = gparam.get('action', 'read')
    try:
        if action == 'read':
            sch_shift_name = gparam.get('sch_shift_name')
            
            sql = '''
            SELECT 
                s.id AS shift_id
                ,s."Name" AS shift_name
                ,s."Code" AS shift_code
                ,s."StartTime" AS shift_start_time
                ,s."EndTime" AS shift_end_time
                ,s."Description" AS shift_description
            FROM shift s
            where 1=1
            '''
            if sch_shift_name:
                sql += '''
                AND s."Name" LIKE CONCAT('%%', %(sch_shift_name)s, '%%')
                '''
            sql += '''
            ORDER BY s."Name"
            '''
            dc = {}
            dc['sch_shift_name'] = sch_shift_name
            result = DbUtil.get_rows(sql, dc)    
            
        elif action == 'save':
            shift_id = posparam.get('shift_id')
            shift_name = posparam.get('shift_name')
            shift_code = posparam.get('shift_code')
            shift_start_time = posparam.get('shift_start_time')
            shift_end_time = posparam.get('shift_end_time')
            shift_description = posparam.get('shift_description')

            shift = None
            if shift_id:
                shift = Shift.objects.filter(id=shift_id).first()
            else:
                shift = Shift()
            
            shift.Name = shift_name
            shift.Code = shift_code
            shift.StartTime = shift_start_time
            shift.EndTime = shift_end_time
            shift.Description = shift_description            
            shift.save()
                
            result = { 'success':True, 'shift_id':shift.id}
        
        elif action == 'delete':
            shift_id = posparam.get('shift_id')
            
            shift = Shift.objects.filter(id=shift_id)
            shift.delete()
            
            result = { 'success':True }

    except Exception as ex:
        source = '/api/definition/shift, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items
        
    return result