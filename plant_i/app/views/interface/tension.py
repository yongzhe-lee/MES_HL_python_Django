
from domain.models.smt import TensionCheckResult

from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

def tension(context):

    request = context.request
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', None)
    source  = f'/api/tension?action={action}'
    result = {'success' : False}

    try:
        if action == 'read':

            start_dt = gparam.get('start_dt')
            end_dt = gparam.get('end_dt') + " 23:59:59"
            line_cd = gparam.get('line_cd', None)
            keyword = gparam.get('keyword')

            dic_param = {'start_dt': start_dt, 'end_dt':end_dt, 'line_cd':line_cd, 'keyword':keyword}
            
            sql='''
            select 
            tcr.id as rst_id
            , tcr.line_cd
            , to_char(tcr.data_date ,'yyyy-mm-dd') as data_date
            ,tcr.barcode
            ,tcr.tension_value1
            ,tcr.tension_value2
            ,tcr.tension_value3
            ,tcr.tension_value4
            ,tcr.tension_value5
            ,tcr."Result" as result
            , up."Name" as worker_nm
            ,tcr.defect_reason
            , to_char(tcr._created, 'yyyy-mm-dd hh24:mi:ss') as created
            , to_char(tcr._modified, 'yyyy-mm-dd hh24:mi:ss') as modified
            from ten_chk_result tcr
            left join auth_user au on au.id = tcr.worker_id
            left join user_profile up on up."User_id" = au.id
            where 1=1
            and
            tcr.data_date between %(start_dt)s and %(end_dt)s
            '''
            if line_cd:
                sql+='''
                and tcr.line_cd=%(line_cd)s
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

        elif action=="tension_detail":

            rst_id = gparam.get('rst_id')
            dic_param = {"rst_id" : rst_id}
            sql='''
            select 
            tcr.id as rst_id
            , tcr.line_cd
            , to_char(tcr.data_date ,'yyyy-mm-dd') as data_date
            , tcr.barcode
            , tcr.tension_value1
            , tcr.tension_value2
            , tcr.tension_value3
            , tcr.tension_value4
            , tcr.tension_value5
            , tcr."Result" as result
            , up."Name" as worker_nm
            , tcr.defect_reason
            from ten_chk_result tcr
            left join auth_user au on au.id = tcr.worker_id
            left join user_profile up on up."User_id" = au.id
            where tcr.id = %(rst_id)s
            '''
            data = DbUtil.get_row(sql, dic_param)
            result["success"] = True
            result['data'] = data

        elif action=="save_tension":

            rst_id = posparam.get("rst_id")
            data_date = posparam.get('data_date')
            barcode = posparam.get('barcode')
            line_cd = posparam.get('line_cd')
            tension_value1 = posparam.get("tension_value1")
            tension_value2 = posparam.get("tension_value2")
            tension_value3 = posparam.get("tension_value3")
            tension_value4 = posparam.get("tension_value4")
            tension_value5 = posparam.get("tension_value5")
            txt_result = posparam.get("result")
            defect_reason = posparam.get('defect_reason')


            if tension_value1:
                tension_value1 = CommonUtil.try_decimal(tension_value1);
            if tension_value2:
                tension_value2 = CommonUtil.try_decimal(tension_value2);
            if tension_value3:
                tension_value3 = CommonUtil.try_decimal(tension_value3);
            if tension_value4:
                tension_value4 = CommonUtil.try_decimal(tension_value4);
            if tension_value5:
                tension_value5 = CommonUtil.try_decimal(tension_value5);


            # tension_value 0.4 ~ 0.8 mm , 0.8mm 초과시 이메일 전송
            is_sendmail = False
            tension_values = [tension_value1, tension_value2, tension_value3, tension_value4, tension_value5]

            for v in tension_values:
                if v>0.8:
                    is_sendmail = True
                    break;

            if is_sendmail:
                print("메일 전송서비스 호출")

            tension_check_result = None

            if rst_id:
                tension_check_result = TensionCheckResult.objects.get(id=rst_id)
            else:
                tension_check_result = TensionCheckResult()


            tension_check_result.DataDate = data_date
            tension_check_result.line_cd = line_cd
            tension_check_result.Barcode = barcode
            tension_check_result.TensionValue1 = tension_value1
            tension_check_result.TensionValue2 = tension_value2
            tension_check_result.TensionValue3 = tension_value3
            tension_check_result.TensionValue4 = tension_value4
            tension_check_result.TensionValue5 = tension_value5

            tension_check_result.DefectReason = defect_reason
            tension_check_result.Result = txt_result
            tension_check_result.Worker = request.user
            tension_check_result.set_audit(request.user)
            tension_check_result.save()

            result["success"] = True
            result["data"] = tension_check_result.id

        elif action=="delete_tension":

            rst_id = posparam.get("rst_id")
            tension_check_result = TensionCheckResult.objects.filter(id=rst_id).delete()
            result["success"] = True


        else:
            raise ValueError("Invalid action")


    except Exception as ex:
        LogWriter.add_dblog('error', source, ex)

    return result