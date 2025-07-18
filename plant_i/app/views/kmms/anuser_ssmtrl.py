from re import A
from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAnUserSsMtrl

def anuser_ssmtrl(context):
    '''
    api/kmms/anuser_ssmtrl    알람알림사용자구독자재
    김태영 

    getAlarmNotiUserMtrlList
    save
    deleteByAlarmNotiGrp_AlarmNotiGrpPkAndUserInfo_UserPk
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'getAlarmNotiUserMtrlList':
            alarmNotiGrpPk = CommonUtil.try_int( gparam.get('alarmNotiGrpPk') )
            userPk = CommonUtil.try_int( gparam.get('userPk') )

            sql = ''' select ang.alarm_noti_grp_pk
	        , ui."User_id" as user_pk, cm_fn_user_nm(ui."Name", 'N') as user_nm
	        , m.mtrl_pk, m.mtrl_cd, m.mtrl_nm
	        , m.safety_stock_amt, m.unit_price, s.supplier_nm
	        from cm_an_user_ss_mtrl aus
	        inner join cm_alarm_noti_grp ang on ang.alarm_noti_grp_pk = aus.alarm_noti_grp_pk
	        inner join user_profile ui on ui."User_id"  = aus.user_pk
	        inner join cm_material m on m.mtrl_pk = aus.mtrl_pk
	        left outer join cm_supplier s on s.supplier_pk = m.supplier_pk
	        where ang.alarm_noti_grp_pk = %(alarmNotiGrpPk)s
	        and ui."User_id" = %(userPk)s
            '''

            dc = {}
            dc['alarmNotiGrpPk'] = alarmNotiGrpPk
            dc['userPk'] = userPk

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'save':
            Q = posparam.get('Q')

            for item in Q:
                c = CmAnUserSsMtrl()

                c.CmAlarmNotiGroup_id = item['alarmNotiGrpPk']
                c.CmMaterial_id = item['mtrlPk']
                c.UserPk = item['userPk']

                #c.set_audit(user)
                c.save()

            return {'success': True, 'message': '알람알림사용자구독자재가 저장되었습니다.'}

        elif action == 'deleteByAlarmNotiGrp_AlarmNotiGrpPkAndUserInfo_UserPk':
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            userPk = CommonUtil.try_int(posparam.get('userPk'))

            q = CmAnUserSsMtrl.objects.filter(CmAlarmNotiGroup_id=alarmNotiGrpPk)
            q = q.filter(UserPk=userPk)
            q.delete()

            items = {'success': True}


    except Exception as ex:
        source = 'kmms/anuser_ssmtrl : action-{}'.format(action)
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