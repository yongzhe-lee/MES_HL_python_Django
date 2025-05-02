from re import A
from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAnotiSmsHist

def anoti_sms_hist(context):
    '''
    api/kmms/anoti_sms_hist    알림메일이력
    김태영 

    findAll
    findOne
    insert
    update
    delete
    sendSms
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            resultType = gparam.get('resultType')
            notiGrpType = gparam.get('notiGrpType')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')

            sql = ''' SELECT t.anoti_sms_hist_pk, t.alarm_noti_grp_pk, ang.noti_grp_nm
		       , ngt.code_nm as noti_grp_type_nm, t.sms_content
		       , t.sms_sndr_no, t.sms_rcvr_no, t.sms_rcvr_id
		       , t.result_type as result_type_cd, rt.code_nm as result_type_nm
		       , t.send_ts, t.send_rmk, t.error_cnt
		       , t.insert_ts, t.inserter_id, cu."Name" as inserter_nm
		       , t.update_ts, t.updater_id, uu."Name" as updater_nm
		       , t.factory_pk 
		    from cm_anoti_sms_hist t
		    inner join cm_alarm_noti_grp ang ON ang.alarm_noti_grp_pk = t.alarm_noti_grp_pk
		    inner join cm_base_code ngt on ngt.code_cd = ang.noti_grp_type 
		    and ngt.code_grp_cd = 'NOTI_GRP_TYPE'
		    left outer join cm_base_code rt on rt.code_cd = t.result_type 
		    and rt.code_grp_cd = 'NOTI_RESULT_TYPE'
		    left outer join user_profile cu on cu."User_id" = t.inserter_id
            left outer join user_profile uu on uu."User_id" = t.updater_id
    	    where 1 = 1
            '''
            if factory_id > 0:
                sql += ''' and t.factory_pk = %(factory_pk)s
                '''
            if resultType:
                sql += ''' and t.result_type = %(resultType)s
                '''
            if notiGrpType:
                sql += ''' and ang.noti_grp_type = %(notiGrpType)s
                '''
            if startDate and endDate:
                sql += ''' and (date(t.insert_ts) between to_date(%(startDate)s, 'YYYY-MM-DD')
	    			AND to_date(%(endDate)s, 'YYYY-MM-DD'))
                '''

            dc = {}
            dc['resultType'] = resultType
            dc['notiGrpType'] = notiGrpType
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            anotiSmsHistPk = CommonUtil.try_int( gparam.get('anotiSmsHistPk') )

            sql = ''' SELECT t.anoti_sms_hist_pk, t.alarm_noti_grp_pk, ang.noti_grp_nm
		       , ngt.code_nm as noti_grp_type_nm, t.sms_content
		       , t.sms_sndr_no, t.sms_rcvr_no, t.sms_rcvr_id
		       , t.result_type as result_type_cd, rt.code_nm as result_type_nm
		       , t.send_ts, t.send_rmk, t.error_cnt
		       , t.insert_ts, t.inserter_id, cu."Name" as inserter_nm
		       , t.update_ts, t.updater_id, uu."Name" as updater_nm
		       , t.factory_pk 
		    from cm_anoti_sms_hist t
		    inner join cm_alarm_noti_grp ang ON ang.alarm_noti_grp_pk = t.alarm_noti_grp_pk
		    inner join cm_base_code ngt on ngt.code_cd = ang.noti_grp_type 
		    and ngt.code_grp_cd = 'NOTI_GRP_TYPE'
		    left outer join cm_base_code rt on rt.code_cd = t.result_type 
		    and rt.code_grp_cd = 'NOTI_RESULT_TYPE'
		    left outer join user_profile cu on cu."User_id" = t.inserter_id
            left outer join user_profile uu on uu."User_id" = t.updater_id
    	    where 1 = 1
            AND t.anoti_sms_hist_pk = %(anotiSmsHistPk)s
            '''

            dc = {}
            dc['anotiSmsHistPk'] = anotiSmsHistPk

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'update']:
            anotiSmsHistPk = CommonUtil.try_int(posparam.get('anotiSmsHistPk'))
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            #mailTitle = posparam.get('mailTitle')
            smsContent = posparam.get('smsContent')
            smsSndrNo = posparam.get('smsSndrNo')
            smsRcvrNo = posparam.get('smsRcvrNo')
            smsRcvrId = posparam.get('smsRcvrId')
            resultTypeCd = posparam.get('resultTypeCd')
            sendTs = posparam.get('sendTs')
            sendRmk = posparam.get('sendRmk')
            errorCnt = posparam.get('errorCnt')

            if action == 'update':
                c = CmAnotiSmsHist.objects.get(id=anotiSmsHistPk)
            else:
                c = CmAnotiSmsHist()

            c.CmAlarmNotiGroup_id = alarmNotiGrpPk
            #c.MailTitle = smsContent
            c.SmsContent = smsContent
            c.SmsSndrNo = smsSndrNo
            c.SmsRcvrNo = smsRcvrNo
            c.SmsRcvrId = smsRcvrId
            c.ResultType = resultTypeCd
            c.SendTs = sendTs
            c.SendRmk = sendRmk
            c.ErrorCnt = errorCnt
            c.Factory_id = factory_id
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알림SMS이력의 정보가 수정되었습니다.'}

        elif action == 'delete':
            anotiSmsHistPk = CommonUtil.try_int(posparam.get('anotiSmsHistPk'))
            #if not findDeletableAlarmNotiGroup(anotiSmsHistPk):
            CmAnotiSmsHist.objects.filter(id=anotiSmsHistPk).delete()

            items = {'success': True}

        elif action == 'sendSms':
            anotiSmsHistPk = CommonUtil.try_int(posparam.get('anotiSmsHistPk'))
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            contents = posparam.get('contents')
            userMail = posparam.get('userMail')
            #currLoginId = posparam.get('currLoginId')
            #currUserNm = posparam.get('currUserNm')
            userId = user.id
            currLoginId = user.id
            currUserNm = user.username

            sql = ''' INSERT INTO cm_anoti_sms_hist( alarm_noti_grp_pk
			, sms_content, sms_sndr_no, sms_rcvr_no, sms_rcvr_id
            , result_type, factory_pk
            , insert_ts, inserter_id, inserter_nm
            )
			select ang.alarm_noti_grp_pk
				, substring(%(contents)s), 1, 4000) as sms_content
				, ang.sms_sndr_no, %(userMail)s as sms_rcvr_no, %(userId)s as sms_rcvr_id
				, %(resultType)s, %(factory_pk)s, current_timestamp
                , %(currLoginId)s as inserter_id, %(currUserNm)s as inserter_nm
			from cm_alarm_noti_grp ang
			where ang.noti_grp_type = %(notiGrpType)s
			and ang.mail_snd_yn = 'Y'
            '''
            dc = {}
            dc['contents'] = contents
            dc['userId'] = userId
            dc['userMail'] = userMail
            dc['resultType'] = resultType
            dc['currLoginId'] = currLoginId
            dc['currUserNm'] = currUserNm
            dc['factory_pk'] = factory_id

            ret = DbUtil.execute(sql, dc)

            return {'success': True, 'message': ''}

    except Exception as ex:
        source = 'kmms/anoti_sms_hist : action-{}'.format(action)
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