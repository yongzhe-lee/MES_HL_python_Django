from django.db import transaction
from domain.services.sql import DbUtil
from domain.models.user import Depart, User
# from domain.models.kmms import PreventiveMaintenance  
from domain.models.cmms import CmEquipChkMaster
from domain.services.kmms.pi_master import PIService
# from domain.services.file import FileService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json

def pi_master(context):
    '''
    /api/kmms/pi_master
    
    작성명 : 점검마스터정보
    작성자 : 최성열
    작성일 : 
    비고 :

    -수정사항-
    수정일             작업자     수정내용

    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    pi_master_service = PIService()

    #저장의 경우 mybatis의 쿼리를 적용하지 않고 ORM으로 등록한다
    if action=='save':
        # 데이터 저장 로직        
        chk_mast_pk = posparam.get('chk_mast_pk')# pk 값을 가져옵니다. 없으면 None
        pi = None

        try:
            if chk_mast_pk:
                pi = CmEquipChkMaster.objects.filter(chk_mast_pk=chk_mast_pk).first()
                if not pi:
                    return JsonResponse({
                        'result': False,
                        'message': f"pi with pk {chk_mast_pk} does not exist."
                    })
            else:
                # 새 객체 생성
                pi = CmEquipChkMaster()

            # 파라미터 가져오기
            
            result = pi_master_service.selectMaxEquipChkMastNo()

            # 데이터 저장2
            pi.ChkMastNo = result["max_no"];    
            pi.ChkMastName = posparam.get('piName')          
            pi.WorkText = posparam.get('work_text')
            pi.SchedStartDate = posparam.get('schedStartDt')
            pi.CycleType = posparam.get('cycleType')
            pi.PerNumber = posparam.get('perNumber')

            dept_pk = posparam.get('dept_pk')
            chk_user_pk = posparam.get('piManager')
            
            # Depart 객체 가져오기
            try:
                depart = Depart.objects.get(id=dept_pk)
            except Depart.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'Depart with id {dept_pk} does not exist.'
                })

            # User 객체 가져오기
            try:
                user_id = User.objects.get(id=chk_user_pk)
            except User.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'User with id {chk_user_pk} does not exist.'
                })
            
            pi.DeptPk = dept_pk
            pi.ChkUserPk= chk_user_pk
            
            pi.SiteId = '1'
            pi.UseYn = 'Y'
            pi.DelYn = 'N'           
        
            if not chk_mast_pk:  # 신규 등록시
                pi.InsertTs = timezone.now()
                pi.InserterId = request.user.id
                pi.InserterNm = request.user.username
            else:  # 수정시
                pi.UpdateTs = timezone.now()
                pi.UpdaterId = request.user.id
                pi.UpdaterNm = request.user.username

            pi.save()

            items = {'success': True, 'id': pi.id}

        except Exception as ex:
            source = 'api/kmms/pi_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex
        
    elif action=='read':
        chkMastNo = gparam.get('chkMastNo', None)
        searchText = gparam.get('searchText', None)  
        equipDeptPk = gparam.get('equipDeptPk', None)
        locPk = gparam.get('locPk', None)
        deptPk = gparam.get('deptPk', None)
        useYn = gparam.get('useYn', None)
        cycleTypeCd = gparam.get('cycleTypes', None)        
        startDate = gparam.get('startDate', None)
        endDate = gparam.get('endDate', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else ''
        isLegal = gparam.get('isLegal', None)
        
        items = pi_master_service.findAll(searchText, equipDeptPk, locPk, deptPk, isMyTask, isLegal,useYn,cycleTypeCd, chkMastNo,startDate,endDate)

    



    return items


