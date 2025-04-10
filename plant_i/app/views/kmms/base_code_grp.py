from django import db
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.cmms import CmBaseCodeGroup
from symbol import factor
#from django.db import transaction

def base_code_grp(context):
    '''
    api/kmms/base_code_grp    기초코드그룹
    김태영 작업중

    findAll
    findOne
    countBy
    insert
    update
    delete
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    factory_id = 1

    action = gparam.get('action', 'read') 

    try:
        if action == 'findAll':
            editYn = gparam.get('editYn')

            sql = ''' SELECT code_grp_cd
			, code_grp_nm
			, code_grp_dsc
			, edit_yn
			, disp_order
			, code_pk_yn
		    FROM cm_base_code_grp
		    WHERE 1 = 1
            '''
            if editYn:
                sql += ''' AND edit_yn = %(editYn)s
                '''

            sql += ''' order by 1
            '''

            dc = {}
            dc['editYn'] = editYn

            items = DbUtil.get_rows(sql, dc)
 

        elif action == 'findOne':
            codeGrpCd = gparam.get('codeGrpCd')

            sql = ''' SELECT code_grp_cd
			, code_grp_nm
			, code_grp_dsc
			, edit_yn
			, disp_order
			, code_pk_yn
		    FROM cm_base_code_grp
		    WHERE upper(code_grp_cd) = upper(%(codeGrpCd)s)
            '''

            dc = {}
            dc['codeGrpCd'] = codeGrpCd

            items = DbUtil.get_row(sql, dc)

        elif action == 'countBy':
            codeGrpCd = gparam.get('codeGrpCd')

            sql = ''' SELECT count(*)
		    FROM cm_base_code_grp
            where 1 = 1
            '''
            if codeGrpCd:
                sql += ''' and upper(code_grp_cd) = upper(%(codeGrpCd)s)
                '''

            dc = {}
            dc['codeGrpCd'] = codeGrpCd

            items = DbUtil.get_row(sql, dc)

        elif action in ['insert', 'update']:
            codeGrpCd = posparam.get('codeGrpCd')
            codeGrpNm = posparam.get('codeGrpNm')
            codeGrpDsc = posparam.get('codeGrpDsc')
            dispOrder = posparam.get('dispOrder')
            editYn = posparam.get('editYn')
            codePkYn = posparam.get('codePkYn')
  
            if action == 'update':
                c = CmBaseCodeGroup.objects.get(CodeGroupCode=codeGrpCd)
            else:
                c = CmBaseCodeGroup()
                c.CodeGroupCode = codeGrpCd
                c.EditYn = editYn
            c.CodeGrpName = codeGrpNm
            c.CodeGrpDsc = codeGrpDsc
            c.DispOrder = dispOrder
            
            c.CodePkYn = codePkYn

            c.set_audit(user)
            c.save()

            return {'success': True, 'message': '코드그룹 정보가 수정되었습니다.'}

        elif action == 'delete':
            codeGrpCd = posparam.get('codeGrpCd')
            CmBaseCodeGroup.objects.filter(CodeGroupCode=code_grp_cd).delete()

            items = {'success': True}
  

    except Exception as ex:
        source = 'kmms/base_code_grp : action-{}'.format(action)
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