from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmChkEquip

def chk_equip(context):
    '''
    api/kmms/chk_equip    점검대상설비
    김태영 

    findAll
    insertBatch
    insert
    deleteByChkMastPk
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
            chkMastPk = CommonUtil.try_int( gparam.get('chkMastPk') )

            sql = ''' select t.chk_mast_pk, ecm.chk_mast_no
			, e.equip_pk, e.equip_cd, e.equip_nm
			, l.loc_pk, l.loc_cd, l.loc_nm
			, ec.equip_category_id, ec.equip_category_desc
			, e.equip_class_path, e.equip_class_desc
			, es.code_nm as equip_status_nm
			, e.equip_dsc
			, e.import_rank_pk, ir.import_rank_cd
		    from cm_chk_equip t
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = t.chk_mast_pk
		    inner join cm_equipment e on e.equip_pk = t.equip_pk
		    left join cm_location l on l.loc_pk = e.loc_pk
		    left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
		    left join cm_base_code es on es.code_cd = e.equip_status
		    and es.code_grp_cd = 'EQUIP_STATUS'
		    left join cm_import_rank ir on ir.import_rank_pk = e.import_rank_pk
		    WHERE t.chk_mast_pk  = %(chkMastPk)s
            '''
          
            dc = {}
            dc['chkMastPk'] = chkMastPk

            items = DbUtil.get_rows(sql, dc)


        elif action == 'insertBatch':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            chkEquips =posparam.get('chkEquips')

            chkEquip_list = chkEquips.split(',')

            for item in chkEquip_list:
                equip_pk = CommonUtil.try_int(item)
                c = CmChkEquip()

                c.CmEquipChkMaster_id = chkMastPk
                c.CmEquipment_id = equip_pk
                #c.set_audit(user)
                c.save()

            return {'success': True, 'message': '점검대상설비 정보가 등록되었습니다.'}

        elif action == 'insert':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))

            c = CmChkEquip()

            c.CmEquipChkMaster_id = chkMastPk
            c.CmEquipment_id = equipPk
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '점검대상설비 정보가 등록되었습니다.'}

        elif action == 'deleteByChkMastPk':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            CmChkEquip.objects.filter(CmEquipChkMaster_id=chkMastPk).delete()

            items = {'success': True}
    
        elif action == 'delete':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            q = CmChkEquip.objects.filter(CmEquipChkMaster_id=chkMastPk)
            q = q.filter(CmEquipment_id=equipPk)
            q.delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/chk_equip : action-{}'.format(action)
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