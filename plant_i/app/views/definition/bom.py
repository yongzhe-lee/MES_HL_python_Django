import datetime

from django.db import transaction
from django.db.models import Q

from domain.services.common import CommonUtil
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.definition import Material
from domain.services.definition.bom import BOMService
from configurations import settings

def bom(context):

    items = []
    gparam = context.gparam
    posparam = context.posparam
    request = context.request

    action = gparam.get('action')
    bom_service = BOMService()
    try:
        if action=='read':
            mat_type = gparam.get('mat_type', '')
            mat_group = gparam.get('mat_group', '')
            bom_type = gparam.get('bom_type', '')
            mat_name = gparam.get('mat_name', '')
            not_past_flag = gparam.get('not_past_flag', '')
            items = bom_service.get_bom_list(mat_type, mat_group, bom_type, mat_name, not_past_flag)

        elif action=='detail':
            id = gparam.get('id')
            items = bom_service.get_bom_detail(id)


        elif action=='material_detail':
            id = gparam.get('id')
            items = bom_service.get_bom_material_detail(id)

        elif action=='bom_comp_list':
            id = gparam.get('id')
            items = bom_service.get_bom_material_list(id)

        elif action=='material_list':
            id = gparam.get('id')
            items = bom_service.get_bom_material_tree_list(id)

    except Exception as ex:
        source = '/api/definition/bom'
        LogWriter.add_dblog('error', source, ex)
        if action == 'bom_delete' or 'material_delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items
        #raise ex

    return items
