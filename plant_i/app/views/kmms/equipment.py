from django.db import transaction
from app.views.kmms import equip_spec
from domain.models.cmms import CmEquipCategory, CmEquipClassify, CmEquipDeptHist, CmEquipLocHist, CmEquipment, CmImportRank, CmLocation, CmMaterial, CmSupplier
from domain.models.user import Depart
from domain.services.sql import DbUtil
from domain.services.kmms.equipment import EquipmentService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from domain.services.common import CommonUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import os

#urls.py를 따로 건드리지 않고 기존 API 라우팅 구조 내에서 처리
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

def handle_equipment_specs(equipment_id, posparam, request):
    """
    설비 사양 데이터를 처리하는 메소드
    Args:
        equipment_id: 설비 ID
        posparam: POST 파라미터
        request: HTTP 요청 객체
    """
    from app.views.kmms.equip_spec import equip_spec

    # 기존 사양 데이터 전체 삭제
    delete_context = type('Context', (), {})()
    delete_context.gparam = {'action': 'delete'}
    delete_context.posparam = {'equipPk': equipment_id}
    delete_context.request = request
    equip_spec(delete_context)

    # form-urlencoded 방식 specList 파싱 함수
    def parse_spec_list(posparam):
        spec_list = []
        idx = 0
        while True:
            key_prefix = f'specList[{idx}]'
            specnm = posparam.get(f'{key_prefix}[specnm]')
            unit = posparam.get(f'{key_prefix}[unit]')
            spec = posparam.get(f'{key_prefix}[spec]')
            if specnm is None:
                break
            spec_list.append({
                'specnm': specnm,
                'unit': unit,
                'spec': spec
            })
            idx += 1
        return spec_list

    # 새 사양 데이터 insert
    spec_list = parse_spec_list(posparam)
    for spec in spec_list:
        insert_context = type('Context', (), {})()
        insert_context.gparam = {'action': 'insert'}
        insert_context.posparam = {
            'equipPk': equipment_id,
            'equipSpecNm': spec.get('specnm'),
            'equipSpecUnit': spec.get('unit'),
            'equipSpecValue': spec.get('spec')
        }
        insert_context.request = request
        equip_spec(insert_context)

def handle_equip_part_mtrl(equipment_id, posparam, request):
    """
    설비 자재 데이터를 처리하는 메소드
    Args:
        equipment_id: 설비 ID
        posparam: POST 파라미터
        request: HTTP 요청 객체
    """
    from app.views.kmms.equip_part_mtrl import equip_part_mtrl

    # 기존 데이터 전체 삭제
    delete_context = type('Context', (), {})()
    delete_context.gparam = {'action': 'delete'}
    delete_context.posparam = {'equipPk': equipment_id}
    delete_context.request = request
    equip_part_mtrl(delete_context)

    # form-urlencoded 방식 partList 파싱 함수
    def parse_part_mtrl_list(posparam):
        part_mtrl_list = []
        idx = 0
        while True:
            key_prefix = f'partsList[{idx}]'
            mtrlPk = posparam.get(f'{key_prefix}[_mtrl_pk]')
            amt = posparam.get(f'{key_prefix}[_safety_stock_amt]')
            if mtrlPk is None:
                break
            part_mtrl_list.append({
                'mtrlPk': mtrlPk,           
                'amt': amt,
            })
            idx += 1
        return part_mtrl_list

    # 새 사양 데이터 insert
    part_mtrl_list = parse_part_mtrl_list(posparam)
    for part_mtrl in part_mtrl_list:
        insert_context = type('Context', (), {})()
        insert_context.gparam = {'action': 'insert'}
        insert_context.posparam = {
            'equipPk': equipment_id,
            'mtrlPk': part_mtrl.get('mtrlPk'),
            'amt': part_mtrl.get('amt')
        }
        insert_context.request = request
        equip_part_mtrl(insert_context)

def equipment(context):
    '''
    /api/kmms/equipment
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user
    factory_id = 1

    equipmentService = EquipmentService()

    # ✅ 첨부파일 모달을 HTML 문자열로 응답
    if action == 'load_modal':
        try:
            data_pk = gparam.get('equip_pk')            

            if data_pk == None:
                data = ''
            else:
                data = equipmentService.get_equipment_findOne(data_pk)

            print("=== 모달 로딩 시작 ===")
            template_path = 'components/equipment.html'
            context = {
                'request': request,
                'equipment': data  # ✅ 여기 핵심!
            }
            html = render_to_string(template_path, context)
            return html  # HttpResponse 대신 html 문자열 직접 반환

        except Exception as e:
            import traceback
            error_msg = f"템플릿 렌더링 오류: {str(e)}"
            print(error_msg)
            print("상세 오류:\n", traceback.format_exc())
            return error_msg  # 오류 메시지 문자열 직접 반환

    elif action=='read': 
        keyword = gparam.get('keyword', None)
        equip_status = gparam.get('equip_status', None)
        loc_pk = gparam.get('loc_pk', None)
        equip_category_id = gparam.get('equip_category_id', None)
        equip_class_path = gparam.get('equip_class_path', None)
        supplier_pk = gparam.get('supplier_pk', None)
        use_yn = gparam.get('use_yn', None)
        environ_equip_yn = gparam.get('environ_equip_yn', None)

        items = equipmentService.searchEquipment(keyword, equip_status, loc_pk, equip_category_id, equip_class_path, supplier_pk, use_yn, environ_equip_yn)

    elif action=='findAll':
        keyword = gparam.get('keyword', None)
        depart_id = gparam.get('depart_id', None)
        items = equipmentService.get_equipment_findAll(keyword, depart_id)

    elif action=='selectAll':
        keyword = gparam.get('keyword', None)
        depart_id = gparam.get('depart_id', None)
        items = equipmentService.get_equipment_selectAll(keyword, depart_id)

    elif action=='findOne':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equipment_findOne(equip_pk)

    elif action=='getEquipPmList':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.getEquipPmList(equip_pk)

    elif action=='log':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equipment_log(equip_pk)    

    elif action in ['save', 'update']:
        id = CommonUtil.try_int(posparam.get('equip_pk'))
        equipCode = posparam.get('equipCode')
        equipName = posparam.get('equipName')
        equip_category_id = posparam.get('equip_category_id')
        locPK = posparam.get('loc_pk')
        deptPK = posparam.get('dept_pk')
        upEquipPk = posparam.get('up_equip_pk', None)        
        environEquipYn = posparam.get('environ_equip_yn', None)        
        equip_mtrl_pk = posparam.get('mtrl_pk') #순환설비자재
        import_rank_pk = posparam.get('import_rank_pk', None)        
        process_cd = posparam.get('process_cd')
        supplier = posparam.get('supplier_pk', None)
        system_cd = posparam.get('system_cd')        
        warranty_dt = posparam.get('warranty_dt')
        Description = posparam.get('equip_dsc')
        InstallDate = posparam.get('install_dt')
        Maker = posparam.get('maker_pk')
        Model = posparam.get('model_number')
        ProductionYear = posparam.get('make_dt')
        BuyCost = posparam.get('buy_cost')
        SerialNumber = posparam.get('serial_number')
        asset_nos = posparam.get('asset_nos')
        ccenterCd = posparam.get('ccenter_cd')
        EquipClassPath = posparam.get('EquipClassPath')
        EquipClassDesc = posparam.get('EquipClassDesc')

        c = None
        try:
            if id:
                c = CmEquipment.objects.filter(id=id).first()
                equipLocBef = c.CmLocation.LocName
                # 기존 부서명 가져오기
                try:
                    oldDept = Depart.objects.get(id=c.DeptPk)
                    equipDeptBef = oldDept.Name
                except Depart.DoesNotExist:
                    equipDeptBef = ""
            else:
                c = CmEquipment()
                c.EquipStatus = 'ES_OPER'
                c.UseYn = 'Y'
           
            c.EquipCode = equipCode
            c.EquipName = equipName
            # 설비 카테고리 처리
            c.CmEquipCategory = CmEquipCategory.objects.get(EquipCategoryCode=equip_category_id)
            c.SiteId = 1
        
            c.CmLocation = CmLocation.objects.get(LocPk=locPK)   ## 위치코드
            try:
                dept = Depart.objects.get(id=deptPK)
                c.DeptPk = dept.id ## 부서코드 - ID값만 저장
            except Depart.DoesNotExist:
                return {'success': False, 'message': '존재하지 않는 부서코드입니다.'}
            
            if equip_mtrl_pk:
                c.CmMaterial = CmMaterial.objects.get(id=equip_mtrl_pk) ## 자재대상설비 
            if upEquipPk:
                c.Parent = CmEquipment.objects.get(id=upEquipPk)   ## 상위설비PK
            if supplier:
                c.CmSupplier = CmSupplier.objects.get(id=supplier) ## 공급업체 
            if import_rank_pk:
                c.CmImportRank = CmImportRank.objects.get(id=import_rank_pk) ## 중요도등급         
        
            c.ProcessCode = process_cd        
            c.SystemCode = system_cd

            # 날짜 필드 처리
            def validate_date(date_str, field_name):
                if not date_str:
                    return None
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"'{field_name}'은(는) YYYY-MM-DD 형식이어야 합니다.")

            try:
                c.WarrantyDt = validate_date(warranty_dt, '보증일자')
                c.InstallDt = validate_date(InstallDate, '설치일자')
                c.MakeDt = validate_date(ProductionYear, '제조일자')
            except ValueError as e:
                return {'success': False, 'message': str(e)}

            c.EquipDsc = Description
        
            # 제조사 처리
            try:
                c.MakerPk = int(Maker) if Maker else None
            except ValueError:
                return {'success': False, 'message': '제조사 코드는 숫자만 입력 가능합니다.'}
            
            c.ModelNumber = Model
        
            # 구매비용 처리
            try:
                c.BuyCost = int(BuyCost) if BuyCost else None
            except ValueError:
                return {'success': False, 'message': '구매비용은 숫자만 입력 가능합니다.'}
            
            c.SerialNumber = SerialNumber
            c.AssetNos = asset_nos
            c.CcenterCode = ccenterCd
            c.EnvironEquipYn = environEquipYn

            c.DelYn = 'N'           

            c.EquipClassPath = EquipClassPath
            c.EquipClassDesc = EquipClassDesc

            c.set_audit(user)
            c.save()
            print("PK:", c.id)  # 저장 후 PK가 할당되는지 확인

            #이미 등록된 설비에서만
            if id:

                # 기존 설비위치가 변경 되었을 때
                locHist = CmEquipLocHist()
                locHist.CmEquipment = c
                locHist.EquipLocBefore = equipLocBef
                locHist.EquipLocAfter = c.CmLocation.LocName

                if locHist.EquipLocBefore != "" and locHist.EquipLocBefore != locHist.EquipLocAfter :
                    locHist.set_audit(user)
                    locHist.save()                

                # 기존 관리부서가 변경 되었을 때
                deptHist = CmEquipDeptHist()
                deptHist.CmEquipment = c
                deptHist.EquipDeptBefore = equipDeptBef
                deptHist.EquipDeptAfter = dept.Name

                if deptHist.EquipDeptBefore != "" and deptHist.EquipDeptBefore != deptHist.EquipDeptAfter:
                    deptHist.set_audit(user)
                    deptHist.save()

            if c.id:
                handle_equipment_specs(c.id, posparam, request)

                handle_equip_part_mtrl(c.id, posparam, request)

            return {'success': True, 'message': '설비마스터 정보가 저장되었습니다.', 'data': {'equip_pk': c.id}}
        except Exception as e:
            return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'}

    elif action in ['change']:
        id = CommonUtil.try_int(posparam.get('equip_pk'))
        EquipStatus = posparam.get('equipStatus');

        c = None
        try:
            if id:
                c = CmEquipment.objects.filter(id=id).first()
            else:
                return {'success': False, 'message': '설비상태 수정 중 오류가 발생했습니다'}
            c.EquipStatus = EquipStatus
            c.save()
            return {'success': True, 'message': '설비상태가 성공적으로 변경되었습니다.'}
        except Exception as e:
            return {'success': False, 'message': f'설비상태 수정 중 오류가 발생했습니다: {str(e)}'}

    elif action == 'set_not_use':
        id = CommonUtil.try_int(posparam.get('equip_pk'))

        c = None
        try:
            if id:
                c = CmEquipment.objects.filter(id=id).first()
            else:
                return {'success': False, 'message': '설비 정보를 찾을 수 없습니다.'}
            
            if not c:
                return {'success': False, 'message': '존재하지 않는 설비입니다.'}
            
            c.UseYn = 'N'
            c.set_audit(user)
            c.save()
            
            return {'success': True, 'message': '설비마스터가 사용안함으로 처리되었습니다.'}
        except Exception as e:
            return {'success': False, 'message': f'설비 사용안함 처리 중 오류가 발생했습니다: {str(e)}'}

    elif action == 'set_use':
        id = CommonUtil.try_int(posparam.get('equip_pk'))

        c = None
        try:
            if id:
                c = CmEquipment.objects.filter(id=id).first()
            else:
                return {'success': False, 'message': '설비 정보를 찾을 수 없습니다.'}
            
            if not c:
                return {'success': False, 'message': '존재하지 않는 설비입니다.'}
            
            c.UseYn = 'Y'
            c.set_audit(user)
            c.save()
            
            return {'success': True, 'message': '설비마스터가 사용으로 처리되었습니다.'}
        except Exception as e:
            return {'success': False, 'message': f'설비 사용 처리 중 오류가 발생했습니다: {str(e)}'}

    # 설비 위치 변경이력 조회
    elif action=='read_loc_hist':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equip_loc_hist(equip_pk)

    # 설비 관리부서 변경이력 조회
    elif action=='read_dept_hist':
        equip_pk = gparam.get('equip_pk', None)
        items = equipmentService.get_equip_dept_hist(equip_pk)

    # kmms - 설비정보 - 불용설비 조회
    elif action=='read_dispose':
        keyword = gparam.get('keyword', None)
        srchCat = gparam.get('srchCat', None)
        srch_dept = gparam.get('srchDept', None)
        start_date = gparam.get('sDate', None)
        end_date = gparam.get('eDate', None)

        items = equipmentService.get_equipment_disposed(keyword, srchCat, srch_dept, start_date, end_date)

    # kmms - 설비정보 - 설비별작업이력 조회
    elif action=='read_equip_workhist':
        keyword = gparam.get('keyword', None)
        manage_dept = gparam.get('manage_dept', None)
        loc_pk = gparam.get('loc_pk', None)
        start_dt = gparam.get('start_dt', None)
        end_dt = gparam.get('end_dt', None)
        maint_type_cd = gparam.get('maint_type_cd', None)
        equip_category_id = gparam.get('equip_category_id', None)
        equip_class_path = gparam.get('equip_class_path', None)
        work_dept = gparam.get('work_dept', None)
        srch_environ_equip_only = gparam.get('srch_environ_equip_only', None)

        items = equipmentService.get_equipment_workhistory(keyword, manage_dept, loc_pk, start_dt, end_dt, maint_type_cd, equip_category_id, equip_class_path, work_dept, srch_environ_equip_only)

    elif action=='pm_equip_disposed':
        equipPk = gparam.get('equipPk', None)
        items = equipmentService.pm_equip_disposed(equipPk)

        return items

    elif action=='equip_check_disposed':
        equipPk = gparam.get('equipPk', None)
        items = equipmentService.equip_check_disposed(equipPk)

    elif action=='equip_chk_sche_disposed':
        equipPk = gparam.get('equipPk', None)
        items = equipmentService.equip_chk_sche_disposed(equipPk)

    elif action=='equip_child_disposed':
        equipPk = gparam.get('equipPk', None)
        items = equipmentService.equip_child_disposed(equipPk)

    elif action=='equip_disabled_update':
        equip_pk = gparam.get('equipPk')
        chkMastPk = gparam.get('chkMastPk', [])
        chkSchePk = gparam.get('chkSchePk', [])
        pmPk = gparam.get('pmPk', [])
        workOrderPk = gparam.get('workOrderPk', [])
        workOrderApprovalPk = gparam.get('workOrderApprovalPk', [])
        equipListPk = gparam.get('equipListPk', []) 
        

        # WO가 삭제되지 않을경우
        # 1, 점검일정 삭제 로직 2, 점검일정pk로 해당 일정의 설비 갯수 확인 3, 설비점검결과 삭제, 4, 설비가 본인것만 있으면 설비점검일정을 삭제
     
        #  점검마스터 삭제 로직
        # // 점검마스터에 묶인 설비(점검별설비)가 1개 이상이면 점검별 설비만 삭제
		# 	// 아니면 점검마스터 사용여부 N으로 변경
  
        # PM WO 삭제 로직
        # 1, 작업내역이 없는경우 (고장부위, 외주업체, 작업자재, 작업인력)
        
        # PM 마스터 삭제로직
        
        # 자식 설비목록의 상위설비 항목 업데이트

        # items = equipmentService.equip_disabled_update(equipPk)

    elif action == 'cm_equip_classify_tree':
        def get_all_children(parent_codes, all_equip_classes):
            """재귀적으로 모든 하위 항목들을 찾아서 반환"""
            children = []
            for parent_code in parent_codes:
                for equip_class in all_equip_classes:
                    if equip_class["ParentCode"] == parent_code:
                        children.append(equip_class)
            
            if children:
                # 찾은 하위 항목들의 코드들을 수집
                child_codes = [child["EquipClassCode"] for child in children]
                # 재귀적으로 더 하위 항목들도 찾기
                grandchildren = get_all_children(child_codes, all_equip_classes)
                children.extend(grandchildren)
            
            return children

        def build_tree(nodes, parent_id=None, depth=0):
            tree = []
            # 2단계까지만 트리 구성 (depth 0: 최상위, depth 1: 하위)
            if depth >= 2:
                return []
                
            for node in nodes:
                if node["ParentCode"] == parent_id:
                    # 하위 항목들은 더 이상의 children을 가지지 않음
                    if depth == 1:
                        tree.append({
                            "id": node["EquipClassCode"],
                            "text": node["EquipClassDesc"],
                            "items": []  # 2단계 항목은 빈 items
                        })
                    else:
                        # 최상위 항목만 하위 항목을 가짐
                        children = build_tree(nodes, node["EquipClassCode"], depth + 1)
                        tree.append({
                            "id": node["EquipClassCode"],
                            "text": node["EquipClassDesc"],
                            "items": children
                        })
            return tree

        try:
            category = gparam.get('category', None)
            
            # 카테고리가 'all'인 경우 빈 트리 반환
            if category == '':
                items = {"items": []}
                return items
            
            # 전체 설비 분류 데이터 조회
            all_equip_classes = CmEquipClassify.objects.filter(UseYn='Y').values('EquipClassCode', 'EquipClassDesc', 'ParentCode', 'CategoryCode')
            
            # 필터링된 설비 분류 조회
            filtered_equip_classes = all_equip_classes.filter(CategoryCode=category) if category else all_equip_classes
            
            # 필터링된 항목들의 모든 하위 항목들도 포함
            filtered_codes = [item["EquipClassCode"] for item in filtered_equip_classes]
            all_children = get_all_children(filtered_codes, list(all_equip_classes))
            
            # 필터링된 항목들과 모든 하위 항목들을 합침
            final_equip_classes = list(filtered_equip_classes) + all_children
            
            # 중복 제거 (EquipClassCode + ParentCode 조합 기준)
            seen_combinations = set()
            unique_equip_classes = []
            for item in final_equip_classes:
                # EquipClassCode와 ParentCode를 조합한 키 생성
                combination_key = f"{item['EquipClassCode']}_{item['ParentCode']}"
                if combination_key not in seen_combinations:
                    seen_combinations.add(combination_key)
                    unique_equip_classes.append(item)

            equip_classify_tree = build_tree(unique_equip_classes)

            # ✅ `{ "items": [...] }` 형식으로 반환
            items = {"items": equip_classify_tree}

        except Exception as e:
            print("🚨 서버 오류 발생:", str(e))  # 🚀 콘솔에 오류 로그 출력
            items = {"error": str(e)}

    return items   
