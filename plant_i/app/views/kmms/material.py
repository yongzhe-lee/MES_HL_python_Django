from django.db import transaction
from domain.models.cmms import CmMaterial, CmSupplier
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.kmms.material import MaterialService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import os

#urls.py를 따로 건드리지 않고 기존 API 라우팅 구조 내에서 처리
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

def material(context):
    '''
    /api/kmms/material
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user

    materialService = MaterialService()

    # ✅ 첨부파일 모달을 HTML 문자열로 응답
    if action=='load_modal':
        try:
            data_pk = gparam.get('mtrl_pk')

            if data_pk == None:
                data = ''
            else:
                data = materialService.get_material_findOne(data_pk)

            print("=== 모달 로딩 시작 ===")
            template_path = 'components/material.html'
            context = {
                'request': request,
                'material': data  # ✅ 여기 핵심!
            }
            html = render_to_string(template_path, context)
            return html  # HttpResponse 대신 html 문자열 직접 반환

        except Exception as e:
            import traceback
            error_msg = f"템플릿 렌더링 오류: {str(e)}"
            print(error_msg)
            print("상세 오류:\n", traceback.format_exc())
            return error_msg  # 오류 메시지 문자열 직접 반환

    elif action=='findAll': 
        keyword = gparam.get('keyword', None)
        useYn = gparam.get('useYn', None)
        matClassPk = gparam.get('matClassPk', None)
        supplierNm = gparam.get('supplierNm', None)
        makerNm = gparam.get('makerNm', None)
        matDsc = gparam.get('matDsc', None)

        items = materialService.searchMaterial(keyword, useYn, matClassPk, supplierNm, makerNm, matDsc)

    elif action=='findOne': 
        mtrl_pk = gparam.get('mtrl_pk', None)
        items = materialService.get_material_findOne(mtrl_pk)

    elif action=='selectAll':
        keyword = gparam.get('keyword', None)
        supplier = gparam.get('supplier', None)
        mtrl_class = gparam.get('mtrl_class', None)
        items = materialService.get_material_selectAll(keyword, supplier, mtrl_class)

    elif action=='save':
        try:
            id = CommonUtil.try_int(posparam.get('mtrl_pk'))
            MtrlCode = posparam.get('MtrlCode')
            MtrlName = posparam.get('MtrlName')
            MtrlClassCodePk = posparam.get('MtrlClassCodePk')
            MtrlDsc = posparam.get('mtrl_dsc')
            MakerPk = posparam.get('maker_pk')
            if MakerPk in [None, '']:
                MakerPk = None
            else:
                MakerPk = int(MakerPk)
            SafetyStockAmt = posparam.get('safety_stock_amt') or 0
            AmtUnitPk = posparam.get('amt_unit_pk')
            UnitPrice = posparam.get('unit_price')
            if UnitPrice in [None, '']:
                UnitPrice = None
            else:
                UnitPrice = float(UnitPrice)
            UnitPriceDt = posparam.get('unit_price_dt')
            SupplierPk = posparam.get('supplier_pk')
            DeliveryDays = posparam.get('delivery_days')
            if DeliveryDays in [None, '']:
                DeliveryDays = None
            else:
                DeliveryDays = int(DeliveryDays)
            DeliveryType = posparam.get('delivery_type')
            ErpMtrlCode = posparam.get('erp_mtrl_cd')
            AllowAddBom = posparam.get('allow_add_bom')
            ConstructionPk = posparam.get('construction_pk')
            if ConstructionPk in [None, '']:
                ConstructionPk = None
            else:
                ConstructionPk = int(ConstructionPk)
            EquipmentPk = posparam.get('equipment_pk')
            if EquipmentPk in [None, '']:
                EquipmentPk = None
            else:
                EquipmentPk = int(EquipmentPk)

            if id:
                c = CmMaterial.objects.get(id=id)

            else:
                c = CmMaterial()

            c.MtrlCode = MtrlCode
            c.MtrlName = MtrlName
            c.MtrlClassCodePk = MtrlClassCodePk
            c.MtrlDsc = MtrlDsc
            c.MakerPk = MakerPk
            c.SafetyStockAmt = SafetyStockAmt
            c.AmtUnitPk = AmtUnitPk 
            c.UnitPrice = UnitPrice
            c.DeliveryDays = DeliveryDays
            c.DeliveryType = DeliveryType
            c.ErpMtrlCode = ErpMtrlCode
            c.AllowAddBom = AllowAddBom
            c.ConstructionPk = ConstructionPk
            c.EquipmentPk = EquipmentPk

            if SupplierPk:
                c.CmSupplier = CmSupplier.objects.get(id=SupplierPk)

            # 날짜 필드 처리
            def validate_date(date_str, field_name):
                if not date_str:
                    return None
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"'{field_name}'은(는) YYYY-MM-DD 형식이어야 합니다.")

            try:
                c.UnitPriceDt = validate_date(UnitPriceDt, '보증일자')
            except ValueError as e:
                return {'success': False, 'message': str(e)}
        
            c.SiteId = 1
            c.UseYn = 'Y'
            c.DelYn = 'N'
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '자재의 정보가 저장되었습니다.'}
        except Exception as ex:
            source = 'api/kmms/material, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='delete':
        try:
            id = posparam.get('mtrl_pk')
            CmMaterial.objects.filter(id=id).delete()
            items = {'success': True}
        except Exception as ex:
            source = 'api/kmms/material, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='log':
        mtrl_pk = gparam.get('mtrl_pk', None)
        items = materialService.get_material_log(mtrl_pk) 

    return items   
