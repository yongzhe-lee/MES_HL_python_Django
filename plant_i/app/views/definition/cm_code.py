from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
# from domain.models.definition import CodeGroup, Code
from domain.models.cmms import CmBaseCodeGroup, CmBaseCode
from django.db import transaction

def cm_code(context):
    '''
    api/definition/cm_code
        getCodeClassTree: 트리용 그룹 코드 조회
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user

    action = gparam.get('action', 'read') 

    try:
        if action == 'read':
            code_grp_code = gparam.get('code_grp_code')
            keyword = gparam.get('sch_keyword')
            use_yn = gparam.get('sch_use_yn')

            sql = '''
            SELECT
                c.code_pk as id
                , c."code_grp_cd" AS code_grp_code
                , c."code_cd" AS code
                , c."code_nm" AS name
                , c."use_yn" AS use_yn
                , c."attr1" AS attr1
                , '' AS attr2
                , '' AS attr3
                , c."code_dsc" AS remark
                , c."disp_order" AS disp
            FROM 
                cm_base_code c
            INNER JOIN 
                cm_base_code_grp cg ON c."code_grp_cd" = cg."code_grp_cd" 
            WHERE 1=1 
                AND c."use_yn" = 'Y'
            '''
            if code_grp_code:
                sql += '''
                    AND UPPER(c."code_grp_cd") = UPPER(%(code_grp_code)s)
                '''
            if keyword:
                sql += ''' 
                AND (
                    UPPER(c."code_cd") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(c."code_nm") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(c."code_dsc") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                ) 
                '''
            if use_yn:
                sql +='''
                AND c."UseYn" = %(use_yn)s
                '''

            sql += '''
            ORDER BY 
                c."disp_order" IS NULL asc, c."disp_order", c."code_cd";
            '''

            dc = {}
            dc['code_grp_code'] = code_grp_code
            dc['keyword'] = keyword
            dc['use_yn'] = use_yn

            items = DbUtil.get_rows(sql, dc)


        elif action in ['getCodeClassTree']:

            sql = '''
            SELECT
                cg."code_grp_cd" as id
                , cg."code_grp_cd" AS grp_code
                , cg."code_grp_nm" AS grp_name
                , 'N' AS grp_sys_yn
                , 'Y' AS grp_use_yn
                , cg."code_grp_dsc" AS grp_remark
            FROM 
                cm_base_code_grp cg
            WHERE 1=1
            ORDER BY cg."code_grp_cd", cg."code_grp_nm";
            '''
            items = DbUtil.get_rows(sql)

        elif action == 'save':
            grp = CommonUtil.blank_to_none(posparam.get('grp'))
            id = posparam.get('id')
            
            with transaction.atomic():

                if grp:
                    # code_group
                    grp_code = posparam.get('grp_code', '').strip()
                    grp_name = posparam.get('grp_name', '').strip()
                    grp_sys_yn = posparam.get('grp_sys_yn')
                    grp_use_yn = posparam.get('grp_use_yn')
                    grp_remark = posparam.get('grp_remark', '').strip()


                    old_grp_code = None

                    # 기존 Group 코드 가져오기(수정 전)
                    if id:
                        existing_group = CmBaseCodeGroup.objects.get(CodeGroupCode=id)
                        old_grp_code = existing_group.CodeGroupCode

                    # 중복체크
                    q = CmBaseCodeGroup.objects.filter(CodeGroupCode=grp_code)

                    if id:
                        q = q.exclude(CodeGroupCode=id)
                    
                    if id:
                        cg = CmBaseCodeGroup.objects.get(CodeGroupCode=id)
                    else:
                        cg = CmBaseCodeGroup()

                    cg.CodeGroupCode = grp_code
                    cg.CodeGrpName = grp_name
                    cg.CodeGrpDsc = grp_remark         
                    # cg.set_audit(user)
                    cg.save()

                    # 기존 Group 코드와 다른 경우 관련 Code들의 Group 코드 동기화
                    if old_grp_code and old_grp_code != grp_code:
                        CmBaseCode.objects.filter(CodeGroupCode=old_grp_code).update(CodeGroupCode=grp_code)

                        return {'success': True, 'message': '그룹 코드 및 관련 코드들의 정보가 수정되었습니다.'}

                    items = { 'success': True }

                else:
                    # code
                    code_grp_code = posparam.get('code_grp_code', '').strip()
                    code = posparam.get('code', '').strip()
                    name = posparam.get('name', '').strip()
                    disp = CommonUtil.try_int(posparam.get('disp'))
                    attr1 = posparam.get('attr1')
                    use_yn = posparam.get('use_yn')

                    q = CmBaseCode.objects.filter(GroupCode = code_grp_code, CodeCd = code)

                    if id:
                        q = q.exclude(id=id)

                    existing = q.first()

                    if existing:
                        if existing.UseYn == 'N':
                            return {'success': False, 'message': '삭제된 코드가 존재합니다. 복구를 요청하세요.'}
                        else:
                            return {'success': False, 'message': '중복된 코드가 존재합니다.'}

                    if id:
                        c = CmBaseCode.objects.get(id=id)
                    else:
                        c = CmBaseCode()

                   
                    group_obj = CmBaseCodeGroup.objects.get(CodeGroupCode=code_grp_code)
                    c.CmBaseCodeGroup = group_obj  # ✅ 올바른 객체 지정

                    c.CodeCd = code
                    c.CodeName = name
                    c.DispOrder = disp
                    c.Attr1 = attr1
                    c.UseYn = use_yn
                    c.set_audit(user)
                    c.save()

                    items = { 'success': True }

        elif action == 'delete':
            grp = CommonUtil.blank_to_none(posparam.get('grp'))
            id = CommonUtil.try_int(posparam.get('id'))
            
            if grp:
                code_group = CmBaseCodeGroup.objects.get(CodeGroupCode=id)
                linked_codes = CmBaseCode.objects.filter(CmBaseCodeGroup=code_group.CodeGroupCode, UseYn='Y')

                if linked_codes.exists():
                    return {'success': False, 'message': f'그룹 코드 "{code_group.Code}"에 연결된 코드가 존재합니다. 먼저 관련 코드를 삭제하거나 이동하세요.'}

                code_group.save()
                
            else:
                code = CmBaseCode.objects.get(id=id)
                code.UseYn = 'N'
                code.save()

            items = {'success': True}
    
    except Exception as ex:
        source = 'definition/cm_code : action-{}'.format(action)
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