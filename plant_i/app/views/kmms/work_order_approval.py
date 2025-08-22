import json
from django import db
from domain.services.kmms.work_order_approval import WorkOrderApprovalService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmExSupplier, CmJobClass, CmMaterial, CmWoFaultLoc, CmWoLabor, CmWoMtrl, CmWorkOrderApproval, CmWorkOrderSupplier, CmWorkOrder

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
            if not isinstance(workOrderPks, list):
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
            c.WorkFinishDt = thistime
            c.WorkFinishUserName = workFinishUserNm
            c.WorkFinishUserPk = workFinishUserPk

            #c.set_audit(user)
            c.save()

            return {'success': True, 'message': '작업완료 상태로 처리되었습니다.'}

        elif action == 'updateWoFinish':
            ''' 작업완료 쿼리처리
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            tempSave = posparam.get('tempSave', 'N') # 임시저장구분 기본값:  N

            problemCd = posparam.get('problem_cd')
            causeCd = posparam.get('cause_cd')
            remedyCd = posparam.get('remedy_cd')
            projCd = posparam.get('proj_cd')
            workSrcCd = posparam.get('work_src_cd')

            workChargerPk = posparam.get('work_charger_pk')
            planStartDt = posparam.get('start')
            planEndDt = posparam.get('end')
            startDt = posparam.get('start_dt')
            endDt = posparam.get('end_dt')
            workText = posparam.get('reqInfo')
            
            woFaultLoc = posparam.get('woFaultLoc')
            woSupplier = posparam.get('woSupplier')
            woLabor = posparam.get('woLabor')
            woMtrl = posparam.get('woMtrl')
            
            mtrlCost = posparam.get('mtrlCost')
            laborCost = posparam.get('laborCost')
            outsideCost = posparam.get('outsideCost')
            etcCost = posparam.get('etcCost')
            totCost = posparam.get('totCost')

            finishUserPk = user.pk
            finishUserNm = user.username

            cause_cd = posparam.get('cause_cd')
            remedy_cd = posparam.get('remedy_cd')
            try:
                work_order = CmWorkOrder.objects.get(id=workOrderPk)
                work_order.CauseCode = cause_cd
                work_order.RemedyCode = remedy_cd
                work_order.set_audit(user)
                work_order.save()
            except CmWorkOrder.DoesNotExist:
                pass

            #작업내역(전체)
            items = work_order_approval_service.updateWoFinish(workOrderPk, tempSave, problemCd, causeCd, remedyCd, projCd, workSrcCd
                                                               , workChargerPk, planStartDt, planEndDt, startDt, endDt, workText
                                                               , finishUserPk, finishUserNm,mtrlCost,laborCost,outsideCost,etcCost,totCost)
            
            ######################################################
            # region 작업지시 고장위치 정보
            woFaultLocs = []
            if woFaultLoc and isinstance(woFaultLoc, str):    
                    import json as json_module
                    woFaultLocs = json_module.loads(woFaultLoc)
            elif woFaultLoc and isinstance(woFaultLoc, list):    
                woFaultLocs = woFaultLoc

            cm_wo_fault_loc_list = []
            # woFaultLocs 데이터를 CmWoFaultLoc 모델 객체로 변환
            for fault_loc_data in woFaultLocs:    
                insert_dt = fault_loc_data.get('insert_dt')
                if insert_dt:
                    from datetime import datetime
                    insert_dt = datetime.strptime(insert_dt, '%Y-%m-%d') 
                
                cm_wo_fault_loc = CmWoFaultLoc(
                    CmWorkOrder_id=workOrderPk,
                    FaultLocCode=fault_loc_data.get('fault_loc_cd'),    
                    CauseCode=fault_loc_data.get('cause_cd'),
                    FaultLocDesc=fault_loc_data.get('fault_loc_desc'),
                    InserterId=user.pk,
                    InsertDt=insert_dt
                                    )
                cm_wo_fault_loc_list.append(cm_wo_fault_loc)

            # Bulk Insert 전에 workOrderPk 검색조건의 모든 데이터 삭제
            CmWoFaultLoc.objects.filter(CmWorkOrder_id=workOrderPk).delete()
            
            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            if cm_wo_fault_loc_list:
                CmWoFaultLoc.objects.bulk_create(cm_wo_fault_loc_list)
            #endregion
            ######################################################

            ######################################################
            # region 작업지시 외부업체 정보
            woSuppliers = []
            if woSupplier and isinstance(woSupplier, str):    
                    import json as json_module
                    woSuppliers = json_module.loads(woSupplier)
            elif woSupplier and isinstance(woSupplier, list):
                woSuppliers = woSupplier
            cm_work_order_supplier_list = []
            for item in woSuppliers:
                # ex_supplier_pk가 null이 아닌 경우에만 객체 생성
                ex_supplier_pk = item.get('ex_supplier_pk')
                if ex_supplier_pk is not None:
                    # CmExSupplier 인스턴스 가져오기
                    try:
                        ex_supplier_instance = CmExSupplier.objects.get(id=ex_supplier_pk)
                        cm_work_order_supplier = CmWorkOrderSupplier(
                            CmWorkOrder_id=workOrderPk,
                            CmExSupplier=ex_supplier_instance,    
                            Cost=CommonUtil.try_int(item.get('cost')),      
                        )
                        cm_work_order_supplier_list.append(cm_work_order_supplier)
                    except CmExSupplier.DoesNotExist:
                        # ex_supplier_pk가 존재하지 않는 경우 해당 항목을 건너뜀
                        continue

            # Bulk Insert 전에 workOrderPk 검색조건의 모든 데이터 삭제
            CmWorkOrderSupplier.objects.filter(CmWorkOrder_id=workOrderPk).delete()
            
            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            if cm_work_order_supplier_list:
                CmWorkOrderSupplier.objects.bulk_create(cm_work_order_supplier_list)
            #endregion
            ######################################################
            
            ######################################################
            # region 작업지시 인력 정보
            woLabors = []
            if woLabor and isinstance(woLabor, str):    
                    import json as json_module
                    woLabors = json_module.loads(woLabor)
            elif woLabor and isinstance(woLabor, list):
                woLabors = woLabor
            cm_wo_labor_list = []
            for item in woLabors:
                # emp_pk가 null이 아닌 경우에만 객체 생성
                emp_pk = item.get('emp_pk')
                job_class_pk = item.get('job_class_pk')
                
                if emp_pk is not None:
                    
                    job_class_instance = None
                    if job_class_pk is not None:
                        try:
                            job_class_instance = CmJobClass.objects.get(id=job_class_pk)
                        except CmJobClass.DoesNotExist:
                            job_class_instance = None
                    
                    cm_wo_labor = CmWoLabor(
                        CmWorkOrder_id=workOrderPk,
                        CmJobClass=job_class_instance,
                        EmpPk=emp_pk or None,                         
                        LaborPrice=item.get('labor_price'),
                        WorkerNos=item.get('worker_nos'),
                        WorkHr=item.get('work_hr'),
                        RealWorkHr=item.get('real_work_hr'),
                    )
                    cm_wo_labor_list.append(cm_wo_labor)

            # Bulk Insert 전에 workOrderPk 검색조건의 모든 데이터 삭제
            CmWoLabor.objects.filter(CmWorkOrder_id=workOrderPk).delete()
            
            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            if cm_wo_labor_list:
                CmWoLabor.objects.bulk_create(cm_wo_labor_list)            
            #endregion
            ######################################################

            ######################################################
            # region 작업지시 자재 정보
            woMtrls = []
            if woMtrl and isinstance(woMtrl, str):    
                    import json as json_module
                    woMtrls = json_module.loads(woMtrl)
            elif woMtrl and isinstance(woMtrl, list):
                woMtrls = woMtrl
            cm_wo_mtrl_list = []
            for item in woMtrls:
                # mtrl_pk가 null이 아닌 경우에만 객체 생성
                mtrl_pk = item.get('mtrl_pk')
                if mtrl_pk is not None:
                    # CmMaterial 인스턴스 가져오기
                    try:
                        material_instance = CmMaterial.objects.get(id=mtrl_pk)
                        cm_wo_mtrl = CmWoMtrl(
                            CmWorkOrder_id=workOrderPk,
                            CmMaterial=material_instance, 
                            UnitPrice=item.get('unit_price'),
                            AAmt=item.get('a_amt'),
                            BAmt=item.get('b_amt'),
                        )
                        cm_wo_mtrl_list.append(cm_wo_mtrl)
                    except CmMaterial.DoesNotExist:
                        # mtrl_pk가 존재하지 않는 경우 해당 항목을 건너뜀
                        continue

            # Bulk Insert 전에 workOrderPk 검색조건의 모든 데이터 삭제
            CmWoMtrl.objects.filter(CmWorkOrder_id=workOrderPk).delete()
            
            # Bulk Insert 실행 (한 번의 쿼리로 저장)
            if cm_wo_mtrl_list:
                CmWoMtrl.objects.bulk_create(cm_wo_mtrl_list)
            #endregion
            ######################################################

            return {'success': True, 'message': '작업완료 상태로 처리되었습니다.'}

        elif action == 'updateWoFinishPost':
            ''' 사후작업완료 쿼리처리
            '''
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            finishUserPk = user.pk
            finishUserNm = user.username

            #작업내역(전체)

            items = work_order_approval_service.updateWoFinishPost(workOrderPk, finishUserPk, finishUserNm)

            return {'success': True, 'message': '사후작업완료 등록이 완료되었습니다.'}

        elif action == 'updateComplete':
            ''' 완료
            '''
            workOrderApprovalPk = CommonUtil.try_int(posparam.get('workOrderApprovalPk'))

            finishUserNm = posparam.get('finishUserNm')
            finishUserPk = CommonUtil.try_int(posparam.get('finishUserPk'))

            thistime = DateUtil.get_current_datetime()
 
            c = CmWorkOrderApproval.objects.get(id=workOrderApprovalPk)
            c.FinishDt = thistime
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
            c.RqstDt = rqstDt
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
            c.RejectDt = thistime
            c.RejectUserName = rejectUserNm
            c.RejectUserPk = rejectUserPk
            c.RejectReason = rejectReason
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
            c.CancelDt = thistime
            c.CancelUserName = cancelUserNm
            c.CancelUserPk = cancelUserPk
            c.CancelReason = cancelReason
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

