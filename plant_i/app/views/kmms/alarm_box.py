from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAlarmBox, CmEquipment

def alaram_box(context):
    '''
    api/kmms/alaram_box    알람조치
    김태영 

    findAll
    findOne
    boxEquipNmDistPk
    insert
    update
    delete
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            useYn = gparam.get('useYn')
            searchText = gparam.get('searchText')

            sql = ''' select ab.alarm_box_pk, ab.box_equip_nm, ab.box_group_cd
	        , ab.top_scale, ab.left_scale
	        , ab.top_scale_full, ab.left_scale_full
	        , e.equip_cd, e.equip_nm, ab.use_yn
	        from cm_alarm_box ab
	        inner join cm_equipment e on ab.equip_pk=e.equip_pk
	        AND e.factory_pk = %(factory_pk)s
            '''
            if searchText:
                sql += ''' AND (upper(coalesce(ab.box_equip_nm, '')) like ('%'||upper(%(searchText)s)||'%'))
                '''
            if useYn:
                sql += ''' AND ab.use_yn = %(useYn)s'
                '''

            dc = {}
            dc['useYn'] = useYn
            dc['searchText'] = searchText
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
            if action == 'countBy':
                items = len(items)
 

        elif action == 'findOne':
            alarmBoxPk = CommonUtil.try_int( gparam.get('alarmBoxPk') )

            sql = ''' select ab.alarm_box_pk, ab.box_equip_nm, ab.box_group_cd
	        , ab.top_scale, ab.left_scale
	        , ab.top_scale_full, ab.left_scale_full
	        , e.equip_cd, e.equip_nm, ab.use_yn
	        from cm_alarm_box ab
	        inner join cm_equipment e on ab.equip_pk=e.equip_pk
	        where ab.alarm_box_pk = %(alarmBoxPk)s
            '''

            dc = {}
            dc['alarmBoxPk'] = alarmBoxPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'boxEquipNmDistPk':
            alarmBoxPk = CommonUtil.try_int( gparam.get('alarmBoxPk') )
            boxEquipNm =  gparam.get('boxEquipNm') 

            sql = ''' select count(*)
		    from cm_alarm_box
		    where alarm_box_pk != %(alarmBoxPk)s
		    and box_equip_nm = %(boxEquipNm)s
            '''

            dc = {}
            dc['alarmBoxPk'] = alarmBoxPk
            dc['boxEquipNm'] = boxEquipNm

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'update']:
            alarmBoxPk = CommonUtil.try_int(posparam.get('alarmBoxPk'))
            topScale = CommonUtil.try_float(posparam.get('topScale'))
            leftScale = CommonUtil.try_float(posparam.get('leftScale'))
            topScaleFull = CommonUtil.try_float(posparam.get('topScaleFull'))
            leftScaleFull = CommonUtil.try_float(posparam.get('leftScaleFull'))

            boxGroupCd = posparam.get('boxGroupCd')
            boxEquipNm = posparam.get('boxEquipNm')
            useYn = posparam.get('useYn')

            if action == 'update':
                c = CmAlarmBox.objects.get(id=alarmBoxPk)

            else:
                ''' equip pk는 수정 안 한다고 간주함.
                '''
                q = CmEquipment.objects.filter(EquipCode=equipCd)
                equip = q.first()
                equip_pk = equip.id
                c = CmAlarmBox()
                c.CmEquipment_id = equip_pk

            c.BoxGroupCode = boxGroupCd
            c.BoxEquipName = boxEquipNm
            
            c.TopScale = topScale
            c.LeftScale = leftScale
            c.TopScaleFull = topScaleFull
            c.LeftScaleFull = leftScaleFull
            c.UseYn = useYn

            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알람박스가 수정되었습니다.'}


        elif action == 'delete':
            alarmBoxPk = CommonUtil.try_int(posparam.get('alarmBoxPk'))
            CmAlarmBox.objects.filter(id=alarmBoxPk).delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/alaram_box : action-{}'.format(action)
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