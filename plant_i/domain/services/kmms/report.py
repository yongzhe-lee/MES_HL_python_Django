from domain.services.common import CommonUtil
from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter


class CmReportService:
    def __init__(self):
        return

    # 설비별 월간 고장현황황
    def facility_monthly_status(self, searchYear, deptTree, equipLocTree):
        items = []
        dic_param = {
            "searchYear": searchYear,
            "deptTree": deptTree,
            "equipLocTree": equipLocTree,
        }

        sql = """ 
			/* getEquipMonCost (설비별 월간 정비비용) [stat-equip-mapper.xml] */

             with t as (
                select 1 as rownum, e.equip_pk, e.loc_pk, e.equip_cd, e.equip_nm, 'breakTime' as rslt_type
                , 0 as rslt_m1, 0 as rslt_m2, 0 as rslt_m3, 0 as rslt_m4, 0 as rslt_m5, 0 as rslt_m6, 0 as rslt_m7, 0 as rslt_m8, 0 as rslt_m9, 0 as rslt_m10, 0 as rslt_m11, 0 as rslt_m12, 0 as rslt_sum
                , 0 as curr_m, 0 as curr_sum
                from cm_equipment e
                where 1=1 and e.use_yn = 'Y' and e.del_yn = 'N'
       
                union all
                select 2 as rownum, e.equip_pk, e.loc_pk, e.equip_cd, e.equip_nm, 'breakCount' as rslt_type
                , 0 as rslt_m1, 0 as rslt_m2, 0 as rslt_m3, 0 as rslt_m4, 0 as rslt_m5, 0 as rslt_m6, 0 as rslt_m7, 0 as rslt_m8, 0 as rslt_m9, 0 as rslt_m10, 0 as rslt_m11, 0 as rslt_m12, 0 as rslt_sum
                ,  0 as curr_m, 0 as curr_sum
                from cm_equipment e
                where 1=1 and e.use_yn = 'Y' and e.del_yn = 'N'
               
             )
             , tt as (
                select t.rownum
                    , t.equip_pk
                    , t.loc_pk
                    , t.equip_cd
                    , t.equip_nm
                    , t.rslt_type

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '01') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '01') then 1 else 0 end) as rslt_m1

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '02') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '02') then 1 else 0 end) as rslt_m2

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '03') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '03') then 1 else 0 end) as rslt_m3

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '04') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '04') then 1 else 0 end) as rslt_m4

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '05') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '05') then 1 else 0 end) as rslt_m5

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '06') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '06') then 1 else 0 end) as rslt_m6

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '07') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '07') then 1 else 0 end) as rslt_m7

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '08') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '08') then 1 else 0 end) as rslt_m8

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '09') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '09') then 1 else 0 end) as rslt_m9

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '10') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '10') then 1 else 0 end) as rslt_m10

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '11') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '11') then 1 else 0 end) as rslt_m11

                        , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '12') then wo.breakdown_min
                            when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '12') then 1 else 0 end) as rslt_m12

                    , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYY') =  %(searchYear)s  then wo.breakdown_min
                        when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYY') =  %(searchYear)s then 1 else 0 end) as rslt_sum
                    , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYY') =  ((%(searchYear)s)::int - 1)::text  then wo.breakdown_min
                        when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYY') =  ((%(searchYear)s)::int - 1)::text then 1 else 0 end) as curr_sum
                    , sum(case when t.rslt_type = 'breakTime' and wo.breakdown_min is not null and to_char(wo.end_dt, 'YYYYMM') = concat((%(searchYear)s)::int - 1,TO_CHAR(current_date, 'MM'))  then wo.breakdown_min
                         when t.rslt_type = 'breakCount' and to_char(wo.end_dt, 'YYYYMM') =  concat((%(searchYear)s)::int - 1,TO_CHAR(current_date, 'MM')) then 1 else 0 end) as curr_m
                from t
                inner join cm_work_order wo on t.equip_pk = wo.equip_pk
                inner join cm_location l on t.loc_pk = l.loc_pk
                and wo.wo_type = 'WO'
                and wo.wo_status = 'WOS_CL'
                and to_char(wo.end_dt, 'YYYY') in (%(searchYear)s, ((%(searchYear)s)::int - 1)::text)        

                    and wo.maint_type_cd = 'MAINT_TYPE_BM'
                """
        if deptTree:
            sql += """
                AND (
                    wo.req_dept_pk = %(deptTree)s
                    OR
                    wo.req_dept_pk In (select dept_pk from cm_v_dept_path where cast(%(deptTree)s as integer) = path_info_pk)
                )
            """
        if equipLocTree:
            sql += """
                AND (
                    l.loc_pk = %(equipLocTree)s
                    OR
                    l.loc_pk IN ( select loc_pk from (select * from cm_fn_get_loc_path(1)) x1 where %(equipLocTree)s = path_info_pk)
                )
            """
        sql += """
        
                group by t.rownum
                , t.equip_pk
                , t.loc_pk
                , t.equip_cd
                , t.equip_nm
                , t.rslt_type
            )
            select ROW_NUMBER() OVER (ORDER BY concat(tt.rownum, '_', tt.equip_pk)) AS row_num
            , concat(tt.rownum, '_', tt.equip_pk) as row_key
            , tt.equip_pk
            , tt.loc_pk
            , tt.equip_cd
            , tt.equip_nm
            , tt.rslt_type
            , tt.rslt_m1
            , tt.rslt_m2
            , tt.rslt_m3
            , tt.rslt_m4
            , tt.rslt_m5
            , tt.rslt_m6
            , tt.rslt_m7
            , tt.rslt_m8
            , tt.rslt_m9
            , tt.rslt_m10
            , tt.rslt_m11
            , tt.rslt_m12
            , tt.rslt_sum
            , tt.curr_m
            , tt.curr_sum
            from tt
            where tt.equip_cd is not null
            order by tt.equip_cd, row_key

			;
			"""

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_monthly_status", ex)
            raise ex

        return items

    # 설비별 월간 정비비용
    def monthly_maintenance_cost(self, searchYear, woType, maintTypeCd, deptPk):
        items = []
        dic_param = {
            "searchYear": searchYear,
            "woType": woType,
            "maintTypeCd": maintTypeCd,
            "deptPk": deptPk,
        }

        sql = ''' 
			/* getEquipMonCost (설비별 월간 정비비용) [stat-equip-mapper.xml] */

            with t as (
                select 1 as rownum, e.equip_pk, e.equip_cd, e.equip_nm, 'cost' as rslt_type
                , 0 as rslt_m1, 0 as rslt_m2, 0 as rslt_m3, 0 as rslt_m4, 0 as rslt_m5, 0 as rslt_m6, 0 as rslt_m7, 0 as rslt_m8, 0 as rslt_m9, 0 as rslt_m10, 0 as rslt_m11, 0 as rslt_m12, 0 as rslt_sum
                , 0 as curr_m, 0 as curr_sum
                from cm_equipment e
                where 1=1 and e.use_yn = 'Y' and e.del_yn = 'N'
                -- and e.site_id = 'WEZON'
                union all
                select 2 as rownum, e.equip_pk, e.equip_cd, e.equip_nm, 'mtrlCost' as rslt_type
                , 0 as rslt_m1, 0 as rslt_m2, 0 as rslt_m3, 0 as rslt_m4, 0 as rslt_m5, 0 as rslt_m6, 0 as rslt_m7, 0 as rslt_m8, 0 as rslt_m9, 0 as rslt_m10, 0 as rslt_m11, 0 as rslt_m12, 0 as rslt_sum
                ,  0 as curr_m, 0 as curr_sum
                from cm_equipment e
                where 1=1 and e.use_yn = 'Y' and e.del_yn = 'N'
                -- and e.site_id = 'WEZON'
            )
            , tt as (
                select t.rownum
                    , t.equip_pk
                    , t.equip_cd
                    , t.equip_nm
                    , t.rslt_type

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '01') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '01') then wo.mtrl_cost else 0 end) as rslt_m1

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '02') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '02') then wo.mtrl_cost else 0 end) as rslt_m2

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '03') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '03') then wo.mtrl_cost else 0 end) as rslt_m3

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '04') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '04') then wo.mtrl_cost else 0 end) as rslt_m4

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '05') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '05') then wo.mtrl_cost else 0 end) as rslt_m5

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '06') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '06') then wo.mtrl_cost else 0 end) as rslt_m6

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '07') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '07') then wo.mtrl_cost else 0 end) as rslt_m7

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '08') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '08') then wo.mtrl_cost else 0 end) as rslt_m8

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '09') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '09') then wo.mtrl_cost else 0 end) as rslt_m9

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '10') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '10') then wo.mtrl_cost else 0 end) as rslt_m10

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '11') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '11') then wo.mtrl_cost else 0 end) as rslt_m11

                    , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '12') then wo.tot_cost
                        when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '12') then wo.mtrl_cost else 0 end) as rslt_m12

                , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYY') =  %(searchYear)s  then wo.tot_cost
                    when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYY') =  %(searchYear)s then wo.mtrl_cost else 0 end) as rslt_sum
                , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYY') =  ((%(searchYear)s)::int - 1)::text  then wo.tot_cost
                    when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYY') =  ((%(searchYear)s)::int - 1)::text then wo.mtrl_cost else 0 end) as curr_sum
                , sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = concat((%(searchYear)s)::int - 1,TO_CHAR(current_date, 'MM'))  then wo.tot_cost
                     when t.rslt_type = 'mtrlCost' and wo.mtrl_cost is not null and to_char(wo.end_dt, 'YYYYMM') =  concat((%(searchYear)s)::int - 1,TO_CHAR(current_date, 'MM')) then wo.mtrl_cost else 0 end) as curr_m
                from t
                inner join cm_work_order wo on t.equip_pk = wo.equip_pk
                and wo.wo_status = 'WOS_CL'
                and to_char(wo.end_dt, 'YYYY') in (%(searchYear)s, ((%(searchYear)s)::int - 1)::text)         
            '''
        if woType:
            sql += '''
                and wo.wo_type = %(woType)s
            '''
        if maintTypeCd:
            if isinstance(maintTypeCd, str):
                maintTypeCd_list = [item.strip() for item in maintTypeCd.split(',') if item.strip()]
            elif isinstance(maintTypeCd, list):
                maintTypeCd_list = maintTypeCd
            else:
                maintTypeCd_list = [maintTypeCd]
            
            if maintTypeCd_list:
                maintTypeCd_str = ','.join([f"'{item}'" for item in maintTypeCd_list])
                sql += f'''
                    and wo.maint_type_cd in ( {maintTypeCd_str} )
                '''
        if deptPk:
            sql += '''
                AND (
                    wo.req_dept_pk = %(deptPk)s
                    OR
                    wo.req_dept_pk In (select dept_pk from cm_v_dept_path where cast(%(deptPk)s as integer) = path_info_pk)
                )
            '''
        sql += '''
                group by t.rownum
                , t.equip_pk
                , t.equip_cd
                , t.equip_nm
                , t.rslt_type
            )
            select concat(tt.rownum, '_', tt.equip_pk) as row_key
            , tt.equip_pk
            , tt.equip_cd
            , tt.equip_nm
            , tt.rslt_type
            , tt.rslt_m1
            , tt.rslt_m2
            , tt.rslt_m3
            , tt.rslt_m4
            , tt.rslt_m5
            , tt.rslt_m6
            , tt.rslt_m7
            , tt.rslt_m8
            , tt.rslt_m9
            , tt.rslt_m10
            , tt.rslt_m11
            , tt.rslt_m12
            , tt.rslt_sum
            , tt.curr_m
            , tt.curr_sum
            from tt
            where tt.equip_cd is not null
            order by tt.equip_cd, tt.rslt_type
			'''

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.monthly_maintenance_cost", ex)
            raise ex

        return items

    # 기간별 불용처리 설비 현황
    def facility_treatment_status(self, startYear, endYear):
        items = []
        dic_param = {
            "startYear": startYear,
            "endYear": endYear
        }

        sql = """
        /* getDisableEquipTotCount (불용처리 설비 건수(기간별)) [stat-equip-mapper.xml] */

        with sq as (

                SELECT t2.year_mon
                    , count(t1.equip_pk) as tot_cnt
                FROM (
                        SELECT to_char(years, 'YYYY') as year_mon
                        FROM generate_series(
                            to_date(%(startYear)s || '-01-01', 'YYYY-MM-DD'),
                            to_date(%(endYear)s || '-12-31', 'YYYY-MM-DD'),
                            interval '1 year'
                        ) as years
                ) t2

                LEFT OUTER JOIN cm_equipment t1 on t2.year_mon = to_char(t1.disposed_date, 'YYYY')
                AND t1.del_yn = 'N'
                -- AND t1.site_id = 'WEZON'
                AND t1.disposed_date is not null
                AND (t1.disposed_date >= to_date(%(startYear)s || '-01-01', 'YYYY-MM-DD')
                    and t1.disposed_date <= to_date(%(endYear)s || '-12-31', 'YYYY-MM-DD'))

                        WHERE (t2.year_mon >= %(startYear)s and t2.year_mon <= %(endYear)s)

                GROUP BY t2.year_mon
                ORDER BY t2.year_mon
        )
        , cte as (
            select sq.*
            from sq
        )
        SELECT *
        FROM (
            table cte

                -- limit 999 offset (1-1)*999

        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
        """
        
        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_treatment_status", ex)
            raise ex

        return items

    # 기간별 불용처리 설비 현황 상세
    def facility_treatment_status_detail(self, yearMon):
        items = []
        dic_param = {
            "yearMon": yearMon
        }

        sql = """
        /* getDisableEquipList (불용처리 설비목록) [stat-equip-mapper.xml] */

        with sq as (

                select t1.equip_pk
                    , to_char(t1.disposed_date, 'YYYY-MM-DD') as disposed_date
                    , t4.code_nm as disposed_type
                    , t1.equip_cd
                    , t1.equip_nm
                    , t2.equip_category_desc
                    , t1.equip_class_desc
                    , to_char(t1.install_dt, 'YYYY-MM-DD') as install_dt
                    , t3.supplier_nm as maker_nm
                from cm_equipment t1
                left outer join cm_equip_category t2 on t1.equip_category_id = t2.equip_category_id
                left outer join cm_supplier t3 on t1.maker_pk = t3.supplier_pk
                left outer join cm_base_code t4 on t1.disposed_type = t4.code_cd
                where t1.del_yn = 'N'
                -- AND t1.site_id = 'WEZON'
                and t1.disposed_date is not null
                and (t1.disposed_date >= to_date(%(yearMon)s || '-01-01', 'YYYY-MM-DD')
                and t1.disposed_date <= to_date(%(yearMon)s || '-12-31', 'YYYY-MM-DD'))
                order by t1.equip_nm, t1.disposed_date desc

        )
        , cte as (
            select sq.*
            from sq
        )
        SELECT *
        FROM (
            table cte

                -- limit 999 offset (1-1)*999

        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
        """
        
        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_treatment_status_detail", ex)
            raise ex
        return items

    # 설비별 MTTR/MTBF
    def facility_mttr_mtbf(self, searchText, deptPk, startDt, endDt):
        items = []
        dic_param = {
            "searchText": searchText,
            "deptPk": deptPk,
            "startDt": startDt,
            "endDt": endDt
        }

        sql = """
        /* getEquipMTTRMTBFList (MTTR, MTBF 목록) [stat-equip-mapper.xml] */

        with sq as (

            with tt as (
                select eq.equip_pk
                , eq.equip_cd
                , eq.equip_nm
                , irn.import_rank_cd
                , ec.equip_category_desc
                , eq.equip_class_desc
                , count(*) as broken_cnt
                , sum(wo.breakdown_min) as broken_min
                , (case when count(*) = 0 then 0 else round(sum(cast(wo.breakdown_min as numeric))/count(*), 1) end) as mttr
                , (EXTRACT(EPOCH FROM max(wo.end_dt) -
                    (case when min(wo.breakdown_dt) < to_date(%(startDt)s,'YYYY-MM-DD') then
                        min(wo.breakdown_dt) else to_date(%(startDt)s,'YYYY-MM-DD') end))/60) AS oper_min
                from cm_work_order wo
                inner join cm_equipment eq on wo.equip_pk = eq.equip_pk
                left outer join cm_import_rank irn on eq.import_rank_pk = irn.import_rank_pk
                inner join cm_equip_category ec on eq.equip_category_id = ec.equip_category_id
                where wo.wo_type = 'WO'
                and wo.maint_type_cd = 'MAINT_TYPE_BM'
                and wo.wo_status = 'WOS_CL'
                -- and wo.site_id = 'WEZON'
                """
        if searchText:
            sql += """
                AND (
                    UPPER(eq.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
                    OR
                    UPPER(eq.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
                )
            """
        if deptPk:
            sql += """
                AND (
                    wo.req_dept_pk = %(deptPk)s
                    OR
                    wo.req_dept_pk IN (select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
                )
            """
        if startDt and endDt:
            sql += """
                and date(wo.end_dt) between to_date(%(startDt)s, 'YYYY-MM-DD') and to_date(%(endDt)s, 'YYYY-MM-DD')
            """
        sql += """
                group by eq.equip_pk, eq.equip_cd, eq.equip_nm, irn.import_rank_cd
                , ec.equip_category_desc, eq.install_dt, eq.equip_class_desc
            )
            , vox as (
                select tt.*
                , round(cast(tt.oper_min - tt.broken_min as numeric)/tt.broken_cnt, 1) as mtbf
                from tt
            )
            , vo as (
                select vox.equip_pk, vox.equip_cd, vox.equip_nm, vox.import_rank_cd
                , vox.equip_category_desc
                , vox.equip_class_desc
                , vox.mttr, vox.mtbf
                , (case when vox.mtbf = 0 and vox.mttr = 0 then 0 else round((vox.mtbf/(vox.mtbf+vox.mttr))*100,2) end) as operating_rate
                , vox.broken_cnt, vox.broken_min as broken_hr, round(cast(vox.oper_min as numeric), 1) as oper_hr
                from vox
            )
            select vo.equip_pk
                , vo.equip_cd
                , vo.equip_nm
                , vo.import_rank_cd
                , vo.equip_category_desc
                , vo.equip_class_desc
                , vo.mttr
                , vo.mtbf
                , vo.operating_rate
                , vo.broken_cnt
                , vo.broken_hr
                , vo.oper_hr
            from vo
        )
        , cte as (
            select sq.*
            from sq
        )
        SELECT *
        FROM (
            table cte

                 order by equip_cd ASC 

                -- limit 30 offset (1-1)*30

        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_mttr_mtbf", ex)
            raise ex
        return items

    # 카테고리별 설비 현황
    def category_equipment_status(self, locPk):
        items = []
        dic_param = {"locPk": locPk}

        sql = """ 
			     /* getEquipCountByEquipClass (설비 종류별 사용 중인 수, 사용하지 않는 수) [stat-equip-mapper.xml] */

                select row_number() over (order by use_cnt DESC) as row_num
                , v.equip_class_desc as group_nm
                , coalesce(v.use_cnt,0) as use_cnt
                , coalesce(v.not_use_cnt,0) as not_use_cnt
                , coalesce(v.tot_cnt,0) as tot_cnt
                , coalesce(v.break_cnt, 0) as break_cnt
                , coalesce(v.useless_cnt, 0) as useless_cnt
                from (
                    select 1 as disp_order, coalesce(t.equip_class_desc, '-') as equip_class_desc

                        , sum(case when t.use_yn = 'Y' then 1 else 0 end) as use_cnt
                        , sum(case when t.use_yn = 'Y' then 0 else 1 end) as not_use_cnt
                        , sum(case when t.equip_status = 'ES_BKDN' then 1 else 0 end) as break_cnt
                        , sum(case when t.equip_status = 'ES_DISP' then 1 else 0 end) as useless_cnt
                        , count(*) as tot_cnt
                    from cm_equipment t
                    left outer join cm_equip_category t1 on t.equip_category_id = t1.equip_category_id

                    where t.del_yn = 'N'
                    """
        if locPk:
            sql += """
                    AND (
                    t.loc_pk = %(locPk)s
                    OR
                    t.loc_pk IN ( select vl.loc_pk from (select * from cm_fn_get_loc_path(1)) vl where %(locPk)s = vl.path_info_pk)
                    )
                    """
        sql += """
                    group by coalesce(t.equip_class_desc, '-')

                 ) v
                 order by coalesce(v.use_cnt,0) desc;
			    """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.category_equipment_status", ex)
            raise ex

        return items

    # 중요도별 설비 고장 현황
    def critical_equipment_status(self):
        items = []
        dic_param = {}
        
        sql = """
        /* getEquipUseCountListByImportRank (등급별 사용중인 설비수, 고장난설비수) [stat-equip-mapper.xml] */

        select ROW_NUMBER() OVER(order by t5.import_rank_pk) AS row_num
            , t5.import_rank_pk
            , t5.import_rank_cd
            , sum(case when upper(t3.equip_status) = 'ES_OPER' then 1 else 0 end) as use_count
            , sum(case when upper(t3.equip_status) = 'ES_BKDN' then 1 else 0 end) as break_count
            , sum(case when upper(t3.equip_status) = 'ES_DISP' then 1 else 0 end) as useless_cnt
            , sum(case when upper(t3.equip_status) = 'ES_IDLE' then 1 else 0 end) as unuse_cnt
            , sum(case when upper(t3.equip_status) LIKE CONCAT('%%',UPPER('ES_'),'%%') then 1 else 0 end) as all_cnt
        from cm_equipment t3
        left outer join cm_equip_category t4 on t3.equip_category_id = t4.equip_category_id
        left outer join cm_import_rank t5 on t3.import_rank_pk = t5.import_rank_pk
        where t3.del_yn = 'N'
        -- and t3.site_id = 'WEZON'
        group by t5.import_rank_pk, t5.import_rank_cd
        """
        
        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.critical_equipment_status", ex)
            raise ex

        return items

    # 중요도별 설비 고장 현황 상세
    def critical_equipment_status_detail(self, importRankPk):
        items = []
        dic_param = {"importRankPk": importRankPk}
        
        sql = """
        /* getBreakDownEquipListByImportRank (등급별 고장 중인 설비 목록) [stat-equip-mapper.xml] */

        select t3.equip_pk
            , t5.import_rank_cd
            , CM_FN_TIMESTAMPDIFF(cast(max(t3.breakdown_dt) as timestamp)
                    , cast((now() + INTERVAL '1 HOUR')as timestamp)) as breakdown_hr
            , t3.equip_cd
            , t3.equip_nm
            , t4.equip_category_desc
            , t3.equip_class_desc
            , to_char(max(t3.breakdown_dt), 'YYYY-MM-dd HH24:MI') as breakdown_dt
            , max(t6.reliab_cd) as cause_nm
        from cm_equipment t3
        left outer join cm_work_order t1 on t1.equip_pk = t3.equip_pk
        AND t1.wo_status not in ('WOS_DL', 'WOS_CL', 'WOS_RW', 'WOS_RB')
        AND t1.maint_type_cd = 'MAINT_TYPE_BM'
        -- AND t1.site_id = 'WEZON'
        left outer join cm_equip_category t4 on t3.equip_category_id = t4.equip_category_id
        left outer join cm_import_rank t5 on t3.import_rank_pk = t5.import_rank_pk
        left outer join cm_reliab_codes t6 on t1.cause_cd = t6.reliab_cd AND t6."types" = 'CC' 
        -- and t6.site_id = t3.site_id
        where t3.del_yn = 'N'
        -- and t3.site_id = 'WEZON'
        and upper(t3.equip_status) = 'ES_BKDN'

            and t5.import_rank_pk = %(importRankPk)s

        group by t3.equip_pk, t5.import_rank_cd, t3.equip_cd, t3.equip_nm, t4.equip_category_desc, t3.equip_class_desc
        order by t3.equip_cd
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.critical_equipment_status_detail", ex)
            raise ex

        return items

    # 설비별 정비비용
    def facility_maintenance_cost(self, dateType, startDt, endDt, searchText, deptPk, locPk):
        items = []
        dic_param = {
            "dateType": dateType,
            "startDt": startDt,
            "endDt": endDt,
            "searchText": searchText,
            "deptPk": deptPk,
            "locPk": locPk,
        }

        sql = """
        /* getEquipBreakDownCostListOrderByTop (설비별 정비비용(많은순)) [stat-equip-mapper.xml] */

        with v as (

            -- select to_char(wo.end_dt, 'YYYY.MM') as year_mon
            select
                CASE
                    WHEN %(dateType)s = 'MON' THEN to_char(wo.end_dt, 'YYYY.MM')
                    WHEN %(dateType)s = 'YEAR' THEN to_char(wo.end_dt, 'YYYY')
                    ELSE to_char(wo.end_dt, 'YYYY.MM')
                END as year_mon
                    , e.equip_cd
                    , e.equip_nm
                    , e.install_dt
                    -- , wo.end_dt
                    , sum(wo.tot_cost) as tot_cost
                    , sum(wo.mtrl_cost) as mtrl_cost
                    , sum(wo.labor_cost) as labor_cost
                    , sum(wo.outside_cost) as outside_cost
                    , sum(wo.etc_cost) as etc_cost
                FROM cm_work_order wo
                inner join cm_equipment e on wo.equip_pk = e.equip_pk
                left outer join cm_location l on l.loc_pk = e.loc_pk
                left outer join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
                left outer join cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
                WHERE e.del_yn = 'N'
                -- AND wo.site_id = 'WEZON'
                AND wo.wo_status = 'WOS_CL'
                """
        if startDt and endDt:
            sql += """
                AND (
                    wo.end_dt >= to_date(%(startDt)s, 'YYYYMMDD')
                    AND
                    wo.end_dt <= to_date(%(endDt)s, 'YYYYMMDD')
                )
            """
        if searchText:
            sql += """
                AND (
                    UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
                    OR
                    UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
                )
            """
        if deptPk:
            sql += """
                AND (
                    wo.req_dept_pk = %(deptPk)s
                    OR
                    wo.req_dept_pk IN (select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
                )
            """
        if locPk:
            sql += """
                AND (
                    l.loc_pk = %(locPk)s
                    OR
                    l.loc_pk IN (select vl.loc_pk from (select * from cm_fn_get_loc_path(1)) vl where %(locPk)s = vl.path_info_pk)
                )
            """
        sql += """
                GROUP BY
                    CASE
                        WHEN %(dateType)s = 'MON' THEN to_char(wo.end_dt, 'YYYY.MM')
                        WHEN %(dateType)s = 'YEAR' THEN to_char(wo.end_dt, 'YYYY')
                        ELSE to_char(wo.end_dt, 'YYYY.MM')
                    END
                    , e.equip_cd
                    , e.equip_nm
                    , e.install_dt
                    -- , wo.end_dt
            """
        sql += """
        ), cte as (
            SELECT v.year_mon
                , v.equip_cd
                , v.equip_nm
                , to_char(v.install_dt,'YYYY-MM-DD') as install_dt
                , coalesce(sum(v.tot_cost), 0) as tot_cost
                , coalesce(sum(v.mtrl_cost), 0) as mtrl_cost
                , coalesce(sum(v.labor_cost), 0) as labor_cost
                , coalesce(sum(v.outside_cost), 0) as outside_cost
                , coalesce(sum(v.etc_cost), 0) as etc_cost
            FROM v
            GROUP BY v.year_mon
                , v.equip_cd
                , v.equip_nm
                , v.install_dt
        )
        SELECT *
        FROM (
            table cte

                 order by year_mon ASC 

                -- limit 30 offset (1-1)*30

        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_maintenance_cost", ex)
            raise ex

        return items

    # 설비별 고장시간
    def facility_downtime(self, dateType, startDt, endDt, searchText, deptPk, locPk):
        items = []
        dic_param = {
            "dateType": dateType,
            "startDt": startDt,
            "endDt": endDt,
            "searchText": searchText,
            "deptPk": deptPk,
            "locPk": locPk,
        }

        sql = """
        /* getEquipBreakDownTimeList (설비별 Down Time) [stat-equip-mapper.xml] */

        with v as (

                -- select to_char(wo.end_dt, 'YYYY') as year_mon
                select
                    CASE
                        WHEN %(dateType)s = 'MON' THEN to_char(wo.end_dt, 'YYYY.MM')
                        WHEN %(dateType)s = 'YEAR' THEN to_char(wo.end_dt, 'YYYY')
                        ELSE to_char(wo.end_dt, 'YYYY.MM')
                    END as year_mon
                    , wo.end_dt
                    , e.equip_cd
                    , e.equip_nm
                    , ec.equip_category_desc
                    , e.equip_class_desc
                    , l.loc_nm
                    , round(sum(wo.breakdown_min),1) as breakdown_min
                    , max(x.tot_hr) as tot_hr
                    , to_char(e.install_dt,'YYYY-MM-DD') as install_dt
                    , to_char(e.warranty_dt,'YYYY-MM-DD') as warranty_dt
                    , es.code_nm as equip_status
                    , sum(case when wo.breakdown_min is not null then 1 else 0 end) as breakdown_cnt
                from cm_work_order wo
                inner join cm_equipment e on wo.equip_pk = e.equip_pk
                inner join cm_base_code es on e.equip_status = es.code_cd
                inner join cm_location l on l.loc_pk = e.loc_pk
                left outer join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
                left outer join cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
                left outer join (
                    select e.equip_pk
                        , sum(wo.breakdown_min) as tot_hr
                    from cm_work_order wo
                    inner join cm_equipment e on wo.equip_pk = e.equip_pk
                    left outer join cm_equip_category ec on e.equip_category_id = ec.equip_category_id
                    inner join cm_location l on l.loc_pk = e.loc_pk
                    left outer join cm_import_rank ir on e.import_rank_pk = ir.import_rank_pk
                    where e.del_yn = 'N'
                    and wo.wo_status = 'WOS_CL'
                    and wo.breakdown_min is not null and wo.breakdown_min > 0
                    and wo.maint_type_cd = 'MAINT_TYPE_BM'
                    group by e.equip_pk, e.equip_cd, e.equip_nm, ec.equip_category_desc, l.loc_nm
                ) x on e.equip_pk = x.equip_pk
                WHERE e.del_yn = 'N'
                AND wo.wo_status = 'WOS_CL'
                -- AND wo.site_id = 'WEZON'
                """
        if startDt and endDt:
            sql += """
                AND (
                    wo.end_dt >= to_date(%(startDt)s, 'YYYYMMDD')
                    AND
                    wo.end_dt <= to_date(%(endDt)s, 'YYYYMMDD')
                )
            """
        if searchText:
            sql += """
                AND (
                    UPPER(e.equip_cd) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
                    OR
                    UPPER(e.equip_nm) LIKE CONCAT('%%',UPPER(CAST(%(searchText)s as text)),'%%')
                )
            """
        if deptPk:
            sql += """
                AND (
                    wo.req_dept_pk = %(deptPk)s
                    OR
                    wo.req_dept_pk IN (select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
                )
            """
        if locPk:
            sql += """
                AND (
                    l.loc_pk = %(locPk)s
                    OR
                    l.loc_pk IN (select vl.loc_pk from (select * from cm_fn_get_loc_path(1)) vl where %(locPk)s = vl.path_info_pk)
                )
            """
        sql += """
                AND wo.breakdown_min is not null and wo.breakdown_min > 0
                AND wo.maint_type_cd = 'MAINT_TYPE_BM'
            AND e.equip_pk = coalesce(NULL ,e.equip_pk)
            GROUP BY to_char(wo.end_dt, 'YYYY'), wo.end_dt, e.equip_cd
            , e.equip_nm, ec.equip_category_desc, l.loc_nm, e.install_dt, e.warranty_dt, es.code_nm
            , e.equip_class_desc
        )
        , cte as (
                SELECT v.year_mon
                    , v.equip_cd
                    , v.equip_nm
                    , v.equip_category_desc
                    , v.equip_class_desc
                    , v.loc_nm
                    , sum(v.breakdown_min) as tot_break_time
                    , max(v.tot_hr) as all_break_time
                    , v.install_dt
                    , v.warranty_dt
                    , v.equip_status as equip_status_nm
                    , sum(v.breakdown_cnt) as breakdown_cnt
                FROM v
                GROUP BY v.year_mon
                    , v.equip_cd
                    , v.equip_nm
                    , v.equip_category_desc
                    , v.equip_class_desc
                    , v.loc_nm
                    , v.install_dt
                    , v.warranty_dt
                    , v.equip_status
        )
        SELECT *
        FROM (
            table cte

                 order by year_mon ASC 

                -- limit 30 offset (1-1)*30

        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_downtime", ex)
            raise ex

        return items

    # 설비별 사양 목록
    def facility_specifications(self, searchText, deptPk, locPk):
        items = []
        dic_param = {
            "searchText": searchText,
            "deptPk": deptPk,
            "locPk": locPk,
        }

        sql = """
        /* getEquipSpecList (설비별 사양 목록) [stat-equip-mapper.xml] */

        with cte as (

                SELECT e.equip_cd
                       , e.equip_nm
                       , s.supplier_nm
                       , e.install_dt
                       , l.loc_nm
                       , d."Name" as dept_nm
                       , es.equip_spec_nm
                       , es.equip_spec_unit
                       , es.equip_spec_value
                       , Row_number() OVER( partition BY e.equip_cd) rowNum
                FROM   cm_equip_spec es
                       LEFT OUTER JOIN cm_equipment e ON es.equip_pk = e.equip_pk
                       LEFT OUTER JOIN cm_supplier s ON e.maker_pk = s.supplier_pk
                       INNER JOIN cm_location l ON e.loc_pk = l.loc_pk
                       INNER JOIN dept d ON d.id = e.dept_pk
                WHERE  1 = 1
            """
        if searchText:
            sql += """
                    AND (upper(e.equip_nm) like concat('%%',upper(COALESCE(%(searchText)s, e.equip_nm )),'%%')
                         or upper(e.equip_cd) like concat('%%',upper(COALESCE(%(searchText)s, e.equip_nm )),'%%'))
                """
        if deptPk:
            sql += """
                    AND (
                        e.dept_pk = %(deptPk)s
                        OR
                        e.dept_pk IN (select dept_pk from v_dept_path where %(deptPk)s = path_info_pk)
                    )
                """
        if locPk:
            sql += """
                    AND (
                        e.loc_pk = %(locPk)s
                        OR
                        e.loc_pk IN (select vl.loc_pk from (select * from cm_fn_get_loc_path(1)) vl where %(locPk)s = vl.path_info_pk)
                    )
                """
        sql += """
        )
        SELECT *
        FROM (
            table cte

                -- limit 30 offset (1-1)*30

        ) sub
        RIGHT JOIN (select count(*) from cte) c(total_rows) on true
        WHERE total_rows != 0
        order by equip_cd, rowNum
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.facility_specifications", ex)
            raise ex

        return items

######################## 작업통계 ####################################################

    # 부서별 기간별 WO 발행 실적
    def wm_wo_dept_performance(self, dateType, startDt, endDt, deptPk):
        items = []
        dic_param = {
            "dateType": dateType,
            "startDt": startDt,
            "endDt": endDt,
            "deptPk": deptPk,
        }

        sql = """
        /* getWorkOrderCount (작업 건수(기간별, 부서 등의 기타 구분)) [stat-work-order-mapper.xml] */

		WITH sql1 AS (
			select coalesce(t2."Name", '-') as dept_nm
				, CASE
					WHEN %(dateType)s = 'MON' THEN to_char(t1.plan_end_dt, 'YYYY.MM')
					WHEN %(dateType)s = 'YEAR' THEN to_char(t1.plan_end_dt, 'YYYY')
					ELSE to_char(t1.plan_end_dt, 'YYYY.MM')
				END as plan_end_dt
				, count(t1.work_order_pk) as tot_cnt
				, sum(case when t1.wo_status = 'WOS_CL' then 1 else 0 end) as finish_cnt
				, sum(case when t1.wo_status = 'WOS_CL' then 0 else 1 end) as not_finish_cnt
				, sum(case when t1.wo_status = 'WOS_DL' then 1 else 0 end) as cancle_cnt
			from cm_work_order t1
			inner join dept t2 on t1.req_dept_pk = t2.id
			inner join cm_work_order_approval t3 on t1.work_order_approval_pk = t3.work_order_approval_pk
			-- where t1.site_id = 'WEZON'
            where 1=1
			and (t1.plan_end_dt >= to_date(%(startDt)s, 'YYYYMMDD') and t1.plan_end_dt <= to_date(%(endDt)s, 'YYYYMMDD'))
            """
        if deptPk:
            sql += """
				AND (
					t1.req_dept_pk = %(deptPk)s
					OR
					t1.req_dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
			group by t2."Name", t1.plan_end_dt
		)
		, v as (
			select sql1.dept_nm
				, sql1.plan_end_dt
				, sum(sql1.tot_cnt) as tot_cnt
				, sum(sql1.finish_cnt) as finish_cnt
				, sum(sql1.not_finish_cnt) as not_finish_cnt
				, sum(sql1.cancle_cnt) as cancle_cnt
			FROM sql1
			group by sql1.dept_nm
				, sql1.plan_end_dt
		)
		, dp as (
			select v.dept_nm
				, v.plan_end_dt
				, sum(v.tot_cnt) as tot_cnt
				, sum(v.finish_cnt) as finish_cnt
				, sum(v.not_finish_cnt) as not_finish_cnt
				, sum(v.cancle_cnt) as cancle_cnt
			FROM v
			GROUP BY ROLLUP(v.dept_nm, v.plan_end_dt)
		)
		, cte as (
			select (case 	when dp.plan_end_dt is null and dp.dept_nm is null then 'TOTSUM'
							when dp.plan_end_dt is null and dp.dept_nm is not null then 'SUBSUM'
								else dp.dept_nm end) as dept_nm
				, dp.plan_end_dt as year_mon
				, dp.tot_cnt
				, dp.finish_cnt
				, dp.not_finish_cnt
				, dp.cancle_cnt
			FROM dp
			order by dp.plan_end_dt asc
		)
		SELECT *
		FROM (
			table cte

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.wm_wo_dept_performance", ex)
            raise ex

        return items

    # 부서별 기간별 작업비용
    def dept_work_costs(self, dateType, startDt, endDt, deptPk):
        items = []
        dic_param = {
            "dateType": dateType,
            "startDt": startDt,
            "endDt": endDt,
            "deptPk": deptPk,
        }

        sql = """
        /* getWorkOrderCost (부서별 기간별 작업 비용) [stat-work-order-mapper.xml] */

		WITH vo AS (
			select coalesce(t2."Name", '-') as dept_nm
				, CASE
					WHEN %(dateType)s = 'MON' THEN to_char(t1.end_dt, 'YYYY.MM')
					WHEN %(dateType)s = 'YEAR' THEN to_char(t1.end_dt, 'YYYY')
					ELSE to_char(t1.end_dt, 'YYYY.MM')
				END as year_mon
				, sum(t1.tot_cost) as tot_cost
				, sum(t1.mtrl_cost) as mtrl_cost
				, sum(t1.labor_cost) as labor_cost
				, sum(t1.outside_cost) as outside_cost
				, sum(t1.etc_cost) as etc_cost
			from cm_work_order t1
			inner join dept t2 on t1.req_dept_pk = t2.id
			inner join cm_work_order_approval t3 on t1.work_order_approval_pk = t3.work_order_approval_pk
			where t1.wo_status = 'WOS_CL'
			and (t1.end_dt >= to_date(%(startDt)s, 'YYYYMMDD') and t1.end_dt <= to_date(%(endDt)s, 'YYYYMMDD'))
			-- and t1.site_id = 'WEZON'
        """
        if deptPk:
            sql += """
				AND (
					t1.req_dept_pk = %(deptPk)s
					OR
					t1.req_dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
			group by t2."Name", t1.end_dt
		)
		, v as (
			select vo.dept_nm
				, vo.year_mon
				, sum(vo.tot_cost) as tot_cost
				, sum(vo.mtrl_cost) as mtrl_cost
				, sum(vo.labor_cost) as labor_cost
				, sum(vo.outside_cost) as outside_cost
				, sum(vo.etc_cost) as etc_cost
			from vo
			group by vo.dept_nm, vo.year_mon
		)
		, v2 as (
			select v.dept_nm
				, v.year_mon
				, sum(v.tot_cost) as tot_cost
				, sum(v.mtrl_cost) as mtrl_cost
				, sum(v.labor_cost) as labor_cost
				, sum(v.outside_cost) as outside_cost
				, sum(v.etc_cost) as etc_cost
			from v
			GROUP BY ROLLUP(v.dept_nm, v.year_mon)
		)
		SELECT (case 	when v2.dept_nm is null and v2.year_mon is null then 'TOTSUM'
						when v2.dept_nm is not null and v2.year_mon is null then 'SUBSUM' else v2.dept_nm end) as dept_nm
		, coalesce(v2.year_mon, '-') as year_mon
		, coalesce(v2.tot_cost, 0) as tot_cost
		, coalesce(v2.mtrl_cost, 0) as mtrl_cost
		, coalesce(v2.labor_cost, 0) as labor_cost
		, coalesce(v2.outside_cost, 0) as outside_cost
		, coalesce(v2.etc_cost, 0) as etc_cost
		FROM v2
		order by v2.year_mon, v2.dept_nm
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.dept_work_costs", ex)
            raise ex

        return items

    # 상위 작업시간 WO
    def top_working_hours_wo(self, startDt, endDt, reqDeptPk, deptPk):
        items = []
        dic_param = {
            "startDt": startDt,
            "endDt": endDt,
            "reqDeptPk": reqDeptPk,
            "deptPk": deptPk,
        }

        sql = """
        /* getWorkOrderHourTop (작업 시간(상위 W/O)) [stat-work-order-mapper.xml] */

		WITH v AS (
			select t1.work_order_no
			, t1.work_title
			, coalesce(t2."Name", '-') as dept_nm
			, coalesce(rd."Name", '-') as req_dept_nm
			, CM_FN_TIMESTAMPDIFF(cast(t1.start_dt as timestamp), cast((t1.end_dt + INTERVAL '1 hour') as timestamp)) as work_hour
			, to_char(t1.start_dt, 'YYYY-MM-DD') as start_dt
			, to_char(t1.end_dt, 'YYYY-MM-DD') as end_dt
			from cm_work_order t1
			left outer join dept t2 on t1.dept_pk = t2.id
			left outer join dept rd on t1.req_dept_pk = rd.id
			inner join cm_work_order_approval t3 on t1.work_order_approval_pk = t3.work_order_approval_pk
			WHERE t1.wo_status = 'WOS_CL'
			AND (t1.end_dt >= to_date(%(startDt)s, 'YYYY-MM-DD') and t1.end_dt <= to_date(%(endDt)s, 'YYYY-MM-DD'))
			AND t1.start_dt is not null and t1.end_dt is not null
			-- and t1.site_id = 'WEZON'

        """
        if reqDeptPk:
            sql += """
				AND (
					t1.req_dept_pk = %(reqDeptPk)s
					OR
					t1.req_dept_pk IN ( select dept_pk from cm_v_dept_path where %(reqDeptPk)s = path_info_pk)
				)
            """
        if deptPk:
            sql += """
				AND (
					t1.dept_pk = %(deptPk)s
					OR
					t1.dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
		)
		, cte as (
			SELECT v.work_order_no
				, v.work_title
				, v.dept_nm
				, v.req_dept_nm
				, coalesce(v.work_hour, 0) as tot_work_hour
				, v.start_dt
				, v.end_dt
			FROM v
		)
		SELECT *
		FROM (
			table cte

	             order by tot_work_hour DESC 

	            -- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.top_working_hours_wo", ex)
            raise ex

        return items

    # 상위 작업비용 WO
    def top_work_cost_wo(self, startDt, endDt, reqDeptPk, deptPk):
        items = []
        dic_param = {
            "startDt": startDt,
            "endDt": endDt,
            "reqDeptPk": reqDeptPk,
            "deptPk": deptPk,
        }

        sql = """
        /* getWorkOrderCostTop (작업 비용(상위 W/O)) [stat-work-order-mapper.xml] */

		WITH v AS (
			select t1.work_order_no
				, t1.work_title
				, coalesce(t2."Name", '-') as dept_nm
				, coalesce(rd."Name", '-') as req_dept_nm
                , CM_FN_TIMESTAMPDIFF(cast((t1.end_dt + INTERVAL '1 hour') as timestamp), cast(t1.start_dt as timestamp)) as work_hour
				, t1.tot_cost as tot_cost
				, t1.mtrl_cost as mtrl_cost
				, t1.labor_cost as labor_cost
				, t1.outside_cost as outside_cost
				, t1.etc_cost as etc_cost
			from cm_work_order t1
			left outer join dept t2 on t1.dept_pk = t2.id
			left outer join dept rd on t1.req_dept_pk = rd.id
			inner join cm_work_order_approval t3 on t1.work_order_approval_pk = t3.work_order_approval_pk
			where t1.wo_status = 'WOS_CL'
			and (t1.end_dt >= to_date(%(startDt)s, 'YYYY-MM-DD') and t1.end_dt <= to_date(%(endDt)s, 'YYYY-MM-DD'))
			and t1.start_dt is not null and t1.end_dt is not null
			-- and t1.site_id = 'WEZON'
        """
        if reqDeptPk:
            sql += """
				AND (
					t1.req_dept_pk = %(reqDeptPk)s
					OR
					t1.req_dept_pk IN ( select dept_pk from cm_v_dept_path where %(reqDeptPk)s = path_info_pk)
				)
            """
        if deptPk:
            sql += """
				AND (
					t1.dept_pk = %(deptPk)s
					OR
					t1.dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
		)
		, cte as (
			SELECT v.work_order_no
				, v.work_title
				, v.dept_nm
				, v.req_dept_nm
				, cast(v.work_hour as integer) as tot_work_hour
 				, v.mtrl_cost
 				, v.labor_cost
 				, v.outside_cost
 				, v.etc_cost
 				, v.tot_cost
			FROM v
		)
		SELECT *
		FROM (
			table cte

	             order by tot_cost DESC 

	            -- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.top_work_cost_wo", ex)
            raise ex

        return items

    # 부서별 예방 정비율
    def dept_pm_rate(self, startDt, endDt, deptPk):
        items = []
        dic_param = {
            "startDt": startDt,
            "endDt": endDt,
            "deptPk": deptPk,
        }

        sql = """
        /* getWorkOrderPmRate (예방 정비율(기간별, 전체 작업 중 PM 작업의 비율)) [stat-work-order-mapper.xml] */

		WITH v as (
			select coalesce(t2."Name", '-') as dept_nm
				, count(t1.work_order_pk) as tot_cnt
				, sum(case when t1.wo_status = 'WOS_CL' then 1 else 0 end) as finish_cnt
				, sum(case when t1.pm_pk is not null then 1 else 0 end) as pm_tot_cnt
				, sum(case when t1.pm_pk is not null and t1.wo_status = 'WOS_CL' then 1 else 0 end) as pm_finish_cnt
			from cm_work_order t1
			left outer join dept t2 on t1.dept_pk = t2.id
			inner join cm_work_order_approval t3 on t1.work_order_approval_pk = t3.work_order_approval_pk
			where t1.wo_status <> 'WOS_DL'
			and (t1.end_dt >= to_date(%(startDt)s, 'YYYY-MM-DD') and t1.end_dt <= to_date(%(endDt)s, 'YYYY-MM-DD'))
			-- and t1.site_id = 'WEZON'
        """
        if deptPk:
            sql += """
				AND (
					t1.dept_pk = %(deptPk)s
					OR
					t1.dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
			GROUP BY t2."Name"
		)
		, cte as (
			SELECT v.dept_nm
				, v.tot_cnt as wo_tot_cnt
				, v.finish_cnt as wo_finish_cnt
				, CAST(case when v.tot_cnt = 0 then 0 else round(cast((coalesce(v.finish_cnt,0)/cast(coalesce(v.tot_cnt,0) as float))*100 as numeric),2) end AS CHAR(5)) as tot_percent
				, v.pm_tot_cnt
				, v.pm_finish_cnt
				, CAST(case when v.pm_tot_cnt = 0 then 0 else round(cast((coalesce(v.pm_finish_cnt,0)/cast(coalesce(v.pm_tot_cnt,0) as float))*100 as numeric),2) end AS CHAR(5)) as pm_percent
			FROM v
		)
		SELECT *
		FROM (
			table cte

	             order by dept_nm ASC 

	            -- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.dept_pm_rate", ex)
            raise ex

        return items

    # 팀별 고장비용 현황
    def team_breakdown_costs(self, searchYear, maintTypeCd, deptPk):
        items = []
        dic_param = {
            "searchYear": searchYear,
            "maintTypeCd": maintTypeCd,
            "deptPk": deptPk,
        }

        sql = """
        /* getTeamBreakDownCostStatus (팀별 보전비용 현황) [stat-require-mapper.xml] */

		 with t as (
		 	select 1 as RN, d.id as dept_pk, d."Name" as dept_nm, 'cost' as rslt_type
		 	, 0 as rslt_m1, 0 as rslt_m2, 0 as rslt_m3, 0 as rslt_m4, 0 as rslt_m5, 0 as rslt_m6, 0 as rslt_m7, 0 as rslt_m8, 0 as rslt_m9, 0 as rslt_m10, 0 as rslt_m11, 0 as rslt_m12, 0 as rslt_sum
		 	, 0 as curr_m, 0 as curr_sum

	            , cm_fn_get_dept_team_pk(d.id) as team_dept_pk
	            , cm_fn_get_dept_team_nm(d.id) as team_dept_nm

		 	from dept d
		 	where 1=1 and d."UseYN" = 'Y' and d."DelYN" = 'N'
            -- AND d.site_id = 'WEZON'
		 	union all
		 	select 2 as RN, d.id, d."Name", 'count' as rslt_type
		 	, 0 as rslt_m1, 0 as rslt_m2, 0 as rslt_m3, 0 as rslt_m4, 0 as rslt_m5, 0 as rslt_m6, 0 as rslt_m7, 0 as rslt_m8, 0 as rslt_m9, 0 as rslt_m10, 0 as rslt_m11, 0 as rslt_m12, 0 as rslt_sum
		 	,  0 as curr_m, 0 as curr_sum
            , cm_fn_get_dept_team_pk(d.id) as team_dept_pk
            , cm_fn_get_dept_team_nm(d.id) as team_dept_nm
		 	from dept d
		 	where 1=1 and d."UseYN" = 'Y' and d."DelYN" = 'N'
            -- AND d.site_id = 'WEZON'
		 )
		 , tt as (
		 	select t.RN
                , t.team_dept_pk as dept_pk
                , t.team_dept_nm as dept_nm
			 	, t.rslt_type

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '01') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '01') then 1 else 0 end) as rslt_m1

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '02') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '02') then 1 else 0 end) as rslt_m2

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '03') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '03') then 1 else 0 end) as rslt_m3

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '04') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '04') then 1 else 0 end) as rslt_m4

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '05') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '05') then 1 else 0 end) as rslt_m5

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '06') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '06') then 1 else 0 end) as rslt_m6

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '07') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '07') then 1 else 0 end) as rslt_m7

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '08') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '08') then 1 else 0 end) as rslt_m8

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '09') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '09') then 1 else 0 end) as rslt_m9

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '10') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '10') then 1 else 0 end) as rslt_m10

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '11') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '11') then 1 else 0 end) as rslt_m11

	            	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '12') then wo.tot_cost
	            		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') = CONCAT(%(searchYear)s, '12') then 1 else 0 end) as rslt_m12

				, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYY') =  %(searchYear)s  then wo.tot_cost
			   		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYY') =  %(searchYear)s then 1 else 0 end) as rslt_sum
			   	, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYY') =  ((%(searchYear)s)::int - 1)::text then wo.tot_cost
		    		when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYY') =  ((%(searchYear)s)::int - 1)::text then 1 else 0 end) as curr_sum
				, sum(case when t.rslt_type = 'cost' and to_char(wo.end_dt, 'YYYYMM') = concat(((%(searchYear)s)::int - 1)::text,TO_CHAR(current_date, 'MM'))  then wo.tot_cost
					 when t.rslt_type = 'count' and to_char(wo.end_dt, 'YYYYMM') =  concat(((%(searchYear)s)::int - 1)::text,TO_CHAR(current_date, 'MM')) then 1 else 0 end) as curr_m
			from t
			inner join cm_work_order wo on t.dept_pk = wo.req_dept_pk
			and wo.wo_type != 'PM'
			and wo.wo_status = 'WOS_CL'
			-- and wo.site_id = 'WEZON'
			and to_char(wo.end_dt, 'YYYY') in (%(searchYear)s, ((%(searchYear)s)::int - 1)::text)
            """
        if maintTypeCd:
            if isinstance(maintTypeCd, str):
                maintTypeCd_list = [item.strip() for item in maintTypeCd.split(',') if item.strip()]
            elif isinstance(maintTypeCd, list):
                maintTypeCd_list = maintTypeCd
            else:
                maintTypeCd_list = [maintTypeCd]
            
            if maintTypeCd_list:
                maintTypeCd_str = ','.join([f"'{item}'" for item in maintTypeCd_list])
                sql += f'''
                    and wo.maint_type_cd in ( {maintTypeCd_str} )
                '''
        if deptPk:
            sql += """
		  		AND (
					wo.req_dept_pk = %(deptPk)s
					OR
					wo.req_dept_pk In (select dept_pk from cm_v_dept_path where cast(%(deptPk)s as integer) = path_info_pk)
				)
            """
        sql += """
			group by t.RN
	            , t.team_dept_pk
	            , t.team_dept_nm
				, t.rslt_type
		)
		select concat(tt.RN, '_', tt.dept_pk) as row_key
		, tt.dept_pk
		, tt.dept_nm
		, tt.rslt_type
		, tt.rslt_m1
		, tt.rslt_m2
		, tt.rslt_m3
		, tt.rslt_m4
		, tt.rslt_m5
		, tt.rslt_m6
		, tt.rslt_m7
		, tt.rslt_m8
		, tt.rslt_m9
		, tt.rslt_m10
		, tt.rslt_m11
		, tt.rslt_m12
		, tt.rslt_sum
		, tt.curr_m
		, tt.curr_sum
		from tt
		where tt.dept_pk is not null
		order by tt.dept_nm, tt.rslt_type
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.team_breakdown_costs", ex)
            raise ex

        return items

    # 부서별 기간별 지연작업 목록
    def dept_overdue_tasks(self, startDt, endDt, deptPk, reqDeptPk):
        items = []
        dic_param = {
            "startDt": startDt,
            "endDt": endDt,
            "deptPk": deptPk,
            "reqDeptPk": reqDeptPk,
        }

        sql = """
        /* getWorkOrderDelayList (지연 작업 목록(종료일이 계획보다 지체된 것)) [stat-work-order-mapper.xml] */

		with v as (
			select t1.work_order_no
				, t1.work_title
				, coalesce(t2."Name", '-') as dept_nm
				, coalesce(rd."Name", '-') as req_dept_nm
				, to_char(t1.plan_end_dt, 'YYYY-MM-DD') as plan_end_dt
				, to_char(t1.end_dt, 'YYYY-MM-DD') as end_dt
				, cm_fn_datediff(cast(coalesce(t1.end_dt, now()) as timestamp), plan_end_dt) as delay_days
			from cm_work_order t1
			left outer join dept t2 on t1.dept_pk = t2.id
			left outer join dept rd on t1.req_dept_pk = rd.id
			where t1.wo_status = 'WOS_CL'
			and (coalesce(t1.end_dt, now()) >= to_date(%(startDt)s, 'YYYY-MM-DD') and coalesce(t1.end_dt, now()) <= to_date(%(endDt)s, 'YYYY-MM-DD'))
			and coalesce(t1.end_dt, now()) > t1.plan_end_dt
			-- and t1.site_id = 'WEZON'
        """
        if reqDeptPk:
            sql += """
				AND (
					t1.req_dept_pk = %(reqDeptPk)s
					OR
					t1.req_dept_pk IN ( select dept_pk from cm_v_dept_path where %(reqDeptPk)s = path_info_pk)
				)
            """
        if deptPk:
            sql += """
				AND (
					t1.dept_pk = %(deptPk)s
					OR
					t1.dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
		)
		, cte as (
			SELECT v.work_order_no
				, v.work_title
				, v.dept_nm
				, v.req_dept_nm
				, v.plan_end_dt
				, v.end_dt
				, v.delay_days
			FROM v
			WHERE v.delay_days > 0
		)
		SELECT *
		FROM (
			table cte

	             order by work_order_no ASC 

	            -- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.dept_overdue_tasks", ex)
            raise ex

        return items

    # 부서별 기간별 작업 준수율
    def dept_task_compliance_rate(self, dateType, startDt, endDt):
        items = []
        dic_param = {
            "dateType": dateType,
            "startDt": startDt,
            "endDt": endDt,
        }
        
        sql = """
        /* getWorkOrderComplyWithRate (부서별 기간별 작업 준수율(지연되지 않은 작업 비율, 기간별, 부서 등의 기타 구분) - 목록, 계획완료일기준) [stat-work-order-mapper.xml] */

		with sql1 as (
			select coalesce(t2."Name", '-') as dept_nm
				,
                CASE
                    WHEN %(dateType)s = 'MON' THEN to_char(t1.end_dt, 'YYYY.MM')
                    WHEN %(dateType)s = 'YEAR' THEN to_char(t1.end_dt, 'YYYY')
                    ELSE to_char(t1.end_dt, 'YYYY.MM')
                END as year_mon
				, count(t1.work_order_pk) as tot_wo_cnt
				, sum(case when t1.end_dt > t1.plan_end_dt then 0 else 1 end) as ok_wo_cnt
			from cm_work_order t1
			left outer join dept t2 on t1.dept_pk = t2.id
			where t1.wo_status = 'WOS_CL'
			and (t1.end_dt >= to_date(%(startDt)s, 'YYYYMMDD') and t1.end_dt <= to_date(%(endDt)s, 'YYYYMMDD'))
			-- and t1.site_id = 'WEZON'
			group by t2."Name", t1.end_dt
		),
		v as (
			select sql1.dept_nm
				, sql1.year_mon
				, sum(sql1.tot_wo_cnt) as tot_wo_cnt
				, sum(sql1.ok_wo_cnt) as ok_wo_cnt
			from sql1
			group by sql1.dept_nm, sql1.year_mon
		)

		, vo as (
			SELECT v.dept_nm
				, v.year_mon
				, v.tot_wo_cnt
				, v.ok_wo_cnt
				, (case when v.tot_wo_cnt = 0 then 0 else round(cast((v.ok_wo_cnt/cast(v.tot_wo_cnt as float))*100 as numeric),2) end) as ok_percent
			FROM v
		)

		, cte as (
			SELECT vo.dept_nm
				, vo.year_mon
				, vo.tot_wo_cnt
				, vo.ok_wo_cnt
				, vo.ok_percent
			FROM vo
		)
		SELECT *
		FROM (
			table cte

	             order by year_mon ASC 

	            -- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.dept_task_compliance_rate", ex)
            raise ex

        return items

    # 부서별 작업 요청 통계
    def dept_work_request_stats(self, dateType, startDt, endDt, reqDeptPk, deptPk):
        items = []
        dic_param = {
            "dateType": dateType,
            "startDt": startDt,
            "endDt": endDt,
            "reqDeptPk": reqDeptPk,
            "deptPk": deptPk,
        }

        sql = """
        /* getWorkOrderRequestStat (작업 요청 통계(요청 수)) [stat-work-order-mapper.xml] */

			with v as (
				-- select to_char(t3.reg_dt, 'YYYY') as yyyy_mm
                select 
                CASE
                    WHEN %(dateType)s = 'MON' THEN to_char(t3.reg_dt, 'YYYY.MM')
                    WHEN %(dateType)s = 'YEAR' THEN to_char(t3.reg_dt, 'YYYY')
                    ELSE to_char(t3.reg_dt, 'YYYY.MM')
                END as yyyy_mm
				, coalesce(t2."Name", '-') as dept_nm
				, count(t1.work_order_pk) as req_cnt
				, sum(case when t1.wo_status = 'WOS_DL' then 1 else 0 end) as cancel_cnt
				, sum(case when t1.wo_status = 'WOS_CL' then 1 else 0 end) as finish_cnt
				, sum(case when t1.wo_status NOT IN ('WOS_CL','WOS_DL','WOS_RW') then 1 else 0 end) as not_finish_cnt
				from cm_work_order t1
				left outer join dept t2 on t1.dept_pk = t2.id
				inner join cm_work_order_approval t3 on t1.work_order_approval_pk = t3.work_order_approval_pk
				WHERE t3.reg_dt is not null
				AND t1.wo_status <> 'WOS_DL'
			 	AND (t3.reg_dt >= to_date(%(startDt)s, 'YYYYMMDD') and t3.reg_dt <= to_date(%(endDt)s, 'YYYYMMDD'))
			 	-- and t1.site_id = 'WEZON'
        """
        if reqDeptPk:
            sql += """
				AND (
					t1.req_dept_pk = %(reqDeptPk)s
					OR
					t1.req_dept_pk IN ( select dept_pk from cm_v_dept_path where %(reqDeptPk)s = path_info_pk)
				)
            """
        if deptPk:
            sql += """
				AND (
					t1.dept_pk = %(deptPk)s
					OR
					t1.dept_pk IN ( select dept_pk from cm_v_dept_path where %(deptPk)s = path_info_pk)
				)
            """
        sql += """
				-- group by to_char(t3.reg_dt, 'YYYY'), t2."Name"
                group by 
                case 
                    when %(dateType)s = 'MON' then to_char(t3.reg_dt, 'YYYY.MM')
                    when %(dateType)s = 'YEAR' then to_char(t3.reg_dt, 'YYYY')
                    else to_char(t3.reg_dt, 'YYYY.MM')
                end
                , coalesce(t2."Name", '-')
				order by yyyy_mm

		)
		, cte as (
			SELECT v.yyyy_mm
				, v.dept_nm
				, v.req_cnt
				, v.cancel_cnt
				, v.finish_cnt
				, v.not_finish_cnt
			FROM v
		)
		SELECT *
		FROM (
			table cte

	            -- limit 30 offset (1-1)*30

		) sub
		RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		WHERE total_rows != 0
        """

        try:
            items = DbUtil.get_rows(sql, dic_param)
            items = CommonUtil.res_snake_to_camel(items)
        except Exception as ex:
            LogWriter.add_dblog("error", "CmReportService.dept_work_request_stats", ex)
            raise ex

        return items