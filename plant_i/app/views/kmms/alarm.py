from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAlarm, CmEquipment

def alarm(context):
    '''
    api/kmms/alarm    알람조치
    김태영 

    findOne
    getEquipAlarmByLoc
    getAlarmbyAlarmTypeDanger
    getAlarmbyAlarmTypeWarn
    getEquipAlarmStaticsSum
    getEquipAlarmBoxInfo
    findAlarm
    updateAlarmAck
    updateAlarmActn
    getPlantAlarmStatus
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findOne':
            alarmPk = CommonUtil.try_int( gparam.get('alarmPk') )

            sql = ''' select al.alarm_pk, t.tag_pk, al.alarm_dt
			, at.code_cd as alarm_type_cd, at.code_nm as alarm_type_nm
			, al.data_val, al.std_val, al.alarm_status
			, al.return_dt, al.alarm_actn_pk, al.del_yn
			, al.update_dt, al.alarm_ack
		    from cm_alarm al
		    inner join cm_tag t on t.tag_pk = al.tag_pk
		    left join cm_alarm_actn aa on aa.alarm_actn_pk = al.alarm_actn_pk
		    left join cm_base_code ac on ac.code_cd = aa.alarm_cause 
		    and ac.code_grp_cd = 'ALARM_CAUSE'
		    left join cm_base_code act on act.code_cd = aa.actn_type 
		    and act.code_grp_cd = 'ACTION_TYPE'
		    left join cm_base_code at on at.code_cd = al.alarm_type
		    and at.code_grp_cd = 'ALARM_TYPE'
		    where al.alarm_pk = %(alarmPk)s
            '''

            dc = {}
            dc['alarmPk'] = alarmPk

            items = DbUtil.get_rows(sql, dc)
        

        elif action == 'getEquipAlarmByLoc':
            ''' tunning 필요
            '''
            sql = ''' with sub as (SELECT l.loc_nm AS loc_nm
		        , Max(a.alarm_dt) AS alarm_dt
		        , t.tag_pk AS tag_pk, t.tag_desc AS tag_desc
		        FROM   cm_alarm a
		        INNER JOIN cm_tag t ON t.tag_pk = a.tag_pk
		        INNER JOIN cm_equipment e ON e.equip_pk = t.equip_pk
		        INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
		        WHERE  To_char(a.alarm_dt, 'YYYYMMDD') = To_char(Now(), 'YYYYMMDD')
                and e.factory_pk = %(factory_pk)s
                GROUP  BY l.loc_nm, t.tag_pk, t.tag_desc
            )
            SELECT sub.loc_nm, sub.alarm_dt, sub.tag_desc
		    , tmt.meas_type_nm, a.alarm_type, a.data_val
		    , a.std_val, t.src_system, 'yyyymmddhhmmss' as date_hh_mm_ss_format
		    FROM  sub
		    INNER JOIN cm_tag t ON t.tag_pk = sub.tag_pk
		    INNER JOIN cm_tag_meas_type tmt ON tmt.tag_meas_type_pk = t.tag_meas_type_pk
		    INNER JOIN cm_alarm a ON a.tag_pk = t.tag_pk
		    AND a.alarm_dt = sub.alarm_dt
		    ORDER  BY a.alarm_dt DESC
            '''

            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)


        elif action == 'getAlarmbyAlarmTypeDanger':

            sql = ''' select l.loc_nm, e.equip_cd, e.equip_nm
			, max(al.alarm_dt) as alarm_dt
		    from cm_alarm al
		    inner join cm_tag t on t.tag_pk = al.tag_pk
		    inner join cm_equipment e on e.equip_pk = t.equip_pk
		    inner join cm_location l on l.loc_pk = e.loc_pk 
		    inner join cm_base_code at on at.code_cd = al.alarm_type  
		    and at.code_grp_cd = 'ALARM_TYPE'
		    where at.code_cd in ('HH', 'LL')
		    AND to_char(al.alarm_dt , 'YYYYMMDD') = to_char(now(), 'YYYYMMDD')
            and e.factory_pk = %(factory_pk)s
 		    GROUP BY l.loc_nm, e.equip_cd, e.equip_nm
		    ORDER BY alarm_dt desc
            '''

            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getAlarmbyAlarmTypeWarn':

            sql = ''' select l.loc_nm, e.equip_cd, e.equip_nm
			, max(al.alarm_dt) as alarm_dt
		    from cm_alarm al
		    inner join cm_tag t on t.tag_pk = al.tag_pk
		    inner join cm_equipment e on e.equip_pk = t.equip_pk
		    inner join cm_location l on l.loc_pk = e.loc_pk 
		    inner join cm_base_code at on at.code_cd = al.alarm_type  
		    and at.code_grp_cd = 'ALARM_TYPE'
		    where at.code_cd in ('HI', 'LO', 'LK', 'ND')
		    AND to_char(al.alarm_dt , 'YYYYMMDD') = to_char(now(), 'YYYYMMDD')
            and e.factory_pk = %(factory_pk)s
 		    GROUP BY l.loc_nm, e.equip_cd, e.equip_nm
		    ORDER BY alarm_dt desc
            '''

            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getEquipAlarmStaticsSum':
            today = gparam.get('today')
            sql = ''' WITH cte AS ( select
			    count(case when t.alarm_status = 'A' and at.code_cd in ('HH', 'LL') then 1 end) as da
			    , count(case when to_char(t.alarm_dt, 'YYYY-MM-DD') = %(today)s and at.code_cd in ('HH', 'LL') then 1 end) as de
			    , count(case when to_char(t.alarm_dt, 'YYYY-MM-DD') = %(today)s and at.code_cd in ('HH', 'LL') 
                        and t.alarm_status = 'C' then 1 end) as dr
			    , count(case when t.alarm_status = 'A' and at.code_cd in ('HI', 'LO', 'LK', 'ND') then 1 end) as wa
			    , count(case when to_char(t.alarm_dt, 'YYYY-MM-DD') = %(today)s and at.code_cd in ('HI', 'LO', 'LK', 'ND') then 1 end) as we
			    , count(case when to_char(t.alarm_dt, 'YYYY-MM-DD') = %(today)s and at.code_cd in ('HI', 'LO', 'LK', 'ND') 
                        and t.alarm_status = 'C' then 1 end) as wr
			FROM cm_alarm t
            inner join cm_tag tg on t.tag_pk = tg.tag_pk
            inner join cm_equipment e on tg.equip_pk = e.equip_pk
			left outer join cm_base_code at on t.alarm_type = at.code_cd 
			and at.code_grp_cd = 'ALARM_TYPE'
			WHERE 1 = 1
            AND e.factory_pk = %(factory_pk)s
		    )
		    SELECT cte.*
		    , (cte.da + cte.wa) as sum_a
		    , (cte.de + cte.we) as sum_e
		    , (cte.dr + cte.wr) as sum_r
		    FROM cte
            '''

            dc = {}
            dc['today'] = today
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'getEquipAlarmBoxInfo':
            boxGroupCd = gparam.get('boxGroupCd')
            today = gparam.get('today')

            sql = ''' WITH cte AS ( select ab.box_equip_nm as equip_nm
			    , count(case when a.alarm_status = '0' and a.alarm_type in ('HH', 'LL') then 1 end) as da
			    , count(case when to_char(a.alarm_dt, 'YYYY-MM-DD') = %(today)s and a.alarm_type in ('HH', 'LL') then 1 end) as de
			    , count(case when to_char(a.alarm_dt, 'YYYY-MM-DD') = %(today)s and a.alarm_type in ('HH', 'LL') 
                            and a.alarm_status = '1' then 1 end) as dr
			    , count(case when a.alarm_status = '0' and a.alarm_type in ('HI', 'LO', 'LK', 'ND') then 1 end) as wa
			    , count(case when to_char(a.alarm_dt, 'YYYY-MM-DD') = %(today)s and a.alarm_type in ('HI', 'LO', 'LK', 'ND') then 1 end) as we
			    , count(case when to_char(a.alarm_dt, 'YYYY-MM-DD') = %(today)s and a.alarm_type in ('HI', 'LO', 'LK', 'ND') 
                            and a.alarm_status = '1' then 1 end) as wr
			    , (case when ab.top_scale is not null then concat(ab.top_scale::text, '%') else '' end) as top_scale
			    , (case when ab.left_scale is not null then concat(ab.left_scale::text, '%') else '' end) as left_scale
			    , (case when ab.top_scale_full is not null then concat(ab.top_scale_full::text, '%') else '' end) as top_scale_full
			    , (case when ab.left_scale_full is not null then concat(ab.left_scale_full::text, '%') else '' end) as left_scale_full
			    from cm_alarm_box ab
			    inner join cm_equipment e on e.equip_pk = ab.equip_pk
			    left join cm_tag t on t.equip_pk = e.equip_pk
			    left join cm_alarm a on a.tag_pk = t.tag_pk
			    where ab.box_group_cd = %(boxGroupCd)s
			    group by e.equip_cd, ab.box_equip_nm, ab.top_scale, ab.left_scale, ab.top_scale_full, ab.left_scale_full
		    )
		    SELECT cte.*
		    , (cte.da + cte.wa) as sum_a
		    , (cte.de + cte.we) as sum_e
		    , (cte.dr + cte.wr) as sum_r
		    FROM cte
            '''

            dc = {}
            dc['boxGroupCd'] = boxGroupCd
            dc['today'] = today
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'findAlarm':
            alarmPk = CommonUtil.try_int( gparam.get('alarmPk') )

            sql = ''' select al.alarm_pk, aa.alarm_actn_pk
			, l.loc_nm, e.equip_cd, e.equip_nm
			, t.tag, at.code_cd as alarm_type
			, al.alarm_status, ac.code_cd as alarm_cause, act.code_cd as actn_type, aa.actn_remark
		    from cm_alarm al
		    inner join cm_tag t on t.tag_pk = al.tag_pk
		    inner join cm_equipment e on e.equip_pk = t.equip_pk
		    inner join cm_location l on l.loc_pk = e.loc_pk
		    left join cm_alarm_actn aa on aa.alarm_actn_pk = al.alarm_actn_pk
		    left join cm_base_code ac on ac.code_cd = aa.alarm_cause 
		    and ac.code_grp_cd = 'ALARM_CAUSE'
		    left join cm_base_code act on act.code_cd = aa.actn_type 
		    and act.code_grp_cd = 'ACTION_TYPE'
		    left join cm_base_code at on at.code_cd = al.alarm_type 
		    and at.code_grp_cd = 'ALARM_TYPE'
		    where al.alarm_pk = %(alarmPk)s
            '''

            dc = {}
            dc['alarmPk'] = alarmPk

            items = DbUtil.get_rows(sql, dc)


        elif action == 'updateAlarmAck':
            alarmPk = CommonUtil.try_int(posparam.get('alarmPk'))
            alarmAck = posparam.get('alarmAck')
         
            q = CmEquipment.objects.filter(EquipCode=equipCd)
            c.AlarmAck = alarmAck
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알람이 수정되었습니다.'}


        elif action == 'updateAlarmActn':
            alarmPk = CommonUtil.try_int(posparam.get('alarmPk'))
            alarmActnPk = CommonUtil.try_int(posparam.get('alarmActnPk'))
         
            q = CmEquipment.objects.filter(EquipCode=equipCd)
            c.CmAlarmAction_id = alarmActnPk
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알람이 수정되었습니다.'}


        elif action == 'findAlarm':
            today = gparam.get('today') 
            yesterday = gparam.get('yesterday') 

            sql = ''' select cm_fn_get_loc_plant_nm_code(l.loc_cd, l.factory_pk) as plant_nm
			, l.loc_nm
			, count(distinct e.equip_pk) as equip_cnt
			, count(distinct t.equip_pk) as tag_equip_cnt
			, count(case when to_char(a.alarm_dt,'YYYY-MM-DD') = %(today)s and a.alarm_type in ('HH', 'LL') then 1 end) as today_danger
			, count(case when to_char(a.alarm_dt,'YYYY-MM-DD') = %(today)s and a.alarm_type in ('HI', 'LO', 'LK', 'ND') then 1 end) as today_warn
			, count(case when to_char(a.alarm_dt,'YYYY-MM-DD') = %(yesterday)s and a.alarm_type in ('HH', 'LL') then 1 end) as yesterday_danger
			, count(case when to_char(a.alarm_dt,'YYYY-MM-DD') = %(yesterday)s and a.alarm_type in ('HI', 'LO', 'LK', 'ND') then 1 end) as yesterday_warn
			from cm_location l
			inner join cm_equipment e on e.loc_pk =l.loc_pk
			left join cm_tag t on t.equip_pk = e.equip_pk 
			left join cm_alarm a on a.tag_pk = t.tag_pk
			where l.building_yn = 'N' 
			and l.plant_yn = 'N'
            and e.factory_pk = %(factory_pk)s
			group by l.loc_cd, l.loc_nm, l.factory_pk
			having count(distinct t.equip_pk) > 0
            '''

            dc = {}
            dc['today'] = today
            dc['yesterday'] = yesterday
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = 'kmms/alarm : action-{}'.format(action)
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