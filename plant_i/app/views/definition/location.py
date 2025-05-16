import json

from django.db import transaction
from domain.models.cmms import CmLocation
from domain.models.definition import Location
from domain.services.definition.equipment import EquipmentService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse

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
            up_loc_pk = posparam.get('upperLocation')

            # 빈 문자열이거나 공백만 있는 경우 None으로 변경
            if up_loc_pk is None or up_loc_pk.strip() == "":
                up_loc_pk = None
            else:
                up_loc_pk = int(up_loc_pk)  # 숫자로 변환


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
            location.up_loc_pk = up_loc_pk
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

        elif action == 'loc_tree':
            def build_tree(nodes, parent_id=None):
                tree = []
                for node in nodes:
                    if node["up_loc_pk"] == parent_id:  # ✅ 상위 위치(부모 ID) 비교
                        children = build_tree(nodes, node["id"])  # ✅ 재귀 호출로 하위 노드 검색
                        tree.append({
                            "id": node["id"],       # ✅ 위치 PK
                            "text": node["loc_nm"], # ✅ 위치 이름 (DropDownTree에서 표시)
                            "items": children if children else []  # ✅ 하위 항목 없으면 빈 배열 반환
                        })
                return tree

            try:
                # DB에서 부서 정보 조회
                locations = Location.objects.values('id', 'loc_nm', 'up_loc_pk')
                print("📌 설비위치 데이터 확인:", list(locations))  # 🚀 로그 추가

                # 트리 구조 변환
                loc_tree = build_tree(list(locations))

                # ✅ `{ "items": [...] }` 형식으로 반환
                result = {"items": loc_tree}

            except Exception as e:
                print("🚨 서버 오류 발생:", str(e))  # 🚀 콘솔에 오류 로그 출력
                result = {"error": str(e)}

        elif action == 'cm_loc_tree':
            def build_tree(nodes, parent_id=None):
                tree = []
                for node in nodes:
                    if node["UpLocPk"] == parent_id:  # ✅ 상위 위치(부모 ID) 비교
                        children = build_tree(nodes, node["LocPk"])  # ✅ 재귀 호출로 하위 노드 검색
                        tree.append({
                            "id": node["LocPk"],       # ✅ 위치 PK
                            "text": node["LocName"], # ✅ 위치 이름 (DropDownTree에서 표시)
                            "items": children if children else []  # ✅ 하위 항목 없으면 빈 배열 반환
                        })
                return tree

            try:
                # DB에서 부서 정보 조회
                locations = CmLocation.objects.values('LocPk', 'LocName', 'UpLocPk')         

                # 트리 구조 변환
                loc_tree = build_tree(list(locations))

                # ✅ `{ "items": [...] }` 형식으로 반환
                result = {"items": loc_tree}

            except Exception as e:
                print("🚨 서버 오류 발생:", str(e))  # 🚀 콘솔에 오류 로그 출력
                result = {"error": str(e)}

        else:
            result = {'error': 'Invalid action'}

    except Exception as ex:
        source = '/api/definition/location, action:{}'.format(action)
        LogWriter.add_dblog('error', source, ex)
        result = {'success':False}
        
    return result

