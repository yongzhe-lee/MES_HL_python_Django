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
        if action=="read":

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"
            equ_id= gparam.get('equ_id')

            dic_param = { 'start_dt' : start_dt, "end_dt" : end_dt , "equ_id" : equ_id}

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
            left join equ e on e."Code" = imfr.equ_cd
            where imfr.data_date between %(start_dt)s and %(end_dt)s
            '''
            if equ_id:
                sql+='''
                and e.id = %(equ_id)s
                '''
            sql+='''
            order by imfr.data_date desc, imfr.machine, imfr."position"            
            '''

            data = DbUtil.get_rows(sql, dic_param)
            result['success'] = True
            result["data"] = data

   
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