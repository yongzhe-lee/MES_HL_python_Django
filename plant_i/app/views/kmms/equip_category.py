from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmBaseCodeGroup

def equip_category(context):
    '''
    api/kmms/equip_category    설비 카테고리 정보6
    김태영 

    getEquipCategoryList
    getUseEquipCategoryList
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'getEquipCategoryList':            
            keyword = gparam.get('keyword', None)
            useYn = gparam.get('useYn', None)

            sql = ''' SELECT t.equip_category_id
			, t.equip_category_desc
			, t.remark
			, t.use_yn
			, t.insert_ts
			, t.inserter_id
			, iu."Name" as inserter_nm
			, t.update_ts
			, t.updater_id
			, uu."Name"  as updater_nm
		    FROM cm_equip_category t
		    INNER JOIN user_profile iu on iu."User_id" = t.inserter_id
		    LEFT JOIN user_profile uu on uu."User_id"  = t.updater_id
            WHERE 1 = 1          
            '''

            if keyword:
                sql += ''' 
                 (
				          UPPER(t.equip_category_id) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
				    OR UPPER(t.equip_category_desc) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
                    OR UPPER(t.remark) LIKE CONCAT('%%',UPPER(CAST(%(keyword)s as text)),'%%')
                )
                '''

            sql += ''' 
            AND t.use_yn = 'Y'
            ORDER BY t.equip_category_id
            '''

            dc = {}
            dc['keyword'] = keyword
            dc['useYn'] = useYn

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'getUseEquipCategoryList':
            codeGrpCd = gparam.get('codeGrpCd')

            sql = ''' SELECT ec.equip_category_id
		     , ec.equip_category_desc
		     , ec.remark
		    FROM cm_equip_category ec
		    WHERE ec.use_yn = 'Y'
            '''

            dc = {}

            items = DbUtil.get_rows(sql, dc)

 
    except Exception as ex:
        source = 'kmms/equip_category : action-{}'.format(action)
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