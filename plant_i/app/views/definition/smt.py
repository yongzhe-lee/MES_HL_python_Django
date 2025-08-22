from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

def smt(context):
    '''
    /api/definition/smt
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    
    action = gparam.get('action', 'read')
    source = f'/api/definition/smt?action={action}'

    result = {}
    try:
        if action=="read":
            parts_type = gparam.get('parts_type')
            keyword  = gparam.get('keyword', '')
            sql ='''
            '''
            if parts_type:
                sql += '''
                AND s."PartsType" = %(parts_type)s
                '''
            items = DbUtil.get_rows(sql, {'parts_type': parts_type})

        elif action == 'save':
            parts_type = gparam.get('parts_type')
            sn = posparam.get('sn')

            result['success'] = True


    except Exception as e:
        LogWriter.add_dblog('error', source, e)
        result['success'] = False
        result['message'] = str(e)


    return result



