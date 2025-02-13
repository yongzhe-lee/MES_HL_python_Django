from domain.gui import GUIConfiguration
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.user import Depart
from domain.services.common import CommonUtil
from django.http import JsonResponse


def depart(context):
    '''
    /api/system/depart
    
    -수정사항-
    수정일             작업자     수정내용
    2020-01-01         홍길동     unit 조인추가
    '''
    gparam = context.gparam
    posparam = context.posparam

    action = gparam.get('action')
    user = context.request.user

    try:
        if action=='read':
            dept_name = gparam.get('dept_name', '')
            
            sql = '''
            SELECT 
                d.id AS dept_id
                , d."UpDept_id" AS parent_id
                , d."UpDeptCode" AS parent_code
                , d."ReqDivCode" AS reqdiv_code
                , d."Code" AS dept_code
                , d."Name" AS dept_name
                , d._modified
	            , d."LabYN" AS lab_yn
	            , d."MfgYN" AS mfg_yn
                , d."RoleNo" AS role_no
	            , ug."Name" AS role_name
                , d."UseYN" AS use_yn
                , d."ApplyYN" AS apply_yn
	            , d."_creater_id"
                , cu."Name" AS create_user_nm
                , d._created
	            , d."_modifier_id"
                , uu."Name" AS update_user_nm
                , s."Name" AS site_name
                , s.id AS site_no
                , up."Name" AS up_dept
            FROM 
                dept d
            LEFT JOIN 
                site s ON d."Site_id" = s.id
            LEFT JOIN 
                user_profile cu ON d._creater_id = cu."User_id"
            LEFT JOIN 
                user_profile uu ON d._modifier_id = uu."User_id"
            LEFT JOIN 
                user_group ug ON ug.id = d."RoleNo"
            LEFT JOIN 
                dept up ON up.id = d."UpDept_id"
            WHERE  1=1
                AND d."DelYN"='N'
            '''
            if dept_name:
                sql += '''
                AND d."Name" = %(dept_name)s
                '''

            dc = {}
            dc['dept_name'] = dept_name
            result = DbUtil.get_rows(sql, dc)

        elif action == 'get_dept':
            keyword = gparam.get('keyword')
            sql = '''
            SELECT 
                d.id AS dept_id
                , d."UpDept_id" AS parent_id
                , d."Code" AS dept_code
                , d."Name" AS dept_name
                , d."ReqDivCode" AS reqdiv_code
                , d."LabYN" AS lab_yn
	            , d."MfgYN" AS mfg_yn
                , d."UseYN" AS use_yn
	            , d."ApplyYN" AS apply_yn
                , ug."Name" AS role_no
                , s."Name" AS site_no
            FROM 
                dept d
            LEFT JOIN 
                site s ON d."Site_id" = s.id
            LEFT JOIN 
                user_group ug ON ug.id = d."RoleNo"
            WHERE 1=1
                AND d."DelYN"='N'
            '''
            if keyword:
                sql += '''
                AND (
                    UPPER(d."Name") LIKE UPPER(CONCAT('%%', %(keyword)s, '%%'))
                    OR UPPER(d."Code") LIKE UPPER(CONCAT('%%', %(keyword)s, '%%'))
                )
                '''
            dc = {}
            dc['keyword'] = keyword
            data = DbUtil.get_rows(sql, dc)
            result = {'items': data}
            
        elif action =='save':
            dept_id = posparam.get('dept_id')
            dept_code = posparam.get('dept_code')
            dept_name = posparam.get('dept_name')
            reqdiv_code = posparam.get('reqdiv_code')
            lab_yn = posparam.get('lab_yn')
            mfg_yn = posparam.get('mfg_yn')
            role_no = posparam.get('role_no')
            use_yn = posparam.get('use_yn')
            apply_yn = posparam.get('apply_yn')
            up_dept = CommonUtil.blank_to_none(posparam.get('up_dept'))
            site_no = posparam.get('site_no')
            
            # 상위 부서 조회 및 None 처리
            up_dept = Depart.objects.filter(Name=up_dept).first()
            up_dept_id = up_dept.id if up_dept else None
            up_dept_code = up_dept.Code if up_dept else None
            
            dept = None
            if dept_id:
                dept = Depart.objects.filter(id=dept_id).first()
            else:
                dept = Depart()

            dept.Code = dept_code
            dept.Name = dept_name
            dept.UpDept_id = up_dept_id
            dept.UpDept_code = up_dept_code
            dept.ReqDivCode = reqdiv_code
            dept.LabYN = lab_yn
            dept.MfgYN = mfg_yn
            dept.RoleNo = role_no
            dept.UseYN = use_yn
            dept.ApplyYN = apply_yn
            dept.Site_id = site_no
            dept.set_audit(user)
            dept.save()

            result = { 'success': True }
        
        elif action == 'delete':
            dept_id = posparam.get('dept_id')
            dept = Depart.objects.filter(id=dept_id).first()
            dept.DelYN = 'Y'
            dept.set_audit(user)
            dept.save()
            
            result = { 'success': True }

        elif action == 'depart_tree':
            def build_tree(nodes, parent_id=None):
                tree = []
                for node in nodes:
                    if node["UpDept_id"] == parent_id:
                        children = build_tree(nodes, node["id"])
                        tree.append({
                            "id": node["id"],
                            "text": node["Name"],
                            "items": children if children else []
                        })
                return tree

            try:
                # DB에서 부서 정보 조회
                departments = Depart.objects.filter(UseYN='Y', DelYN='N').values('id', 'Name', 'UpDept_id')
                print("📌 부서 데이터 확인:", list(departments))  # 🚀 로그 추가

                # 트리 구조 변환
                department_tree = build_tree(list(departments))

                # ✅ `{ "items": [...] }` 형식으로 반환
                result = {"items": department_tree}

            except Exception as e:
                print("🚨 서버 오류 발생:", str(e))  # 🚀 콘솔에 오류 로그 출력
                result = {"error": str(e)}

        else:
            result = {'error': 'Invalid action'}

    except Exception as ex:
        source = 'dept : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return result






