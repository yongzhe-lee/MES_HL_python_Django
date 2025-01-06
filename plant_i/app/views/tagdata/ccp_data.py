from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from configurations import settings
from domain.services.system_definition.tag_data import TagDataService



def ccp_data(context):
    """ CCP 모니터링
    """
    items = {}
    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action')
    
    try:
        if action=='read':
            tag_group_pk = gparam.get('tag_group_pk', '')
            tag_code = gparam.get('tag_code', '')
            data_date = gparam.get('data_date', '')
            start_time = gparam.get('start_time', '')
            end_time = gparam.get('end_time', '')


            sql = '''
			select td.tag_code, t.tag_name, td.data_date, to_char(td.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_time, td.data_value
	        from tag_dat td 
            inner join tag t on t.tag_code = td.tag_code            
            where td.data_date between %(date_from)s and %(date_to)s
            '''
            if tag_code:
                sql += ''' and td.tag_code = %(tag_code)s
                '''
            if tag_group_pk:
                sql += ''' and t."tag_group_id" = %(tag_group_pk)s
                '''     
            sql += ''' order by td.tag_code, td.data_date
            '''

            dc = {}
            dc['tag_group_pk'] = tag_group_pk
            dc['tag_code'] = tag_code
            dc['date_from'] = data_date + ' ' + start_time
            dc['date_to'] = data_date + ' ' + end_time

            items = DbUtil.get_rows(sql, dc)


    except Exception as ex:
        source = '/api/tagdata/ccp_data'
        LogWriter.add_dblog('error', source, ex)
        raise ex

    return items