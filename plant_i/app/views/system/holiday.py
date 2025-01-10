from domain.services.logging import LogWriter
from domain.services.sql import DbUtil
from domain.services.common import CommonUtil
from domain.services.system import SystemService    # mes에서 가져온 것
from domain.models.system import HolidayOff
from django.db import IntegrityError

def holiday(context):
    '''
    /api/system/holiday
    '''    
    posparam = context.posparam
    gparam = context.gparam
    request = context.request
    user = request.user    
    action = gparam.get('action', 'read')
    systemService = SystemService()

    try:
        if action == 'read':            
            keyword = gparam.get('keyword')
            year = gparam.get('srch_year')
            result = systemService.get_holiday_list(keyword, year)

        elif action == 'save':
            # 데이터 저장 로직 수정
            holiday_id = posparam.get('id')  # id 값을 가져옵니다. 없으면 None.
            holiday = None

            if holiday_id:
                holiday = HolidayOff.objects.filter(id=holiday_id).first()
                if not holiday:
                    return {
                        'success': False,
                        'message': f"Record with id {holiday_id} does not exist."
                    }
            else:
                # 새 객체 생성
                holiday = HolidayOff()

            NationCd = posparam.get('nation_cd', 'ko')  # 기본값을 빈 문자열로 설정
            NameVal = posparam.get('name_val')
            Repeatyn = posparam.get('repeat_yn')
            Holidate = posparam.get('holidate')

            # 데이터 유효성 검사
            if Repeatyn not in ['Y', 'N']:
                raise ValueError("Invalid value for 'repeat_yn'. Must be 'Y' or 'N'.")
            if len(Holidate) > 10:
                raise ValueError("Invalid value for 'holidate'. Maximum length is 10.")
            if not NameVal or len(NameVal) > 100:
                raise ValueError("Invalid value for 'name_val'. Maximum length is 100.")
            if not NationCd or len(NationCd) > 10:
                raise ValueError("Invalid value for 'nation_cd'. Maximum length is 10.")

            # 중복 데이터 확인
            if holiday_id is None:
                if HolidayOff.objects.filter(nation_cd=NationCd, holidate=Holidate, name_val=NameVal).exists():
                    return {
                        'success': False,
                        'message': 'Duplicate entry: A record with the same nation_cd, holidate, and name_val already exists.'
                    }


            # 데이터 저장
            holiday.nation_cd = NationCd
            holiday.name_val = NameVal
            holiday.repeat_yn = Repeatyn
            holiday.holidate = Holidate
            holiday.save()
            holiday.save()
            result = {'success': True}

        elif action == 'delete':
            holiday_id = posparam.get('id')  # 삭제할 id 값

            if not holiday_id:
                return {'success': False, 'message': '삭제할 데이터의 ID가 전달되지 않았습니다.'}

            # 데이터 삭제
            try:
                holiday = HolidayOff.objects.filter(id=holiday_id).first()
                if holiday:
                    holiday.delete()
                    result = {'success': True, 'message': '삭제되었습니다.'}
                else:
                    result = {'success': False, 'message': f'ID {holiday_id}에 해당하는 데이터가 없습니다.'}
            except Exception as ex:
                LogWriter.add_dblog('error', 'holiday delete', ex)
                result = {'success': False, 'message': str(ex)}



    except Exception as ex:
        source = f'holiday : action-{action}'
        LogWriter.add_dblog('error', source, ex)

        result = {
            'success': False,
            'message': str(ex)
        }
        
    return result
