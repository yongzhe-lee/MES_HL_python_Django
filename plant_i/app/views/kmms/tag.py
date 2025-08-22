from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmTag, CmEquipment

def tag(context):
    '''
    api/kmms/tag    외부업체
    김태영 

    findOne
    findAll
    insert
    update
    countByTagIgnoreCase
    countByTagIgnoreCaseAndTagPkNot
    searchChartGrpByEquip
    searchChartGrpByEquipCode
    delete
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['findAll', 'countBy']:
            tagMeasTypePk = CommonUtil.try_int( gparam.get('tagMeasTypePk') )
            locPk = CommonUtil.try_int( gparam.get('locPk') )
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            useYn = gparam.get('useYn')
            locCd = gparam.get('locCd')
            equipCd = gparam.get('equipCd')
            searchText = gparam.get('searchText')

            sql = ''' SELECT t.tag_pk, t.tag, t.tag_desc
	       ,lc.loc_pk, lc.loc_cd, lc.loc_nm
	       ,eq.equip_pk, eq.equip_cd, eq.equip_nm
	       ,tmt.tag_meas_type_pk, tmt.meas_type_nm as tag_meas_type_nm, tmt.meas_unit as tag_meas_unit
	       ,t.meas_point
	       ,bc2.code_cd as src_system, bc2.code_nm as src_system_nm
	       ,t.src_tag
	       ,bc3.code_cd as meas_sensor, bc3.code_nm as meas_sensor_nm
	       ,t.alarm_trouble
	       ,t.warn_low, t.warn_high, t.danger_low, t.danger_high
	       ,t.dec_place, t.disp_order
	       ,bc.code_nm, bc.code_cd as alarm_disp_type_cd
	       ,t.alarm_chk_yn
	       ,t.use_yn
	       ,t.inserter_nm, t.insert_ts, t.updater_nm, t.update_ts
	       ,t.src_ip_addr
	        FROM cm_tag t
	        INNER JOIN cm_equipment eq ON eq.equip_pk = t.equip_pk
	        INNER JOIN cm_location lc ON lc.loc_pk = eq.loc_pk
	        INNER JOIN cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t.tag_meas_type_pk
	        INNER JOIN cm_base_code bc on bc.code_grp_cd = 'ALARM_DISP_TYPE'
	        AND bc.code_cd = tmt.alarm_disp_type
	        INNER JOIN cm_base_code bc2 ON bc2.code_grp_cd = 'SRC_SYSTEM' 
	        AND bc2.code_cd = t.src_system
	        INNER JOIN cm_base_code bc3 on bc3.code_grp_cd = 'MEAS_SENSOR'
	        AND bc3.code_cd = t.meas_sensor
            
            where 1 = 1
            '''
            # -- where eq.factory_pk = %(factory_pk)s
            if searchText:
                sql += ''' AND ( UPPER(t.tag) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
                or UPPER(t.tag_desc) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
   			    )
                '''
            if useYn:
                sql += ''' and t.use_yn = %(useYn)s
                    '''
            if tagMeasTypePk:
                sql += ''' AND tmt.tag_meas_type_pk = = %(tagMeasTypePk)s                
                '''            
            if locPk > 0:
                sql += ''' AND ( lc.loc_pk = %(locPk)s
					OR lc.loc_pk IN ( select loc_pk from (select * 
                                from cm_fn_get_loc_path(%(factory_pk)s)) x 
                                where %(locPk)s = path_info_pk)
				)
                '''
            if equipPk > 0:
                sql += ''' AND eq.equip_pk = = %(equipPk)s                
                '''  
            if locCd:
                sql += ''' 	AND ( lc.loc_cd = %(locCd)s
					OR lc.loc_cd IN ( select loc_cd from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x 
                        where %(locCd)s = path_info_cd 

                        )
				)
                '''
                        # -- and factory_pk = %(factory_pk)s)
            if equipCd:
                sql += ''' AND eq.equip_cd = = %(equipCd)s                
                '''  

            dc = {}
            dc['useYn'] = useYn
            dc['tagMeasTypePk'] = tagMeasTypePk
            dc['locPk'] = locPk
            dc['equipPk'] = equipPk
            dc['searchText'] = searchText
            dc['locCd'] = locCd
            dc['equipCd'] = equipCd

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            tagPk = CommonUtil.try_int( gparam.get('tagPk') )

            sql = ''' SELECT t.tag_pk, t.tag, t.tag_desc
	       ,lc.loc_pk, lc.loc_cd, lc.loc_nm
	       ,eq.equip_pk, eq.equip_cd, eq.equip_nm
	       ,tmt.tag_meas_type_pk, tmt.meas_type_nm as tag_meas_type_nm, tmt.meas_unit as tag_meas_unit
	       ,t.meas_point
	       ,bc2.code_cd as src_system, bc2.code_nm as src_system_nm
	       ,t.src_tag
	       ,bc3.code_cd as meas_sensor, bc3.code_nm as meas_sensor_nm
	       ,t.alarm_trouble
	       ,t.warn_low, t.warn_high, t.danger_low, t.danger_high
	       ,t.dec_place, t.disp_order
	       ,bc.code_nm, bc.code_cd as alarm_disp_type_cd
	       ,t.alarm_chk_yn
	       ,t.use_yn
	       ,t.inserter_nm, t.insert_ts, t.updater_nm, t.update_ts
	       ,t.src_ip_addr
	        FROM cm_tag t
	        INNER JOIN cm_equipment eq ON eq.equip_pk = t.equip_pk
	        INNER JOIN cm_location lc ON lc.loc_pk = eq.loc_pk
	        INNER JOIN cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t.tag_meas_type_pk
	        INNER JOIN cm_base_code bc on bc.code_grp_cd = 'ALARM_DISP_TYPE'
	        AND bc.code_cd = tmt.alarm_disp_type
	        INNER JOIN cm_base_code bc2 ON bc2.code_grp_cd = 'SRC_SYSTEM' 
	        AND bc2.code_cd = t.src_system
	        INNER JOIN cm_base_code bc3 on bc3.code_grp_cd = 'MEAS_SENSOR'
	        AND bc3.code_cd = t.meas_sensor
	        where t.tag_pk = %(tagPk)s
            '''

            dc = {}
            dc['tagPk'] = tagPk

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            tagPk = CommonUtil.try_int(posparam.get('tagPk'))
            equipCd = posparam.get('equipCd')
            tag = posparam.get('tag')
            tagDesc = posparam.get('tagDesc')
            tagMeasTypePk = posparam.get('tagMeasTypePk')
            measPoint = posparam.get('measPoint')
            srcSystem = posparam.get('srcSystem')
            srcTag = posparam.get('srcTag')
            srcIpAddr = posparam.get('srcIpAddr')
            warnLow = posparam.get('warnLow')
            warnHigh = posparam.get('warnHigh')
            dangerLow = posparam.get('dangerLow')
            dangerHigh = posparam.get('dangerHigh')
            decPlace = posparam.get('decPlace')
            measSensor = posparam.get('measSensor')
            alarmChkYn = posparam.get('alarmChkYn')
            dispOrder = posparam.get('dispOrder')
            useYn = posparam.get('useYn')
  
            q = CmEquipment.objects.filter(EquipCode=equipCd)
            equip = q.first()

            if action == 'update':
                c = CmTag.objects.get(id=tagPk)
            else:
                c = CmTag()

            c.Tag = tag
            c.CmEquipment = equip
            c.TagDesc = tagDesc
            c.CmTagMeasType_id = tagMeasTypePk
            c.MeasPoint = measPoint
            c.SrcSystem = srcSystem
            c.SrcTag = srcTag
            c.SrcIpAddr = srcIpAddr
            c.WarnLow = warnLow
            c.WarnHigh = warnHigh
            c.DangerLow = dangerLow
            c.DangerHigh = dangerHigh
            c.DecPlace = decPlace
            c.MeasSensor = measSensor
            c.AlarmChkYn = alarmChkYn
            c.DispOrder = dispOrder
            c.UseYn = useYn
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '태그 정보가 수정되었습니다.'}


        elif action == 'delete':
            tagPk = CommonUtil.try_int(posparam.get('tagPk'))
            #if not findDeletableTag(tagPk):
            CmTag.objects.filter(id=tagPk).delete()

            items = {'success': True}
   

        elif action == 'countByTagIgnoreCase':
            tag = gparam.get('tag')
            sql = ''' select count(*) as cnt
   	        from cm_tag
   	        where tag = %(tag)s
            '''
            dc = {}
            dc['tag'] = tag

            items = DbUtil.get_row(sql, dc)
            return items['cnt']


        elif action == 'countByTagIgnoreCaseAndTagPkNot':
            tag = gparam.get('tag')
            tagPk = CommonUtil.try_int(posparam.get('tagPk'))

            sql = ''' select count(*) as cnt
   	        from cm_tag
   	        where tag = %(tag)s
            and tag_pk != %(tagPk)s
            '''
            dc = {}
            dc['tag'] = tag
            dc['tagPk'] = tagPk

            items = DbUtil.get_row(sql, dc)
            return items['cnt']

        elif action == 'searchChartGrpByEquip':
            equipPk = CommonUtil.try_int(posparam.get('equipPk'))

            sql = ''' select t.chart_grp_cd
   	        from cm_tag t
   	        WHERE t.equip_pk = %(equipPk)s
   	        and t.chart_grp_cd is not null
   	        group by t.chart_grp_cd order by t.chart_grp_cd
            '''
            dc = {}
            dc['equipPk'] = equipPk

            items = DbUtil.get_rows(sql, dc)


        elif action == 'searchChartGrpByEquipCode':
            equipCd = gparam.get('equipCd')

            sql = ''' select t.chart_grp_cd
   	        from cm_tag t
   	        inner join cm_equipment eq on eq.equip_pk = t.equip_pk
   	        WHERE eq.equip_cd = %(equipCd)s

   	        and t.chart_grp_cd is not null
   	        group by t.chart_grp_cd order by t.chart_grp_cd
            '''
            # -- AND eq.factory_pk = %(factory_pk)s
            dc = {}
            dc['equipCd'] = equipCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = 'kmms/tag : action-{}'.format(action)
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