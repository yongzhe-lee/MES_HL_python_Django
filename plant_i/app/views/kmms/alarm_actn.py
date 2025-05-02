from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAlarmAction, CmEquipment

def alarm_actn(context):
    '''
    api/kmms/alarm_actn    알람조치
    김태영 

    insert
    update
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action in ['insert', 'update']:
            alarmActnPk = CommonUtil.try_int(posparam.get('alarmActnPk'))

            equipCd = posparam.get('equipCd')
            actnDt = posparam.get('actnDt')
            alarmStatus = posparam.get('alarmStatus')
            alarmCauseCd = posparam.get('alarmCauseCd')
            actnTypeCd = posparam.get('actnTypeCd')
            actnRemark = posparam.get('actnRemark')
            actnUserId = user.id
  
            if action == 'update':
                c = CmAlarmAction.objects.get(id=alarmActnPk)

            else:
                ''' equip pk는 수정 안 한다고 간주함.
                '''
                q = CmEquipment.objects.filter(EquipCode=equipCd)
                equip = q.first()
                equip_pk = equip.id
                c = CmAlarmAction()
                c.CmEquipment_id = equip_pk

            c.ActionnDt = actnDt
            c.ActionUserId = actnUserId
            
            c.AlarmStatus = alarmStatus
            c.AlarmCause = alarmCauseCd
            c.ActionType = actnTypeCd
            c.ActionRemark = actnRemark

            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알람조치가 수정되었습니다.'}


    except Exception as ex:
        source = 'kmms/alarm_actn : action-{}'.format(action)
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