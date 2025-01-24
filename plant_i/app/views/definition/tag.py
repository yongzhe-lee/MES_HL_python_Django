from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.definition import TagMaster

def tag(context):
    '''
    /api/definition/tag
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action', 'read')

    try:
        if action == 'read':
            tag_group_id = gparam.get('sch_tag_group')
            equipment_id = gparam.get('sch_equipment')
            keyword = gparam.get('sch_keyword')
            ai_yn = gparam.get('ai_yn')

            sql = ''' 
            SELECT 
                t.tag_code
	            , t.tag_name
	            , t.tag_group_id
	            , tg."Name" AS tag_group_name
	            , t."Equipment_id" AS equipment_id
	            , e."Name" AS equipment_name  
                , t."RoundDigit" AS round_digit
	            , t."LSL" AS lsl
	            , t."USL" AS usl
                , dc.id AS "DASconfig_id"
                , dc."Name" AS "DASconfig_name"
            FROM 
                tag t 
            LEFT JOIN 
                tag_grp tg ON t.tag_group_id = tg.id
            LEFT JOIN 
                equ e ON e.id = t."Equipment_id"
            LEFT JOIN 
                das_config dc ON dc.id=t."DASConfig_id"
            WHERE 1=1
            '''

            if tag_group_id:
                sql += '''
                AND t.tag_group_id = %(tag_group_id)s
                '''
            if equipment_id:
                sql += '''
                AND t."Equipment_id" = %(equipment_id)s
                '''
            if keyword:
                sql+='''
                AND (
                    UPPER(t.tag_code) LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                    OR UPPER(t.tag_name) LIKE CONCAT('%%', UPPER(%(keyword)s),'%%')
                )
                '''
            if ai_yn == 'Y':
                # 임시(조건 변경 필요)
                sql+='''
                    and e."Code" in ('EQ_A_PRESS_2','EQ_B_ETC_5')
                '''
            sql += '''ORDER BY t.tag_name desc'''

            dc = {}
            dc['tag_group_id'] = tag_group_id
            dc['equipment_id'] = equipment_id
            dc['keyword'] = keyword
        
            result = DbUtil.get_rows(sql, dc)   
            
        elif action == 'save':
            id = posparam.get('tag_id') 
            tag_code = posparam.get('tag_code')
            tag_name = posparam.get('tag_name')
            tag_group_id = posparam.get('tag_group_id')
            equipment_id = posparam.get('equipment_id')
            round_digit = posparam.get('round_digit')
            DASconfig_id = posparam.get('DASconfig_id')
            LSL = posparam.get('lsl')
            USL = posparam.get('usl')
            
            round_digit = CommonUtil.try_int(round_digit, 3)
            LSL = CommonUtil.try_float(LSL)
            USL = CommonUtil.try_float(USL)
                        
            if id:
                tag = TagMaster.objects.get(tag_code=id)
            else:
                tag = TagMaster()
            tag.tag_code = tag_code
            tag.tag_name = tag_name
            tag.RoundDigit = round_digit
            tag.tag_group_id = tag_group_id
            tag.Equipment_id = equipment_id
            tag.DASConfig_id = DASconfig_id
            tag.LSL = LSL
            tag.USL = USL
  
            tag.set_audit(request.user)
            tag.save()

            result = { 'success':True }         
        
        elif action == 'delete':
            tag_code = posparam.get('tag_code')

            if tag_code:
                tag = TagMaster.objects.filter(tag_code=tag_code).first()
                tag.delete()
                result = { 'success':True }
            
    except Exception as ex:
        source = '/api/definition/tag, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result