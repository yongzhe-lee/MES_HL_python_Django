from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
#from domain.models.cmms import CmExSupplier, CmWorkOrderSupplier

def monitor(context):
    '''
    api/kmms/monitor    
    김태영 

    selectMonitorEquipByUseYnWithCode
    searchLastTagDataPage
    searchTagDataCount
    searchTagData
    searchAlarm
    getTagDataByDate
    getMinMaxTagDataByDate
    getAlarmList
    getTagListByEquipAndDate
    getTagListByEquipCodeAndDate
    getAlarmByEquipList
    getAlarmByEquipCodeList
    getTagDataMultiList
    getTagDataCodeMultiList
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'selectMonitorEquipByUseYnWithCode':
            useYn = gparam.get('useYn')

            sql = ''' select eq.equip_pk
	      , eq.equip_cd, eq.equip_nm
	      , cm_fn_get_dept_path_names(d.id)
	      , eq.use_yn
	        from cm_tag t
	        inner join cm_equipment eq on eq.equip_pk = t.equip_pk
	        inner join dept d on d.id = eq.dept_pk
	        where eq.del_yn = 'N'

            '''
            # -- AND eq.factory_pk = %(factory_pk)s
            if useYn:
                sql += ''' AND eq.use_yn = %(useYn)s
                '''
            sql += ''' group by eq.equip_pk, eq.equip_cd, eq.equip_nm
	      , d.id, eq.use_yn
	        order by eq.equip_nm
            '''

            dc = {}
            dc['useYn'] = useYn
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rowss(sql, dc)
 

        elif action == 'searchLastTagDataPage':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            locPk = CommonUtil.try_int( gparam.get('locPk') )
            tagMeasTypePk = CommonUtil.try_int( gparam.get('tagMeasTypePk') )
            equipCd = posparam.get('equipCd')
            locCd = posparam.get('locCd')
            searchText = posparam.get('searchText')

            sql = ''' with cte as (	select t.tag_data_pk
			, round(cast(t.data_val as numeric),  t1.dec_place) as data_val
			, t1.tag_pk, t1.tag_desc, t1.meas_point
			, tmt.meas_type_nm
			, bc.code_nm as src_system, t1.src_tag
			, eq.equip_pk, eq.equip_cd, eq.equip_nm
			, tmt.meas_unit
			, lc.loc_nm, t.data_dt
			, t1.warn_low, t1.warn_high
			, cast(round(cast(t.data_val as numeric), t1.dec_place) as text) as data_val_text
			from cm_tag_data t
			inner join (SELECT tag_pk, max(data_dt) maxDate
			      FROM cm_tag_data
			      GROUP BY tag_pk) b ON b.tag_pk = t.tag_pk 
			      AND b.maxDate = t.data_dt
			inner join cm_tag t1 on t1.tag_pk = t.tag_pk
			inner join cm_equipment eq on eq.equip_pk = t1.equip_pk
			inner join cm_location lc on lc.loc_pk = eq.loc_pk
			inner join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t1.tag_meas_type_pk
			inner join cm_base_code bc on bc.code_grp_cd = 'SRC_SYSTEM'
			and bc.code_cd = t1.src_system
			where 1 = 1

            '''
			# -- where eq.factory_pk = %(factory_pk)s
            if searchText:
                sql += ''' AND ( upper(t1.tag) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR upper(t1.tag_desc) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				)
                '''
            if equipPk > 0:
                sql += ''' AND eq.equip_pk = %(equipPk)s
                '''
            if locPk > 0:
                sql += ''' AND ( lc.loc_pk = %(locPk)s
					OR lc.loc_pk IN ( select loc_pk from (select * 
                                from cm_fn_get_loc_path(%(factory_pk)s)) x 
                                where %(locPk)s = path_info_pk)
				)
                '''
                if equipCd:
                    sql += ''' AND eq.equip_cd = %(equipCd)s
                    '''
                if locCd:
                    sql += ''' 	AND ( lc.loc_cd = %(locCd)s
					    OR lc.loc_cd IN ( select loc_cd from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x 
                            where %(locCd)s = path_info_cd 

                            )
				    )
                    '''
                            # -- and factory_pk = %(factory_pk)s)
                if tagMeasTypePk > 0:
                    sql += ''' AND tmt.tag_meas_type_pk = %(tagMeasTypePk)s
                    '''
            sql += ''' order by t1.tag_desc ASC,t.data_dt desc
		    )
		    SELECT *
		    FROM cte
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['locPk'] = locPk
            dc['tagMeasTypePk'] = tagMeasTypePk
            dc['equipCd'] = equipCd
            dc['locCd'] = locCd
            dc['searchText'] = searchText
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'searchTagDataCount':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            locPk = CommonUtil.try_int( gparam.get('locPk') )
            tagMeasTypePk = CommonUtil.try_int( gparam.get('tagMeasTypePk') )
            equipCd = posparam.get('equipCd')
            locCd = posparam.get('locCd')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            searchText = posparam.get('searchText')

            sql = ''' select count(*) as cnt
			from cm_tag_data t
			inner join cm_tag t1 on t1.tag_pk = t.tag_pk
			inner join cm_equipment eq on eq.equip_pk = t1.equip_pk
			inner join cm_location lc on lc.loc_pk = eq.loc_pk
			inner join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t1.tag_meas_type_pk
			inner join cm_base_code bc on bc.code_grp_cd = 'SRC_SYSTEM'
			and bc.code_cd = t1.src_system
			where t.data_dt BETWEEN concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            
            '''
            # -- and eq.factory_pk = %(factory_pk)s
            if searchText:
                sql += ''' AND ( upper(t1.tag) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR upper(t1.tag_desc) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				)
                '''
            if equipPk > 0:
                sql += ''' AND eq.equip_pk = %(equipPk)s
                '''
            if locPk > 0:
                sql += ''' AND ( lc.loc_pk = %(locPk)s
					OR lc.loc_pk IN ( select loc_pk from (select * 
                                from cm_fn_get_loc_path(%(factory_pk)s)) x 
                                where %(locPk)s = path_info_pk)
				)
                '''
                if equipCd:
                    sql += ''' AND eq.equip_cd = %(equipCd)s
                    '''
                if locCd:
                    sql += ''' 	AND ( lc.loc_cd = %(locCd)s
					    OR lc.loc_cd IN ( select loc_cd from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x 
                            where %(locCd)s = path_info_cd 

                            )
				    )
                    '''
                            # -- and factory_pk = %(factory_pk)s)
                if tagMeasTypePk > 0:
                    sql += ''' AND tmt.tag_meas_type_pk = %(tagMeasTypePk)s
                    '''
            sql += ''' limit 5000000
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['locPk'] = locPk
            dc['tagMeasTypePk'] = tagMeasTypePk
            dc['equipCd'] = equipCd
            dc['locCd'] = locCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['searchText'] = searchText
            dc['factory_pk'] = factory_id

            row = DbUtil.get_row(sql, dc)

            return row['cnt']


        elif action == 'searchTagData':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            locPk = CommonUtil.try_int( gparam.get('locPk') )
            tagMeasTypePk = CommonUtil.try_int( gparam.get('tagMeasTypePk') )
            equipCd = posparam.get('equipCd')
            locCd = posparam.get('locCd')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            searchText = posparam.get('searchText')

            sql = ''' select t.tag_data_pk
			    , round(cast(t.data_val as numeric), t1.dec_place) as data_val
			    , t1.tag_pk
			    , t1.tag_desc
			    , t1.meas_point
			    , tmt.meas_type_nm
			    , bc.code_nm as src_system
			    , t1.src_tag
			    , eq.equip_pk
			    , eq.equip_cd
			    , eq.equip_nm
			    , tmt.meas_unit
			    , lc.loc_nm
			    , t.data_dt
			    , t1.warn_low
			    , t1.warn_high
			    , cast(round(cast(t.data_val as numeric), t1.dec_place) as text) as data_val_text
			from cm_tag_data t
			inner join cm_tag t1 on t1.tag_pk = t.tag_pk
			inner join cm_equipment eq on eq.equip_pk = t1.equip_pk
			inner join cm_location lc on lc.loc_pk = eq.loc_pk
			inner join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t1.tag_meas_type_pk
			inner join cm_base_code bc on bc.code_grp_cd = 'SRC_SYSTEM'
			and bc.code_cd = t1.src_system
			where t.data_dt BETWEEN concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            
            '''
            # -- and eq.factory_pk = %(factory_pk)s
            if searchText:
                sql += ''' AND ( upper(t1.tag) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR upper(t1.tag_desc) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				)
                '''
            if equipPk > 0:
                sql += ''' AND eq.equip_pk = %(equipPk)s
                '''
            if locPk > 0:
                sql += ''' AND ( lc.loc_pk = %(locPk)s
					OR lc.loc_pk IN ( select loc_pk from (select * 
                                from cm_fn_get_loc_path(%(factory_pk)s)) x 
                                where %(locPk)s = path_info_pk)
				)
                '''
                if equipCd:
                    sql += ''' AND eq.equip_cd = %(equipCd)s
                    '''
                if locCd:
                    sql += ''' 	AND ( lc.loc_cd = %(locCd)s
					    OR lc.loc_cd IN ( select loc_cd from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x 
                            where %(locCd)s = path_info_cd 

                            )
				    )
                    '''
                            # -- and factory_pk = %(factory_pk)s)
                if tagMeasTypePk > 0:
                    sql += ''' AND tmt.tag_meas_type_pk = %(tagMeasTypePk)s
                    '''
            sql += ''' order by data_dt desc
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['locPk'] = locPk
            dc['tagMeasTypePk'] = tagMeasTypePk
            dc['equipCd'] = equipCd
            dc['locCd'] = locCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['searchText'] = searchText
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'searchAlarm':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            locPk = CommonUtil.try_int( gparam.get('locPk') )
            tagMeasTypePk = CommonUtil.try_int( gparam.get('tagMeasTypePk') )
            equipCd = posparam.get('equipCd')
            locCd = posparam.get('locCd')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            alarmType = posparam.get('alarmType')
            alarmStatus = posparam.get('alarmStatus')
            searchText = posparam.get('searchText')

            sql = ''' with cte as (	select al.alarm_pk
			    , e.equip_pk, e.equip_cd, e.equip_nm
			    , aa.alarm_actn_pk, l.loc_nm, l.loc_cd, t.tag_pk, t.tag
			    , sc.code_nm as src_system, ms.code_nm as meas_sensor, t.meas_point
			    , al.alarm_dt, al.alarm_status, al.return_dt
			    , at.code_nm as alarm_type, ac.code_nm as alarm_cause
			    , cast(cm_fn_round_val(al.data_val, t.dec_place) as float) as data_val
			    , al.std_val, al.alarm_ack, tmt.meas_type_nm
			    from cm_alarm al
			    inner join cm_tag t on t.tag_pk = al.tag_pk
			    inner join cm_equipment e on e.equip_pk = t.equip_pk
			    inner join cm_location l on l.loc_pk = e.loc_pk
			    left join cm_alarm_actn aa on aa.alarm_actn_pk = al.alarm_actn_pk
			    left join cm_base_code ac on ac.code_cd  = aa.alarm_cause
                and ac.code_grp_cd = 'ALARM_CAUSE'
			    left join cm_base_code at on at.code_cd = al.alarm_type 
                and at.code_grp_cd = 'ALARM_TYPE'
			    left join cm_base_code sc on sc.code_cd = t.src_system 
                and sc.code_grp_cd = 'SRC_SYSTEM'
			    left join cm_base_code ms on ms.code_cd = t.meas_sensor 
                and ms.code_grp_cd = 'MEAS_SENSOR'
			    left join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t.tag_meas_type_pk
			    where date(al.alarm_dt) >= to_date(%(startDate)s, 'YYYY-MM-DD')
		        AND date(al.alarm_dt) <= to_date(%(endDate)s, 'YYYY-MM-DD')
            
            '''
                # -- and e.factory_pk = %(factory_pk)s
            if searchText:
                sql += ''' AND ( upper(t.tag) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
					OR upper(t.tag_desc) LIKE CONCAT('%%',UPPER(%(searchText)s),'%%')
				)
                '''
            if equipPk > 0:
                sql += ''' AND e.equip_pk = %(equipPk)s
                '''
            if equipCd:
                sql += ''' AND e.equip_cd = %(equipCd)s
                '''
            if tagMeasTypePk > 0:
                sql += ''' AND tmt.tag_meas_type_pk = %(tagMeasTypePk)s
                '''
            if alarmType:
                sql += ''' and at.code_cd = %(alarmType)s
                '''
            if alarmStatus:
                sql += ''' and al.alarm_status = %(alarmStatus)s
                '''
            if locPk > 0:
                sql += ''' AND ( l.loc_pk = %(locPk)s
					OR l.loc_pk IN ( select loc_pk from (select * 
                                from cm_fn_get_loc_path(%(factory_pk)s)) x 
                                where %(locPk)s = path_info_pk)
				)
                '''
            if locCd:
                sql += ''' 	AND ( l.loc_cd = %(locCd)s
					OR l.loc_cd IN ( select loc_cd from (select * from cm_fn_get_loc_path(%(factory_pk)s)) x 
                        where %(locCd)s = path_info_cd 

                        )
				)
                '''
                        # -- and factory_pk = %(factory_pk)s)
            sql += ''' ORDER BY al.alarm_dt DESC, t.tag ASC
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['locPk'] = locPk
            dc['tagMeasTypePk'] = tagMeasTypePk
            dc['equipCd'] = equipCd
            dc['locCd'] = locCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['alarmType'] = alarmType
            dc['alarmStatus'] = alarmStatus
            dc['searchText'] = searchText
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getTagDataByDate':
            tagPk = CommonUtil.try_int( gparam.get('tagPk') )
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')

            sql = ''' select t.tag_pk
		    , t.warn_low, t.warn_high
		    , case when td.data_val= 9999 then null else td.data_val end as data_val
		    , td.data_dt
		    from cm_tag_data td
		    inner join cm_tag t on t.tag_pk = td.tag_pk 
		    where t.tag_pk = %(tagPk)s
		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
		    order by td.data_dt , t.tag_pk
            '''

            dc = {}
            dc['tagPk'] = tagPk
            dc['startDate'] = startDate
            dc['endDate'] = endDate

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getMinMaxTagDataByDate':
            tagPk = CommonUtil.try_int( gparam.get('tagPk') )
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')

            sql = ''' select t.tag as tag_nm
			, min(t.warn_low) as warn_low
			, min(t.warn_high) as warn_high
			, min(t.danger_low) as danger_low
			, min(t.danger_high) as danger_high
			, min(td.data_val) as min_val
			, max(td.data_val) as max_val
			, tmt.meas_unit as meas_unit
			, tmt.meas_type_nm as tag_meas_type_nm
		    from cm_tag_data td
		    inner join cm_tag t on t.tag_pk = td.tag_pk
		    inner join cm_tag_meas_type tmt on tmt.tag_meas_type_pk = t.tag_meas_type_pk
		    where td.tag_pk = %(tagPk)s
			and td.data_val <> 9999
		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
		    group by t.tag, tmt.meas_unit, tmt.meas_type_nm
            '''

            dc = {}
            dc['tagPk'] = tagPk
            dc['startDate'] = startDate
            dc['endDate'] = endDate

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getAlarmList':
            tagPk = CommonUtil.try_int( gparam.get('tagPk') )
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')

            sql = ''' select al.alarm_pk
			, to_char(td.data_dt, 'YYYY-MM-DD HH24:MI:SS') as alarm_dt
			, t.tag, at.code_cd as alarm_type
			, al.data_val, al.std_val, al.alarm_status
		    from cm_alarm al
		    inner join cm_tag t on al.tag_pk = t.tag_pk
		    inner join cm_base_code at on at.code_cd  = al.alarm_type
		    and at.code_grp_cd = 'ALARM_TYPE'
		    inner join cm_tag_data td on td.tag_data_pk = al.tag_data_pk
		    where al.del_yn = 'N'
		    and t.tag_pk = %(tagPk)s
		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            '''

            dc = {}
            dc['tagPk'] = tagPk
            dc['startDate'] = startDate
            dc['endDate'] = endDate

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getTagListByEquipAndDate':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            chartGrpCd = posparam.get('chartGrpCd')

            sql = ''' SELECT t.tag_pk, t.tag AS tag_nm, t.tag_desc AS tag_desc
		       , Min(t.warn_low) AS warn_low
		       , Max(t.warn_high) AS warn_high
		       , Min(t.danger_low) AS danger_low
		       , Max(t.danger_high) AS danger_high
		       , Min(td.data_val) AS min_val
		       , Max(td.data_val) AS max_val
		    FROM cm_tag_data td
		    INNER JOIN cm_tag t on t.tag_pk = td.tag_pk
		    INNER JOIN cm_equipment eq ON eq.equip_pk = t.equip_pk
		    WHERE eq.equip_pk = %(equipPk)s
		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            and td.data_val <> 9999
            '''
            if chartGrpCd:
                sql += ''' and t.chart_grp_cd = %(chartGrpCd)s
                '''
            sql += ''' GROUP  BY t.tag_pk , t.tag
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['chartGrpCd'] = chartGrpCd

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getTagListByEquipCodeAndDate':
            equipCd = posparam.get('equipCd')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            chartGrpCd = posparam.get('chartGrpCd')

            sql = ''' SELECT t.tag_pk, t.tag AS tag_nm, t.tag_desc AS tag_desc
		       , Min(t.warn_low) AS warn_low
		       , Max(t.warn_high) AS warn_high
		       , Min(t.danger_low) AS danger_low
		       , Max(t.danger_high) AS danger_high
		       , Min(td.data_val) AS min_val
		       , Max(td.data_val) AS max_val
		    FROM cm_tag_data td
		    INNER JOIN cm_tag t on t.tag_pk = td.tag_pk
		    INNER JOIN cm_equipment eq ON eq.equip_pk = t.equip_pk
		    WHERE eq.equip_cd = %(equipCd)s

		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            and td.data_val <> 9999
            '''
            # -- and eq.factory_pk = %(factory_pk)s
            if chartGrpCd:
                sql += ''' and t.chart_grp_cd = %(chartGrpCd)s
                '''
            sql += ''' GROUP  BY t.tag_pk , t.tag
            '''

            dc = {}
            dc['equipCd'] = equipCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['chartGrpCd'] = chartGrpCd
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getAlarmByEquipList':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')

            sql = ''' select al.alarm_pk
			, to_char(td.data_dt, 'YYYY-MM-DD HH24:MI:SS') as alarm_dt
			, t.tag, alt.code_cd as alarm_type
			, al.data_val, al.std_val, al.alarm_status
		    from cm_alarm al
		    inner join cm_tag t on t.tag_pk = al.tag_pk
		    inner join cm_base_code alt on alt.code_cd  = al.alarm_type
		    and alt.code_grp_cd = 'ALARM_TYPE'
		    inner join cm_tag_data td on td.tag_data_pk = al.tag_data_pk
		    WHERE t.equip_pk = %(equipPk)s
		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            and al.del_yn = 'N'
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['startDate'] = startDate
            dc['endDate'] = endDate

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getAlarmByEquipCodeList':
            equipCd = posparam.get('equipCd')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')

            sql = ''' select al.alarm_pk
			, to_char(td.data_dt, 'YYYY-MM-DD HH24:MI:SS') as alarm_dt
			, t.tag, alt.code_cd as alarm_type
			, al.data_val, al.std_val, al.alarm_status
		    from cm_alarm al
		    inner join cm_tag t on t.tag_pk = al.tag_pk
		    inner join cm_base_code alt on alt.code_cd  = al.alarm_type
		    and alt.code_grp_cd = 'ALARM_TYPE'
		    inner join cm_tag_data td on td.tag_data_pk = al.tag_data_pk
            inner join cm_equipment eq on eq.equip_pk = t.equip_pk
		    WHERE eq.equip_cd = %(equipCd)s
		    and td.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            and al.del_yn = 'N'
            '''

            dc = {}
            dc['equipCd'] = equipCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getTagDataMultiList':
            equipPk = CommonUtil.try_int( gparam.get('equipPk') )
            tagPks = posparam.get('tagPks')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            chartGrpCd = posparam.get('chartGrpCd')

            tag_pk_list = tagPks.split(',')

            #dc = {}
            sql = ''' SELECT to_char(t1.data_dt, 'YYYY-MM-DD HH24:MI:SS') as date_val '''
            for item in tag_pk_list:
                #tag_pk = CommonUtil.try_int(item)
                #key = 'tag'+str(tag_pk)
                #dc[key] = tag_pk
                sql += '''
                , max(case when t1.tag_pk = ''' + item + ''')s then (case when t1.data_val = 9999 then null else t1.data_val end) else null end) as data_''' + item
            sql += ''' 
            from cm_tag_data T1
            INNER JOIN cm_tag T2 ON T2.TAG_PK = T1.TAG_PK
		    where t1.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            and t2.equip_pk = %(equipPk)s
            '''
            if chartGrpCd:
                sql += ''' and t2.chart_grp_cd = %(chartGrpCd)s
                '''
            sql += ''' GROUP BY T1.data_dt
            ORDER BY T1.data_dt
            '''

            dc = {}
            dc['equipPk'] = equipPk
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['chartGrpCd'] = chartGrpCd

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getTagDataCodeMultiList':
            equipCd = CommonUtil.try_int( gparam.get('equipCd') )
            tagPks = posparam.get('tagPks')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            chartGrpCd = posparam.get('chartGrpCd')

            tag_pk_list = tagPks.split(',')

            #dc = {}
            sql = ''' SELECT to_char(t1.data_dt, 'YYYY-MM-DD HH24:MI:SS') as date_val '''
            for item in tag_pk_list:
                #tag_pk = CommonUtil.try_int(item)
                #key = 'tag'+str(tag_pk)
                #dc[key] = tag_pk
                sql += '''
                , max(case when t1.tag_pk = ''' + item + ''')s then (case when t1.data_val = 9999 then null else t1.data_val end) else null end) as data_''' + item
            sql += ''' 
            from cm_tag_data T1
            INNER JOIN cm_tag T2 ON T2.tag_pk = T1.tag_pk
            INNER JOIN cm_equipment eq on eq.equip_pk = t2.equip_pk
		    where t1.data_dt between concat(%(startDate)s, ' 00:00:00')::timestamp and concat(%(endDate)s, ' 23:59:59')::timestamp
            and eq.equip_cd = %(equipCd)s
            '''
            if chartGrpCd:
                sql += ''' and t2.chart_grp_cd = %(chartGrpCd)s
                '''
            sql += ''' GROUP BY T1.data_dt
            ORDER BY T1.data_dt
            '''

            dc = {}
            dc['equipCd'] = equipCd
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['chartGrpCd'] = chartGrpCd

            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = 'kmms/monitor : action-{}'.format(action)
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