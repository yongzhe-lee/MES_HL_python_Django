from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class TagService():
    def __init__(self):
        pass


    def get_tag_list(self, keyword, tag_group_id, equipment_id):
        '''
        작성명 : 태그 리스트 조회
        작성자 : 이주영
        작성일 : 2020-12-30
        비고 :

        -수정사항-
        수정일             작업자     수정내용
        2020-01-01     홍길동      테스트수정내용
        '''
        items = []
        
        sql = '''
        select t.tag_code
	    , t."LSL" as lsl
	    , t."USL" as usl
	    , t.tag_name
	    , t.tag_group_id
	    , tg."Name" as tag_group_name
	    , t."Equipment_id" as equipment_id
	    , e."Name" as equipment_name  
        from tag t 
        left join tag_grp tg on t.tag_group_id = tg.id
        left join equ e on e.id = t."Equipment_id"
        where 1=1
        '''
        if keyword:
            sql+='''
              and upper(t.tag_name) like concat('%%',upper(%(keyword)s),'%%')
            '''
        if tag_group_id:
            sql+='''
              and t.tag_group_id = %(tag_group_id)s
            '''
        if equipment_id:
            sql+='''
              and t."Equipment_id" = %(equipment_id)s
            '''

        sql+=' order by t.tag_name '
        
        try:
            dc = {}
            dc['tag_group_id'] = tag_group_id
            dc['equipment_id'] = equipment_id
            dc['keyword'] = keyword
            items = DbUtil.get_rows(sql, dc)
        except Exception as ex:
            LogWriter.add_dblog('error','DefinitionService.get_tag_list', ex)
            raise ex

        return items


    def get_tag_detail(self, tag_code):
        '''
        작성명 : 태그 상세 조회
        작성자 : 이주영
        작성일 : 2020-12-30
        비고 :

        -수정사항-
        수정일             작업자     수정내용
        2020-01-01     홍길동      테스트수정내용
        '''
        
        sql = '''
        SELECT 
            t.tag_code AS id
            , t.tag_code
	        , t.tag_name
            , t."RoundDigit" AS round_digit
	        , t."LSL" AS lsl
	        , t."USL" AS usl
	        , t.tag_group_id
	        , tg."Name" AS tag_group_name
	        , t."Equipment_id" AS equipment_id
	        , e."Name" AS equipment_name  
        FROM 
            tag t 
        LEFT JOIN 
            tag_grp tg ON t.tag_group_id = tg.id
        LEFT JOIN 
            equ e ON e.id = t."Equipment_id"
        WHERE 1=1
            AND t.tag_code = %(tag_code)s
        '''
        tag = {}
        try:
            dc = { }
            dc['tag_code'] = tag_code
            items = DbUtil.get_row(sql, dc)

        except Exception as ex:
            LogWriter.add_dblog('error', 'DefinitionService.get_tag_detail', ex)
            raise ex

        return items
