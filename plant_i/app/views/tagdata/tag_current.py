from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.system_definition.tag_data import TagDataService
from domain.services.definition.tag import TagService

def tag_current(context):
    '''
    /api/tagdata/tag_current
    '''
    items=[]
    posparam = context.posparam
    gparam = context.gparam
    action = gparam.get('action', 'read')
    result = {}

    try:
        if action == 'read':
            # 25.06.19 김하늘 수정 em_tag_dat 추가되어 UNION 쿼리로 변경
            sql = '''
                WITH A AS
                (
	                SELECT 
                        tag_code
    	                --, MAX(TO_CHAR(data_date,'yyyy-mm-dd hh24:mi:ss')||'-'||data_value) AS date_value
	                    , MAX(data_date::text||'-'||data_value) AS date_value
	                FROM das.tag_dat
	                WHERE 1 = 1
                        and data_date > (current_timestamp + '-2 hours')
	                GROUP BY tag_code

                    UNION ALL

                    SELECT 
                        tag_code
    	                --, MAX(TO_CHAR(data_date,'yyyy-mm-dd hh24:mi:ss')||'-'||data_value) AS date_value
	                    , MAX(data_date::text||'-'||data_value) AS date_value
	                FROM das.em_tag_dat
	                WHERE 1 = 1
                        and data_date > (current_timestamp + '-2 hours')
	                GROUP BY tag_code
	            )
	            SELECT 
                    A.tag_code AS tag_code
                    , t.tag_name
                    , tg."Name" || '(' || tg."Code" || ')' AS tag_group
                    --, substring(A.date_value, 24, 10) AS data_value
                    -- split_part 추가 / 이주영 / 나노인스텍의 경우 tag_dat의 data_date에 millisecond까지 저장되기 때문에 다음과 같이 수정
                    , SPLIT_PART(A.date_value, '-', 4) AS data_value
                    , SUBSTRING(A.date_value, 1, 19) AS data_date
                    , concat(t."LSL", '~', t."USL") AS spec
                    , e."Name" AS equip_name
	            FROM A a
	            INNER JOIN 
                    tag t ON a.tag_code = t.tag_code 
                LEFT JOIN 
                    equ e ON e.id = t."Equipment_id"
                LEFT JOIN
                    tag_grp tg ON tg.id = t.tag_group_id
	            ORDER BY a.tag_code
            '''        
            # dc = {}
            result['data'] = DbUtil.get_rows(sql)
            result['success'] = True
            #result = equipment_final_tagdata_service.get_equipment_final_tagdata_list()

    except Exception as ex:
        source = '/api/tagdata/tag_current : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        result = {'success':False, 'message': str(ex)}

    return result


