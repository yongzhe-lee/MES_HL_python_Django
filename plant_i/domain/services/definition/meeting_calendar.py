from configurations import settings
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class CalendarService():
    def __init__(self):
        pass


    def get_calendar_list(self, keyword):
        '''
        작성명 : 일정조회
        작성자 : 
        작성일 : 2021-02-22
        비고 :

        -수정사항-
        수정일             작업자     수정내용
        2020-01-01     홍길동      테스트수정내용
        '''
        items = []
        if settings.DBMS =='MSSQL' : 
            sql = '''
                select id
                , "Title" as title
                , Format("DataDate",'yyyy-mm-dd') as "DataDate"
                , concat(Format("DataDate",'yyyy-MM-dd'),' ',Format("StartTime",'HH:mm')) as start
                , concat(Format("DataDate",'yyyy-MM-dd'),' ',Format("EndTime",'HH:mm')) as "end"
                , "Color" as color
                , 'calendar' as data_div
                , "Description" as description
                from calendar
                where "DataDate" between convert(date,'2021-07-01') and eomonth(convert(date,'2021-07-01')) 
                union all
                SELECT concat('mo', mo.id)
                --, true as allDay
		        --, mo."OrderNumber"
		        --, mo."AvailableStock"
		        , concat(m."Name",' ',mo."OrderQty", u."Name") as title
                , Format(mo."InputPlanDate",'yyyy-MM-dd') as "DataDate"
                , concat(Format(mo."InputPlanDate",'yyyy-MM-dd'),' 00:00') as start
                , concat(Format(mo."InputPlanDate",'yyyy-MM-dd'),' 00:00') as "end"
	            , '#FF0000' as color
                , 'mat_order' as data_div
                , mo."Description" as description
	            from mat_order mo
	            inner join material m ON m.id = mo."Material_id"
                LEFT JOIN unit u ON m."Unit_id" = u.id
                WHERE mo."InputPlanDate" between convert(date,%(date_from)s) and eomonth(convert(date,%(date_from)s)) 
                and mo."State" = 'approved' 
            '''
        else :
            sql = '''
                select id::text
                , "Title" as title
                , to_char("DataDate",'yyyy-mm-dd') as "DataDate"
                , to_char("DataDate",'yyyy-mm-dd')||' '||to_char("StartTime",'hh24:mi') as start
                , to_char("DataDate",'yyyy-mm-dd')||' '||to_char("EndTime",'hh24:mi') as end
                , "Color" as color
                , 'calendar' as data_div
                , "Description" as description
                from calendar
                where "DataDate" between %(date_from)s and %(date_from)s::date + interval '1 month - 1 day'
                union all
                SELECT 'mo'|| mo.id::text
                --, true as allDay
		        --, mo."OrderNumber"
		        --, mo."AvailableStock"
		        , concat(m."Name",' ',mo."OrderQty", u."Name") as title
                , to_char(mo."InputPlanDate",'yyyy-mm-dd') as "DataDate"
                , to_char(mo."InputPlanDate",'yyyy-mm-dd')||' 00:00' as start
                , to_char(mo."InputPlanDate",'yyyy-mm-dd')||' 00:00' as end
	            , '#FF0000' as color
                , 'mat_order' as data_div
                , mo."Description" as description
	            from mat_order mo
	            inner join material m ON m.id = mo."Material_id"
                LEFT JOIN unit u ON m."Unit_id" = u.id
                WHERE mo."InputPlanDate" between %(date_from)s and %(date_from)s::date + interval '1 month - 1 day'
                and mo."State" = 'approved' 
            '''            
        try:
            dc = {}
            dc['date_from'] = keyword + '-01'
            
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','CalendarService.get_calendar_list', ex)
            raise ex

        return items
