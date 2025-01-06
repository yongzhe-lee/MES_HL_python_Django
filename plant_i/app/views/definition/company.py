from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.models.definition import Company

def company(context):
    '''
    /api/master/company
    
    작성명 : 업체
    작성자 : 진우석
    작성일 : 2024-08-28
    비고 :

    -수정사항-
    수정일             작업자     수정내용
    '''
    gparam = context.gparam
    posparam = context.posparam
    
    action = gparam.get('action', 'read')
    
    try:
        if action == 'read':
            comp_type = gparam.get('sch_comp_kind')
            keyword = gparam.get('sch_keyword')
            use_yn = gparam.get('filter[use_yn]')

            sql = '''
            select c.id as comp_id
	            , c.Name as comp_name
	            , c.Code as comp_code
	            , c.Email as email
	            , c.TelNo as tel_no
	            , c.Addr as addr
	            , c.BusinessDesc as business_desc
	            , ifnull(c.CustomerYn,'N') as customer_yn
	            , ifnull(c.SupplierYn,'N') as supplier_yn
            -- 	, c.user_text1
            -- 	, c.user_text2
            -- 	, c.user_text3
            -- 	, c.user_text4
            -- 	, c.user_text5
	            , c.Remark as remark
                , c.UseYn as use_yn
	            , c.DelYn as del_yn
	            , c._modifier_id
                , uu.username AS upt_user_nm
	            , DATE_FORMAT(c._modified, '%%Y-%%m-%%d %%H:%%i:%%s') AS upt_date
	            , c._creater_id
                , cu.username AS crt_user_nm
	            , DATE_FORMAT(c._created, '%%Y-%%m-%%d %%H:%%i:%%s') AS crt_date
            from company c
            left outer join auth_user cu on c._creater_id = cu.id
            left outer join auth_user uu on c._modifier_id = uu.id
            where c.DelYn = 'N'
            '''
            if use_yn:
                sql += '''
                and c.UseYn = %(use_yn)s
                '''
            if comp_type: 
                if comp_type == 'S':
                    sql += '''
                    and c.SupplierYn = 'Y'
                    '''
                if comp_type =='C':
                    sql += '''
                    and c.CustomerYn = 'Y'
                    '''
            if keyword:
                sql += '''
                and (
                    c.Name LIKE CONCAT('%%', %(keyword)s, '%%')
                    or c.Code LIKE CONCAT('%%', %(keyword)s, '%%')
                    or c.BusinessDesc LIKE CONCAT('%%', %(keyword)s, '%%')
                    or c.Remark LIKE CONCAT('%%', %(keyword)s, '%%')
                )
                '''
            
            sql += '''
            order by c.Name
            '''

            dc = {}
            dc['keyword'] = keyword
            dc['use_yn'] = use_yn
            
            result = DbUtil.get_rows(sql, dc)
            
        elif action == 'count_company':
            comp_id = gparam.get('comp_id')
            comp_name = gparam.get('comp_name')
            comp_id = int(comp_id)
            
            sql = '''
            select 
	            count(*) as cnt
            from company
            where 1=1
            and DelYn = 'N'
            and id != %(comp_id)s
            and Name = trim(%(comp_name)s)
            '''
            dc = {}
            dc['comp_name'] = comp_name
            dc['comp_id'] = comp_id
            
            result = DbUtil.get_row(sql, dc)
            
        elif action == 'save':
            comp_id = posparam.get('comp_id')
            comp_name = posparam.get('comp_name', '').strip()
            comp_code = posparam.get('comp_code', '').strip()
            email = posparam.get('email', '').strip()
            tel_no = posparam.get('tel_no', '').strip()
            addr = posparam.get('addr', '').strip()
            customer_yn = posparam.get('customer_yn')
            supplier_yn = posparam.get('supplier_yn')
            business_desc = posparam.get('business_desc', '').strip()
            remark = posparam.get('remark', '').strip()
            use_yn = posparam.get('use_yn')
            
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
            comp.Email = email
            comp.TelNo = tel_no
            comp.Addr = addr
            comp.CustomerYn = customer_yn
            comp.SupplierYn = supplier_yn
            comp.BusinessDesc = business_desc
            comp.Remark = remark
            comp.UseYn = use_yn
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
            select 
                Code as code
                , Description as name
            from sys_code
            where CodeType = 'COMP_KIND'
            order by _ordering
            '''
            result = DbUtil.get_rows(sql, {})
        
    except Exception as ex:
        source = '/api/master/company, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result