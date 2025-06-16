from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.definition import Line

def line(context):
    '''
    /api/definition/line
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request

    action = gparam.get('action', 'read')
    result = {}
    try:
        if action =='read':
            keyword = gparam.get('keyword')

            sql = '''
            SELECT 
                id
                , "Name"
                , "Code"
                , "Description"
                , _created
                , _modified
            FROM 
                line L
            WHERE 1=1
            '''
            if keyword:
                sql += '''
                AND (
                    L."Name" LIKE CONCAT('%%', %(keyword)s, '%%')
                    OR L."Code" LIKE CONCAT('%%', %(keyword)s, '%%')
                )
                '''
            sql += '''
            ORDER BY L."Name"
            '''
            dc = {}
            dc['keyword'] = keyword

            result = DbUtil.get_rows(sql, dc)

        elif action == 'save':
            id = posparam.get('id')
            name = posparam.get('Name')
            code = posparam.get('Code')
            description = posparam.get('Description')

            line = None
            try:

                if id:
                    line = Line.objects.filter(id=id).first()
                else:
                    line = Line()

                line.Name = name
                line.Code = code
                line.Description = description
                line.set_audit(request.user)                
                line.save()

                result = { 'success':True }
            except Exception as ex:
                source = 'api/definition/factory, action:{}'.format(action)
                LogWriter.add_dblog('error', source, ex)
                raise ex

        elif action == 'delete':
            id = posparam.get('id')
            line = Line.objects.filter(id=id).first()
            line.delete()
            result = { 'success':True }

    except Exception as ex:
        source = '/api/definition/line, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = { 'success':False, 'message':str(ex) }

    return result