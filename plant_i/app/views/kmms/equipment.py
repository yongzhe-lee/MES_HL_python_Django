from django.db import transaction
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

    elif action=='load_component': 
        try:
            pageName = gparam.get('pageName')

            template_path = 'components/' + pageName
            context = {
                'request': request,
            }
            html = render_to_string(template_path, context)
            return html 

        except Exception as e:
            import traceback
            error_msg = f"템플릿 렌더링 오류: {str(e)}"
            return error_msg  # 오류 메시지 문자열 직접 반환

    elif action=='read': 
        equipment = gparam.get('equipment', None)

        items = equipmentService.searchEquipment(equipment)

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

    elif action in ['save', 'update']:
        id = CommonUtil.try_int(posparam.get('id'))
        equipCode = posparam.get('equipCode')
        equipName = posparam.get('equipName')
        equipClassPk = posparam.get('equipClassPk')
        locPK = posparam.get('loc_pk')
        deptPK = posparam.get('dept_pk')
        upEquipPk = posparam.get('upEquipPk', None)        
        environEquipYn = posparam.get('environEquipYn')        
        equip_mtrl_pk = posparam.get('equip_mtrl_pk') #순환설비자재
        import_rank_pk = posparam.get('import_rank_pk', None)        
        process_cd = posparam.get('process_cd')
        supplier = posparam.get('supplier', None)
        system_cd = posparam.get('system_cd')        
        upEquip_pk = posparam.get('upEquip_pk')
        warranty_dt = posparam.get('warranty_dt')
        Description = posparam.get('Description')
        InstallDate = posparam.get('InstallDate')
        Maker = posparam.get('Maker')
        Model = posparam.get('Model')
        ProductionYear = posparam.get('ProductionYear')
        PurchaseCost = posparam.get('PurchaseCost')
        SerialNumber = posparam.get('SerialNumber')
        asset_nos = posparam.get('asset_nos')
        ccenterCd = posparam.get('ccenterCd')

        c = None
        try:
            if id:
                c = CmEquipment.objects.filter(id=id).first()
            else:
                c = CmEquipment()
           
            c.EquipCode = equipCode
            c.EquipName = equipName
            # 설비 카테고리 처리
            c.CmEquipCategory = CmEquipCategory.objects.get(EquipCategoryCode=equipClassPk)
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
            c.set_audit(user)
            c.save()
            print("PK:", c.id)  # 저장 후 PK가 할당되는지 확인

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
