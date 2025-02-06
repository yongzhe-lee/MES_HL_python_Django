import json, threading

from domain.services.common import CommonUtil
from domain.services.logging import LogWriter
from domain.services.ai.data_processing import DataProcessingService
from domain.services.sql import DbUtil
from domain.services.date import DateUtil

def defect_inspection(context):
    items = []
    posparam = context.posparam
    gparam = context.gparam
    request = context.request
    action = gparam.get('action', 'read')

    try:
        if action == 'read_tag_data':
            pass
        
    except Exception as ex:
        source = 'defect_inspection : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex
    return items
