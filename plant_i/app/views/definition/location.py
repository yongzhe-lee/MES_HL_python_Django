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

    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')    
    request = context.request
    user = request.user

    location_service = EquipmentService()

    if action=='read':
        items = location_service.get_location_list()

    elif action=='save':
        try:
            id = posparam.get('id')  # id 값 가져오기
            
            # 입력 데이터 가져오기
            location_code = posparam.get('locationCode')
            location_name = posparam.get('locationName')
            upper_location = posparam.get('upperLocation')
            plant_yn = posparam.get('plantYn')
            building_yn = posparam.get('buildingYn')
            spshop_yn = posparam.get('spshopYn')

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
            location.plant_yn = plant_yn
            location.building_yn = building_yn
            location.spshop_yn = spshop_yn

            # 감사 정보 설정
            location.set_audit(user)
            location.save()

            return {'success': True, 'message': '저장되었습니다.', 'id': location.id}

        except Exception as e:
            return {'success': False, 'message': str(e)}