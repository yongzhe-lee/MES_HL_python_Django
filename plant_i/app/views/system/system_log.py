from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.services.system import SystemService    # mes에서 가져온 것

def system_log(context):
    '''
    /api/system/system_log
    '''
    gparam = context.gparam
    # posparam = context.posparam
    request = context.request
    user = request.user    
    action = gparam.get('action', 'read')
    systemService = SystemService()
    result = {'success': False}
    try:
        if action == 'read':
            start = gparam.get('start') + ' 00:00:00'
            end = gparam.get('end') + ' 23:59:59'
            type = gparam.get('log_type')
            source = gparam.get('keyword')
            items = systemService.get_systemlog_list(start, end, type, source)
            result = {'success': True, 'items': items}

        elif action == 'detail':
            log_id = context.gparam.get('log_id')
            data = systemService.get_systemlog_detail(log_id)
            result = {'success': True, 'data': data}

        else:
            result = {'success': False, 'message': 'Invalid action parameter.'}

    except Exception as ex:
        source = '/api/system/system_log, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result