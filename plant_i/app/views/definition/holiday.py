from re import T
from domain.services.logging import LogWriter
from domain.services.sql import DbUtil

from domain.models.definition import Holiday
from django.db import DatabaseError, transaction

def holiday(context):
    '''
    /api/definition/holiday
    
    작성명 : 공휴일
    작성자 : 김진욱
    작성일 : 2024-09-05
    비고 :

    -수정사항-
    수정일             작업자     수정내용
    2024-10-15         박상희     DelYn컬럼추가로 조회시 조건에 DelYn=N 추가
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    action = gparam.get('action')

    try:
        if action == 'read':
            sch_keyword = gparam.get('sch_keyword')
    
            sql = '''
                select h.id as h_id
                    , h.`Date` as holiday_date
                    , h.UseYn as use_yn
                    , h.FixedYn as fixed_yn
                    , h.Remark as remark
                    from holiday h 
                    where 1=1
                    and h.DelYn = 'N'
            '''
           
            if sch_keyword:
                sql += '''
                    and h.Remark like concat('%%', %(sch_keyword)s, '%%')
                '''
            sql += '''
                order by h.`Date` ;
            '''
    
            dc = {}
            dc['sch_keyword'] = sch_keyword
    
            result = DbUtil.get_rows(sql, dc)
            

        elif action =='save':
            id = posparam.get('h_id')
            holiday_date = posparam.get('holiday_date')
            use_yn = posparam.get('use_yn')
            fixed_yn = posparam.get('fixed_yn')
            remark = posparam.get('remark')

            if id:
                holiday = Holiday.objects.filter(id=id).first()
            else:
                holiday = Holiday()

            # transaction
            with transaction.atomic():
                holiday.Date = holiday_date
                holiday.Remark = remark
                holiday.UseYn = use_yn
                holiday.FixedYn = fixed_yn
                holiday.set_audit(request.user)
                holiday.save()

            result = {'success':True}

        elif action == 'delete':
            h_id = posparam.get('h_id')
            h = Holiday.objects.filter(id=h_id).first()
            h.DelYn = 'Y'
            h.save()
            result = {'success':True}
            
    except Exception as ex:
        source = '/api/definition/holiday, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}

    return result