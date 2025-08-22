from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmBaseCodeGroup, CmEquipCategory, CmEquipClassify

def equip_classify(context):
	'''
	api/kmms/equip_classify    설비분류 정보
	김태영 => 이용재

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

			WHERE 1 = 1
			ORDER BY 2
			'''

			# -- WHERE t.factory_pk = %(factory_pk)s
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
				and ec.factory_pk = t.factory_pk
				and ec.lvl > t.lvl) as sub_count
			from (select * from cm_fn_get_equip_classify(t.factory_pk)) t
			
			WHERE 1 = 1
			'''

			# -- WHERE t.factory_pk = %(factory_pk)s
			dc = {}
			dc['factory_pk'] = factory_id

			items = DbUtil.get_rows(sql, dc)

		elif action == 'findClassifyTree':
			keyword = gparam.get('keyword')
			categoryId = gparam.get('categoryId')
			factory_pk = 1

			if categoryId:
				sql = ''' 
				SELECT T.ID,
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
				T.CATEGORY_ID,
				(SELECT COUNT(*)
					FROM (SELECT * FROM cm_FN_GET_EQUIP_CLASSIFY_CTG(%(factory_pk)s, %(categoryId)s)) EC
					WHERE EC.PARENT_ID = T.EQUIP_CLASS_ID
					AND EC.CLASS_TYPE = 'TYPES'
					AND EC.factory_pk = T.factory_pk
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
					T.factory_pk,
					(SELECT COUNT(*)
						FROM ( SELECT * FROM CM_FN_GET_EQUIP_CLASSIFY(%(factory_pk)s)) EC
						WHERE EC.PARENT_ID = T.EQUIP_CLASS_ID
						AND EC.CLASS_TYPE = 'TYPES'
						AND EC.factory_pk = T.factory_pk
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
			# if factory_id:
			# 	sql += ''' and ec.factory_pk = %(factory_pk)s
			# 	'''

			dc = {}
			dc['classType'] = classType
			dc['factory_pk'] = factory_id

			items = DbUtil.get_rows(sql, dc)

		elif action in ['findAll']:
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
			'''
			# -- AND t.factory_pk = %(factory_pk)s
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
			
			if classType == 'CLASS':
				try:
					c = CmEquipClassify.objects.get(id=equipClassPk)				
				except CmEquipClassify.DoesNotExist:
					c = CmEquipClassify()      
			elif classType == 'TYPES':
				# 복합 유니크 제약조건을 고려하여 조회
				parent_classify = CmEquipClassify.objects.filter(EquipClassCode=equipClassId, ParentCode=parentId).first()
				if parent_classify:
					c = CmEquipClassify.objects.get(id=equipClassPk)
				else:
					c = CmEquipClassify()

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