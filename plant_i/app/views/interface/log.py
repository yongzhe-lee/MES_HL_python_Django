from domain.services.sql import DbUtil

def log(context):
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', 'read')

    user  = context.request.user

    source = f'/api/interface/log?action={action}'
    result = {}
    try:
        if action=="read":

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"
            dic_param = { 'start_dt' : start_dt, "end_dt" : end_dt }

            sql='''
            select 
            id, 
            task,
            "method", 
            contents, 
            equ_cd, 
            mat_cd, 
            rev_no, 
            is_success,
            to_char(log_date, 'yyyy-mm-dd hh24:mi:ss') as data_date
            from if_log
            where 1=1
            and log_date between %(start_dt)s and %(end_dt)s
            order by log_date desc
            '''

            items = DbUtil.get_rows(sql, dic_param)
            result = {'success': True, 'items': items, 'message': 'Data retrieved successfully.'}

    except Exception as e:
        result = {'success': False, 'message': str(e)}


    return result