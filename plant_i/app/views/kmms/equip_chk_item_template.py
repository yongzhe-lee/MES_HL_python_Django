from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmChkItemTemplate

def equip_chk_item_template(context):
    '''
    api/kmms/equip_chk_item_template    설비점검항목 템플릿
    최성열 

    findAll
    findOne
    selectChkItemTemplate
    insertChkItemTemplate
    deleteChkItemTemplate
   
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':

            keyword = gparam.get('keyword', None)
            dic_param = {'keyword':keyword}

            sql = ''' 
            select t.template_id
	            , t.chk_item
	            , t.unit
	            , t.group_code
	            , t.hash_tag
	            , bc.code_pk as chk_item_unit_pk
	            , t.insert_ts
	            , t.inserter_id
	            , t.update_ts
	            , t.updater_id
            from cm_chk_item_template t
            left outer join cm_base_code bc on t.unit = bc.code_nm and bc.code_grp_cd = 'CHK_ITEM_UNIT'
            where 1=1 
            --t.site_id = 1
            '''

            if keyword:
                sql+=''' 
                    and (upper(t."chk_item") like concat('%%',upper(%(keyword)s),'%%')
                        or upper(t."hash_tag") like concat('%%',upper(%(keyword)s),'%%')
                        )
                '''
        
            items = DbUtil.get_rows(sql, dic_param)
 
        elif action == 'selectChkItemTemplate':
            sql = ''' 
            select t.template_id
                , t.chk_item
                , t.unit
                , t.group_code
                , t.hash_tag
                , t.insert_ts
                , t.inserter_id
                , t.update_ts
                , t.updater_id
            from chk_item_template t
            where 1=1 
                --t.site_id = #{siteId}
            '''

            items = DbUtil.get_rows(sql)

        elif action == 'findOne':            
            templateId = CommonUtil.try_int( gparam.get('templateId') )

            sql = ''' 
            select t.template_id
                , t.chk_item
                , t.unit
                , t.group_code
                , t.hash_tag
                , t.insert_ts
                , t.inserter_id
                , t.update_ts
                , t.updater_id
            from chk_item_template t
            where 1=1 
                --t.site_id = #{siteId}
                and t.template_id = %{templateId}s
            '''
            dc = {}
            dc['templateId'] = templateId

            items = DbUtil.get_rows(sql, dc)

        elif action == 'insertChkItemTemplate':
            id = CommonUtil.try_int(posparam.get('template_id'))
            chkitem = posparam.get('chk_item')
            unit = posparam.get('unit')

            if id:
                return {'success': False, 'message': '수정은 불가능합니다. 신규 등록만 가능합니다.'}

            # 신규 등록만 가능
            c = CmChkItemTemplate()
            c.ChkItem = chkitem
            c.Unit = unit
            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '점검항목이 등록되었습니다.'}

        elif action == 'deleteChkItemTemplate':
            templateId = posparam.get('template_id')
            CmChkItemTemplate.objects.filter(id = templateId).delete()
            
            items = {'success': True}

    except Exception as ex:
        source = 'kmms/equip_chk_item_template : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items    

    return items