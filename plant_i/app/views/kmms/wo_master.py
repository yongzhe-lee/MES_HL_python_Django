from django.db import transaction
from domain.services.sql import DbUtil
from domain.models.kmms import PreventiveMaintenace
from domain.services.kmms.work_order import WorkOrderService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse


def wo_master(context):
    '''
    /api/kmms/wo_master
    '''
    items = []
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user

    workorder_service = WorkOrderService()

    if action=='read':
        keyword = gparam.get('keyword', None)
        req_dept = gparam.get('req_dept', None)
        _creater_id = user.id
        
        items = workorder_service.get_work_order_list(keyword, req_dept, _creater_id)

    elif action=='detail':
        id = gparam.get('id', None)
        items = WorkOrderService.get_equipment_detail(id)

    elif action=='save':               

        # 기본 정보
        work_order_no = gparam.get('work_order_no', None)
        wo_status = gparam.get('wo_status', None)
        work_title = gparam.get('work_title', None)
        wo_type = gparam.get('wo_type', None)
        maint_type_cd = gparam.get('maint_type_cd', None)
        
        # 요청 정보
        req_info = gparam.get('req_info', None)
        req_file_grp_cd = gparam.get('req_file_grp_cd', None)
        want_dt = gparam.get('want_dt', None)
        
        # 고장 정보
        breakdown_dt = gparam.get('breakdown_dt', None)
        breakdown_hr = gparam.get('breakdown_hr', None)
        problem_cd = gparam.get('problem_cd', None)
        cause_cd = gparam.get('cause_cd', None)
        remedy_cd = gparam.get('remedy_cd', None)
        
        # 일정 정보
        plan_start_dt = gparam.get('plan_start_dt', None)
        plan_end_dt = gparam.get('plan_end_dt', None)
        start_dt = gparam.get('start_dt', None)
        end_dt = gparam.get('end_dt', None)
        
        # 작업 정보
        work_text = gparam.get('work_text', None)
        work_file_grp_cd = gparam.get('work_file_grp_cd', None)
        work_src_cd = gparam.get('work_src_cd', None)
        
        # 비용 정보
        tot_cost = gparam.get('tot_cost', None)
        mtrl_cost = gparam.get('mtrl_cost', None)
        labor_cost = gparam.get('labor_cost', None)
        outsourcing_cost = gparam.get('outsourcing_cost', None)
        etc_cost = gparam.get('etc_cost', None)
        
        # PM 관련 정보
        pm_req_type = gparam.get('pm_req_type', None)
        work_order_sort = gparam.get('work_order_sort', None)
        rqst_insp_yn = gparam.get('rqst_insp_yn', None)
        rqst_dpr_yn = gparam.get('rqst_dpr_yn', None)
        wo_file_grp_cd = gparam.get('wo_file_grp_cd', None)
        
        # AUDIT 정보
        _status = gparam.get('_status', None)
        _created = gparam.get('_created', None)
        _modified = gparam.get('_modified', None)
        _creater_id = gparam.get('_creater_id', None)
        _modifier_id = gparam.get('_modifier_id', None)
        _creater_nm = gparam.get('_creater_nm', None)
        _modifier_nm = gparam.get('_modifier_nm', None)
        
        # 관계 정보
        chk_result_pk = gparam.get('chk_result_pk', None)
        equ_id = gparam.get('equ_id', None)
        pm_pk = gparam.get('pm_pk', None)
        req_dept_id = gparam.get('req_dept_id', None)
        work_charger_id = gparam.get('work_charger_id', None)
        work_dept_id = gparam.get('work_dept_id', None)


        work_order = None
        eh_content = ''
        today = DateUtil.get_today()

        try:
            
            work_order.set_audit(user)

            work_order.save()

            items = {'success': True, 'id': work_order.id}

        except Exception as ex:
            source = 'api/kmms/work_order, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    elif action=='delete':
        try:
            id = posparam.get('id','')
            Equipment.objects.filter(id=id).delete()
            items = {'success': True}

        except Exception as ex:
            source = 'api/definition/equipment, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
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
            #if action == 'delete':
            #    items = {'success':False, 'message': '삭제중 오류가 발생하였습니다.'}
            #    return items
            #raise ex

    # elif action == 'save_photo':
    #     eq_id = posparam.get('eq_id', '')
    #     file_id = posparam.get('file_id',None)
    #     if eq_id:
    #         fileService = FileService()
    #         file_id_list = file_id.split(',')
    #         for id in file_id_list:
    #             fileService.updateDataPk(id, eq_id)

    #         items = {'success' : True}

    return items

def get_work_order_list(context):
    try:
        gparam = context.gparam
        
        sql = '''
        SELECT 
            wo.work_order_no,
            wo.work_title,
            wo.wo_status,
            e.code as equ_code,
            e.name as equ_name,
            d1.name as req_dept_name,
            wo._creater_nm as requester,
            wo._created as req_date,
            wo.want_dt,
            d2.name as work_dept_name,
            u.name as work_charger_name,
            wo.maint_type_cd,
            wo.wo_type,
            wo.req_info,
            wo.breakdown_dt,
            wo.plan_start_dt,
            wo.plan_end_dt,
            wo.start_dt,
            wo.end_dt
        FROM work_order wo
        LEFT JOIN equipment e ON wo.equ_id = e.id
        LEFT JOIN department d1 ON wo.req_dept_id = d1.id
        LEFT JOIN department d2 ON wo.work_dept_id = d2.id
        LEFT JOIN users u ON wo.work_charger_id = u.id
        WHERE 1=1
        '''
        
        dic_param = {}
        
        # 검색 조건 추가
        if gparam.get('start_date'):
            sql += ' AND wo._created >= %(start_date)s'
            dic_param['start_date'] = gparam.get('start_date')
            
        if gparam.get('end_date'):
            sql += ' AND wo._created <= %(end_date)s'
            dic_param['end_date'] = gparam.get('end_date')
            
        sql += ' ORDER BY wo._created DESC'
        
        items = DbUtil.get_rows(sql, dic_param)
        return JsonResponse({'data': items})
        
    except Exception as ex:
        return JsonResponse({'result': 'fail', 'message': str(ex)})