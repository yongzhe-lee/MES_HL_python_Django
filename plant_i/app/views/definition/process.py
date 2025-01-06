from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from django.db import transaction
from domain.models.definition import Process

def process(context):
    '''
    /api/master/process
    
    작성명 : 공정
    작성자 : 
    작성일 : 
    비고 :

    -수정사항-
    수정일             작업자     수정내용

    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    
    action = gparam.get('action', 'read')
    try:
        if action =='read':
            
            keyword = gparam.get('sch_keyword')

            sql = '''
            SELECT 
                p.id AS process_id
                , p."Name" AS process_name
                , p."Code" AS process_code
                , p."ProcessType" AS process_type
                , p."Description" AS description
            FROM 
                process p 
            WHERE 1=1
            '''
            if keyword:
                sql += ''' 
                AND (p."Name" LIKE %(keyword)s OR u."Code" LIKE %(keyword)s) 
                '''

            sql += '''
            ORDER BY p."Name"
            '''

            dc = {}
            dc['keyword'] = keyword
            
            result = DbUtil.get_rows(sql, dc)
        

        elif action == 'detail':
            id = gparam.get('id')
            
            sql = '''
            SELECT 
                p.id AS process_id
                , p."Name" AS process_name
                , p."Code" AS process_code
                , p."ProcessType" AS process_type
                , p."Description" AS description
            FROM 
                process p 
            where 1=1
                AND p.id = %(id)s
            '''

            dc = {}
            dc['id'] = id
            
            result = DbUtil.get_row(sql, dc)

        elif action == 'save':
            id = posparam.get('process_id')
            process_name = posparam.get('process_name') 
            process_code = posparam.get('process_code') 
            process_type = posparam.get('process_type')
            description = posparam.get('description')

            # 중복검사
            check_name = Process.objects.filter(Name = process_name)
            check_code = Process.objects.filter(Code = process_code)

            if id:
                check_name = check_name.exclude(id = id)
                check_code = check_code.exclude(id = id)

            check_name = check_name.first()
            check_code = check_code.first()

            if check_name:
                result = {'success' : False, 'message' : '중복된 이름이 존재합니다.'}
                return result

            if check_code:
                result = {'success' : False, 'message' : '중복된 코드가 존재합니다.'}
                return result

            if id:
                proc = Process.objects.filter(id = id).first()
            else:
                proc = Process()

            # transaction
            with transaction.atomic():
                proc.Name = process_name
                proc.Code = process_code
                proc.ProcessType = process_type
                proc.Description = description
                proc.set_audit(request.user)
                proc.save()

            result = {'success' : True}

        elif action == 'delete':
            id = posparam.get('id')

            if id:
                proc = Process.objects.filter(id = id).first()
                proc.DelYN = 'Y'
                proc.UseYN = 'N'
                proc.save()

            result = {'success' : True}

    except Exception as ex:
        source = '/api/definition/process, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)

    return result