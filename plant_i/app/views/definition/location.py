import json

from django.db import transaction
from domain.models.definition import Location
from domain.services.definition.equipment import EquipmentService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil

def location(context):
    '''
    /api/definition/location
    '''

    result = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    location_service = EquipmentService()

    try:
        if action=='read':       
            result = location_service.get_location_list()

        elif action=='save':
        
            id = posparam.get('id')  # id 값 가져오기
            
            # 입력 데이터 가져오기
            location_code = posparam.get('locationCode')
            location_name = posparam.get('locationName')
            upper_location = posparam.get('upperLocation')
            loc_status = posparam.get('locStatus')
            plant_yn = posparam.get('plantYn', 'N')
            building_yn = posparam.get('buildingYn', 'N')
            spshop_yn = posparam.get('spshopYn', 'N')

            # 중복 체크 (수정 시에는 자기 자신 제외)
            if id:
                code_exists = Location.objects.filter(loc_cd=location_code).exclude(id=id).exists()
                name_exists = Location.objects.filter(loc_nm=location_name).exclude(id=id).exists()
            else:
                code_exists = Location.objects.filter(loc_cd=location_code).exists()
                name_exists = Location.objects.filter(loc_nm=location_name).exists()

            if code_exists:
                return {'success': False, 'message': '중복된 위치코드가 존재합니다.'}

            if name_exists:
                return {'success': False, 'message': '중복된 위치명이 존재합니다.'}

            # 신규 또는 기존 데이터 가져오기
            if id:
                try:
                    location = Location.objects.get(id=id)
                except Location.DoesNotExist:
                    return {'success': False, 'message': '수정할 데이터가 존재하지 않습니다.'}
            else:
                location = Location()

            # 데이터 설정
            location.loc_cd = location_code
            location.loc_nm = location_name
            location.up_loc_pk = upper_location
            location.loc_status = loc_status
            location.plant_yn = 'Y' if plant_yn == 'Y' else 'N'
            location.building_yn = 'Y' if building_yn == 'Y' else 'N'
            location.spshop_yn = 'Y' if spshop_yn == 'Y' else 'N'

            # 감사 정보 설정
            location.set_audit(user)
            location.save()
            result = {'success' : True}

        elif action=='read_loc_hist':
            result = location_service.get_equip_loc_hist()

    except Exception as ex:
        source = '/api/definition/location, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result

