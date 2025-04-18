from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWorkOrderSupplier

def work_order_supplier(context):
    '''
    api/kmms/work_order_supplier    작업지시 외부업체
    김태영 작업중

    countBy
    findAll
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

            sql = ''' select wos.work_order_pk
		    , wos.ex_supplier_pk
		    , wos.cost
		    , es.ex_supplier_cd
		    , es.ex_supplier_nm
		    , wo.work_order_no
		    , wo.work_title
		    from cm_work_order_supplier wos
		    inner join cm_work_order wo on wos.work_order_pk = wo.work_order_pk
		    inner join cm_ex_supplier es on wos.ex_supplier_pk = es.ex_supplier_pk
		    where wos.work_order_pk = %(workOrderPk)s
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_rows(sql, dc)
 
        elif action == 'countBy':
            exSupplierPk = gparam.get('exSupplierPk')
            exSupplierPk = CommonUtil.try_int(exSupplierPk)

            sql = ''' select count(*) as cnt
            from cm_work_order_supplier wos
            inner join cm_work_order wo on wos.work_order_pk = wo.work_order_pk
            where wos.ex_supplier_pk = %(exSupplierPk)s
            and wo.factory_pk = %(factory_pk)s
            '''
            dc = {}
            dc['exSupplierPk'] = exSupplierPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'insertBatch':
            Q = posparam.get('Q')

            for item in Q:
                c = CmWorkOrderSupplier()
                c.CmWorkOrder_id = item['workOrderPk']
                c.CmExSupplier_id = item['exSupplierPk']
                c.Cost = item['cost']
                c.set_audit(user)
                c.save()

            return {'success': True, 'message': '작업지시 외부업체 데이터가 등록되었습니다.'}


        elif action == 'delete':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWorkOrderSupplier.objects.filter(CmWorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/work_order_supplier : action-{}'.format(action)
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