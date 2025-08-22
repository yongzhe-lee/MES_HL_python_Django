
import os, uuid
from django.db import transaction

from domain.models import DBAssetAdministrationShell, DBResource
from domain.models.aas import DBAssetInformation
from domain.services.aas.asset import AssetService

from domain.services.logging import LogWriter
from domain.services.common import CommonUtil
from configurations import settings
from domain.services.sql import DbUtil

def assetgui(context) :
    '''
    /api/aas/assetgui?action=
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
    result = {'success' : False, "message": ''}
    source = f'/api/aas/assetgui?action={action}'

    asset_service = AssetService()

    try:
        if action=="read":
            asset_kind = gparam.get("asset_kind") # 자산구분 Instance, Type
            asset_type = gparam.get("asset_type") # 자산종류 equipment, software
            aas_yn = gparam.get("aas_yn") # AAS등록여부 Y,N
            keyword = gparam.get("keyword")

            dic_param = {
                "asset_kind": asset_kind, 
                "asset_type":asset_type, 
                "aas_yn" : aas_yn, 
                "lang_code":lang_code,
                "keyword" : keyword
             }

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
            , case when ai."defaultThumbnail_id" is not null then 'Y' else 'N' end as thumbnail_yn
            , to_char(ai._created, 'yyyy-mm-dd hh24:mi:ss') as created 
            , ai._creater_id
            , up."Name" as creator
            , case when a.aas_pk is not null then 'Y' else 'N' end as aas_yn
            , r."contentType"
            , r.path
            from asset_info ai
            left join user_profile up on up."User_id" =ai._creater_id
            left join aas a on a.asset_pk = ai.asset_pk
            left join resource r on r.res_pk  = ai."defaultThumbnail_id"
            where 1=1
            '''
            if asset_kind:
                sql+='''
                and ai."assetKind" = %(asset_kind)s
                '''
            if asset_type:
                sql+='''
                and ai."assetType" = %(asset_Type)s
                '''
            if aas_yn=="Y":
                sql+='''
                and a.aas_pk is not null
                '''
            if keyword:
                sql+='''
                and upper(ai."globalAssetId") like concat('%%',upper(%(keyword)s),'%%'))
                '''

            sql+='''
            order by ai.asset_pk desc
            '''

            items = DbUtil.get_rows(sql, dic_param)
            result["items"] = items
            result["success"] = True

        elif action=="detail_asset":

            asset_pk = gparam.get("asset_pk")      
            data = asset_service.get_asset_detail(asset_pk, lang_code)
            items = asset_service.get_asset_sepecific_ids(asset_pk)

            result["data"] = data
            result["specific_items"] = items
            result["success"] = True
        elif action =="specific_ids":
            asset_pk = gparam.get("asset_pk")
            items = asset_service.get_asset_sepecific_ids(asset_pk);

            result["success"] =True
            result["items"] = items

        elif action=="save_asset":

            # asset Infomation에서 path는 상대경로 resource에서 path는물리적경로를 저장한다.

            asset_pk = posparam.get("asset_pk")
            asset_kind = posparam.get("asset_kind")
            asset_type = posparam.get("asset_type")
            global_asset_id = posparam.get("global_asset_id")
            aas_id = posparam.get("aas_id")

            file = context.request.FILES.get('thumbnailfile', None)

            if asset_pk:
                asset_info = DBAssetInformation.objects.get(asset_pk = asset_pk)
            else:
                asset_info = DBAssetInformation()

            asset_info.assetKind = asset_kind
            asset_info.assetType = asset_type
            asset_info.globalAssetId = global_asset_id
            resource = None
            with transaction.atomic():

                # 업데이트의 경우 파일을 첨부하지 않을 수 있다.
                if file:
                    # asset Infomation에서 path는 상대경로 resource에서 path는물리적경로를 저장한다.

                    ext = os.path.splitext(file.name)[1].replace('.','') or "png"
                    content_type= CommonUtil.get_content_type_ex(ext)

                    resource_directory = f"/resources/thumbnails/"
                    save_folder_path = os.path.join(settings.AAS_BASE_PATH, resource_directory.lstrip('/').replace('/', os.sep))
                    filename = f"{uuid.uuid4()}.{ext}"

                    physical_path = os.path.join(save_folder_path, filename)

                    if not os.path.exists(save_folder_path):
                        os.makedirs(save_folder_path)

                    if asset_info.defaultThumbnail:
                        resource = asset_info.defaultThumbnail
                    else:
                        resource = DBResource()


                    resource.contentType = content_type
                    resource.path = physical_path # 물리적경로

                    
                    asset_info.path = f'{resource_directory}{filename}' # 상대경로

                    resource.set_audit(request.user)
                    resource.save()
                    asset_info.defaultThumbnail = resource
                    with open(physical_path, mode='wb') as upload_file:
                        upload_file.write(file.read())
                else:
                    # 파일이 없으면 기존의 파일을 그대로 사용한다.
                    if not asset_info.defaultThumbnail:
                        #raise ValueError("썸네일 이미지가 없습니다.")
                        print("썸네일 이미지가 없습니다.")
                        result["message"] = "썸네일 이미지가 없습니다."

                asset_info.set_audit(request.user)
                asset_info.save()

                if aas_id:
                    aas = DBAssetAdministrationShell.objects.get(id=aas_id)
                    aas.AssetInformation = asset_info
                    aas.set_audit(request.user)
                    aas.save()



            result["success"] = True
            result["asset_pk"] = asset_info.asset_pk

        elif action=="delete_asset":
                asset_pk = posparam.get("asset_pk")
                if not asset_pk:
                    raise ValueError("자산 정보가 없습니다.")

                asset_info = DBAssetInformation.objects.get(asset_pk=asset_pk)
                if asset_info.defaultThumbnail:
                    asset_info.defaultThumbnail.delete()

                asset_info.delete()

        elif action=="search_aas":
            keyword= gparam.get('keyword')
            dic_param = {"keyword" : keyword, "lang_code": lang_code}
            sql='''
            with recursive at1 as(
              select
              a1.aas_pk
              , a1.id
              , a1.id_short
              , a1."displayName"
              , a1.parent_aas_pk as parent_pk
              , 0 as lvl
              , a1._created
              from aas a1
              where a1.parent_aas_pk is null
              union all
              select
              a2.aas_pk
              , a2.id
              , a2.id_short
              , a2."displayName"  
              , a2.parent_aas_pk as parent_pk
              , at1.lvl+1
              , a2._created
              from aas a2
              inner join at1 on at1.aas_pk = a2.parent_aas_pk      
            )
            select 
             a.aas_pk
             , a.parent_pk
             , a.id
             , a.id_short
             , a."displayName"
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
            order by a.lvl asc
            '''
            items = DbUtil.get_rows(sql, dic_param)
            result["items"] = items
            result["success"] = True


        else:
            pass


    except Exception as ex:
        LogWriter.add_dblog("error", source, ex)
        result["message"] = str(ex)

    return result


