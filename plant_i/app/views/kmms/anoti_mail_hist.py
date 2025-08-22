from re import A
from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmAnotiMailHist

def anoti_mail_hist(context):
    '''
    api/kmms/anoti_mail_hist    알림메일이력
    김태영 

    findAll
    findOne
    insert
    update
    delete
    insertPasswordTemp
    sendMail
    findMailToSend
    updateFail
    updateSuccess
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == ['findAll']:
            resultType = gparam.get('resultType')
            notiGrpType = gparam.get('notiGrpType')
            startDate = gparam.get('startDate')
            endDate = gparam.get('endDate')

            sql = ''' SELECT t.anoti_mail_hist_pk, t.alarm_noti_grp_pk, ang.noti_grp_nm
		    , ngt.code_nm as noti_grp_type_nm
		    , t.mail_title, t.mail_content, t.mail_sndr_addr, t.mail_rcvr_addr, t.mail_rcvr_id
		    , t.result_type as result_type_cd, rt.code_nm as result_type_nm
		    , t.send_ts, t.send_rmk, t.error_cnt
		    , t.insert_ts, t.inserter_id, cu."Name" as inserter_nm
            , t.update_ts, t.updater_id, uu."Name" as updater_nm
            , t.factory_pk
		    --, t.cc_mail_addr
		    from cm_anoti_mail_hist t
		    inner join cm_alarm_noti_grp ang ON ang.alarm_noti_grp_pk = t.alarm_noti_grp_pk
		    inner join cm_base_code ngt on ngt.code_cd  = ang.noti_grp_type
            and ngt.code_grp_cd = 'NOTI_GRP_TYPE'
		    left join cm_base_code rt on rt.code_cd = t.result_type 
            and rt.code_grp_cd = 'NOTI_RESULT_TYPE'
            left join user_profile cu on t.inserter_id = cu."User_id"
            left join user_profile uu on t.updater_id = uu."User_id"
    	    where 1 = 1
            '''
            # if factory_id > 0:
            #     sql += ''' and t.factory_pk = %(factory_pk)s
            #     '''
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
            anotiMailHistPk = CommonUtil.try_int( gparam.get('anotiMailHistPk') )

            sql = ''' SELECT t.anoti_mail_hist_pk, t.alarm_noti_grp_pk, ang.noti_grp_nm
		    , ngt.code_nm as noti_grp_type_nm
		    , t.mail_title, t.mail_content, t.mail_sndr_addr, t.mail_rcvr_addr, t.mail_rcvr_id
		    , t.result_type as result_type_cd, rt.code_nm as result_type_nm
		    , t.send_ts, t.send_rmk, t.error_cnt
		    , t.insert_ts, t.inserter_id, cu."Name" as inserter_nm
            , t.update_ts, t.updater_id, uu."Name" as updater_nm
            , t.factory_pk
		    --, t.cc_mail_addr
		    from cm_anoti_mail_hist t
		    inner join cm_alarm_noti_grp ang ON ang.alarm_noti_grp_pk = t.alarm_noti_grp_pk
		    inner join cm_base_code ngt on ngt.code_cd  = ang.noti_grp_type
            and ngt.code_grp_cd = 'NOTI_GRP_TYPE'
		    left join cm_base_code rt on rt.code_cd = t.result_type 
            and rt.code_grp_cd = 'NOTI_RESULT_TYPE'
            left join user_profile cu on t.inserter_id = cu."User_id"
            left join user_profile uu on t.updater_id = uu."User_id"
    	    where 1 = 1
            AND t.anoti_mail_hist_pk = %(anotiMailHistPk)s
            '''

            dc = {}
            dc['anotiMailHistPk'] = anotiMailHistPk

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'update']:
            anotiMailHistPk = CommonUtil.try_int(posparam.get('anotiMailHistPk'))
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            mailTitle = posparam.get('mailTitle')
            mailContent = posparam.get('mailContent')
            mailSndrAddr = posparam.get('mailSndrAddr')
            mailRcvrAddr = posparam.get('mailRcvrAddr')
            mailRcvrId = posparam.get('mailRcvrId')
            resultTypeCd = posparam.get('resultTypeCd')
            sendTs = posparam.get('sendTs')
            sendRmk = posparam.get('sendRmk')
            errorCnt = posparam.get('errorCnt')

            if action == 'update':
                c = CmAnotiMailHist.objects.get(id=anotiMailHistPk)
            else:
                c = CmAnotiMailHist()

            c.CmAlarmNotiGroup_id = alarmNotiGrpPk
            c.MailTitle = mailTitle
            c.MailContent = mailContent
            c.MailSndrAddr = mailSndrAddr
            c.MailRcvrAddr = mailRcvrAddr
            c.MailRcvrId = mailRcvrId
            c.ResultType = resultTypeCd
            c.SendTs = sendTs
            c.SendRmk = sendRmk
            c.ErrorCnt = errorCnt
            c.Factory_id = factory_id
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '알림메일이력의 정보가 수정되었습니다.'}

        elif action == 'delete':
            anotiMailHistPk = CommonUtil.try_int(posparam.get('anotiMailHistPk'))
            #if not findDeletableAlarmNotiGroup(anotiMailHistPk):
            CmAnotiMailHist.objects.filter(id=anotiMailHistPk).delete()

            items = {'success': True}

        elif action == 'insertPasswordTemp':
            anotiMailHistPk = CommonUtil.try_int(posparam.get('anotiMailHistPk'))
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            contents = posparam.get('contents')
            userMail = posparam.get('userMail')
            userLoginId = posparam.get('userLoginId')
            LoginId = user.id
            userLoginId = user.id

            sql = ''' INSERT INTO cm_anoti_mail_hist(alarm_noti_grp_pk
			, mail_title, mail_content, mail_sndr_addr, mail_rcvr_addr, mail_rcvr_id
			, result_type, factory_pk, insert_ts, inserter_id)
			select ang.alarm_noti_grp_pk
				, ang.mail_title
				, substring(replace(replace(ang.mail_content, '@contents', %(contents)s), '@loginid', %(userLoginId)s), 1, 4000)
				, ang.mail_sndr_addr, %(userMail)s, %(userLoginId)s
				, 'W', %(factory_pk)s, current_timestamp, %(LoginId)s
			from cm_alarm_noti_grp ang
			where ang.noti_grp_type = 'NGT-D01'
			and ang.mail_snd_yn = 'Y'
            '''
            dc = {}
            dc['contents'] = contents
            dc['userId'] = userId
            dc['userMail'] = userMail
            dc['LoginId'] = LoginId
            dc['factory_pk'] = factory_id

            ret = DbUtil.execute(sql, dc)

            return {'success': True, 'message': ''}

        elif action == 'sendMail':
            anotiMailHistPk = CommonUtil.try_int(posparam.get('anotiMailHistPk'))
            alarmNotiGrpPk = CommonUtil.try_int(posparam.get('alarmNotiGrpPk'))
            contents = posparam.get('contents')
            userMail = posparam.get('userMail')
            userLoginId = posparam.get('userLoginId')
            resultType = posparam.get('resultType')
            ccMailAddr = posparam.get('ccMailAddr')
            notiGrpType = posparam.get('notiGrpType')
            currLoginId = user.id
            userId = user.id

            if not userMail:
                return {'success': False, 'message': ''}

            sql = ''' INSERT INTO cm_anoti_mail_hist(alarm_noti_grp_pk
			, mail_title, mail_content, mail_sndr_addr, mail_rcvr_addr, mail_rcvr_id
			, result_type, factory_pk, insert_ts, inserter_id
           -- , cc_mail_addr
            )
			select ang.alarm_noti_grp_pk
			, ang.mail_title
			, %(contents)s
			, ang.mail_sndr_addr, %(userMail)s, %(userId)s
			, '%(resultType)s, %(factory_pk)s, current_timestamp, %(currLoginId)s
            --, %(ccMailAddr)s
			from cm_alarm_noti_grp ang
			where ang.noti_grp_type = %(notiGrpType)s
			and ang.mail_snd_yn = 'Y'
            '''
            dc = {}
            dc['contents'] = contents
            dc['userId'] = userId
            dc['userMail'] = userMail
            dc['currLoginId'] = currLoginId
            dc['resultType'] = resultType
            dc['ccMailAddr'] = ccMailAddr
            dc['notiGrpType'] = notiGrpType
            dc['factory_pk'] = factory_id

            ret = DbUtil.execute(sql, dc)

            return {'success': True, 'message': ''}


        elif action == 'findMailToSend']:

            sql = ''' SELECT t.anoti_mail_hist_pk, t.alarm_noti_grp_pk, ang.noti_grp_nm
		    , ngt.code_nm as noti_grp_type_nm
		    , t.mail_title, t.mail_content, t.mail_sndr_addr, t.mail_rcvr_addr, t.mail_rcvr_id
		    , t.result_type as result_type_cd, rt.code_nm as result_type_nm
		    , t.send_ts, t.send_rmk, t.error_cnt
		    , t.insert_ts, t.inserter_id, cu."Name" as inserter_nm
            , t.update_ts, t.updater_id, uu."Name" as updater_nm
            , t.factory_pk
		    --, t.cc_mail_addr
		    from cm_anoti_mail_hist t
		    inner join cm_alarm_noti_grp ang ON ang.alarm_noti_grp_pk = t.alarm_noti_grp_pk
		    inner join cm_base_code ngt on ngt.code_cd  = ang.noti_grp_type
            and ngt.code_grp_cd = 'NOTI_GRP_TYPE'
		    left join cm_base_code rt on rt.code_cd = t.result_type 
            and rt.code_grp_cd = 'NOTI_RESULT_TYPE'
            left join user_profile cu on t.inserter_id = cu."User_id"
            left join user_profile uu on t.updater_id = uu."User_id"
    	    where 1 = 1

            AND ( t.result_type = 'W'
		    	OR ( t.result_type in ('F', 'R') AND t.error_cnt <= 5)
	    	)
            '''

            # -- and t.factory_pk = %(factory_pk)s
            dc = {}
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)

        elif action == 'updateFail':
            anotiMailHistPk = CommonUtil.try_int(posparam.get('anotiMailHistPk'))
            resultTypeCd = posparam.get('resultTypeCd')
            sendRmk = posparam.get('sendRmk')

            c = CmAnotiMailHist.objects.get(id=anotiMailHistPk)
            c.ResultType = resultTypeCd
            c.SendRmk = sendRmk
            c.ErrorCnt = c.ErrorCnt + 1 if c.ErrorCnt > 0 else 1
            c.Factory_id = factory_id
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': ''}

        elif action == 'updateSuccess':
            anotiMailHistPk = CommonUtil.try_int(posparam.get('anotiMailHistPk'))
            resultTypeCd = posparam.get('resultTypeCd')

            c = CmAnotiMailHist.objects.get(id=anotiMailHistPk)
            c.ResultType = resultTypeCd
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': ''}

    except Exception as ex:
        source = 'kmms/anoti_mail_hist : action-{}'.format(action)
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