from django import db
from domain.services.date import DateUtil
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipChkSche
#from symbol import factor

def equip_chk_sche(context):
    '''
    api/kmms/equip_chk_sche    설비점검스케줄
    김태영 

    findAll
    findOne
    searchOne
    countBy
    insert
    update
    updateChkScheDt
    updateEquipChkScheStatus
    updateChkUser
    finishEquipChkSche
    delete
    executeMakeScheduleInsp
    getEquipChkItemInfo
    selectMaxChkScheNo
    findReferencedTablesInfo
    searchEquipSchedule
    selectEquipResult
    getDailyReportResult
    getDailyVibListByeChkSchePk
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['findAll', 'searchOne', 'countBy']:
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
			, ecm.per_number, t.chk_user_pk, cm_fn_user_nm(cu."Name" , 'N') as chk_user_nm
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
            sql += ''' AND ecm.factory_pk = e.factory_pk 
		    AND e.factory_pk = %(factory_pk)s
            '''
            if searchText:
                sql += ''' AND (
				    UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%')
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
            if deptPk > 0:
                sql += ''' AND (
					    d.id = %(deptPk)s
					    OR
					    d.id In (select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				    )
                '''
            if equipDeptPk > 0:
                sql += ''' AND (
					    ed.id = %(equipDeptPk)s
					    OR
					    ed.id In (select dept_pk from cm_v_dept_path where %(equipDeptPk)s = path_info_pk)
				    )
            '''
            if locPk > 0:
                sql += ''' AND (
					    l.loc_pk = %(locPk)s
					    OR
					    l.loc_pk In (select loc_pk from (select * from cm_fn_get_loc_path(33)) x where %(locPk)s = path_info_pk)
				    )
            '''
            if environEquipYn:
                sql += ''' AND e.environ_equip_yn = %(environEquipYn)s
                '''
            if chkUserPk > 0:
                sql += ''' AND cu."User_id"  = %(chkUserPk)s
                '''
            if chkMastPk > 0:
                sql += ''' AND t.chk_mast_pk = %(chkMastPk)s
                '''
            if chkSchePk > 0:
                sql += ''' AND t.chk_sche_pk = %(chkSchePk)s
                '''
            if chkStatusCd:
                sql += ''' AND cs.code_cd = %(chkStatusCd)s
                '''
            if chkScheDt:
                sql += ''' AND TO_CHAR(t.chk_sche_dt, 'YYYY-MM-DD') = %(chkScheDt)s
                '''
            if chkSchePkNot > 0:
                sql += ''' AND t.chk_sche_pk <> %(chkSchePkNot)s
                '''
            if unCheckedEquipPk > 0:
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
            dc['factory_pk'] = factory_id

            if action == '':
                items = DbUtil.get_rows(sql, dc)
            else:
                items = DbUtil.get_row(sql, dc)
                if action == 'countBy':
                    return items['cnt']
 

        elif action == 'findOne':
            chkSchePk = CommonUtil.try_int( gparam.get('chkSchePk') )

            sql = ''' select t.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
			, t.chk_sche_pk, t.chk_sche_no, t.chk_sche_dt
			, cs.code_cd as chk_status_cd, cs.code_nm as chk_status_nm
			, d.id as dept_pk, d."Name" as dept_nm
			, ecm.last_chk_date, ct.code_cd as cycle_type_cd, ct.code_nm as cycle_type_nm
			, concat(ecm.per_number, ct.code_dsc) as cycle_display_nm
			, ecm.per_number, t.chk_user_pk, cm_fn_user_nm(cu."Name" , 'N') as chk_user_nm
			, t.chk_dt, t.factory_pk
			, t.insert_ts, t.inserter_id, t.inserter_nm
			, t.update_ts, t.updater_id, t.updater_nm
			, ecm.daily_report_cd, ecm.daily_report_type_cd
            --, count(distinct case when ecr.chk_rslt='A' then e.equip_pk else null end) as fail_count
            , count(ecr.chk_rslt_pk) as equip_count
		    , (select count(*) 
                    from cm_equip_chk_item_mst ecim 
                    where ecim.chk_sche_pk = t.chk_sche_pk) as item_count
			from cm_equip_chk_sche t
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
                AND t.chk_sche_pk = %(chkSchePk)s
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
            

            dc = {}
            dc['chkSchePk'] = chkSchePk

            try:
                items = DbUtil.get_rows(sql, dc)
            except Exception as ex:
                LogWriter.add_dblog('error','findOne', ex)
                raise ex

            return {'success': True, 'data': items}

        elif action in ['insert', 'update']:
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            deptPk = CommonUtil.try_int(posparam.get('deptPk'))
            chkUserPk = CommonUtil.try_int(posparam.get('chkUserPk'))

            chkScheNo = posparam.get('chkScheNo')
            chkScheDt = posparam.get('chkScheDt')
            chkStatusCd = posparam.get('chkStatusCd')

            if action == 'update':
                c = CmEquipChkSche.objects.get(id=chkSchePk)
            else:
                c = CmEquipChkSche()
                c.ChkScheNo = chkScheNo
                c.ChkUserPk = chkUserPk
                c.CmEquipChkMaster_id = chkMastPk
                c.ChkStatus = chkStatusCd
                c.Factory_id = factory_id
            
            c.DeptPk = deptPk
            c.ChkScheDt = chkScheDt
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비점검스케줄이 등록되었습니다.'}

        elif action == 'updateEquipChkScheStatus':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            
            sql = ''' update cm_equip_chk_sche
			set chk_status = (case when
			    (select max(case when chk_rslt is null then 0 else 1 end)
			    	from cm_equip_chk_rslt t where t.chk_sche_pk = %(chkSchePk)s) > 0
			    		then 'CHK_STATUS_P' else chk_status end)
			where chk_sche_pk = %(chkSchePk)s
			and chk_status = 'CHK_STATUS_N'
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            ret = DbUtil.execute(sql, dc)

            return {'success': True, 'message': '설비점검스케줄이 수정되었습니다.'}

        elif action == 'updateChkScheDt':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkScheDt = posparam.get('chkScheDt')

            cr = CmEquipChkSche.objects.get(id=chkSchePk)
            cr.ChkScheDt = chkScheDt
            cr.save()

            return {'success': True, 'message': '설비점검스케줄이 수정되었습니다.'}

        elif action == 'updateChkUser':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkUserPk = CommonUtil.try_int(posparam.get('chkUserPk'))
            deptPk = CommonUtil.try_int(posparam.get('deptPk'))

            cr = CmEquipChkSche.objects.get(id=chkSchePk)
            cr.ChkUserPk = chkUserPk
            cr.DeptPk = deptPk
            cr.save()

            return {'success': True, 'message': '설비점검스케줄이 수정되었습니다.'}

        elif action == 'finishEquipChkSche':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkUserPk = CommonUtil.try_int(posparam.get('chkUserPk'))
            chkStatusCd = posparam.get('chkStatusCd')
            chkDt = posparam.get('chkDt')

            if chkStatusCd == 'CHK_STATUS_Y':
                pass
            else:
                chkDt = DateUtil.get_current_datetime()

            cr = CmEquipChkSche.objects.get(id=chkSchePk)
            cr.ChkStatus = chkStatusCd
            cr.ChkUserPk = chkUserPk
            cr.ChkDt = chkDt
            cr.save()

            return {'success': True, 'message': '설비점검스케줄이 수정되었습니다.'}

        elif action == 'delete':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            CmEquipChkSche.objects.filter(id=chkSchePk).delete()

            items = {'success': True}
    
        #수동 점검스케줄 만들기
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
		        , %(startDate)s
		        , %(endDate)s
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
                    LogWriter.add_dblog('error','executeMakeScheduleInsp', ex)
                    raise ex

            return {'success': True, 'message': '설비점검스케줄이 생성되었습니다.'}

        elif action == 'getEquipChkItemInfo':
            chkSchePk = CommonUtil.try_int( gparam.get('chkSchePk') )

            sql = ''' select count(distinct t3.equip_pk) as equipCount
			, count(distinct t2.chk_item_pk) as itemCount
		    from cm_equip_chk_sche t1
		    left join cm_equip_chk_item_mst t2 on t2.chk_sche_pk = t1.chk_sche_pk
		    left join cm_equip_chk_rslt t3 on t3.chk_sche_pk = t1.chk_sche_pk 
		    where t1.chk_sche_pk = %(chkSchePk)
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            items = DbUtil.get_row(sql, dc)

        elif action == 'selectMaxChkScheNo':

            sql = ''' select coalesce(MAX((select chk_sche_no
				from (
				    select max(cast(t.chk_sche_no as integer)) as chk_sche_no
				    from cm_equip_chk_sche t
				    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = t.chk_mast_pk
				    WHERE (cast(t.chk_sche_no as text)  ~ E'^[0-9]+$') = true
				    and ecm.factory_pk = %(factory_pk)s
				    ) as sub_table
			)) + 1, '1')
			from cm_equip_chk_sche
            '''

            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'findReferencedTablesInfo':
            chkSchePk = CommonUtil.try_int( gparam.get('chkSchePk') )

            sql = ''' select t.i18n_code, t1.def_msg, t.cnt
			FROM (
			    select 'equipchkrslt.chkplanpk.lbl' as i18n_code, count(*) as cnt
			    from cm_equip_chk_rslt t1 
			    inner join cm_work_order t2 on t2.chk_rslt_pk = t1.chk_rslt_pk
			    where t1.chk_sche_pk = %(chkSchePk)s
			) t
			left outer join cm_i18n t1 on t.i18n_code = t1.lang_code
			where t.cnt > 0
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            items = DbUtil.get_row(sql, dc)

        #점검일정목록
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

            sql = ''' 
            SELECT ecs.chk_sche_pk, ecs.chk_sche_no, ecm.chk_mast_pk
			    , ecm.chk_mast_no, ecm.chk_mast_nm, d."Name" as dept_nm, cm_fn_user_nm(cu."Name", 'N') as chk_user_nm
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
			        --AND wo.factory_pk = 1
			WHERE 1= 1
                --ecm.factory_pk = e.factory_pk
			    --AND e.factory_pk = 1
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
            #if chkMastNo:
            #    sql += ''' AND ecm.chk_mast_no = %(chkMastNo)s
            #   '''
            
     #        if chkScheNo:
     #            sql += ''' AND ecs.chk_sche_no = %(chkScheNo)s
     #           '''
     #        else:
     #            sql += ''' AND case when %(chkStatus)s = 'CHK_STATUS_NP' then bc.grp_cd else bc.code_cd end 
     #                    = case when %(chkStatus)s = 'CHK_STATUS_NP' then 'NP' 
     #                            when coalesce('chkStatus', '') = '' then bc.code_cd 
     #                            else %(chkStatus)s end
					# AND date(case when %(chkStatus)s = 'CHK_STATUS_Y' then ecs.chk_dt 
     #                        else ecs.chk_sche_dt end) >= to_date(%(startDate)s, 'YYYY-MM-DD')
					#  	and date(case when %(chkStatus)s = 'CHK_STATUS_Y' then ecs.chk_dt 
     #                        else ecs.chk_sche_dt end) <= to_date(%(endDate)s, 'YYYY-MM-DD')
     #           '''
            if chkScheNo:
                sql += ''' AND ecs.chk_sche_no = %(chkScheNo)s
                '''
            else:
               sql += '''                 
				    AND date(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_Y' then ecs.chk_dt else ecs.chk_sche_dt end) >= to_date(%(startDate)s, 'YYYY-MM-DD')
                   and date(case when coalesce(%(chkStatus)s, '') = 'CHK_STATUS_Y' then ecs.chk_dt else ecs.chk_sche_dt end) <= to_date(%(endDate)s, 'YYYY-MM-DD')
                '''            

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
            dc['factory_pk'] = factory_id

            try:
                items = DbUtil.get_rows(sql, dc)
            except Exception as ex:
                LogWriter.add_dblog('error','searchEquipSchedule', ex)
                raise ex
            return {'success': True, 'data': items}
        elif action == 'selectEquipResult':
            ''' 원 자바 소스에 버그가 있었음.
            '''
            deptPk = CommonUtil.try_int(gparam.get('deptPk'))
            chkStatus = gparam.get('chkStatus')
            searchText = gparam.get('searchText')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')

            sql = ''' select ecs.chk_sche_pk, ecs.chk_sche_no, ecm.chk_mast_nm
			, d."Name" as dept_nm, ecm.last_chk_date, ecr.rslt_dsc
			, sum(case when ecr.chk_rslt = 'N' then 1 else 0 end) as fail_count
			, ecs.chk_dt, ecs.chk_sche_dt
			, wo.work_order_pk, wo.work_order_no
			FROM cm_equip_chk_rslt ecr
			INNER JOIN cm_equip_chk_sche ecs on ecs.chk_sche_pk = ecr.chk_sche_pk
			inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
			left join dept d on d.id = ecs.dept_pk
			inner join cm_equipment e on e.equip_pk = ecr.equip_pk
			inner join cm_base_code cs on cs.code_cd = ecs.chk_status 
			and cs.code_grp_cd = 'CHK_STATUS'
			left join cm_work_order wo on wo.chk_rslt_pk = ecr.chk_rslt_pk
			WHERE 1=1
			-- and (date(t1.chkScheDt) >= to_date(%(startDate)s, 'YYYY-MM-DD')
			-- AND date(t1.chkScheDt) <= to_date(%(endDate)s, 'YYYY-MM-DD'))
			AND ecm.factory_pk = e.factory_pk
			AND e.factory_pk = %(factory_pk)s
            '''
            if searchText:
                sql += ''' AND ( UPPER(ecm.chk_mast_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR
					UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR
					UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
	   			)
                '''
            if deptPk > 0:
                sql += ''' and d.id = %(deptPk)s
                '''
            if chkStatusCd:
                sql += ''' and cs.code_cd = %(chkStatusCd)s
                '''
            sql += ''' group by ecs.chk_sche_pk, ecs.chk_sche_no, ecm.chk_mast_nm, d."Name" 
			, ecm.last_chk_date, ecr.rslt_dsc, ecs.chk_dt, ecs.chk_sche_dt
			, wo.work_order_pk, wo.work_order_no
			-- Having MAX(case when t.chkRslt = 'N' then 1 else 0 end) = coalesce('chkRslt', MAX(case when ecr.chk_rslt = 'N' then 1 else 0 end))
            '''
            

            dc = {}
            dc['searchText'] = searchText
            dc['deptPk'] = deptPk
            dc['chkStatus'] = chkStatus
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)


        elif action == 'getDailyReportResult':
            ''' 
            '''
            chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))

            sql = ''' select 1 as dummy
		--	, A.daily_report_item_cd as code_cd
			,case when cnt_c > 0 then '/' when cnt_a > 0 then 'X' else 'O' end as result_value
		    from (
			    select count(case when ir.chk_item_rslt = 'A' then 1 end) cnt_a
				,count(case when ir.chk_item_rslt = 'C' then 1 end) cnt_c
				--,eci.daily_report_item_cd
			    from cm_equip_chk_sche ecs
			    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
			    left join cm_equip_chk_item_rslt ir on ir.chk_sche_pk = ecs.chk_sche_pk
			    left join cm_equip_chk_item eci on eci.chk_item_pk = ir.chk_item_pk
			    where ecs.chk_sche_pk = %(chkSchePk)s
				-- and eci.daily_report_item_cd is not null
			    -- group by eci.daily_report_item_cd
		    ) A
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getDailyVibListByeChkSchePk':
            ''' cm_equip_chk_item.daily_report_item_cd 컬럼 추가해야 함.
            '''

            chkSchePk = CommonUtil.try_int(gparam.get('chkSchePk'))

            sql = ''' select
			ecr.equip_pk
			,ecs.chk_dt as create_date
			,ecs.chk_user_pk as manager_id
			,ecs.factory_pk
			,max(case when eci.daily_report_item_cd = 'DRV01' then ir.chk_item_rslt_num end) as pump_de_v
			,max(case when eci.daily_report_item_cd = 'DRV02' then ir.chk_item_rslt_num end) as pump_nde_v
			,max(case when eci.daily_report_item_cd = 'DRV03' then ir.chk_item_rslt_num end) as pump_de_h
			,max(case when eci.daily_report_item_cd = 'DRV04' then ir.chk_item_rslt_num end) as pump_nde_h
			,max(case when eci.daily_report_item_cd = 'DRV05' then ir.chk_item_rslt_num end) as pump_a
			,max(case when eci.daily_report_item_cd = 'DRV08' then ir.chk_item_rslt_num end) as motor_de_v
			,max(case when eci.daily_report_item_cd = 'DRV09' then ir.chk_item_rslt_num end) as motor_nde_v
			,max(case when eci.daily_report_item_cd = 'DRV10' then ir.chk_item_rslt_num end) as motor_de_h
			,max(case when eci.daily_report_item_cd = 'DRV11' then ir.chk_item_rslt_num end) as motor_nde_h
			,max(case when eci.daily_report_item_cd = 'DRV12' then ir.chk_item_rslt_num end) as motor_a
			,max(case when eci.daily_report_item_cd = 'DRV15' then ir.chk_item_rslt_num end) as insp_opt_out_per
			,max(case when eci.daily_report_item_cd = 'DRV16' then ir.chk_item_rslt_num end) as insp_opt_pres
			,max(case when eci.daily_report_item_cd = 'DRV17' then ir.chk_item_rslt_num end) as insp_opt_temp
			,max(case when eci.daily_report_item_cd = 'DRV18' then ir.chk_item_rslt_num end) as insp_opt_out_hz
		    from cm_equip_chk_sche ecs
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = ecs.chk_mast_pk
		    left join cm_equip_chk_item_rslt ir on ir.chk_sche_pk = ecs.chk_sche_pk
		    left join cm_equip_chk_rslt ecr on ecr.chk_sche_pk = ecs.chk_sche_pk 
		    and ir.chk_rslt_pk = ecr.chk_rslt_pk
		    left join cm_equip_chk_item eci on eci.chk_item_pk = ir.chk_item_pk
		    where	ecs.chk_sche_pk = %(chkSchePk)s
			and eci.daily_report_item_cd is not null
		    group by ecr.equip_pk, ecs.chk_dt, ecs.chk_user_pk, ecs.factory_pk
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            items = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = 'kmms/equip_chk_sche : action-{}'.format(action)
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