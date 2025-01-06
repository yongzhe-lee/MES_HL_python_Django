from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from configurations import settings
from domain.services.system_definition.tag_data import TagDataService

def tagdata_list(context):
    '''
    /api/maintenance/equipementtagdata
    '''
    items=[]
    posparam = context.posparam
    gparam = context.gparam
    action = gparam.get('action', 'read')

    try:
        if action == 'read':
            data_date = gparam.get('data_date', None)
            start_time = gparam.get('start_time', None)
            end_time = gparam.get('end_time', None)
            tag_code = gparam.get('tag_code', None)
            if settings.DBMS =='MSSQL' :
                sql = ''' select td.tag_code as tag_code
		        ,t.tag_name as tag_name
		        ,Format(td.data_date, 'yyyy-MM-dd HH:mm:ss') as data_date
                , td.data_value
                , td.data_char
	            from tag_dat td
                inner join tag t on t.tag_code = td.tag_code
	            where 1=1
                and td.tag_code = %(tag_code)s
	            and td.data_date between %(date_from)s and %(date_to)s
                order by td.tag_code, td.data_date 
                '''
            else :
                sql = ''' select td.tag_code as tag_code
		        ,t.tag_name as tag_name
		        ,to_char(td.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_date
                , td.data_value
                , td.data_char
	            from tag_dat td
                inner join tag t on t.tag_code = td.tag_code
	            where 1=1
                and td.tag_code = %(tag_code)s
	            and td.data_date between %(date_from)s and %(date_to)s
                order by td.tag_code, td.data_date 
                '''
            dc = {}
            dc['date_from'] = data_date + ' ' + start_time
            dc['date_to'] =  data_date + ' ' + end_time
            dc['tag_code'] = tag_code
            
            items = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = 'tagdata_list : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return items

