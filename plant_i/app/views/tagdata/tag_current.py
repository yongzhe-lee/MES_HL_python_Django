from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from configurations import settings
from domain.services.system_definition.tag_data import TagDataService


def tag_current(context):
    '''
    /api/tag_data/tag_current
    '''
    items=[]
    posparam = context.posparam
    gparam = context.gparam
    action = gparam.get('action', 'read')
    
    try:
        if action == 'read':
            if settings.DBMS =='MSSQL' :
                sql = '''
                    with A as 
	                (
	                select tag_code
	                , max(concat(Format(data_date,'yyyy-MM-dd HH:mm:ss'),'-',data_value)) as date_value
	                --, max(concat(convert(varchar , data_date),'-',data_value)) as date_value
	                from tag_dat
	                where 1 = 1
	                group by tag_code
	                )
	                select A.tag_code as tag_code
                    , t.tag_name
                    ,substring(A.date_value, 21, 10) as data_value
                    --,substring(A.date_value, 29, 10) as data_value
                    ,substring(A.date_value, 1, 19) as data_date
                    ,concat(t."LSL", '~', t."USL") as spec
                    , e."Name" as equip_name
	                from A a
	                inner join tag t on a.tag_code = t.tag_code 
                    left join equ e on e.id = t."Equipment_id"
	                order by a.tag_code
                '''
            else :
                sql = '''
                    with A as
	                (
	                select tag_code
	                --, max(to_char(data_date,'yyyy-mm-dd hh24:mi:ss')||'-'||data_value) as date_value
	                , max(data_date::text||'-'||data_value) as date_value
	                from tag_dat
	                where 1 = 1
	                group by tag_code
	                )
	                select A.tag_code as tag_code
                    , t.tag_name
                    --, substring(A.date_value, 24, 10) as data_value
                    -- split_part 추가 / 이주영 / 나노인스텍의 경우 tag_dat의 data_date에 millisecond까지 저장되기 때문에 다음과 같이 수정
                    , split_part(A.date_value, '-', 4) as data_value
                    ,substring(A.date_value, 1, 19) as data_date
                    ,concat(t."LSL", '~', t."USL") as spec
                    , e."Name" as equip_name
	                from A a
	                inner join tag t on a.tag_code = t.tag_code 
                    left join equ e on e.id = t."Equipment_id"
	                order by a.tag_code
                '''        
            dc = {}
            items = DbUtil.get_rows(sql)
            #items = equipment_final_tagdata_service.get_equipment_final_tagdata_list()

    except Exception as ex:
        source = 'tag_current : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return items


