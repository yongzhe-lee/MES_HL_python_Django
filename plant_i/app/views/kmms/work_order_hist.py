from django import db
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWorkOrderHist

def work_order_hist(context):
    '''
    api/kmms/work_order_hist    작업지시 이력 정보
    김태영 

    save
    selectWorkOrderHists
    getRecentAfterStatus
    delete
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'selectWorkOrderHists':

            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))

            sql = ''' select woh.work_order_hist_pk
			, woh.work_order_pk
			, wo.work_order_no
			, wo.work_title
			, woh.before_status as before_status_cd
			, bws.code_nm as before_status_nm
			, woh.after_status as after_status_cd
			, aws.code_nm as after_status_nm
			, to_char(woh.change_ts, 'yyyy-MM-dd') as change_ts
			, woh.changer_pk
			, coalesce(woh.changer_nm, cm_fn_user_nm(cu."user_nm", 'N')) as changer_nm
			, woh.change_reason
		    from cm_work_order_hist woh
	            inner join cm_base_code bws on woh.before_status = bws.code_cd and bws.code_grp_cd = 'WO_STATUS'
	            inner join cm_base_code aws on aws.code_cd  = woh.after_status and aws.code_grp_cd = 'WO_STATUS'
	            inner join cm_user_info cu on woh.changer_pk = cu.user_pk
	            inner join cm_work_order wo on wo.work_order_pk = woh.work_order_pk 
		    where woh.work_order_pk = %(workOrderPk)s
		    order by woh.change_ts desc, woh.work_order_hist_pk desc
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getRecentAfterStatus':
            workOrderPk = CommonUtil.try_int(gparam.get('workOrderPk'))

            sql = ''' SELECT after_status
		    FROM  cm_work_order_hist
		    WHERE  work_order_pk = %(workOrderPk)s
		    ORDER  BY work_order_hist_pk DESC
		    LIMIT  1
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_row(sql, dc)


        elif action == 'save':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            changerPk = CommonUtil.try_int(posparam.get('changerPk'))
            beforeStatusCd = posparam.get('beforeStatusCd')
            afterStatusCd = posparam.get('afterStatusCd')            
            changerNm = posparam.get('changerNm')
            changeReason = posparam.get('changeReason')            
 
            c = CmWorkOrderHist()

            c.CmWorkOrder_id = workOrderPk
            c.BeforeStatus = beforeStatusCd
            c.AfterStatus = afterStatusCd
            c.ChangeTs = DateUtil.get_current_datetime()
            c.ChangerPk = changerPk
            c.ChangerName = changerNm
            c.ChangeReason = changeReason
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': ''}


        elif action == 'delete':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            CmWorkOrderHist.objects.filter(CmWorkOrder_id=workOrderPk).delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/work_order_hist : action-{}'.format(action)
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