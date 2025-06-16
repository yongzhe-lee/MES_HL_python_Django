from django import db
from app.views.kmms.work_order_hist import DateUtil
from domain.models import user
from domain.services.kmms.work_order import WorkOrderService
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWorkOrder, CmEquipment, CmWoLabor, CmWoMtrl, CmWorkOrderSupplier, CmWoFaultLoc, CmWorkOrderHist

def handle_work_order_approval(posparam, request):
    """
    작업지시 결재 정보를 처리하는 메소드
    Args:
        posparam: POST 파라미터
        request: HTTP 요청 객체
    Returns:
        workOrderApprovalPk: 생성된 작업지시 결재 PK
    """
    from app.views.kmms.work_order_approval import work_order_approval
    
    # work_order_approval 호출을 위한 context 생성
    class Context:
        def __init__(self, gparam, posparam, request):
            self.gparam = gparam
            self.posparam = posparam
            self.request = request
    
    # action을 insert로 설정
    gparam = {'action': 'insert'}
    context = Context(gparam, posparam, request)
    
    # work_order_approval 호출
    result = work_order_approval(context)
    
    if result.get('success'):
        # 생성된 workOrderApprovalPk 반환
        return result.get('workOrderApprovalPk')
    else:
        raise Exception(result.get('message', '작업지시 결재 정보 저장 실패'))

def handle_work_order_hist(work_order_pk, posparam, request):
    """
    작업지시 이력 저장을 처리하는 함수
    Args:
        work_order_pk: 작업지시 PK
        posparam: POST 파라미터
        request: HTTP 요청 객체
    """
    from app.views.kmms.work_order_hist import work_order_hist

    # context 객체 생성
    class Context:
        def __init__(self, gparam, posparam, request):
            self.gparam = gparam
            self.posparam = posparam
            self.request = request

    gparam = {'action': 'save'}
    # posparam 복사 및 work_order_pk 추가
    posparam = dict(posparam)
    posparam['changerPk'] = request.user.id
    posparam['beforeStatusCd'] = 'WOS_RQ'
    posparam['afterStatusCd'] = 'WOS_RQ'
    posparam['changerNm'] = request.user.username
    posparam['workOrderPk'] = work_order_pk
    context = Context(gparam, posparam, request)

    # work_order_hist 함수 실행
    result = work_order_hist(context)

    return result

def work_order(context):
    '''
    api/kmms/work_order   작업지시 
    김태영 

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

    workorder_service = WorkOrderService()

    try:
        if action == 'findOneWo':
            ''' 
            '''
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))
            
            sql = '''
            /* findOne [work-order-mapper.xml] */

            select t.work_order_pk
                    , t.work_order_no
                    , t.work_title
                    , t.work_text
                    , t.work_order_sort
                    , t.req_dept_pk
                    , rd.dept_nm as req_dept_nm
                    , rd.tpm_yn as req_dept_tpm_yn
                    , t.dept_pk
                    , wd.dept_nm as dept_nm
                    , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
                    , cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 'WEZON') as business_nm
                    , t.work_charger_pk
                    , cm_fn_user_nm(wcu.user_nm, wcu.del_yn) as work_charger_nm
                    , mt.code_cd as maint_type_cd
                    , mt.code_nm as maint_type_nm
                    , ws.code_cd as wo_status_cd
                    , ws.code_nm as wo_status_nm
                    , t.plan_start_dt
                    , t.plan_end_dt
                    , t.start_dt
                    , t.end_dt
                    , to_char(t.want_dt, 'yyyy-MM-dd') as want_dt
                    , t.equip_pk
                    , e.equip_cd
                    , e.equip_nm
                    , ed.dept_pk as equip_dept_pk
                    , ed.dept_nm as equip_dept_nm
                    , to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
                    , t.pm_pk
                    , p.pm_no
                    , p.pm_nm
                    , pt.code_nm                        AS pm_type_nm
                    , p.work_text as pm_work_text
                    , t.chk_rslt_pk
                    , ecs.chk_sche_pk
                    , ecs.chk_sche_no
                    , ecm.chk_mast_nm
                    , ecm.chk_mast_pk
                    , ecs.chk_sche_dt
                    , l.loc_nm
                    , t.req_info
                    , t.wo_type
                    , t.rqst_insp_yn
                    , t.rqst_dpr_yn
                    , wt.code_nm as wo_type_nm
                    , to_char(t.breakdown_dt, 'yyyy-MM-dd') as breakdown_dt
                    , t.breakdown_min
                    , wsc.code_cd as work_src_cd
                    , wsc.code_nm as work_src_nm
                    , t.tot_cost
                    , t.mtrl_cost
                    , t.labor_cost
                    , t.outside_cost
                    , t.etc_cost
                    , t.problem_cd
                    , wp.reliab_nm as problem_nm
                    , t.cause_cd
                    , wc.reliab_nm as cause_nm
                    , t.remedy_cd
                    , wr.reliab_nm as remedy_nm
                    , prj.proj_cd
                    , prj.proj_nm
                    , t.wo_file_grp_cd
                    , t.req_info_img_grp_cd
                    , t.work_text_img_grp_cd
                    , t.pm_req_type
                    , t.req_dept_busi_cd
                    , t.appr_line
                    , t.appr_line_next
                    , t.work_order_approval_pk
                    , woa.reg_dt
                    , woa.rqst_dt
                    , woa.rqst_user_nm
                    , woarqstd.dept_pk as rqst_dept_pk
                    , woarqstd.dept_nm as rqst_dept_nm
                    , woa.cancel_dt
                    , woa.cancel_user_nm
                    , woa.accept_dt
                    , woa.appr_dt
                    , woa.finish_dt
                    , substring(t.appr_line, 1,2) as wo_start_type
                    , cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
                    , t.insert_ts
                    , e.environ_equip_yn
                    , e.equip_status as equip_stauts_cd
                    , e.import_rank_pk
                    , ir.import_rank_cd
                    , e.up_equip_pk
                    , ue.equip_nm AS up_equip_name
                    , ec.equip_category_id
                    , ec.equip_category_desc
                    , ec.remark
                    , e.equip_class_path
                    , e.equip_class_desc
                    , av.code_nm as first_asset_status
                    , av.code_cd as first_asset_status_cd
                    , cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
                    , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
                    , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm
                    , l.loc_nm
                    , es.ex_supplier_nm
                    , woa.cancel_reason
                    , t.cost_type
                    , (select code_nm from cm_base_code where code_cd = t.cost_type and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm

            from cm_work_order t
                inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
                inner join cm_base_code mt on t.maint_type_cd = mt.code_cd and mt.code_grp_cd = 'MAINT_TYPE'
                inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
                inner join cm_equipment e on t.equip_pk = e.equip_pk
                inner join cm_location l on e.loc_pk = l.loc_pk
                left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
                left outer join cm_dept ed on e.dept_pk  = ed.dept_pk
                left outer join cm_dept wd on t.dept_pk = wd.dept_pk
                left outer join cm_dept rd on t.req_dept_pk = rd.dept_pk
                left outer join cm_user_info wcu on t.work_charger_pk = wcu.user_pk
                left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC' 
                left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC' 
                left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC' 
                left outer join cm_pm p on t.pm_pk = p.pm_pk
                left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
                left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
                left outer join cm_user_info pmu on p.pm_user_pk = pmu.user_pk
                left outer join cm_user_info wou on t.WORK_CHARGER_PK = wou.user_pk
                left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
                left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
                left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
                left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
                left outer join cm_project prj on t.proj_cd = prj.proj_cd
                left outer join cm_user_info woarqstu on woa.rqst_user_pk = woarqstu.user_pk
                left outer join cm_dept woarqstd on woarqstu.dept_pk = woarqstd.dept_pk
                left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
                left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
                left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
                left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
                left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
                left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
            where 1 = 1

            AND t.work_order_pk = %(workOrderPk)s
            '''
            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_row(sql, dc)

        elif action=='my_work_request_read':
            keyword = gparam.get('keyword', None)
            req_dept = gparam.get('req_dept', None)
            rqst_user_nm = gparam.get('rqst_user_nm', None)
            start_dt = gparam.get('start_dt', None)
            end_dt = gparam.get('end_dt', None)
            wo_status = gparam.get('wo_status', None)
            maint_type_cd = gparam.get('maint_type_cd', None)
            dept_pk = gparam.get('dept_pk', None)
            problem_cd = gparam.get('problem_cd', None)
            cause_cd = gparam.get('cause_cd', None)
            srch_wo_no_only = gparam.get('srch_wo_no_only', None)
            srch_my_req_only = gparam.get('srch_my_req_only', None)
            srch_environ_equip_only = gparam.get('srch_environ_equip_only', None)
            srch_non_del_only = gparam.get('srch_non_del_only', None)

            wos_type = gparam.get('wos_type', None)

            current_user_id = user.id

            try:
                items = workorder_service.get_work_order_list(keyword, req_dept, rqst_user_nm, start_dt, end_dt, wo_status, maint_type_cd, dept_pk, problem_cd, cause_cd, srch_wo_no_only, srch_my_req_only, srch_environ_equip_only, srch_non_del_only, wos_type, current_user_id)
            except Exception as ex:
                source = 'api/kmms/work_order, action:{}'.format(action)
                LogWriter.add_dblog('error', source, ex)
                raise ex

        elif action == 'wo_equip_disposed': 
            equipPk = gparam.get('equipPk')

            sql = '''
              /* searchAll [work-order-mapper.xml] */

        select t.work_order_pk
                , t.work_order_no
                , t.work_title
                , t.work_text
                , t.work_order_sort
                , t.req_dept_pk
                , rd.dept_nm as req_dept_nm
                , rd.tpm_yn as req_dept_tpm_yn
                , t.dept_pk
                , wd.dept_nm as dept_nm
                , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
                , cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 'WEZON') as business_nm
                , t.work_charger_pk
                , cm_fn_user_nm(wcu.user_nm, wcu.del_yn) as work_charger_nm
                , mt.code_cd as maint_type_cd
                , mt.code_nm as maint_type_nm
                , ws.code_cd as wo_status_cd
                , ws.code_nm as wo_status_nm
                , t.plan_start_dt
                , t.plan_end_dt
                , t.start_dt
                , t.end_dt
                , t.want_dt
                , t.equip_pk
                , e.equip_cd
                , e.equip_nm
                , ed.dept_pk as equip_dept_pk
                , ed.dept_nm as equip_dept_nm
                , to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
                , t.pm_pk
                , p.pm_no
                , p.pm_nm
                , pt.code_nm                        AS pm_type_nm
                , p.work_text as pm_work_text
                , t.chk_rslt_pk
                , ecs.chk_sche_pk
                , ecs.chk_sche_no
                , ecm.chk_mast_nm
                , ecm.chk_mast_pk
                , ecs.chk_sche_dt
                , l.loc_nm
                , t.req_info
                , t.wo_type
                , t.rqst_insp_yn
                , t.rqst_dpr_yn
                , wt.code_nm as wo_type_nm
                , t.breakdown_dt
                , t.breakdown_min
                , wsc.code_cd as work_src_cd
                , wsc.code_nm as work_src_nm
                , t.tot_cost
                , t.mtrl_cost
                , t.labor_cost
                , t.outside_cost
                , t.etc_cost
                , t.problem_cd
                , wp.reliab_nm as problem_nm
                , t.cause_cd
                , wc.reliab_nm as cause_nm
                , t.remedy_cd
                , wr.reliab_nm as remedy_nm
                , prj.proj_cd
                , prj.proj_nm
                , t.wo_file_grp_cd
                , t.req_info_img_grp_cd
                , t.work_text_img_grp_cd
                , t.pm_req_type
                , t.req_dept_busi_cd
                , t.appr_line
                , t.appr_line_next
                , t.work_order_approval_pk
                , woa.reg_dt
                , woa.rqst_dt
                , woa.rqst_user_nm
                , woarqstd.dept_pk as rqst_dept_pk
                , woarqstd.dept_nm as rqst_dept_nm
                , woa.cancel_dt
                , woa.cancel_user_nm
                , woa.accept_dt
                , woa.appr_dt
                , woa.finish_dt
                , substring(t.appr_line, 1,2) as wo_start_type
                , cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
                , t.insert_ts
                , e.environ_equip_yn
                , e.equip_status as equip_stauts_cd
                , e.import_rank_pk
                , ir.import_rank_cd
                , e.up_equip_pk
                , ue.equip_nm AS up_equip_name
                , ec.equip_category_id
                , ec.equip_category_desc
                , ec.remark
                , e.equip_class_path
                , e.equip_class_desc
                , av.code_nm as first_asset_status
                , av.code_cd as first_asset_status_cd
                , cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
                , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
                , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm
                , l.loc_nm
                , es.ex_supplier_nm
                , woa.cancel_reason
                , t.cost_type
                , (select code_nm from cm_base_code where code_cd = t.cost_type and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm

        from cm_work_order t
    inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
    inner join cm_base_code mt on t.maint_type_cd = mt.code_cd and mt.code_grp_cd = 'MAINT_TYPE'
    inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
    inner join cm_equipment e on t.equip_pk = e.equip_pk
    inner join cm_location l on e.loc_pk = l.loc_pk
    left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
    left outer join cm_dept ed on e.dept_pk  = ed.dept_pk
    left outer join cm_dept wd on t.dept_pk = wd.dept_pk
    left outer join cm_dept rd on t.req_dept_pk = rd.dept_pk
    left outer join cm_user_info wcu on t.work_charger_pk = wcu.user_pk
    left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC' 
    left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC' 
    left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC' 
    left outer join cm_pm p on t.pm_pk = p.pm_pk
    left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
    left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
    left outer join cm_user_info pmu on p.pm_user_pk = pmu.user_pk
    left outer join cm_user_info wou on t.WORK_CHARGER_PK = wou.user_pk
    left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
    left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
    left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
    left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
    left outer join cm_project prj on t.proj_cd = prj.proj_cd
    left outer join cm_user_info woarqstu on woa.rqst_user_pk = woarqstu.user_pk
    left outer join cm_dept woarqstd on woarqstu.dept_pk = woarqstd.dept_pk
    left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
    left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
    left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
    left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
    left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
    left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
        where 1 = 1
            AND t.equip_pk = %(equipPk)s

            AND t.wo_status NOT IN (
                    'WOS_DL'
                 ,  
                    'WOS_CL'
                 ,  
                    'WOS_RW'
            )
            
            

             '''
            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_rows(sql, dc)
            items = CommonUtil.res_snake_to_camel(items)

        elif action == 'findSel':       
            keywords = gparam.get('keywords')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')
            isMine = gparam.get('isMine')

            sql = '''
             /* findAll [work-order-mapper.xml] */

                with cte as (

                select t.work_order_pk
                        , t.work_order_no
                        , t.work_title
                        , t.work_text
                        , t.work_order_sort
                        , t.req_dept_pk
                        , rd.dept_nm as req_dept_nm
                        , rd.tpm_yn as req_dept_tpm_yn
                        , t.dept_pk
                        , wd.dept_nm as dept_nm
                        , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
                        , cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 'WEZON') as business_nm
                        , t.work_charger_pk
                        , cm_fn_user_nm(wcu.user_nm, wcu.del_yn) as work_charger_nm
                        , mt.code_cd as maint_type_cd
                        , mt.code_nm as maint_type_nm
                        , ws.code_cd as wo_status_cd
                        , ws.code_nm as wo_status_nm
                        , t.plan_start_dt
                        , t.plan_end_dt
                        , t.start_dt
                        , t.end_dt
                        , to_char(t.start_dt, 'YYYY-MM-DD HH24:MI') || ' ~ ' || to_char(t.end_dt, 'YYYY-MM-DD HH24:MI') as startEndPeriod
                        , to_char(t.want_dt, 'YYYY-MM-DD') as want_dt
                        , t.equip_pk
                        , e.equip_cd
                        , e.equip_nm
                        , ed.dept_pk as equip_dept_pk
                        , ed.dept_nm as equip_dept_nm
                        , to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
                        , t.pm_pk
                        , p.pm_no
                        , p.pm_nm
                        , pt.code_nm                        AS pm_type_nm
                        , p.work_text as pm_work_text
                        , t.chk_rslt_pk
                        , ecs.chk_sche_pk
                        , ecs.chk_sche_no
                        , ecm.chk_mast_nm
                        , ecm.chk_mast_pk
                        , ecs.chk_sche_dt
                        , l.loc_nm
                        , t.req_info
                        , t.wo_type
                        , t.rqst_insp_yn
                        , t.rqst_dpr_yn
                        , wt.code_nm as wo_type_nm
                        , to_char(t.breakdown_dt, 'YYYY-MM-DD') as breakdown_dt
                        , t.breakdown_min
                        , wsc.code_cd as work_src_cd
                        , wsc.code_nm as work_src_nm
                        , t.tot_cost
                        , t.mtrl_cost
                        , t.labor_cost
                        , t.outside_cost
                        , t.etc_cost
                        , t.problem_cd
                        , wp.reliab_nm as problem_nm
                        , t.cause_cd
                        , wc.reliab_nm as cause_nm
                        , t.remedy_cd
                        , wr.reliab_nm as remedy_nm
                        , prj.proj_cd
                        , prj.proj_nm
                        , t.wo_file_grp_cd
                        , t.req_info_img_grp_cd
                        , t.work_text_img_grp_cd
                        , t.pm_req_type
                        , t.req_dept_busi_cd
                        , t.appr_line
                        , t.appr_line_next
                        , t.work_order_approval_pk
                        , woa.reg_dt
                        , to_char(woa.rqst_dt, 'YYYY-MM-DD HH24:MI') as rqst_dt
                        , woa.rqst_user_nm
                        , woarqstd.dept_pk as rqst_dept_pk
                        , woarqstd.dept_nm as rqst_dept_nm
                        , woa.cancel_dt
                        , woa.cancel_user_nm
                        , woa.accept_dt
                        , woa.appr_dt
                        , woa.finish_dt
                        , substring(t.appr_line, 1,2) as wo_start_type
                        , cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
                        , t.insert_ts
                        , e.environ_equip_yn
                        , e.equip_status as equip_stauts_cd
                        , e.import_rank_pk
                        , ir.import_rank_cd
                        , e.up_equip_pk
                        , ue.equip_nm AS up_equip_name
                        , ec.equip_category_id
                        , ec.equip_category_desc
                        , ec.remark
                        , e.equip_class_path
                        , e.equip_class_desc
                        , av.code_nm as first_asset_status
                        , av.code_cd as first_asset_status_cd
                        , cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
                        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
                        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm
                        , l.loc_nm
                        , es.ex_supplier_nm
                        , woa.cancel_reason
                        , t.cost_type
                        , (select code_nm from cm_base_code where code_cd = t.cost_type and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm

                from cm_work_order t
                    inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
                    inner join cm_base_code mt on t.maint_type_cd = mt.code_cd and mt.code_grp_cd = 'MAINT_TYPE'
                    inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
                    inner join cm_equipment e on t.equip_pk = e.equip_pk
                    inner join cm_location l on e.loc_pk = l.loc_pk
                    left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
                    left outer join cm_dept ed on e.dept_pk  = ed.dept_pk
                    left outer join cm_dept wd on t.dept_pk = wd.dept_pk
                    left outer join cm_dept rd on t.req_dept_pk = rd.dept_pk
                    left outer join cm_user_info wcu on t.work_charger_pk = wcu.user_pk
                    left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC' 
                    left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC' 
                    left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC' 
                    left outer join cm_pm p on t.pm_pk = p.pm_pk
                    left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
                    left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
                    left outer join cm_user_info pmu on p.pm_user_pk = pmu.user_pk
                    left outer join cm_user_info wou on t.WORK_CHARGER_PK = wou.user_pk
                    left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
                    left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
                    left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
                    left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
                    left outer join cm_project prj on t.proj_cd = prj.proj_cd
                    left outer join cm_user_info woarqstu on woa.rqst_user_pk = woarqstu.user_pk
                    left outer join cm_dept woarqstd on woarqstu.dept_pk = woarqstd.dept_pk
                    left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
                    left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
                    left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
                    left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
                    left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
                    left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk
                where 1 = 1

                    AND t.wo_status NOT IN (

                            'WOS_RW'

                    )

                    AND t.wo_status IN (

                            'WOS_RW'
                         ,  
                            'WOS_RB'
                         ,  
                            'WOS_RQ'
                         ,  
                            'WOS_OC'
                         ,  
                            'WOS_AP'
                         ,  
                            'WOS_CM'
                         ,  
                            'WOS_CL'
                         ,  
                            'WOS_DL'

                    )

                    --AND t.wo_type = 'WO'

                    --AND woa.rqst_user_pk = 1

                     AND (
                        (date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
                                        when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date('2022-08-09', 'YYYY-MM-DD')
                            AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
                                        when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date('2025-05-31', 'YYYY-MM-DD'))
                        OR
                        (date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
                                        when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date('2022-08-09', 'YYYY-MM-DD')
                            AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
                                            when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date('2025-05-31', 'YYYY-MM-DD'))
                    )

                    --AND t.WO_TYPE = 'WO'

                )
                SELECT *
                FROM (
                    table cte
                         order by rqst_dt DESC
                            , 
                                work_order_sort DESC 


                ) sub
                RIGHT JOIN (select count(*) from cte) c(total_rows) on true
                WHERE total_rows != 0
                order by pm_no desc, work_order_no desc

             '''
            dc={}
            dc['keywords'] = keywords
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['isMine'] = isMine

            items = DbUtil.get_rows(sql, dc)

        elif action == 'work_order_approval_read':       
            keywords = gparam.get('keywords')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')
            isMine = gparam.get('isMine')

            sql = '''
             /* findAll [work-order-mapper.xml] */

                with cte as (

                select t.work_order_pk
                        , t.work_order_no
                        , t.work_title
                        , t.work_text
                        , t.work_order_sort
                        , t.req_dept_pk
                        , rd.dept_nm as req_dept_nm
                        , rd.tpm_yn as req_dept_tpm_yn
                        , t.dept_pk
                        , wd.dept_nm as dept_nm
                        , cm_fn_get_dept_team_pk(t.dept_pk) as dept_team_pk
                        , cm_fn_get_dept_cd_business_nm(t.req_dept_busi_cd, 'WEZON') as business_nm
                        , t.work_charger_pk
                        , cm_fn_user_nm(wcu.user_nm, wcu.del_yn) as work_charger_nm
                        , mt.code_cd as maint_type_cd
                        , mt.code_nm as maint_type_nm
                        , ws.code_cd as wo_status_cd
                        , ws.code_nm as wo_status_nm
                        , t.plan_start_dt
                        , t.plan_end_dt
                        , t.start_dt
                        , t.end_dt
                        , t.want_dt
                        , t.equip_pk
                        , e.equip_cd
                        , e.equip_nm
                        , ed.dept_pk as equip_dept_pk
                        , ed.dept_nm as equip_dept_nm
                        , to_char(e.warranty_dt, 'YYYY-MM-DD') AS warranty_dt
                        , t.pm_pk
                        , p.pm_no
                        , p.pm_nm
                        , pt.code_nm                        AS pm_type_nm
                        , p.work_text as pm_work_text
                        , t.chk_rslt_pk
                        , ecs.chk_sche_pk
                        , ecs.chk_sche_no
                        , ecm.chk_mast_nm
                        , ecm.chk_mast_pk
                        , ecs.chk_sche_dt
                        , l.loc_nm
                        , t.req_info
                        , t.wo_type
                        , t.rqst_insp_yn
                        , t.rqst_dpr_yn
                        , wt.code_nm as wo_type_nm
                        , t.breakdown_dt
                        , t.breakdown_min
                        , wsc.code_cd as work_src_cd
                        , wsc.code_nm as work_src_nm
                        , t.tot_cost
                        , t.mtrl_cost
                        , t.labor_cost
                        , t.outside_cost
                        , t.etc_cost
                        , t.problem_cd
                        , wp.reliab_nm as problem_nm
                        , t.cause_cd
                        , wc.reliab_nm as cause_nm
                        , t.remedy_cd
                        , wr.reliab_nm as remedy_nm
                        , prj.proj_cd
                        , prj.proj_nm
                        , t.wo_file_grp_cd
                        , t.req_info_img_grp_cd
                        , t.work_text_img_grp_cd
                        , t.pm_req_type
                        , t.req_dept_busi_cd
                        , t.appr_line
                        , t.appr_line_next
                        , t.work_order_approval_pk
                        , woa.reg_dt
                        , woa.rqst_dt
                        , woa.rqst_user_nm
                        , woarqstd.dept_pk as rqst_dept_pk
                        , woarqstd.dept_nm as rqst_dept_nm
                        , woa.cancel_dt
                        , woa.cancel_user_nm
                        , woa.accept_dt
                        , woa.appr_dt
                        , woa.finish_dt
                        , substring(t.appr_line, 1,2) as wo_start_type
                        , cm_fn_datediff(cast(now() as timestamp), cast(t.plan_end_dt as timestamp)) as delay_days
                        , t.insert_ts
                        , e.environ_equip_yn
                        , e.equip_status as equip_stauts_cd
                        , e.import_rank_pk
                        , ir.import_rank_cd
                        , e.up_equip_pk
                        , ue.equip_nm AS up_equip_name
                        , ec.equip_category_id
                        , ec.equip_category_desc
                        , ec.remark
                        , e.equip_class_path
                        , e.equip_class_desc
                        , av.code_nm as first_asset_status
                        , av.code_cd as first_asset_status_cd
                        , cm_fn_minutediff(cast(t.start_dt as timestamp), cast(t.end_dt as timestamp)) as breakdown_Hr
                        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIPMENT_PROCESS' and code_cd = e.process_cd) as process_nm
                        , (select code_nm from cm_base_code where code_grp_cd = 'EQUIP_SYSTEM' and code_cd = e.system_cd) as system_nm
                        , l.loc_nm
                        , es.ex_supplier_nm
                        , woa.cancel_reason
                        , t.cost_type
                        , (select code_nm from cm_base_code where code_cd = t.cost_type and code_grp_cd = 'WO_COST_TYPE') as cost_type_nm

                        from cm_work_order t
                    inner join cm_work_order_approval woa on t.work_order_approval_pk = woa.work_order_approval_pk
                    inner join cm_base_code mt on t.maint_type_cd = mt.code_cd and mt.code_grp_cd = 'MAINT_TYPE'
                    inner join cm_base_code ws on t.wo_status = ws.code_cd and ws.code_grp_cd = 'WO_STATUS'
                    inner join cm_equipment e on t.equip_pk = e.equip_pk
                    inner join cm_location l on e.loc_pk = l.loc_pk
                    left join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
                    left outer join cm_dept ed on e.dept_pk  = ed.dept_pk
                    left outer join cm_dept wd on t.dept_pk = wd.dept_pk
                    left outer join cm_dept rd on t.req_dept_pk = rd.dept_pk
                    left outer join cm_user_info wcu on t.work_charger_pk = wcu.user_pk
                    left outer join cm_reliab_codes wp on t.problem_cd = wp.reliab_cd and wp."types" = 'PC' 
                    left outer join cm_reliab_codes wc on t.cause_cd  = wc.reliab_cd and wc."types" = 'CC' 
                    left outer join cm_reliab_codes wr on t.remedy_cd  = wr.reliab_cd and wr."types" = 'RC' 
                    left outer join cm_pm p on t.pm_pk = p.pm_pk
                    left outer join cm_base_code ct on p.cycle_type = ct.code_cd and ct.code_grp_cd = 'CYCLE_TYPE'
                    left outer join cm_base_code pt on p.pm_type  = pt.code_cd and pt.code_grp_cd = 'PM_TYPE'
                    left outer join cm_user_info pmu on p.pm_user_pk = pmu.user_pk
                    left outer join cm_user_info wou on t.WORK_CHARGER_PK = wou.user_pk
                    left outer join cm_equip_chk_rslt ecr on t.chk_rslt_pk = ecr.chk_rslt_pk
                    left outer join cm_equip_chk_sche ecs on ecr.chk_sche_pk  = ecs.chk_sche_pk
                    left outer join cm_equip_chk_mast ecm on ecs.chk_mast_pk = ecm.chk_mast_pk
                    left outer join cm_base_code wsc on t.work_src_cd = wsc.code_cd and wsc.code_grp_cd = 'WORK_SRC'
                    left outer join cm_project prj on t.proj_cd = prj.proj_cd
                    left outer join cm_user_info woarqstu on woa.rqst_user_pk = woarqstu.user_pk
                    left outer join cm_dept woarqstd on woarqstu.dept_pk = woarqstd.dept_pk
                    left outer join cm_base_code wt on t.wo_type = wt.code_cd and wt.code_grp_cd = 'WO_TYPE'
                    left outer join cm_IMPORT_RANK ir on e.IMPORT_RANK_PK = ir.IMPORT_RANK_PK
                    left outer join cm_equipment ue on e.UP_EQUIP_PK  = ue.EQUIP_PK
                    left outer join cm_base_code av on av.code_cd = e.first_asset_status and av.code_grp_cd = 'ASSET_VAL_STATUS'
                    left outer join cm_work_order_supplier wos on wos.work_order_pk = t.work_order_pk
                    left outer join cm_ex_supplier es on es.ex_supplier_pk = wos.ex_supplier_pk

                where 1 = 1

                    AND substring(t.appr_line, 1, 2) = 'RQ'

                    AND t.wo_type NOT IN (

                            'PM'

                    )

                    AND t.wo_status NOT IN (

                            'WOS_DL'
                         ,  
                            'WOS_CL'
                         ,  
                            'WOS_RW'

                    )

                    AND t.wo_status IN (

                            'WOS_RQ'
                         ,  
                            'WOS_RJ'

                    )
                    '''
            if keywords:
                sql += '''

                    AND (
                        UPPER(t.work_title) LIKE CONCAT('%',UPPER(CAST(%(keywords)s as text)),'%')
                        OR UPPER(t.work_text) LIKE CONCAT('%',UPPER(CAST(%(keywords)s as text)),'%')
                        OR UPPER(e.equip_nm) LIKE CONCAT('%',UPPER(CAST(%(keywords)s as text)),'%')
                        OR UPPER(e.equip_cd) LIKE CONCAT('%',UPPER(CAST(%(keywords)s as text)),'%')
                        OR UPPER(t.work_order_no) LIKE CONCAT('%',UPPER(CAST(%(keywords)s as text)),'%')
                    )
                    '''

            if startDate or endDate:
                sql += '''
                     AND (
                        (date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
                                        when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) >= to_date('2025-06-09', 'YYYY-MM-DD')
                            AND date(case when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.start_dt)
                                        when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.start_dt, t.plan_start_dt) end) <= to_date('2025-06-16', 'YYYY-MM-DD'))
                        OR
                        (date(case 		when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
                                        when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) >= to_date('2025-06-09', 'YYYY-MM-DD')
                            AND date(case 	when 'rqstdt' = 'rqstdt' then COALESCE(woa.rqst_dt, t.end_dt)
                                            when 'rqstdt' = 'wantdt' then COALESCE(t.want_dt, woa.rqst_dt) else coalesce(t.end_dt, t.plan_end_dt) end) <= to_date('2025-06-16', 'YYYY-MM-DD'))
                    )
                    '''

            sql += '''

                    AND coalesce(t.rqst_dpr_yn, 'N') = 'N'

                )
                SELECT *
                FROM (
                    table cte

                         order by rqst_dt DESC
                            , 
                                work_order_sort DESC 


                ) sub
                RIGHT JOIN (select count(*) from cte) c(total_rows) on true
                WHERE total_rows != 0
                order by cast(pm_no as INTEGER) desc, cast(work_order_no as INTEGER) desc

             '''
            dc={}
            dc['keywords'] = keywords
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['isMine'] = isMine

            items = DbUtil.get_rows(sql, dc)

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

        elif action == 'save':
           #파라미터 전환
            posparam = CommonUtil.snake_to_camel_dict(posparam)
            #작업 결재정보 먼저 등록
            workOrderApprovalPk = handle_work_order_approval(posparam, request)
            tempSave = posparam.get('tempSave', 'N') # 임시저장구분 기본값:  N

            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            workOrderNo = posparam.get('workOrderNo')
            workOrderSort = posparam.get('workOrderSort')
            workTitle = posparam.get('workTitle')
            workText = posparam.get('workText')
            reqInfo = posparam.get('reqInfo')
            woStatusCd = posparam.get('woStatusCd')
            maintTypeCd = posparam.get('maintTypeCd')
            woType = posparam.get('woType')
            wantDt = posparam.get('wantDt')
            planStartDt = wantDt
            planEndDt = wantDt
            startDt =wantDt
            endDt = wantDt
            deptPk = posparam.get('deptPk')
            workChargerPk = posparam.get('workChargerPk')
            pmPk = posparam.get('pmPk')
            apprLine = posparam.get('apprLine')
            apprLineNext = posparam.get('apprLineNext')
            reqDeptPk = posparam.get('reqDeptPk')
            pmReqType = posparam.get('pmReqType')
            workSrcCd = posparam.get('workSrcCd')
            breakdownDt = posparam.get('breakdownDt')
            causeCd = posparam.get('causeCd')
            problemCd = posparam.get('problemCd')
            remedyCd = posparam.get('remedyCd')
            projCd = posparam.get('projCd')
            workSrcCd = posparam.get('workSrcCd')
            totCost = posparam.get('totCost')
            mtrlCost = posparam.get('mtrlCost')
            laborCost = posparam.get('laborCost')
            outsideCost = posparam.get('outsideCost')
            etcCost = posparam.get('etcCost')
            if_send_yn = posparam.get('if_send_yn')       
  
            if workOrderPk ==None:
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
            else:
                wo = CmWorkOrder.objects.get(id=workOrderPk)
                wo.WorkText = workText

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
            wo.WorkSrcCode = workSrcCd
            wo.BreakdownDt = breakdownDt
            wo.CauseCode = causeCd
            wo.ProblemCode = problemCd
            wo.ProjCode = projCd            
            wo.Factory_id = 1
            wo.set_audit(user)
            wo.save()
            print("PK:", wo.id)  # 저장 후 PK가 할당되는지 확인

            if tempSave == 'N':
                handle_work_order_hist(wo.id, posparam, request)

            return {'success': True, 'message': '작업지시 정보가 저장되었습니다.'}

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