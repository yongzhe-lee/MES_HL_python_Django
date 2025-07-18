
from domain.models.aas import DBSubmodelElement
from domain.services.sql import DbUtil

class AASDataService():
    def __init__(self):
        pass

    def make_id_with_short_id(self, id_short, model_type):
        '''
        id_short를 이용하여 id를 생성한다.
        model_type은 'aas', 'submodel', 'submodel_element' 중 하나이다.
        '''
        if model_type == 'aas':
            return f'urn:aas:{id_short}'
        elif model_type == 'submodel':
            return f'urn:submodel:{id_short}'
        elif model_type == 'submodel_element':
            return f'urn:sme:{id_short}'
        else:
            raise ValueError("Invalid model type. Must be one of 'aas', 'submodel', or 'submodel_element'.")

    def set_multi_language_text(self, json_data, language, text):
        if json_data:
            dic_data = json_data
            exists = False
            for dic in dic_data:
                if dic.get('language') == language:
                    dic['text'] = text
                    exists = True
                    break
            if not exists:
                dic_data.append({'language': language, 'text': text})

        else:
            dic_data = [{'language' : language, 'text' : text}]

        return dic_data

    def get_aas_list(self, keyword, lang_code):

        dic_param = {"keyword": keyword, "lang_code" :lang_code}

        sql ='''
        with recursive aas_tree as ( 
            with recursive at1 as(
              select
               a1.aas_pk
               , a1.id
               , a1.id_short
               , a1.description
               , a1."displayName"
               , a1.base_aas_pk as parent_pk
               , 0 as lvl
               , a1._created
              from aas a1
              where a1.base_aas_pk is null
              union all
              select
              a2.aas_pk
              , a2.id
              , a2.id_short
              , a2.description
              , a2."displayName"  
              , a2.base_aas_pk as parent_pk
              , at1.lvl+1
              , a2._created
              from aas a2
              inner join at1 on at1.aas_pk = a2.base_aas_pk      
            )        
	          select 
	          a.aas_pk 
	          , null::numeric as sm_pk
	          , a.parent_pk
	          , a.id
	          , a.id_short
	          , a.description
	          , a."displayName"
	          , 'aas' as gubun
	          , a._created 
	          , a.lvl as lvl
	          from at1 a 
	          where 1=1
        '''
        if keyword:
            sql+='''
            and exists ( select 1  from jsonb_array_elements(a."displayName") as kk  where  kk->>'language' = %(lang_code)s and upper(kk->>'text') like concat('%%',upper(%(keyword)s),'%%'))
            '''

        sql+='''
	        union all 
	          select
	          asr.aas_pk
	          , sb.sm_pk
	          , asr.aas_pk as parent_pk
	          , sb.id
	          , sb.id_short
	          , sb.description
	          , sb."displayName"
	          , 'sub' as gubun
	          , sb._created
	          , aatt.lvl+1 as lvl
	          from aas_submodel_refs asr  
	          inner join reference r on r.ref_pk = asr.ref_pk
	          inner join "keys" k on k.ref_pk =r.ref_pk and k."type"='SUBMODEL'
	          inner join submodel as sb on sb.id = k.value  
	          inner join aas_tree aatt on asr.aas_pk = aatt.aas_pk and aatt.gubun='aas' 
        ) 
        select
              aas_tree.parent_pk
	          , aas_tree.aas_pk	  
	          , aas_tree.sm_pk
	          , aas_tree.id
	          , aas_tree.id_short
	          , fn_json_lang_text(aas_tree."displayName", %(lang_code)s) as "displayName"
              , aas_tree.gubun  
              , to_char(aas_tree._created, 'yyyy-mm-dd hh24:mi:ss') created
          , aas_tree.lvl
          from aas_tree
          where 1=1
          order by aas_tree.lvl, aas_tree."displayName"
        '''

        items = DbUtil.get_rows(sql, dic_param)

        dic_aas = {}
        aas_items = []
        for item in items:
            gubun = item["gubun"]
            aas_pk = item["aas_pk"]
            parent_pk = item["parent_pk"]
            aas = None

            # 부모가 없는 최상위 AAS 목록
            if  gubun=="aas" and parent_pk is None:
                aas = item
                dic_aas[aas_pk] = aas
                aas["sub_items"] = []
                aas_items.append(aas)
                continue

            # 상위AAS를 부모로 둔 AAS
            if gubun=="aas":
                if aas_pk in dic_aas:
                    aas = dic_aas.get(aas_pk)
                else:
                    aas = item
                    parent_aas = dic_aas.get(parent_pk)
                    parent_sub_items = parent_aas.get('sub_items')
                    parent_sub_items.append(aas)

                    dic_aas[aas_pk] = aas
                    aas["sub_items"] = []
                    
            else:
                aas = dic_aas.get(aas_pk)
                sub_items = aas.get('sub_items')
                sub_items.append(item)

        return aas_items

    def get_aas_detail(self, aas_pk, lang_code='ko-KR'):
        dic_param = {"aas_pk": aas_pk, "lang_code" :lang_code}
        sql='''
        select 
        a.aas_pk 
        , a.id
        , a.id_short
        , %(lang_code)s as lang_code
        , fn_json_lang_text(a.description, %(lang_code)s) as "description" 
        , fn_json_lang_text(a."displayName", %(lang_code)s) as "displayName"
        , a.description as json_description
        , a."displayName" as json_displayname
        , 'aas' as gubun
        , (select count(*) from specific_asset where specific_asset.asset_pk= ai.asset_pk) as asset_count
        , to_char(a._created, 'yyyy-mm-dd hh24:mi:ss') created
        , r."path"
        , r."contentType"
        , r."StringType"
        , ai."assetKind"
        , fn_code_name('asset_type', ai."assetType") as asset_type
        , ai."globalAssetId" as global_asset_id
        , fn_json_lang_text(pa."displayName", %(lang_code)s) as p_display_name
        , adm.version
        , adm.revision
        from aas a
        left join administration adm on adm.admin_pk = a.admin_pk
        left join asset_info ai on a.asset_pk = ai.asset_pk 
        left join resource r on r.res_pk = ai."defaultThumbnail_id"
        left join aas as pa on pa.aas_pk = a.base_aas_pk
        where a.aas_pk=%(aas_pk)s
        '''
        data = DbUtil.get_row(sql, dic_param)
        return data

    def get_submodel_detail(self, sm_pk, lang_code, aas_pk):

        dic_param = {"sm_pk": sm_pk, "lang_code":lang_code, "aas_pk": aas_pk}

        sql='''
        select
        sb.aas_pk as sm_aas_pk
        , asr.aas_pk
        , sb.sm_pk
        , sb.aas_pk as parent_pk
        , sb.id
        , sb.id_short
        , %(lang_code)s as lang_code
        , fn_json_lang_text(sb.description, %(lang_code)s) as "description" 
        , fn_json_lang_text(sb."displayName", %(lang_code)s) as "displayName"
        , sb.description as json_description
        , sb."displayName" as json_displayname
        , 'sub' as gubun
        , to_char(sb._created, 'yyyy-mm-dd hh24:mi:ss') created
        , fn_json_lang_text(a."displayName", 'ko-KR') as p_display_name
        , case when sb.aas_pk is null then 'share' else 'exclusive' end as scope
        from submodel sb
        left join aas_submodel_refs asr on asr.aas_pk =%(aas_pk)s
        left join keys k on k.ref_pk =asr.ref_pk and k."type" ='SUBMODEL'
        left join aas a on a.aas_pk = asr.aas_pk
        where sb.sm_pk=%(sm_pk)s
        '''

        data = DbUtil.get_row(sql, dic_param)
        return data

    def get_submodel_element_collection_detail(self, sme_pk, lang_code):
        dic_param = {"sme_pk": sme_pk, 'lang_code' : lang_code}
        sql='''
        with aa as (
        select 
        sme.sme_pk
        , sme_parent.sme_pk as p_sme_pk
        , sm.sm_pk as p_sm_pk
        , sm.id as sm_id
        , sm.id_short sm_id_short
        , sme.id_short
        , sme."ModelKind"
        , sme."modelType"
        , sme."displayName" as "displayName"
        , sme.description as description
        , case when sm.sm_pk is null then sme_parent."displayName" else sm."displayName" end as p_display_name
        , case when sm.sm_pk is null then sme_parent."modelType" else 'submodel' end as "p_modelType"
        , sme._created
        from submodel_element sme
        inner join submodel_element_collection sec on sec.sme_pk =sme.sme_pk 
        left join submodel sm on sm.sm_pk = sme.sm_pk
        left join submodel_element_collection_values secv on secv.dbsubmodelelement_id  = sme.sme_pk
        left join submodel_element sme_parent on sme_parent.sme_pk = secv.dbsubmodelelementcollection_id
        where sme.sme_pk = %(sme_pk)s
        )
        select 
        aa.sme_pk 
        , aa.p_sme_pk
        , aa.p_sm_pk
        , aa.sm_id
        , aa.sm_id_short
        , aa.id_short
        , aa."ModelKind"
        , aa."modelType"
        , aa."displayName" as json_displayname
        , aa.description as json_description
        , fn_json_lang_text(aa."displayName" , %(lang_code)s) as "displayName"
        , fn_json_lang_text(aa.description , %(lang_code)s) as description
        , fn_json_lang_text(aa.p_display_name, %(lang_code)s) as p_display_name
        , aa."p_modelType"
        , to_char(aa._created, 'yyyy-mm-dd hh24:mi:ss') created
        from aa
        '''
        data = DbUtil.get_row(sql, dic_param)
        return data


    def get_property_detail(self, sme_pk, lang_code):
        '''
        PropertElement 단건 상세조회
        '''
        dic_param = {"sme_pk": sme_pk, 'lang_code' : lang_code}
        sql='''
        with aa as(
        select 
        se.sme_pk
        , se.sm_pk
        , se.id_short
        , se."modelType"
        , se."ModelKind"
        , se.category
        , se."displayName"
        , se.description 
        , pe."valueType"
        , 'prop' as gubun
        , pe.value_id
        , pe.value
        , r."type" as value_id_ref_type
        , rs."type" as semantice_type
        , se.semanctic_id
        , case when sm.sm_pk is null then sme_parent."displayName" else sm."displayName" end as p_display_name
        , case when sm.sm_pk is null then sme_parent."modelType" else 'Submodel' end as "p_modelType"  
        , se._created
        from submodel_element se 
        inner join property_element pe on pe.sme_pk =se.sme_pk
        left join submodel sm on sm.sm_pk  = se.sm_pk 
        left join submodel_element_collection_values secv on secv.dbsubmodelelement_id  = se.sme_pk
        left join submodel_element sme_parent on sme_parent.sme_pk = secv.dbsubmodelelementcollection_id
        left join reference rs on rs.ref_pk = se.semanctic_id 
        left join reference r on r.ref_pk = pe.value_id
        where se.sme_pk=%(sme_pk)s
        )
        select
        aa.sme_pk
        , aa.sm_pk
        , aa.id_short
        , aa."modelType"
        , aa."ModelKind"
        , aa.category
        , fn_json_lang_text(aa."displayName", %(lang_code)s) as "displayName"
        , fn_json_lang_text(aa.description, %(lang_code)s) as description
        , aa."displayName" as json_displayname
        , aa.description as json_description
        , aa."valueType"
        , aa.value
        , aa.value_id
        , aa.value_id_ref_type
        , aa.semantice_type
        , aa.semanctic_id
        , fn_json_lang_text(aa.p_display_name, %(lang_code)s) as p_display_name
        , aa."p_modelType"
        , to_char(aa._created, 'yyyy-mm-dd hh24:mi:ss') created
        from aa
        '''
        data = DbUtil.get_row(sql, dic_param)
        return data
    def get_file_detail(self, sme_pk, lang_code):
        '''
        FileElement 단건 상세조회
        '''
        dic_param = {"sme_pk": sme_pk, 'lang_code' : lang_code}
        sql='''
        with aa as(
        select 
        se.sme_pk
        , se.sm_pk
        , se.id_short
        , se."modelType"
        , se."ModelKind"
        , se.category
        , se."displayName"
        , se.description 
        , 'file' as gubun
        , fe.value
        , fe.content_type
        , fe.filename
        , rs."type" as semantice_type
        , se.semanctic_id
        , case when sm.sm_pk is null then sme_parent."displayName" else sm."displayName" end as p_display_name
        , case when sm.sm_pk is null then sme_parent."modelType" else 'Submodel' end as "p_modelType"  
        , se._created
        from submodel_element se 
        inner join file_element fe on se.sme_pk =fe.sme_pk
        left join submodel sm on sm.sm_pk  = se.sm_pk 
        left join submodel_element_collection_values secv on secv.dbsubmodelelement_id  = se.sme_pk
        left join submodel_element sme_parent on sme_parent.sme_pk = secv.dbsubmodelelementcollection_id
        left join reference rs on rs.ref_pk = se.semanctic_id 
        where se.sme_pk=%(sme_pk)s
        )
        select
        aa.sme_pk
        , aa.sm_pk
        , aa.id_short
        , aa."modelType"
        , aa."ModelKind"
        , aa.category
        , fn_json_lang_text(aa."displayName", %(lang_code)s) as "displayName"
        , fn_json_lang_text(aa.description, %(lang_code)s) as description
        , aa."displayName" as json_displayname
        , aa.description as json_description
        , aa.value
        , aa.content_type
        , aa.filename
        , aa.semantice_type
        , aa.semanctic_id
        , fn_json_lang_text(aa.p_display_name, %(lang_code)s) as p_display_name
        , aa."p_modelType"
        , to_char(aa._created, 'yyyy-mm-dd hh24:mi:ss') created
        from aa
        '''
        data = DbUtil.get_row(sql, dic_param)
        return data


    def get_submodel_element_list(self, sm_pk, lang_code='ko-KR'):
        '''
        submodel 하위 submodel 엘리먼트 목록을 가져온다
        '''
        dic_param = {'sm_pk' : sm_pk, 'lang_code' : lang_code} 
        sql = '''
        select 
        sme.sme_pk
        , sme.sm_pk
        , sme."ModelKind"
        , sme."modelType"
        , case sme."modelType" when 'Property' then 
            'prop' 
          when 'File' then
            'file' 
          when 'Collection' then
            'coll' 
          when 'Entity' then
            'entity'
          else 
            'etc' 
          end as gubun
        , fn_json_lang_text(sme.description, %(lang_code)s) as "description"    
        , fn_json_lang_text(sme."displayName", %(lang_code)s) as "displayName"
        , to_char(sme._created, 'yyyy-mm-dd hh24:mi:ss') created
        , pe.value as prpt_value
        , fe.value as file_value
        from submodel_element sme
        left join property_element pe on pe.sme_pk = sme.sme_pk
        left join file_element fe on fe.sme_pk = sme.sme_pk
        left join entity_element ee on ee.sme_pk =sme.sme_pk
        left join submodel_element_collection sec on sec.sme_pk = sme.sme_pk
        where sme.sm_pk=%(sm_pk)s
        order by sme."modelType" desc
        '''
        items = DbUtil.get_rows(sql, dic_param)
        return items

    def get_submodel_element_collection_items(self, sme_pk, lang_code='ko-KR'):
        dic_param = {'sme_pk' : sme_pk, 'lang_code' : lang_code} 

        sql='''
        select        
        smev.dbsubmodelelement_id as sme_pk
        , fn_json_lang_text(sme."displayName", %(lang_code)s) as "displayName"
        , sme."modelType"
         , case sme."modelType" when 'Property' then 
             'prop' 
           when 'File' then
             'file' 
           when 'Collection' then
             'coll' 
           when 'Entity' then
             'entity'
           else 
             'etc' 
           end as gubun
        , sme.id_short
        , sme."modelType"
        , sm.sm_pk
        , to_char(smec._created, 'yyyy-mm-dd hh24:mi:ss') created
        , pe.value as prpt_value
        from submodel_element_collection smec        
        inner join submodel_element_collection_values smev on smev.dbsubmodelelementcollection_id = smec.sme_pk
        inner join submodel_element sme on sme.sme_pk = smev.dbsubmodelelement_id 
        left join property_element pe on pe.sme_pk = sme.sme_pk
        left join submodel sm on sm.sm_pk = sme.sm_pk
        where smec.sme_pk = %(sme_pk)s 
        '''
        items = DbUtil.get_rows(sql, dic_param)
        return items
