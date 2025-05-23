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
            
            resultMax = pi_master_service.selectMaxEquipChkMastNo()

            # 데이터 저장2
            pi.ChkMastNo = resultMax["max_no"];    
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
                chkItemNm = item.get('chkItemNm')
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
        
        #(searchText, equipDeptPk, locPk, deptPk, isMyTask, isLegal,useYn,cycleTypeCd, chkMastNo,startDate,endDate)
        items = pi_master_service.findAll(dcparam)
    #점검일정생성(수동)에서 호출
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

    #점검등록>점검항목>점검항목선택
    #java : com.yullin.swing.inspection.infra.mapper.EquipChkItemTemplateMapper
    elif action == 'equipChkItemTemplatefindAll':

        keyword = gparam.get('keyword', None)
        dic_param = {'keyword':keyword}

        sql = ''' 
            select t.template_id
	            , t.chk_item
	            , t.unit
	            , t.group_code
	            , t.hash_tag
	            , bc.code_pk as chk_item_unit_pk
	            , t.insert_ts
	            , t.inserter_id
	            , t.update_ts
	            , t.updater_id
            from cm_chk_item_template t
            left outer join cm_base_code bc on t.unit = bc.code_nm and bc.code_grp_cd = 'CHK_ITEM_UNIT'
            where 1=1 
            --t.site_id = 1
            '''

        if keyword:
            sql+=''' 
                and (upper(t."chk_item") like concat('%%',upper(%(keyword)s),'%%')
                    or upper(t."hash_tag") like concat('%%',upper(%(keyword)s),'%%')
                    )
            '''
        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','equipChkItemTemplatefindAll', ex)
            raise ex

    #수동 점검스케줄 만들기
    #    java: com.yullin.swing.inspection.infra.mapper.EquipChkScheMapper
    elif action == 'executeMakeScheduleInsp':

        ''' ["1000","1002"] '''
        equipChkList = posparam.get('equipChkList').split(',')         
        
        #for문으로 아래를 반복실행
        for chkMastPk in equipChkList:
            
            scheType = posparam.get('scheType')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            
            sql = ''' select cm_fn_make_schedule_insp(%(scheType)s
		    , %(chkMastPk)s
		    , to_date(%(startDate)s, 'YYYYMMDD')
		    , to_date(%(endDate)s, 'YYYYMMDD')
		    , %(factory_pk)s )
            '''

            dc = {}
            dc['chkMastPk'] = chkMastPk
            dc['scheType'] = scheType
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['factory_pk'] = 1 #factory_id

            try:
                ret = DbUtil.execute(sql, dc)
            except Exception as ex:
                LogWriter.add_dblog('error','equipChkItemTemplatefindAll', ex)
                raise ex

        return {'success': True, 'message': '설비점검스케줄이 생성되었습니다.'}


    #java: com.yullin.swing.inspection.infra.mapper.EquipChkScheMapper
    elif action == 'checkScheduleAll':

            deptPk = CommonUtil.try_int(gparam.get('deptPk'))
            equipDeptPk = CommonUtil.try_int(gparam.get('equipDeptPk'))
            locPk = CommonUtil.try_int(gparam.get('locPk'))
            chkUserPk = CommonUtil.try_int(gparam.get('chkUserPk'))
            chkMastPk = CommonUtil.try_int(gparam.get('chkMastPk'))
            chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))
            chkSchePkNot = CommonUtil.try_int(gparam.get('chkSchePkNot'))
            unCheckedEquipPk = CommonUtil.try_int(gparam.get('unCheckedEquipPk'))

            searchText = gparam.get('searchText')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')
            chkMastNo = gparam.get('chkMastNo')
            chkScheNo = gparam.get('chkScheNo')
            environEquipYn = gparam.get('environEquipYn')
            chkStatusCd = gparam.get('chkStatusCd')
            chkScheDt = gparam.get('chkScheDt')
            chkStatus = gparam.get('chkStatus')
            calYn = gparam.get('calYn')

            sql = ''' select t.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
			, t.chk_sche_pk, t.chk_sche_no, t.chk_sche_dt
			, cs.code_cd as chk_status_cd, cs.code_nm as chk_status_nm
			, d.id as dept_pk, d."Name" as dept_nm
			, ecm.last_chk_date, ct.code_cd as cycle_type_cd, ct.code_nm as cycle_type_nm
			, concat(ecm.per_number, ct.code_dsc) as cycle_display_nm
			, ecm.per_number, t.chk_user_pk, fn_user_nm(cu."Name" , 'N') as chk_user_nm
			, t.chk_dt, t.factory_pk
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			, ecm.daily_report_cd, ecm.daily_report_type_cd
            , count(distinct case when ecr.chk_rslt='A' then e.equip_pk else null end) as fail_count
            '''
            if action == 'countBy':
                sql = ''' select count(*) as cnt
                '''
            sql += ''' from cm_equip_chk_sche t
			inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = t.chk_mast_pk
			left join cm_base_code ct on ct.code_cd = ecm.cycle_type
			    and ct.code_grp_cd = 'CYCLE_TYPE'
			left join dept d on d.id = t.dept_pk
			inner join cm_base_code cs on cs.code_cd = t.chk_status
			    and cs.code_grp_cd = 'CHK_STATUS'
			inner join cm_equip_chk_rslt ecr on ecr.chk_sche_pk = t.chk_sche_pk
			inner join cm_equipment e on e.equip_pk = ecr.equip_pk
			left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
			inner join cm_location l on l.loc_pk = e.loc_pk
			left join dept ed on ed.id = e.dept_pk
			left join user_profile cu on cu."User_id" = t.chk_user_pk 
		    where 1 = 1
            '''
            #choi : factory삭제
            #sql += ''' AND ecm.factory_pk = e.factory_pk 
		    #AND e.factory_pk = %(factory_pk)s
            #'''
            
            if searchText:
                sql += ''' AND (
				    UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				    OR
				    UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				    OR
				    UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				    OR
				    UPPER(ecm.chk_mast_no) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				    OR
				    UPPER(cast(t.chk_sche_no as text)) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )	
            '''
            if startDate and endDate:
                sql += ''' AND (t.chk_sche_dt >= to_date(%(startDate)s, 'YYYYMMDD') 
                AND t.chk_sche_dt <= to_date(%(endDate)s, 'YYYYMMDD'))
               '''
            if chkMastNo:
                sql += ''' AND ecm.chk_mast_no = %(chkMastNo)s
               '''
            if chkScheNo:
                sql += ''' AND t.chk_sche_no = %(chkScheNo)s
               '''
            if deptPk and deptPk > 0:
                sql += ''' AND (
					    d.id = %(deptPk)s
					    OR
					    d.id In (select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				    )
                '''
            if equipDeptPk and equipDeptPk > 0:
                sql += ''' AND (
					    ed.id = %(equipDeptPk)s
					    OR
					    ed.id In (select dept_pk from cm_v_dept_path where %(equipDeptPk)s = path_info_pk)
				    )
            '''
            if locPk and locPk > 0:
                sql += ''' AND (
					    l.loc_pk = %(locPk)s
					    OR
					    l.loc_pk In (select loc_pk from (select * from cm_fn_get_loc_path(33)) x where %(locPk)s = path_info_pk)
				    )
            '''
            if environEquipYn:
                sql += ''' AND e.environ_equip_yn = %(environEquipYn)s
                '''
            if chkUserPk and chkUserPk > 0:
                sql += ''' AND cu."User_id"  = %(chkUserPk)s
                '''
            if chkMastPk and chkMastPk > 0:
                sql += ''' AND t.chk_mast_pk = %(chkMastPk)s
                '''
            if chkSchePk and chkSchePk > 0:
                sql += ''' AND t.chk_sche_pk = %(chkSchePk)s
                '''
            if chkStatusCd:
                sql += ''' AND cs.code_cd = %(chkStatusCd)s
                '''
            if chkScheDt:
                sql += ''' AND TO_CHAR(t.chk_sche_dt, 'YYYY-MM-DD') = %(chkScheDt)s
                '''
            if chkSchePkNot and chkSchePkNot > 0:
                sql += ''' AND t.chk_sche_pk <> %(chkSchePkNot)s
                '''
            if unCheckedEquipPk and unCheckedEquipPk > 0:
                sql += ''' AND e.equip_pk = %(unCheckedEquipPk)s
			    AND cs.code_cd = 'CHK_STATUS_N'
			    AND t.chk_dt IS null
                '''
            if chkStatus:
                sql += ''' AND case when %(chkStatus)s = 'CHK_STATUS_NP' then cs.grp_cd else cs.code_cd end
                                =  case when %(chkStatus)s = 'CHK_STATUS_NP' then 'NP' when %(chkStatus)s = '' then cs.code_cd else %(chkStatus)s end
                '''
            sql += ''' group by t.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
			, t.chk_sche_pk, t.chk_sche_no, t.chk_sche_dt
			, cs.code_cd, cs.code_nm, d.id, d."Name" 
			, ecm.last_chk_date, ct.code_cd, ct.code_nm, ct.code_dsc
			, ecm.per_number, t.chk_user_pk, cu."Name" 
			-- , cu.del_yn
			, t.chk_dt, t.factory_pk 
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			, ecm.daily_report_cd, ecm.daily_report_type_cd
            '''
            if action == 'countBy':
                pass
            if action == 'searchOne':
                sql += ''' limit 1 '''
            elif calYn == 'Y':
                sql += ''' order by t.chk_mast_pk, t.chk_sche_pk, t.chk_sche_no, ecm.chk_mast_nm, ecm.chk_mast_no, t.chk_sche_dt, cs.code_cd
                '''

            dc = {}
            dc['searchText'] = searchText
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['chkMastNo'] = chkMastNo
            dc['chkScheNo'] = chkScheNo
            dc['deptPk'] = deptPk
            dc['equipDeptPk'] = equipDeptPk
            dc['locPk'] = locPk
            dc['environEquipYn'] = environEquipYn
            dc['chkUserPk'] = chkUserPk
            dc['chkMastPk'] = chkMastPk
            dc['chkSchePk'] = chkSchePk
            dc['chkStatusCd'] = chkStatusCd
            dc['chkScheDt'] = chkScheDt
            dc['chkSchePkNot'] = chkSchePkNot
            dc['unCheckedEquipPk'] = unCheckedEquipPk
            dc['chkStatus'] = chkStatus
            #dc['factory_pk'] = factory_id


            try:
                items = DbUtil.get_rows(sql, dc)
            except Exception as ex:
                LogWriter.add_dblog('error','checkScheduleAll', ex)
                raise ex

    
    #점검일정목록
    #java: com.yullin.swing.inspection.infra.mapper.EquipChkScheMapper
    elif action == 'searchEquipSchedule':
        chkMastPk = CommonUtil.try_int(gparam.get('chkMastPk'))
        chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))
        deptPk = CommonUtil.try_int(gparam.get('deptPk'))
        equipDeptPk = CommonUtil.try_int(gparam.get('equipDeptPk'))
        chkUserPk = CommonUtil.try_int(gparam.get('chkUserPk'))
        locPk = CommonUtil.try_int(gparam.get('locPk'))

        '''
        chkSchePkNot = CommonUtil.try_int(gparam.get('chkSchePkNot'))
        unCheckedEquipPk = CommonUtil.try_int(gparam.get('unCheckedEquipPk'))
        '''

        searchText = gparam.get('searchText')
        chkScheNo = gparam.get('chkScheNo')
        environEquipYn = gparam.get('environEquipYn')
        chkRslt = gparam.get('chkRslt')
        startDate = gparam.get('startDate')
        endDate = gparam.get('endDate')
        chkStatus = gparam.get('chkStatus')

        '''
        chkMastNo = gparam.get('chkMastNo')
            
            
        chkStatusCd = gparam.get('chkStatusCd')
        chkScheDt = gparam.get('chkScheDt')
            
        calYn = gparam.get('calYn')
        '''

        sql = ''' SELECT ecs.chk_sche_pk, ecs.chk_sche_no, ecm.chk_mast_pk
		, ecm.chk_mast_no, ecm.chk_mast_nm, d."Name" as dept_nm, fn_user_nm(cu."Name", 'N') as chk_user_nm
		, bc.code_nm as chk_status_nm, bc.code_cd as chk_status_cd, bc.code_cd as chk_status
		, ecm.last_chk_date, ecs.chk_sche_dt, ecs.chk_dt
		, count(distinct e.equip_pk) as equip_cnt
		, count(distinct eim.chk_item_pk) as item_cnt
		, count(distinct case when ecr.chk_rslt='N' then e.equip_pk else null end) as normal_count
		, count(distinct case when ecr.chk_rslt='A' then e.equip_pk else null end) as fail_count
		, count(distinct case when ecr.chk_rslt='C' then e.equip_pk else null end) as unable_check_count
		, count(distinct case when ecr.chk_rslt_file_grp_cd is not null then e.equip_pk else null end) as result_attach_count
		, count(wo.work_order_no) as wo_count
		FROM cm_equip_chk_sche ecs
		inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
		inner join cm_equip_chk_item_mst eim on eim.chk_sche_pk = ecs.chk_sche_pk
		left join dept d on d.id = ecs.dept_pk
		left join user_profile cu on cu."User_id" = ecs.chk_user_pk 
		inner join cm_base_code bc on bc.code_cd = ecs.chk_status 
			and bc.code_grp_cd='CHK_STATUS'
		inner join cm_equip_chk_rslt ecr on ecs.chk_sche_pk=ecr.chk_sche_pk
		inner join cm_equipment e on ecr.equip_pk=e.equip_pk
		left join dept ed on e.dept_pk = ed.id
		left join cm_work_order wo on ecr.chk_rslt_pk = wo.chk_rslt_pk 
			--and wo.factory_pk = 1
		WHERE 1=1 
            --and ecm.factory_pk = e.factory_pk
			--and e.factory_pk = 1
        '''
        if searchText:
            sql += ''' AND (
				UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(ecm.chk_mast_no) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				OR
				UPPER(cast(t.chk_sche_no as text)) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			)	
        '''
        # if chkMastNo:
        #     sql += ''' AND ecm.chk_mast_no = %(chkMastNo)s
        #     '''
        
        if chkScheNo:
            sql += ''' AND ecs.chk_sche_no = %(chkScheNo)s
            '''
        else:
           sql += '''                 
				AND date(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_Y' then ecs.chk_dt else ecs.chk_sche_dt end) >= to_date(%(startDate)s, 'YYYY-MM-DD')
               and date(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_Y' then ecs.chk_dt else ecs.chk_sche_dt end) <= to_date(%(endDate)s, 'YYYY-MM-DD')
            '''
         
            # AND case when %(chkStatus)s = 'CHK_STATUS_NP' then bc.grp_cd 
            #              else bc.code_cd 
            #         end 
            #         = 
            #         case when %(chkStatus)s = 'CHK_STATUS_NP' then 'NP' 
            #              when coalesce(%(chkStatus)s, '') = '' then bc.code_cd 
            #              else %(chkStatus)s 
            #         end

        
        if chkStatus:
            sql += ''' AND ecs.chk_status = %(chkStatus)s
            '''
        
        if deptPk and deptPk > 0:
            sql += ''' AND (
					d.id = %(deptPk)s
					OR
					d.id In (select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            '''
        if equipDeptPk and equipDeptPk > 0:
            sql += ''' AND (
					ed.id = %(equipDeptPk)s
					OR
					ed.id In (select dept_pk from cm_v_dept_path where %(equipDeptPk)s = path_info_pk)
				)
        '''
        if environEquipYn:
            sql += ''' AND e.environ_equip_yn = %(environEquipYn)s
            '''
        if chkUserPk and chkUserPk > 0:
            sql += ''' AND cu."User_id"  = %(chkUserPk)s
            '''
        if locPk and locPk > 0:
            sql += ''' AND (
					e.loc_pk = %(locPk)s
					OR
					e.loc_pk In (select loc_pk from (select * from cm_fn_get_loc_path(33)) x where %(locPk)s = path_info_pk)
				)
        '''
        if chkRslt in ['N','A','C']:
            sql += ''' AND ecr.chk_rslt = %(chkRslt)s
            '''
        sql += ''' GROUP BY ecs.chk_sche_pk, ecs.chk_sche_no, ecm.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
		, d."Name", cu."Name" 
		--, cu.del_yn
		, bc.code_nm, bc.code_cd, ecm.last_chk_date, ecs.chk_sche_dt, ecs.chk_dt
        '''
            

        dc = {}
        dc['searchText'] = searchText
        dc['startDate'] = startDate
        dc['endDate'] = endDate
        #dc['chkMastNo'] = chkMastNo
        dc['chkScheNo'] = chkScheNo
        dc['deptPk'] = deptPk
        dc['equipDeptPk'] = equipDeptPk
        dc['locPk'] = locPk
        dc['environEquipYn'] = environEquipYn
        dc['chkUserPk'] = chkUserPk
        #dc['chkMastPk'] = chkMastPk
        #dc['chkSchePk'] = chkSchePk
        #dc['chkStatusCd'] = chkStatusCd
        #dc['chkScheDt'] = chkScheDt
        #dc['chkSchePkNot'] = chkSchePkNot
        #dc['unCheckedEquipPk'] = unCheckedEquipPk
        dc['chkStatus'] = chkStatus
        #dc['factory_pk'] = factory_id

        try:
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','checkScheduleAll', ex)
            raise ex
        return {'success': True, 'data': items}

    elif action == 'selectEquipChkScheSimulationCycleByMon':
        calDeptPk = gparam.get('calDeptPk', None)
        calChkUserPk = gparam.get('calChkUserPk', None)
        calSearchType = gparam.get('calSearchType', None)

        items = pi_master_service.selectEquipChkScheSimulationCycleByMon(calDeptPk, calChkUserPk,calSearchType )

    elif action == 'selectEquipChkScheSimulationByMon':
        calDeptPk = gparam.get('calDeptPk', None)
        calChkUserPk = gparam.get('calChkUserPk', None)
        calSearchType = gparam.get('calSearchType', None)

        items = pi_master_service.selectEquipChkScheSimulationByMon(calDeptPk, calChkUserPk,calSearchType )

    return items


