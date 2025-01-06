from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.definition import TagGroup

def tag_group(context):
    '''
    /api/definition/tag_group
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action', 'read')

    try:
        if action == 'read':
            tag_group_id = gparam.get('tag_group_id')
            tag_group_name = gparam.get('tag_group_name')
  
            sql = '''
            SELECT 
                tg.id AS tag_group_id
	            , tg."Name" AS tag_group_name
	            , tg."Code" AS tag_group_code
	            , tg."Description" AS description
            FROM tag_grp tg 
            WHERE 1=1
            '''
            if tag_group_id:
                sql += '''
                /* AND UPPER(tg."Code") LIKE CONCAT('%%',UPPER(%(tag_group_code)s),'%%') */
                AND tg.tag_group_id = %(tag_group_id)s
                '''
            if tag_group_name:
                sql += '''
                AND UPPER(tg."Name") LIKE CONCAT('%%',UPPER(%(tag_group_name)s),'%%')
                '''

            sql += '''ORDER BY tg."Code" desc'''

            dc = {}
            dc['tag_group_id'] = tag_group_id
            dc['tag_group_name'] = tag_group_name
        
            result = DbUtil.get_rows(sql, dc)   
            
        elif action == 'save':
            id = posparam.get('tag_group_id')
            tag_group_code = posparam.get('tag_group_code')
            tag_group_name = posparam.get('tag_group_name')
            description = posparam.get('description')
            if id:
                tag_group = TagGroup.objects.get(id=id)
            else:
                check_code = TagGroup.objects.filter(Code=tag_group_code).first()
                if check_code:
                    items = {'success': False, 'message' : '중복된 태그그룹코드가 존재합니다.'}
                    return items
                tag_group = TagGroup()
            tag_group.Name = tag_group_name
            tag_group.Code = tag_group_code
            tag_group.Description = description
            tag_group.set_audit(request.user)
            tag_group.save()

            result = { 'success':True, 'tag_group_id':tag_group.id }         
        
        elif action == 'delete':
            id = posparam.get('tag_group_id')

            if id:
                tag_group = TagGroup.objects.filter(id=id).first()
                tag_group.delete()
                result = { 'success':True }
            
    except Exception as ex:
        source = '/api/definition/tag_group, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result