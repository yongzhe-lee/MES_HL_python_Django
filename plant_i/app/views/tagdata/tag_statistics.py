import numpy as np

from configurations import settings
from domain.models.mes import TagMaster
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
    
    try:
        if action=='read':
            start_date = gparam.get('start_date', '')
            end_date = gparam.get('end_date', '')
            tag_code = gparam.get('tag_code', '')
            tag_group_pk = gparam.get('tag_group_pk', '')
            if settings.DBMS =='MSSQL' :
                sql = '''
                select td.tag_code, t.tag_name, count(*) as count_value, avg(td.data_value) as avg_value
                , min(td.data_value) as min_value, max(td.data_value) as max_value
                , round(convert(decimal, stdev(td.data_value)),5) as std_value
	            from tag_dat td 
                inner join tag t on t.tag_code = td.tag_code
	            where td.data_date between %(date_from)s and dateadd(day,1,convert(date, %(date_to)s))
	            and td.data_value is not null
                '''
            else :
                sql = '''
                select td.tag_code, t.tag_name, count(*) as count_value, avg(td.data_value) as avg_value
                , min(td.data_value) as min_value, max(td.data_value) as max_value
                , round(stddev(td.data_value)::decimal,5) as std_value
	            from tag_dat td 
                inner join tag t on t.tag_code = td.tag_code
	            where td.data_date between %(date_from)s and %(date_to)s::date + interval '1 days'
	            and td.data_value is not null
                '''
            if tag_code:
                sql += ''' and td.tag_code = %(tag_code)s
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

            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = '/api/tagdata/tag_statistics'
        LogWriter.add_dblog('error', source, ex)
        raise ex

    return items
