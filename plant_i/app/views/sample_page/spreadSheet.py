from django.db import transaction
from domain.services.common import CommonUtil
from domain.services.sample_page.spreadSheet import SpreadSheetService
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.models.cmms import CmProject
from django.shortcuts import render

import os
import uuid
from django.db import transaction
from django.http import JsonResponse
from configurations import settings
import pandas as pd

def spreadSheet(context):
    '''
    /api/sample_page/spreadSheet
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action') or posparam.get('action') or 'read'
    request = context.request
    user = request.user
    factory_id = 1

    spreadSheet_Service = SpreadSheetService()

    try:
        if action in ['read', 'findAll']: 
            items = spreadSheet_Service.read()

        elif action == 'getDateHeader':
            items = spreadSheet_Service.getDateHeader()

        elif action == 'submit':
            # 스프레드시트에서 전송된 데이터 처리
            print("posparam:", posparam)
            
            # 평면화된 데이터를 파싱하여 배열로 변환
            data = []
            i = 0
            while True:
                proj_pk_key = f'data[{i}][proj_pk]'
                if proj_pk_key not in posparam:
                    break
                
                # 날짜별 데이터 파싱
                daily_data = {}
                for day in range(1, 8):  # day_1부터 day_7까지
                    day_key = f'day_{day}'
                    daily_data[day_key] = posparam.get(f'data[{i}][daily_data][{day_key}]', '')
                
                item = {
                    'proj_pk': posparam.get(f'data[{i}][proj_pk]', ''),
                    'proj_cd': posparam.get(f'data[{i}][proj_cd]', ''),
                    'proj_nm': posparam.get(f'data[{i}][proj_nm]', ''),
                    'plan_start_dt': posparam.get(f'data[{i}][plan_start_dt]', ''),
                    'plan_end_dt': posparam.get(f'data[{i}][plan_end_dt]', ''),
                    'proj_tot_cost': posparam.get(f'data[{i}][proj_tot_cost]', 0),
                    'status': posparam.get(f'data[{i}][status]', 'PREP'),
                    'daily_data': daily_data
                }
                data.append(item)
                i += 1
            
            print("파싱된 데이터:", data)
            print("데이터 타입:", type(data))
            print("데이터 길이:", len(data) if data else 0)
            
            if not data:
                return {'success': False, 'message': '저장할 데이터가 없습니다.'}
            
            try:
                with transaction.atomic():
                    for item in data:
                        projNm = item.get('proj_nm')
                        projCd = item.get('proj_cd')
                        planStartDt = item.get('plan_start_dt')
                        planEndDt = item.get('plan_end_dt')
                        projTotCost = item.get('proj_tot_cost')
                        status = item.get('status', 'PREP')
                        
                        # 프로젝트 코드가 있는 경우에만 처리
                        if projCd:
                            try:
                                c = CmProject.objects.get(ProjCode=projCd)
                            except CmProject.DoesNotExist:
                                c = CmProject()
                            
                            c.ProjName = projNm
                            c.ProjCode = projCd
                            c.PlanStartDt = planStartDt
                            c.PlanEndDt = planEndDt
                            c.ProjTotCost = projTotCost
                            c.Status = status
                            c.Factory_id = factory_id
                            c.set_audit(user)
                            
                            c.save()
                            
                            # 날짜별 데이터 처리
                            daily_data = item.get('daily_data', {})
                            print(f"프로젝트 {projCd}의 날짜별 데이터:", daily_data)
                            
                            # 여기서 날짜별 데이터를 데이터베이스에 저장하거나 처리할 수 있습니다
                            # 예: 별도 테이블에 저장하거나 로그로 기록
                            for day_key, value in daily_data.items():
                                if value and value.strip():  # 값이 있는 경우만 처리
                                    print(f"  {day_key}: {value}")
                
                items = {'success': True, 'message': '프로젝트 정보가 저장되었습니다.'}
                
            except Exception as ex:
                return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(ex)}'}

    except Exception as ex:
        source = 'api/sample_page/spreadSheet : action-{}'.format(action)
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
