import numpy as np

from configurations import settings
from domain.models.definition import TagMaster
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.services.system_definition.tag_data import TagDataService
from domain.services.calculation.box_plot import BoxPlot
from domain.services.calculation.regression import RegressionCalc
from domain.services.calculation.histogram import HistogramCalc


def tag_statistics(context):

    items = []
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action')
    result = {}
    
    try:
        if action=='read':
            start_date = gparam.get('start_date', '')
            end_date = gparam.get('end_date', '')
            tag_code = gparam.get('tag_code', '')
            tag_group_pk = gparam.get('tag_group_pk', '')
            # 25.06.19 김하늘 전체 데이터 조회 조건 수정(아무 조건 없을 때)
            # em_tag_dat 반영 -> table명 분기가 아닌 union으로 처리
            if not tag_code and not tag_group_pk:
                sql = '''
                WITH merged AS (
                    SELECT 
                        t.tag_group_id,
                        td.tag_code,
                        t.tag_name,
                        td.data_value
                    FROM das.tag_dat td
                    INNER JOIN tag t ON t.tag_code = td.tag_code
                    WHERE 
                        td.data_date BETWEEN %(date_from)s AND %(date_to)s::date + interval '1 days'
                        AND td.data_value IS NOT NULL

                    UNION ALL

                    SELECT 
                        t.tag_group_id,
                        td.tag_code,
                        t.tag_name,
                        td.data_value
                    FROM das.em_tag_dat td
                    INNER JOIN tag t ON t.tag_code = td.tag_code
                    WHERE 
                        td.data_date BETWEEN %(date_from)s AND %(date_to)s::date + interval '1 days'
                        AND td.data_value IS NOT NULL
                )
                -- 주석 처리된 조건은 이미 union할 때 반영됨
                SELECT
                    -- tg."Name" || '(' || tg."Code" || ')' AS tag_group
                    tag_code
                    , tag_name
                    , count(*) AS count_value
                    , avg(data_value) AS avg_value
                    , min(data_value) AS min_value
                    , max(data_value) AS max_value
                    , round(stddev(data_value)::decimal,5) AS std_value
	            FROM merged
                -- inner join tag t ON t.tag_code = td.tag_code
                LEFT JOIN tag_grp tg ON tg.id = tag_group_id 
	            WHERE 1=1
                    -- and td.data_date between %(date_from)s and %(date_to)s::date + interval '1 days'
	                -- and td.data_value is not null
	            GROUP BY tag_code, tag_name
                '''
            else:
                # 조회 조건이 존재할 때
                if tag_group_pk == 7:
                    data_table = 'em_tag_dat'
                elif tag_group_pk == 8:
                    data_table = 'tag_dat'
                elif tag_code and '.em.' in tag_code:
                    data_table = 'em_tag_dat'
                else:
                    data_table = 'tag_dat'

                sql = f'''
                SELECT 
                    -- tg."Name" || '(' || tg."Code" || ')' AS tag_group,
                    -- t.tag_group_id,
                    td.tag_code AS tag_code,
                    t.tag_name AS tag_name,
                    count(*) AS count_value,
                    avg(td.data_value) AS avg_value,
                    min(td.data_value) AS min_value,
                    max(td.data_value) AS max_value,
                    round(stddev(td.data_value)::decimal, 5) AS std_value
                FROM das.{data_table} td
                INNER JOIN tag t ON t.tag_code = td.tag_code
                LEFT JOIN tag_grp tg ON tg.id = t.tag_group_id 
                WHERE 
                    td.data_date BETWEEN %(date_from)s AND %(date_to)s::date + interval '1 days'
                    AND td.data_value IS NOT NULL
                '''
                if tag_code:
                    sql += ''' and t.tag_code = %(tag_code)s
                    '''
                if tag_group_pk:
                    sql += ''' and t."tag_group_id" = %(tag_group_pk)s
                    '''
                sql += '''
	            group by td.tag_code, t.tag_name
                '''
            dc = {}
            dc['date_from'] = start_date
            dc['date_to'] = end_date
            dc['tag_code'] = tag_code
            dc['tag_group_pk'] = tag_group_pk

            result['data'] = DbUtil.get_rows(sql, dc)
            result['success'] = True


    except Exception as ex:
        source = '/api/tagdata/tag_statistics'
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False, 'message': str(ex)}

    return result
