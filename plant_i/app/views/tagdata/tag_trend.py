from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from configurations import settings
from domain.services.system_definition.tag_data import TagDataService




def tag_trend(context):

    items = {}
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action')

    tag_service = TagDataService()
    
    try:
        if action=='read':
            start_date = posparam.get('start_time', '')
            end_date = posparam.get('end_time', '')
            tag_codes = posparam.get('tag_codes', '')

            items = tag_service.tag_multi_data_list2(start_date, end_date, tag_codes)

   #         sql = '''
   #         with A as (
   #             select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
   #         )
			#select T.tag_code, T.tag_name,  t."LSL" as lsl, t."USL" as usl
			#from Tag T 
			#inner join A on A.tag_code = T.tag_code 
   #         '''
   #         dc = {}
   #         dc['tag_codes'] = tag_codes
   #         #dc['tag_group_pk'] = tag_group_pk

   #         rows = DbUtil.get_rows(sql, dc)
   #         for row in rows:
   #             tag = {}
   #             tag_code = row['tag_code']
   #             tag['tag_name'] = row['tag_name']
   #             tag['lsl'] = row['lsl']
   #             tag['usl'] = row['usl']
   #             items[tag_code] = tag


   #         sql = '''
   #         with A as (
   #             select unnest(string_to_array(%(tag_codes)s, ';')) as tag_code
   #         )
			#select td.tag_code, td.data_date, to_char(td.data_date, 'yyyy-mm-dd hh24:mi:ss') as data_time, td.data_value
	  #      from tag_dat td 
   #         inner join A on A.tag_code = td.tag_code
   #         where 1=1
   #         and td.data_date between %(date_from)s and %(date_to)s
   #         order by td.tag_code, td.data_date
   #         '''

   #         dc = {}
   #         dc['date_from'] = start_date
   #         dc['date_to'] = end_date
   #         dc['tag_codes'] = tag_codes
   #         #dc['tag_group_pk'] = tag_group_pk

   #         rows = DbUtil.get_rows(sql, dc)
   #         #for row in rows:
   #         #    tag_code = row['tag_code']
   #         #    data = items[tag_code]
   #         #    data['data'] = row

   #         items['rows'] = rows
            return items

    except Exception as ex:
        source = '/api/tagdata/tag_trend'
        LogWriter.add_dblog('error', source, ex)
        raise ex

    return items


