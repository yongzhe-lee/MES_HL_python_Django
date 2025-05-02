from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipSpec
#from django.db import transaction

def equip_spec(context):
    '''
    api/kmms/equip_spec    설비사양
    김태영 

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

    try:
        if action == 'findAll':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )

            sql = ''' SELECT t.equip_spec_pk
		       , t.equip_pk, e.equip_cd, e.equip_nm
		       , t.equip_spec_nm, t.equip_spec_unit, t.equip_spec_value
		       , t.insert_ts, t.inserter_id, t.inserter_nm
		       , t.update_ts, t.updater_id, t.updater_nm
		    from cm_equip_spec t
		    inner join cm_equipment e on t.equip_pk = e.equip_pk
		    where t.equip_pk = %(equipPk)s
            '''

            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_row(sql, dc)


        elif action == 'insert':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            equipSpecNm = posparam.get('equipSpecNm')
            equipSpecUnit = posparam.get('equipSpecUnit')
            equipSpecValue = posparam.get('equipSpecValue')

            c = CmEquipSpec()

            c.CmEquipment_id = equipPk
            c.EquipSpecName = equipSpecNm
            c.EquipSpecUnit = equipSpecUnit
            c.EquipSpecValue = equipSpecValue
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비사양 정보가 수정되었습니다.'}


        elif action == 'delete':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            CmEquipSpec.objects.filter(CmEquipment_id=equipPk).delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/equip_spec : action-{}'.format(action)
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