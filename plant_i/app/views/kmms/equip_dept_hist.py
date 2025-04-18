from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipDeptHist

def equip_dept_hist(context):
    '''
    api/kmms/equip_dept_hist    설비관리부서 변경이력?
    김태영 작업중

    findAll
    delete
    insert
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableExSupplier(exSupplierPk):
        q = CmWorkOrderSupplier.objects.filter(CmExSupplier_id=exSupplierPk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action == 'findAll':
            equipPk = gparam.get('equipPk')

            sql = ''' SELECT t.equip_dept_hist_pk
		       , t.equip_pk
		       , e.equip_cd
		       , e.equip_nm
		       , t.equip_dept_bef
		       , t.equip_dept_aft
		       , t.insert_ts
		       , t.inserter_id
		       , t.inserter_nm
		    from cm_equip_dept_hist t
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    where t.equip_pk = %(equipPk)s
            order by e.equip_nm
            '''

            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 


        elif action == 'insert':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            equipDeptBef = posparam.get('equipDeptBef')
            equipDeptAft = posparam.get('equipDeptAft')

            c = CmEquipDeptHist()

            c.CmEquipment_id = equipPk
            c.EquipDeptBefore = equipDeptBef
            c.EquipDeptAfter = equipDeptAft
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비관리부서 변경이력 데이터가 등록되었습니다.'}


        elif action == 'delete':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            q  = CmEquipDeptHist.objects.filter(CmEquipment_id=equipPk)
            q.delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/equip_dept_hist : action-{}'.format(action)
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