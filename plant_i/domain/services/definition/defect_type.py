from domain.services.sql import DbUtil
from domain.services.logging import LogWriter

class DefectTypeService():
    def __init__(self):
        pass

    
    def get_defect_type_list(self, coverage, _4m_type, keyword):
        '''
        작성명 : 부적합유형 리스트 조회
        작성자 : kga
        작성일 : 2021-01-28
        비고 :
        -수정사항-
        수정일             작업자     수정내용
        '''
        items=[]
        dic_param = { 'coverage': coverage, '4m_type': _4m_type, 'keyword': keyword }
        sql = '''
        select dt.id
	    , dt."Code" as defect_type_code
	    , dt."Name" as defect_type_name
	    , dt."Description" as description
        , c2."Value" as "defect_type_coverage"
        , c3."Value" as "defect_type_4m_type"
        from defect_type dt
        left join sys_code c2 on c2."Code" = dt."Coverage" and c2."CodeType" = 'coverage'
        left join sys_code c3 on c3."Code" = dt."Type" and c3."CodeType" = '4m_type'
        where 1=1
        '''
        if coverage:
            sql += ''' and c2."Code" = %(coverage)s'''
        if _4m_type:
            sql += ''' and c3."Code" = %(4m_type)s'''
        if keyword:
            sql += '''
            and upper(dt."Name") like concat('%%',upper(%(keyword)s),'%%')
            '''

        sql += '''order by dt."Code"'''

        try:
            items = DbUtil.get_rows(sql, dic_param)
        except Exception as ex:
            LogWriter.add_dblog('error','DefectTypeService.get_defect_type_list', ex)
            raise ex

        return items


    def get_defect_type_detail(self, id):
        '''
        작성명 : 부적합유형 상세 조회
        작성자 : kga
        작성일 : 2021-01-28
        비고 :

        -수정사항-
        수정일             작업자     수정내용
        2020-01-01     홍길동      테스트수정내용
        '''
        dic_param = { 'id': id }
        sql = '''
        select dt.id
        , dt."Code" as defect_type_code
	    , dt."Name" as defect_type_name
	    , dt."Description" as description
        , dt."Coverage" as "defect_type_coverage"
        , dt."Type" as "defect_type_4m_type"
        from defect_type dt
        where 1=1
        and dt.id = %(id)s
        '''

        defect_type = {}
        try:
            items = DbUtil.get_rows(sql, dic_param)
            if len(items) > 0:
                defect_type = items[0]

        except Exception as ex:
            LogWriter.add_dblog('error', 'DefectTypeService.get_defect_type_detail', ex)
            raise ex

        return defect_type

