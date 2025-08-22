from django.db import transaction
from domain.services.common import CommonUtil
from domain.services.kmms.mig import MigService
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.shortcuts import render
from domain.models.cmms import CmMigDept, CmMigUser, CmMigLoc, CmMigSupplier, CmMigBaseCode, CmMigMtrl, CmMigEquipClass, CmMigEquipType, CmMigEquip, CmMigEquipSpec, CmMigMtrlPhoto, CmMigEquipPhoto, CmMigEquipFile, CmMigPm, CmMigEquipChkMst, CmMigChkEquip, CmMigEquipChkMstItem, CmMigWo, CmMigWoFaultLoc, CmMigStorLocAddr, CmMigMtrlInout

import os
import uuid
from django.db import transaction
from django.http import JsonResponse
from domain.models.system import AttachFile
from configurations import settings
import pandas as pd

def mig(context):
    '''
    /api/kmms/mig
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action') or posparam.get('action') or 'read'
    request = context.request
    user = request.user

    mig_Service = MigService()

    if action=='read':
        Site = gparam.get('Site', None)  
        if not Site:
            return {'success': False, 'message': 'Site ID가 제공되지 않았습니다.'}

    elif action=='mig':
        try:
            Site = gparam.get('Site', None) or posparam.get('Site', None)
            if not Site:
                return {'success': False, 'message': 'Site ID가 제공되지 않았습니다.'}
            path = settings.MIG_UPLOAD_PATH
            if not os.path.exists(path):
                os.makedirs(path)

            migrationType = posparam.get('migrationType', None)

            with transaction.atomic():
                file = request.FILES.get('migFile')
                if not file:
                    return {'success': False, 'message': '파일이 업로드되지 않았습니다.'}
                file_name = file.name
                # path에 파일명이 포함되어 있으면 그대로 사용
                if path.endswith(file_name):
                    save_path = path
                else:
                    save_path = os.path.join(path, file_name)
                with open(save_path, mode='wb') as upload_file:
                    upload_file.write(file.read())

                # 엑셀 파일 읽기 (첫 행이 헤더)
                df = pd.read_excel(save_path)

                if migrationType == 'DEPT':
                    mig_Service.delete_dept(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigDept = CmMigDept(
                            ActionType=to_none(row.get('유형', None)),
                            DeptCd=to_none(row.get('부서코드', None)),
                            DeptNm=to_none(row.get('부서명', None)),
                            UpDeptCd=to_none(row.get('상위 부서코드', None)),
                            UpDeptNm=to_none(row.get('상위 부서명', None)),
                            BusinessYn=to_none(row.get('사업부 여부', None)),
                            TeamYn=to_none(row.get('팀 여부', None)),
                            TpmYn=to_none(row.get('정비부서 여부', None)),
                            CcCd=to_none(row.get('코스트센터', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigDept.set_audit(request.user)
                        cmMigDept.save()
                    items = mig_Service.migrate_dept(Site)
                elif migrationType == 'USER_INFO':
                    mig_Service.delete_user_info(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigUser = CmMigUser(
                            ActionType=to_none(row.get('유형', None)),
                            LoginId=to_none(row.get('사용자ID', None)),
                            UserNm=to_none(row.get('사용자명', None)),
                            UserPassword=to_none(row.get('비밀번호', None)),
                            DeptCd=to_none(row.get('부서코드', None)),
                            DeptNm=to_none(row.get('부서명', None)),
                            RoleCd=to_none(row.get('역할', None)),
                            UserMail=to_none(row.get('이메일 주소', None)),
                            UserPhone=to_none(row.get('휴대폰 번호', None)),
                            EmpNo=to_none(row.get('사원번호', None)),
                            JobPos=to_none(row.get('직위(직급)', None)),
                            AllowLogin=to_none(row.get('로그인여부', None)),
                            LeaderYn=to_none(row.get('부서장 여부', None)),
                            RetireYn=to_none(row.get('퇴사 여부', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigUser.set_audit(request.user)
                        cmMigUser.save()
                    items = mig_Service.migrate_user_info(Site)
                elif migrationType == 'LOCATION':
                    mig_Service.delete_location(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigLoc = CmMigLoc(
                            ActionType=to_none(row.get('유형', None)),
                            LocCd=to_none(row.get('위치코드', None)),
                            LocNm=to_none(row.get('위치명(설명)', None)),
                            UpLocCd=to_none(row.get('상위 위치코드', None)),
                            UpLocNm=to_none(row.get('상위 위치', None)),
                            PlantYn=to_none(row.get('공장 여부', None)),
                            BuildingYn=to_none(row.get('건물 여부', None)),
                            SpshopYn=to_none(row.get('자재창고 여부', None)),
                            Isa95class=to_none(row.get('ISA-95 분류', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None,
                            OutOrder=to_none(row.get('순서', None))
                        )
                        cmMigLoc.set_audit(request.user)
                        cmMigLoc.save()
                    items = mig_Service.migrate_location(Site)
                elif migrationType == 'SUPPLIER':
                    mig_Service.delete_supplier(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigSupplier = CmMigSupplier(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('사이트ID', '1')),
                            SupplierCd=to_none(row.get('업체코드', None)),
                            SupplierNm=to_none(row.get('업체(공급사/제조사)', None)),
                            CompType=to_none(row.get('업체구분(S/M/B)', None)),
                            CeoNm=to_none(row.get('대표자', None)),
                            Phone=to_none(row.get('회사 전화번호', None)),
                            EmailAddr=to_none(row.get('회사 전자메일', None)),
                            ChargerNm=to_none(row.get('담당자1', None)),
                            ChargerTel=to_none(row.get('담당자1 연락처', None)),
                            Charger2Nm=to_none(row.get('담당자2', None)),
                            Charger2Tel=to_none(row.get('담당자2 연락처', None)),
                            BusinessClassNm=to_none(row.get('업종명', None)),
                            Nation=to_none(row.get('국가명', None)),
                            Local=to_none(row.get('지역', None)),
                            Homepage=to_none(row.get('홈페이지 주소', None)),
                            Address1=to_none(row.get('주소', None)),
                            Address2=to_none(row.get('상세주소', None)),
                            UseYn=to_none(row.get('사용 여부', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigSupplier.set_audit(request.user)
                        cmMigSupplier.save()
                    items = mig_Service.migrate_supplier(Site)
                elif migrationType == 'BASE_CODE':
                    mig_Service.delete_base_code(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    
                    for _, row in df.iterrows():
                        cmMigBaseCode = CmMigBaseCode(
                            ActionType=to_none(row.get('유형', None)),
                            CodeGrpCd=to_none(row.get('코드그룹코드', None)),
                            CodeCd=to_none(row.get('코드', None)),
                            CodeNm=to_none(row.get('코드명', None)),
                            CodeDsc=to_none(row.get('코드설명', None)),
                            DispOrder=to_none(row.get('표시순서', None)),
                            UseYn=to_none(row.get('사용여부', None)),
                            GrpCd=to_none(row.get('그룹코드', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigBaseCode.set_audit(request.user)
                        cmMigBaseCode.save()
                    items = mig_Service.migrate_base_code(Site)
                elif migrationType == 'MATERIAL':
                    mig_Service.delete_material(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigMtrl = CmMigMtrl(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            MtrlCd=to_none(row.get('자재코드', None)),
                            MtrlNm=to_none(row.get('자재명(설명)', None)),
                            MtrlClsCd=to_none(row.get('자재종류 코드', None)),
                            MtrlClsNm=to_none(row.get('자재종류', None)),
                            AmtUnit=to_none(row.get('측정단위(uom)', None)),
                            SafetyStockAmt=to_none(row.get('안전재고량', None)),
                            UnitPrice=to_none(row.get('최근 단가', None)),
                            UnitPriceDt=to_none(row.get('최근 단가일자', None)),
                            MtrlDsc=to_none(row.get('자재사양', None)),
                            MakerCd=to_none(row.get('제조업체코드', None)),
                            MakerNm=to_none(row.get('제조업체', None)),
                            SupplierCd=to_none(row.get('공급업체코드', None)),
                            SupplierNm=to_none(row.get('공급업체', None)),
                            DeliveryDays=to_none(row.get('조달기간', None)),
                            DeliveryType=to_none(row.get('조달유형(D/M/Y)', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigMtrl.set_audit(request.user)
                        cmMigMtrl.save()
                    items = mig_Service.migrate_material(Site)
                elif migrationType == 'EQUIP_CLASS':
                    mig_Service.delete_equip_class(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquipClass = CmMigEquipClass(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            EquipCategoryId=to_none(row.get('카테고리ID', None)),
                            EquipCategoryDesc=to_none(row.get('설비 카테고리', None)),
                            EquipClassId=to_none(row.get('설비 종류ID', None)),
                            EquipClassDesc=to_none(row.get('설비 종류', None)),
                            UseYn=to_none(row.get('사용 여부', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipClass.set_audit(request.user)
                        cmMigEquipClass.save()
                    items = mig_Service.migrate_equip_class(Site)
                elif migrationType == 'EQUIP_TYPE':
                    mig_Service.delete_equip_type(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquipType = CmMigEquipType(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            EquipClassId=to_none(row.get('설비 종류ID', None)),
                            EquipClassDesc=to_none(row.get('설비 종류', None)),
                            HierarchyPath=to_none(row.get('계층 분류', None)),
                            EquipTypeId=to_none(row.get('설비 유형ID', None)),
                            EquipTypeDesc=to_none(row.get('설비 유형(Type)', None)),
                            UseYn=to_none(row.get('사용 여부', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipType.set_audit(request.user)
                        cmMigEquipType.save()
                    items = mig_Service.migrate_equip_type(Site)
                elif migrationType == 'EQUIPMENT':
                    mig_Service.delete_equipment(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquip = CmMigEquip(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명(설명)', None)),
                            EquipCategoryId=to_none(row.get('카테고리코드', None)),
                            EquipCategoryDesc=to_none(row.get('카테고리', None)),
                            LocCd=to_none(row.get('설비위치 코드', None)),
                            LocNm=to_none(row.get('설비위치', None)),
                            UpEquipCd=to_none(row.get('상위 설비코드', None)),
                            UpEquipNm=to_none(row.get('상위 설비명(설명)', None)),
                            AssetNos=to_none(row.get('자산번호', None)),
                            ImportRankCd=to_none(row.get('중요도', None)),
                            EquipStatus=to_none(row.get('설비상태', None)),
                            DisposedType=to_none(row.get('불용처리', None)),
                            DeptCd=to_none(row.get('관리부서 코드', None)),
                            DeptNm=to_none(row.get('관리부서', None)),
                            CcCd=to_none(row.get('코스트센터', None)),
                            InstallDt=to_none(row.get('설치일자', None)),
                            EquipTypeCd=to_none(row.get('설비유형 코드', None)),
                            EquipClass=to_none(row.get('설비종류', None)),
                            EquipTypeNm=to_none(row.get('설비유형', None)),
                            SupplierCd=to_none(row.get('공급업체 코드', None)),
                            SupplierNm=to_none(row.get('공급업체', None)),
                            BuyCost=to_none(row.get('구매비용', None)),
                            WarrantyDt=to_none(row.get('보증만료일', None)),
                            MakerCd=to_none(row.get('제조사 코드', None)),
                            MakerNm=to_none(row.get('제조사', None)),
                            ModelNumber=to_none(row.get('모델 번호', None)),
                            PartNo=to_none(row.get('Part No.', None)),
                            SerialNumber=to_none(row.get('Serial No.', None)),
                            MakeDt=to_none(row.get('제조일', None)),
                            MtrlCd=to_none(row.get('순환설비 자재', None)),
                            EnvironYn=to_none(row.get('환경설비 여부', None)),
                            Msg=to_none(row.get('비고', None)),
                            UserId=request.user.username,
                            InsertTs=None
                        )
                        cmMigEquip.set_audit(request.user)
                        cmMigEquip.save()
                    items = mig_Service.migrate_equipment(Site)
                elif migrationType == 'EQUIP_SPEC':
                    mig_Service.delete_equip_spec(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquipSpec = CmMigEquipSpec(
                            ActionType=to_none(row.get('유형', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명(장황)', None)),
                            SiteId=to_none(row.get('사이트', '1')),
                            EquipSpecNm1=to_none(row.get('사양명칭(1st)', None)),
                            EquipSpecUnit1=to_none(row.get('단위(1st)', None)),
                            EquipSpecValue1=to_none(row.get('값/설명(1st)', None)),
                            EquipSpecNm2=to_none(row.get('사양명칭(2nd)', None)),
                            EquipSpecUnit2=to_none(row.get('단위(2nd)', None)),
                            EquipSpecValue2=to_none(row.get('값/설명(2nd)', None)),
                            EquipSpecNm3=to_none(row.get('사양명칭(3rd)', None)),
                            EquipSpecUnit3=to_none(row.get('단위(3rd)', None)),
                            EquipSpecValue3=to_none(row.get('값/설명(3rd)', None)),
                            EquipSpecNm4=to_none(row.get('사양명칭(4th)', None)),
                            EquipSpecUnit4=to_none(row.get('단위(4th)', None)),
                            EquipSpecValue4=to_none(row.get('값/설명(4th)', None)),
                            EquipSpecNm5=to_none(row.get('사양명칭(5th)', None)),
                            EquipSpecUnit5=to_none(row.get('단위(5th)', None)),
                            EquipSpecValue5=to_none(row.get('값/설명(5th)', None)),
                            EquipSpecNm6=to_none(row.get('사양명칭(6th)', None)),
                            EquipSpecUnit6=to_none(row.get('단위(6th)', None)),
                            EquipSpecValue6=to_none(row.get('값/설명(6th)', None)),
                            EquipSpecNm7=to_none(row.get('사양명칭(7th)', None)),
                            EquipSpecUnit7=to_none(row.get('단위(7th)', None)),
                            EquipSpecValue7=to_none(row.get('값/설명(7th)', None)),
                            EquipSpecNm8=to_none(row.get('사양명칭(8th)', None)),
                            EquipSpecUnit8=to_none(row.get('단위(8th)', None)),
                            EquipSpecValue8=to_none(row.get('값/설명(8th)', None)),
                            EquipSpecNm9=to_none(row.get('사양명칭(9th)', None)),
                            EquipSpecUnit9=to_none(row.get('단위(9th)', None)),
                            EquipSpecValue9=to_none(row.get('값/설명(9th)', None)),
                            EquipSpecNm10=to_none(row.get('사양명칭(10th)', None)),
                            EquipSpecUnit10=to_none(row.get('단위(10th)', None)),
                            EquipSpecValue10=to_none(row.get('값/설명(10th)', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipSpec.set_audit(request.user)
                        cmMigEquipSpec.save()
                    items = mig_Service.migrate_equip_spec(Site)
                elif migrationType == 'MTRL_PHOTO':
                    mig_Service.delete_mtrl_photo(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    
                    def extract_file_extension(filename):
                        if isinstance(filename, str) and '.' in filename:
                            return filename.split('.')[-1].lower()
                        return None
                    for _, row in df.iterrows():
                        filename = row.get('자재사진 파일이름', None)
                        fileloc = row.get('자재사진 파일 위치(full path)', None)
                        FileExt = extract_file_extension(filename)
                        # 파일이 없으면 skip
                        if not (isinstance(fileloc, str) and os.path.exists(fileloc)):
                            continue
                        cmMigMtrlPhoto = CmMigMtrlPhoto(
                            ActionType=to_none(row.get('유형', None)),
                            MtrlCd=to_none(row.get('자재코드', None)),
                            MtrlNm=to_none(row.get('자재명(설명)', None)),
                            FileLoc=fileloc,
                            FileNm=filename,
                            FileOrgNm=filename,
                            FileExt=FileExt,
                            PhotoDesc=filename,
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigMtrlPhoto.set_audit(request.user)
                        cmMigMtrlPhoto.save()
                    items = mig_Service.migrate_mtrl_photo(Site)
                elif migrationType == 'EQUIP_PHOTO':
                    mig_Service.delete_equip_photo(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    def extract_file_extension(filename):
                        if isinstance(filename, str) and '.' in filename:
                            return filename.split('.')[-1].lower()
                        return None
                    for _, row in df.iterrows():
                        filename = row.get('설비사진 파일 이름', None)
                        fileloc = row.get('설비사진 파일 위치(full path)', None)
                        FileExt = extract_file_extension(filename)
                        # 파일이 없으면 skip
                        if not (isinstance(fileloc, str) and os.path.exists(fileloc)):
                            continue
                        cmMigEquipPhoto = CmMigEquipPhoto(
                            ActionType=to_none(row.get('유형', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명(설명)', None)),
                            FileLoc=fileloc,
                            FileNm=filename,
                            FileOrgNm=filename,
                            FileExt=FileExt,
                            PhotoDesc=filename,
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipPhoto.set_audit(request.user)
                        cmMigEquipPhoto.save()
                    items = mig_Service.migrate_equip_photo(Site)
                elif migrationType == 'EQUIP_FILE':
                    mig_Service.delete_equip_file(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    def extract_file_extension(filename):
                        if isinstance(filename, str) and '.' in filename:
                            return filename.split('.')[-1].lower()
                        return None
                    for _, row in df.iterrows():
                        fileloc = row.get('설비 기술문서 파일 위치(full path)', None)
                        filename = row.get('설비 기술문서 파일명', None)
                        if isinstance(fileloc, str) and isinstance(filename, str):
                            file_path = os.path.join(fileloc, filename)
                        else:
                            continue
                        FileExt = extract_file_extension(filename)
                        # 파일이 없으면 skip
                        if not os.path.exists(file_path):
                            continue
                        cmMigEquipFile = CmMigEquipFile(
                            ActionType=to_none(row.get('유형', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명(설명)', None)),
                            FileLoc=fileloc,
                            FileNm=filename,
                            FileOrgNm=filename,
                            FileExt=FileExt,
                            FileDesc=filename,
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipFile.set_audit(request.user)
                        cmMigEquipFile.save()
                    items = mig_Service.migrate_equip_file(Site)
                elif migrationType == 'PM':
                    mig_Service.delete_pm(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigPm = CmMigPm(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('사이트ID', '1')),
                            PmNo=to_none(row.get('PM번호', None)),
                            PmNm=to_none(row.get('PM명(설명)', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명', None)),
                            ImportRankCd=to_none(row.get('중요도(설비)', None)),
                            PmType=to_none(row.get('PM유형', None)),
                            PerNumber=to_none(row.get('주기(빈도)', None)),
                            CycleType=to_none(row.get('주기단위', None)),
                            SchedStartDt=to_none(row.get('주기시작일', None)),
                            DeptCd=to_none(row.get('PM 부서코드', None)),
                            DeptNm=to_none(row.get('PM 부서명', None)),
                            PmUserId=to_none(row.get('PM 담당자ID', None)),
                            PmUserNm=to_none(row.get('PM 담당자', None)),
                            WorkExpectHr=to_none(row.get('정비소요시간', None)),
                            WorkText=to_none(row.get('작업지침', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigPm.set_audit(request.user)
                        cmMigPm.save()
                    items = mig_Service.migrate_pm(Site)
                elif migrationType == 'EQUIPCHKMAST':
                    mig_Service.delete_equipchkmast(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquipChkMst = CmMigEquipChkMst(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('사이트ID', '1')),
                            ChkMastNo=to_none(row.get('점검번호', None)),
                            ChkMastNm=to_none(row.get('점검명(설명)', None)),
                            PerNumber=to_none(row.get('주기(빈도)', None)),
                            CycleType=to_none(row.get('주기단위', None)),
                            SchedStartDt=to_none(row.get('주기시작일', None)),
                            DeptCd=to_none(row.get('점검 부서코드', None)),
                            DeptNm=to_none(row.get('점검 부서명', None)),
                            ChkUserId=to_none(row.get('점검 담당자ID', None)),
                            ChkUserNm=to_none(row.get('점검 담당자', None)),
                            WorkText=to_none(row.get('작업지침', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipChkMst.set_audit(request.user)
                        cmMigEquipChkMst.save()
                    items = mig_Service.migrate_equipchkmast(Site)
                elif migrationType == 'CHKEQUIP':
                    mig_Service.delete_chkequip(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigChkEquip = CmMigChkEquip(
                            ActionType=to_none(row.get('유형', None)),
                            ChkMastNo=to_none(row.get('점검번호', None)),
                            ChkMastNm=to_none(row.get('점검명(설명)', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명', None)),
                            SiteId=to_none(row.get('사이트', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigChkEquip.set_audit(request.user)
                        cmMigChkEquip.save()
                    items = mig_Service.migrate_chkequip(Site)
                elif migrationType == 'EQUIPCHKITEM':
                    mig_Service.delete_equipchkitem(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquipChkMstItem = CmMigEquipChkMstItem(
                            ActionType=to_none(row.get('유형', None)),
                            ChkMastNo=to_none(row.get('점검번호', None)),
                            ChkMastNm=to_none(row.get('점검명(설명)', None)),
                            ItemIdx=to_none(row.get('순번', None)),
                            ChkItemNm=to_none(row.get('점검항목명', None)),
                            Lcl=to_none(row.get('LCL', None)),
                            Ucl=to_none(row.get('UCL', None)),
                            ChkItemUnit=to_none(row.get('단위', None)),
                            Method=to_none(row.get('점검방법', None)),
                            Guide=to_none(row.get('이상기준', None)),
                            SiteId=to_none(row.get('사이트', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipChkMstItem.set_audit(request.user)
                        cmMigEquipChkMstItem.save()
                    items = mig_Service.migrate_equipchkitem(Site)
                elif migrationType == 'WO':
                    mig_Service.delete_wo(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigWo = CmMigWo(
                            ActionType=to_none(row.get('유형', None)),
                            SiteId=to_none(row.get('SITEId', '1')),
                            TempWoNo=to_none(row.get('임시APK NO', None)),
                            WoType=to_none(row.get('작업 유형', None)),
                            MaintTypeCd=to_none(row.get('작업 보전유형', None)),
                            WoTitle=to_none(row.get('작업 제목', None)),
                            WoStatus=to_none(row.get('작업상태', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명(장황)', None)),
                            ReqDt=to_none(row.get('요청일자', None)),
                            ReqBsiDeptCd=to_none(row.get('요청사업부', None)),
                            ReqBsiDeptNm=to_none(row.get('요청사업부명', None)),
                            ReqDeptCd=to_none(row.get('요청부서', None)),
                            ReqDeptNm=to_none(row.get('요청부서명', None)),
                            ReqUserId=to_none(row.get('요청자ID', None)),
                            ReqUserNm=to_none(row.get('요청자명', None)),
                            ReqUserDeptNm=to_none(row.get('요청자부서명', None)),
                            ReqInfo=to_none(row.get('요청정보', None)),
                            WantDt=to_none(row.get('원로 희망일', None)),
                            BrokenDt=to_none(row.get('고장일시', None)),
                            BrokenHr=to_none(row.get('고장시간', None)),
                            ProblemCd=to_none(row.get('고장코드', None)),
                            CauseCd=to_none(row.get('조치', None)),
                            RemedyCd=to_none(row.get('계획기간', None)),
                            PlanStartDt=to_none(row.get('작업 시작일', None)),
                            PlanEndDt=to_none(row.get('작업 종료일', None)),
                            StartDt=to_none(row.get('WO 완료일', None)),
                            EndDt=to_none(row.get('작업 부서3', None)),
                            FinishDt=to_none(row.get('작업 담당자', None)),
                            DeptCd=to_none(row.get('작업 담당자', None)),
                            DeptNm=to_none(row.get('작업 담당자', None)),
                            ChargerId=to_none(row.get('작업 담당자', None)),
                            ChargerNm=to_none(row.get('작업 담당자', None)),
                            WorkDesc=to_none(row.get('작업비고', None)),
                            TotCost=to_none(row.get('총공수', None)),
                            MtrlCost=to_none(row.get('비용 자재비', None)),
                            LaborCost=to_none(row.get('인건비', None)),
                            OutsideCost=to_none(row.get('외주비', None)),
                            EtcCost=to_none(row.get('기타비용', None)),
                            WorkSrc=to_none(row.get('작업소싱', None)),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigWo.set_audit(request.user)
                        cmMigWo.save()
                    items = mig_Service.migrate_wo(Site)
                elif migrationType == 'WO_FAULT_LOC':
                    mig_Service.delete_wo_fault_loc(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigWoFaultLoc = CmMigWoFaultLoc(
                            ActionType=to_none(row.get('유형', None)),
                            TempWoNo=to_none(row.get('정비이력 임시APK', None)),
                            FaultLocCd=to_none(row.get('고장부위 코드', None)),
                            FaultLocNm=to_none(row.get('고장부위명', None)),
                            CauseCd=to_none(row.get('원인 코드', None)),
                            CauseNm=to_none(row.get('원인명', None)),
                            SiteId=to_none(row.get('SITE(plant)', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigWoFaultLoc.set_audit(request.user)
                        cmMigWoFaultLoc.save()
                    items = mig_Service.migrate_wo_fault_loc(Site)
                elif migrationType == 'STOR_LOC_ADDR':
                    mig_Service.delete_stor_loc_addr(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigStorLocAddr = CmMigStorLocAddr(
                            ActionType=to_none(row.get('유형', None)),
                            LocCd=to_none(row.get('위치코드', None)),
                            LocNm=to_none(row.get('위치명(Spare-Parts)', None)),
                            LocCellAddr=to_none(row.get('셀위치', None)),
                            RackNo=to_none(row.get('랙 번호(Rack)', None)),
                            LevelNo=to_none(row.get('단 번호(Level)', None)),
                            ColNo=to_none(row.get('칸 번호(Column)', None)),
                            SiteId=to_none(row.get('사이트아이디', '1')),
                        )
                        cmMigStorLocAddr.save()
                    mig_Service.migrate_stor_loc_addr(Site)
                elif migrationType == 'MTRLINOUT':
                    mig_Service.delete_mtrlinout(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigMtrlInout = CmMigMtrlInout(
                            ActionType=to_none(row.get('유형', None)),
                            MtrlCd=to_none(row.get('자재코드', None)),
                            MtrlNm=to_none(row.get('자재명(설명)', None)),
                            InoutLocCd=to_none(row.get('보관장소 위치코드', None)),
                            LocCellAddr=to_none(row.get('셀위치', None)),
                            OwnDeptCd=to_none(row.get('부서코드', None)),
                            OwnDeptNm=to_none(row.get('소유부서', None)),
                            InoutDiv=to_none(row.get('입출고 구분', None)),
                            InoutType=to_none(row.get('입고유형', None)),
                            InoutDt=to_none(row.get('입고일', None)),
                            AbGrade=to_none(row.get('A/B 등급', None)),
                            InoutQty=to_none(row.get('수량(현재고)', None)),
                            InoutUprice=to_none(row.get('구매 단가', None)),
                            SupplierCd=to_none(row.get('공급업체 코드', None)),
                            SupplierNm=to_none(row.get('공급업체', None)),
                            SiteId=to_none(row.get('SITE(Plant)', '1')),
                        )
                        cmMigMtrlInout.save()
                    mig_Service.migrate_mtrlinout(Site)
                elif migrationType == 'EQUIP_PART_MTRL':
                    mig_Service.delete_equip_part_mtrl(Site)
                    items = mig_Service.migrate_equip_part_mtrl(Site)
                elif migrationType == 'TECH_FILE':
                    mig_Service.delete_tech_file(Site)
                    def to_none(val):
                        if pd.isna(val) or val == '':
                            return None
                        return val
                    for _, row in df.iterrows():
                        cmMigEquipFile = CmMigEquipFile(
                            ActionType=to_none(row.get('유형', None)),
                            EquipCd=to_none(row.get('설비코드', None)),
                            EquipNm=to_none(row.get('설비명(설명)', None)),
                            FileLoc=to_none(row.get('설비 기술문서 파일 위치(full path)', None)),
                            FileNm=to_none(row.get('설비 기술문서 파일명', None)),
                            FileDesc=to_none(row.get('설명', None)),
                            SiteId=to_none(row.get('SITE ID', '1')),
                            UserId=request.user.username,
                            InsertTs=None,
                            Msg=None
                        )
                        cmMigEquipFile.set_audit(request.user)
                        cmMigEquipFile.save()
                    items = mig_Service.migrate_tech_file(Site)
                else:
                    items = mig_Service.migrate(Site)

        except Exception as e:
            return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'}
        
        return {'success': True, 'message': '정보가 저장되었습니다.'}

    return items
