from django.db import transaction
from domain.services.sql import DbUtil
from domain.models.kmms import PreventiveMaintenace
from domain.services.kmms.pm_master import PMService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil


def pm_master(context):
    '''
    /api/kmms/pm_master
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    pm_master_service = PMService()

    if action=='read':
        keyword = gparam.get('keyword', None)       
        
        items = pm_master_service.get_pm_master_list(keyword)

    elif action=='detail':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_master_detail(id)



    return items