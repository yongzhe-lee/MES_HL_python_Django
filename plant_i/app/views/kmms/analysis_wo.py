from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
#from domain.models.cmms import CmExSupplier, CmWorkOrderSupplier

def analysis_wo(context):
    '''
    api/kmms/analysis_wo    
    김태영 

    selectAllAnalysisWoList
    searchReliability
    equipClassSearch
    problemSearch
    causeSearch
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    def findDeletableExSupplier(exSupplierPk):
        q = CmWorkOrderSupplier.objects.filter(CmExSupplier_id=exSupplierPk)
        if q.first():
            return 1
        else:
            return 0

    try:
        if action == 'selectAllAnalysisWoList':
            searchText = gparam.get('searchText')
            pageSize = CommonUtil.try_int( gparam.get('pageSize') )
            page = CommonUtil.try_int(gparam.get('page'))

            sql = ''' with cte as ( SELECT *
			 FROM  (
                SELECT t.work_order_pk
				, t.work_order_no
				, t.work_title
				, REGEXP_REPLACE(t.req_info, '<[^>]*>|\&([^;])*;', '', 'g') AS req_info
				, REGEXP_REPLACE(t.work_text, '<[^>]*>|\&([^;])*;', '', 'g') AS work_text
				, POSITION (array_to_string(REGEXP_MATCHES(t.req_info, %(searchText)s), ',') IN REGEXP_REPLACE(t.req_info, '<[^>]*>|\&([^;])*;', '', 'g')) AS req_info_position
				, POSITION (array_to_string(REGEXP_MATCHES(t.work_text, %(searchText)s), ',') IN REGEXP_REPLACE(t.work_text, '<[^>]*>|\&([^;])*;', '', 'g')) AS work_text_position
				, woa.rqst_user_nm
				, to_char(woa.rqst_dt, 'YYYY. fmMM. fmDD') AS rqst_dt
				, woa.work_finish_user_nm
				, to_char(woa.finish_dt, 'YYYY. fmMM. fmDD') AS work_finish_dt
			    , ts_rank_cd(to_tsvector(t.req_info) || to_tsvector(t.work_text), query) AS score
			    FROM cm_work_order AS t
				INNER JOIN cm_work_order_approval AS woa ON t.work_order_approval_pk = woa.work_order_approval_pk
				INNER JOIN to_tsquery(%(searchText)s) query on 1=1
			    WHERE t.wo_type = 'WO'
			    AND t.wo_status in('WOS_CL') /* 완료 WOS_CL */
			    AND to_tsvector(t.work_text)  @@ query
			    AND t.factory_pk = %(factory_pk)s
		   		) AS sc
		    WHERE sc.score > 0
		    ORDER BY sc.score desc
		    )
		    SELECT work_order_pk
			     , work_order_no
			     , SUBSTRING(work_title, 0, 60) AS work_title
			     , COALESCE(CASE when req_info_position > 20 THEN SUBSTRING (req_info, req_info_position - 10, 80)
			 		    ELSE SUBSTRING (req_info, 0, 80)
			       END, '(정보없음)') AS req_info
			     , COALESCE(CASE when work_text_position > 20 THEN SUBSTRING (work_text, work_text_position - 10, 80)
			 		    ELSE SUBSTRING (work_text, 0, 80)
			       END, '(정보없음)') AS work_text
			     , rqst_user_nm
		         , rqst_dt
		         , COALESCE(work_finish_user_nm, '(정보없음)') AS work_finish_user_nm
		         , COALESCE(work_finish_dt, '(정보없음)') AS work_finish_dt
			     , total_rows
		    FROM (
			    table cte
			    order by cte.score desc
	           -- limit %(pageSize)s offset (%(page)s-1)*%(pageSize)s
		    ) sub
		    RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		    WHERE total_rows != 0
            '''

            dc = {}
            dc['pageSize'] = pageSize
            dc['page'] = page
            dc['searchText'] = searchText
            dc['factory_pk'] = factory_id

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'searchReliability':
            searchYear =  gparam.get('searchYear') 
            importRankPk = CommonUtil.try_int( gparam.get('importRankPk') )
            equipCategoryId = posparam.get('equipCategoryId')
            equipClassId = posparam.get('equipClassId')

            sql = ''' with base as (
		        select wo.work_order_pk, string_agg(rc.reliab_nm  , ',') as faulty_part
		        , e.equip_class_path, e.equip_class_desc, ir.import_rank_cd
		        from cm_work_order wo
                left join cm_equipment e on e.equip_pk = wo.equip_pk
                left join cm_equip_category ec on ec.equip_category_id = e.equip_category_id
		        left join cm_wo_fault_loc wfl on wfl.work_order_pk = wo.work_order_pk
		        left join cm_reliab_codes rc on rc.reliab_cd = wfl.fault_loc_cd
		        and rc."types" = 'FC' 
		        and rc.factory_pk = wo.factory_pk
			    left join cm_import_rank ir on ir.import_rank_pk = e.import_rank_pk
		        where 1=1
                and wo.wo_status = 'WOS_CL'
                and wo.wo_type ='WO'
                and wo.maint_type_cd = 'MAINT_TYPE_BM'
                AND wo.factory_pk = %(factory_pk)s
                '''
            if searchYear:
                sql += ''' AND to_char(wo.end_dt,'YYYY') = %(searchYear)s
                '''
            if importRankPk > 0:
                sql += ''' AND e.import_rank_pk = %(importRankPk)s
                '''
            elif importRankPk == -1:
                sql += ''' AND e.import_rank_pk is null
                '''
            if equipCategoryId:
                sql += ''' AND ec.equip_category_id = %(equipCategoryId)s
                '''
            if equipClassId:
                sql += ''' AND e.equip_class_path = %(equipClassId)s
                '''
            sql += ''' group by wo.work_order_pk, e.equip_class_path, e.equip_class_desc, ir.import_rank_cd
		    ), cte as (
                select 1 as rownum, base.equip_class_path, base.equip_class_desc, base.faulty_part
                 , wo.problem_cd, pp.reliab_nm as problem_nm
                 , wo.cause_cd, cp.reliab_nm as cause_nm
                 , wo.remedy_cd, rp.reliab_nm as remedy_nm
                 , sum(case when EXTRACT(month from wo.end_dt ) between 1 and 3 then 1 else 0 end) as q1
                 , sum(case when EXTRACT(month from wo.end_dt ) between 4 and 6 then 1 else 0 end) as q2
                 , sum(case when EXTRACT(month from wo.end_dt ) between 7 and 9 then 1 else 0 end) as q3
                 , sum(case when EXTRACT(month from wo.end_dt ) between 10 and 12 then 1 else 0 end) as q4
                 , sum(case when EXTRACT(month from wo.end_dt ) between 1 and 12 then 1 else 0 end) as qsum
			     , base.import_rank_cd
                from base
                inner join cm_work_order wo on base.work_order_pk = wo.work_order_pk
                left join cm_reliab_codes pp on pp.reliab_cd = wo.problem_cd
                and pp.use_yn = 'Y' 
                and pp."types" = 'PC' 
                and pp.factory_pk = wo.factory_pk
                left join cm_reliab_codes cp on cp.reliab_cd = wo.cause_cd 
                and cp.use_yn = 'Y' 
                and cp."types" = 'CC' 
                and cp.factory_pk = wo.factory_pk
                left join cm_reliab_codes rp on rp.reliab_cd = wo.remedy_cd  
                and rp.use_yn = 'Y' and rp."types" = 'RC' 
                and rp.factory_pk = wo.factory_pk
                where 1=1
                group by base.equip_class_path, base.equip_class_desc, base.faulty_part,
                wo.problem_cd, pp.reliab_nm, wo.cause_cd, cp.reliab_nm, wo.remedy_cd, rp.reliab_nm, base.import_rank_cd
                order by qsum desc
		    )
		    SELECT *
		    FROM cte
            '''

            dc = {}
            dc['searchYear'] = searchYear
            dc['importRankPk'] = importRankPk
            dc['equipCategoryId'] = equipCategoryId
            dc['equipClassId'] = equipClassId
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)


        elif action == 'equipClassSearch':
            equipClasify =  gparam.get('equipClasify') 
            importRankPk = CommonUtil.try_int( gparam.get('importRankPk') )
            chartData = posparam.get('chartData')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')

            sql = ''' with cte as (
            '''
            if equipClasify == 'CLASS':
                sql += ''' SELECT case when ec2.class_type = 'CLASS' then coalesce(e.equip_class_path, '') else coalesce(ec3.equip_class_id, '') end as code_cd
				    , case when ec2.class_type = 'CLASS' then coalesce(e.equip_class_desc, '미지정') else coalesce(ec3.equip_class_desc, '미지정') end as code_nm
                    '''
            elif equipClasify == 'TYPES':
                sql += ''' SELECT coalesce(e.equip_class_path, '') as code_cd
		        , coalesce(ec3.equip_class_desc, '') || (case when ec3.equip_class_desc is null then '' else '-' end) || coalesce(e.equip_class_desc, '미지정') as code_nm
                    '''
            if chartData == 'WORKCOST':
                sql += ''', sum(wo.tot_cost) as cost
                '''
            elif chartData == 'WORKCOUNT':
                sql += ''', count(distinct wo.work_order_pk) as cost
                '''
            elif chartData == 'BROKENHOUR':
                sql += ''', ssum(wo.breakdown_min) as cost
                '''
            elif chartData == 'WORKHOUR':
                sql += ''' , sum(round(((date_part('day', wo.end_dt::timestamp - wo.start_dt::timestamp)*24*60
	                + date_part('hour', wo.end_dt::timestamp - wo.start_dt::timestamp)*60
	                + date_part('minute', wo.end_dt::timestamp - wo.start_dt::timestamp))/60)::numeric, 0)) as cost
                    '''
            else:
                sql += ''', sum(wo.tot_cost) as cost
                '''
            sql += ''' FROM cm_work_order wo
			INNER JOIN cm_equipment e ON e.equip_pk = wo.equip_pk
			INNER JOIN cm_equip_category ec ON ec.equip_category_id = e.equip_category_id
            '''
            if equipClasify == 'CLASS':
                sql += ''' left join cm_equip_classify ec2 on ec2.hierarchy_path = e.equip_class_path
			    AND ec2.class_type in ( 'TYPES', 'CLASS')
			    left join cm_equip_classify ec3 ON ec3.equip_class_id = ec2.parent_id
			    and ec3.class_type = 'CLASS'
                '''
            elif equipClasify == 'TYPES':
                sql += ''' left join equip_classify ec2 ON ec2.hierarchy_path = e.equip_class_path
	            AND ec2.class_type = 'TYPES'
	            left join equip_classify ec3 ON ec3.equip_class_id = ec2.parent_id
                and ec3.class_type = 'CLASS'
                '''
            sql += ''' LEFT JOIN cm_reliab_codes pp ON pp.reliab_cd = wo.problem_cd 
		    and pp.use_yn = 'Y' 
            and pp."types" = 'PC' 
		    and pp.factory_pk = wo.factory_pk
			LEFT JOIN cm_reliab_codes cp ON wo.cause_cd  = cp.reliab_cd 
			and cp.use_yn = 'Y' 
			and cp."types" = 'CC' 
			and cp.factory_pk = wo.factory_pk
			LEFT JOIN cm_reliab_codes rp ON wo.remedy_cd  = rp.reliab_cd  
			and rp.use_yn = 'Y' 
			and rp."types" = 'RC' 
			and rp.factory_pk = wo.factory_pk
			WHERE wo.factory_pk = %(factory_pk)s
            '''
            if startDate and endDate:
                sql += ''' AND to_char(end_dt,'yyyy-mm-dd') >= %(startDate)s and to_char(end_dt,'yyyy-mm-dd') <= %(endDate)s
                '''
            sql += ''' AND wo_type = 'WO' 
			and maint_type_cd = 'MAINT_TYPE_BM' 
			and wo.wo_status = 'WOS_CL'
            '''
            if chartData == 'WORKCOST':
                sql += ''' AND wo.tot_cost > 0
                '''
            elif chartData == 'BROKENHOUR':
                sql += ''' AND wo.breakdown_min > 0
                '''
            elif chartData == 'WORKHOUR':
                sql += ''' AND round(((date_part('day', wo.end_dt::timestamp - wo.start_dt::timestamp)*24*60
	                + date_part('hour', wo.end_dt::timestamp - wo.start_dt::timestamp)*60
	                + date_part('minute', wo.end_dt::timestamp - wo.start_dt::timestamp))/60)::numeric, 0) > 0
                '''
            sql += ''' AND round(((date_part('day', wo.end_dt::timestamp - wo.start_dt::timestamp)*24*60
	                + date_part('hour', wo.end_dt::timestamp - wo.start_dt::timestamp)*60
	                + date_part('minute', wo.end_dt::timestamp - wo.start_dt::timestamp))/60)::numeric, 0) > 0
                    '''
            if equipClasify == 'CLASS':
                sql += ''' AND (ec2.class_type in ('CLASS', 'TYPES') OR e.equip_class_desc is null)
                GROUP BY e.equip_class_path, e.equip_class_desc, ec2.class_type, ec3.equip_class_desc, ec3.equip_class_id
                '''
            elif equipClasify == 'TYPES':
                sql += ''' AND (ec2.class_type = 'TYPES' OR e.equip_class_desc is null)
			    GROUP BY e.equip_class_path, e.equip_class_desc, ec3.equip_class_desc
                '''
            sql += ''' )
	        select sub.code_cd, sub.code_nm, sum(sub.cost) as cost
		    FROM (
			    table cte
			    order by cte.cost desc
			    limit 10 offset (1-1)*10
		    ) sub
		    RIGHT JOIN (select count(*) from cte) c(total_rows) on true
		    WHERE total_rows != 0
	        group by sub.code_cd, sub.code_nm
		    order by cost desc
            '''

            dc = {}
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'problemSearch':
            equipClasify =  gparam.get('equipClasify') 
            #importRankPk = CommonUtil.try_int( gparam.get('importRankPk') )
            chartData = posparam.get('chartData')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            typeVal = posparam.get('typeVal')

            sql = ''' select bc.reliab_cd as code_cd, bc.reliab_nm as code_nm
            '''
            if chartData == 'WORKCOST':
                sql += ''', sum(wo.tot_cost) as cost
                '''
            elif chartData == 'WORKCOUNT':
                sql += ''', count(distinct wo.work_order_pk) as cost
                '''
            elif chartData == 'BROKENHOUR':
                sql += ''', sum(wo.breakdown_min) as cost
                '''
            elif chartData == 'WORKHOUR':
                sql += ''', sum(round(((date_part('day', wo.end_dt::timestamp - wo.start_dt::timestamp)*24*60
				+ date_part('hour', wo.end_dt::timestamp - wo.start_dt::timestamp)*60
				+ date_part('minute', wo.end_dt::timestamp - wo.start_dt::timestamp))/60)::numeric, 0)) as cost
                '''
            else:
                sql += ''', sum(wo.tot_cost) as cost
                '''
            sql += ''' FROM cm_work_order wo
			INNER JOIN cm_equipment e ON e.equip_pk = wo.equip_pk
			INNER JOIN cm_equip_category ec ON ec.equip_category_id = e.equip_category_id
            '''
            if equipClasify == 'CLASS':
                sql += ''' left join cm_equip_classify ec2 on ec2.hierarchy_path = e.equip_class_path
			    AND ec2.class_type in ( 'TYPES', 'CLASS')
			    left join cm_equip_classify ec3 ON ec3.equip_class_id = ec2.parent_id
			    and ec3.class_type = 'CLASS'
                '''
            elif equipClasify == 'TYPES':
                sql += ''' left join equip_classify ec2 ON ec2.hierarchy_path = e.equip_class_path
	            AND ec2.class_type = 'TYPES'
	            left join equip_classify ec3 ON ec3.equip_class_id = ec2.parent_id
                and ec3.class_type = 'CLASS'
                '''
            sql += ''' LEFT JOIN cm_reliab_codes bc ON bc.reliab_cd = wo.problem_cd 
		    and bc.use_yn = 'Y' 
            and bc."types" = 'PC' 
            and bc.factory_pk = wo.factory_pk
			WHERE wo.factory_pk = %(factory_pk)s
            '''
            if startDate and endDate:
                sql += ''' AND to_char(end_dt,'yyyy-mm-dd') >= %(startDate)s and to_char(end_dt,'yyyy-mm-dd') <= %(endDate)s
                '''
            if typeVal:
                if equipClasify == 'CLASS':
                    sql += ''' and case when ec2.class_type = 'CLASS' then coalesce(e.equip_class_path, '') else coalesce(ec3.equip_class_id, '') end = %(typeVal)s
                    '''
                elif equipClasify == 'TYPES':
                    sql += ''' and ec2.hierarchy_path = %(typeVal)s
                    '''
            else:
                sql += ''' and ec2.hierarchy_path IS NULL
                '''
            sql += ''' AND wo_type = 'WO' 
			and maint_type_cd = 'MAINT_TYPE_BM' 
			and wo.wo_status = 'WOS_CL'
            '''
            if equipClasify == 'CLASS':
                sql += ''' AND (ec2.class_type in ('CLASS', 'TYPES') OR e.equip_class_desc is null)
                '''
            elif equipClasify == 'TYPES':
                sql += ''' AND (ec2.class_type = 'TYPES' OR e.equip_class_desc is null)
                '''
            sql += ''' group by bc.reliab_cd, bc.reliab_nm
		    order by cost desc
            '''

            dc = {}
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['typeVal'] = typeVal
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)

        elif action == 'causeSearch':
            equipClasify =  gparam.get('equipClasify') 
            #importRankPk = CommonUtil.try_int( gparam.get('importRankPk') )
            chartData = posparam.get('chartData')
            startDate = posparam.get('startDate')
            endDate = posparam.get('endDate')
            typeVal = posparam.get('typeVal')
            problemVal = posparam.get('problemVal')

            sql = ''' select ca.reliab_cd as code_cd, ca.reliab_nm as code_nm
            '''
            if chartData == 'WORKCOST':
                sql += ''', sum(wo.tot_cost) as cost
                '''
            elif chartData == 'WORKCOUNT':
                sql += ''', count(distinct wo.work_order_pk) as cost
                '''
            elif chartData == 'BROKENHOUR':
                sql += ''', sum(wo.breakdown_min) as cost
                '''
            elif chartData == 'WORKHOUR':
                sql += ''', sum(round(((date_part('day', wo.end_dt::timestamp - wo.start_dt::timestamp)*24*60
				+ date_part('hour', wo.end_dt::timestamp - wo.start_dt::timestamp)*60
				+ date_part('minute', wo.end_dt::timestamp - wo.start_dt::timestamp))/60)::numeric, 0)) as cost
                '''
            else:
                sql += ''', sum(wo.tot_cost) as cost
                '''
            sql += ''' FROM cm_work_order wo
			INNER JOIN cm_equipment e ON e.equip_pk = wo.equip_pk
			INNER JOIN cm_equip_category ec ON ec.equip_category_id = e.equip_category_id
            '''
            if equipClasify == 'CLASS':
                sql += ''' left join cm_equip_classify ec2 on ec2.hierarchy_path = e.equip_class_path
			    AND ec2.class_type in ( 'TYPES', 'CLASS')
			    left join cm_equip_classify ec3 ON ec3.equip_class_id = ec2.parent_id
			    and ec3.class_type = 'CLASS'
                '''
            elif equipClasify == 'TYPES':
                sql += ''' left join equip_classify ec2 ON ec2.hierarchy_path = e.equip_class_path
	            AND ec2.class_type = 'TYPES'
	            left join equip_classify ec3 ON ec3.equip_class_id = ec2.parent_id
                and ec3.class_type = 'CLASS'
                '''
            sql += ''' inner join cm_reliab_codes pb ON pb.reliab_cd = wo.problem_cd 
		    and pb.use_yn = 'Y' 
            and pb."types" = 'PC' 
            and pb.factory_pk = wo.factory_pk
            and pb.reliab_cd = %(problemVal)s
            inner join cm_reliab_codes ca ON ca.reliab_cd = wo.cause_cd 
		    and ca.use_yn = 'Y' 
            and ca."types" = 'CC' 
            and ca.factory_pk = wo.factory_pk
			WHERE wo.factory_pk = %(factory_pk)s
            '''
            if startDate and endDate:
                sql += ''' AND to_char(wo.end_dt,'yyyy-mm-dd') >= %(startDate)s and to_char(wo.end_dt,'yyyy-mm-dd') <= %(endDate)s
                '''
            if typeVal:
                if equipClasify == 'CLASS':
                    sql += ''' and case when ec2.class_type = 'CLASS' then coalesce(e.equip_class_path, '') else coalesce(ec3.equip_class_id, '') end = %(typeVal)s
                    '''
                elif equipClasify == 'TYPES':
                    sql += ''' and ec2.hierarchy_path = %(typeVal)s
                    '''
            else:
                sql += ''' and ec2.hierarchy_path IS NULL
                '''
            sql += ''' AND wo_type = 'WO' 
			and maint_type_cd = 'MAINT_TYPE_BM' 
			and wo.wo_status = 'WOS_CL'
            '''
            if equipClasify == 'CLASS':
                sql += ''' AND (ec2.class_type = 'CLASS' OR e.equip_class_desc is null)
                '''
            elif equipClasify == 'TYPES':
                sql += ''' AND (ec2.class_type = 'TYPES' OR e.equip_class_desc is null)
                '''
            sql += ''' group by ca.reliab_cd, ca.reliab_nm
		    order by cost desc
            '''

            dc = {}
            dc['startDate'] = startDate
            dc['endDate'] = endDate
            dc['problemVal'] = problemVal
            dc['typeVal'] = typeVal
            dc['factory_pk'] = factory_id

            items = DbUtil.get_row(sql, dc)
    except Exception as ex:
        source = 'kmms/analysis_wo : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items

    return items