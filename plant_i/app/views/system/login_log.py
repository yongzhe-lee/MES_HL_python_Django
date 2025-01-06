from configurations import settings

from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.sql import DbUtil

from domain.services.system import SystemService




def login_log(context):
    '''
    api/system/login_log
    '''
    systemService = SystemService()
    gparam = context.gparam
    start = gparam.get('srchStartDt', None) + ' 00:00:00'
    end = gparam.get('srchEndDt', None) + ' 23:59:59'
    keyword = gparam.get('keyword', None)

    items = systemService.get_loginlog_list(start, end, keyword)
    return items



