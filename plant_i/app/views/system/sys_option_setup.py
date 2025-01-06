import sys
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.system import SystemCode, SystemOption
from django.db import DatabaseError, transaction

def sys_option_setup(context):
    '''
    /api/system/sys_option_setup

    작성명 : 시스템 옵션
    작성자 : 김진욱
    작성일 : 2024-09-09
    비고 :

    -수정사항-
    수정일             작업자     수정내용
    2020-01-01         홍길동     unit 조인추가
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action  = gparam.get('action','read')
    
    
    try:
        if action == 'read':
            
            sql = '''
                select 
                    so.id AS so_id
                    , so."Code" AS so_code
                    , so."Value" AS so_value
                    , so."Description" AS so_description
                from 
                    sys_option so 
                where 1=1
            '''
            result = DbUtil.get_rows(sql,{})

        elif action == 'sys_option_save':

            id = posparam.get('so_id')

            so_code = posparam.get('so_code') 
            so_value = posparam.get('so_value') 
            so_description = posparam.get('so_description')

            so = SystemOption.objects.filter(id=id).first()

            # transaction
            with transaction.atomic():
                so.Code = so_code
                so.Value = so_value
                so.Description = so_description
                so.save()
                
            result = {'success':True}

        elif action == 'sys_setup':
            
            sysoption_items = [
                # Test sys_option
                {"Code": "test", "Value": "test", "Description": "test_sys_option"}
                
                # 차후 시스템 옵션 추가되면 기입 예정
            ]

            for item in sysoption_items:
                code = item.get('Code')
                value = item.get('Value')
                description = item.get('Description')
                
                count = SystemOption.objects.filter(Code=code).count()

                if count == 0:
                    sys_option = SystemOption(Code=code, Value=value, Description=description)
                    sys_option.save()

            result = {'success':True}

    except Exception as ex:
        source = '/api/system/sys_option_setup, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}

    return result