from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWoLabor
from symbol import factor
#from django.db import transaction

def wo_labor(context):
    '''
    api/kmms/wo_labor    작업지시 인력
    김태영 작업중

    findAll 전체목록조회
    insertBatch
    delete
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
			, wo.work_order_no
			, wo.work_title
			, t.job_class_pk
			, jc.job_class_nm
			, coalesce(t.labor_price, (case when coalesce(t.emp_pk, 0) = 0 
                                        then jc.wage_cost else ujc.wage_cost end)) as wage_cost
			, t.emp_pk as user_pk
			, cm_fn_user_nm(ui."Name", 'N') as user_nm
			, ui."Name" as dept_nm
			, t.work_hr
			, t.real_work_hr
			, t.labor_dsc
			, t.labor_price
			, t.worker_nos
		    from cm_wo_labor t
		    inner join cm_work_order wo on t.work_order_pk = wo.work_order_pk
		    left join cm_job_class jc on t.job_class_pk = jc.job_class_pk
		    left join user_profile ui on t.emp_pk = ui."User_id"
		    left join dept d on d.id = ui."Depart_id" 
		    left join cm_job_class ujc on ujc.job_class_pk = ui.job_class_pk
		    WHERE 1 = 1
		    AND t.work_order_pk = %(workOrderPk)s
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'insertBatch':
            Q = posparam.get('Q')

            for item in Q:
                c = CmWoLabor()
                c.CmWorkOrder_id = item['workOrderPk']
                c.EmpPk = item['userPk']
                c.CmJobClass_id = item['jobClassPk']
                #c.LaborPrice = item['laborPrice']
                c.WorkerNos = item['workerNos']
                c.WorkHr = item['workHr']
                c.RealWorkHr = item['realWorkHr']
                c.LaborDsc = item['laborDsc']
                c.set_audit(user)
                c.save()

            return {'success': True, 'message': '작업지시 인력 데이터가 등록되었습니다.'}


        elif action == 'delete':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWoLabor.objects.filter(CmWorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/wo_labor : action-{}'.format(action)
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