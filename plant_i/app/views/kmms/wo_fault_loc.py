from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWoFaultLoc

def wo_fault_loc(context):
    '''
    api/kmms/wo_fault_loc    작업지시 고장위치
    김태영 작업중

    findAll 전체목록조회
    findOne 없음
    countBy 
    insert
    update 없음
    delete
    deleteByWorkOrder
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            workOrderPk = gparam.get('workOrderPk')

            sql = ''' select t.work_order_pk
            , t.fault_loc_cd
            , fl.reliab_nm as fault_loc_nm
            , t.fault_loc_desc
            , t.cause_cd
            , woc.reliab_nm as cause_nm
            , t.insert_dt
            , t.inserter_id
            , ui."Name" as inserter_nm
            from cm_wo_fault_loc t
            left join cm_reliab_codes fl on t.fault_loc_cd  = fl.reliab_cd 
            AND fl."types" = 'FC' 
            and fl.factory_pk = %(factory_pk)s
            left join cm_reliab_codes woc on t.cause_cd  = woc.reliab_cd 
            AND woc."types" = 'CC' 
            and woc.factory_pk = %(factory_pk)s
            left join user_profile ui on t.inserter_id = ui."User_id"::text
            WHERE t.work_order_pk = %(workOrderPk)s
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
 
        elif action == 'countBy':
            workOrderPk = gparam.get('workOrderPk')
            faultLocCd = gparam.get('faultLocCd')

            sql = ''' select count(*) as cnt
            from cm_wo_fault_loc t
            left join reliab_codes fl on t.fault_loc_cd  = fl.reliab_cd 
            AND fl."types" = 'FC' 
            and fl.factory_pk = %(factory_pk)s
            left join reliab_codes woc on t.cause_cd  = woc.reliab_cd 
            AND woc."types" = 'CC' 
            and woc.factory_pk = %(factory_pk)s
            WHERE t.work_order_pk = %(workOrderPk)s
            '''
            if faultLocCd:
                sql += ''' and t.fault_loc_cd = %(faultLocCd)s
                '''

            dc = {}
            dc['workOrderPk'] = workOrderPk
            dc['faultLocCd'] = faultLocCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)


        elif action == 'insert':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            faultLocCd = posparam.get('faultLocCd')
            faultLocDesc = posparam.get('faultLocDesc')
            causeCd = posparam.get('causeCd')
  
            q = CmWoFaultLoc.objects.filter(CmWorkOrder_id=workOrderPk)
            q = q.filter(FaultLocCode=faultLocCd)
            if not q.first():
                c = CmWoFaultLoc()
                c.CmWorkOrder_id = workOrderPk
                c.FaultLocCode = faultLocCd
                c.FaultLocDesc = faultLocDesc
                c.CauseCode = causeCd
                c.set_audit(user)
                c.save()

            return {'success': True, 'message': '작업지시 고장위치 정보가 수정되었습니다.'}


        elif action == 'delete':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            exFaultLocCds = posparam.get('exFaultLocCds')
            exFaultLocCd_list = exFaultLocCds.split(',')
            faultLocCd = posparam.get('faultLocCd')
            q = CmWoFaultLoc.objects.filter(CmWorkOrder_id=workOrderPk)
            if faultLocCd:
                q = q.filter(FaultLocCode=faultLocCd)
            if len(exFaultLocCd_list) > 0:
                q = q.exclude(FaultLocCode__in=exFaultLocCd_list)
            q.delete()

            items = {'success': True}
    

        elif action == 'deleteByWorkOrder':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWoFaultLoc.objects.filter(CmWorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/wo_fault_loc : action-{}'.format(action)
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