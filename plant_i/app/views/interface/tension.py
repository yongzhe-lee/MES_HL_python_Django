from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

def tension(context):

    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', None)
    source  = f'/api/tension?action={action}'
    result = {'success' : False}
    try:
        if action == 'read':

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"

            line_id = gparam.get('line_id', None)
            keyword = gparam.get('keyword')

            dic_param = {'start_dt': start_dt, 'end_dt':end_dt, 'line_id':line_id, 'keyword':keyword}

            sql='''
            select 
            tcr.id
            , l."Name" as line_nm
            , pp.plan_date
            , pp.mat_cd
            ,tcr.data_date 
            ,tcr.barcode
            ,tcr.tension_value1
            ,tcr.tension_value2
            ,tcr.tension_value3
            ,tcr.tension_value4
            ,tcr.tension_value5
            ,tcr."Result" as result
            , up."Name" as worker_nm
            ,tcr.defect_reason
            , tcr.prod_plan_pk
            from ten_chk_result tcr
            left join if_mes_prod_plan pp on pp.id = tcr.prod_plan_pk
            left join line l on l."Code" = pp.line_cd
            left join auth_user au on au.id = tcr.worker_id
            left join user_profile up on up."User_id" = au.id
            where 1=1
            and
            tcr.data_date between %(start_dt)s and %(end_dt)s
            '''
            if line_id:
                sql+='''
                and l.id=%(line_id)s
                '''

            if keyword:
                sql+='''
                and (upper(tcr.barcode) like  concat('%%', upper( %(keyword)s), '%%'  )
                '''
            sql+='''
            order by tcr.data_date desc
            '''

            items = DbUtil.get_rows(sql, dic_param)
            result['success'] = True
            result['items'] = items

        else:
            raise ValueError("Invalid action")


    except Exception as ex:
        LogWriter.add_dblog('error', source, ex)

    return result