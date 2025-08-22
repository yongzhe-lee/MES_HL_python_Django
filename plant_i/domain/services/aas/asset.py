import os
from domain.services.sql import DbUtil
from domain.models import DBResource

class AssetService:
    """
    Service class for managing assets in the AAS (Asset Administration Shell).
    This class provides methods to create, update, and delete assets.
    """
    def __init__(self):
        pass

    def get_asset_detail(self, asset_pk, lang_code='ko-KR'):
        dic_param =  {"asset_pk": asset_pk, "lang_code" : lang_code}
        sql='''
        select 
        ai.asset_pk
        , a.id as aas_id
        , a.aas_pk
        , a."displayName"
        , ai."assetKind"
        , fn_code_name('asset_type', ai."assetType") as asset_type
        , ai."globalAssetId" as global_asset_id
        , ai."defaultThumbnail_id" as default_thumbnail_id
        , to_char(ai._created, 'yyyy-mm-dd hh24:mi:ss') as created 
        , ai._creater_id
        , up."Name" as creator
        , case when a.aas_pk is not null then 'Y' else 'N' end as aas_yn
        , a.id as aas_id
        , r."contentType"
        , r.path
        from asset_info ai
        left join user_profile up on up."User_id" =ai._creater_id
        left join aas a on a.asset_pk = ai.asset_pk
        left join resource r on r.res_pk  = ai."defaultThumbnail_id"
        where ai.asset_pk = %(asset_pk)s
        '''
        data = DbUtil.get_row(sql,dic_param)

        return data


    def get_asset_sepecific_ids(self, asset_pk):
        dic_param = {"asset_pk": asset_pk}

        sql = '''
        select 
            s."name"
            , s.value
            , s.asset_pk
            , to_char(s._created, 'yyyy-mm-dd hh24:mi:ss') as created
            , up."Name"
            from asset_info ai 
            inner join specific_asset s  on s.asset_pk = ai.asset_pk
            left join user_profile up on up."User_id" = s._creater_id
            where 1=1
            and ai.asset_pk = %(asset_pk)s
        '''
        
        items = DbUtil.get_rows(sql, dic_param)
        return items

