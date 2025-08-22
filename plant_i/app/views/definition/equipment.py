import json

from django.db import transaction
from domain.models.cmms import CmEquipClassify
from domain.models.definition import Equipment
from domain.models.definition import EquipLocHist
from domain.models.definition import EquipDeptHist
from domain.services.definition.equipment import EquipmentService
# from domain.services.file import FileService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil

def equipment(context):
    '''
    /api/definition/equipment
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    equipment_service = EquipmentService()

    if action=='read':
        equipment_line = gparam.get('line', None)
        equipment_group = gparam.get('group', None)
        equipment = gparam.get('equipment', None)

        items = equipment_service.get_equipment_list(equipment_line, equipment_group, equipment)

    elif action=='read_obs':
        dept_name = gparam.get('dept_name', None)
        equipment = gparam.get('equipment', None)

        items = equipment_service.get_equip_obsolete_list(dept_name, equipment)

    elif action=='read_modal':
        keyword = gparam.get('keyword', None)
        depart_id = gparam.get('depart_id', None)

        items = equipment_service.get_equip_modal(keyword, depart_id)

    elif action=='detail':
        id = gparam.get('id', None)
        items = equipment_service.get_equipment_detail(id)

    elif action=='read_dept_hist':
        items = equipment_service.get_equip_dept_hist()

    elif action=='save':
        posparam = context.posparam
        print(posparam)
        id = posparam.get('id','')
        code = posparam.get('Code')
        name = posparam.get('Name')
        equipment = None
        locHist = None #설비 위치 변경이력
        deptHist = None #설비 관리부서 변경이력
        eh_content = ''
        today = DateUtil.get_today()

        try:
            if id:
                equipment = Equipment.objects.get(id=id)          

                q = Equipment.objects.filter(Code=code)
                q = q.exclude(pk=id)
                check_code = q.first()

                name = Equipment.objects.filter(Name=name)
                name = name.exclude(pk=id)
                check_name = name.first()             

            else:
                equipment = Equipment()

                check_code = Equipment.objects.filter(Code=code).first()
                check_name = Equipment.objects.filter(Name=name).first()

            if check_code:
                items = {'success': False, 'message' : '중복된 설비그룹코드가 존재합니다.'}
                return items

            if check_name:
                items = {'success': False, 'message' : '중복된 설비그룹명이 존재합니다.'}
                return items

            equipment.Code = posparam.get('Code')
            equipment.Name = posparam.get('Name')
            equipment.Line_id = posparam.get('Line_id')
            equipment.MESCode = posparam.get('MESCode')
            equipment.SAPCode = posparam.get('SAPCode')
            equipment.EquipmentGroup_id = posparam.get('EquipmentGroup_id')
            equipment.Description = posparam.get('Description')
            equipment.Maker = posparam.get('Maker')
            equipment.Model = posparam.get('Model')
            equipment.Standard = posparam.get('Standard')
            equipment.Usage = posparam.get('Usage')
            equipment.ManageNumber = posparam.get('ManageNumber')
            equipment.SerialNumber = posparam.get('SerialNumber')
            equipment.Depart_id = posparam.get('Depart_id')
            equipment.ProductionYear = posparam.get('ProductionYear') if posparam.get('ProductionYear') else None
            equipment.AssetYN = posparam.get('AssetYN')
            equipment.DurableYears = posparam.get('DurableYears') if posparam.get('DurableYears') else None
            equipment.PowerWatt = posparam.get('PowerWatt') if posparam.get('DurableYears') else None
            equipment.Voltage = posparam.get('Voltage')
            equipment.Manager = posparam.get('Manager')
            equipment.SupplierName = posparam.get('SupplierName')
            equipment.PurchaseDate = posparam.get('PurchaseDate') if posparam.get('PurchaseDate') else None
            equipment.PurchaseCost = posparam.get('PurchaseCost') if posparam.get('PurchaseCost') else None
            equipment.ServiceCharger = posparam.get('ServiceCharger')
            equipment.ASTelNumber = posparam.get('ASTelNumber')
            equipment.AttentionRemark = posparam.get('AttentionRemark')
            equipment.Inputdate = posparam.get('InputDate') if posparam.get('InputDate') else None
            equipment.InstallDate = posparam.get('InstallDate') if posparam.get('InstallDate') else None
            equipment.DisposalDate = posparam.get('DisposalDate') if posparam.get('DisposalDate') else None
            equipment.DisposalReason = posparam.get('DisposalReason')
            equipment.OperationRateYN = posparam.get('OperationRateYN')
            equipment.loc_pk = posparam.get('loc_pk')
            equipment.import_rank = posparam.get('import_rank')     
            equipment.Status = posparam.get('Status')

            equipment.set_audit(user)

            equipment.save()

            #이미 등록된 설비에서만
            if id:
                # equipment = Equipment.objects.get(id=id)

                # 기존 설비위치가 변경 되었을 때
                locHist = EquipLocHist()
                locHist.equip_pk = equipment.id
                locHist.equip_loc_bef = posparam.get('equip_loc_bef')
                locHist.equip_loc_aft = posparam.get('loc_pk')

                if locHist.equip_loc_bef != "" and locHist.equip_loc_bef != locHist.equip_loc_aft :
                    locHist.set_audit(user)
                    locHist.save()                

                # 기존 관리부서가 변경 되었을 때
                deptHist = EquipDeptHist()
                deptHist.equip_pk = equipment.id
                deptHist.equip_dept_bef = posparam.get('equip_dept_bef')
                deptHist.equip_dept_aft = posparam.get('Depart_id')

                if deptHist.equip_dept_bef != "" and deptHist.equip_dept_bef != deptHist.equip_dept_aft:
                    deptHist.set_audit(user)
                    deptHist.save()

            items = {'success': True, 'id': equipment.id}

        except Exception as ex:
            source = 'api/definition/equipment, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='delete':
        try:
            id = posparam.get('id','')
            Equipment.objects.filter(id=id).delete()
            items = {'success': True}

        except Exception as ex:
            source = 'api/definition/equipment, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
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
            #if action == 'delete':
            #    items = {'success':False, 'message': '삭제중 오류가 발생하였습니다.'}
            #    return items
            #raise ex

    return items