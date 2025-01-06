from configurations import settings

from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter


class BoardService():
    def __init__(self):
        pass

    def get_board_list(self, board_group, keyword, srchStartDt, srchEndDt):
        items = []
        try:  
            if settings.DBMS == 'MSSQL' :
                sql = ''' with A as (
                    select id, "Title" as title
	                , Format("WriteDateTime", 'yyyy-MM-dd hh:mm:ss') as write_date_time
	                from board
	                where "BoardGroup" = %(board_group)s
                    and "NoticeYN" = 'Y'
	                and "NoticeEndDate" >= %(today)s
                ), B as (
                    select B.id, B."Title" as title
                    , Format(B."WriteDateTime", 'yyyy-MM-dd hh:mm:ss') as write_date_time
                    from board B 
                    left join A on A.id = B.id
                    where B."BoardGroup" = %(board_group)s
                    and B."WriteDateTime" between %(srchStartDt)s and %(srchEndDt)s
                    and A.id is null
                    '''
            else :
                sql = ''' with A as (
                    select id, "Title" as title
	                , to_char("WriteDateTime", 'yyyy-mm-dd hh24:mi:ss') as write_date_time
	                from board
	                where "BoardGroup" = %(board_group)s
                    and "NoticeYN" = 'Y'
	                and "NoticeEndDate" >= %(today)s
                ), B as (
                    select B.id, B."Title" as title
                    , to_char(B."WriteDateTime", 'yyyy-mm-dd hh24:mi:ss') as write_date_time
                    from board B 
                    left join A on A.id = B.id
                    where B."BoardGroup" = %(board_group)s
                    and B."WriteDateTime" between %(srchStartDt)s and %(srchEndDt)s
                    and A.id is null
                    '''
            if keyword:
                sql += '''
                and ( B."Title" like concat('%%', %(keyword)s, '%%') 
                        or B."Content" like concat('%%', %(keyword)s, '%%')
                        )
                '''
            sql += ''' )
            select 1 as data_group, id, title, write_date_time
            from A 
            union all 
            select 2 as data_group, id, title, write_date_time
            from B 
            order by data_group, write_date_time desc
            '''
            today = DateUtil.get_today_string()

            dc = {}
            dc['board_group'] = board_group
            dc['srchStartDt'] = srchStartDt
            dc['srchEndDt'] = srchEndDt
            dc['keyword'] = keyword
            dc['today'] = today
                
            items = DbUtil.get_rows(sql, dc)
        except Exception as e:
            LogWriter.add_dblog('error', 'BoardService.get_board_list', e)
            raise e
        return items

    def get_board_detail(self, id):
        items = []
        sql = ''' select id
	            , "Title" title 
	            , "NoticeYN" notice_yn
	            , "NoticeEndDate" notice_end_date
	            , "Content" as content
            from board b 
            where id = %(id)s
        '''
        data = {}
        try:
            items = DbUtil.get_row(sql, {'id': id})
            if len(items) > 0:
                data = items
        except Exception as ex:
            LogWriter.add_dblog('error', 'BoardService.get_board_detail', ex)
            raise ex
        return data

    def chk_creater(self, id, create_id):
        items = []
        sql = ''' select 1
            from board b 
            where id = %(id)s 
            and "_creater_id" = %(_create_id)s
        '''
        data = {}
        try:
            items = DbUtil.get_rows(sql, {'id': id, '_create_id': create_id})
            if len(items) > 0:
                data = True
            else:
                data = False
        except Exception as e:
            LogWriter.add_dblog('error', 'BoardService.chk_reater', e)
            raise e
        return data