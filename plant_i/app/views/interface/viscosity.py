from itertools import filterfalse
from django.db import DatabaseError, transaction

from domain.models.aas import DateUtil
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.models.smt import SolderViscosityCheckResult, SolderViscosityCheckItem
from domain.models.definition import Material

def viscosity(context):

    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action', None)
    result = {'success' : False}

    try:
        if action=="read":
            data_year = gparam.get('data_year')
      

            dic_param = {"data_year" : data_year}
            sql = '''
            with mm as (
                select generate_series(1, 12) AS mon
            )
            select 
            id 
            , %(data_year)s as data_year
            ,  mm.mon as data_month
            , mr.data_group
            , mr.confirm_yn
            , mr.confirmer_id
            , to_char(mr.confirm_date, 'yyyy-mm-dd hh24:mi:ss') as confirm_date
            , up."Name" as confirmer
            from  mm 
            left join mon_term_result mr on  mr.data_month = mm.mon and mr.data_group = 'viscosity' and mr.data_year = %(data_year)s 
            left join user_profile up on up."User_id" = mr.confirmer_id 
            order by mm.mon desc
            '''

            items = DbUtil.get_rows(sql, dic_param)

            result["success"] = True
            result["items"] = items

        elif action == 'viscosity_check_result':
            data_year = gparam.get('data_year', None)
            data_month = gparam.get('data_month', None)

            
            yyyy = int(data_year)
            mm = int(data_month)
            #yyyy=2025
            #mm=7

            dic_param = { "yyyy" : yyyy, "mm" : mm }
            sql = '''
             SELECT
              d.data_day AS day
              , r.storage_temp 
              , r.agi_cond
              , r.clean_check
              , upa."Name" as admin 
              , upw."Name" as worker
            FROM dummy_date d
            LEFT JOIN visco_chk_result r ON r.data_date = d.data_date
            left join user_profile upw on upw."User_id" = r.worker_id
            left join user_profile upa on upa."User_id" = r.admin_id
            WHERE d.data_year = %(yyyy)s AND d.data_month = %(mm)s
            order by d.data_day 
             '''
            rst_rows = DbUtil.get_rows(sql, dic_param)

            items = []
            dic_storage_temp = {"row_key" : 'storage_temp', 'row_nm' :'보관규격확인', "chk_grp" : "공통", "data_year" : yyyy, "data_month" : mm}
            dic_agi_cond = {"row_key" : 'agi_cond', 'row_nm' : '교반조건확인', "chk_grp" : "공통", "data_year" : yyyy, "data_month" : mm}
            dic_clean_check = {"row_key" :  "clean_check", "row_nm":'점도계 세척확인', "chk_grp" : "공통" , "data_year" : yyyy, "data_month" : mm}
            dic_worker =  {"row_key" :  "worker", "row_nm":'작업자(무연납 생산 시작전)', "chk_grp" : "공통", "data_year" : yyyy, "data_month" : mm}
            dic_admin =  {"row_key" :  "admin", "row_nm":'관리자 확인' , "chk_grp" : "공통", "data_year" : yyyy, "data_month" : mm}


            for r in rst_rows:
                day = r.get('day')
                storage_temp = r.get("storage_temp")
                agi_cond = r.get("agi_cond")
                clean_check = r.get("clean_check")
                admin = r.get('admin')
                worker = r.get('worker')

                col = f"c_{day}"
                dic_storage_temp[col] = storage_temp
                dic_agi_cond[col] = agi_cond
                dic_clean_check[col] = clean_check
                dic_worker[col] = worker
                dic_admin[col] = admin


            sql_mat = '''
            select
              d.data_day AS day
              , i.mat_cd AS row_key
              , coalesce(m."Name", i.mat_cd) as row_nm
              , STRING_AGG('lot : ' || i.lot_no || ', sn: ' || i.serial_no || ', 점도 : ' || TO_CHAR(i.visc_value, 'FM999.999'), ',' ORDER BY i.lot_no) AS val              
            FROM dummy_date d
            LEFT JOIN visco_chk_item i ON  d.data_date=i.data_date 
            LEFT JOIN material m ON i.mat_cd = m."Code"
            WHERE d.data_year = %(yyyy)s AND d.data_month = %(mm)s
            GROUP BY d.data_day, i.mat_cd, m."Name"
            ORDER BY row_key, day
            '''
            mat_rows = DbUtil.get_rows(sql_mat, dic_param)
            day_count = DateUtil.get_day_count(yyyy, mm)
            dic_mat = {}

            for dic_row in mat_rows:
                row_key = dic_row['row_key']
                row_nm = dic_row["row_nm"]

                val = dic_row['val']
                day = dic_row["day"]
                col = f"c_{day}"
                
                if row_key in dic_mat:
                    dic = dic_mat[row_key]
                    dic[col] = val
                else:              
                    if row_key :
                        dic = {"row_key" : row_key, "row_nm" : row_nm, "data_year" : yyyy, "data_month" : mm, "chk_grp": "LOT 변경시" }
                        dic[col] = val
                        dic_mat[row_key] = dic

            items.append(dic_storage_temp)
            items.append(dic_agi_cond)
            items.append(dic_clean_check)

            if len(dic_mat)>0:
                for k, v in dic_mat.items():
                    items.append(v)

            items.append(dic_worker)
            items.append(dic_admin)

            result["items"] = items
            result['success'] = True
            result["column_count"] = day_count


        elif action=="save_viscosity_result":

            data_date = posparam.get('data_date')

            StorageTemperature = posparam.get('storage_temp') # 보관규격확인
            AgitationCondition = posparam.get('agi_cond') # 교반조건확인
            CleanCheck = posparam.get('clean_check')  # 점도계 세척확인

            viscosity_check_result = None

            query = SolderViscosityCheckResult.objects.filter(DataDate=data_date)
            if query.exists():
                viscosity_check_result = query.first();
            else:
                viscosity_check_result = SolderViscosityCheckResult()

            viscosity_check_result.DataDate = data_date
            viscosity_check_result.StorageTemperature = StorageTemperature
            viscosity_check_result.AgitationCondition = AgitationCondition
            viscosity_check_result.CleanCheck = CleanCheck  # 점도계 세척확인
            viscosity_check_result.Worker = request.user
            viscosity_check_result.set_audit(request.user)
            viscosity_check_result.save()

            result["success"] = True
            result["rst_id"] = viscosity_check_result.id
            result["message"] = "Viscosity check result saved successfully."

        elif action=="delete_viscosity_result":
            data_date = posparam.get('data_date')


            query = SolderViscosityCheckResult.objects.filter(DataDate=data_date)
            if query.count()>0:
                visco_check_result = query.first()

                if visco_check_result.TeamLeader:
                    result["success"] =False
                    result["message"] = '팀장승인이 진행되어 삭제될 수 없습니다.'
                    return result
                visco_check_result.delete()
                result["success"] = True

            else:
                result["success"] = False
                result["message"] = '삭제할 데이터가 없습니다.'

        elif action=="delete_viscosity_check_item":
            data_date = posparam.get('data_date')
            check_item_id = posparam.get('check_item_id')

            query = SolderViscosityCheckResult.objects.filter(DataDate=data_date)
            if query.count()>0:
                visco_check_result = query.first()

                if visco_check_result.TeamLeader:
                    result["success"] =False
                    result["message"] = '팀장승인이 진행되어 삭제될 수 없습니다.'
                    return result
                visco_check_result.delete()
                result["success"] = True


            check_item = None
            query = SolderViscosityCheckItem.objects.filter(id=check_item_id)
            if query.count()>0:
                check_item = query.delete()
                result["success"] = True
            else:
                result["success"] =False
                result["message"] = '삭제할 데이터가 없습니다.'



        elif action=="save_viscosity_check_item":

            data_date = posparam.get('data_date')


            if not data_date:
                raise ValueError("Data date is required.")

            
            mat_cd = posparam.get('mat_cd')
            lot_no = posparam.get('lot_no')
            serial_no = posparam.get('serial_no')
            InDate = posparam.get('InDate')
            ExpirationDate = posparam.get('ExpirationDate')
            viscometer = posparam.get('viscometer')

            viscosity_value = posparam.get('viscosity_value')
            
            check_item = None
            query = SolderViscosityCheckItem.objects.filter(DataDate=data_date)
            if query.count()>0:
                check_item = query.first()
            else:
                check_item = SolderViscosityCheckItem()

            check_item.DataDate = data_date
            check_item.mat_cd = mat_cd
            check_item.serial_no = serial_no
            check_item.lot_no = lot_no
            check_item.InDate = InDate
            check_item.ExpirationDate = ExpirationDate

            check_item.viscometer = viscometer
            check_item.ViscosityValue=viscosity_value
            check_item.set_audit(request.user)
            check_item.save()

            result["success"] = True
            result["check_item_id"] = check_item.id

        elif action=="solder_check_detail":

            data_date = gparam.get('data_date')
            dic_param = {"data_date" : data_date}

            sql='''
            select
              r.id
              , r.data_date
              , r.storage_temp 
              , r.agi_cond
              , r.clean_check
              , upa."Name" as admin 
              , upw."Name" as worker
              , to_char(r._created, 'yyyy-mm-dd hh24:mi:ss') as created
              , to_char(r._modified, 'yyyy-mm-dd hh24:mi:ss') as modified             
            FROM visco_chk_result r  
            left join user_profile upw on upw."User_id" = r.worker_id
            left join user_profile upa on upa."User_id" = r.admin_id
            WHERE 1=1
            and r.data_date=%(data_date)s
            '''
            comm_data = DbUtil.get_row(sql, dic_param)

            sql_mat = '''
            SELECT 
            t.id as check_item_id
            , t.data_date
            , t.mat_cd, m."Name" as mat_nm
            , t.lot_no, t.serial_no
            , t.in_date, t.exp_date, t.refr_in_date
            , t.viscometer
            , t.visc_value
            , to_char(t._created, 'yyyy-mm-dd hh24:mi:ss') as created
            , to_char(t._modified, 'yyyy-mm-dd hh24:mi:ss') as modified
            FROM visco_chk_item t
            left join material m on m."Code"=t.mat_cd
            where 1=1
            and t.data_date=%(data_date)s 
            '''
            mat_items = DbUtil.get_rows(sql_mat, dic_param)

            result['success'] = True
            result['data'] = comm_data
            result['items'] = mat_items

        elif action=="search_solder_material":
            '''
            바코드 스캔후 넘어온 솔더품목코드가 존재하는 코드인지 검증 함
            '''
            mat_cd = gparam.get('mat_cd')

            query = Material.objects.filter(Code=mat_cd)
            if query.exists():
                material = query.first()
                data =material.Code
                result['success'] = True
                result['data'] = data
            else:
                result['success'] = False
                result["message"] = "존재하지 않는 자재입니다."

        else:
            raise ValueError("Invalid action")

    except Exception as e:
        context.error = str(e)
        result['success'] = False
        result["message"] = context.error
        LogWriter.add_dblog('error', 'viscosity', e)

    return result