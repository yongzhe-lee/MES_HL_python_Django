from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.sql import DbUtil


def menu_log(context):
    '''
    api/system/menu_log
    '''
    gparam = context.gparam
    # posparam = context.posparam
    request = context.request
    action = gparam.get('action', 'read')

    try:
        if action == 'read':
            date_from = gparam.get('date_from')
            date_to = gparam.get('date_to')
            menu_code = gparam.get('cboMenu')
            user_pk = gparam.get('cboUser')

            sql = ''' 
            SELECT 
                g.id
                , mf."FolderName" AS folder_name
                , g."MenuCode" AS menu_code
                , m."MenuName" AS menu_name
                , u.username
	            --, u.last_name ||u.first_name AS user_name
                , p."Name" AS user_name
	            , TO_CHAR(g._created, 'yyyy-mm-dd hh24:mi:ss') AS click_date
	        FROM 
                menu_use_log g 
	        INNER JOIN 
                menu_item m ON m."MenuCode" = g."MenuCode" 
	        LEFT JOIN 
                menu_folder mf ON mf.id = m."MenuFolder_id" 
	        LEFT JOIN 
                auth_user u ON u.id = g."User_id" 
            LEFT JOIN 
                user_profile p ON p."User_id" = g."User_id" 
	        WHERE 
                g._created BETWEEN %(date_from)s AND %(date_to)s
            '''
            if menu_code:
                sql += ''' AND g."MenuCode" = %(menu_code)s
                '''
            if user_pk:
                sql += ''' AND g."User_id" = %(user_pk)s
                '''
            sql += ''' ORDER BY g._created '''

            dc = {}
            dc['date_from'] = date_from
            dc['date_to'] = date_to + ' 23:59:59'
            dc['menu_code'] = menu_code
            dc['user_pk'] = user_pk

            result = DbUtil.get_rows(sql, dc)

        elif action == 'log_count':
            date_from = gparam.get('date_from')
            date_to = gparam.get('date_to')
            menu_code = gparam.get('cboMenu')
            user_pk = gparam.get('cboUser')

            sql = ''' 
            SELECT 
                mf."FolderName" AS folder_name
                , g."MenuCode" AS menu_code
                , m."MenuName" AS menu_name
	            , COUNT(*) AS use_count
	        FROM 
                menu_use_log g 
	        INNER JOIN 
                menu_item m ON m."MenuCode" = g."MenuCode" 
	        LEFT JOIN 
                menu_folder mf ON mf.id = m."MenuFolder_id" 
	        LEFT JOIN 
                auth_user u ON u.id = g."User_id" 
	        WHERE 
                g._created BETWEEN %(date_from)s AND %(date_to)s
            '''
            if menu_code:
                sql += ''' AND g."MenuCode" = %(menu_code)s
                '''
            if user_pk:
                sql += ''' AND g."User_id" = %(user_pk)s
                '''
            sql += ''' 
            GROUP BY 
                mf."FolderName", g."MenuCode", m."MenuName" 
            '''
            dc = {}
            dc['date_from'] = date_from
            dc['date_to'] = date_to + ' 23:59:59'
            dc['menu_code'] = menu_code
            dc['user_pk'] = user_pk

            result = DbUtil.get_rows(sql, dc)

        elif action == 'user_list':
            sql = ''' 
            SELECT 
                u.id AS value
                , u.username||'('||u.last_name||u.first_name||')' AS text
	        FROM 
                auth_user u 
	        INNER JOIN 
                user_profile up ON up."User_id" = u.id 
	        INNER JOIN 
                user_group ug ON ug.id = up."UserGroup_id" 
	        WHERE 
                u.is_active 
	            AND NOT u.is_superuser 
	            AND  ug."Code" NOT IN ('dev')
	        ORDER BY 2
            '''
            dc = {}

            result = DbUtil.get_rows(sql, dc)

    except Exception as ex:
        source = '/api/system/menu_log, action:{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        result = {'success':False}

    return result
