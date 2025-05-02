from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipChkItemRslt, CmWorkOrder

def equip_chk_item_rslt(context):
    '''
    api/kmms/equip_chk_item_rslt    설비점검항목결과
    김태영 

    selectEquipInfo
    selectEquipChkItemRslt
    equipChkItemRsltSummary
    insert
    insertUpdate
    insertUpdate2
    delete
    deleteByChkSche
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'selectEquipInfo':
            chkRsltPk = gparam.get('chkRsltPk')

            sql = ''' select t.chk_rslt_pk
		    , t.equip_pk, e.equip_nm, e.equip_cd
		    , t.chk_rslt
		    , wo.work_order_pk, wo.work_order_no
		    , case when e.disposed_date is not null then 'Y' else 'N' end as disable_yn
		    from cm_equip_chk_rslt t
		    inner join cm_equipment e on e.equip_pk = t.equip_pk
		    left join cm_work_order wo on wo.chk_rslt_pk = t.chk_rslt_pk
		    where t.chk_rslt_pk = %(chkRsltPk)s
            '''

            dc = {}
            dc['chkRsltPk'] = chkRsltPk

            items = DbUtil.get_rows(sql, dc)
 
        if action == 'selectEquipChkItemRslt':
            chkRsltPk = gparam.get('chkRsltPk')

            sql = ''' SELECT t1.chk_rslt_pk
		       , t4.chk_item_pk, t3.chk_sche_pk
		       , t4.item_idx, t4.chk_item_nm
		       , t4.lcl, t4.ucl
		       , Max(Coalesce(t6.chk_item_rslt, '')) AS chk_item_rslt
		     --  , Max(t6.chk_item_rslt_num) AS chk_item_rslt_num
		       , Max(Coalesce(t6.chk_item_rslt, '')) AS chk_item_rslt_save_data
		       , Max(t6.chk_item_rslt_desc) AS chk_item_rslt_desc
		       , Max(fn_user_nm(t7."Name", 'N')) AS chk_user_nm
		       , Max(t6.chk_dt) AS chk_dt
		       , t8.code_pk	AS chk_item_unit_pk, t8.code_nm	AS chk_item_unit_nm
		    FROM cm_equip_chk_rslt t1
		    inner join cm_equipment t2 on t2.equip_pk = t1.equip_pk
		    inner join cm_equip_chk_sche t3 on t3.chk_sche_pk = t1.chk_sche_pk
		    inner join cm_equip_chk_item_mst t4 on t4.chk_sche_pk = t3.chk_sche_pk
		    left join cm_equip_chk_item_rslt t6 on t6.chk_rslt_pk = t1.chk_rslt_pk 
		    and t6.chk_item_pk = t4.chk_item_pk
		    left join user_profile t7 on t7."user_id"  = t6.chk_user_pk
		    left join cm_base_code t8 on t8.code_pk = t4.chk_item_unit_pk
		    WHERE  t1.chk_rslt_pk = %(chkRsltPk)s
		    GROUP  BY t1.chk_rslt_pk, t4.chk_item_pk, t3.chk_sche_pk
		    , t4.item_idx, t4.chk_item_nm, t4.lcl, t4.ucl
		    , t8.code_pk, t8.code_nm
		    ORDER  BY t1.chk_rslt_pk, t4.item_idx
            '''

            dc = {}
            dc['chkRsltPk'] = chkRsltPk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'equipChkItemRsltSummary':
            chkRsltPk = CommonUtil.try_int( gparam.get('chkRsltPk') )

            sql = ''' select count(*) as tot_count
		    , coalesce(sum(case when t.chk_item_rslt = 'N' then 1 else 0 end), 0) as normal_count
		    , coalesce(sum(case when t.chk_item_rslt = 'A' then 1 else 0 end), 0) as ab_normal_count
		    , coalesce(sum(case when t.chk_item_rslt = 'C' then 1 else 0 end), 0) as unable_check_count
		    , coalesce(sum(case when coalesce(t.chk_item_rslt, '')  = '' then 1 else 0 end), 0) as null_count
		    from cm_equip_chk_item_rslt t
		    where t.chk_rslt_pk = %(chkRsltPk)s
            '''

            dc = {}
            dc['chkRsltPk'] = chkRsltPk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'insert':
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            chkItemPk = CommonUtil.try_int(posparam.get('chkItemPk'))
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkItemRslt = posparam.get('chkItemRslt')
            chkItemRsltDesc = posparam.get('chkItemRsltDesc')
            chkItemRsltNum = posparam.get('chkItemRsltNum')
            c = CmEquipChkItemRslt()

            c.CmEquipChkRslt_id = chkRsltPk
            c.CmEquipChkItem_id = chkItemPk
            c.CmEquipChkSche_id = chkSchePk
            c.ChkItemRslt = chkItemRslt
            c.ChkItemRsltDesc = chkItemRsltDesc
            c.ChkItemRsltNum = chkItemRsltNum

            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비점검항목결과가 등록되었습니다.'}

        elif action == 'insertUpdate':
            ''' 사용 안 하는듯
            '''
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            chkItemPk = CommonUtil.try_int(posparam.get('chkItemPk'))
            #chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkItemRslt = posparam.get('chkItemRslt')
            chkItemRsltDesc = posparam.get('chkItemRsltDesc')
            chkItemRsltNum = posparam.get('chkItemRsltNum')
            
            sql = ''' 		CALL cm_prc_equip_item_rslt_upsert(
			%(chkItemPk)s, %(chkItemRslt)s, %(chkItemRsltDesc)s
			, %(chkUserPk)s, %(chkItemRsltNum)s
			, %(chkRsltPk)s, %(chkSchePk)s
		    )
            '''
            dc = {}
            dc['chkItemPk'] = chkItemPk
            dc['chkItemRslt'] = chkItemRslt
            dc['chkItemRsltDesc'] = chkItemRsltDesc
            dc['chkUserPk'] = user.id
            dc['chkItemRsltNum'] = chkItemRsltNum
            dc['chkRsltPk'] = chkRsltPk
            dc['chkSchePk'] = chkSchePk
            ret = DbUtil.execute(sql, dc)

            return {'success': True, 'message': '설비점검항목결과가 등록되었습니다.'}

        elif action == 'insertUpdate2':
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            chkItemPk = CommonUtil.try_int(posparam.get('chkItemPk'))
            #chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            chkItemRslt = posparam.get('chkItemRslt')
            chkItemRsltDesc = posparam.get('chkItemRsltDesc')
            chkItemRsltNum = posparam.get('chkItemRsltNum')
            
            q = CmWorkOrder.objects.filter(ChkRsltPk=chkRsltPk)
            if not q.first():
                return {'success': False, 'message': '.'} 

            q = CmEquipChkItemRslt.objects.filter(CmEquipChkRslt_id=chkRsltPk)
            q = q.filter(CmEquipChkItem_id=chkItemPk)
            cir = q.first()
            if not cir:
                cir = CmEquipChkItemRslt()
                cir.CmEquipChkRslt_id = chkRsltPk
                cir.CmEquipChkItem_id = chkItemPk

            cir.ChkItemRslt = CommonUtil.blank_to_none( chkItemRslt )
            cir.ChkItemRsltDesc = CommonUtil.blank_to_none(chkItemRsltDesc )
            cir.ChkItemRsltNum = CommonUtil.try_float( chkItemRsltNum )
            cir.set_audit(user)
            cir.save()

            return {'success': True, 'message': '설비점검항목결과가 저장되었습니다.'}


        elif action == 'delete':
            chkRsltPk = CommonUtil.try_int(posparam.get('chkRsltPk'))
            q = CmEquipChkItemRslt.objects.filter(CmEquipChkMaster_id=chkRsltPk)
            q.delete()

            items = {'success': True}
    

        elif action == 'deleteByChkSche':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))
            q = CmEquipChkItemRslt.objects.filter(CmEquipChkSche_id=chkSchePk)
            q.delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/equip_chk_item_rslt : action-{}'.format(action)
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