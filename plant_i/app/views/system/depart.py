
from domain.gui import GUIConfiguration
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.user import Depart
from domain.services.common import CommonUtil


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

        elif action == 'read_tree':            
            sql = '''
            WITH RECURSIVE dc2 AS (
                SELECT DISTINCT t1.id,
                       NULL::bigint AS "UpDept_id",
                       t1."Name",
                       CONCAT('', t1."Name") AS indent_dept_nm,
                       1 AS level,
                       ARRAY[t1.id] AS path_info,
                       t1."Code",
                       CAST('' AS TEXT) AS up_dept_cd,
                       CAST('' AS TEXT) AS up_dept_nm,
                       t1."Site_id"
                FROM public.dept t1
                WHERE t1.id IN (
                    SELECT DISTINCT rootdept.id
                    FROM public.dept rootdept
                    LEFT OUTER JOIN public.dept rootUpdept ON rootdept."UpDept_id" = rootUpdept.id
                    WHERE rootdept."DelYN" = 'N' 
                      AND rootdept."UseYN" = 'Y'
                      AND rootdept."Site_id" = '1'
                      AND COALESCE(rootUpdept."Site_id", 0) != '1'
                )
                AND t1."DelYN" = 'N' 
                AND t1."UseYN" = 'Y'
    
                UNION ALL
    
                SELECT DISTINCT t2.id,
                       t2."UpDept_id",
                       t2."Name",
                       CONCAT(RPAD('', s.level * 2, '　'), t2."Name") AS indent_dept_nm,
                       s.level + 1,
                       s.path_info || t2.id,
                       t2."Code",
                       s."Code" AS up_dept_cd,
                       s."Name" AS up_dept_nm,
                       t2."Site_id"
                FROM public.dept t2
                JOIN dc2 s ON s.id = t2."UpDept_id"
                WHERE t2."DelYN" = 'N' 
                  AND t2."UseYN" = 'Y'
                  AND t2."Site_id" = '1'
            ), x AS (
                SELECT DISTINCT dc2.id,
                       dc2."UpDept_id",
                       dc2."Name",
                       dc."Code",
                       dc2.indent_dept_nm,
                       dc2.up_dept_cd,
                       dc2.up_dept_nm,
                       dc2.level,
                       dc."DelYN",
                       dc."UseYN",
                       TO_CHAR(dc."_created", 'YYYY-MM-DD HH24:MI') AS insert_ts,
                       dc."_creater_id",
                       TO_CHAR(dc."_modified", 'YYYY-MM-DD HH24:MI') AS update_ts,
                       dc."_modifier_id",
                       (SELECT COUNT(*) FROM public.dept WHERE "UpDept_id" = dc2.id AND "DelYN" = 'N' AND "Site_id" = '1') AS sub_count,
                       (SELECT COUNT(*) FROM public.dept WHERE "UpDept_id" = dc2.id AND "DelYN" = 'N' AND "Site_id" = '1') AS sub_item_count,
                       dc2.path_info,
                       dc2."Site_id",
                       ARRAY_TO_STRING(dc2.path_info, ',') AS path_info_str -- 🔹 추가
                FROM dc2
                JOIN public.dept dc ON dc.id = dc2.id
                WHERE dc."DelYN" = 'N'
                  AND dc."UseYN" = 'Y'
            )

            SELECT DISTINCT x.id AS dept_pk,
                   x."UpDept_id" AS up_dept_pk,
                   CASE WHEN 'N' = 'Y' AND x.sub_item_count >= 0 THEN x."Name" || ' (' || CAST(x.sub_item_count AS INTEGER) || ')' ELSE x."Name" END AS dept_nm,
                   x."Code" AS dept_cd,
                   x.indent_dept_nm,
                   x.up_dept_cd,
                   x.up_dept_nm,
                   x.level AS lev,
                   x."DelYN",
                   x."UseYN",
                   x.insert_ts,
                   x."_creater_id" AS inserter_id,
                   x.update_ts,
                   x."_modifier_id" AS updater_id,
                   CAST(x.sub_count AS INTEGER) AS sub_count,
                   CAST(x.sub_item_count AS INTEGER) AS sub_item_count,
                   ARRAY_TO_STRING(x.path_info, ',') AS path_info,
                   x.path_info_str -- 🔹 추가
            FROM x
            WHERE x.id IN (
                SELECT DISTINCT UNNEST(x.path_info)
                FROM x
                WHERE x."Site_id" = '1'
            )
            ORDER BY x.path_info_str; -- 🔹 `SELECT` 리스트에 있는 값으로 정렬

            '''            

            result = DbUtil.get_rows(sql)


    except Exception as ex:
        source = 'dept : action-{}'.format(action)
        LogWriter.add_dblog('error', source , ex)
        raise ex

    return result


