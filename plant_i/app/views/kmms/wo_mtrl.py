from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmWoMtrl

def wo_mtrl(context):
    '''
    api/kmms/wo_mtrl    작업지시 자재
    김태영 

    findAll 전체목록조회
    findWorkOrdersByMtrl 자재를 참조하고 있는 작업지시 목록
    insertBatch
    delete
    insertByMtrlInout
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            workOrderPk = gparam.get('workOrderPk')

            sql = ''' select t.work_order_pk, wo.work_order_no
					, wo.work_title	, t.mtrl_pk
					, m.mtrl_cd, m.mtrl_nm
					, t.plan_amt, t.a_amt as amtrl_amt, t.b_amt as bmtrl_amt, t.unit_price
					, t.loc_cd, t.own_dept_cd
					, t.ab_grade
					, (case when t.loc_cd is not null and t.ab_grade is null and t.a_amt = 0 and t.b_amt > 0 then 'AB_GRADE_B'
							when t.loc_cd is not null and t.ab_grade is null and t.a_amt > 0 and t.b_amt = 0 then 'AB_GRADE_A'
							else t.ab_grade end ) as ab_grade_cd
					, sum(case when pl.pinv_loc_status = 'PINV_EXEC' then 1 else 0 end) as pinv_loc_count
			from cm_wo_mtrl t
			inner join cm_work_order wo on wo.work_order_pk = t.work_order_pk
			inner join cm_material m on m.mtrl_pk = t.mtrl_pk
			left join cm_pinv_loc_mtrl plm on plm.mtrl_cd = m.mtrl_cd
			left join cm_pinv_loc pl on pl.pinv_loc_pk = plm.pinv_loc_pk
			WHERE 1 = 1
			AND t.work_order_pk =  %(workOrderPk)s
			group by t.work_order_pk, wo.work_order_no, wo.work_title
			, t.mtrl_pk, m.mtrl_cd, m.mtrl_nm
			, t.plan_amt, t.a_amt, t.b_amt
			, t.unit_price, t.loc_cd, t.own_dept_cd, t.ab_grade
            '''

            dc = {}
            dc['workOrderPk'] = workOrderPk

            items = DbUtil.get_rows(sql, dc)
 
        elif action == 'findWorkOrdersByMtrl':
            workOrderPk = gparam.get('workOrderPk')
            workOrderPk = CommonUtil.try_int(workOrderPk)
            mtrlPk = gparam.get('mtrlPk')
            mtrlPk = CommonUtil.try_int(mtrlPk)
            woStatusEx = gparam.get('woStatusEx')
            woStatusEx2 = CommonUtil.convert_quotation_mark_string(woStatusEx)

            sql = ''' select t.work_order_pk, wo.work_order_no
				, wo.work_title, coalesce(woa.rqst_dt, wo.start_dt) as rqst_dt
				, d."Name" as dept_nm, rd."Name" as rqst_dept_nm
				, mt.code_nm as maint_type_nm, mt.code_cd as maint_type_cd
				, ws.code_cd as wo_status_cd, ws.code_nm as wo_status_nm
				, wo.plan_start_dt, wo.plan_end_dt
				, wo.start_dt, wo.end_dt, wo.want_dt
				, e.equip_cd, e.equip_nm, l.loc_nm
				, fn_user_nm(wcu."Name" , 'N') as rqst_user_nm
				, wo.req_info, wo.wo_type
				, wo.rqst_insp_yn, wo.rqst_dpr_yn, t.loc_cd, t.own_dept_cd, t.ab_grade
				, (case when t.loc_cd is not null and t.ab_grade is null and t.a_amt = 0 and t.b_amt > 0 then 'AB_GRADE_B'
						when t.loc_cd is not null and t.ab_grade is null and t.a_amt > 0 and t.b_amt = 0 then 'AB_GRADE_A'
						else t.ab_grade end ) as ab_grade_cd
			from cm_wo_mtrl t
			inner join cm_work_order wo on t.work_order_pk = wo.work_order_pk
			inner join cm_material m on t.mtrl_pk = m.mtrl_pk
			inner join cm_work_order_approval woa on wo.work_order_approval_pk = woa.work_order_approval_pk
			inner join cm_base_code mt on wo.maint_type_cd = mt.code_cd 
			and mt.code_grp_cd = 'MAINT_TYPE'
			inner join cm_base_code ws on wo.wo_status = ws.code_cd 
			and ws.code_grp_cd = 'WO_STATUS'
			inner join cm_equipment e on wo.equip_pk = e.equip_pk
			inner join cm_location l on e.loc_pk = l.loc_pk
			left outer join dept d on d.id = wo.dept_pk 
			left outer join dept rd on rd.id = wo.req_dept_pk 
			left outer join user_profile wcu on wcu."User_id" = wo.work_charger_pk  
			where wo.factory_pk = 1
            '''
            if workOrderPk:
                sql += ''' and t.work_order_pk = %(workOrderPk)s
                ''' 
            if mtrlPk:
                sql += ''' and t.mtrl_pk = %(mtrlPk)s
                ''' 
            if woStatusEx:
                sql += ''' and wo.wo_status not in ( ''' + woStatusEx2 + ''')
                ''' 
            dc = {}
            dc['workOrderPk'] = workOrderPk
            dc['mtrlPk'] = mtrlPk
            #dc['woStatusEx'] = woStatusEx

            items = DbUtil.get_rows(sql, dc)

        elif action == 'insertBatch':
            Q = posparam.get('Q')

            for item in Q:
                c = CmWoMtrl()
                c.CmWorkOrder_id = item['workOrderPk']
                c.EmpPk = item['userPk']
                c.CmMaterial_id = item['mtrlPk']
                c.UnitPrice = item['unitPrice']
                c.LocCode = item['locCd']
                c.OwnDeptCode = item['ownDeptCd']
                c.AbGrade = item['abGradeCd']
                c.PlanAmt = item['planAmt']
                c.AAmt = item['amtrlAmt']
                c.BAmt = item['bmtrlAmt']
                c.set_audit(user)
                c.save()

            return {'success': True, 'message': '작업지시 자재 데이터가 등록되었습니다.'}


        elif action == 'delete':
            workOrderPk = CommonUtil.try_int(posparam.get('workOrderPk'))
            q = CmWoMtrl.objects.filter(CmWorkOrder_id=workOrderPk)
            q.delete()

            items = {'success': True}
    
        elif action == 'insertByMtrlInout':
            workOrderPk = posparam.get('workOrderPk')
            mtrlPk = posparam.get('mtrlPk')
            aAmt = posparam.get('aAmt')
            unitPrice = posparam.get('unitPrice')
            locCd = posparam.get('locCd')
            ownDeptCd = posparam.get('ownDeptCd')
            abGrade = posparam.get('abGrade')

            q = CmWoMtrl.objects.filter(CmWorkOrder_id=workOrderPk)
            q = q.filter(CmMaterial_id=mtrlPk)
            q = q.filter(UnitPrice=unitPrice)
            q = q.filter(LocCode=locCd)
            q = q.filter(OwnDeptCode=ownDeptCd)
            q = q.filter(AbGrade=abGrade)
            c = q.first()
            if c:
                c.AAmt = aAmt
                c.save()
            else:
                c = CmWoMtrl()
                c.CmWorkOrder_id = workOrderPk
                c.EmpPk = item['userPk']
                c.CmMaterial_id = mtrlPk
                c.UnitPrice = unitPrice
                c.LocCode = locCd
                c.OwnDeptCode = ownDeptCd
                c.AbGrade = abGrade
                c.PlanAmt = 0
                c.AAmt = aAmt
                c.BAmt = 0
                c.set_audit(user)
                c.save()

            return {'success': True, 'message': '작업지시 자재 데이터가 등록되었습니다.'}


    except Exception as ex:
        source = 'kmms/wo_mtrl : action-{}'.format(action)
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