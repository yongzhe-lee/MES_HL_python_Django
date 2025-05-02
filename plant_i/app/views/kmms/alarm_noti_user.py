from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAlarmNotiUser

def alarm_noti_user(context):
    '''
    api/kmms/alarm_noti_user    알람알림사용자
    김태영 

    getAlarmNotiUserList
    save
    deleteByAlarmNotiGrp_AlarmNotiGrpPk
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 


    try:
        if action == 'getAlarmNotiUserList']:
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))

            sql = ''' select
	          anu.alarm_noti_grp_pk
	        , ui."User_id" as user_pk
	        , fn_user_nm(ui."Name", 'N') as user_nm
	        , au.username as login_id
	        , d.id as dept_pk
	        , d."Name" as dept_nm
	        , anu.noti_yn
	       	, bc.code_cd as notiGrpTypeCd
	        from cm_alarm_noti_user anu
	        inner join cm_alarm_noti_grp ang on ang.alarm_noti_grp_pk = anu.alarm_noti_grp_pk
	        inner join cm_base_code bc on bc.code_grp_cd = 'NOTI_GRP_TYPE' 
	        and bc.code_cd = ang.noti_grp_type 
	        inner join user_profile ui on ui."User_id" = anu.user_pk
	        left join auth_user au on au.id = ui."User_id" 
	        inner join dept d on d.id = ui."Depart_id" 
	        where ang.alarm_noti_grp_pk = %(alarmNotiGrpPk)s
            '''

            dc = {}
            dc['alarmNotiGrpPk'] = alarmNotiGrpPk

            items = DbUtil.get_rows(sql, dc)

        elif action == 'save']:
            Q = posparam.get('Q')

            for item in Q:
                c = CmAlarmNotiUser()
                c.CmAlarmNotiGroup_id = item['alarmNotiGrpPk']
                c.NotiYn = item['notiYn']
                c.UserPk = item['userPk']

                c.set_audit(user)
                c.save()

            return {'success': True, 'message': '알람알림사용자의 정보가 수정되었습니다.'}

            return {'success': True, 'message': '알람알림사용자의 사용여부가 수정되었습니다.'}

        elif action == 'deleteByAlarmNotiGrp_AlarmNotiGrpPk':
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))

            CmAlarmNotiUser.objects.filter(id=alarmNotiGrpPk).delete()

            items = {'success': True}
    

    except Exception as ex:
        source = 'kmms/alarm_noti_user : action-{}'.format(action)
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