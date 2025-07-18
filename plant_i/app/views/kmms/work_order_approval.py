from django import db
from domain.services.kmms.work_order_approval import WorkOrderApprovalService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWorkOrderApproval

def work_order_approval(context):
    '''
    api/kmms/work_order_approval  작업지시 결재
    김태영 

    findOne
    insert
    update
    insertPm    insert와 동일
    insertInspection    insert와 동일
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 
    work_order_approval_service = WorkOrderApprovalService()

    try:
        if action == 'findOne':

            workOrderApprovalPk = CommonUtil.try_int(gparam.get('workOrderApprovalPk'))

            sql = ''' SELECT woa.work_order_approval_pk, woa.wo_status
		    , woa.reg_dt, woa.reg_user_nm, woa.reg_user_pk
		    , woa.rqst_dt, woa.rqst_user_nm , woa.rqst_user_pk
		    , woa.accept_dt, woa.accept_user_nm, woa.accept_user_pk
		    , woa.appr_dt, woa.appr_user_nm, woa.appr_user_pk
		    , woa.cancel_dt, woa.cancel_reason, woa.cancel_user_nm, woa.cancel_user_pk
		    , woa.finish_dt, woa.finish_user_nm, woa.finish_user_pk
		    , woa.reject_dt, woa.reject_reason
		    , woa.reject_user_nm, woa.reject_user_pk
		    , woa.work_finish_dt, woa.work_finish_user_nm, woa.work_finish_user_pk
		    FROM  cm_work_order_approval woa
		    WHERE woa.work_order_approval_pk = %(workOrderApprovalPk)s
            '''

            dc = {}
            dc['workOrderApprovalPk'] = workOrderApprovalPk

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'insertPm','insertInspection','update']:
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))

            woStatusCd = posparam.get('woStatusCd')
            regUserNm = user.username
            regUserPk = user.pk
            rqstUserNm = regUserNm
            rqstUserPk = regUserPk

            rqstDt = posparam.get('rqstDt')
            if rqstDt is None:
                rqstDt = DateUtil.get_current_datetime()

            acceptDt = posparam.get('acceptDt')
            acceptUserNm = posparam.get('acceptUserNm')
            acceptUserPk = CommonUtil.try_int(posparam.get('acceptUserPk'))
            apprDt = posparam.get('apprDt')
            apprUserNm = posparam.get('apprUserNm')
            apprUserPk = CommonUtil.try_int(posparam.get('apprUserPk'))

            thistime = DateUtil.get_current_datetime()
 
            if action in ['insert','insertPm', 'insertInspection']:
                c = CmWorkOrderApproval()
                c.RegDt = thistime
                c.RegUserName = regUserNm
                c.RegUserPk = regUserPk
            else:
                c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            if woStatusCd:
                c.WoStatus = woStatusCd
            c.RqstDt = rqstDt



            c.RqstUserName = rqstUserNm
            c.RqstUserPk = rqstUserPk
            if acceptDt:
                c.AcceptDt = acceptDt
            if acceptUserPk:
                c.AcceptUserName = acceptUserNm
                c.AcceptUserPk = acceptUserPk
            if apprDt:
                c.ApprDt = apprDt
            if apprUserPk:
                c.ApprUserName = apprUserNm
                c.ApprUserPk = apprUserPk
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업지시 결재 정보가 저장되었습니다.', 'workOrderApprovalPk': c.id}

        elif action == 'insertDailyReport':

            woStatusCd = posparam.get('woStatusCd')
            regUserNm = posparam.get('regUserNm')
            regUserPk = CommonUtil.try_int(posparam.get('regUserPk'))
            rqstDt = posparam.get('rqstDt')
            rqstUserNm = posparam.get('rqstUserNm')
            rqstUserPk = CommonUtil.try_int(posparam.get('rqstUserPk'))
            acceptDt = posparam.get('acceptDt')
            acceptUserNm = posparam.get('acceptUserNm')
            acceptUserPk = CommonUtil.try_int(posparam.get('acceptUserPk'))
            apprDt = posparam.get('apprDt')
            apprUserNm = posparam.get('apprUserNm')
            apprUserPk = CommonUtil.try_int(posparam.get('apprUserPk'))
            finishDt = posparam.get('finishDt')
            finishUserPk = CommonUtil.try_int(posparam.get('finishUserPk'))
            finishUserNm = posparam.get('finishUserNm')

            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval()
            c.RegDt = thistime
            c.RegUserName = regUserNm
            c.RegUserPk = regUserPk

            if woStatusCd:
                c.WoStatus = woStatusCd
            c.RqstDt = rqstDt
            c.RqstUserName = rqstUserNm
            c.RqstUserPk = rqstUserPk
            if acceptDt:
                c.AcceptDt = acceptDt
            if acceptUserPk:
                c.AcceptUserName = acceptUserNm
                c.AcceptUserPk = acceptUserPk
            if apprDt:
                c.ApprDt = apprDt
            if apprUserPk:
                c.ApprUserName = apprUserNm
                c.ApprUserPk = apprUserPk
            if finishDt:
                c.WorkFinishDt = finishDt
                c.FinishDt = finishDt
            if finishUserPk:
                c.WorkFinishUserName = finishUserNm
                c.WorkFinishUserPk = finishUserPk
                c.FinishUserName = finishUserNm
                c.FinishUserPk = finishUserPk
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업지시 결재 정보가 저장되었습니다.', 'workOrderApprovalPk': c.id}


        elif action == 'updateAccept':
            ''' 작업요청승인
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))

            acceptDt = posparam.get('acceptDt')
            acceptUserNm = posparam.get('acceptUserNm')
            acceptUserPk = CommonUtil.try_int(posparam.get('acceptUserPk'))

            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c.AcceptDt = thistime
            c.AcceptUserName = acceptUserNm
            c.AcceptUserPk = acceptUserPk

            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업요청이 승인되었습니다.'}

        elif action == 'updateApproval':
            ''' 작업승인
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))

            apprUserNm = posparam.get('apprUserNm')
            apprUserPk = CommonUtil.try_int(posparam.get('apprUserPk'))

            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c,ApprDt = thistime
            c.ApprUserName = apprUserNm
            c.ApprUserPk = apprUserPk

            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업요청이 승인되었습니다.'}

        elif action == 'updateWoRequest':
            ''' 작업요청승인 쿼리처리
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            acceptUserPk = user.pk
            acceptUserNm = user.username
            items = work_order_approval_service.updateWoRequest(workOrderPk, acceptUserPk, acceptUserNm)   
     
            return {'success': True, 'message': '작업요청이 승인되었습니다.'}

        elif action == 'bulkWoRequest':
            ''' 작업요청승인 일괄쿼리처리 '''
            import json
            workOrderPks = posparam.get('workOrderPk')
            if not workOrderPks:
                workOrderPks = posparam.get('workOrderPk[]')
            if isinstance(workOrderPks, str):
                try:
                    workOrderPks = json.loads(workOrderPks)
                except Exception:
                    workOrderPks = [workOrderPks]
            elif not isinstance(workOrderPks, list):
                workOrderPks = [workOrderPks]
            acceptUserPk = user.pk
            acceptUserNm = user.username
            # 서비스 계층에서 배열을 그대로 넘겨 DB 프로시저 호출
            items = work_order_approval_service.updateWoRequestBulk(workOrderPks, acceptUserPk, acceptUserNm)
            return {'success': True, 'message': '작업요청이 승인되었습니다.'}

        elif action == 'updateWoApproval':
            ''' 작업지시승인 쿼리처리
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            acceptUserPk = user.pk
            acceptUserNm = user.username
            items = work_order_approval_service.updateWoApproval(workOrderPk, acceptUserPk, acceptUserNm)   
     
            return {'success': True, 'message': '작업요청이 승인되었습니다.'}

        elif action == 'updateWorkFinish':
            ''' 작업완료
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))

            workFinishUserNm = posparam.get('workFinishUserNm')
            workFinishUserPk = CommonUtil.try_int(posparam.get('workFinishUserPk'))

            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c,WorkFinishDt = thistime
            c.WorkFinishUserName = workFinishUserNm
            c.WorkFinishUserPk = workFinishUserPk

            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업완료 상태로 처리되었습니다.'}

        elif action == 'updateComplete':
            ''' 완료
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))

            finishUserNm = posparam.get('finishUserNm')
            finishUserPk = CommonUtil.try_int(posparam.get('finishUserPk'))

            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c,FinishDt = thistime
            c.FinishUserName = finishUserNm
            c.FinishUserPk = finishUserPk

            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업이 완료상태로 처리되었습니다.'}

        elif action == 'updateRqstDt':
            ''' 요청일 업데이트
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))
            rqstDt = posparam.get('rqstDt')
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c,RqstDt = rqstDt
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '요청일이 변경되었습니다.'}

        elif action == 'updateReject':
            ''' 반려
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))
            rejectUserNm = posparam.get('rejectUserNm')
            rejectUserPk = posparam.get('rejectUserPk')
            rejectReason = posparam.get('rejectReason')
            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c,RejectDt = thistime
            c,RejectUserName = rejectUserNm
            c,RejectUserPk = rejectUserPk
            c,RejectReason = rejectReason
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업지시 결재가 반려되었습니다.'}

        elif action == 'updateRejectReq':
            ''' 반려
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            rejectUserPk = user.pk
            rejectUserNm = user.username
            rejectReason = posparam.get('reject_reason')

            items = work_order_approval_service.updateWoRejectReq(workOrderPk, rejectUserPk, rejectUserNm,rejectReason)

            return {'success': True, 'message': '작업요청 결재가 반려되었습니다.'}

        elif action == 'updateCancel':
            ''' 취소
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))
            cancelUserNm = posparam.get('cancelUserNm')
            cancelUserPk = posparam.get('cancelUserPk')
            cancelReason = posparam.get('cancelReason')
            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c,CancelDt = thistime
            c,CancelUserName = cancelUserNm
            c,CancelUserPk = cancelUserPk
            c,CancelReason = cancelReason
            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업지시결재가 취소되었습니다.'}

    except Exception as ex:
        source = 'kmms/work_order_approval : action-{}'.format(action)
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

