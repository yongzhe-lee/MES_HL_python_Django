from domain.services.date import DateUtil
from domain.services.sql import DbUtil


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
            , ier.sn_new
            , ier.pcb_cn
            , ier.state
            , ier.is_alarm
            , to_char(ier.data_date, 'yyyy-mm-dd hh24:mi:ss') data_date
            , ier.bom_ver
            , ier.mat_cd
            , e."Name" as equ_nm
            ,  m."Name" as mat_nm
            from if_equ_result ier
            left join equ e on e."Code" =ier.equ_cd
            left join material m on m."Code"=ier.mat_cd
            where 1=1 
            and ier.data_date between %(start_dt)s and %(end_dt)s
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

            sql='''
            select
            ier.data_date
            , ieri.max_val
            , ieri.min_val
            , ieri.test_item_cd
            , ieri.test_item_val
            , ieri.unit
            , ieri.failcode
            , ieri."_created"
            from if_equ_result ier 
            inner join if_equ_result_item ieri on ieri.rst_id = ier.id
            where ier= %(result_id)s
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