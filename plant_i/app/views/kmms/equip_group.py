from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmEquipCategory, CmEquipClassify

def equip_group(context):
    '''
    api/kmms/equip_group    설비분류
    김태영 

    findAll
    findOne
    classFindAll
    classifyFindOne
    insert
    update
    insertEquipClassify
    updateEquipClassify
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['findAll']:
            showCodeYn = gparam.get('showCodeYn')
            equipCategoryId = gparam.get('equipCategoryId')
            useYn = gparam.get('useYn')
            searchText = gparam.get('searchText')

            sql = ''' SELECT t.equip_category_id
            , concat('[', t.equip_category_id, '] ', t.equip_category_desc) as equip_category_desc
            , t.equip_category_desc
            '''
            sql += ''', t.remark
            , t.use_yn
            , t.insert_ts
            , t.inserter_id
            , t.update_ts
            , t.updater_id
            FROM  cm_equip_category t
            where 1=1
            '''
            if equipCategoryId:
                sql += ''' AND UPPER(t.equip_category_id) = 'ab'
			    AND UPPER(t.equip_category_desc) = 'abc'
                '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                '''
            if searchText:
                sql += ''' AND (
				UPPER(t.equip_category_id) LIKE CONCAT('%%', UPPER(%(searchText)s), '%%')
				OR
				UPPER(t.equip_category_desc) LIKE CONCAT('%%', UPPER(%(searchText)s), '%%')
   			    )
                '''
            sql += ''' order by t.equip_category_id
            '''

            dc = {}
            dc['showCodeYn'] = showCodeYn
            dc['equipCategoryId'] = equipCategoryId
            dc['useYn'] = useYn
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            equipCategoryId = gparam.get('equipCategoryId')
            showCodeYn = gparam.get('showCodeYn')

            sql = ''' SELECT t.equip_category_id
            '''
            if showCodeYn == 'Y':
                sql += ''' , concat('[', t.equip_category_id, '] ', t.equip_category_desc) as equip_category_desc
                , t.equip_category_desc
                '''
            sql += ''', t.remark
            , t.use_yn
            , t.insert_ts
            , t.inserter_id
            , t.update_ts
            , t.updater_id
            FROM  cm_equip_category t
            where t.EquipCategoryCode = %(equipCategoryId)s
            '''

            dc = {}
            dc['equipCategoryId'] = equipCategoryId

            items = DbUtil.get_row(sql, dc)

        elif action == 'classFindAll':
            equipClassPk = gparam.get('equipClassPk')
            types = gparam.get('types')
            useYn = gparam.get('useYn')
            searchText = gparam.get('searchText')

            sql = ''' select distinct t.equip_class_pk
		        ,t.equip_class_id
		        ,t.equip_class_desc
		        ,t.hierarchy_path
		        ,t.category_id
                '''
            if types == 'CLASS':
                sql += ''' , concat(t.category_id,' : ',ec.equip_category_desc) as category
                '''
            elif types == 'TYPES':
                sql += ''' ,concat(t.parent_id, ' : ', ecl.equip_class_desc) as category
                '''
            sql += ''', t.parent_id
		        ,t.class_type
		        ,t.factory_pk as site_id
		        ,t.use_yn
                ,t.insert_ts
                ,t.inserter_id
                ,t.update_ts
                ,t.updater_id
            FROM cm_equip_classify t

            '''
            if types == 'CLASS':
                sql += ''' left join cm_equip_category ec on ec.equip_category_id = t.category_id
                '''
            elif types == 'TYPES':
                sql += ''' left join cm_equip_classify ecl on ecl.class_type ='CLASS' 
                AND ecl.equip_class_id = t.parent_id
                '''
            sql += '''
            where 1=1 
            AND t.factory_pk = %(factory_pk)s
            '''
            if types:
                sql += ''' AND t.class_type = UPPER(%(types)s)
                '''
            if useYn:
                sql += ''' AND t.use_yn = %(useYn)s
                '''
            if searchText:
                sql += ''' AND (
				UPPER(t.equip_class_id) LIKE CONCAT('%%', UPPER(%(searchText)s), '%%')
				OR
				UPPER(t.equip_class_desc) LIKE CONCAT('%%', UPPER(%(searchText)s), '%%')
				)
                '''


            dc = {}
            dc['factory_pk'] = factory_id
            dc['types'] = types
            dc['useYn'] = useYn
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)

        elif action == 'classifyFindOne':
            equipClassPk = gparam.get('equipClassPk')
            types = gparam.get('types')

            sql = ''' select distinct t.equip_class_pk
		  		,t.equip_class_id
		  		,t.equip_class_desc
		  		,t.hierarchy_path
		  		,t.category_id
                '''
            if types == 'CLASS':
                sql += ''' , concat(t.category_id,' : ',ec.equip_category_desc) as category
                '''
            elif types == 'TYPES':
                sql += ''' ,concat(t.parent_id, ' : ', ecl.equip_class_desc) as category
                '''
            sql += ''', t.parent_id,
		  		,t.class_type,
			  	,t.factory_pk as site_id,
		  		,t.use_yn,
                ,t.insert_ts,
                ,t.inserter_id,
                ,t.update_ts,
                ,t.updater_id
            FROM cm_equip_classify t
            where 1=1
            AND t.equip_class_pk =%(equipClassPk)s
            AND t.site_id = %(factory_pk)s
            '''

            dc = {}
            dc['equipClassPk'] = equipClassPk
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action in ['save']:
            equipCategoryId = posparam.get('equip_category_id')
            equipCategoryDesc = posparam.get('equip_category_desc')
            remark = posparam.get('remark')
            useYn = posparam.get('use_yn')
  
            try:
                c = CmEquipCategory.objects.get(EquipCategoryCode=equipCategoryId)
                # 기존 데이터가 있는 경우 수정
            except CmEquipCategory.DoesNotExist:
                # 기존 데이터가 없는 경우 신규 등록
                c = CmEquipCategory()

            c.EquipCategoryCode = equipCategoryId
            c.EquipCategoryDesc = equipCategoryDesc
            c.Remark = remark
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비 카테고리 정보가 수정되었습니다.'}

        elif action in ['insertEquipClassify', 'updateEquipClassify']:
            equipClassPk = CommonUtil.try_int( posparam.get('equip_class_pk') )
            equipClassId = posparam.get('equip_class_id')
            equipClassDesc = posparam.get('equip_class_desc')
            hierarchyPath = posparam.get('hierarchy_path')
            categoryId = posparam.get('category_id')
            parentId = posparam.get('parent_id')
            classType = posparam.get('class_type')
            useYn = posparam.get('use_yn')
  
            try:
               c = CmEquipClassify.objects.get(id=equipClassPk)
            
            except CmEquipClassify.DoesNotExist:
                c = CmEquipClassify()       

            if classType == 'TYPES':
                categoryId = CmEquipClassify.objects.get(EquipClassCode=parentId).CategoryCode

            c.EquipClassCode = equipClassId
            c.EquipClassDesc = equipClassDesc
            c.HierarchyPath = hierarchyPath
            c.CategoryCode = categoryId
            c.ParentCode = parentId
            c.ClassType = classType
            c.UseYn = useYn
            c.Factory_id = factory_id
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '설비분류 정보가 수정되었습니다.'}


    except Exception as ex:
        source = 'kmms/equip_group : action-{}'.format(action)
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