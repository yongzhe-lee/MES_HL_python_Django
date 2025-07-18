from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.system_definition.tag_data import TagDataService
from domain.services.definition.tag import TagService

def tagdata_list(context):
    '''
    /api/tagdata/tagdata_list
    '''
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action', 'read')
    result = {}

    try:
        if action == 'read':
            data_date = gparam.get('data_date', '')
            start_time = gparam.get('start_time', '')
            end_time = gparam.get('end_time', '')
            line = gparam.get('line', '')
            equipment = gparam.get('equipment', '')
            tag_group = gparam.get('tag_group', '')
            tag_code = gparam.get('tag_code', '')

            table = 'das.tag_dat'
            if tag_group=="7":
                table = 'das.em_tag_dat'

            # 25.06.17 김하늘 로직 추가(em_tag_dat 반영) - 단일 조건이라 union 필요없이 table명만 태그에 맞게 할당 
            table = 'das.em_tag_dat' if '.em.' in tag_code else 'das.tag_dat' # .em.이 포함된 태그코드가 있는지 확인

            sql = f''' 
            SELECT
                e."Name" AS equ_name
                , tg."Name" || '(' || tg."Code" || ')' AS tag_group
                , td.tag_code AS tag_code
                , t.tag_name AS tag_name
		        , TO_CHAR(td.data_date, 'yyyy-mm-dd hh24:mi:ss') AS data_date
                , td.data_value
                , td.data_char
	        FROM 
                {table} td
            INNER JOIN 
                tag t ON t.tag_code = td.tag_code
            INNER JOIN
                equ e ON e.id = t."Equipment_id"
            LEFT JOIN
                tag_grp tg ON tg.id = t.tag_group_id
	        WHERE 1=1
	            AND td.data_date BETWEEN %(date_from)s AND %(date_to)s
            '''
            if line:
                sql += '''
                AND e.line_id = %(line)s
                '''
            if equipment:
                sql += '''
                AND t."Equipment_id" = %(equipment)s
                '''
            if tag_group:
                sql += '''
                AND t.tag_group_id = %(tag_group)s
                '''
            if tag_code:
                sql += '''
                AND td.tag_code = %(tag_code)s
                '''

            sql += '''
            ORDER BY td.tag_code, td.data_date 
            '''

            dc = {}
            dc['date_from'] = data_date + ' ' + start_time
            dc['date_to'] =  data_date + ' ' + end_time
            dc['line'] = line
            dc['equipment'] = equipment
            dc['tag_group'] = tag_group
            dc['tag_code'] = tag_code
            
            result['data'] = DbUtil.get_rows(sql, dc)
            result['success'] = True

        elif action == 'tag_detail':
            tag_code = gparam.get('tag_code')
            result = TagService().get_tag_detail(tag_code)

    except Exception as ex:
        source = '/api/tagdata/tagdata_list : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        result = {'success':False, 'message': str(ex)}

    return result

