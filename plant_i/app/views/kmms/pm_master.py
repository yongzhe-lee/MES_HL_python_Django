from django.db import transaction
from domain.models.cmms import CmEquipment, CmJobClass, CmMaterial, CmPm, CmPmLabor, CmPmMtrl, CmWorkOrder
from domain.models.system import User
from domain.models.user import Depart, UserProfile
from domain.services import common
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
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

    if action=='findAll':
        keyword = gparam.get('keyword', None)
        equDept = gparam.get('equDept', None)
        equLoc = gparam.get('equLoc', None)
        pmDept = gparam.get('pmDept', None)
        pmType = gparam.get('pmType', None)
        applyYn = gparam.get('applyYn', None)
        cycleType = gparam.get('cycleType', None)
        sDay = gparam.get('start_dt', None)
        eDay = gparam.get('end_dt', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else (None if gparam.get('isMyTask', None) == 'N' else '')
        isLegal = gparam.get('isLegal', None)

        items = pm_master_service.get_pm_master_list(keyword, equDept, equLoc, pmDept, pmType, applyYn, cycleType, sDay, eDay, isMyTask, isLegal)

    elif action=='findOne':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_master_findOne(id)
        items = items

    elif action=='selectPmScheSimulationCycleByMon':
        fromDate = gparam.get('fromDate', None)
        toDate = gparam.get('toDate', None)
        deptPk = gparam.get('deptPk', None)
        userPk = gparam.get('userPk', None)
        items = pm_master_service.selectPmScheSimulationCycleByMon(fromDate,toDate,deptPk,userPk)

    elif action=='selectPmScheSimulationByMon':
        fromDate = gparam.get('fromDate', None)
        toDate = gparam.get('toDate', None)
        deptPk = gparam.get('deptPk', None)
        userPk = gparam.get('userPk', None)
        items = pm_master_service.selectPmScheSimulationByMon(fromDate,toDate,deptPk,userPk)

    # WO 상세 작업내역 탭 #############################################################
    # 고장부위 목록 조회
    elif action=='read_breakdown_point':
        work_order_pk = gparam.get('id', None)
        items = pm_master_service.get_breakdown_point(work_order_pk)

    # WO 상세 작업 인력/자재 탭 ########################################################
    # 외주업체 목록 조회
    elif action == 'read_work_order_supplier':
        work_order_pk = gparam.get('id', None)
        items = pm_master_service.get_work_order_supplier(work_order_pk)

    # 작업인력 목록 조회
    elif action == 'read_work_order_manpower':
        work_order_pk = gparam.get('id', None)
        items = pm_master_service.get_work_order_manpower(work_order_pk)

    # 작업자재 목록 조회
    elif action == 'read_work_order_material':
        work_order_pk = gparam.get('id', None)
        items = pm_master_service.get_work_order_material(work_order_pk)
    ##################################################################################

    elif action=='findAllPm':
        keyword = gparam.get('keyword', None)
        equDept = gparam.get('equDept', None)
        equLoc = gparam.get('equLoc', None)
        pmDept = gparam.get('pmDept', None)
        pmType = gparam.get('pmType', None)
        woStatus = gparam.get('woStatus', None)
        sDay = gparam.get('start_date', None)
        eDay = gparam.get('end_date', None)
        equCategory = gparam.get('equCategory', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else (None if gparam.get('isMyTask', None) == 'N' else None)
        isLegal = None if gparam.get('isLegal', None) == 'N' else gparam.get('isLegal', None)

        items = pm_master_service.findAllPm(keyword, equDept, equLoc, pmDept, pmType, woStatus, sDay, eDay, equCategory, isMyTask, isLegal)

    elif action=='pm_work_findAll':
        keyword = gparam.get('keyword', None)
        srchPmNo = gparam.get('srchPmNo', None)
        srchWoNo = gparam.get('srchWoNo', None)
        pmType = gparam.get('pmType', None)
        equDept = gparam.get('equDept', None)
        pmDept = gparam.get('pmDept', None)
        sDay = gparam.get('start_dt', None)
        eDay = gparam.get('end_dt', None)
        srchEquCategory = gparam.get('srchEquCategory', None)
        isNotFinished = gparam.get('isNotFinished', None)
        isLegal = None if gparam.get('isLegal', None) == 'N' else gparam.get('isLegal', None)

        items = pm_master_service.pm_work_findAll(keyword, srchPmNo, srchWoNo, pmType, equDept, pmDept, sDay, eDay, srchEquCategory, isNotFinished, isLegal)

    elif action=='detail_pm_labor':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_labor_detail(id)

    elif action=='detail_pm_mtrl':
        id = gparam.get('id', None)
        items = pm_master_service.get_pm_mtrl_detail(id)

    elif action=='findSel':
        searchText = gparam.get('keyword', None)
        deptPk = gparam.get('dept_pk', None)
        pmUserPk = user.id

        items = pm_master_service.get_pm_findSel(searchText, deptPk, pmUserPk)
        items = CommonUtil.res_snake_to_camel(items)

    elif action=='read_pm_wo':
        pm_pk = gparam.get('pm_pk', None)

        items = pm_master_service.get_pm_wo(pm_pk)

    # PM 작업오더 결재라인 /* findOne [work-order-approval-mapper.xml] */
    elif action=='read_work_order_summary':
        work_order_pk = gparam.get('id', None)

        items = pm_master_service.pm_work_findOne(work_order_pk)

    # PM 작업 결과 로그
    elif action=='read_work_order_hist':
        work_order_pk = gparam.get('id', None)

        items = pm_master_service.get_work_order_hist(work_order_pk)

    elif action=='delete':
        try:
            PmPk = posparam.get('pm_pk')
            CmPm.objects.filter(PmPk=PmPk).delete()
            
            items = {'success': True}
            
        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            items = {'success': False, 'message': str(ex)}

    elif action=='disable':
        try:
            PmPk = posparam.get('pm_pk')
            pm = CmPm.objects.filter(PmPk=PmPk).first()
            
            if not pm:
                items = {'success': False, 'message': f"PM with pk {PmPk} does not exist."}
            else:
                pm.UseYn = 'N'
                pm.UpdateTs = timezone.now()
                pm.UpdaterId = request.user.id
                pm.UpdaterName = request.user.username
                pm.save()
                
                items = {'success': True}
            
        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            items = {'success': False, 'message': str(ex)}

    elif action=='enable':
        try:
            PmPk = posparam.get('pm_pk')
            pm = CmPm.objects.filter(PmPk=PmPk).first()
            
            if not pm:
                items = {'success': False, 'message': f"PM with pk {PmPk} does not exist."}
            else:
                pm.UseYn = 'Y'
                pm.UpdateTs = timezone.now()
                pm.UpdaterId = request.user.id
                pm.UpdaterName = request.user.username
                pm.save()
                
                items = {'success': True}
            
        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            items = {'success': False, 'message': str(ex)}

    elif action=='save':
        # 데이터 저장 로직
        pm_pk = posparam.get('pm_pk')# pk 값을 가져옵니다. 없으면 None
        pm = None

        try:

            if pm_pk:
                pm = CmPm.objects.filter(PmPk=pm_pk).first()
                if not pm:
                    return JsonResponse({
                        'result': False,
                        'message': f"PM with pk {pm_pk} does not exist."
                    })

            else:
                # 새 객체 생성
                pm = CmPm()

            # 파라미터 가져오기
            if not pm_pk:  # 신규 등록시 PM 번호 생성
                PmNo = generate_pm_number()
            else:
                PmNo = posparam.get('pm_no')

            # 데이터 저장
            pm.PmNo = PmNo
            pm.PmName = posparam.get('pm_nm')
            pm.PmType = posparam.get('pm_type_cd')
            pm.WorkText = posparam.get('work_text')

            work_expect_hr = posparam.get('work_expect_hr')
            if work_expect_hr:
                pm.WorkExpectHr = int(work_expect_hr)  # 숫자형으로 변환
            else:
                pm.WorkExpectHr = None  # 기본값 설정

            if pm.PmType == 'PM_TYPE_TBM':  # 주기유형이 주기일 경우
                pm.SchedStartDt = posparam.get('sched_start_dt')
                pm.CycleType = posparam.get('cycle_type_cd')
                pm.PerNumber = CommonUtil.try_int(posparam.get('per_number'))

            dept_pk = CommonUtil.try_int(posparam.get('dept_pk'))
            pm_user_pk = CommonUtil.try_int(posparam.get('pm_user_pk'))
            equip_pk = CommonUtil.try_int(posparam.get('equip_pk'))

            depart = Depart.objects.get(id=dept_pk)
            user_profile = UserProfile.objects.get(User_id=pm_user_pk)
            equipment = CmEquipment.objects.get(id=equip_pk)

            pm.DeptPk = depart.id
            pm.PmUserPk = user_profile.User_id
            pm.CmEquipment = equipment

            pm.UseYn = 'Y'
            pm.DelYn = 'N'

            if not pm_pk:  # 신규 등록시
                pm.InsertTs = timezone.now()
                pm.InserterId = request.user.id
                pm.InserterName = request.user.username
            else:  # 수정시
                pm.UpdateTs = timezone.now()
                pm.UpdaterId = request.user.id
                pm.UpdaterName = request.user.username

            pm.save()

            items = {'success': True, 'id': pm.PmPk}

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
            pm_instance = CmPm.objects.get(pk=pm_pk)

            # 저장할 CmPmLabor 객체 리스트 생성
            pm_labor_list = []

            for job_class in job_classes:
                job_class_pk = int(job_class.get('job_class_pk'))  # job_class_pk를 정수형 변환
                jc_instance =CmJobClass.objects.get(pk=job_class_pk)

                # CmPmLabor 객체 생성 (아직 DB에 저장하지 않음)
                pm_labor = CmPmLabor(
                    CmPm=pm_instance,  # ForeignKey 필드
                    CmJobClass=jc_instance,  # ForeignKey 필드
                    WorkHr=CommonUtil.try_float(job_class.get('work_hr', 0)),  # not null, 기본값 0
                )

                # 리스트에 추가
                pm_labor_list.append(pm_labor)

            #기존 pm_labor 삭제
            CmPmLabor.objects.filter(CmPm=pm_instance).delete()

            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            CmPmLabor.objects.bulk_create(pm_labor_list)

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
            pm_instance = CmPm.objects.get(pk=pm_pk)

            # 저장할 CmPmLabor 객체 리스트 생성
            pm_mtrl_list = []

            for material in materials:
                mat_pk = int(material.get('mat_pk'))  # mat_pk를 정수형 변환
                mat_instance = CmMaterial.objects.get(pk=mat_pk)

                # CmPmLabor 객체 생성 (아직 DB에 저장하지 않음)
                pm_mtrl = CmPmMtrl(
                    CmPm=pm_instance,  # ForeignKey 필드
                    CmMaterial=mat_instance,  # not null
                    Amt=material.get('mtrl_qty', 0),  # not null, 기본값 0      
                )

                # 리스트에 추가
                pm_mtrl_list.append(pm_mtrl)

            #기존 pm_mtrl 삭제
            CmPmMtrl.objects.filter(CmPm=pm_instance).delete()

            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            CmPmMtrl.objects.bulk_create(pm_mtrl_list)

            items = {'success': True}

        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='save_work_order':
        # 데이터 저장 로직
        work_order_pk = posparam.get('work_order_pk')# pk 값을 가져옵니다. 없으면 None
        wo = None

        try:

            if work_order_pk:
                wo = CmWorkOrder.objects.filter(work_order_pk=work_order_pk).first()
                if not wo:
                    return JsonResponse({
                        'result': False,
                        'message': f"WO with pk {work_order_pk} does not exist."
                    })

            else:
                # 새 객체 생성
                wo = CmWorkOrder()

            # 데이터 저장
            # Depart 객체 가져오기
            dept_pk = posparam.get('wo_dept_pk')
            try:
                depart = Depart.objects.get(id=dept_pk)
            except Depart.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'Depart with id {dept_pk} does not exist.'
                })

            wo.Depart = depart

            # User 객체 가져오기
            work_charger_pk = posparam.get('wo_work_charger_sel')
            try:
                user_id = User.objects.get(id= work_charger_pk)
            except User.DoesNotExist:
                return JsonResponse({
                    'result': False,
                    'message': f'User with id {work_charger_pk} does not exist.'
                })

            wo.WorkCharger = user_id

            wo.plan_start_dt = posparam.get('wo_plan_start_dt')
            wo.plan_end_dt = posparam.get('wo_plan_end_dt')
            wo.start_dt = posparam.get('wo_start_dt')
            wo.end_dt = posparam.get('wo_end_dt')
            wo.MaintenanceTypeCode = posparam.get('wo_maint_type_cd')
            wo.CauseCode = posparam.get('wo_cause_sel')
            wo.ProblemCode = posparam.get('wo_problem_sel')
            wo.RemedyCode = posparam.get('wo_remedy_sel')
            wo.proj_cd = posparam.get('wo_proj_sel')
            wo.WorkSourcingCode = posparam.get('wo_work_src_sel')
            wo.WorkText = posparam.get('wo_work_text')

            if not work_order_pk:  # 신규 등록시
                wo._status = 'C'
                wo._created = timezone.now()
                wo._creater_id = request.user.id
                wo._creater_nm = request.user.username
            else:  # 수정시
                wo._status = 'U'
                wo._modified = timezone.now()
                wo._modifier_id = request.user.id
                wo._modifier_nm = request.user.username

            wo.save()

            items = {'success': True, 'id': wo.work_order_pk}

        except Exception as ex:
            source = 'api/kmms/pm_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='executeMakeSchedulePm':
        sche_type = posparam.get('sche_type', None)
        pm_pk_list = posparam.get('pm_pks', None)
        if pm_pk_list and isinstance(pm_pk_list, str):
            pm_pk_list = pm_pk_list.split(',')
        else:
            pm_pk_list = []
        start_date = posparam.get('start_date', None)
        end_date = posparam.get('end_date', None)
        items = pm_master_service.executeMakeSchedulePm(sche_type, pm_pk_list, start_date, end_date)

    return items

def generate_pm_number():
    today = datetime.today().strftime('%Y%m%d')
    prefix = f"PM-{today}-"

    # 오늘 날짜의 마지막 PM 번호 조회
    today_max_pm = CmPm.objects.filter(
        PmNo__startswith=prefix,
        DelYn='N'  # 삭제되지 않은 데이터만
    ).order_by('-PmNo').first()

    if today_max_pm:
        # 마지막 번호에서 순번 추출하여 1 증가
        last_sequence = int(today_max_pm.PmNo[-3:])
        new_sequence = str(last_sequence + 1).zfill(3)
    else:
        # 해당 날짜의 첫 번호
        new_sequence = '001'

    PmNo = f"{prefix}{new_sequence}"
    return PmNo
