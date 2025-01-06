from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.system import SystemCode


def sys_code_setup(context):
    '''
    /api/system/sys_code_setup

    작성명 : 시스템 코드
    작성자 : 김진욱
    작성일 : 2024-09-06
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
            sch_sys_code_type = gparam.get('sch_sys_code_type')
            keyword = gparam.get('srch_keyword')
            
            sql = '''
                select sc.id as sc_id
                    , sc."CodeType" as code_type
                    , sc."Code" as code
                    , sc."Value" as value
                    , sc._ordering as _order
                    , sc."Description" as description 
                    from sys_code sc 
                    where 1=1
            '''
            
            if sch_sys_code_type:
                sql += ''' and sc."CodeType" = %(sch_sys_code_type)s '''


            dc = {}
            dc['sch_sys_code_type'] = sch_sys_code_type
            dc['keyword'] = keyword
            
            result = DbUtil.get_rows(sql,dc)
            
        elif action == 'sys_setup':
            syscode_items = [
                # 결과값 유형
                {"CodeType": "result_type", "Code": "N", "Value": "수치형", "Description": "결과값유형"},
                {"CodeType": "result_type", "Code": "S", "Value": "선택형", "Description": "결과값유형"},
                {"CodeType": "result_type", "Code": "D", "Value": "서술형", "Description": "결과값유형"},
                {"CodeType": "result_type", "Code": "Y", "Value": "날짜형", "Description": "결과값유형"},
                {"CodeType": "result_type", "Code": "T", "Value": "시간형", "Description": "결과값유형"},
                {"CodeType": "result_type", "Code": "X", "Value": "결과없음", "Description": "결과값유형"},
                # 언어코드
                
                {"CodeType": "lang_code", "Code": "ko-KR", "Value": "한국어", "Description": "언어코드"},
                {"CodeType": "lang_code", "Code": "en-US", "Value": "영어", "Description": "언어코드"},
                # 제품구분
                
                {"CodeType": "prod_type", "Code": "product", "Value": "제품", "Description": "제품유형"},
                {"CodeType": "prod_type", "Code": "semi", "Value": "반제품", "Description": "제품유형"},
                {"CodeType": "prod_type", "Code": "raw_mat", "Value": "원재료", "Description": "제품유형"},
                # 고객구분
                
                {"CodeType": "comp_kind", "Code": "C", "Value": "고객", "Description": "회사구분"},
                {"CodeType": "comp_kind", "Code": "S", "Value": "공급처", "Description": "회사구분"},
                # 채취장소구분
                
                {"CodeType": "smp_point_cls", "Code": "Tank", "Value": "Tank", "Description": "채취장소유형"},
                {"CodeType": "smp_point_cls", "Code": "Silo", "Value": "Silo", "Description": "채취장소유형"},
                # 설비상태
                
                {"CodeType": "inst_state", "Code": "IS01", "Value": "정상", "Description": "시험기기상태"},
                {"CodeType": "inst_state", "Code": "IS02", "Value": "고장", "Description": "시험기기상태"},
                {"CodeType": "inst_state", "Code": "IS03", "Value": "수리중", "Description": "시험기기상태"},
                {"CodeType": "inst_state", "Code": "IS04", "Value": "폐기", "Description": "시험기기상태"},
                # 측정단위종류
                
                {"CodeType": "test_unit_type", "Code": "LGTH", "Value": "길이", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "CONC", "Value": "농도", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "WT", "Value": "무게", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "DENS", "Value": "밀도", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "VOL", "Value": "부피", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "TIME", "Value": "시간", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "P", "Value": "압력", "Description": "측정단위종류"},
                {"CodeType": "test_unit_type", "Code": "E", "Value": "기타", "Description": "측정단위종류"}
            ]

            for item in syscode_items:
                code_type = item.get('CodeType')
                code = item.get('Code')
                value = item.get('Value')
                description = item.get('Description')
                count  = SystemCode.objects.filter(CodeType=code_type,Code=code).count()

                if count == 0:
                    syscode = SystemCode(CodeType=code_type,Code=code, Value=value, Description=description )
                    syscode.save()

            result = {'success':True}

    except Exception as ex:
        source = '/api/system/sys_code_setup, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}

    return result