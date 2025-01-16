from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.definition import Company

def company(context):
    '''
    /api/master/company
    
    작성명 : 업체

    -수정사항-
    수정일             작업자     수정내용
    '''
    gparam = context.gparam
    posparam = context.posparam
    
    action = gparam.get('action', 'read')
    
    try:
        if action == 'read':
            comp_kind = gparam.get('sch_comp_kind')
            keyword = gparam.get('sch_keyword')
            use_yn = gparam.get('sch_use_yn')
            comp_list = []

            sql = '''
            SELECT 
                c.id AS comp_id
	            , c."Name" AS comp_name
	            , c."Code" AS comp_code
	            , c."Site_id" AS site_id
                , s."Name" AS site_name
                , c."CEOName" AS ceo_name
	            , c."CompanyType" AS comp_type
                , c."BusinessType" AS business_type
	            , c."BusinessItem" AS business_item
                , c."Country" AS country
	            , c."Local" AS local
	            , c."Manager" AS manager_name
	            , c."ManagerPhone" AS manager_tel
	            , c."Manager2" AS manager2_name
	            , c."Manager2Phone" AS manager2_tel
                , c."TelNumber" AS tel_no
	            , c."FaxNumber" AS fax_no
	            , c."ZipCode" AS zip_code
                , c."addr" AS addr
                , c."Email" AS email
                , c."Homepage" AS homepage
	            , c."Description" AS desc
            -- 	, c.user_text1
            -- 	, c.user_text2
            -- 	, c.user_text3
            -- 	, c.user_text4
            -- 	, c.user_text5
                , c."UseYn" AS use_yn
	            , c."DelYn" AS del_yn
	            , c._modifier_id
                , c._modifier_nm AS upt_user_nm
	            , TO_CHAR(c._modified, 'YYYY-MM-DD HH24:MI:SS') AS upt_date
	            , c._creater_id
                , c._creater_nm AS crt_user_nm
	            , TO_CHAR(c._created, 'YYYY-MM-DD HH24:MI:SS') AS crt_date
            FROM 
                company c
            LEFT OUTER JOIN 
                site s ON c."Site_id" = s.id
            WHERE 
                c."DelYn" = 'N'
            '''
            if use_yn:
                sql += '''
                AND c."UseYn" = %(use_yn)s
                '''
            if comp_kind:
                # 우선 이렇게. 추후에 코드 정리되면 다시 손볼 것
                # ','로 나누고 각 항목의 공백 제거 후 Python 리스트로 변환
                comp_list = [item.strip() for item in comp_kind.split(',')]
                sql += '''
                AND c."CompanyType" = ANY(%(comp_list)s)
                '''
            if keyword:
                sql += '''
                AND (
                    UPPER(c."Name") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(c."Code") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                    OR UPPER(c."Description") LIKE CONCAT('%%', UPPER(%(keyword)s), '%%')
                )
                '''
            
            sql += '''
            ORDER BY c."Name"
            '''

            dc = {}
            dc['comp_list'] = comp_list
            dc['keyword'] = keyword
            dc['use_yn'] = use_yn
            
            result = DbUtil.get_rows(sql, dc)
            
        elif action == 'save':
            comp_id = posparam.get('comp_id')
            comp_name = posparam.get('comp_name', '').strip()
            comp_code = posparam.get('comp_code', '').strip()
            site_id = posparam.get('site_id')  # ForeignKey
            comp_type = posparam.get('comp_type', '').strip()
            business_type = posparam.get('business_type', '').strip()
            business_item = posparam.get('business_item', '').strip()
            ceo_name = posparam.get('ceo_name', '').strip()
            country = posparam.get('country', '').strip()
            local = posparam.get('local', '').strip()
            manager_name = posparam.get('manager_name', '').strip()
            manager_tel = posparam.get('manager_tel', '').strip()
            manager2_name = posparam.get('manager2_name', '').strip()
            manager2_tel = posparam.get('manager2_tel', '').strip()
            tel_no = posparam.get('tel_no', '').strip()
            fax_no = posparam.get('fax_no', '').strip()
            zip_code = posparam.get('zip_code', '').strip()
            addr = posparam.get('addr', '').strip()
            homepage = posparam.get('homepage', '').strip()
            email = posparam.get('email', '').strip()
            use_yn = posparam.get('use_yn')
            desc = posparam.get('desc', '').strip()
            
            comp = Company()
            id = CommonUtil.try_int(comp_id)

            # 중복 체크
            if CommonUtil.check_duplicate(Company, 'Name', comp_name, exclude_id=id):
                result = {'success': False, 'message': '중복된 이름이 존재합니다.'}
                return result
            
            if id:
                comp = Company.objects.filter(id=id).first()
                
            comp.Name = comp_name
            comp.Code = comp_code
            comp.Country = country
            comp.Local = local
            comp.CompanyType = comp_type
            comp.CEOName = ceo_name
            comp.Email = email
            comp.ZipCode = zip_code
            comp.Address = addr
            comp.TelNumber = tel_no
            comp.FaxNumber = fax_no
            comp.BusinessType = business_type
            comp.BusinessItem = business_item
            comp.Homepage = homepage
            comp.Description = desc
            comp.Manager = manager_name
            comp.ManagerPhone = manager_tel
            comp.Manager2 = manager2_name
            comp.Manager2Phone = manager2_tel
            comp.UseYn = use_yn

            if site_id:
                comp.Site_id = site_id

            comp.set_audit(context.request.user)
            comp.save()
            
            result = {'success':True}

        elif action == 'delete':
            comp_id = posparam.get('comp_id')
            
            comp = Company.objects.filter(id=comp_id).first()
            comp.DelYn = 'Y'
            comp.set_audit(context.request.user)
            comp.save()
            
            result = {'success':True}
            
        elif action == 'comp_type_list':
            sql = '''
            SELECT 
                "Code" AS code
                , "Description" AS name
            FROM sys_code
            WHERE "CodeType" = 'COMP_KIND'
            ORDER BY _ordering
            '''
            result = DbUtil.get_rows(sql, {})
        
    except Exception as ex:
        source = '/api/master/company, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result