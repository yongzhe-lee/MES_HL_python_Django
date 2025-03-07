from django.db import transaction
from domain.services.sql import DbUtil
from domain.models.kmms import PreventiveMaintenance
from domain.services.kmms.pi_master import PIService
# from domain.services.file import FileService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil


def pi_master(context):
    '''
    /api/kmms/pi_master
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    pi_master_service = PIService()

    if action=='read':
        keyword = gparam.get('keyword', None)  
        equDept = gparam.get('equDept', None)
        equLoc = gparam.get('equLoc', None)
        pmDept = gparam.get('pmDept', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else ''
        isLegal = gparam.get('isLegal', None)
        
        items = pi_master_service.get_pi_master_list(keyword, equDept, equLoc, pmDept, isMyTask, isLegal)

    # elif action=='detail':
    #     id = gparam.get('id', None)
    #     items = equipment_service.get_equipment_detail(id)

    # elif action=='save':
    #     posparam = context.posparam
    #     print(posparam)
    #     id = posparam.get('id','')
    #     code = posparam.get('Code')
    #     name = posparam.get('Name')
    #     equipment = None
    #     eh_content = ''
    #     today = DateUtil.get_today()

    #     try:
    #         if id:
    #             equipment = Equipment.objects.get(id=id)

    #             q = Equipment.objects.filter(Code=code)
    #             q = q.exclude(pk=id)
    #             check_code = q.first()

    #             name = Equipment.objects.filter(Name=name)
    #             name = name.exclude(pk=id)
    #             check_name = name.first()

    #         else:
    #             #{'id': '', 'EquipmentGroup_id': '1', 'Code': 'equip-1', 'Name': '설비1', 'ManageNumber': 'ㅁㄴㄻㄴ', 'WorkCenter_id': '2', 
    #             #'Model': 'ㅁㄴㅇㄹ', 'Maker': 'ㄴ', 'SerialNumber': 'ㅁㄴㄻㄴ', 'ProductionYear': '', 'PurchaseYear': '', 
    #             #'InstallDate': 'ㄴ', 'SupplierName': 'ㄴㄴ', 
    #             #'PurchaseCost': 'ㅁㄴㅇㄹ', 'OperationRateYN': 'Y', 'DisposalDate': 'ㅇㅁㄴㅇㄻ', 'Manager': 'ㅁ', 
    #             #'Description': 'ㅁㄴㅇㄻㄴㅇㄻㄴㅇㄻㄴㅇㄻㄴㅇㄻㄴㅇㄹ', 
    #             #'csrfmiddlewaretoken': 'xJwIk4wgZG9Gv3tllsxNHec3BBOAWi21dyjjtlUaFO7NJcimoJvawsoMsm01gn8t'}
    #             equipment = Equipment()

    #             check_code = Equipment.objects.filter(Code=code).first()
    #             check_name = Equipment.objects.filter(Name=name).first()

    #         if check_code:
    #             items = {'success': False, 'message' : '중복된 설비그룹코드가 존재합니다.'}
    #             return items

    #         if check_name:
    #             items = {'success': False, 'message' : '중복된 설비그룹명이 존재합니다.'}
    #             return items

    #         equipment.Code = posparam.get('Code')
    #         equipment.Name = posparam.get('Name')
    #         equipment.Line_id = posparam.get('Line_id')
    #         equipment.MESCode = posparam.get('MESCode')
    #         equipment.SAPCode = posparam.get('SAPCode')
    #         equipment.EquipmentGroup_id = posparam.get('EquipmentGroup_id')
    #         equipment.Description = posparam.get('Description')
    #         equipment.Maker = posparam.get('Maker')
    #         equipment.Model = posparam.get('Model')
    #         equipment.Standard = posparam.get('Standard')
    #         equipment.Usage = posparam.get('Usage')
    #         equipment.ManageNumber = posparam.get('ManageNumber')
    #         equipment.SerialNumber = posparam.get('SerialNumber')
    #         equipment.Depart_id = posparam.get('Depart_id')
    #         equipment.ProductionYear = posparam.get('ProductionYear') if posparam.get('ProductionYear') else None
    #         equipment.AssetYN = posparam.get('AssetYN')
    #         equipment.DurableYears = posparam.get('DurableYears') if posparam.get('DurableYears') else None
    #         equipment.PowerWatt = posparam.get('PowerWatt')
    #         equipment.Voltage = posparam.get('Voltage')
    #         equipment.Manager = posparam.get('Manager')
    #         equipment.SupplierName = posparam.get('SupplierName')
    #         equipment.PurchaseDate = posparam.get('PurchaseDate') if posparam.get('PurchaseDate') else None
    #         equipment.PurchaseCost = posparam.get('PurchaseCost') if posparam.get('PurchaseCost') else None
    #         equipment.ServiceCharger = posparam.get('ServiceCharger')
    #         equipment.ASTelNumber = posparam.get('ASTelNumber')
    #         equipment.AttentionRemark = posparam.get('AttentionRemark')
    #         equipment.Inputdate = posparam.get('InputDate') if posparam.get('InputDate') else None
    #         equipment.InstallDate = posparam.get('InstallDate') if posparam.get('InstallDate') else None
    #         equipment.DisposalDate = posparam.get('DisposalDate') if posparam.get('DisposalDate') else None
    #         equipment.DisposalReason = posparam.get('DisposalReason')
    #         equipment.OperationRateYN = posparam.get('OperationRateYN')
    #         equipment.set_audit(user)

    #         equipment.save()

    #         items = {'success': True, 'id': equipment.id}

    #     except Exception as ex:
    #         source = 'api/definition/equipment, action:{}'.format(action)
    #         LogWriter.add_dblog('error', source, ex)
    #         raise ex

    # elif action=='delete':
    #     try:
    #         id = posparam.get('id','')
    #         Equipment.objects.filter(id=id).delete()
    #         items = {'success': True}

    #     except Exception as ex:
    #         source = 'api/definition/equipment, action:{}'.format(action)
    #         LogWriter.add_dblog('error', source, ex)
    #         if action == 'delete':
    #             err_msg = LogWriter.delete_err_message(ex)
    #             items = {'success':False, 'message': err_msg}
    #             return items
    #         else:
    #             items = {}
    #             items['success'] = False
    #             if not items.get('message'):
    #                 items['message'] = str(ex)
    #             return items
    #         #if action == 'delete':
    #         #    items = {'success':False, 'message': '삭제중 오류가 발생하였습니다.'}
    #         #    return items
    #         #raise ex



    return items