from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.interface.equipment import IFEquipmentResultService

def equ_result(context):
    '''
    /api/interface/equ_result
    '''

    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    result = {'success' : True, 'message' : ''}
    action = gparam.get('action')
    source = f'/api/interface/equ_result?{action}'

    try:
        if action=="read":

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"
            equ_id= gparam.get('equ_id')

            dic_param = { 'start_dt' : start_dt, "end_dt" : end_dt , "equ_id" : equ_id}

            sql='''
            select
            ier.id
            , ier.sn
            , ln."Name" as line_nm
            , ier.sn_new
            , ier.pcb_input
            , ier.pcb_cn
            , ier.pcb_size 
            , ier.pcb_array
            , ier.state
            , ier.is_alarm
            , ier.equ_cd
            , to_char(ier.data_date, 'yyyy-mm-dd hh24:mi:ss') data_date
            , ier.bom_ver
            , ier.mat_cd
            , ier.mat_desc
            , e."Name" as equ_nm
            , m."Name" as mat_nm
            from if_equ_result ier
            left join equ e on e."Code" =ier.equ_cd
            left join line ln on ln.id  = e.line_id 
            left join material m on m."Code"=ier.mat_cd
            where 
            ier.data_date between %(start_dt)s and %(end_dt)s
            '''
            if equ_id:
                sql+='''
                and e.id = %(equ_id)s
                '''
            sql+='''
            order by ier.data_date desc
            '''

            data = DbUtil.get_rows(sql, dic_param)
            result['success'] = True
            result["data"] = data

        elif action=="result_item_list":

            result_id = gparam.get('result_id')
            dic_param = {"result_id": result_id}
            sql='''
            select
            ier.data_date
            , ieri.max_val
            , ieri.min_val
            , ieri.test_item_cd
            , ieri.test_item_val
            , ieri.unit
            , ieri.failcode
            , to_char(ieri."_created", 'yyyy-mm-dd hh24:mi:ss') created
            from if_equ_result ier 
            inner join if_equ_result_item ieri on ieri.rst_id = ier.id
            where ier.id= %(result_id)s
            '''
            data = DbUtil.get_rows(sql, dic_param)
            result['success'] = True
            result["data"] = data

        elif action=="defect_item_list":
            result_id = gparam.get('result_id')
            dic_param = {"result_id": result_id}
            sql='''
            select 
            aa.defect_cd
            ,aa.defect_nm
            , aa.part_no
            , aa.component_nm
            , to_char(aa._created, 'yyyy-mm-dd hh24:mi:ss') created
            from if_equ_result ier 
            inner join if_equ_defect_item aa on aa.rst_id = ier.id
            where ier.id= %(result_id)s
            '''
            data = DbUtil.get_rows(sql, dic_param)
            result['success'] = True
            result["data"] = data

        else:
            raise Exception("잘못된 호출")


    except Exception as ex:
        result['success'] = False
        result['message'] = str(ex)


    return result