
from domain.services.sql import DbUtil

class AASDataService():
    def __init__(self):
        pass

    def get_submodel_element_list(self, sm_pk):
        '''
        submodel 하위 submodel 엘리먼트 목록을 가져온다
        '''
        dic_param = {'sm_pk' : sm_pk}
        sql = '''
        select 
         sme.sme_pk
         , sme.sm_pk         
         , sme."ModelKind"
         , sme.model_type
         , sme."displayName"
         , sme."_created"
        from 
        submodel_element sme
        where sme.sm_pk=%(sm_pk)s
        '''
        data = DbUtil.get_row(sql, dic_param)
        return data

    def get_property_element(self, sme_pk):
        '''
        PropertElement 단건 상세조회
        '''
        dic_param = {"sme_pk": sme_pk}
        sql='''
        select 
        se.sme_pk
        , se.sm_pk
        , se.id_short
        , se.model_type
        , se."ModelKind"
        , se."displayName"
        , se.description
        , pe."valueType"
        , 'prop' as gubun
        , pe.value_id
        , pe.value
        , r."type" as value_id_ref_type
        , rs."type" as semantice_type
        , se.semanctic_id
        from submodel_element se 
        inner join property_element pe on pe.sme_pk =se.sme_pk 
        left join reference rs on rs.ref_pk = se.semanctic_id 
        left join reference r on r.ref_pk = pe.value_id
        where se.sme_pk=%(sme_pk)s
        '''
        data = DbUtil.get_row(sql, dic_param)
        return data

