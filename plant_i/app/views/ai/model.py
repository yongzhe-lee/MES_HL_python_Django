from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.da import DsMaster

def model(context):
    '''
    /api/ai/model
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action', 'read')

    try:
        if action == 'read':
            model_type = gparam.get('sch_model_type')
            equipment_id = gparam.get('sch_equipment')
            keyword = gparam.get('sch_keyword')
  
            sql = '''
            SELECT 
                mm.id
	            , mm."Name" AS model_name
	            , mm."Type" AS model_type
	            , mm."Cycle" AS cycle
	            , mm."Equipment_id" AS equip_id
	            , e."Name" AS equip_name
            FROM ds_master mm
            LEFT JOIN equ e ON e.id = mm."Equipment_id"
            WHERE 1=1
            '''
            if equipment_id:
                sql += '''
                AND mm."Equipment_id" = %(equipment_id)s
                '''
            if model_type:
                sql += '''
                AND mm."Type" = %(model_type)s
                '''
            if keyword:
                sql += '''
                AND (
                    UPPER(mm."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
                    OR UPPER(mm."Type") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
                    OR UPPER(e."Name") LIKE CONCAT('%%',UPPER(%(keyword)s),'%%')
                    )
                '''

            sql += '''ORDER BY mm."Name" desc'''

            dc = {}
            dc['model_type'] = model_type
            dc['equipment_id'] = equipment_id
            dc['keyword'] = keyword
        
            result = DbUtil.get_rows(sql, dc)   
            
        elif action == 'save':
            id = posparam.get('id')
            equip_id = posparam.get('equip_id')
            model_name = posparam.get('model_name')
            model_type = posparam.get('model_type')
            cycle = posparam.get('cycle')

            if id:
                model_master = DsMaster.objects.get(id=id)
            else:
                check_name = DsMaster.objects.filter(Name=model_name).first()
                if check_name:
                    items = {'success': False, 'message' : '중복된 모델마스터명이 존재합니다.'}
                    return items
                model_master = DsMaster()

            model_master.Equipment_id = equip_id
            model_master.Name = model_name
            model_master.Type = model_type
            model_master.Cycle = cycle

            model_master.set_audit(request.user)
            model_master.save()

            result = { 'success':True }         
        
        elif action == 'delete':
            id = posparam.get('id')

            if id:
                model_master = DsMaster.objects.filter(id=id).first()
                model_master.delete()
                result = { 'success':True }
            
    except Exception as ex:
        source = '/api/ai/model, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result