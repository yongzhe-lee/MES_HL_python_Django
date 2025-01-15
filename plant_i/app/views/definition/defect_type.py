from datetime import datetime
from domain.models.mes import DefectType
from domain.services.definition.defect_type import DefectTypeService
from domain.services.logging import LogWriter

def defect_type(context):
    '''
    /api/definition/defect_type
    '''
    items = []
    posparam = context.posparam
    gparam = context.gparam
    keyword = gparam.get('keyword', None)
    action = gparam.get('action', 'read')

    svc = DefectTypeService()    

    try:
        if action == 'read':
            coverage = gparam.get('coverage')
            _4m_type = gparam.get('4m_type')
            items = svc.get_defect_type_list(coverage, _4m_type, keyword)
        elif action == 'detail':
            id = context.gparam.get('id')
            items = svc.get_defect_type_detail(id)
        elif action == 'save':
            id = posparam.get('id')
            defect_type_code = posparam.get('defect_type_code')
            defect_type_name = posparam.get('defect_type_name')
            defect_type_coverage = posparam.get('defect_type_coverage')
            defect_type_4m_type = posparam.get('defect_type_4m_type')
            description = posparam.get('description')

            if id:
                defect_type = DefectType.objects.get(id=id)
            else:
                check_code = DefectType.objects.filter(Code=defect_type_code).first()
                if check_code:
                    items = {'success': False, 'message' : '중복된 코드가 존재합니다.'}
                    return items

                check_code = DefectType.objects.filter(Name=defect_type_name).first()
                if check_code:
                    items = {'success': False, 'message' : '중복된 부적합유형명이 존재합니다.'}
                    return items
                defect_type = DefectType()
            defect_type.Code = defect_type_code
            defect_type.Name = defect_type_name
            defect_type.Description = description
            defect_type.Coverage = defect_type_coverage
            defect_type.Type = defect_type_4m_type
            defect_type.save()

            items = {'success':True, 'message':''}

        elif action == 'delete':
            id = posparam.get('id')

            if id:
                defect_type = DefectType.objects.filter(id=id).first()
                defect_type.delete()
                items = {'success': True}

    except Exception as ex:
        source = 'defect_type : action-{}'.format(action)
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
        #return ex

    return items