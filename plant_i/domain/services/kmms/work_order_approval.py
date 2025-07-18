from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class WorkOrderApprovalService():

	def __init__(self):
		return

	# 작업요청 승인
	def updateWoRequest(self, workOrderPk, acceptUserPk, acceptUserNm):
		dic_param = {'workOrderPk': workOrderPk, 'acceptUserPk': acceptUserPk, 'acceptUserNm': acceptUserNm}
		sql = '''
			/* execute [mig-dept-mapper.xml] */
			CALL cm_prc_wo_request(%(workOrderPk)s, %(acceptUserPk)s, %(acceptUserNm)s);
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderApprovalService.updateWoRequest', ex)
			raise ex

	# 작업지시 승인
	def updateWoApproval(self, workOrderPk, acceptUserPk, acceptUserNm):
		dic_param = {'workOrderPk': workOrderPk, 'acceptUserPk': acceptUserPk, 'acceptUserNm': acceptUserNm}
		sql = '''
			/* execute [mig-dept-mapper.xml] */
			CALL cm_prc_wo_approval(%(workOrderPk)s, %(acceptUserPk)s, %(acceptUserNm)s);
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderApprovalService.updateWoApproval', ex)
			raise ex

	# 작업요청 반려
	def updateWoRejectReq(self, workOrderPk, rejectUserPk, rejectUserNm, rejectReason):
		dic_param = {'workOrderPk': workOrderPk, 'rejectUserPk': rejectUserPk, 'rejectUserNm': rejectUserNm, 'rejectReason': rejectReason}
		sql = '''
			/* execute [mig-dept-mapper.xml] */
			CALL cm_prc_wo_reject_req(%(workOrderPk)s, %(rejectUserPk)s, %(rejectUserNm)s, %(rejectReason)s);
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderApprovalService.updateWoApproval', ex)
			raise ex

	# 작업요청 일괄 승인 (bulk)
	def updateWoRequestBulk(self, workOrderPks, acceptUserPk, acceptUserNm):
		dic_param = {'workOrderPks': workOrderPks, 'acceptUserPk': acceptUserPk, 'acceptUserNm': acceptUserNm}
		sql = '''
			CALL cm_prc_wo_request_bulk(%(workOrderPks)s, %(acceptUserPk)s, %(acceptUserNm)s);
		'''
		try:
			DbUtil.execute(sql, dic_param)
		except Exception as ex:
			LogWriter.add_dblog('error', 'WorkOrderApprovalService.updateWoRequestBulk', ex)
			raise ex
