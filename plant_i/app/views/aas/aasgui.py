
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.models.aas import DBAssetAdministrationShell

def aasgui(context) :
    '''
    /api/aas/aasgui?action=
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    action = gparam.get('action')
    lang_code = user.userprofile.lang_code
    if lang_code is None:
        lang_code = 'ko-KR'

    method = request.method
    result = {}

    source = f'/api/aas/aasgui?action={action}'

    try:

        if action=="aas_read":

            keyword = gparam.get('keyword')
            dic_param = {"keyword": keyword, "lang_code" :lang_code}

            sql ='''
            with recursive aas_tree as (
            select 
            a.aas_pk 
            , null::numeric as sm_pk
            , null::numeric as parent_pk
            , a.id
            , a.id_short
            , fn_json_lang_text(a.description, %(lang_code)s) as "description" 
            , fn_json_lang_text(a."displayName", %(lang_code)s) as "displayName"
            , 'aas' as gubun
            , a."_created" 
            , 1 as lvl
            , (select count(*) from specific_asset where specific_asset.asset_pk= ai.asset_pk) as asset_count
            , to_char(a._created, 'yyyy-mm-dd hh24:mi:ss') created
            from aas a   
            left join asset_info ai on a.asset_pk = ai.asset_pk 
            where 1=1
            '''
            if keyword:
                sql+='''
                and exists ( select 1  from jsonb_array_elements(a."displayName") as kk  where  kk->>'language' = 'ko-KR' and upper(kk->>'text') like concat('%%',upper(%(keyword)s),'%%'))
                '''

            sql+='''
            union all 
            select
                sb.aas_pk
                , sb.sm_pk
                , sb.aas_pk as parent_pk
                , sb.id
                , sb.id_short
            , fn_json_lang_text(sb.description, %(lang_code)s) as "description" 
            , fn_json_lang_text(sb."displayName", %(lang_code)s) as "displayName"
                , 'sub' as gubun
                , sb."_created"
                , (aatt.lvl+1)  as lvl
                , null as asset_count
                ,to_char(sb._created, 'yyyy-mm-dd hh24:mi:ss') created
            from submodel sb
            inner join aas_tree aatt on sb.aas_pk = aatt.aas_pk and aatt.gubun='aas'
            )
            select
            aas_tree.aas_pk
            , aas_tree.sm_pk
            , aas_tree.id
            , aas_tree.id_short
            , aas_tree.parent_pk
            , aas_tree."displayName" 
            , aas_tree.gubun 
            , aas_tree."_created" 
            , aas_tree.lvl
            , aas_tree.asset_count
            , aas_tree.created
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
                aas = None

                if gubun=="aas":
                    if aas_pk in dic_aas:
                        aas = dic_aas.get(aas_pk)
                    else:
                        aas = item
                        dic_aas[aas_pk] = aas
                        aas["sub_items"] = []
                        aas_items.append(item)
                else:
                    aas = dic_aas.get(aas_pk)
                    sub_items = aas.get('sub_items')
                    sub_items.append(item)

            result['success'] = True
            result['items'] = aas_items

        elif action=="aas_detail":
            aas_pk = gparam.get('data_pk')
            dic_param = {"aas_pk": aas_pk, "lang_code" :lang_code}

            sql='''
            select 
            a.aas_pk 
            , null::numeric as sm_pk
            , null::numeric as parent_pk
            , a.id
            , a.id_short
            , fn_json_lang_text(a.description, %(lang_code)s) as "description" 
            , fn_json_lang_text(a."displayName", %(lang_code)s) as "displayName"
            , 'aas' as gubun
            , a."_created" 
            , 1 as lvl
            , (select count(*) from specific_asset where specific_asset.asset_pk= ai.asset_pk) as asset_count
            , to_char(a._created, 'yyyy-mm-dd hh24:mi:ss') created
            , a.description as json_description
            , a."displayName" as json_displayname
            from aas a   
            left join asset_info ai on a.asset_pk = ai.asset_pk 
            where a.aas_pk=%(aas_pk)s
            '''

            data = DbUtil.get_row(sql, dic_param)
            result['success'] = True
            result['data'] = data

        elif action=="sub_detail":
            sm_pk = gparam.get('data_pk')
            dic_param = {"sm_pk": sm_pk}

            sql='''
            select
            sb.aas_pk
            , sb.sm_pk
            , sb.aas_pk as parent_pk
            , sb.id
            , sb.id_short
            , fn_json_lang_text(sb.description, %(lang_code)s) as "description" 
            , fn_json_lang_text(sb."displayName", %(lang_code)s) as "displayName"
            , 'sub' as gubun
            , to_char(sb._created, 'yyyy-mm-dd hh24:mi:ss') created
            from submodel sb
            where sb.sm_pk=%(sm_pk)s
            '''

            DbUtil.execute(sql, dic_param)
            result['success'] = True
            result['data'] = data

        elif action=='submodel_element_list':
            sm_pk = gparam.get('sm_pk')
            dic_param = {"sm_pk": sm_pk}

            sql='''

            select 
            se.sme_pk
            , se."ModelKind"
            , se.model_type
            , fn_json_lang_text(se.description, 'ko-KR') as "description" 
            , fn_json_lang_text(se."displayName", 'ko-KR') as "displayName"
            , to_char(se._created, 'yyyy-mm-dd hh24:mi:ss') created
            from submodel s 
            inner join submodel_element se  on s.sm_pk = se.sm_pk
            where s.sm_pk =1
            '''
            sm_elements = DbUtil.get_row(sql, dic_param)

            for smelement in sm_elements:
                model_type = smelement['model_type']
                if model_type=='Property':
                    pass




            result['success'] = True
            result['items'] = items

        else:

            category = posparam.get('category')
            description = posparam.get('description')
            id_short = posparam.get('id_short')
            aas_id = posparam.get('aas_id')
            asset_pk = posparam.get('asset_pk')
            disp_name_pk = posparam.get('disp_name_pk')
            desc_pk = posparam.get('desc_pk')

            aas = DBAssetAdministrationShell()
            aas.category = category
            aas.displayName.id = disp_name_pk
            if desc_pk:
                aas.description.id = desc_pk

            aas.set_audit(user)
            aas.save()


    except Exception as ex:
        LogWriter.add_dblog("error", source, ex)
        result['message'] = str(ex)
        result['success'] = False


    return result


        







