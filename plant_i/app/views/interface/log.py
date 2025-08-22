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
            aa.id
            , aa.task,  aa."method"
            , aa.api_param, aa.contents
            , aa.rev_no
            , aa.success_yn
            , aa.sec_taken
            , to_char(aa.log_date, 'yyyy-mm-dd hh24:mi:ss') as log_date
            , sc."Value" as task_name
            , up."Name" as user_name
            from if_log aa
            left join sys_code sc on sc."CodeType"='if_type' and sc."Code"=aa.task
            left join user_profile up on up."User_id" =aa._creater_id
            where 1=1
            and log_date between %(start_dt)s and %(end_dt)s
            order by log_date desc
            '''

            items = DbUtil.get_rows(sql, dic_param)
            result = {'success': True, 'items': items, 'message': 'Data retrieved successfully.'}

    except Exception as e:
        result = {'success': False, 'message': str(e)}


    return result