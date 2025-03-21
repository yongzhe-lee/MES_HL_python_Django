import os, json
from domain.services.date import DateUtil
from domain.services.sql import DbUtil


def equ_result(context):
    '''
    /api/interface/equ_result
    '''

    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    result = {'success' : True, 'message' : ''}
    action = gparam.get('action')
    source = f'/api/interface/equ_result?{action}'

    try:
        if action=="read":
            data_date = gparam.get('data_date')
            dic_param = {'data_date' : data_date}



    except Exception as ex:
        result['success'] = False
        result['message'] = str(ex)


    return result