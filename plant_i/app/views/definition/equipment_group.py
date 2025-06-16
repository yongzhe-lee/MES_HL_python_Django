from datetime import datetime

from domain.models.definition import Equipment, EquipmentGroup
from domain.services.common import CommonUtil
from domain.services.definition.equipment_group import EquipmentGroupService
from domain.services.logging import LogWriter

def equipment_group(context):
    '''
    /api/definition/equipment_group
    '''
    items = []
    posparam = context.posparam
    gparam = context.gparam
    keyword = gparam.get('keyword', None)
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user


    equipment_group_service = EquipmentGroupService()

    try:
        if action == 'read':
            items = equipment_group_service.get_equipment_group_list(keyword)
        elif action == 'detail':
            group_id = context.gparam.get('id')
            items = equipment_group_service.get_equipment_group_detail(group_id)
        elif action == 'save':
            id = CommonUtil.try_int(posparam.get('id'), 0)
            equipment_type = posparam.get('equipment_type')
            equipment_group_code = posparam.get('equipment_group_code')
            equipment_group_name = posparam.get('equipment_group_name')
            description = posparam.get('description')

            if id > 0:
                q = EquipmentGroup.objects.filter(Code=equipment_group_code)
                q = q.exclude(pk=id)
                check_code = q.first()

                name = EquipmentGroup.objects.filter(Name=equipment_group_name)
                name = name.exclude(pk=id)
                check_name = name.first()
            else:
                check_code = EquipmentGroup.objects.filter(Code=equipment_group_code).first()
                check_name = EquipmentGroup.objects.filter(Name=equipment_group_name).first()

            if check_code:
                items = {'success': False, 'message' : '중복된 설비그룹코드가 존재합니다.'}
                return items

            if check_name:
                items = {'success': False, 'message' : '중복된 설비그룹명이 존재합니다.'}
                return items

            if id:
                equ_grp = EquipmentGroup.objects.get(id=id)
            else:
                equ_grp = EquipmentGroup()
            equ_grp.Code = equipment_group_code
            equ_grp.Name = equipment_group_name
            equ_grp.EquipmentType = equipment_type
            equ_grp.Description = description
            equ_grp.set_audit(user)

            equ_grp.save()

            items = {'success':True, 'message':''}

        elif action == 'delete':
            id = posparam.get('id')

            if id:
                equ = Equipment.objects.filter(EquipmentGroup_id = id)

                if len(equ) != 0:
                   items = {'success': False, 'message': '해당 설비그룹을 사용중인 \n 설비가 존재합니다.'}
                   return items

                equ_grp = EquipmentGroup.objects.filter(id=id)
                equ_grp.delete()
                items = {'success': True}

    except Exception as ex:
        source = '/api/definition/equipment_group : action{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items

    return items