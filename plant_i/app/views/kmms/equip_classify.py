from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmBaseCodeGroup

def equip_classify(context):
    '''
    api/kmms/equip_classify    설비종류
    김태영 작업중

    getEquipClassifyList
    getEquipClassifyTree
    findClassifyTree
    getComboEquipClassity
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'getEquipClassifyList':
            useYn = gparam.get('useYn')

            sql = ''' SELECT t.equip_class_pk
			, t.equip_class_id
			, t.equip_class_desc
			, t.hierarchy_path
			, t.category_id
			, t.parent_id
			, t.class_type
			, t.factory_pk as site_id
			, t.use_yn
			, t.insert_ts
			, t.inserter_id
			, iu."Name"  as inserter_nm
			, t.update_ts
			, t.updater_id
			, uu."Name" as updater_nm
		    FROM cm_equip_classify t
		    INNER JOIN user_profile iu on iu."User_id"::text  = t.inserter_id
		    LEFT  JOIN user_profile uu on uu."User_id"::text = t.updater_id
		    WHERE t.factory_pk = %(factory_pk)s
		    ORDER BY 2
            '''

            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'getEquipClassifyTree':

            sql = ''' select t.id as cd, t.up_id as up_cd
		    , t.equip_class_id
			, t.equip_class_desc
			, t.parent_id
			, t.equip_class_pk
			, t.up_equip_class_pk
			, t.lvl
			, t.class_type
			, t.hierarchy_path
			, (select count(*)
			     from (select * from cm_fn_get_equip_classify(t.factory_pk) ec
			     where ec.parent_id = t.equip_class_id
		        and ec.class_type = 'TYPES'
		        and ec.site_id = t.site_id
		        and ec.lvl > t.lvl) as sub_count
		    from (select * from cm_fn_get_equip_classify(t.factory_pk)) t
		    WHERE t.factory_pk = %(factory_pk)s
            '''

            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'findClassifyTree':
            categoryId = gparam.get('categoryId')

            if categoryId:
                sql = ''' SELECT T.ID,
		        T.UP_ID,
		        T.EQUIP_CLASS_ID,
		        T.EQUIP_CLASS_DESC,
		        T.PARENT_ID,
		        T.EQUIP_CLASS_PK,
		        T.UP_EQUIP_CLASS_PK,
		        T.HIERARCHY_PATH,
		        T.PATH_INFO,
		        T.LVL,
		        T.CLASS_TYPE,
		        T.SITE_ID,
		        T.CATEGORY_ID,
		        (SELECT COUNT(*)
		            FROM (SELECT * FROM cm_FN_GET_EQUIP_CLASSIFY_CTG(%(factory_pk)s, %(categoryId)s)) EC
		            WHERE EC.PARENT_ID = T.EQUIP_CLASS_ID
		            AND EC.CLASS_TYPE = 'TYPES'
		            AND EC.SITE_ID = T.SITE_ID
		            AND EC.LVL > T.LVL) AS SUB_COUNT
		        FROM cm_FN_GET_EQUIP_CLASSIFY_CTG(%(factory_pk)s, %(categoryId)s) T
		        ORDER BY T.PATH_INFO
                '''
            else:
                sql = ''' SELECT T.ID,
			        T.UP_ID,
			        T.EQUIP_CLASS_ID,
			        T.EQUIP_CLASS_DESC,
			        T.PARENT_ID,
			        T.EQUIP_CLASS_PK,
			        T.UP_EQUIP_CLASS_PK,
			        T.HIERARCHY_PATH,
			        T.PATH_INFO,
			        T.LVL,
			        T.CLASS_TYPE,
			        T.SITE_ID,
			        (SELECT COUNT(*)
			           FROM ( SELECT * FROM CM_FN_GET_EQUIP_CLASSIFY(%(factory_pk)s)) EC
			           WHERE EC.PARENT_ID = T.EQUIP_CLASS_ID
			           AND EC.CLASS_TYPE = 'TYPES'
			           AND EC.SITE_ID = T.SITE_ID
			           AND EC.LVL > T.LVL) AS SUB_COUNT
				FROM CM_FN_GET_EQUIP_CLASSIFY(%(factory_pk)s) T
				ORDER BY T.PATH_INFO
                '''
            dc = {}
            dc['categoryId'] = categoryId
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getComboEquipClassity':
            classType = gparam.get('classType')

            sql = ''' select ec.equip_class_id, ec.equip_class_desc
			from cm_equip_classify ec
			where ec.use_yn = 'Y'
			'''			

			if classType:
				sql += ''' and ec.class_type = %(classType)s'
				'''
			if factory_id:
				sql += ''' and ec.factory_pk = %(factory_pk)s
				'''

            dc = {}
            dc['classType'] = classType
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = 'kmms/equip_classify : action-{}'.format(action)
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