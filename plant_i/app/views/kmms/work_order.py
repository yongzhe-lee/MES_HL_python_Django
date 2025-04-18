from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWorkOrder, CmEquipment, CmWoLabor, CmWoMtrl, CmWorkOrderSupplier, CmWoFaultLoc, CmWorkOrderHist

def work_order(context):
    '''
    api/kmms/work_order   작업지시 
    김태영 작업중

    findAll
    searchAll
    findOne
    countBy
    findAllD
    findAllWithWorkDay
    getBrokenEquipWorkOrders
    selectDateFromTo
    selectMaxWorkOrderNo
    insert  작업요청
    update  작업요청수정
    acceptWorkOrder 작업요청승인
    approvalWorkOrder 작업승인
    inputResult 결과입력
    finishWorkOrder 작업완료
    completeWorkOrder 완료
    rejectWorkOrder 승인반려
    rejectRequestWorkOrder 요청반려
    updateStatus
    delete
    getPinvLocMaterialByWorkOrder
    startDateEndDateDiff
    updateWorkOrderStartEndDate
    updateWorkOrderPlanStartEndDate
    checkBrokenWorkOrder
    selectWorkOrderApprInfo
    updateWorkOrderStatusBySysOpt
    insertWorkOrderInspection 점검이상발행
    insertDailyReport 작업일보등록
    updateDailyReport   작업일보수정
    getFullApprLine     이력포함 전체 appr_line (OC,AP,CM,CL)
    selectWorkOrderLogList
    insertEquipBom 완료시 설비의 BOM으로 자재 추가
    getWorkOrderInfo workOrderPk로 간단한 정보 조회
    changeEquip 설비변경
    updateBreakDownMin  고장시간(분) 업데이트
    getWorkOrderInfoByNo
    updateFirstAssetStatus
    deleteWoLabor
    deleteWoMtrl
    deleteWoSupplier
    deleteWoFaultLoc
    deleteWohist
    deleteWo
    updateCostInfo
    
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['findAll','searchAll', 'findOne', 'findAllPm', 'findAllD', 'findAllWithWorkDay']:
            ''' findAllWithWorkDay 는 where 조건이 별도로 있음.
            '''
            if action == 'findOne':
                workOrderPk = gparam.get('workOrderPk')
                workOrderPk = CommonUtil.try_int(workOrderPk)
            else:
                workOrderPk = 0
            workOrderPkNot = gparam.get('workOrderPkNot')
            workOrderPkNot = CommonUtil.try_int(workOrderPkNot)
            processCd = gparam.get('processCd')
            systemCd = gparam.get('systemCd')
            projCd = gparam.get('projCd')
            equipPk = gparam.get('equipPk')
            equipPk = CommonUtil.try_int(equipPk)
            projCd = gparam.get('projCd')
            equipCategoryId = gparam.get('equipCategoryId')
            projCd = gparam.get('projCd')
            equipPk = gparam.get('equipPk')
            equipCategoryId = gparam.get('equipCategoryId')
            equipCategoryId = CommonUtil.try_int(equipCategoryId)
            processCd = gparam.get('processCd')
            systemCd = gparam.get('systemCd')
            equipClassId = gparam.get('equipClassId')
            problemCd = gparam.get('problemCd')
            causeCd = gparam.get('causeCd')
            remedyCd = gparam.get('remedyCd')
            workChargerPk = gparam.get('workChargerPk')
            workChargerPk = CommonUtil.try_int(workChargerPk)
            rqstUserNm = gparam.get('rqstUserNm')
            rqstYn = gparam.get('rqstYn')
            woTypeEx = gparam.get('woTypeEx')
            woStatusEx = gparam.get('woStatusEx')
            woStatusIn = gparam.get('woStatusIn')
            woStatusCd = gparam.get('woStatusCd')
            woStatusCdNot = gparam.get('woStatusCdNot')
            pmYn = gparam.get('pmYn')
            chkYn = gparam.get('chkYn')
            deptPk = gparam.get('deptPk')
            deptPk = CommonUtil.try_int(deptPk)
            reqDeptPk = gparam.get('reqDeptPk')
            reqDeptPk = CommonUtil.try_int(reqDeptPk)
            equipDeptPk = gparam.get('equipDeptPk')
            equipDeptPk = CommonUtil.try_int(equipDeptPk)
            locPk = gparam.get('locPk')
            locPk = CommonUtil.try_int(locPk)
            pmTypeCd = gparam.get('pmTypeCd')
            pmNo = gparam.get('pmNo')
            workOrderNo = gparam.get('workOrderNo')
            environEquipYn = gparam.get('environEquipYn')
            notFinishYn = gparam.get('notFinishYn')
            maintTypeCd = gparam.get('maintTypeCd')
            maintTypes = gparam.get('maintTypes')
            woTypeCd = gparam.get('woTypeCd')
            chkMastNo = gparam.get('chkMastNo')
            chkScheNo = gparam.get('chkScheNo')
            chkScheNo = CommonUtil.try_int(chkScheNo)
            rqstUserPk = gparam.get('rqstUserPk')
            rqstUserPk = CommonUtil.try_int(rqstUserPk)
            searchYear = gparam.get('searchYear')
            nextApprLine = gparam.get('nextApprLine')
            includeFinWo = gparam.get('includeFinWo')
            planStartDtFrom = gparam.get('planStartDtFrom')
            planStartDtEnd = gparam.get('planStartDtEnd')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')
            endDtYn = gparam.get('endDtYn')
            startDtYn = gparam.get('startDtYn')
            isDateCond = gparam.get('isDateCond')
            dateConds = gparam.get('dateConds')
            startWantDate = gparam.get('startWantDate')
            endWantDate = gparam.get('endWantDate')
            startFinishDate = gparam.get('startFinishDate')
            endFinishDate = gparam.get('endFinishDate')
            startCancelDate = gparam.get('startCancelDate')
            endCancelDate = gparam.get('endCancelDate')
            woTypeCal = gparam.get('woTypeCal')
            delayDays = gparam.get('delayDays')
            delayDays = CommonUtil.try_int(delayDays)
            exRqstDprYn = gparam.get('exRqstDprYn')
            rqstDprYn = gparam.get('rqstDprYn')
            exRqstInspYn = gparam.get('exRqstInspYn')
            rqstInspYn = gparam.get('rqstInspYn')
            woType = gparam.get('woType')
            workDayStatus = gparam.get('workDayStatus')
            locAreaPk = gparam.get('locAreaPk')
            locAreaPk = CommonUtil.try_int(locAreaPk)
            locLinePks = gparam.get('locLinePks')

            searchText = gparam.get('searchText')
            searchTextA = gparam.get('searchTextA')
            searchTextB = gparam.get('searchTextB')
            searchTextTypeA = gparam.get('searchTextTypeA')
            searchTextWorkDay = gparam.get('searchTextWorkDay')
            searchTextPm = gparam.get('searchTextPm')
            searchTextCal = gparam.get('searchTextCal')
            searchTextDelayHistory = gparam.get('searchTextDelayHistory')

            reqDeptBusiCdOrder = gparam.get('reqDeptBusiCdOrder')

            if action != 'findAllPm':
                sql = ''' select t.work_order_pk, t.work_order_no
				    , t.work_title, t.work_text, t.work_order_sort
				    , t.req_dept_pk, rd."Name"  as req_dept_nm
				    , rd.tpm_yn as req_dept_tpm_yn
				    , t.dept_pk, wd."Name"  as dept_nm
				    , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
				    , cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, '1') as business_nm
				    , t.work_charger_pk
				    , cm_fn_user_nm(wcu."Name", 'N') as work_charger_nm
				    , mt.code_cd as maint_type_cd
				    , mt.code_nm as maint_type_nm
				    , ws.code_cd as wo_status_cd
				    , ws.code_nm as wo_status_nm
				    , t.plan_start_dt, t.plan_end_dt
				    , t.start_dt, t.end_dt, t.want_dt
				    , t.equip_pk, e.equip_cd, e.equip_nm
				    , ed.id as equip_dept_pk, ed."Name" as equip_dept_nm
				    , to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
				    , t.pm_pk, p.pm_no, p.pm_nm
				    , pt.code_nm  AS pm_type_nm
				    , p.work_text as pm_work_text
				    , t.chk_rslt_pk, ecs.chk_sche_pk, ecs.chk_sche_no
				    , ecm.chk_mast_nm, ecm.chk_mast_pk, ecs.chk_sche_dt
				    , l.loc_nm
				    , t.req_info, t.wo_type
				    , t.rqst_insp_yn, t.rqst_dpr_yn
				    , wt.code_nm as wo_type_nm
				    , t.breakdown_dt, t.breakdown_min
				    , wsc.code_cd as work_src_cd, wsc.code_nm as work_src_nm
				    , t.tot_cost, t.mtrl_cost, t.labor_cost, t.outside_cost, t.etc_cost
				    , t.problem_cd, wp.reliab_nm as problem_nm
				    , t.cause_cd, wc.reliab_nm as cause_nm
				    , t.remedy_cd, wr.reliab_nm as remedy_nm
				    , prj.proj_cd, prj.proj_nm
				    , t.wo_file_grp_cd, t.req_info_img_grp_cd, t.work_text_img_grp_cd
				    , t.pm_req_type, t.req_dept_busi_cd
				    , t.appr_line, t.appr_line_next
				    , t.work_order_approval_pk
				    , woa.reg_dt, woa.rqst_dt
				    , woa.rqst_user_nm, woarqstd.id as rqst_dept_pk, woarqstd."Name" as rqst_dept_nm
				    , woa.cancel_dt, woa.cancel_user_nm, woa.accept_dt
				    , woa.appr_dt, woa.finish_dt
				    , substring(t.appr_line, 1,2) as wo_start_type
				    , cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
				    , t.insert_ts
				    , e.environ_equip_yn
				    , e.equip_status as equip_stauts_cd
				    , e.import_rank_pk, ir.import_rank_cd
				    , e.up_equip_pk, ue.equip_nm AS up_equip_name
				    , ec.equip_category_id, ec.equip_category_desc
        		    , ec.remark
				    , e.equip_class_path, e.equip_class_desc
				    , av.code_nm as first_asset_status, av.code_cd as first_asset_status_cd
				    , cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
				    , (select code_nm from cm_base_code 
					    where code_grp_cd = 'EQUIPMENT_PROCESS' 
					    and code_cd = e.process_cd) as process_nm
				    , (select code_nm from cm_base_code 
					    where code_grp_cd = 'EQUIP_SYSTEM' 
					    and code_cd = e.system_cd) as system_nm
				    , l.loc_nm
				    , es.ex_supplier_nm
				    , woa.cancel_reason
				    , t.cost_type
				    , (select code_nm from cm_base_code 
					    where code_cd = t.cost_type 
					    and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm
                        '''
            else:   # findAllPm
                sql + ''' select t.pm_pk
			    , to_char(t.plan_start_dt, 'YYYYMMDD') as pm_plan_dt
			    , to_char(t.plan_start_dt, 'YYYY-MM-DD') as pm_plan_dt_label
			    , p.pm_nm
			    , p.per_number
			    , p.cycle_type
			    , ct.code_nm as cycle_type_nm
			    , e.equip_cd
			    , e.equip_nm
			    , ed."Name" as dept_nm
			    , wd."Name" AS wo_dept_nm
			    , t.work_order_pk
			    , t.work_order_no
			    , p.pm_no
			    , t.start_dt
			    , t.end_dt
			    , t.plan_start_dt
			    , t.plan_end_dt
			    , t.work_title
			    , ws.code_nm as wo_status_nm
			    , ws.code_cd as wo_status
			    , pt.code_cd as pm_type
			    , pt.code_nm as pm_type_nm
			    , cm_fn_user_nm(pmu."Name" , 'N') as pm_user_nm
                , cm_fn_user_nm(wou."Name" , 'N') as wo_user_nm
                , t.work_charger_pk
                , t.dept_pk
                , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
                , woarqstd.id as rqst_dept_pk
			    , ec.equip_category_desc
			    , (select code_nm from cm_base_code 
					    where code_grp_cd = 'EQUIPMENT_PROCESS' 
					    and code_cd = e.process_cd) as process_nm
			    , (select code_nm from cm_base_code 
					    where code_grp_cd = 'EQUIP_SYSTEM' 
					    and code_cd = e.system_cd) as system_nm
                ''' 

            sql += ''' from cm_work_order t
			inner join cm_work_order_approval woa on woa.work_order_approval_pk = t.work_order_approval_pk
			inner join cm_base_code mt on mt.code_cd = t.maint_type_cd 
			and mt.code_grp_cd = 'MAINT_TYPE'
			inner join cm_base_code ws on ws.code_cd = t.wo_status
			and ws.code_grp_cd = 'WO_STATUS'
			inner join cm_equipment e on e.equip_pk = t.equip_pk
			inner join cm_location l on l.loc_pk = e.loc_pk
			left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
			left join dept ed on ed.id = e.dept_pk
			left join dept wd on wd.id = t.dept_pk
			left join dept rd on rd.id = t.req_dept_pk 
			left join user_profile wcu on wcu."User_id" = t.work_charger_pk 
			left join cm_reliab_codes wp on wp.reliab_cd = t.problem_cd  
			and wp."types" = 'PC' 
			and wp.factory_pk = t.factory_pk
			left join cm_reliab_codes wc on wc.reliab_cd = t.cause_cd 
			and wc."types" = 'CC' 
			and wc.factory_pk = t.factory_pk
			left join cm_reliab_codes wr on wr.reliab_cd = t.remedy_cd 
			and wr."types" = 'RC' 
			and wr.factory_pk = t.factory_pk
			left join cm_pm p on p.pm_pk = t.pm_pk
			left join cm_base_code ct on ct.code_cd = p.cycle_type 
			and ct.code_grp_cd = 'CYCLE_TYPE'
			left join cm_base_code pt on pt.code_cd = p.pm_type
			and pt.code_grp_cd = 'PM_TYPE'
			left join user_profile pmu on pmu."User_id" = p.pm_user_pk
			left join user_profile wou on wou."User_id" = t.WORK_CHARGER_PK 
			left join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
			left join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
			left join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
			left join cm_base_code wsc on t.work_src_cd = wsc.code_cd 
			and wsc.code_grp_cd = 'WORK_SRC'
			left join cm_project prj on t.proj_cd = prj.proj_cd
			left join user_profile woarqstu on woarqstu."User_id" = woa.rqst_user_pk
			left join dept woarqstd on woarqstd.id = woarqstu."Depart_id" 
			left join cm_base_code wt on wt.code_cd  = t.wo_type 
			and wt.code_grp_cd = 'WO_TYPE'
			left join cm_IMPORT_RANK ir on ir.IMPORT_RANK_PK = e.IMPORT_RANK_PK  
			left join cm_equipment ue on ue.EQUIP_PK = e.UP_EQUIP_PK
			left join cm_base_code av on av.code_cd = e.first_asset_status 
			and av.code_grp_cd = 'ASSET_VAL_STATUS'
			left join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
			left join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk	
			where 1 = 1
			AND t.factory_pk = %(factory_pk)s
            '''
            if action == 'findOne':
                sql += ''' and t.work_order_pk = %(workOrderPk)s
                '''
                dc = {}
                dc['workOrderPk'] = workOrderPk
                items = DbUtil.get_row(sql, dc)
                return items

            if workOrderPkNot:
                sql += ''' and t.work_order_pk <> %(workOrderPkNot)s
                '''
            if processCd:
                sql += ''' AND e.process_cd = %(processCd)s
                '''            
            if systemCd:
                sql += ''' AND e.system_cd = %(systemCd)s
                '''
            if projCd:
                sql += ''' AND t.proj_cd = %(projCd)s
                '''
            if equipPk:
                sql += ''' AND t.equip_pk = %(equipPk)s
                '''
            if equipCategoryId:
                sql += ''' AND ec.equip_category_id = %(equipCategoryId)s
                '''
            if equipClassId:
                sql += ''' AND e.equip_class_path = %(equipClassId)s
                '''
            if problemCd:
                sql += ''' AND t.problem_cd = %(problemCd)s
                '''
            if causeCd:
                sql += ''' AND t.cause_cd = %(causeCd)s
                '''
            if remedyCd:
                sql += ''' AND t.remedy_cd = %(remedyCd)s
                '''
            if workChargerPk:
                sql += ''' AND t.work_charger_pk = %(workChargerPk)s
                '''
            if rqstUserNm:
                sql += ''' AND woa.rqst_user_nm = %(rqstUserNm)s
                '''
            if rqstYn:
                sql += ''' AND substring(t.appr_line, 1, 2) = %(rqstYn)s
                '''
            if woTypeEx:
                woTypeEx2 = CommonUtil.convert_quotation_mark_string(woTypeEx)
                sql += ''' AND t.wo_type NOT IN ( ''' + woTypeEx2 + ''' )
                '''
            if woStatusEx:
                woStatusEx2 = CommonUtil.convert_quotation_mark_string(woStatusEx)
                sql += ''' AND t.wo_status NOT IN ( ''' + woStatusEx + ''')
                '''
            if woStatusIn:
                woStatusIn2 = CommonUtil.convert_quotation_mark_string(woStatusIn)
                sql += ''' AND t.wo_status IN ( ''' + woStatusIn2 + ''' )
                '''
            if woStatusCd:
                sql += ''' AND ws.code_cd = %(woStatusCd)s
                '''
            if woStatusCdNot:
                sql += ''' AND ws.code_cd <> %(woStatusCdNot)s
                '''
            if pmYn:
                sql += ''' AND t.pm_pk IS NOT NULL
                '''
            if chkYn:
                sql += ''' AND t.chk_rslt_pk IS NOT NULL
                '''
            if deptPk:
                sql += ''' AND (
				wd.dept_pk = %(deptPk)s
				OR
				wd.dept_pk IN ( select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
			    )
                '''
            if reqDeptPk:
                sql += ''' AND (
				rd.dept_pk = %(reqDeptPk)s
				OR
				rd.dept_pk IN ( select dept_pk from v_dept_path 
                    where %(reqDeptPk)s = path_info_pk)
			    )
                '''
            if equipDeptPk:
                sql += ''' AND (
				ed.dept_pk = %(equipDeptPk)s
				OR
				ed.dept_pk IN ( select dept_pk from cm_v_dept_path 
                    where %(equipDeptPk)s = path_info_pk)
			    )
                '''
            if locPk:
                sql += ''' AND ( l.loc_pk = %(locPk)s
				OR l.loc_pk IN ( select loc_pk 
                                from (select * 
                                        from cm_fn_get_loc_path(%(factory_pk)s)) x 
                    where %(locPk)s = path_info_pk)
			    )
                '''
            if pmTypeCd:
                sql += ''' AND pt.code_cd = %(pmTypeCd)s
                '''
            if searchText:
                sql += ''' AND (
				UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(CAST(%(searchText)s as text)),'%')
				OR UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(CAST(%(searchText)s as text)),'%')
                '''
                if pmYn == 'Y':
                    sql += ''' OR UPPER(p.pm_nm) LIKE CONCAT('%',UPPER(CAST(%(searchText)s as text)),'%')
                    '''
                if chkYn == 'Y':
                    sql += ''' OR UPPER(ecm.chk_mast_nm) LIKE CONCAT('%',UPPER(CAST(%(searchText)s as text)),'%')
                    '''
                sql += ''' )
                '''
            if searchTextA:
                sql += ''' AND (
				    UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(searchTextA)s as text)),'%%')
				    OR UPPER(woa.rqst_user_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchTextA)s as text)),'%%')
				    OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchTextA)s as text)),'%%')
			    )
                '''
            if searchTextB:
                sql += ''' AND (
				    UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(searchTextB)s as text)),'%%')
				    OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(searchTextB)s as text)),'%%')
				    OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchTextB)s as text)),'%%')
				    OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchTextB)s as text)),'%%')
                '''
                if searchTextTypeA == 'Y':
                    sql += ''' OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(searchTextB)s as text)),'%%')
                    '''
                sql += ''' )
                '''
            if searchTextWorkDay:
                sql += ''' AND (
				    UPPER(t.work_title) LIKE CONCAT('%%',UPPER(CAST(%(searchTextWorkDay)s as text)),'%%')
				    OR UPPER(t.work_text) LIKE CONCAT('%%',UPPER(CAST(%(searchTextWorkDay)s as text)),'%%')
				    OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchTextWorkDay)s as text)),'%%')
				    OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchTextWorkDay)s as text)),'%%')
                    OR UPPER(wcu."Name") LIKE CONCAT('%',UPPER(CAST(%(searchTextWorkDay)s as text)),'%')
                '''
                if searchTextTypeA == 'Y':
                    sql += ''' OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(searchTextWorkDay)s as text)),'%%')
                    '''
                sql += ''' )
                '''
            if searchTextPm:
                sql += ''' AND (
				    UPPER(p.pm_no) LIKE CONCAT('%',UPPER(CAST(%(searchTextPm)s as text)),'%')
				    OR UPPER(p.pm_nm) LIKE CONCAT('%',UPPER(CAST(%(searchTextPm)s as text)),'%')
				    OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchTextPm)s as text)),'%%')
				    OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchTextPm)s as text)),'%%')
                    OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(searchTextPm)s as text)),'%%')
                    )
                '''
            if searchTextCal:
                sql += ''' AND (
				    UPPER(p.pm_nm) LIKE CONCAT('%',UPPER(CAST(%(searchTextCal)s as text)),'%')
				    OR UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchTextCal)s as text)),'%%')
				    OR UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchTextCal)s as text)),'%%')
                    OR UPPER(ecm.chk_mast_nm) LIKE CONCAT('%',UPPER(CAST(%(searchTextCal)s as text)),'%')
                '''
                if searchTextTypeA == 'Y':
                    sql += ''' OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(searchTextCal)s as text)),'%%')
                    '''
                sql += ''' )
                '''
            if searchTextDelayHistory:
                sql += ''' AND (
				    UPPER(p.pm_no) LIKE CONCAT('%',UPPER(CAST(%(searchTextDelayHistory)s as text)),'%')
                    OR UPPER(t.work_order_no) LIKE CONCAT('%%',UPPER(CAST(%(searchTextDelayHistory)s as text)),'%%')
				    OR UPPER(t.work_title) LIKE CONCAT('%',UPPER(CAST(%(searchTextDelayHistory)s as text)),'%')
                    )
                '''
            if pmNo:
                sql += ''' AND p.pm_no = %(pmNo)s
                '''
            if workOrderNo:
                sql += ''' AND t.work_order_no = %(workOrderNo)s
                '''
            if environEquipYn == 'Y':
                sql += ''' AND t.environ_equip_yn = 'Y'
                '''
            if notFinishYn == 'Y':
                sql += ''' AND t.wo_status NOT IN ('WOS_RW', 'WOS_DL', 'WOS_CM', 'WOS_CL')
                '''
            if maintTypeCd:
                sql += ''' AND mt.code_cd = %(maintTypeCd)s
                '''
            if maintTypes:
                maintTypes2 = CommonUtil.convert_quotation_mark_string(maintTypes)
                sql += ''' AND mt.code_cd in ( ''' + maintTypes2 + ''')
                '''
            if woTypeCd:
                sql += ''' AND t.wo_type = %(woTypeCd)s
                '''
            if chkMastNo:
                sql += ''' AND ecm.chk_mast_no = %(chkMastNo)s
                '''
            if chkScheNo:
                sql += ''' AND ecs.chk_sche_no = %(chkScheNo)s
                '''
            if rqstUserPk:
                sql += ''' AND woa.rqst_user_pk = %(rqstUserPk)s
                '''
            if searchYear:
                sql += ''' AND to_char(t.end_dt, 'YYYY') = %(searchYear)s
                '''
            if nextApprLine:
                sql += ''' AND t.appr_line_next = %(nextApprLine)s
                '''
            if includeFinWo:
                sql += ''' AND t.wo_status not in ( %(includeFinWo)s )
                '''
            if planStartDtFrom and planStartDtEnd:
                sql += ''' AND ( t.plan_start_dt >= to_date(%(planStartDtFrom)s,'YYYY-MM-DD') 
                        AND t.plan_start_dt <= to_date(%(planStartDtEnd)s, 'YYYY-MM-DD')
                )
                '''
            if startDate and endDate and not endDtYn == 'Y' and not startDtYn =='Y' and not isDateCond == 'N' and not dateConds :
                sql += ''' AND t.start_dt <= to_date(%(endDate)s, 'YYYY-MM-DD')
                and t.end_dt >= to_date(%(startDate)s, 'YYYY-MM-DD')
                '''
            if endDtYn == 'Y':
                sql += ''' AND t.end_dt >= to_date(%(startDate)s, 'YYYY-MM-DD')
                and t.end_dt <= to_date(%(endDate)s, 'YYYY-MM-DD')
                '''
            if startDtYn == 'Y':
                sql += ''' AND AND t.start_dt >= to_date(%(startDate)s, 'YYYY-MM-DD')
                and t.start_dt <= to_date(%(endDate)s, 'YYYY-MM-DD')
                '''
            if dateConds:
                sql += ''' AND (
			 	(date(case when %(dateConds)s = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when %(dateConds)s = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date(%(startDate)s, 'YYYY-MM-DD')
			 		AND date(case when %(dateConds)s = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
								when %(dateConds)s = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date(%(endDate)s, 'YYYY-MM-DD'))
			 	OR
			 	(date(case 		when %(dateConds)s = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
								when %(dateConds)s = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date(%(startDate)s, 'YYYY-MM-DD')
			 		AND date(case when %(dateConds)s = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
									when %(dateConds)s = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date(%(endDate)s, 'YYYY-MM-DD'))
			)
                '''
            if startWantDate and endWantDate:
                sql += ''' AND date(t.want_dt) BETWEEN  to_date(%(startWantDate), 'YYYY-MM-DD') AND to_date(%(endWantDate)s, 'YYYY-MM-DD')
                '''
            if startFinishDate and endFinishDate:
                sql += ''' AND date(woa.finish_dt) BETWEEN  to_date(%(startFinishDate)s, 'YYYY-MM-DD') AND to_date(%(endFinishDate)s, 'YYYY-MM-DD')
                '''
            if startCancelDate and endCancelDate:
                sql += ''' AND date(woa.cancel_dt) BETWEEN  to_date(%(startCancelDate)s, 'YYYY-MM-DD') AND to_date(%(endCancelDate)s, 'YYYY-MM-DD')
                '''
            if woTypeCal:
                sql += ''' AND t.wo_type = %(woTypeCal)s
                '''
            if delayDays > 0:
                sql += ''' AND cm_fn_datediff(cast(now() as timestamp), t.plan_end_dt) >= %(delayDays)s
                '''
            if exRqstDprYn == 'Y':
                sql += ''' AND coalesce(t.rqst_dpr_yn, 'N') = 'N'
                '''
            if rqstDprYn == 'Y':
                sql += ''' AND coalesce(t.rqst_dpr_yn, 'N') = 'Y'
                '''
            if exRqstInspYn == 'Y':
                sql += ''' AND coalesce(t.rqst_insp_yn, 'N') = 'N'
                '''
            if rqstInspYn == 'Y':
                sql += ''' AND coalesce(t.rqst_insp_yn, 'N') = 'Y'
                '''
            if woType:
                sql += ''' AND t.wo_type  = %(woType)s
                '''
            if workDayStatus == '10':
                sql += ''' AND (t.wo_status = 'WOS_RW' AND t.end_dt IS NULL)
                '''
            if workDayStatus == '20':
                sql += ''' AND (t.wo_status = 'WOS_RW' AND t.end_dt IS NOT NULL)
                '''
            if workDayStatus == '30':
                sql += ''' AND t.wo_status = 'WOS_CL'
                '''
            if locAreaPk > 0 or not locLinePks:
                sql += ''' AND e.loc_pk IN (
                   SELECT id
                   FROM (
                       SELECT loc_pk as id, path_info_pk
                       FROM cm_fn_get_loc_path(%(factory_pk)s)
                   ) x WHERE 1 = 1
                '''
                if locAreaPk > 0:
                    sql += ''' AND path_info_pk = %(locAreaPk)s
                    '''
                if locLinePks:
                    locLinePks2 = CommonUtil.convert_quotation_mark_string(locLinePks)
                    sql += ''' AND path_info_pk in (''' + locLinePks2 + ''')
                    '''

            if action == 'searchAll':
                if reqDeptBusiCdOrder == 'Y':
                    sql += ''' ORDER BY cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, %(factory_pk)s), rd.dept_nm
                    '''

            dc = {}
            dc['workOrderPk'] = workOrderPk
            dc['workOrderPkNot'] = workOrderPkNot
            dc['processCd'] = processCd
            dc['systemCd'] = systemCd
            dc['projCd'] = projCd
            dc['equipPk'] = equipPk
            dc['equipCategoryId'] = equipCategoryId
            dc['problemCd'] = problemCd
            dc['causeCd'] = causeCd
            dc['remedyCd'] = remedyCd
            dc['workChargerPk'] = workChargerPk
            dc['rqstUserNm'] = rqstUserNm
            dc['rqstYn'] = rqstYn
            dc['woStatusCd'] = woStatusCd
            dc['woStatusCdNot'] = woStatusCdNot
            dc['deptPk'] = deptPk
            dc['reqDeptPk'] = reqDeptPk
            dc['equipDeptPk'] = equipDeptPk
            dc['locPk'] = locPk
            dc['pmTypeCd'] = pmTypeCd
            dc['searchText'] = searchText
            dc['searchTextA'] = searchTextA
            dc['searchTextB'] = searchTextB
            dc['searchTextWorkDay'] = searchTextWorkDay
            dc['searchTextPm'] = searchTextPm
            dc['searchTextCal'] = searchTextCal
            dc['searchTextDelayHistory'] = searchTextDelayHistory
            dc['pmNo'] = pmNo
            dc['workOrderNo'] = workOrderNo
            dc['maintTypeCd'] = maintTypeCd
            dc['chkMastNo'] = chkMastNo
            dc['chkScheNo'] = chkScheNo
            dc['rqstUserPk'] = rqstUserPk
            dc['searchYear'] = searchYear
            dc['nextApprLine'] = nextApprLine
            dc['includeFinWo'] = includeFinWo
            dc['planStartDtFrom'] = planStartDtFrom
            dc['planStartDtEnd'] = planStartDtEnd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['dateConds'] = dateConds
            dc['startWantDate'] = startWantDate
            dc['endWantDate'] = endWantDate
            dc['startFinishDate'] = startFinishDate
            dc['endFinishDate'] = endFinishDate
            dc['startCancelDate'] = startCancelDate
            dc['endCancelDate'] = endCancelDate
            dc['woTypeCal'] = woTypeCal
            dc['delayDays'] = delayDays
            dc['woType'] = woType
            dc['locAreaPk'] = locAreaPk
            dc['factory_pk'] = factory_id

            if action == 'findOne':
                items = DbUtil.get_row(sql, dc)
            else:
                items = DbUtil.get_rows(sql, dc)
                if action == 'countBy':
                    items = len(items)

 

        elif action == 'findOne':
            ''' 위에서 구현
            '''

            items = DbUtil.get_row(sql, dc)

        elif action == 'getBrokenEquipWorkOrders':
            equipPk = CommonUtil.try_int(gparam.get('equipPk'))

            sql = ''' select t.work_order_pk
		    , t.work_order_no
		    from cm_work_order t
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    inner join cm_base_code mt on t.maint_type_cd = mt.code_cd 
		    and mt.code_grp_cd = 'MAINT_TYPE'
		    inner join cm_base_code ws on t.wo_status = ws.code_cd 
		    and ws.code_grp_cd = 'WO_STATUS'
		    where t.maint_type_cd = 'MAINT_TYPE_BM'
		    and t.wo_status NOT IN ('WOS_CL','WOS_DL')
		    and t.equip_pk = %(equipPk)s
            and t.factory_pk = %(factory_pk)s
		    order by t.work_order_pk desc
            '''
            dc={}
            dc['equipPk'] = equipPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'selectDateFromTo':
            baseDate = CommonUtil.try_int(gparam.get('baseDate'))
            addDays = CommonUtil.try_int(gparam.get('addDays'))

            sql = ''' with t as (
			    select to_date(concat(%baseDate)s,'01'), 'YYYYMMDD') as curr_date
		    )
		    select to_char(t.curr_date - (%(addDays)s || ' day')::INTERVAL, 'YYYYMMDD') as start_date
		    , to_char(fn_last_day(t.curr_date) + (%(addDays)s || ' day')::INTERVAL, 'YYYYMMDD') as end_date
		    from t
            '''
            dc={}
            dc['baseDate'] = baseDate
            dc['addDays'] = addDays

            items = DbUtil.get_row(sql, dc)

        elif action == 'selectMaxWorkOrderNo':

            sql = ''' SELECT coalesce(max(cast(work_order_no AS integer))+1,1) AS work_order_no
            FROM  cm_work_order
            WHERE factory_pk = %(factory_pk)s
            AND  ( work_order_no ~ e'^[0-9]+$') = true
            '''
            dc={}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action in ['insert', 'update']:
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            workOrderNo = posparam.get('workOrderNo')
            workOrderSort = posparam.get('workOrderSort')
            workTitle = posparam.get('workTitle')
            workText = posparam.get('workText')
            workOrderApprovalPk = posparam.get('workOrderApprovalPk')
            workOrderApprovalPk = CommonUtil.try_int(workOrderApprovalPk)
            reqInfo = posparam.get('reqInfo')
            woStatusCd = posparam.get('woStatusCd')
            maintTypeCd = posparam.get('maintTypeCd')
            woType = posparam.get('woType')
            wantDt = posparam.get('wantDt')
            planStartDt = posparam.get('planStartDt')
            planEndDt = posparam.get('planEndDt')
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')
            deptPk = posparam.get('deptPk')
            workChargerPk = posparam.get('workChargerPk')
            pmPk = posparam.get('pmPk')
            apprLine = posparam.get('apprLine')
            apprLineNext = posparam.get('apprLineNext')
            reqDeptPk = posparam.get('reqDeptPk')
            pmReqType = posparam.get('pmReqType')
            work_src_cd = posparam.get('work_src_cd')
            breakdown_dt = posparam.get('breakdown_dt')
            cause_cd = posparam.get('cause_cd')
            problem_cd = posparam.get('problem_cd')
            remedyCd = posparam.get('remedyCd')
            proj_cd = posparam.get('proj_cd')
            work_src_cd = posparam.get('work_src_cd')
            totCost = posparam.get('totCost')
            mtrlCost = posparam.get('mtrlCost')
            laborCost = posparam.get('laborCost')
            outsideCost = posparam.get('outsideCost')
            etcCost = posparam.get('etcCost')
            if_send_yn = posparam.get('if_send_yn')
  
            if action == 'update':
                wo = CmWorkOrder.objects.get(id=workOrderPk)
                wo.WorkText = workText
            else:
                wo = CmWorkOrder()
                wo.CmWorkOrderApproval_id = workOrderApprovalPk
                wo.CmPm_id = pmPk
                if pmReqType:
                    wo.PmReqType = pmReqType
                wo.RemedyCode = remedyCd
                wo.TotCost = totCost
                wo.MtrlCost = mtrlCost
                wo.LaborCost = laborCost
                wo.OutsideCost = outsideCost
                wo.EtcCost = etcCost
                wo.IfSendYn = if_send_yn

            wo.CmEquipment_id = equipPk
            if workOrderNo:
                wo.WorkOrderNo = workOrderNo
                wo.WorkOrderSort = workOrderSort

            wo.WorkTitle = workTitle
            
            wo.ReqInfo = reqInfo
            wo.WoStatus = woStatusCd
            wo.MaintTypeCode = maintTypeCd
            wo.WoType = woType
            wo.WantDt = wantDt
            if planStartDt:
                wo.PlanStartDt = planStartDt
            if planEndDt:
                wo.PlanEndDt = planEndDt
            if startDt:
                wo.StartDt = startDt
            else:
                wo.StartDt = None
            if endDt:
                wo.EndDt = endDt
            else:
                wo.EndDt = None
            wo.DeptPk = deptPk
            wo.WorkChargerPk = workChargerPk
            
            wo.ApprLine = apprLine
            wo.ApprLineNext = apprLineNext
            wo.ReqDeptPk = reqDeptPk

            #req_dept_busi_cd
            wo.WorkSrcCode = work_src_cd
            wo.BreakdownDt = breakdown_dt
            wo.CauseCode = cause_cd
            wo.ProblemCode = problem_cd
            wo.ProjCode = proj_cd
            
            wo.Factory_id = factory_id
            #wo.InsertTs = insert_ts
            #wo.InserterId = inserter_id
            #wo.InserterName = inserter_nm
            wo.set_audit(user)
            wo.save()

            return {'success': True, 'message': '작업지시 정보가 수정되었습니다.'}

        elif action == 'acceptWorkOrder':
            ''' 작업요청승인
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            woStatusCd = posparam.get('woStatusCd')
            apprLineNext = posparam.get('apprLineNext')
            workTitle = posparam.get('workTitle')
            reqInfo = posparam.get('reqInfo')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.ApprLineNext = apprLineNext
            wo.WorkTitle = workTitle
            wo.ReqInfo = reqInfo
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'approvalWorkOrder':
            ''' 작업승인
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            workChargerPk = CommonUtil.try_int(posparam.get('workChargerPk'))
            woStatusCd = posparam.get('woStatusCd')
            apprLineNext = posparam.get('apprLineNext')
            workTitle = posparam.get('workTitle')
            planStartDt = posparam.get('planStartDt')
            startDt = posparam.get('startDt')
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')
            maintTypeCd = posparam.get('maintTypeCd')
            causeCd = posparam.get('causeCd')
            problemCd = posparam.get('problemCd')
            remedyCd = posparam.get('remedyCd')
            projCd = posparam.get('projCd')
            breakdownDt = posparam.get('breakdownDt')
            workSrcCd = posparam.get('workSrcCd')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.ApprLineNext = apprLineNext
            wo.WorkChargerPk = workChargerPk
            wo.PlanStartDt = planStartDt
            wo.PlanEndDt = planEndDt
            wo.StartDt = startDt
            wo.EndDt = endDt
            wo.MaintTypeCode = maintTypeCd
            wo.CauseCode = causeCd
            wo.ProblemCode = problemCd
            wo.RemedyCode = remedyCd
            wo.ProjCode = projCd
            if breakdownDt:
                wo.BreakdownDt = breakdownDt
            else:
                wo.BreakdownDt = None
            wo.WorkSrcCode = workSrcCd
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'inputResult':
            ''' 결과입력
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            workChargerPk = CommonUtil.try_int(posparam.get('workChargerPk'))
            deptPk = posparam.get('deptPk')
            workTitle = posparam.get('workTitle')
            planStartDt = posparam.get('planStartDt')
            startDt = posparam.get('startDt')
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')
            maintTypeCd = posparam.get('maintTypeCd')
            causeCd = posparam.get('causeCd')
            problemCd = posparam.get('problemCd')
            remedyCd = posparam.get('remedyCd')
            projCd = posparam.get('projCd')
            breakdownDt = posparam.get('breakdownDt')
            workSrcCd = posparam.get('workSrcCd')
            totCost = CommonUtil.try_int(posparam.get('totCost'))
            mtrlCost = CommonUtil.try_int(posparam.get('mtrlCost'))
            laborCost = CommonUtil.try_int(posparam.get('laborCost'))
            outsideCost = CommonUtil.try_int(posparam.get('outsideCost'))
            etcCost = CommonUtil.try_int(posparam.get('etcCost'))

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = deptPk
            wo.WorkChargerPk = workChargerPk
            wo.PlanStartDt = planStartDt
            wo.PlanEndDt = planEndDt
            wo.StartDt = startDt
            wo.EndDt = endDt
            wo.MaintTypeCode = maintTypeCd
            wo.CauseCode = causeCd
            wo.ProblemCode = problemCd
            wo.RemedyCode = remedyCd
            wo.ProjCode = projCd
            if breakdownDt:
                wo.BreakdownDt = breakdownDt
            else:
                wo.BreakdownDt = None
            wo.WorkSrcCode = workSrcCd
            wo.WorkText = workText
            wo.TotCost = totCost
            wo.MtrlCost = mtrlCost
            wo.LaborCost = laborCost
            wo.OutsideCost = outsideCost
            wo.EtcCost = etcCost
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'finishWorkOrder':
            ''' 작업완료
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            workChargerPk = CommonUtil.try_int(posparam.get('workChargerPk'))
            apprLineNext = posparam.get('apprLineNext')
            deptPk = posparam.get('deptPk')
            workTitle = posparam.get('workTitle')
            planStartDt = posparam.get('planStartDt')
            startDt = posparam.get('startDt')
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')
            maintTypeCd = posparam.get('maintTypeCd')
            causeCd = posparam.get('causeCd')
            problemCd = posparam.get('problemCd')
            remedyCd = posparam.get('remedyCd')
            projCd = posparam.get('projCd')
            breakdownDt = posparam.get('breakdownDt')
            workSrcCd = posparam.get('workSrcCd')
            totCost = CommonUtil.try_int(posparam.get('totCost'))
            mtrlCost = CommonUtil.try_int(posparam.get('mtrlCost'))
            laborCost = CommonUtil.try_int(posparam.get('laborCost'))
            outsideCost = CommonUtil.try_int(posparam.get('outsideCost'))
            etcCost = CommonUtil.try_int(posparam.get('etcCost'))

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.apprLineNext = apprLineNext
            wo.WoStatus = deptPk
            wo.WorkChargerPk = workChargerPk
            wo.PlanStartDt = planStartDt
            wo.PlanEndDt = planEndDt
            wo.StartDt = startDt
            wo.EndDt = endDt
            wo.MaintTypeCode = maintTypeCd
            wo.CauseCode = causeCd
            wo.ProblemCode = problemCd
            wo.RemedyCode = remedyCd
            wo.ProjCode = projCd
            if breakdownDt:
                wo.BreakdownDt = breakdownDt
            else:
                wo.BreakdownDt = None
            wo.WorkSrcCode = workSrcCd
            wo.WorkText = workText
            wo.TotCost = totCost
            wo.MtrlCost = mtrlCost
            wo.LaborCost = laborCost
            wo.OutsideCost = outsideCost
            wo.EtcCost = etcCost
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'completeWorkOrder':
            ''' 완료
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            workChargerPk = CommonUtil.try_int(posparam.get('workChargerPk'))
            woStatusCd = posparam.get('woStatusCd')
            breakdownMin = CommonUtil.try_int(posparam.get('breakdownMin'))

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.BreakdownMin = breakdownMin
            wo.set_audit(user)
            wo.save()
        
            items = {'success': True}

        elif action == 'rejectWorkOrder':
            ''' 승인반려
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            apprLineNext = posparam.get('apprLineNext')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.ApprLineNext = apprLineNext
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'rejectRequestWorkOrder':
            ''' 요청반려
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            woStatusCd = posparam.get('woStatusCd')
            apprLineNext = posparam.get('apprLineNext')
            workTitle = posparam.get('workTitle')
            reqInfo = posparam.get('reqInfo')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.ApprLineNext = apprLineNext
            wo.WorkTitle = workTitle
            wo.ReqInfo = reqInfo
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'updateStatus':
            ''' 
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            woStatusCd = posparam.get('woStatusCd')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'delete':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))

            q = CmWorkOrder.objects.filter(id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'getPinvLocMaterialByWorkOrder':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            sql = ''' 
            '''
            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'startDateEndDateDiff':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            sql = ''' 
            '''
            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'updateWorkOrderStartEndDate':
            ''' 
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.StartDt = startDt
            wo.EndDt = endDt
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'updateWorkOrderPlanStartEndDate':
            ''' 
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            planStartDt = posparam.get('planStartDt')
            planEndDt = posparam.get('planEndDt')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.PlanStartDt = planStartDt
            wo.PlanEndDt = planEndDt
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'checkBrokenWorkOrder':
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            equip_pk = CommonUtil.try_int(gparam.get('equip_pk'))
            woTypeCd = gparam.get('woTypeCd')
            woStatusEx = gparam.get('woStatusEx')
            woStatusEx2 = CommonUtil.convert_quotation_mark_string(woStatusEx)

            ''' SELECT count(*) as cnt
		    FROM cm_work_order t
		    inner join cm_base_code ws on t.wo_status = ws.code_cd 
		    and ws.code_grp_cd = 'WO_STATUS'
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    inner join cm_base_code mt on t.maint_type_cd = mt.code_cd 
		    and mt.code_grp_cd = 'MAINT_TYPE'
		    WHERE mt.code_cd = 'MAINT_TYPE_BM'
            AND t.factory_pk = %(factory_pk)s
            AND e.equip_pk = %(equipPk)s
            '''
            if woTypeCd:
                sql += ''' AND t.wo_type = %(woTypeCd)s
                '''
            else:
                sql += ''' AND t.work_order_pk = %(workOrderPk)s
                '''
            sql += ''' AND ws.code_cd NOT IN (''' + woStatusEx2 + ''')
            '''

            dc = {}
            dc['factory_pk'] = factory_id
            dc['workOrderPk'] = workOrderPk
            dc['equip_pk'] = equip_pk
            dc['woTypeCd'] = woTypeCd

            items = DbUtil.get_row(sql, dc)


        elif action == 'selectWorkOrderApprInfo':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            sql = ''' SELECT t.work_order_pk
		    , t.work_order_no
		    , t.appr_line
		    , t.appr_line_next
		    , t.wo_status as wo_status_cd
		    FROM cm_work_order t
		    WHERE t.wo_status IN ('WOS_CL', 'WOS_DL')
            AND t.factory_pk = %(factory_pk)s
            '''
            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'updateWorkOrderStatusBySysOpt':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            woStatusCd = posparam.get('woStatusCd')
            apprLine = posparam.get('apprLine')
            apprLineNext = posparam.get('apprLineNext')

            wo = CmWorkOrder.objects.get(id=workOrderPk)

            wo.WoStatus = woStatusCd
            wo.ApprLine = apprLine
            wo.ApprLineNext = apprLineNext
            wo.set_audit(user)
            wo.save()

            items = {'success': True}

        elif action == 'insertWorkOrderInspection':
            ''' 점검이상발행
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            workOrderNo = posparam.get('workOrderNo')
            workOrderSort = posparam.get('workOrderSort')
            workTitle = posparam.get('workTitle')
            workText = posparam.get('workText')
            workOrderApprovalPk = posparam.get('workOrderApprovalPk')
            workOrderApprovalPk = CommonUtil.try_int(workOrderApprovalPk)
            reqInfo = posparam.get('reqInfo')
            woStatusCd = posparam.get('woStatusCd')
            maintTypeCd = posparam.get('maintTypeCd')
            woType = posparam.get('woType')
            wantDt = posparam.get('wantDt')
            planStartDt = posparam.get('planStartDt')
            planEndDt = posparam.get('planEndDt')
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')
            deptPk = posparam.get('deptPk')
            workChargerPk = posparam.get('workChargerPk')
            pmPk = posparam.get('pmPk')
            apprLine = posparam.get('apprLine')
            apprLineNext = posparam.get('apprLineNext')
            reqDeptPk = posparam.get('reqDeptPk')
            pmReqType = posparam.get('pmReqType')
            work_src_cd = posparam.get('work_src_cd')
            breakdown_dt = posparam.get('breakdown_dt')
            cause_cd = posparam.get('cause_cd')
            problem_cd = posparam.get('problem_cd')
            remedyCd = posparam.get('remedyCd')
            proj_cd = posparam.get('proj_cd')
            work_src_cd = posparam.get('work_src_cd')
            totCost = posparam.get('totCost')
            mtrlCost = posparam.get('mtrlCost')
            laborCost = posparam.get('laborCost')
            outsideCost = posparam.get('outsideCost')
            etcCost = posparam.get('etcCost')
            if_send_yn = posparam.get('if_send_yn')
            chkRsltPk = posparam.get('chkRsltPk')
  

            wo = CmWorkOrder()
            wo.CmEquipment_id = equipPk
            wo.WorkOrderNo = workOrderNo
            wo.WorkOrderSort = workOrderSort
            wo.WorkTitle = workTitle
            wo.CmWorkOrderApproval_id = workOrderApprovalPk
            wo.ReqInfo = reqInfo
            wo.WoStatus = woStatusCd
            wo.MaintTypeCode = maintTypeCd
            wo.WoType = woType
            wo.WantDt = wantDt
            wo.PlanStartDt = planStartDt
            wo.PlanEndDt = planEndDt
            wo.StartDt = startDt
            wo.EndDt = endDt
            wo.DeptPk = deptPk
            wo.WorkChargerPk = workChargerPk
            
            wo.ApprLine = apprLine
            wo.ApprLineNext = apprLineNext
            wo.ReqDeptPk = reqDeptPk
            #req_dept_busi_cd
            wo.BreakdownDt = breakdown_dt if breakdown_dt else None
            wo.IfSendYn = 'N'
            wo.ChkRsltPk = chkRsltPk
            wo.RqstInspYn = rqstInspYn

            wo.Factory_id = factory_id
            #wo.InsertTs = insert_ts
            #wo.InserterId = inserter_id
            #wo.InserterName = inserter_nm
            wo.set_audit(user)
            wo.save()

            return {'success': True, }

        elif action in ['insertDailyReport', 'updateDailyReport']:
            ''' 작업일보등록
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            workOrderNo = posparam.get('workOrderNo')
            workOrderSort = posparam.get('workOrderSort')
            workTitle = posparam.get('workTitle')
            workText = posparam.get('workText')
            workOrderApprovalPk = posparam.get('workOrderApprovalPk')
            workOrderApprovalPk = CommonUtil.try_int(workOrderApprovalPk)
            reqInfo = posparam.get('reqInfo')
            woStatusCd = posparam.get('woStatusCd')
            maintTypeCd = posparam.get('maintTypeCd')
            woType = posparam.get('woType')
            wantDt = posparam.get('wantDt')
            planStartDt = posparam.get('planStartDt')
            planEndDt = posparam.get('planEndDt')
            startDt = posparam.get('startDt')
            endDt = posparam.get('endDt')
            deptPk = posparam.get('deptPk')
            workChargerPk = posparam.get('workChargerPk')
            pmPk = posparam.get('pmPk')
            apprLine = posparam.get('apprLine')
            apprLineNext = posparam.get('apprLineNext')
            reqDeptPk = posparam.get('reqDeptPk')
            pmReqType = posparam.get('pmReqType')
            work_src_cd = posparam.get('work_src_cd')
            breakdown_dt = posparam.get('breakdown_dt')
            cause_cd = posparam.get('cause_cd')
            problem_cd = posparam.get('problem_cd')
            remedyCd = posparam.get('remedyCd')
            proj_cd = posparam.get('proj_cd')
            work_src_cd = posparam.get('work_src_cd')
            totCost = posparam.get('totCost')
            mtrlCost = posparam.get('mtrlCost')
            laborCost = posparam.get('laborCost')
            outsideCost = posparam.get('outsideCost')
            etcCost = posparam.get('etcCost')
            if_send_yn = posparam.get('if_send_yn')
            chkRsltPk = posparam.get('chkRsltPk')
  
            if action == 'updateDailyReport':
                wo = CmWorkOrder.get(id=workOrderPk)
            else:
                wo = CmWorkOrder()
                wo.CmWorkOrderApproval_id = workOrderApprovalPk
                wo.IfSendYn = 'N'
                wo.RqstDprYn = rqstDprYn
                wo.Factory_id = factory_id

            wo.CmEquipment_id = equipPk
            if workOrderNo:
                wo.WorkOrderNo = workOrderNo
                wo.WorkOrderSort = workOrderSort
            wo.WorkTitle = workTitle
            
            wo.ReqInfo = reqInfo
            wo.WorkText = workText
            wo.WoStatus = woStatusCd
            wo.MaintTypeCode = maintTypeCd
            wo.WoType = woType
            wo.WantDt = wantDt
            if planStartDt:
                wo.PlanStartDt = planStartDt
            if planEndDt:
                wo.PlanEndDt = planEndDt
            if startDt:
                wo.StartDt = startDt
            if endDt:
                wo.EndDt = endDt
            wo.DeptPk = deptPk
            wo.WorkChargerPk = workChargerPk
            
            wo.ApprLine = apprLine
            wo.ApprLineNext = apprLineNext
            wo.ReqDeptPk = reqDeptPk
            #req_dept_busi_cd
            wo.BreakdownDt = breakdown_dt if breakdown_dt else None

            wo.CauseCode = causeCd
            wo.ProblemCode = problemCd
            wo.RemedyCode = remedyCd
            wo.ProjCode = projCd

            wo.TotCost = totCost
            wo.MtrlCost = mtrlCost
            wo.LaborCost = laborCost
            wo.OutsideCost = outsideCost
            wo.EtcCost = etcCost
            wo.WorkSrcCode = workSrcCd
            #wo.InsertTs = insert_ts
            #wo.InserterId = inserter_id
            #wo.InserterName = inserter_nm
            wo.set_audit(user)
            wo.save()

            return {'success': True, }

        elif action == 'getFullApprLine':
            ''' 이력포함 전체 appr_line (OC,AP,CM,CL)
            '''
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            sql = ''' with tt as (
				select unnest(string_to_array(appr_line, ',')) AS appr_line
				from cm_work_order
				where work_order_pk = %(workOrderPk)s
			)
			, ttt as (
				select tt.appr_line
				from tt
				group by tt.appr_line
				order by (case when tt.appr_line = 'RQ' then 1
				when tt.appr_line = 'OC' then 2
				when tt.appr_line = 'AP' then 3
				when tt.appr_line = 'CM' then 4
				when tt.appr_line = 'CL' then 5 else 0 end)
			)
			, cte as (
				select string_agg(ttt.appr_line::text, ',') as full_appr_line
				from ttt
			)
			select concat((case when substring(cte.full_appr_line, 1, 2) <> 'RQ' then 'RQ,' else '' end)
			, cte.full_appr_line) as full_appr_line
			from cte
            '''
            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_row(sql, dc)


        elif action == 'selectWorkOrderLogList':

            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            sql = ''' SELECT 1 as work_order_hist_pk
			 , wo.work_order_pk
			 , wo.work_order_no
			 , '작성(생성)' as after_status_nm
			 , wo.insert_ts as change_ts
			 , coalesce(wo.inserter_nm, fn_user_nm(cu."Name", 'N')) as changer_nm
			 , '' AS change_reason
		    from cm_work_order wo
		    inner join user_profile cu on cu."User_id" = wo.INSERTER_ID::integer
		    where wo.work_order_pk = %(workOrderPk)s
		    UNION ALL
		    SELECT woh.work_order_hist_pk
			    , woh.work_order_pk
			    , wo.work_order_no
			    , aws.code_nm as after_status_nm
			    , woh.change_ts as change_ts
			    , coalesce(woh.changer_nm, cm_fn_user_nm(cu."Name", 'N')) as changer_nm
			    , woh.change_reason
		    from cm_work_order_hist woh
		    inner join cm_base_code aws on woh.after_status = aws.code_cd 
		    and aws.code_grp_cd = 'WO_STATUS'
		    inner join user_profile cu on cu."User_id" = woh.changer_pk
		    inner join cm_work_order wo on woh.work_order_pk = wo.work_order_pk
		    where woh.work_order_pk = %(workOrderPk)s
		    order by change_ts desc, work_order_hist_pk desc
            '''
            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'insertEquipBom':
            ''' 완료시 설비의 BOM으로 자재 추가
            '''

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))

            sql = ''' insert into cm_equip_part_mtrl(equip_pk, mtrl_pk, amt, use_yn, del_yn, insert_ts, inserter_id, inserter_nm)
    	    SELECT wo.equip_pk, wm.mtrl_pk, 1, 'Y', 'N', CURRENT_TIMESTAMP, %(userId)s, %(userNm)s
		    FROM cm_wo_mtrl wm
		    INNER JOIN cm_material m ON wm.mtrl_pk = m.mtrl_pk
		    INNER JOIN cm_work_order wo ON wm.work_order_pk = wo.work_order_pk
		    LEFT JOIN cm_equip_part_mtrl epm ON wm.mtrl_pk = epm.mtrl_pk 
		    AND wo.equip_pk = epm.EQUIP_PK
		    WHERE wm.work_order_pk = %(workOrderPk)s
		    AND m.allow_add_bom = 'Y'
		    AND epm.mtrl_pk IS NULL
		    GROUP BY wo.equip_pk, wm.mtrl_pk
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk
            dc['userId'] = user.id
            dc['userNm'] = user.username

            ret = DbUtil.execute(sql, dc)

            items = {'success': True}

        elif action == 'getWorkOrderInfo':
            ''' workOrderPk로 간단한 정보 조회
            '''

            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))

            sql = ''' SELECT wo_status as wo_status_cd,
        		rqst_dpr_yn,
        		work_title,
				rqst_insp_yn,
				work_order_pk, work_order_no, wo_status,
				equip_pk, wo_type, maint_type_cd, factory_pk as site_id,
				req_dept_busi_cd, req_dept_pk, req_info,
				req_info_img_grp_cd, want_dt, breakdown_dt, breakdown_min, problem_cd, cause_cd, remedy_cd,
				plan_start_dt, plan_end_dt, start_dt, end_dt, dept_pk, work_charger_pk, work_text, work_text_img_grp_cd,
				work_src_cd, tot_cost, mtrl_cost, labor_cost, outside_cost, etc_cost, chk_rslt_pk, pm_pk, pm_req_type,
				work_order_sort,
				appr_line, appr_line_next, work_order_approval_pk, proj_cd
            FROM cm_work_order
            WHERE work_order_pk = %(workOrderPk)s
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'changeEquip':
            ''' 설비변경
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))

            q = CmWorkOrder.objects.filter(id=workOrderPk)
            q.update(CmEquipment_id=equipPk)

            items = {'success': True}

        elif action == 'updateBreakDownMin':
            ''' 고장시간(분) 업데이트
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            breakdownMin = CommonUtil.try_int(posparam.get('breakdownMin'))

            q = CmWorkOrder.objects.filter(id=workOrderPk)
            q.update(BreakdownMin=breakdownMin)

            items = {'success': True}

        elif action == 'getWorkOrderInfoByNo':
            ''' workOrderPk로 간단한 정보 조회
            '''

            workOrderNo = posparam.get('workOrderNo')

            sql = ''' select work_order_pk
    		, work_order_no
    		, wo_status as wo_status_cd
    		, factory_pk as site_id
		    from cm_work_order
		    where work_order_no = %(workOrderPk)s
		    and factory_pk = %(factory_pk)s
            '''

            dc = {}
            dc['workOrderNo'] = workOrderNo
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'updateFirstAssetStatus':
            ''' 
            '''
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            firstAssetStatus = posparam.get('firstAssetStatus')

            q = CmEquipment.objects.filter(id=workOrderPk)
            q.update(FirstAssetStatus=firstAssetStatus)

            items = {'success': True}

        elif action == 'deleteWoLabor':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWoLabor.objects.filter(WorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'deleteWoMtrl':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWoMtrl.objects.filter(WorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'deleteWoSupplier':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWorkOrderSupplier.objects.filter(WorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'deleteWoFaultLoc':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWoFaultLoc.objects.filter(WorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'deleteWohist':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWorkOrderHist.objects.filter(WorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'deleteWo':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWorkOrder.objects.filter(id=workOrderPk)
            q.delete()

            items = {'success': True}

        elif action == 'updateCostInfo':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            totCost = CommonUtil.try_int(posparam.get('totCost'))
            mtrlCost = CommonUtil.try_int(posparam.get('mtrlCost'))
            laborCost = CommonUtil.try_int(posparam.get('laborCost'))
            etcCost = CommonUtil.try_int(posparam.get('etcCost'))
            costType = posparam.get('costType')

            c = CmWorkOrder.objects.filter(id=workOrderPk)
            c.TotCost = totCost
            c.MtrlCost = mtrlCost
            c.LaborCost = laborCost
            #c.OutsideCost = laborCost
            c.EtcCost = etcCost
            c.CostType = costType
            c.save()

            items = {'success': True}

 
    except Exception as ex:
        source = 'kmms/work_order : action-{}'.format(action)
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