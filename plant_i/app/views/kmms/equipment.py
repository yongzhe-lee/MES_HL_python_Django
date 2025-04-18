from django.db import transaction
from domain.models.kmms import JobClass
from domain.services.sql import DbUtil
from domain.services.kmms.equipment import EquipmentService
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

    # ✅ equipment.html 모달을 HTML 문자열로 응답
    if action == 'load_modal':
        try:
            equip_pk = gparam.get('equip_pk')
            equipment_data = equipmentService.get_equipment_findOne(equip_pk)

            print("=== 모달 로딩 시작 ===")
            template_path = 'components/equipment.html'
            context = {
                'request': request,
                'equipment': equipment_data  # ✅ 여기 핵심!
            }
            html = render_to_string(template_path, context)
            return html  # HttpResponse 대신 html 문자열 직접 반환
        except Exception as e:
            import traceback
            error_msg = f"템플릿 렌더링 오류: {str(e)}"
            print(error_msg)
            print("상세 오류:\n", traceback.format_exc())
            return error_msg  # 오류 메시지 문자열 직접 반환

    if action=='read': 
        equipment = gparam.get('equipment', None)

        items = equipmentService.searchEquipment(equipment)

    elif action=='findOne':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equipment_findOne(equip_pk)

    elif action=='read_dispose':
        keyword = gparam.get('keyword', None)
        srchCat = gparam.get('srchCat', None)
        srch_dept = gparam.get('srchDept', None)
        start_date = gparam.get('sDate', None)
        end_date = gparam.get('eDate', None)

        items = equipmentService.get_equipment_disposed(keyword, srchCat, srch_dept, start_date, end_date)

    return items   
