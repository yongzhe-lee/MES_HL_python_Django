from django.db import transaction
from domain.models.cmms import CmMaterial
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
    if action == 'load_modal':
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

    elif action in ['insert', 'update']:
        id = CommonUtil.try_int(posparam.get('mtrl_pk'))
        MtrlCode = posparam.get('mtrl_cd')
        MtrlName = posparam.get('mtrl_nm')
        MtrlClassCodePk = CommonUtil.try_int(posparam.get('mtrl_class_cd_pk'))
        MtrlDsc = posparam.get('mtrl_dsc')
        MakerPk = CommonUtil.try_int(posparam.get('maker_pk'))
        SafetyStockAmt = posparam.get('safety_stock_amt')
        AmtUnitPk = posparam.get('amt_unit_pk')
        UnitPrice = CommonUtil.try_int(posparam.get('unit_price'))
        UnitPriceDt = posparam.get('unit_price_dt')
        CmSupplier = CommonUtil.try_int(posparam.get('supplier_pk'))
        DeliveryDays = CommonUtil.try_int(posparam.get('delivery_days'))
        DeliveryType = posparam.get('delivery_type')
        ErpMtrlCode = posparam.get('erp_mtrl_cd')
        AllowAddBom = posparam.get('allow_add_bom')
        ConstructionPk = CommonUtil.try_int(posparam.get('construction_pk'))
        EquipmentPk = CommonUtil.try_int(posparam.get('equipment_pk'))
  
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
        c.UnitPriceDt = UnitPriceDt
        c.CmSupplier = CmSupplier
        c.DeliveryDays = DeliveryDays
        c.DeliveryType = DeliveryType
        c.ErpMtrlCode = ErpMtrlCode
        c.AllowAddBom = AllowAddBom
        c.ConstructionPk = ConstructionPk
        c.EquipmentPk = EquipmentPk

        c.set_audit(user)
        c.save()

        return {'success': True, 'message': '자재의 정보가 수정되었습니다.'}

    return items   
