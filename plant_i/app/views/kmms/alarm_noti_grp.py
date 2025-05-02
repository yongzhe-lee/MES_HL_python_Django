from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAlarmNotiGroup

def alarm_noti_grp(context):
    '''
    api/kmms/alarm_noti_grp    알람알림그룹
    김태영 

    findAll
    findOne
    findCode
    insert
    update
    updateAlarmNotiGrpUseYn
    delete
    findDeletable
    countByNotiGrpNmIgnoreCase
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

    def findDeletableAlarmNotiGroup(alarmNotiGrpPk):
        sql = ''' select 1 as check
    	where exists (select 1 
            from cm_alarm_noti_user 
            where alarm_noti_grp_pk = %(alarmNotiGrpPk)s
            UNION ALL 
            select 1
            from cm_an_user_ss_mtrl
            where alarm_noti_grp_pk = %(alarmNotiGrpPk)s
            UNION ALL 
            select 1
            from cm_anoti_sms_hist
            where alarm_noti_grp_pk = %(alarmNotiGrpPk)s
            UNION ALL select 1
	        from cm_anoti_mail_hist
	        where alarm_noti_grp_pk = %(alarmNotiGrpPk)s
        )
        '''
        dc = {}
        dc['alarmNotiGrpPk'] = alarmNotiGrpPk
        row = DbUtil.get_row(sql, dc)
        if row != {}:
            return 1
        else:
            return 0

    try:
        if action == 'findAll']:

            sql = ''' select ang.alarm_noti_grp_pk, ang.noti_grp_nm
	        , bc.code_cd as notiGrpType, bc.code_nm as notiGrpTypeNm
	        , ang.mail_snd_yn, ang.sms_snd_yn, ang.mail_title, ang.mail_content
	        , ang.mail_sndr_addr, ang.sms_content, ang.sms_sndr_no
	        , ang.remark, ang.use_yn
	        , ang.inserter_id, ang.insert_dt, ang.updater_id, ang.update_dt
	        from alarm_noti_grp ang
	        inner join base_code bc on bc.code_grp_cd = 'NOTI_GRP_TYPE'
	        and bc.code_cd = ang.noti_grp_type
            where 1 = 1
            order by ang.noti_grp_nm
            '''

            dc = {}

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            alarmNotiGrpPk = CommonUtil.try_int( gparam.get('alarmNotiGrpPk') )

            sql = ''' select ang.alarm_noti_grp_pk, ang.noti_grp_nm
	        , bc.code_cd as notiGrpType, bc.code_nm as notiGrpTypeNm
	        , ang.mail_snd_yn, ang.sms_snd_yn, ang.mail_title, ang.mail_content
	        , ang.mail_sndr_addr, ang.sms_content, ang.sms_sndr_no
	        , ang.remark, ang.use_yn
	        , ang.inserter_id, ang.insert_dt, ang.updater_id, ang.update_dt
	        from alarm_noti_grp ang
	        inner join base_code bc on bc.code_grp_cd = 'NOTI_GRP_TYPE'
	        and bc.code_cd = ang.noti_grp_type
            where ang.alarm_noti_grp_pk = %(alarmNotiGrpPk)s
	        order by ang.noti_grp_nm
            '''

            dc = {}
            dc['alarmNotiGrpPk'] = alarmNotiGrpPk

            items = DbUtil.get_row(sql, dc)

        elif action == 'findCode':
            notiGrpType = gparam.get('notiGrpType')

            sql = ''' select ang.alarm_noti_grp_pk, ang.noti_grp_nm
	        , bc.code_cd as notiGrpType, bc.code_nm as notiGrpTypeNm
	        , ang.mail_snd_yn, ang.sms_snd_yn, ang.mail_title, ang.mail_content
	        , ang.mail_sndr_addr, ang.sms_content, ang.sms_sndr_no
	        , ang.remark, ang.use_yn
	        , ang.inserter_id, ang.insert_dt, ang.updater_id, ang.update_dt
	        from alarm_noti_grp ang
	        inner join base_code bc on bc.code_grp_cd = 'NOTI_GRP_TYPE'
	        and bc.code_cd = ang.noti_grp_type
            where ang.noti_grp_type = %(notiGrpType)s
	        order by ang.noti_grp_nm
            '''

            dc = {}
            dc['notiGrpType'] = notiGrpType

            items = DbUtil.get_row(sql, dc)


        elif action in ['insert', 'update']:
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            notiGrpNm = posparam.get('notiGrpNm')
            mailTitle = posparam.get('mailTitle')
            mailContent = posparam.get('mailContent')
            mailSndrAddr = posparam.get('mailSndrAddr')
            smsContent = posparam.get('smsContent')
            smsSndrNo = posparam.get('smsSndrNo')
            mailSndYn = posparam.get('mailSndYn')
            smsSndYn = posparam.get('smsSndYn')
            remark = posparam.get('remark')
            useYn = posparam.get('useYn')
  
            if action == 'update':
                c = CmAlarmNotiGroup.objects.get(id=alarmNotiGrpPk)

            else:
                c = CmAlarmNotiGroup()

            c.NotiGrpName = notiGrpNm
            c.UseYn = useYn
            c.NotiGrpType = notiGrpType
            c.MailTitle = mailTitle
            c.MailContent = mailContent
            c.MailSndrAddr = mailSndrAddr
            c.SmsContent = smsContent
            c.SmsSndrNo = smsSndrNo
            c.MailSndYn = mailSndYn
            c.SmsSndYn = smsSndYn
            c.Remark = remark
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알람알림그룹의 정보가 수정되었습니다.'}

        elif action == 'updateAlarmNotiGrpUseYn':
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            useYn = posparam.get('useYn')
  
            c = CmAlarmNotiGroup.objects.get(id=alarmNotiGrpPk)
            c.UseYn = useYn
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알람알림그룹의 사용여부가 수정되었습니다.'}

        elif action == 'delete':
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            if not findDeletableAlarmNotiGroup(alarmNotiGrpPk):
                CmAlarmNotiGroup.objects.filter(id=alarmNotiGrpPk).delete()

            items = {'success': True}
    


        elif action == 'findDeletableAlarmNotiGroup':
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            return findDeletableAlarmNotiGroup(alarmNotiGrpPk)


        elif action == 'countByNotiGrpNmIgnoreCase':
            notiGrpNm = gparam.get('notiGrpNm')
            sql = ''' select count(ang.alarm_noti_grp_pk)
            from cm_alarm_noti_grp ang
            where upper(ang.noti_grp_nm) = upper(%(notiGrpNm)s)
            '''
            dc = {}
            dc['notiGrpNm'] = notiGrpNm

            items = DbUtil.get_row(sql, dc)


        elif action == 'countByNotiGrpNmIgnoreCaseAndAlarmNotiGrpPkNot':
            alarmNotiGrpPk = CommonUtil.try_int( gparam.get('alarmNotiGrpPk'))
            notiGrpNm = gparam.get('notiGrpNm')
            sql = ''' select count(ang.alarm_noti_grp_pk)
            from cm_alarm_noti_grp ang
            where upper(ang.noti_grp_nm) = upper(%(notiGrpNm)s)
            and ang.alarm_noti_grp_pk != %(alarmNotiGrpPk)s
            '''
            dc = {}
            dc['notiGrpNm'] = notiGrpNm
            dc['alarmNotiGrpPk'] = alarmNotiGrpPk

            items = DbUtil.get_row(sql, dc)

    except Exception as ex:
        source = 'kmms/alarm_noti_grp : action-{}'.format(action)
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