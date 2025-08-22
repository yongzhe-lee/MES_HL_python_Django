from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmTagMeasType, CmTag

def tag_meas_type(context):
    '''
    api/kmms/tag_meas_type    외부업체
    김태영 

    findOne
    findAll
    findTagType
    findDeletableTagMeas
    insert
    update
    countByMeasTypeNmIgnoreCaseAndTagMeasTypePkNot
    countByMeasTypeNmIgnoreCase
    delete
    findTagTypeByEquipPk
    findTagTypeByEquipCd
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableTagMeasType(tagMeasTypePk):
        q = CmTag.objects.filter(CmTagMeasType_id=tagMeasTypePk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action == 'findAll':
            useYn = gparam.get('useYn')
            searchText = gparam.get('searchText')

            sql = ''' select tmt.tag_meas_type_pk
	        , tmt.meas_type_nm, tmt.meas_unit
	        , bc.code_nm as alarm_disp_type_nm
	        , bc.code_cd as alarm_disp_type_cd
	        , tmt.disp_order, tmt.use_yn
	        from cm_tag_meas_type tmt
	        inner join cm_base_code bc on bc.code_grp_cd = 'ALARM_DISP_TYPE' 
	        and bc.code_cd = tmt.alarm_disp_type
		    where 1=1
            '''
            # -- AND t.factory_pk = %(factory_id)s
            if useYn:
                sql += ''' and tmt.use_yn = %(useYn)s
                '''
            if searchText:
                sql += ''' AND ( UPPER(tmt.meas_type_nm) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''

            sql += ''' order by tmt.meas_type_nm
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['searchText'] = searchText

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            tagMeasTypePk = CommonUtil.try_int( gparam.get('tagMeasTypePk') )

            sql = ''' select tmt.tag_meas_type_pk
	        , tmt.meas_type_nm, tmt.meas_unit
	        , bc.code_nm as alarm_disp_type_nm
	        , bc.code_cd as alarm_disp_type_cd
	        , tmt.disp_order, tmt.use_yn
	        from cm_tag_meas_type tmt
	        inner join cm_base_code bc on bc.code_grp_cd = 'ALARM_DISP_TYPE' 
	        and bc.code_cd = tmt.alarm_disp_type
		    where t.tag_meas_type_pk = %(tagMeasTypePk)s
            '''

            dc = {}
            dc['tagMeasTypePk'] = tagMeasTypePk

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            tagMeasTypePk = CommonUtil.try_int(posparam.get('tagMeasTypePk'))
            measTypeNm = posparam.get('measTypeNm')
            measUnit = posparam.get('measUnit')
            dispOrder = posparam.get('dispOrder')
            alarmDispTypeCd = posparam.get('alarmDispTypeCd')
            useYn = posparam.get('useYn')
  
            if action == 'update':
                c = CmTagMeasType.objects.get(id=tagMeasTypePk)

            else:
                c = CmTagMeasType()

            c.MeasTypeName = measTypeNm
            c.MeasUnit = measUnit
            c.DispOrder = dispOrder
            c.AlarmDispType = alarmDispTypeCd
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '외부공급처의 정보가 수정되었습니다.'}


        elif action == 'delete':
            tagMeasTypePk = CommonUtil.try_int(posparam.get('tagMeasTypePk'))
            if not findDeletableTagMeasType(tagMeasTypePk):
                CmTagMeasType.objects.filter(id=tagMeasTypePk).delete()

            items = {'success': True}
    

        elif action == 'findDeletableTagMeasType':
            tagMeasTypePk = CommonUtil.try_int(posparam.get('tagMeasTypePk'))
            return findDeletableTagMeasType(tagMeasTypePk)


        elif action == 'findTagType':
            sql = '''  select tmt.tag_meas_type_pk, tmt.meas_type_nm, tmt.meas_unit
          , bc.code_nm as alarmDispTypeNm, bc.code_cd as alarmDispTypeCd
	        from cm_tag_meas_type tmt
	        inner join cm_base_code bc on bc.code_grp_cd = 'ALARM_DISP_TYPE'
	        and bc.code_cd = tmt.alarm_disp_type
	        where tmt.use_yn='Y'
	        order by tmt.meas_type_nm ASC
            '''
            dc = {}

            items = DbUtil.get_rows(sql, dc)

        elif action == 'countByMeasTypeNmIgnoreCaseAndTagMeasTypePkNot':
            tagMeasTypePk = CommonUtil.try_int(posparam.get('tagMeasTypePk'))
            measTypeNm = posparam.get('measTypeNm')

            sql = ''' select count(*) as cnt
   	        from cm_tag_meas_type
   	        where  meas_type_nm = %(measTypeNm)s
  	        and tag_meas_type_pk != %(tagMeasTypePk)s
            '''
            dc = {}
            dc['measTypeNm'] = measTypeNm
            dc['tagMeasTypePk'] = tagMeasTypePk

            items = DbUtil.get_row(sql, dc)
            return items['cnt']

        elif action == 'countByMeasTypeNmIgnoreCase':
            #tagMeasTypePk = CommonUtil.try_int(posparam.get('tagMeasTypePk'))
            measTypeNm = posparam.get('measTypeNm')

            sql = ''' select count(*) as cnt
   	        from cm_tag_meas_type
   	        where  meas_type_nm = %(measTypeNm)s
            '''
            dc = {}
            dc['measTypeNm'] = measTypeNm

            items = DbUtil.get_row(sql, dc)
            return items['cnt']

        elif action == 'findTagTypeByEquipPk':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))
            sql = '''  select tmt.tag_meas_type_pk
			, tmt.meas_type_nm
			, tmt.meas_unit
			, adt.code_nm as alarm_disp_type_nm
			, adt.code_cd as alarm_disp_type_cd
		    from cm_tag t
		    inner join cm_equipment eq on eq.equip_pk = t.equip_pk
		    inner join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t.tag_meas_type_pk
		    inner join cm_base_code adt on adt.code_cd = tmt.alarm_disp_type 
		    and adt.code_grp_cd = 'ALARM_DISP_TYPE'
		    where t.use_yn = 'Y'
		    and eq.equip_pk = %(equipPk)s
		    group by tmt.tag_meas_type_pk
		    , tmt.meas_type_nm, tmt.meas_unit
		    , adt.code_nm, adt.code_cd
		    order by tmt.meas_type_nm
            '''
            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'findTagTypeByEquipCd':
            equipCd = posparam.get('equipCd')
            sql = '''  select tmt.tag_meas_type_pk
			, tmt.meas_type_nm
			, tmt.meas_unit
			, adt.code_nm as alarm_disp_type_nm
			, adt.code_cd as alarm_disp_type_cd
		    from cm_tag t
		    inner join cm_equipment eq on eq.equip_pk = t.equip_pk
		    inner join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t.tag_meas_type_pk
		    inner join cm_base_code adt on adt.code_cd = tmt.alarm_disp_type 
		    and adt.code_grp_cd = 'ALARM_DISP_TYPE'
		    where t.use_yn = 'Y'
		    and eq.equip_cd = %(equipCd)s

		    group by tmt.tag_meas_type_pk
		    , tmt.meas_type_nm, tmt.meas_unit
		    , adt.code_nm, adt.code_cd
		    order by tmt.meas_type_nm
            '''
            # -- and eq.factory_pk = %(factory_pk)s
            dc = {}
            dc['equipCd'] = equipCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = 'kmms/tag_meas_type : action-{}'.format(action)
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