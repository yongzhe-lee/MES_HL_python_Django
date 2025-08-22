from django.db import transaction
from domain.services.common import CommonUtil
from domain.services.kmms.mig_spreadsheet import SpreadSheetService
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil

from domain.models.cmms import CmMigDept
from django.shortcuts import render

import os
import uuid
from django.db import transaction
from django.http import JsonResponse
from configurations import settings
import pandas as pd

def mig_spreadsheet(context):
    '''
    /api/kmms/mig_spreadsheet
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action') or posparam.get('action') or 'read'
    request = context.request
    user = request.user

    spreadSheet_Service = SpreadSheetService()    

    try:
        if action == 'read': 
            migrationType = gparam.get('migrationType', None)

            if migrationType == 'DEPT':
                items = spreadSheet_Service.read_dept()
            elif migrationType == 'USER_INFO':
                items = spreadSheet_Service.read_user_info()

        elif action == 'submit':
            # 스프레드시트에서 전송된 데이터 처리
            print("posparam:", posparam)
            migrationType = posparam.get('migrationType', None)

            if migrationType == 'DEPT':
                print("부서 마이그레이션 데이터 처리 시작")
            
                # 먼저 모든 기존 데이터 삭제
                try:
                    with transaction.atomic():
                        # 기존 데이터 모두 삭제
                        deleted_count = CmMigDept.objects.all().delete()[0]
                        print(f"기존 데이터 {deleted_count}개 삭제 완료")
                    
                        # 시퀀스 초기화
                        from django.db import connection
                        with connection.cursor() as cursor:
                            cursor.execute("ALTER SEQUENCE cm_mig_dept_pk_seq RESTART WITH 1;")
                        print("시퀀스 초기화 완료")
                except Exception as ex:
                    print(f"기존 데이터 삭제 및 시퀀스 초기화 오류: {str(ex)}")
                    return {'success': False, 'message': f'기존 데이터 삭제 중 오류가 발생했습니다: {str(ex)}'}
            
                # 평면화된 데이터를 파싱하여 배열로 변환
                data = []
                i = 0
                while True:
                    pk_key = f'data[{i}][pk]'
                    if pk_key not in posparam:
                        break
                
                    item = {
                        'pk': posparam.get(f'data[{i}][pk]', ''),         
                        'action_type': posparam.get(f'data[{i}][action_type]', ''),
                        'dept_cd': posparam.get(f'data[{i}][dept_cd]', ''),
                        'dept_nm': posparam.get(f'data[{i}][dept_nm]', ''),
                        'up_dept_cd': posparam.get(f'data[{i}][up_dept_cd]', ''),
                        'up_dept_nm': posparam.get(f'data[{i}][up_dept_nm]', ''),
                        'business_yn': posparam.get(f'data[{i}][business_yn]', ''),
                        'team_yn': posparam.get(f'data[{i}][team_yn]', ''),
                        'tpm_yn': posparam.get(f'data[{i}][tpm_yn]', ''),
                        'cc_cd': posparam.get(f'data[{i}][cc_cd]', ''),
                        'site_id': posparam.get(f'data[{i}][site_id]', '')
                    }
                    data.append(item)
                    print(f"파싱된 데이터 {i+1}: {item}")
                    i += 1
            
                print(f"총 파싱된 데이터 개수: {len(data)}")
            
                if not data:
                    return {'success': False, 'message': '저장할 데이터가 없습니다.'}
            
                # 새로운 데이터 저장
                saved_count = 0
                try:
                    for item in data:
                        pk = item.get('pk')               
                        action_type = item.get('action_type')
                        dept_cd = item.get('dept_cd')
                        dept_nm = item.get('dept_nm')
                        up_dept_cd = item.get('up_dept_cd')
                        up_dept_nm = item.get('up_dept_nm')
                        business_yn = item.get('business_yn')
                        team_yn = item.get('team_yn')
                        tpm_yn = item.get('tpm_yn')
                        cc_cd = item.get('cc_cd')
                        site_id = item.get('site_id')                    
           
                        # No 컬럼 값을 pk로 사용
                        new_pk = int(pk) if pk and pk.isdigit() else None
                        
                        print(f"처리 중: no={pk}, new_pk={new_pk}, dept_cd={dept_cd}")
                        
                        if new_pk:
                            try:
                                # 새로운 pk로 생성
                                c = CmMigDept()
                                c.pk = new_pk                                
                                c.ActionType = action_type
                                c.DeptCd = dept_cd
                                c.DeptNm = dept_nm
                                c.UpDeptCd = up_dept_cd
                                c.UpDeptNm = up_dept_nm
                                c.BusinessYn = business_yn
                                c.TeamYn = team_yn
                                c.TpmYn = tpm_yn
                                c.CcCd = cc_cd
                                c.SiteId = site_id
                                c.UserId = user.username  # request.user에서 가져오기
                                c.InsertTs = DateUtil.get_current_datetime()  # 현재 시간
                                c.Msg = 'inserted'  # 새로운 pk로 생성하므로 항상 inserted
                                
                                c.save()
                                saved_count += 1
                                print(f"데이터 저장 완료: pk={new_pk}, dept_cd={dept_cd}")
                            except Exception as ex:
                                print(f"데이터 저장 오류 (pk={new_pk}): {str(ex)}")
                                continue
                        else:
                            print(f"No 컬럼 값이 유효하지 않음: pk={new_pk}")
       
                    # 마이그레이션 프로시저 실행
                    migration_result = spreadSheet_Service.migrate_dept()
                
                    # 마이그레이션 결과를 saved_count에 반영
                    if migration_result and isinstance(migration_result, (list, tuple)) and len(migration_result) > 0:
                        saved_count = len(migration_result)
                    elif migration_result and isinstance(migration_result, int):
                        saved_count = migration_result
                
                    print(f"최종 saved_count: {saved_count}")
                
                    # 결과 반환
                    items = {
                        'success': True, 
                        'message': f'부서 마이그레이션 정보가 저장되었습니다. (저장된 데이터: {saved_count}개)'
                    }
                
                except Exception as ex:
                    return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(ex)}'}

            elif migrationType == 'USER_INFO':
                print("사용자 마이그레이션 데이터 처리 시작")

    except Exception as ex:
        source = 'api/kmms/mig_spreadsheet : action-{}'.format(action)
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
