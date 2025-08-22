from domain.services.date import DateUtil
from domain.services.logging import LogWriter
from domain.services.interface.mounter import IFFujiMounterService
from domain.services.sql import DbUtil


def mounter(context):
    '''
    /api/interface/mounter
    '''

    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    result = {'success' : True, 'message' : ''}
    action = gparam.get('action')
    source = f'/api/interface/mounter?{action}'

    try:
        if action=="raw_data_pickup_rate":

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"
            equ_cd= gparam.get('equ_cd')
            item_per_page = gparam.get('item_per_page', 50)
            current_page = gparam.get('current_page', 1)

            limit = int(item_per_page)
            offset = limit *(int(current_page)-1)

            dic_param = { 'start_dt' : start_dt, "end_dt" : end_dt , "equ_cd" : equ_cd, "limit" : limit, "offset" : offset}
            count_sql = '''
            select 
            count(*) as total_count from 
            if_mnt_pickup_rate 
            where 1=1 
            and data_date between %(start_dt)s and %(end_dt)s
            '''
     

            sql='''
            select
            imfr.id
            , imfr.job
            , imfr.equ_cd
            , imfr.machine
            , imfr."position"
            , imfr."part_num"
            , imfr.fidl
            , imfr.pickup
            , imfr.no_pickup 
            , imfr."usage"
            , imfr.reject
            , imfr.error
            , imfr.dislodge
            , imfr.rescan
            , imfr.lcr
            , imfr.pickup_ratio
            , imfr.reject_ratio
            , imfr.error_ratio
            , imfr.dislodge_ratio 
            , imfr.success_ratio
            , to_char(imfr.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_date
            from if_mnt_pickup_rate imfr
            where imfr.data_date between %(start_dt)s and %(end_dt)s
            '''
            if equ_cd:
                sql+='''
                and  imfr.equ_cd= %(equ_cd)s
                '''
                # count query 반영
                count_sql+='''
                and equ_cd= %(equ_cd)s
                '''
            sql+='''
            order by imfr.data_date desc, imfr.machine, imfr."position"
            '''

            if limit:
                sql+='''
                limit %(limit)s
                offset %(offset)s 
                '''

            data = DbUtil.get_rows(sql, dic_param)
            dic_count = DbUtil.get_row(count_sql, dic_param)
            result['success'] = True
            result["data"] = data
            result["total_count"] = dic_count.get("total_count")
   
        elif action=="test":
           service = IFFujiMounterService()
           count = service.test()
           result['success'] = True
           result["data"] = count

        else:
            raise Exception("잘못된 호출")


    except Exception as ex:

        result['success'] = False
        result['message'] = str(ex)
        LogWriter.add_dblog('error', source, ex)

    return result