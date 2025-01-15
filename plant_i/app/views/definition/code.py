from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.definition import CodeGroup, Code
from django.db import transaction

def code(context):
    '''
    api/definition/code
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

            sql = '''
            SELECT
                c.id
                , c."CodeGroupCode" AS code_grp_code
                , c."Code" AS code
                , c."Name" AS name
                , c."UseYn" AS use_yn
                , c."Attr1" AS attr1
                , c."Attr2" AS attr2
                , c."Attr3" AS attr3
                , c."Remark" AS remark
                , c."DispOrder" AS disp
            FROM 
                code c
            INNER JOIN 
                code_group cg ON c."CodeGroupCode" = cg."Code" 
            WHERE 1=1 
            '''

            if code_grp_code:
                sql += '''
                    AND UPPER(c."CodeGroupCode") = UPPER(%(code_grp_code)s)
                '''

            sql += '''
                /* AND c."UseYn" = 'Y' */
                AND c."DelYn" = 'N'
            ORDER BY 
                c."DispOrder" IS NULL asc, c."DispOrder", c."Name";
            '''

            dc = {}
            dc['code_grp_code'] = code_grp_code

            items = DbUtil.get_rows(sql, dc)


        elif action in ['getCodeClassTree']:

            sql = '''
            SELECT
                cg.id
                , cg."Code" AS grp_code
                , cg."Name" AS grp_name
                , cg."SystemYn" AS grp_sys_yn
                , cg."UseYn" AS grp_use_yn
                , cg."Remark" AS grp_remark
            FROM 
                code_group cg
            WHERE 1=1
                /* AND cg."UseYn" = 'Y' */
                AND cg."DelYn" = 'N'
            ORDER BY 
                cg."Name";
            '''
            items = DbUtil.get_rows(sql)

        elif action == 'save':
            grp = CommonUtil.blank_to_none(posparam.get('grp'))
            id = CommonUtil.try_int(posparam.get('id'))
            
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
                        existing_group = CodeGroup.objects.get(id=id)
                        old_grp_code = existing_group.Code

                    # 중복체크
                    q = CodeGroup.objects.filter(Code=grp_code)

                    if id:
                        q = q.exclude(id=id)

                    existing = q.first()

                    if existing:
                        if existing.DelYn == 'Y':
                            return {'success': False, 'message': '삭제된 코드 그룹이 존재합니다. 복구를 요청하세요.'}
                        else:
                            return {'success': False, 'message': '중복된 코드 그룹이 존재합니다.'}

                    if id:
                        c = CodeGroup.objects.get(id=id)
                    else:
                        c = CodeGroup()

                    c.Code = grp_code
                    c.Name = grp_name
                    c.SystemYn = grp_sys_yn
                    c.Remark = grp_remark
                    c.UseYn = grp_use_yn
                    c.set_audit(user)
                    c.save()

                    # 기존 Group 코드와 다른 경우 관련 Code들의 Group 코드 동기화
                    if old_grp_code and old_grp_code != grp_code:
                        Code.objects.filter(CodeGroupCode=old_grp_code).update(CodeGroupCode=grp_code)

                        return {'success': True, 'message': '그룹 코드 및 관련 코드들의 정보가 수정되었습니다.'}

                    items = { 'success': True }

                else:
                    # code
                    code_grp_code = posparam.get('code_grp_code', '').strip()
                    code = posparam.get('code', '').strip()
                    name = posparam.get('name', '').strip()
                    disp = CommonUtil.try_int(posparam.get('disp'))
                    attr1 = posparam.get('attr1')
                    attr2 = posparam.get('attr2')
                    attr3 = posparam.get('attr3')
                    remark = posparam.get('remark', '').strip()
                    use_yn = posparam.get('use_yn')

                    q = Code.objects.filter(CodeGroupCode = code_grp_code, Code = code)

                    if id:
                        q = q.exclude(id=id)

                    existing = q.first()

                    if existing:
                        if existing.DelYn == 'Y':
                            return {'success': False, 'message': '삭제된 코드가 존재합니다. 복구를 요청하세요.'}
                        else:
                            return {'success': False, 'message': '중복된 코드가 존재합니다.'}

                    if id:
                        c = Code.objects.get(id=id)
                    else:
                        c = Code()

                    c.CodeGroupCode = code_grp_code
                    c.Code = code
                    c.Name = name
                    c.DispOrder = disp
                    c.Attr1 = attr1
                    c.Attr2 = attr2
                    c.Attr3 = attr3
                    c.Remark = remark
                    c.UseYn = use_yn
                    c.set_audit(user)
                    c.save()

                    items = { 'success': True }

        elif action == 'delete':
            grp = CommonUtil.blank_to_none(posparam.get('grp'))
            id = CommonUtil.try_int(posparam.get('id'))
            
            if grp:
                code_group = CodeGroup.objects.get(id=id)
                linked_codes = Code.objects.filter(CodeGroupCode=code_group.Code, DelYn='N')

                if linked_codes.exists():
                    return {'success': False, 'message': f'그룹 코드 "{code_group.Code}"에 연결된 코드가 존재합니다. 먼저 관련 코드를 삭제하거나 이동하세요.'}

                code_group.DelYn = 'Y'
                code_group.save()
                
            else:
                code = Code.objects.get(id=id)
                code.DelYn = 'Y'
                code.save()

            items = {'success': True}
    
    except Exception as ex:
        source = 'definition/code : action-{}'.format(action)
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