from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.models.definition import TestCls

def popup_test(context):
    '''
    /api/popup/popup_test
    
    작성명 : 시험Popup
    작성자 : 김진욱
    작성일 : 2024-09-05
    비고 :

    -수정사항-
    수정일             작업자     수정내용
    2020-01-01         홍길동     unit 조인추가
    '''
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action')
    action = gparam.get('action', 'read')
    
    try:
        
        keyword = gparam.get('keyword')
    
        test_sql = '''
        select t.id as test_id
            , t.Name as test_name
            , tc.Name as test_cls_name
            , ic.id as inst_cls_id
            , ic.Name as inst_cls_name
            , i.id as inst_id
            , i.Name as inst_name
            from test t
            inner join test_cls tc on tc.id = t.TestCls_id 
            left join inst_cls ic on ic.id = t.InstCls_id 
            left join inst i on i.id = t.Inst_id 
            where 1=1
        '''
    
        if keyword:
            sql += ''' AND (t.Name LIKE CONCAT('%%', %(keyword)s, '%%') or tc.Name LIKE CONCAT('%%', %(keyword)s, '%%')) '''

        dc = {}
        dc['keyword'] = keyword
            
        test_list = DbUtil.get_rows(test_sql,dc)

        prpt_sql = '''
        select tp.id as tp_id
            , tc.Name as test_cls_name
            , t.id as test_id
            , t.Name as test_name
            , p.id as prpt_id
            , p.Name as prpt_name
            , ic.id as inst_cls_id
            , ic.Name as inst_cls_name
            , i.id as inst_id
            , i.Name as inst_name
            , tu.id as test_unit_id
            , tp.RoundType as round_type
            , tp.DecPlace as dec_place
            from test_prpt tp
            inner join test t on t.id = tp.Test_id 
            inner join prpt p on p.id = tp.Prpt_id 
            inner join test_cls tc on tc.id = t.TestCls_id 
            left join inst_cls ic on ic.id = t.InstCls_id 
            left join inst i on i.id = t.Inst_id 
            inner join test_unit tu on tu.id = tp.TestUnit_id 
        '''

        if keyword:
            sql += ''' AND (t.Name LIKE CONCAT('%%', %(keyword)s, '%%') or tc.Name LIKE CONCAT('%%', %(keyword)s, '%%') or p.Name LIKE CONCAT('%%', %(keyword)s, '%%'))
            '''

        prpt_list = DbUtil.get_rows(prpt_sql,dc)

        result = {'success':True, 'test_list':test_list, 'prpt_list':prpt_list}


    except Exception as ex:
        source = '/api/popup/popup_test, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}

    return result