import os, json
from domain.services.date import DateUtil
from domain.services.sql import DbUtil

def qms(context):
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    result = {'success' : True, 'message' : ''}
    action = gparam.get('action')

    try:
        if action=="read":
            start_dt = gparam.get('start')
            end_dt = gparam.get('end')
            keyword = gparam.get('keyword')

            dic_param = {'start_dt' : start_dt, 'end_dt': end_dt,  "keyword":keyword}
            sql ='''
                select 
                 qis_pk, a_date, o_date, w_shift, step_class
                , line_cd, mat_cd, serial_no, hlk_part_no, de_proc_cd
                , oc_prod_cd, imput_cate, defect_qty, defect_type1, defect_type2, worker_name
                , remark, init_result, complete_date, final_result, final_remark
                , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
                , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
                from if_qms_defect
                where 1=1
            '''

            if keyword:
                sql+='''
                and upper(mat_cd) like concat('%%',upper(%(keyword)s),'%%')
                '''

            if start_dt:
                sql+='''
                and o_date between %(start_dt)s and %(end_dt)s
                order by o_date desc
                '''

            items = DbUtil.get_rows(sql, dic_param)
            result['items'] = items    

    except Exception as e:
        result['success'] = False
        result['message'] = str(e)


    return result