from django.db import transaction
from domain.models.definition import Equipment, Material
from domain.models.user import Depart
from domain.services.sql import DbUtil
from domain.models.kmms import JobClass, PMWorker, PMMaterial, PreventiveMaintenance, User
from domain.services.kmms.pm_master import PMService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json


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
        equDept = gparam.get('equDept', None)
        equLoc = gparam.get('equLoc', None)
        pmDept = gparam.get('pmDept', None)
        pmType = gparam.get('pmType', None)
        applyYn = gparam.get('applyYn', None)
        cycleType = gparam.get('cycleType', None)
        sDay = gparam.get('sDay', None)
        eday = gparam.get('eday', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else ''
        isLegal = gparam.get('isLegal', None)
        
        items = pm_master_service.get_pm_master_list(keyword, equDept, equLoc, pmDept, pmType, applyYn, cycleType, sDay, eday, isMyTask, isLegal)

    elif action=='read_pm_sch':
        keyword = gparam.get('keyword', None)  
        equDept = gparam.get('equDept', None)
        equLoc = gparam.get('equLoc', None)
        pmDept = gparam.get('pmDept', None)
        pmType = gparam.get('pmType', None)
        applyYn = gparam.get('applyYn', None)
        cycleType = gparam.get('cycleType', None)
        sDay = gparam.get('sDay', None)
        eday = gparam.get('eday', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else None
        isLegal = gparam.get('isLegal', None)
        
        items = pm_master_service.get_pm_sch_list(keyword, equDept, equLoc, pmDept, pmType, applyYn, cycleType, sDay, eday, isMyTask, isLegal)

    elif action=='detail':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_master_detail(id)

    elif action=='detail_pm_labor':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_labor_detail(id)

    elif action=='detail_pm_mtrl':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_mtrl_detail(id)

    elif action=='read_modal':
        keyword = gparam.get('keyword', None)
        dept_pk = gparam.get('dept_pk', None)

        items = pm_master_service.get_pm_modal(keyword, dept_pk)

    elif action=='read_pm_wo':
        pm_pk = gparam.get('pm_pk', None)

        items = pm_master_service.get_pm_wo(pm_pk)

    # PM 작업오더 결재라인 /* findOne [work-order-approval-mapper.xml] */
    elif action=='read_work_order_summary':
        work_order_pk = gparam.get('id', None)

        items = pm_master_service.get_work_order_summary(work_order_pk)

    # PM 작업 결과 로그
    elif action=='read_work_order_hist':
        work_order_pk = gparam.get('id', None)

        items = pm_master_service.get_work_order_hist(work_order_pk)

    elif action=='save':
        # 데이터 저장 로직        
        pm_pk = posparam.get('pm_pk')# pk 값을 가져옵니다. 없으면 None
        pm = None

        try:

            if pm_pk:
                pm = PreventiveMaintenance.objects.filter(pm_pk=pm_pk).first()
                if not pm:
                    return JsonResponse({
                        'result': False,
                        'message': f"PM with pk {pm_pk} does not exist."
                    })

            else:
                # 새 객체 생성
                pm = PreventiveMaintenance()

            # 파라미터 가져오기
            pm_no = generate_pm_number()

            # 데이터 저장
            pm.pm_no = pm_no
            pm.Name = posparam.get('pmName')
            pm.PMType = posparam.get('pmType')            
            pm.WorkText = posparam.get('work_text')
            pm.schedStartDt = posparam.get('sched_start_dt')
            
            maintenance_time = posparam.get('maintenanceTime')
            if maintenance_time:
                pm.WorkExpectHour = int(maintenance_time)  # 숫자형으로 변환
            else:
                pm.WorkExpectHour = None  # 기본값 설정

            if pm.PMType == 'PM_TYPE_TBM':  # 주기유형이 주기일 경우
                pm.ScheduleStartDate = posparam.get('sched_start_dt')
                pm.CycleType = posparam.get('cycleType')
                pm.CyclePerNumber = posparam.get('per_number')

            dept_pk = posparam.get('dept_pk')
            pm_user_pk = posparam.get('pmManager')
            equip_pk = posparam.get('equip_pk')
    
            # 설비 필수값 체크
            if not equip_pk:
                return JsonResponse({
                    'result': False,
                    'message': '설비를 선택해주세요.'
                })

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
                user_id = User.objects.get(id=pm_user_pk)
            except User.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'User with id {pm_user_pk} does not exist.'
                })

            # Equipment 객체 가져오기
            try:
                equipment = Equipment.objects.get(id=equip_pk)
            except Equipment.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'Equipment with id {equip_pk} does not exist.'
                })

            pm.Depart = depart
            pm.PMUser= user_id
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
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='save_job_classes':
        try:
            pm_pk = posparam.get('pm_pk')
            job_classes = posparam.get('job_classes')            
            print("Received job_classes:", job_classes)  # 디버깅용
            
            if isinstance(job_classes, str):
                # JSON 문자열을 파이썬 객체로 변환
                job_classes = json.loads(job_classes)

            # PreventiveMaintenance 객체 가져오기
            pm_instance = PreventiveMaintenance.objects.get(pk=pm_pk) 

            # 저장할 PMWorker 객체 리스트 생성
            pm_labor_list = []

            for job_class in job_classes:
                job_class_pk = int(job_class.get('job_class_pk'))  # job_class_pk를 정수형 변환
                jc_instance = JobClass.objects.get(pk=job_class_pk)  # JobClass 객체 조회

                # PMWorker 객체 생성 (아직 DB에 저장하지 않음)
                pm_labor = PMWorker(
                    PreventiveMaintenance=pm_instance,  # ForeignKey 필드
                    JobClass=jc_instance,  # ForeignKey 필드
                    WorkHour=job_class.get('work_hr'),
                    _created=timezone.now()
                )

                # 리스트에 추가
                pm_labor_list.append(pm_labor)    
                
            #기존 pm_labor 삭제
            PMWorker.objects.filter(PreventiveMaintenance=pm_instance).delete()

            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            PMWorker.objects.bulk_create(pm_labor_list)
                
            ##########################################################
            # for job_class in job_classes:
            #     pm_labor = PMWorker()
            #     pm_labor.PreventiveMaintenance = pm_instance
            #     pm_labor._created = timezone.now()

            #     job_class_pk = int(job_class.get('job_class_pk'))
            #     jc_instance = JobClass.objects.get(pk=job_class_pk)
            #     pm_labor.JobClass = jc_instance  # ForeignKey는 객체를 할당해야 함

            #     pm_labor.WorkHour = job_class.get('work_hr')

            #     pm_labor.save()
            ##########################################################

            items = {'success': True}
            
        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='save_materials':
        try:
            pm_pk = posparam.get('pm_pk')
            materials = posparam.get('materials')            
            print("Received materials:", materials)  # 디버깅용
            
            if isinstance(materials, str):
                # JSON 문자열을 파이썬 객체로 변환
                materials = json.loads(materials)

            # PreventiveMaintenance 객체 가져오기
            pm_instance = PreventiveMaintenance.objects.get(pk=pm_pk) 

            # 저장할 PMWorker 객체 리스트 생성
            pm_mtrl_list = []

            for material in materials:
                mat_pk = int(material.get('mat_pk'))  # mat_pk를 정수형 변환
                mat_instance = Material.objects.get(pk=mat_pk)  # JobClass 객체 조회

                # PMWorker 객체 생성 (아직 DB에 저장하지 않음)
                pm_mtrl = PMMaterial(
                    PreventiveMaintenance=pm_instance,  # ForeignKey 필드
                    Material=mat_instance,  # not null      
                    Amount=material.get('mtrl_qty', 0),  # not null, 기본값 0

                    _status='C',  # not null
                    _created=timezone.now(),  # not null
                    _creater_id=request.user.id,  # not null
                    _creater_nm=request.user.username,  # not null                                 
                )

                # 리스트에 추가
                pm_mtrl_list.append(pm_mtrl)    
                
            #기존 pm_mtrl 삭제
            PMMaterial.objects.filter(PreventiveMaintenance=pm_instance).delete()

            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            PMMaterial.objects.bulk_create(pm_mtrl_list)    

            items = {'success': True}
            
        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    return items

def generate_pm_number():
    today = datetime.today().strftime('%Y%m%d')
    prefix = f"PM-{today}-"
    
    # 오늘 날짜의 마지막 PM 번호 조회
    today_max_pm = PreventiveMaintenance.objects.filter(
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




