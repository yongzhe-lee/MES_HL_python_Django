from django.db import transaction
from domain.models.definition import Equipment
from domain.services.sql import DbUtil
from domain.models.kmms import PreventiveMaintenace
from domain.services.kmms.pm_master import PMService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime


def pm_master(context):
    '''
    /api/kmms/pm_master
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    pm_master_service = PMService()

    if action=='read':
        keyword = gparam.get('keyword', None)       
        
        items = pm_master_service.get_pm_master_list(keyword)

    elif action=='detail':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_master_detail(id)

    elif action=='read_modal':
        keyword = gparam.get('keyword', None)
        dept_id = gparam.get('dept_id', None)

        items = pm_master_service.get_pm_modal(keyword, dept_id)

    elif action=='save':
        # 데이터 저장 로직        
        pm_pk = posparam.get('pm_pk')# pk 값을 가져옵니다. 없으면 None
        pm = None

        try:

            if pm_pk:
                pm = PreventiveMaintenace.objects.filter(pm_pk=pm_pk).first()
                if not pm:
                    return JsonResponse({
                        'result': False,
                        'message': f"PM with pk {pm_pk} does not exist."
                    })
            else:
                # 새 객체 생성
                pm = PreventiveMaintenace()

            # 파라미터 가져오기
            pm_no = generate_pm_number()

            # 데이터 저장
            pm.pm_no = pm_no
            pm.Name = posparam.get('pmName')
            pm.PMType = posparam.get('pmType')
            pm.WorkText = posparam.get('work_text')
            pm.maintenanceTime = posparam.get('maintenanceTime')
            pm.dept_id = posparam.get('dept_id')
            pm.pm_user_id = posparam.get('pmManager')            
            # pm.equ_id = int(posparam.get('equ_id', 0))  # 기본값 0을 설정하여 NULL 방지

            # 파라미터 가져오기
            equ_id = posparam.get('equ_id')
    
            # 설비 필수값 체크
            if not equ_id:
                return JsonResponse({
                    'result': False,
                    'message': '설비를 선택해주세요.'
                })

            # Equipment 객체 가져오기
            try:
                equipment = Equipment.objects.get(id=equ_id)
            except Equipment.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'Equipment with id {equ_id} does not exist.'
                })

            pm.Equipment = equipment

            pm.UseYN = 'Y'
            pm.DeleteYN = 'N'
        
            if not pm_pk:  # 신규 등록시
                pm._status = 'C'
                pm._created = timezone.now()
                pm._creater_id = request.user.id
                pm._creater_nm = request.user.username
            else:  # 수정시
                pm._status = 'U'
                pm._modified = timezone.now()
                pm._modifier_id = request.user.id
                pm._modifier_nm = request.user.username

            pm.save()

            items = {'success': True, 'id': pm.pm_pk}

        except Exception as ex:
            source = 'api/definition/equipment, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    return items

def generate_pm_number():
    today = datetime.today().strftime('%Y%m%d')
    prefix = f"PM-{today}-"
    
    # 오늘 날짜의 마지막 PM 번호 조회
    today_max_pm = PreventiveMaintenace.objects.filter(
        pm_no__startswith=prefix,
        DeleteYN='N'  # 삭제되지 않은 데이터만
    ).order_by('-pm_no').first()
    
    if today_max_pm:
        # 마지막 번호에서 순번 추출하여 1 증가
        last_sequence = int(today_max_pm.pm_no[-4:])
        new_sequence = str(last_sequence + 1).zfill(4)
    else:
        # 해당 날짜의 첫 번호
        new_sequence = '001'
    
    pm_no = f"{prefix}{new_sequence}"
    return pm_no