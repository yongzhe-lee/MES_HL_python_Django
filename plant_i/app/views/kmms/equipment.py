from django.db import transaction
from app.views.kmms import equip_spec
from domain.models.cmms import CmDept, CmEquipCategory, CmEquipment, CmImportRank, CmLocation, CmMaterial, CmSupplier
from domain.services.sql import DbUtil
from domain.services.kmms.equipment import EquipmentService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.common import CommonUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import os

#urls.py를 따로 건드리지 않고 기존 API 라우팅 구조 내에서 처리
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

def handle_equipment_specs(equipment_id, posparam, request):
    """
    설비 사양 데이터를 처리하는 메소드
    Args:
        equipment_id: 설비 ID
        posparam: POST 파라미터
        request: HTTP 요청 객체
    """
    from app.views.kmms.equip_spec import equip_spec

    # 기존 사양 데이터 전체 삭제
    delete_context = type('Context', (), {})()
    delete_context.gparam = {'action': 'delete'}
    delete_context.posparam = {'equipPk': equipment_id}
    delete_context.request = request
    equip_spec(delete_context)

    # form-urlencoded 방식 specList 파싱 함수
    def parse_spec_list(posparam):
        spec_list = []
        idx = 0
        while True:
            key_prefix = f'specList[{idx}]'
            specnm = posparam.get(f'{key_prefix}[specnm]')
            unit = posparam.get(f'{key_prefix}[unit]')
            spec = posparam.get(f'{key_prefix}[spec]')
            if specnm is None:
                break
            spec_list.append({
                'specnm': specnm,
                'unit': unit,
                'spec': spec
            })
            idx += 1
        return spec_list

    # 새 사양 데이터 insert
    spec_list = parse_spec_list(posparam)
    for spec in spec_list:
        insert_context = type('Context', (), {})()
        insert_context.gparam = {'action': 'insert'}
        insert_context.posparam = {
            'equipPk': equipment_id,
            'equipSpecNm': spec.get('specnm'),
            'equipSpecUnit': spec.get('unit'),
            'equipSpecValue': spec.get('spec')
        }
        insert_context.request = request
        equip_spec(insert_context)

def handle_equip_part_mtrl(equipment_id, posparam, request):
    """
    설비 자재 데이터를 처리하는 메소드
    Args:
        equipment_id: 설비 ID
        posparam: POST 파라미터
        request: HTTP 요청 객체
    """
    from app.views.kmms.equip_part_mtrl import equip_part_mtrl

    # 기존 데이터 전체 삭제
    delete_context = type('Context', (), {})()
    delete_context.gparam = {'action': 'delete'}
    delete_context.posparam = {'equipPk': equipment_id}
    delete_context.request = request
    equip_part_mtrl(delete_context)

    # form-urlencoded 방식 partList 파싱 함수
    def parse_part_mtrl_list(posparam):
        part_mtrl_list = []
        idx = 0
        while True:
            key_prefix = f'partsList[{idx}]'
            mtrlPk = posparam.get(f'{key_prefix}[_mtrl_pk]')
            amt = posparam.get(f'{key_prefix}[_safety_stock_amt]')
            if mtrlPk is None:
                break
            part_mtrl_list.append({
                'mtrlPk': mtrlPk,           
                'amt': amt,
            })
            idx += 1
        return part_mtrl_list

    # 새 사양 데이터 insert
    part_mtrl_list = parse_part_mtrl_list(posparam)
    for part_mtrl in part_mtrl_list:
        insert_context = type('Context', (), {})()
        insert_context.gparam = {'action': 'insert'}
        insert_context.posparam = {
            'equipPk': equipment_id,
            'mtrlPk': part_mtrl.get('mtrlPk'),
            'amt': part_mtrl.get('amt')
        }
        insert_context.request = request
        equip_part_mtrl(insert_context)

def equipment(context):
    '''
    /api/kmms/equipment
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user
    factory_id = 1

    equipmentService = EquipmentService()

    # ✅ 첨부파일 모달을 HTML 문자열로 응답
    if action == 'load_modal':
        try:
            data_pk = gparam.get('equip_pk')            

            if data_pk == None:
                data = ''
            else:
                data = equipmentService.get_equipment_findOne(data_pk)

            print("=== 모달 로딩 시작 ===")
            template_path = 'components/equipment.html'
            context = {
                'request': request,
                'equipment': data  # ✅ 여기 핵심!
            }
            html = render_to_string(template_path, context)
            return html  # HttpResponse 대신 html 문자열 직접 반환

        except Exception as e:
            import traceback
            error_msg = f"템플릿 렌더링 오류: {str(e)}"
            print(error_msg)
            print("상세 오류:\n", traceback.format_exc())
            return error_msg  # 오류 메시지 문자열 직접 반환

    elif action=='read': 
        keyword = gparam.get('keyword', None)
        equip_status = gparam.get('equip_status', None)
        process_cd = gparam.get('process_cd', None)
        system_cd = gparam.get('system_cd', None)
        loc_pk = gparam.get('loc_pk', None)
        equip_category_id = gparam.get('equip_category_id', None)
        equip_class_path = gparam.get('equip_class_path', None)
        supplier_pk = gparam.get('supplier_pk', None)
        use_yn = gparam.get('use_yn', None)
        environ_equip_yn = gparam.get('environ_equip_yn', None)

        items = equipmentService.searchEquipment(keyword, equip_status, process_cd, system_cd, loc_pk, equip_category_id, equip_class_path, supplier_pk, use_yn, environ_equip_yn)

    elif action=='findAll':
        keyword = gparam.get('keyword', None)
        depart_id = gparam.get('depart_id', None)
        items = equipmentService.get_equipment_findAll(keyword, depart_id)

    elif action=='selectAll':
        keyword = gparam.get('keyword', None)
        depart_id = gparam.get('depart_id', None)
        items = equipmentService.get_equipment_selectAll(keyword, depart_id)

    elif action=='findOne':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equipment_findOne(equip_pk)

    elif action=='getEquipPmList':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.getEquipPmList(equip_pk)

    elif action=='log':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equipment_log(equip_pk)    

    elif action in ['save', 'update']:
        id = CommonUtil.try_int(posparam.get('equip_pk'))
        equipCode = posparam.get('equipCode')
        equipName = posparam.get('equipName')
        equip_category_id = posparam.get('equip_category_id')
        locPK = posparam.get('loc_pk')
        deptPK = posparam.get('dept_pk')
        upEquipPk = posparam.get('upEquipPk', None)        
        environEquipYn = posparam.get('environ_equip_yn', None)        
        equip_mtrl_pk = posparam.get('mtrl_pk') #순환설비자재
        import_rank_pk = posparam.get('import_rank_pk', None)        
        process_cd = posparam.get('process_cd')
        supplier = posparam.get('supplier', None)
        system_cd = posparam.get('system_cd')        
        upEquip_pk = posparam.get('upEquip_pk')
        warranty_dt = posparam.get('warranty_dt')
        Description = posparam.get('Description')
        InstallDate = posparam.get('install_dt')
        Maker = posparam.get('Maker')
        Model = posparam.get('Model')
        ProductionYear = posparam.get('make_dt')
        PurchaseCost = posparam.get('PurchaseCost')
        SerialNumber = posparam.get('SerialNumber')
        asset_nos = posparam.get('asset_nos')
        ccenterCd = posparam.get('ccenterCd')
        EquipClassPath = posparam.get('EquipClassPath')
        EquipClassDesc = posparam.get('EquipClassDesc')

        c = None
        try:
            if id:
                c = CmEquipment.objects.filter(id=id).first()
            else:
                c = CmEquipment()
           
            c.EquipCode = equipCode
            c.EquipName = equipName
            # 설비 카테고리 처리
            c.CmEquipCategory = CmEquipCategory.objects.get(EquipCategoryCode=equip_category_id)
            c.SiteId = 1;
        
            c.CmLocation = CmLocation.objects.get(LocPk=locPK)   ## 위치코드
            try:
                dept = CmDept.objects.get(id=deptPK)
                c.DeptPk = dept.id ## 부서코드 - ID값만 저장
            except CmDept.DoesNotExist:
                return {'success': False, 'message': '존재하지 않는 부서코드입니다.'}
            c.CmMaterial = CmMaterial.objects.get(id=equip_mtrl_pk) ## 자재대상설비 

            if upEquipPk:
                c.Parent = CmEquipment.objects.get(id=upEquipPk)   ## 상위위치코드
            if supplier:
                c.CmSupplier = CmSupplier.objects.get(id=supplier) ## 공급업체 
            if import_rank_pk:
                c.CmImportRank = CmImportRank.objects.get(id=import_rank_pk) ## 중요도등급         
        
            c.ProcessCode = process_cd        
            c.SystemCode = system_cd
            c.Parent = upEquip_pk

            # 날짜 필드 처리
            def validate_date(date_str, field_name):
                if not date_str:
                    return None
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"'{field_name}'은(는) YYYY-MM-DD 형식이어야 합니다.")

            try:
                c.WarrantyDt = validate_date(warranty_dt, '보증일자')
                c.InstallDt = validate_date(InstallDate, '설치일자')
                c.MakeDt = validate_date(ProductionYear, '제조일자')
            except ValueError as e:
                return {'success': False, 'message': str(e)}

            c.EquipDsc = Description
        
            # 제조사 처리
            try:
                c.MakerPk = int(Maker) if Maker else None
            except ValueError:
                return {'success': False, 'message': '제조사 코드는 숫자만 입력 가능합니다.'}
            
            c.ModelNumber = Model
        
            # 구매비용 처리
            try:
                c.BuyCost = int(PurchaseCost) if PurchaseCost else None
            except ValueError:
                return {'success': False, 'message': '구매비용은 숫자만 입력 가능합니다.'}
            
            c.SerialNumber = SerialNumber
            c.AssetNos = asset_nos
            c.CcenterCode = ccenterCd
            c.EnvironEquipYn = environEquipYn
            c.UseYn = 'Y'
            c.DelYn = 'N'

            c.EquipClassPath = EquipClassPath
            c.EquipClassDesc = EquipClassDesc

            c.set_audit(user)
            c.save()
            print("PK:", c.id)  # 저장 후 PK가 할당되는지 확인

            if c.id:
                handle_equipment_specs(c.id, posparam, request)

                handle_equip_part_mtrl(c.id, posparam, request)

            return {'success': True, 'message': '설비마스터 정보가 저장되었습니다.'}
        except Exception as e:
            return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'}

    elif action=='read_dispose':
        keyword = gparam.get('keyword', None)
        srchCat = gparam.get('srchCat', None)
        srch_dept = gparam.get('srchDept', None)
        start_date = gparam.get('sDate', None)
        end_date = gparam.get('eDate', None)

        items = equipmentService.get_equipment_disposed(keyword, srchCat, srch_dept, start_date, end_date)

    return items   
