
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

            with recursive aas_tree as (
            select 
            a.aas_pk 
            , 0 as parent_pk
            , a.id
            , a.id_short
            , a."displayName"
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
             , sb.id
             , sb.id_short
             , sb."displayName"
             , 'submodel' as gubun
             , sb."_created"
             , 1 as lvl 
            from submodel sb
            inner join aas_tree aatt on sb.aas_pk = aatt.aas_pk
            )
            select
            aas_tree.aas_pk
            , aas_tree.id
            , aas_tree.id_short
            , aas_tree.parent_pk
            , aas_tree."displayName" 
            , aas_tree.gubun 
            , aas_tree."_created" 
            , aas_tree.lvl
            from aas_tree
            where 1=1
            '''
            if keyword:
                sql += '''
                where 
                OR UPPER(tt.displayName) like CONCAT('%%', UPPER(%(keyword)s), '%%')
                '''


            items = DbUtil.get_rows(sql, gparam)

            result['success'] = True
            result['items'] = items

        elif method=='POST':

           #asset_kind = posparam.get("asset_kind")
           #asset_type = posparam.get("asset_type")
           id = posparam.get('id')
           id_short = posparam.get('id_short')
           category = posparam.get('category')
           description = posparam.get('description')

           displayName = posparam.get('displpayName')
           description = posparam.get('description')

           aas = DBAssetAdministrationShell()
           aas.category = category
           aas.displayName = {}
           aas.description = {}
           aas.set_audit(user)

           aas.save()


    except Exception as ex:
        source = '/api/aas/shells'
        LogWriter.add_dblog('error', source, ex)
        result['message'] = str(ex)
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
        







