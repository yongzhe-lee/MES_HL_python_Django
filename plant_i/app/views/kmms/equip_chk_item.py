from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipChkItem

def equip_chk_item(context):
    '''
    api/kmms/equip_chk_item    설비점검항목
    김태영 

    findAll
    findOne
    searchOne
    deleteUpdateBatch 등록 및 수정전에 삭제된것 삭제처리
    insert
    update
    delete
    deleteByChkMastPk
    getDailyReportChkItem
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            chkMastPk = gparam.get('chkMastPk')

            sql = ''' select t.chk_item_pk
			, ecm.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
			, t.item_idx, t.chk_item_nm
			, t.lcl, t.ucl
			, t.chk_item_unit_pk, ciu.code_nm as chk_item_unit_nm
			, t.method, t.guide
		    from cm_equip_chk_item t
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = t.chk_mast_pk
		    left join cm_base_code ciu on ciu.code_pk = t.chk_item_unit_pk 
		    and ciu.code_grp_cd = 'CHK_ITEM_UNIT'
		    WHERE t.chk_mast_pk  = %(chkMastPk)s
		    order by t.item_idx
            '''

            dc = {}
            dc['chkMastPk'] = chkMastPk

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            chkItemPk = CommonUtil.try_int( gparam.get('chkItemPk') )

            sql = ''' select t.chk_item_pk
			, ecm.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
			, t.item_idx, t.chk_item_nm
			, t.lcl, t.ucl
			, t.chk_item_unit_pk, ciu.code_nm as chk_item_unit_nm
			, t.method, t.guide
		    from cm_equip_chk_item t
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = t.chk_mast_pk
		    left join cm_base_code ciu on ciu.code_pk = t.chk_item_unit_pk 
		    and ciu.code_grp_cd = 'CHK_ITEM_UNIT'
		    WHERE t.chk_item_pk  = %(chkItemPk)s
            '''

            dc = {}
            dc['chkItemPk'] = chkItemPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'searchOne':
            chkItemPk = CommonUtil.try_int( gparam.get('chkItemPk') )
            itemIdx = CommonUtil.try_int( gparam.get('itemIdx') )
            chkMastNo = gparam.get('chkMastNo') 

            sql = ''' select t.chk_item_pk
			, ecm.chk_mast_pk, ecm.chk_mast_no, ecm.chk_mast_nm
			, t.item_idx, t.chk_item_nm
			, t.lcl, t.ucl
			, t.chk_item_unit_pk, ciu.code_nm as chk_item_unit_nm
			, t.method, t.guide
		    from cm_equip_chk_item t
		    inner join cm_equip_chk_mast ecm on ecm.chk_mast_pk = t.chk_mast_pk
		    left join cm_base_code ciu on ciu.code_pk = t.chk_item_unit_pk 
		    and ciu.code_grp_cd = 'CHK_ITEM_UNIT'
		    WHERE ecm.chk_mast_no = %(chkMastNo)s
            AND ecm.factory_pk = %(factory_pk)s
		    AND	t.item_idx = %(itemIdx)s
		    limit 1
            '''

            dc = {}
            dc['chkMastNo'] = chkMastNo
            dc['itemIdx'] = itemIdx
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)


        elif action == 'deleteUpdateBatch':
            ''' 등록 및 수정전에 삭제된것 삭제처리
            '''
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            equipChkItems = posparam.get('equipChkItems')
            pk_list = equipChkItems.split(',')
            q = CmEquipChkItem.objects.filter(CmEquipChkMaster_id=chkMastPk)
            q = q.exclude(id__in=pk_list)
            q.delete()

            items = {'success': True}

        elif action == 'insert':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            chkItemUnitPk = CommonUtil.try_int(posparam.get('chkItemUnitPk'))
            itemIdx = CommonUtil.try_int(posparam.get('itemIdx'))

            chkItemNm = posparam.get('chkItemNm')
            lcl = posparam.get('lcl')
            ucl = posparam.get('ucl')
            method = posparam.get('method')
            guide = posparam.get('guide')
            dailyReportItemCd = posparam.get('dailyReportItemCd')

            c = CmEquipChkItem()

            c.CmEquipChkMaster_id = chkMastPk
            c.ItemIdx = itemIdx
            c.ChkItemName = chkItemNm
            c.Lcl = lcl
            c.Ucl = ucl
            c.ChkItemUnitPk = chkItemUnitPk
            c.Method = method
            c.Guide = guide
            c.DailyReportItemCd = dailyReportItemCd
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비 점검 항목 정보가 등록되었습니다.'}

        elif action == 'update':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            chkItemUnitPk = CommonUtil.try_int(posparam.get('chkItemUnitPk'))
            itemIdx = CommonUtil.try_int(posparam.get('itemIdx'))

            chkItemNm = posparam.get('chkItemNm')
            lcl = posparam.get('lcl')
            ucl = posparam.get('ucl')
            method = posparam.get('method')
            guide = posparam.get('guide')
            dailyReportItemCd = posparam.get('dailyReportItemCd')


            c = CmEquipChkItem.objects.get(id=item['chkItemPk'])

            c.CmEquipChkMaster_id = chkMastPk
            c.ItemIdx = itemIdx
            c.ChkItemName = chkItemNm
            c.Lcl = lcl
            c.Ucl = ucl
            c.ChkItemUnitPk = chkItemUnitPk
            c.Method = method
            c.Guide = guide
            c.DailyReportItemCd = dailyReportItemCd

            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비 점검 항목 정보가 수정되었습니다.'}


        elif action == 'delete':
            chkItemPk = CommonUtil.try_int(posparam.get('chkItemPk'))
            CmEquipChkItem.objects.filter(id=chkItemPk).delete()

            items = {'success': True}
    

        elif action == 'deleteByChkMastPk':
            chkMastPk = CommonUtil.try_int(posparam.get('chkMastPk'))
            q = CmEquipChkItem.objects.filter(CmEquipChkMaster_id=chkMastPk)
            q.delete()

            items = {'success': True}


        elif action == 'getDailyReportChkItem':
            dailyReportType = gparam.get('dailyReportType')

            sql = ''' select ci.report_chk_item_pk
			, ci.item_idx, ci.chk_item_nm
			, ci.lcl, ci.ucl
			, ci.chk_item_unit_pk
			, ci.method, ci.guide
			, ci.insert_ts, ci.inserter_id, ci.inserter_nm
			, ci.update_ts, ci.updater_id, ci.updater_nm
			, ci.daily_report_type_cd
			, ci.report_item_cd
		    from cm_daily_report_chk_item ci
		    where ci.daily_report_type_cd = %(dailyReportType)s
		    order by ci.item_idx
            '''
            dc = {}
            dc['dailyReportType'] = dailyReportType

            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = 'kmms/equip_chk_item : action-{}'.format(action)
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