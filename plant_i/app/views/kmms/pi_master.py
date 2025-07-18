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


from domain.services.common import CommonUtil
from domain.models.cmms import CmChkEquip

from domain.models.cmms import CmEquipChkItem

def pi_master(context):
    '''
    /api/kmms/pi_master
    
    작성명 : 점검마스터정보
    작성자 : 최성열
    작성일 : 
    비고 :

    findAll
    findOne
    '''

    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    pi_master_service = PIService()

    #점검마스터 저장
    # 저장의 경우 mybatis의 쿼리를 적용하지 않고 ORM으로 등록한다
    #java : 
    if action=='save':
        # 데이터 저장 로직        
        chk_mast_pk = posparam.get('chk_mast_pk')# pk 값을 가져옵니다. 없으면 None
        pi = None

        try:
            #------------점검마스터 등록
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
            
            # resultMax = pi_master_service.selectMaxEquipChkMastNo()
            ChkMastNo = generate_pi_number()

            # 데이터 저장2
            pi.ChkMastNo = ChkMastNo    
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



            #java : saveWithCascade
            #--------점검설비 등록
            #java : deleteByChkMastPk(equipChkMast.getChkMastPk());

            #chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            CmChkEquip.objects.filter(CmEquipChkMaster=pi.id).delete()  

            #java : chkEquipMapper.insertBatch(map);
            #chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            chkEquips =posparam.get('chkEquips')

            chkEquip_list = chkEquips.split(',')

            for item in chkEquip_list:
                equip_pk = CommonUtil.try_int(item)
                c = CmChkEquip()
                c.CmEquipChkMaster_id = pi.id
                c.CmEquipment_id = equip_pk
                #c.set_audit(user)
                c.save()


            #------------점검항목 등록
            #java : equipChkItemMapper.deleteUpdateBatch(map);
            ''' 등록 및 수정전에 삭제된것 삭제처리
            '''
            raw_items  = posparam.get('equipChkItems')

            try:
                equipChkItems = json.loads(raw_items)
            except (TypeError, json.JSONDecodeError):
                equipChkItems = []  # 또는 raise 예외처리


            #pk_list = equipChkItems.split(',')
            q = CmEquipChkItem.objects.filter(CmEquipChkMaster=pi.id)
            #choi : front에서 삭제하면 서버에는 빠지는 것들이 생김
            #q = q.exclude(id__in=pk_list)  
            q.delete()


            #equipChkItems 여러개 들어옴. 멀티 insert
            itemOrder = 1;
            for item in equipChkItems:
                chkItemUnitPk = CommonUtil.try_int(item.get('chkItemUnitPk'))
                #itemIdx = CommonUtil.try_int(item.get('itemIdx'))
                itemIdx = itemOrder;
                itemOrder = itemOrder + 1;   #1증가
                chkItemNm = item.get('chk_item_nm')
                lcl = item.get('lcl')
                ucl = item.get('ucl')
                method = item.get('method')
                guide = item.get('guide')
                #dailyReportItemCd = item.get('dailyReportItemCd')
                dailyReportItemCd = "test"

                c = CmEquipChkItem()

                #choi : ForeignKey의 경우 object가 아닌걸로 해도 됨. _id를 붙여야 함
                c.CmEquipChkMaster_id  = pi.id  
                c.ItemIdx = itemIdx
                c.ChkItemName = chkItemNm
                c.Lcl = lcl
                c.Ucl = ucl
                c.ChkItemUnitPk = chkItemUnitPk
                c.Method = method
                c.Guide = guide
                c.DailyReportItemCd = dailyReportItemCd
                c.set_audit(user)
                c.save()
            
            items = {'success': True, 'id': pi.id}

        except Exception as ex:
            source = 'api/kmms/pi_master, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex
    #점검마스터 조회
    #java : com.yullin.swing.inspection.domain.EquipChkMast 
    #     : equip-check-mast-mapper.xml
    elif action=='findAll':
        chkMastNo = gparam.get('chkMastNo', None)
        searchText = gparam.get('searchText', None)  
        equipDeptPk = gparam.get('equipDeptPk', None)
        locPk = gparam.get('locPk', None)
        deptPk = gparam.get('deptPk', None)
        useYn = gparam.get('useYn', None)
        cycleTypeCd = gparam.get('cycleTypes', None)       
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else ''
        environEquipYn = gparam.get('environEquipYn', None) 

        startDate = gparam.get('startDate', None)
        endDate = gparam.get('endDate', None)        

        #기타변수
        chkMastNm = gparam.get('chkMastNm', None)
        chkUserPk = gparam.get('chkUserPk', None)
        equipPk = gparam.get('equipPk', None)
        chkMastPk = gparam.get('chkMastPk', None)
        chkMastPkNot = gparam.get('chkMastPkNot', None)


        dcparam = {}
        dcparam['chkMastNo'] = chkMastNo
        dcparam['searchText'] = searchText
        dcparam['equipDeptPk'] = equipDeptPk
        dcparam['locPk'] = locPk
        dcparam['deptPk'] = deptPk
        dcparam['useYn'] = useYn
        dcparam['cycleTypeCd'] = cycleTypeCd
        dcparam['startDate'] = startDate
        dcparam['endDate'] = endDate
        dcparam['isMyTask'] = isMyTask
        dcparam['environEquipYn'] = environEquipYn


        #기타 변수
        dcparam['chkMastNm'] = chkMastNm
        dcparam['chkUserPk'] = chkUserPk
        dcparam['equipPk'] = equipPk
        dcparam['chkMastPk'] = chkMastPk
        dcparam['chkMastPkNot'] = chkMastPkNot        
        
        items = pi_master_service.findAll(dcparam)
    #점검상세 보기
    elif action=='findOne':
        chkMastPk = CommonUtil.try_int( gparam.get('chkMastPk') )
        items = pi_master_service.get_pi_master_detail(chkMastPk)
    #점검결과 보기
    elif action=='selectEquipResultList':

        chkMastPk = CommonUtil.try_int( gparam.get('chkMastPk') )

        sql = ''' 
        select ecs.chk_sche_pk						/* 점검일정Pk */
						, ecs.chk_sche_no 					/* 점검일정번호 */
						, ecm.chk_mast_pk 					/* 점검Pk */
						, cm_fn_user_nm(cu."Name", cu.del_yn) as chk_user_nm 		/* 점검담당자 */
						, bc.code_nm as chk_status_nm 		/* 점검상태 */
						, ecm.insert_ts as plan_insert_ts	/* 점검일정 생성일 */
						, ecs.chk_sche_dt					/* 점검계획일 */
						, ecs.chk_dt 						/* 점검완료일 */
						, count(distinct case when ecr.chk_rslt='A' then e.equip_pk else null end) as fail_count /* 점검이상 */
		from cm_equip_chk_sche ecs
		    inner join cm_equip_chk_mast ecm on ecs.chk_mast_pk=ecm.chk_mast_pk
		    inner join cm_base_code bc on ecs.chk_status=bc.code_cd and (bc.code_grp_cd='CHK_STATUS')
		    inner join cm_equip_chk_rslt ecr on ecs.chk_sche_pk=ecr.chk_sche_pk
		    inner join cm_equipment e on ecr.equip_pk=e.equip_pk
		    left outer join user_profile cu on ecs.chk_user_pk = cu."User_id"
		where 1=1
		    and ecm.chk_mast_pk = %(chkMastPk)s
		group by ecs.chk_sche_pk
				, ecs.chk_sche_no
				, ecm.chk_mast_pk
				, ecm.chk_mast_no
				, ecm.chk_mast_nm
				, cu."Name"
				, cu.del_yn
				, bc.code_nm
				, bc.code_cd
				, ecs.chk_sche_dt
				, ecs.chk_dt
		order by ecs.chk_sche_dt DESC
        '''

        try:
            items = DbUtil.get_rows(sql, {'chkMastPk':chkMastPk})
        except Exception as ex:
            LogWriter.add_dblog('error','PiService.selectEquipResultList', ex)
            raise ex
    #wo리스트 보기
    elif action=='selectEquipWoList':
        # id = gparam.get('id', None)
        # items = pi_master_service.get_pi_wo_detail(id)

        chkMastPk = CommonUtil.try_int( gparam.get('chkMastPk') )
        sql = ''' 
        select t.work_order_no				/* WO 번호 */
		        , woa.reg_dt 					/* WO 생성일 */
		        , ws.code_cd as wo_status_cd
		        , ws.code_nm as wo_status_nm  	/* WO 상태 */
		        , t.plan_start_dt 				/* 작업계획일 */
		        , t.end_dt 					/* 작업완료일 */
		        , ecm.chk_user_pk as chk_mast_pk
 		        , cm_fn_user_nm(pmu."Name", pmu.del_yn) as chk_user_nm		/* 담당자 */
        from cm_work_order t
	        inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
	        inner join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
	        inner join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
	        inner join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
	        inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
	        left outer join user_profile pmu on ecm.chk_user_pk = pmu."User_id"
        where ecm.chk_mast_pk = %(chkMastPk)s
	        and t.plan_start_dt < to_date(REPLACE(CURRENT_DATE::varchar, '-', ''), 'YYYYMMDD')
	        order by t.end_dt desc	/* 작업 완료일 */				
        '''

        try:
            items = DbUtil.get_rows(sql, {'chkMastPk':chkMastPk})
        except Exception as ex:
            LogWriter.add_dblog('error','PiService.get_pi_wo_detail', ex)
            raise ex

    #점검 결과 조회
    elif action=='findAllCheckResult':
        searchText = gparam.get('searchText', None)
        chkRslt = gparam.get('chkRslt', None)
        chkStatus = gparam.get('chkStatus', None)
        deptPk = gparam.get('deptPk', None)
        start_date = gparam.get('start_date', None)
        end_date = gparam.get('end_date', None)

        chk_legal = gparam.get('chk_legal', None)
        chk_my_task = gparam.get('chk_my_task', None)

        user_pk = user.id
        
        items = pi_master_service.findAllCheckResult(searchText, chkRslt, chkStatus, deptPk, start_date, end_date, chk_legal, chk_my_task, user_pk)

    #점검이상 발행WO 조회
    elif action=='findAllCheckWoIssued':
        searchText = gparam.get('searchText', None)
        chkScheNo = gparam.get('chkScheNo', None)
        workOrderNo = gparam.get('workOrderNo', None)
        deptPk = gparam.get('deptPk', None)
        equipDeptPk = gparam.get('equipDeptPk', None)

        environEquipYn = gparam.get('environEquipYn', None)
        myRequestYn = gparam.get('myRequestYn', None)
        
        start_date = gparam.get('start_date', None)
        end_date = gparam.get('end_date', None)

        user_pk = user.id

        items = pi_master_service.findAllCheckWoIssued(searchText, chkScheNo, deptPk, environEquipYn, equipDeptPk, myRequestYn, workOrderNo, start_date, end_date, user_pk)

    #점검일정생성(수동)에서 점검마스터 리스트
    elif action=='findAll4Schedule':    
        chkMastNo = gparam.get('chkMastNo', None)
        searchText = gparam.get('searchText', None)  
        equipDeptPk = gparam.get('equipDeptPk', None)
        deptPk = gparam.get('deptPk', None)
        useYn = gparam.get('useYn', None)
        isMyTask = user.id if gparam.get('isMyTask', None) == 'Y' else ''
        environEquipYn = gparam.get('environEquipYn', None) 
        lastChKdateYn = gparam.get('lastChKdateYn', None)

        startDate = gparam.get('startDate', None)
        endDate = gparam.get('endDate', None)

        lastChkDateFrom=""
        lastChkDateTo =""
        if lastChKdateYn == 'Y' :
            lastChkDateFrom = gparam.get('startDate', None)
            lastChkDateTo = gparam.get('endDate', None)
            
        dcparam = {}
        dcparam['chkMastNo'] = chkMastNo
        dcparam['searchText'] = searchText
        dcparam['equipDeptPk'] = equipDeptPk
        dcparam['deptPk'] = deptPk
        dcparam['useYn'] = useYn
        dcparam['isMyTask'] = isMyTask
        dcparam['environEquipYn'] = environEquipYn
        dcparam['lastChkDateFrom'] = lastChkDateFrom
        dcparam['lastChkDateTo'] = lastChkDateTo
        
        items = pi_master_service.findAll(dcparam)

    elif action == 'selectEquipChkScheSimulationCycleByMon':
        calDeptPk = gparam.get('calDeptPk', None)
        calChkUserPk = gparam.get('calChkUserPk', None)
        calSearchType = gparam.get('calSearchType', None)
        fromDate = gparam.get('calFromDate', None)
        toDate = gparam.get('calToDate', None)

        items = pi_master_service.selectEquipChkScheSimulationCycleByMon(calDeptPk, calChkUserPk,calSearchType,fromDate,toDate )

    elif action == 'selectEquipChkScheSimulationByMon':
        calDeptPk = gparam.get('calDeptPk', None)
        calChkUserPk = gparam.get('calChkUserPk', None)
        calSearchType = gparam.get('calSearchType', None)

        items = pi_master_service.selectEquipChkScheSimulationByMon(calDeptPk, calChkUserPk,calSearchType )

    return items

def generate_pi_number():
    today = datetime.today().strftime('%Y%m%d')
    prefix = f"PI-{today}-"
    
    # 오늘 날짜의 마지막 PM 번호 조회
    today_max_pi = CmEquipChkMaster.objects.filter(
        ChkMastNo__startswith=prefix,
        DelYn='N'  # 삭제되지 않은 데이터만
    ).order_by('-ChkMastNo').first()
    
    if today_max_pi:
        # 마지막 번호에서 순번 추출하여 1 증가
        last_sequence = int(today_max_pi.ChkMastNo[-3:])
        new_sequence = str(last_sequence + 1).zfill(3)
    else:
        # 해당 날짜의 첫 번호
        new_sequence = '001'
    
    ChkMastNo = f"{prefix}{new_sequence}"
    return ChkMastNo