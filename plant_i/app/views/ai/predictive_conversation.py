import json, threading

from domain.services.common import CommonUtil
from domain.services.logging import LogWriter
from domain.services.ai.data_processing import DataProcessingService
from domain.services.sql import DbUtil
from domain.services.date import DateUtil

def predictive_conversation(context):
    items = []
    posparam = context.posparam
    gparam = context.gparam
    request = context.request
    action = gparam.get('action', 'read')
    data_svc = DataProcessingService()

    try:
        if action == 'read_tag_data':
            sql = '''
            select 
            t.tag_code ,t.tag_name 
            ,t."LastValue" as last_value
            ,to_char(t."LastDate",'yyyy-mm-dd hh24:mi:ss') as last_date
            from tag t 
            inner join equ e on e.id = t."Equipment_id" and e."Code" in ('EQ_A_PRESS_2','EQ_B_ETC_5')
            order by e.id desc,t.tag_code 
            '''
            items = DbUtil.get_rows(sql)
            
        elif action == 'learning_data': 
            thread = threading.Thread(target=data_svc.run_model_training)
            thread.start()
            
            items = {'success':True}
        
        elif action == 'get_predictive_data':
            items = data_svc.get_predict_list()
        
    except Exception as ex:
        source = 'predictive_conversation : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex
    return items
