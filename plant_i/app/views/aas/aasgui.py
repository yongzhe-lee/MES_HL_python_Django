
from turtle import pos
from unicodedata import category
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.aas import DBAssetAdministrationShell

def aasgui(context) :
    '''
    /api/aas/gui
    '''

    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    lang_code = user.userprofile.lang_code

    if lang_code is None:
        lang_code = 'ko-KR'

    method = request.method

    result = {}

    try:
        if method == 'GET' :

            keyword = gparam.get('keyword')

            sql ='''
            with recursive aas_tree as (
            select 
            a.aas_pk 
            , 0 as parent_pk
            , fn_lang_text(a.disp_name_pk, 'displayName', %(lang_code)) as disp_name
            , 'aas' as gubun
            , a."_created" 
            , 0 as lvl
            from aas a   
            left join asset_info ai on a.asset_pk = ai.asset_pk 
            left join specific_asset sa on sa.asset_pk = ai.asset_pk
            union all 
            select
             aatt.aas_pk
             , aatt.aas_pk as parent_pk 
             , fn_lang_text(sb.disp_name_pk, 'displayName', %(lang_code)) as disp_name
             , 'submodel' as gubun
              , sb."_created"
             , 1 as lvl 
            from submodel sb
            inner join aas_tree aatt on sb.aas_pk = aatt.aas_pk
            )
            select 
            aas_tree.aas_pk 
            , aas_tree.parent_pk
            , aas_tree.disp_name 
            , aas_tree.gubun 
            , aas_tree."_created" 
            , aas_tree.lvl
            from aas_tree
            where 1=1
            '''
            if keyword:
                sql += '''
                and UPPER(aas_tree.disp_name) like CONCAT('%%', UPPER(%(keyword)s), '%%')
                '''


            items = DbUtil.get_rows(sql, gparam)

            result['success'] = True
            result['items'] = items

        elif method=='POST':

           #asset_kind = posparam.get("asset_kind")
           #asset_type = posparam.get("asset_type")

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




    except Exception as e:
        LogWriter.error('Error: %s' % str(e))
        result['message'] = str(e)
        result['success'] = False


    return result


        







