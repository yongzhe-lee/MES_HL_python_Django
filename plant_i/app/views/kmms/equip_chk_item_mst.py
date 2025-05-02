from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipChkItemMst

def equip_chk_item_mst(context):
    '''
    api/kmms/equip_chk_item_mst    외부업체
    김태영 

    findAll
    deleteByChkSchePk
    insertBatch
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 


    try:
        if action == 'findAll':
            chkSchePk = CommonUtil.try_int( gparam.get('chkSchePk') )
            exSupplierCd = gparam.get('exSupplierCd')
            exSupplierNm = gparam.get('exSupplierNm')
            exSupplierPkNot = gparam.get('exSupplierPkNot')
            searchText = gparam.get('searchText')

            sql = ''' select t.chk_item_pk, t.chk_sche_pk
		    , t.item_idx, t.chk_item_nm
		    , t.lcl, t.ucl
		    , t.chk_item_unit_pk, ciu.code_nm as chk_item_unit_nm
		    from cm_equip_chk_item_mst t
		    left join cm_base_code ciu on ciu.code_pk = t.chk_item_unit_pk 
		    and ciu.code_grp_cd = 'CHK_ITEM_UNIT'
		    WHERE t.chk_sche_pk = %(chkSchePk)s
            '''

            dc = {}
            dc['chkSchePk'] = chkSchePk

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'insertBatch':
            Q = posparam.get('Q')

            for item in Q:
                c = CmEquipChkItemMst()

                c.CmEquipChkItem_id = item['chkItemPk']
                c.CmEquipChkSche_id = item['chkSchePk']
                c.ItemIdx = item['itemIdx']
                c.ChkItemName = item['chkItemNm']
                c.Lcl = item['lcl']
                c.Ucl = item['ucl']
                c.ChkItemUnitPk = item['chkItemUnitPk']
                #c.DailyReportItemCd = item['dailyReportItemCd']

                c.set_audit(user)
                c.save()          

            return {'success': True, 'message': '설비 점검 항목 마스터 정보가 수정되었습니다.'}


        elif action == 'deleteByChkSchePk':
            chkSchePk = CommonUtil.try_int(posparam.get('chkSchePk'))

            q = CmEquipChkItemMst.objects.filter(CmEquipChkSche_id=chkSchePk)
            q.delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/equip_chk_item_mst : action-{}'.format(action)
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