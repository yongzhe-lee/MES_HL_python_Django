from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.system import Factory

def factory(context):
    '''
    /api/definition/factory
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
            select id as factory_id
            , "Name" as factory_name
            , "Code" as factory_code
            /* , "Description" as description */
            ,_created,_modified
            from factory f 
            where 1=1
            '''
            if keyword:
                sql += '''
                and (
                    f."Name" like CONCAT('%%', %(keyword)s, '%%')
                    or f."Code" like CONCAT('%%', %(keyword)s, '%%')
                )
                '''
            sql += '''
            order by f."Name"
            '''
            dc = {}
            dc['keyword'] = keyword

            result = DbUtil.get_rows(sql, dc)

        elif action == 'save':
            factory_id = posparam.get('factory_id')
            factory_name = posparam.get('factory_name')
            factory_code = posparam.get('factory_code')
            # description = posparam.get('description')

            factory = None
            if factory_id:
                factory = Factory.objects.filter(id=factory_id).first()
            else:
                factory = Factory()
            factory.Name = factory_name
            factory.Code = factory_code
            # factory.Description = description
            factory.set_audit(request.user)
            factory.Site_id = 1
            factory.save()

            result = { 'success':True }

        elif action == 'delete':
            factory_id = posparam.get('factory_id')
            factory = Factory.objects.filter(id=factory_id).first()
            factory.set_audit(context.request.user)
            factory.save()            
            result = { 'success':True }

    except Exception as ex:
        source = '/api/definition/factory, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = { 'success':False, 'message':str(ex) }

    return result