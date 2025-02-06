
from turtle import pos
from unicodedata import category
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil

from domain.models.aas import DBAssetAdministrationShell


def shells(context) :
    '''
    표준 자산 관리 쉘 목록 조회
    /api/aas/shells

    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    lang_code = user.userprofile.lang_code

    method = request.method

    result = {}

    try:
        if method == 'GET' :

            keyword = gparam.get('keyword')

            sql ='''
            with tt as (
            select
            li.lang_item_pk 
            , lt.language
            , lt.text as displayname 
            , li.category 
            , li."StringType" 
            from lang_item li 
            inner join lang_text lt on li.lang_item_pk = lt.lang_item_pk 
            where li.category='displayName'
            limit 1
            )
            select 
            a.aas_pk 
            , a.id as aas_id
            , a.category 
            , a.disp_name_pk 
            , tt.displayname
            , a.base_aas_pk 
            from aas a 
            left join tt on tt.lang_item_pk = a.disp_name_pk 
            left join asset_info ai on a.asset_pk = ai.asset_pk 
            left join specific_asset sa on sa.asset_pk = ai.asset_pk 
            '''
            if keyword:
                sql += '''
                where 
                OR UPPER(tt.displayname) like CONCAT('%%', UPPER(%(keyword)s), '%%')
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

'''

{
  "extensions": [
    {
      "name": "string",
      "valueType": 0,
      "value": "string",
      "refersTo": [
        {
          "type": 0,
          "keys": [
            {
              "type": 0,
              "value": "string"
            }
          ]
        }
      ]
    }
  ],
  "category": "string",
  "idShort": "string",
  "displayName": [
    {}
  ],
  "description": [
    {}
  ],
  "administration": {
    "version": "string",
    "revision": "string",
    "creator": {
      "type": 0,
      "keys": [
        {
          "type": 0,
          "value": "string"
        }
      ]
    },
    "templateId": "string"
  },
  "id": "string",
  "embeddedDataSpecifications": [
    {
      "dataSpecification": {
        "type": 0,
        "keys": [
          {
            "type": 0,
            "value": "string"
          }
        ]
      },
      "dataSpecificationContent": {}
    }
  ],
  "derivedFrom": {
    "type": 0,
    "keys": [
      {
        "type": 0,
        "value": "string"
      }
    ]
  },
  "assetInformation": {
    "assetKind": 0,
    "globalAssetId": "string",
    "specificAssetIds": [
      {
        "name": "string",
        "value": "string",
        "externalSubjectId": {
          "type": 0,
          "keys": [
            {
              "type": 0,
              "value": "string"
            }
          ]
        }
      }
    ],
    "assetType": "string",
    "defaultThumbnail": {
      "path": "string",
      "contentType": "string"
    }
  },
  "submodels": [
    {
      "type": 0,
      "keys": [
        {
          "type": 0,
          "value": "string"
        }
      ]
    }
  ],
  "parent": {},
  "timeStampCreate": "2025-02-05T08:13:37.280Z",
  "timeStamp": "2025-02-05T08:13:37.280Z",
  "timeStampTree": "2025-02-05T08:13:37.280Z"
}

'''
        







