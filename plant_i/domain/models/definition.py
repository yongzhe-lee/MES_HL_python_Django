from pyexpat import model
from tabnanny import verbose
from django.db import models
from domain.services.date import DateUtil
from .system import space_check, Site, Factory, Unit
from .user import Depart

class Line(models.Model):
    id  = models.AutoField(primary_key=True, db_comment="기본키")
    Code = models.CharField('라인코드', max_length=50, unique=True, db_comment="라인의 고유 코드")  # 개별 고유 제약 적용
    Name = models.CharField('라인명', max_length=100, unique=True, null=True, db_comment="라인의 이름")  # 개별 고유 제약 적용
    Description = models.CharField('설명', max_length=500, null=True, db_comment="라인에 대한 설명")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'line'
        verbose_name = '라인'
        db_table_comment = '라인'

class Process(models.Model):
    id  = models.AutoField(primary_key=True, db_comment="기본키")
    Code = models.CharField('공정코드', max_length=50, unique=True, db_comment="공정의 고유 코드")  # 개별 고유 제약 적용
    Name = models.CharField('공정명', max_length=100, unique=True, null=True, db_comment="공정의 이름")  # 개별 고유 제약 적용
    ProcessType = models.CharField('공정유형', max_length=100, null=True, db_comment="공정의 유형")
    Description = models.CharField('설명', max_length=500, null=True, db_comment="공정에 대한 설명")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'process'
        verbose_name = '공정'
        db_table_comment = '공정'

class Shift(models.Model):
    id  = models.AutoField(primary_key=True, db_comment="기본키")
    Code = models.CharField('근무조코드', max_length=30, db_comment="근무조의 고유 코드")
    Name = models.CharField('근무조명', max_length=30, db_comment="근무조의 이름")
    StartTime = models.CharField('시작시간', max_length=5, null=True, db_comment="근무조 시작 시간 (hh24:mm)")
    EndTime = models.CharField('종료시간', max_length=5, null=True, db_comment="근무조 종료 시간 (hh24:mm)")
    Description = models.CharField('설명', max_length=500, null=True, db_comment="근무조에 대한 설명")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'shift'
        verbose_name = '근무조'
        db_table_comment = '근무조 정보'        

class Company(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본키")
    Name = models.CharField('업체명', max_length=75, db_comment="업체 이름")
    Code = models.CharField('업체코드', max_length=50, null=True, db_comment="업체의 고유 코드")
    Country = models.CharField('국가', max_length=50, null=True, db_comment="업체의 국가")
    Local = models.CharField('지역명', max_length=50, null=True, db_comment="업체의 지역")
    CompanyType = models.CharField('업체유형', max_length=30, null=True, db_comment="업체 유형")
    CEOName = models.CharField('대표이사', max_length=50, null=True, db_comment="대표이사 이름")
    Email = models.EmailField('이메일', null=True, db_comment="업체 이메일 주소")
    ZipCode = models.CharField('우편번호', max_length=50, null=True, db_comment="업체 우편번호")
    Address = models.CharField('주소', db_column='addr', max_length=1000, null=True, db_comment="업체 주소")
    TelNumber = models.CharField('전화번호', max_length=100, null=True, db_comment="업체 전화번호")
    FaxNumber = models.CharField('팩스번호', max_length=100, null=True, db_comment="업체 팩스번호")
    BusinessType = models.CharField('업태', max_length=50, null=True, db_comment="업체의 업태")
    BusinessItem = models.CharField('종목', max_length=50, null=True, db_comment="업체의 종목")
    Homepage = models.CharField('홈페이지', max_length=100, null=True, db_comment="업체 홈페이지 주소")
    Description = models.CharField('비고', max_length=500, null=True, db_comment="업체 관련 추가 설명")
    
    Manager = models.CharField('담당자1', max_length=50, null=True, db_comment="주 담당자")
    ManagerPhone = models.CharField('담당자1 전화번호', max_length=50, null=True, db_comment="주 담당자 전화번호")
    Manager2 = models.CharField('담당자2', max_length=50, null=True, db_comment="부 담당자")
    Manager2Phone = models.CharField('담당자2 전화번호', max_length=50, null=True, db_comment="부 담당자 전화번호")
    UseYn = models.CharField(max_length=1, default='Y', db_comment="사용 여부 (Y/N)")
    DelYn = models.CharField(max_length=1, default='N', db_comment="삭제 여부 (Y/N)")
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True, db_comment="연결된 사이트")
    UserText1 = models.CharField(max_length=200, blank=True, null=True, db_comment="사용자 정의 필드 1")
    UserText2 = models.CharField(max_length=200, blank=True, null=True, db_comment="사용자 정의 필드 2")
    UserText3 = models.CharField(max_length=200, blank=True, null=True, db_comment="사용자 정의 필드 3")
    UserText4 = models.CharField(max_length=200, blank=True, null=True, db_comment="사용자 정의 필드 4")
    UserText5 = models.CharField(max_length=200, blank=True, null=True, db_comment="사용자 정의 필드 5")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")
    _creater_nm = models.CharField('작성자명', max_length=10, null=True, db_comment="작성자 이름")
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True, db_comment="변경자 이름")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'company'
        verbose_name = '업체'
        db_table_comment = '업체 정보'
        unique_together = [
            ['Code', 'Site'],
        ]
        
class Cycle(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본키")
    Type = models.CharField(max_length=50, db_comment="주기 유형")
    Name = models.CharField(max_length=100, unique=True, db_comment="주기 이름")  # 개별 고유 제약 적용
    Code = models.CharField(max_length=400, blank=True, null=True, db_comment="주기 코드")
    StartDate = models.DateField(null=True, db_comment="시작 날짜")
    StartTime = models.CharField(max_length=20, blank=True, null=True, db_comment="시작 시간")
    Remark = models.CharField(max_length=500, blank=True, null=True, db_comment="비고")
    UseYn = models.CharField(max_length=1, default='Y', db_comment="사용 여부 (Y/N)")
    DelYn = models.CharField(max_length=1, default='N', db_comment="삭제 여부 (Y/N)")
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True, db_comment="사이트 ID (참조키)")
    HolidayYn = models.CharField(max_length=1, default='N', db_comment="휴일 여부 (Y/N)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'cycle'
        verbose_name = '주기'
        db_table_comment = '주기 테이블 (반복 일정 관리)'        
        
class DocumentFolder(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본키")
    Name = models.CharField(max_length=100, db_comment="문서 폴더 이름")
    Code = models.CharField(max_length=50, blank=True, null=True, db_comment="문서 폴더 코드")
    UpDocFold_id = models.IntegerField(blank=True, null=True, db_comment="상위 문서 폴더 ID (계층 구조)")
    DispOrder = models.IntegerField(blank=True, null=True, db_comment="표시 순서")
    UseYn = models.CharField(max_length=1, default='Y', db_comment="사용 여부 (Y/N)")
    DelYn = models.CharField(max_length=1, default='N', db_comment="삭제 여부 (Y/N)")
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True, db_comment="사이트 ID (참조키)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'doc_fold'
        verbose_name = '문서폴더'
        db_table_comment = '문서 폴더 테이블 (문서 관리 구조)'
        
class Document(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본키")
    DocumentFolder = models.ForeignKey(DocumentFolder, on_delete=models.PROTECT, db_comment="문서 폴더 ID (참조키)")
    Code = models.CharField(max_length=100, db_comment="문서 코드")
    Title = models.CharField(max_length=300, null=True, db_comment="문서 제목")
    Content = models.CharField(max_length=4000, null=True, db_comment="문서 내용")
    Version = models.IntegerField(db_comment="문서 버전")
    DelYn = models.CharField(max_length=1, default='N', db_comment="삭제 여부 (Y/N)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'doc'
        verbose_name = '문서'
        db_table_comment = '문서 테이블 (문서 정보 관리)'
        
class Holiday(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본키")
    nation_cd = models.CharField('국가코드', max_length=10, db_comment="국가 코드")  # 추가 필드
    name_val = models.CharField('사용자정의휴일명', max_length=100, db_comment="사용자 정의 휴일명")
    repeat_yn = models.CharField('매년반복여부', max_length=1, default='N', blank=False, null=False, db_comment="매년 반복 여부 (Y/N)")
    holidate = models.CharField('사용자정의휴일일자', max_length=10, db_comment="사용자 정의 휴일 날짜 (YYYY-MM-DD)")

    class Meta:
        db_table = 'holiday'
        db_table_comment = '사용자 정의 휴일 테이블'
        
class CustCol(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본키")
    TableName = models.CharField(max_length=50, null=True, db_comment="대상 테이블 이름")
    Name = models.CharField(max_length=50, null=True, db_comment="사용자 정의 컬럼명")
    DataType = models.CharField(max_length=50, null=True, db_comment="데이터 타입")
    DataFormat = models.CharField(max_length=50, null=True, db_comment="데이터 포맷")
    CodeGrpName = models.CharField(max_length=1, null=True, db_comment="코드 그룹명")
    UseYn = models.CharField(max_length=1, default='Y', db_comment="사용 여부 (Y/N)")
    RequiredYn = models.CharField(max_length=1, default='N', db_comment="필수 여부 (Y/N)")
    DispOrder = models.IntegerField(blank=True, null=True, db_comment="표시 순서")
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True, db_comment="사이트 ID (참조키)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'cust_col'
        verbose_name = '사용자 정의 컬럼'
        db_table_comment = '사용자 정의 컬럼 관리 테이블'

class CodeGroup(models.Model):
    id = models.AutoField('코드그룹번호', primary_key=True, db_comment="코드 그룹 번호 (기본키)")
    Code = models.CharField('코드그룹코드', max_length=50, blank=False, null=False, db_comment="코드 그룹 코드")
    Name = models.CharField('코드그룹명', max_length=100, blank=True, null=True, db_comment="코드 그룹 이름")
    SystemYn = models.CharField('시스템여부', max_length=1, blank=False, null=False, db_comment="시스템 여부 (Y/N)")
    Remark = models.CharField('비고', max_length=500, blank=True, null=True, db_comment="비고")
    UseYn = models.CharField('사용여부', max_length=1, default='Y', blank=False, null=False, db_comment="사용 여부 (Y/N)")
    DelYn = models.CharField('삭제여부', max_length=1, default='N', blank=True, null=True, db_comment="삭제 여부 (Y/N)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'code_group'
        verbose_name = '코드그룹'
        db_table_comment = '코드 그룹 관리 테이블'
        
class Code(models.Model):
    id = models.AutoField('코드번호', primary_key=True, db_comment="코드 번호 (기본키)")    
    CodeGroupCode = models.CharField('코드그룹코드', max_length=50, blank=True, null=True, db_comment="코드 그룹 코드")
    Code = models.CharField('코드', max_length=50, blank=False, null=False, db_comment="코드 값")
    Name = models.CharField('코드명', max_length=100, blank=False, null=False, db_comment="코드명")
    Attr1 = models.CharField('속성1', max_length=100, blank=True, null=True, db_comment="속성 1")
    Attr2 = models.CharField('속성2', max_length=100, blank=True, null=True, db_comment="속성 2")
    Attr3 = models.CharField('속성3', max_length=100, blank=True, null=True, db_comment="속성 3")
    Remark = models.CharField('비고', max_length=500, blank=True, null=True, db_comment="비고")
    DispOrder = models.IntegerField('표시순서', blank=True, null=True, db_comment="표시 순서")
    UseYn = models.CharField('사용여부', max_length=1, default='Y', blank=False, null=False, db_comment="사용 여부 (Y/N)")
    DelYn = models.CharField('삭제여부', max_length=1, default='N', blank=True, null=True, db_comment="삭제 여부 (Y/N)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'code'
        verbose_name = '코드'
        db_table_comment = '코드 관리 테이블'

class EquipmentGroup(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField('설비그룹코드', max_length=50, validators=[space_check], db_comment='설비그룹코드')
    Name = models.CharField('설비그룹명', max_length=100, default='None', db_comment='설비그룹이름')
    EquipmentType = models.CharField('설비유형', max_length=50, default='manufacturing', db_comment='설비유형')
    Description	= models.CharField('설명', max_length=500, null=True, db_comment='설비그룹설명')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터상태')
    _created    = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자ID')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'equ_grp'
        verbose_name = '설비그룹'
        db_table_comment = '설비그룹정보'
        unique_together = [
            ['Code'],
            ['Name'],
        ]

class Location(models.Model):
    '''
    설비위치
    '''
    id = models.AutoField(primary_key=True, db_comment='설비위치 PK')
    loc_cd = models.CharField('위치코드', max_length=30, validators=[space_check], db_comment='위치코드')
    loc_nm = models.CharField('위치명', max_length=100, default='None', db_comment='위치이름')
    up_loc_pk = models.IntegerField('상위위치', null=True, db_comment='상위위치PK')
    loc_status = models.CharField('상태', max_length=10, db_comment='위치상태')

    plant_yn = models.CharField('공장여부', max_length=1, null=True, db_comment='공장여부')
    building_yn = models.CharField('건물여부', max_length=1, null=True, db_comment='건물여부')
    spshop_yn = models.CharField('보전자재창고여부', max_length=1, null=True, db_comment='보전자재창고여부')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자ID')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'location'
        verbose_name = '설비위치'
        db_table_comment = '설비위치정보'
        unique_together = [
            ['loc_cd'],
            ['loc_nm'],
        ]

class Equipment(models.Model):
    '''
    설비 정보
    '''
    id = models.AutoField(primary_key=True, db_comment='설비 PK')
    Code = models.CharField('설비코드', max_length=50, validators=[space_check], db_comment='설비코드')
    Line = models.ForeignKey(Line, db_column='line_id', on_delete=models.DO_NOTHING, null=True, db_comment='라인ID')
    MESCode = models.CharField('MES설비코드', max_length=50, null=True, db_comment='MES설비코드')
    SAPCode = models.CharField('SAP설비코드', max_length=50, null=True, db_comment='SAP설비코드')
    Name = models.CharField('설비명', max_length=100, db_comment='설비이름')
    EquipmentGroup = models.ForeignKey(EquipmentGroup, on_delete=models.DO_NOTHING, null=True, db_comment='설비그룹ID')
    Description = models.CharField('설명', max_length=500, null=True, db_comment='설비설명')
    Maker = models.CharField('제조사', max_length=50, null=True, db_comment='제조사')
    Model = models.CharField('모델', max_length=50, null=True, db_comment='모델명')
    Standard = models.CharField('규격', max_length=50, null=True, db_comment='설비규격')
    Usage = models.CharField('용도', max_length=50, null=True, db_comment='설비용도')
    ManageNumber = models.CharField('관리번호', max_length=50, null=True, db_comment='관리번호')
    SerialNumber = models.CharField('시리얼넘버', max_length=50, null=True, db_comment='시리얼번호')
    Depart = models.ForeignKey(Depart, null=True, on_delete=models.DO_NOTHING, db_comment='부서ID')

    ProductionYear = models.SmallIntegerField('제작연도', null=True, db_comment='제작연도')
    AssetYN = models.CharField('자산성여부', max_length=1, null=True, db_comment='자산성여부')
    DurableYears = models.SmallIntegerField('내용연수', null=True, db_comment='내용연수')
    PowerWatt = models.FloatField('소비전력(W)', null=True, db_comment='소비전력(W)')
    Voltage = models.CharField('사용전압', null=True, max_length=50, db_comment='사용전압')
    Manager = models.CharField('관리책임자', max_length=100, null=True, db_comment='관리책임자')
    SupplierName = models.CharField('공급업체', max_length=50, null=True, db_comment='공급업체')
    PurchaseDate = models.DateField('구매일', null=True, db_comment='구매일')
    PurchaseCost = models.FloatField('구매가', null=True, db_comment='구매가')
    ServiceCharger = models.CharField('서비스담당자', max_length=100, null=True, db_comment='서비스담당자')
    ASTelNumber = models.CharField('AS전화번호', null=True, max_length=50, db_comment='AS전화번호')
    AttentionRemark = models.CharField('주의사항', null=True, max_length=2000, db_comment='주의사항')
    Inputdate = models.CharField('입고일', null=True, max_length=12, db_comment='입고일')
    InstallDate = models.DateField('설치일', null=True, db_comment='설치일')
    DisposalDate = models.DateField('폐기일', null=True, db_comment='폐기일')
    DisposalReason = models.CharField('폐기사유', max_length=100, null=True, db_comment='폐기사유')
    disposed_type = models.CharField('불용처리타입', max_length=10, null=True, db_comment='불용처리타입')
    OperationRateYN = models.CharField('가동률표시YN', max_length=1, null=True, db_comment='가동률표시YN')
    Status = models.CharField('설비상태', max_length=10, null=True, default='normal', db_comment='설비상태')
    loc_pk = models.SmallIntegerField('위치PK', null=True, db_comment='위치PK')
    equip_category_id = models.CharField('설비분류', max_length=2, null=True, db_comment='설비분류')
    up_equip_pk = models.IntegerField('상위설비PK', null=True, db_comment='상위설비PK')
    site_id = models.IntegerField('사이트ID', null=True, db_comment='사이트ID')
    equip_class_path = models.CharField('설비계층경로', max_length=100, null=True, db_comment='설비계층경로')
    equip_class_desc = models.CharField('설비계층설명', max_length=100, null=True, db_comment='설비계층설명')
    asset_nos = models.CharField('자산번호', max_length=100, null=True, db_comment='자산번호')
    warranty_dt = models.DateField('보증기간', null=True, db_comment='보증기간')
    buy_cost = models.FloatField('구매가격', null=True, db_comment='구매가격')
    photo_file_grp_cd = models.CharField('사진파일그룹코드', max_length=50, null=True, db_comment='사진파일그룹코드')
    doc_file_grp_cd = models.CharField('문서파일그룹코드', max_length=50, null=True, db_comment='문서파일그룹코드')
    import_rank = models.CharField('중요도등급', null=True, db_comment='중요도등급')
    environ_equip_yn = models.CharField('환경설비여부', max_length=1, null=True, db_comment='환경설비여부')
    ccenter_cd = models.CharField('코스트센터코드', max_length=50, null=True, db_comment='코스트센터코드')
    breakdown_dt = models.DateField('고장일', null=True, db_comment='고장일')
    del_yn = models.CharField('삭제여부', max_length=1, default='N', db_comment='삭제여부')
    process_cd = models.CharField('공정코드', max_length=50, null=True, db_comment='공정코드')
    system_cd = models.CharField('시스템코드', max_length=50, null=True, db_comment='시스템코드')
    first_asset_status = models.CharField('최초자산상태', max_length=10, null=True, db_comment='최초자산상태')
    disposed_type = models.CharField('폐기유형', max_length=10, null=True, db_comment='폐기유형')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자ID')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'equ'
        verbose_name = '설비'
        verbose_name_plural = 'Equipments'
        default_related_name = 'Equipments'
        db_table_comment = '설비정보'
        unique_together = [
            ['Code'],
            ['Name'],
        ]

class EquipLocHist(models.Model):
    '''
    설비 위치 이력
    '''
    equip_loc_hist_pk = models.AutoField(primary_key=True, db_comment='설비위치이력 PK')
    equip_pk = models.IntegerField('설비PK', db_comment='설비PK')
    equip_loc_bef = models.IntegerField('변경전 설비위치', db_comment='변경전 설비위치')
    equip_loc_aft = models.IntegerField('변경후 설비위치', db_comment='변경후 설비위치')

    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자ID')
    _creator_name = models.CharField('_creator_name', null=True, db_comment='생성자이름')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._created = DateUtil.get_current_datetime()
        self._creator_name = user.username
        return

    class Meta:
        db_table = 'equip_loc_hist'
        verbose_name = '설비위치이력'
        db_table_comment = '설비위치변경이력'
        unique_together = [
            ['equip_loc_hist_pk'],
        ]

class EquipDeptHist(models.Model):
    '''
    설비 부서 이력
    '''
    equip_dept_hist_pk = models.AutoField(primary_key=True, db_comment='설비부서이력 PK')
    equip_pk = models.IntegerField('설비PK', db_comment='설비PK')
    equip_dept_bef = models.IntegerField('변경전 관리부서', db_comment='변경전 관리부서')
    equip_dept_aft = models.IntegerField('변경후 관리부서', db_comment='변경후 관리부서')

    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자ID')
    _creator_name = models.CharField('_creator_name', null=True, db_comment='생성자이름')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._created = DateUtil.get_current_datetime()
        self._creator_name = user.username
        return

    class Meta:
        db_table = 'equip_dept_hist'
        verbose_name = '설비부서이력'
        verbose_name_plural = '설비부서이력들'
        db_table_comment = '설비부서변경이력'
        unique_together = [
            ['equip_dept_hist_pk'],
        ]

class EquipCategory(models.Model):
    '''
    설비 카테고리
    '''
    equip_category_id = models.CharField(max_length=2, primary_key=True, db_comment='설비카테고리ID')
    equip_category_desc = models.CharField(max_length=50, db_comment='설비카테고리설명')
    remark = models.CharField(max_length=100, null=True, blank=True, db_comment='비고')
    use_yn = models.CharField(max_length=1, default='Y', db_comment='사용여부')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자ID')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'equip_category'
        verbose_name = '설비카테고리'
        db_table_comment = '설비카테고리정보'

class DASServer(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField('서버코드', max_length=50, validators=[space_check])
    Name = models.CharField('서버명', max_length=100, default='None')
    IPAddress = models.CharField('IP주소', max_length=100, null=True)
    Type = models.CharField('타입', max_length=30, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'das_server'
        verbose_name = 'DAS서버'
        unique_together = [
            ['Code'],
            ['Name'],
        ]

class DASConfig(models.Model):
    id  = models.AutoField(primary_key=True)
    Name = models.CharField('설정명', max_length=100,  default='None')
    Description	= models.CharField('설명', max_length=500, null=True)
    Server = models.ForeignKey(DASServer,on_delete=models.PROTECT, null=True)
    Equipment = models.ForeignKey(Equipment,on_delete=models.PROTECT, null=True)
    Configuration = models.TextField('설정', null=True)
    #Configuration = JSONField('설정', null=True)
    Handler = models.CharField('Handler', max_length=100, null=True)
    Topic = models.CharField('토픽', max_length=100, null=True)
    DeviceType = models.CharField('수집방법', max_length=100, null=True, default='xgt')
    ConfigFileName = models.CharField('설정파일명', max_length=200, null=True)
    is_active = models.CharField('active', max_length=1, default='Y', null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'das_config'
        verbose_name = 'DAS설정'
        index_together = [
            ['Equipment'],
        ]

class DataSource(models.Model):
    '''
    소스아이디	id
    소스명	Name
    소스유형	SourceType
    대상IP	IPAddress
    대상포트	Port
    위치	Location
    비고	Description
    '''

    id = models.AutoField(primary_key=True)
    Name = models.CharField('데이터소스명', max_length=100, unique=True)
    SourceType = models.CharField('소스유형', max_length=100, null=True)
    IPAddress = models.CharField('대상IP', max_length=100, null=True)
    Port = models.IntegerField('대상포트', null=True)
    Location = models.CharField('위치', max_length=500, null=True)
    Description = models.CharField('비고', max_length=2000, null=True)
    Equipment = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'data_src'
        verbose_name = '데이터 소스'
        index_together = [
            ['SourceType'],
        ]

class TagGroup(models.Model):
    id  = models.AutoField(primary_key=True)
    Code = models.CharField('태그그룹코드', max_length=50)
    Name = models.CharField('태그그룹명', max_length=50)
    Description = models.CharField('설명', max_length=100, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'tag_grp'
        verbose_name = '태그그룹'
        unique_together  = [
            ['Code' ],
            ['Name' ],
        ]

class TagMaster(models.Model):
    tag_code = models.CharField('태그코드', primary_key=True, max_length=50)
    tag_name = models.CharField('태그명', max_length=100)
    tag_group = models.ForeignKey(TagGroup, on_delete=models.DO_NOTHING, null=True)
    Equipment = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, null=True)
    DASConfig = models.ForeignKey(DASConfig, on_delete=models.DO_NOTHING, null=True)
    RoundDigit = models.IntegerField('소숫점자릿수', default=3, null=True)
    Unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING, null=True)
    DataSource = models.ForeignKey(DataSource, db_column='data_src_id', on_delete=models.DO_NOTHING, null=True)
    DisplayFormat = models.CharField('화면표시포맷', max_length=200, null=True)
    LSL = models.FloatField('하한값', null=True )
    USL = models.FloatField('상한값', null=True )
    LastValue = models.CharField('최종값', max_length=50, null=True)
    LastDate = models.DateTimeField('최종데이터일시', null=True)
    LastStatus = models.CharField('가동상태', max_length=10, null=True)
    Address = models.CharField('리딩어드레스', max_length=50, null=True)
    VariableName = models.CharField('변수명', max_length=50, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'tag'
        verbose_name = '태그마스터'
        unique_together  = [
            ['tag_name' ],
        ]

class TagData(models.Model):
    id  = models.BigAutoField(primary_key=True)
    tag_code = models.CharField('태그코드', max_length=50) #릴레이션을 맺지 않는다
    data_date = models.DateTimeField('일시', default=None,  blank=False)
    data_value = models.FloatField('데이터값')
    data_char = models.CharField('문자데이터', max_length=2000, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)

    class Meta():
        db_table = 'tag_dat'
        verbose_name = '태그데이터'
        unique_together  = [
            ['tag_code', 'data_date']
        ]
        index_together = [ 
            ['data_date'],
            ['tag_code', 'data_value', 'data_date'],
            ['tag_code', 'data_date', 'data_value'],
        ]
    @classmethod
    def save_data(cls, tag_code, data_date, data_value):
        return cls.objects.create(tag_code=tag_code, data_date=data_date, data_value=data_value)

class ElecMeterData(models.Model):
    id  = models.BigAutoField(primary_key=True)
    tag_code = models.CharField('태그코드', max_length=50) #릴레이션을 맺지 않는다
    data_date = models.DateTimeField('일시', default=None,  blank=False)
    data_value = models.FloatField('데이터값')
    data_char = models.CharField('문자데이터', max_length=2000, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)

    class Meta():
        db_table = 'em_tag_dat'
        verbose_name = '전력량계태그데이터'
        unique_together  = [
            ['tag_code', 'data_date']
        ]
        index_together = [ 
            ['data_date'],
            ['tag_code', 'data_value', 'data_date'],
            ['tag_code', 'data_date', 'data_value'],
        ]
    @classmethod
    def save_data(cls, tag_code, data_date, data_value):
        return cls.objects.create(tag_code=tag_code, data_date=data_date, data_value=data_value)

class Material(models.Model):
    id  = models.AutoField(primary_key=True, db_comment="기본키")
    Factory = models.ForeignKey(Factory, on_delete=models.DO_NOTHING, db_comment="공장 ID (참조키)")
    Code = models.CharField('품목코드', max_length=50, validators=[space_check], unique=True, db_comment="품목 코드")  # 개별 고유 제약 적용
    Name = models.CharField('품목명', max_length=100, unique=True, db_comment="품목명")  # 개별 고유 제약 적용
    Standard = models.CharField('규격', max_length=1000, db_comment="품목 규격")
    ItemGroup = models.CharField('자재그룹', max_length=9, null=True, db_comment="자재 그룹")
    ItemType = models.CharField('품목유형', max_length=15, null=True, db_comment="품목 유형")
    BasicUnit = models.CharField('기본단위', max_length=3, null=True, db_comment="기본 단위")
    CycleTime = models.DecimalField('c/t', decimal_places=3, max_digits=10, null=True, db_comment="Cycle Time (생산 주기 시간)")
    in_price = models.DecimalField('입고금액', decimal_places=3, max_digits=10, null=True, db_comment="입고 금액")
    out_price = models.DecimalField('출고금액', decimal_places=3, max_digits=10, null=True, db_comment="출고 금액")
    supplier_pk = models.IntegerField('공급업체PK', null=True, db_comment="공급업체 ID (참조키)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'material'
        verbose_name = '품목정보'
        db_table_comment = '품목 정보 관리 테이블'

class EquipAlarm(models.Model):    
    alarm_code = models.CharField('알람코드', db_column='alarm_cd', max_length=50, primary_key=True, null=False, db_comment="알람 코드 (기본키)")
    Equipment = models.ForeignKey(Equipment, db_column='Equipment_id', on_delete=models.DO_NOTHING, db_comment="설비 ID (참조키)")    
    Name = models.CharField('알람명', db_column='alarm_nm', max_length=100, db_comment="알람명")
    AlarmNumber = models.CharField('알람식별번호', db_column='alarm_num', max_length=50, null=True, db_comment="알람 식별 번호")    
    Detail = models.TextField('알람상세', db_column='alarm_detail', null=True, db_comment="알람 상세 내용")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 정보")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'equ_alarm'
        verbose_name = '설비알람정보'
        db_table_comment = '설비 알람 정보 관리 테이블'
        indexes = [ 
            models.Index(fields=['Equipment'], name='idx_equipment')
        ]

class EquipAlarmHistory(models.Model):
    id  = models.BigAutoField(primary_key=True, db_comment="알람 이력 ID (기본키)")
    alarm_code = models.CharField('알람코드', db_column='alarm_cd', max_length=50, db_comment="알람 코드 (참조키)")
    details = models.TextField('알람발생상세내용', db_column='details', null=True, db_comment="알람 발생 상세 내용")
    data_date = models.DateTimeField('발생일시', db_comment="알람 발생 일시")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 일시")

    class Meta:
        db_table = 'equ_alarm_hist'
        verbose_name = '설비알람이력'
        db_table_comment = '설비 알람 이력 관리 테이블'
        indexes = [
            models.Index(fields=['alarm_code', 'data_date'], name='idx_alarm_code_date'),
            models.Index(fields=['data_date'], name='idx_data_date'),
        ]

'''
25.01.14 김하늘 BOM 관련 테이블 생성 보류(추후 SAP 데이터 조회만)
'''
# class BOM(models.Model):
#     id = models.AutoField(primary_key=True)
#     Name = models.CharField('제목', max_length=200, null=True)
#     Material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)
#     BOMType = models.CharField('BOM종류', max_length=20, default='manufacturing')
#     OutputAmount = models.FloatField('산출량',  default=1)
#     Version = models.CharField('버전', max_length=10, null=True, default='1')
#     StartDate = models.DateTimeField('적용시작일',null=True)
#     EndDate = models.DateTimeField('적용종료일', null=True, default='2100-12-31')

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'bom'
#         verbose_name = 'BOM헤더'
#         unique_together = [
#             ['Material','BOMType','StartDate'],
#             ['Material','BOMType','Version'],
#         ]
#         index_together = [
#             ['EndDate','StartDate'],
#         ]
#
#
# class BOMComponent(models.Model):
#     id = models.AutoField(primary_key=True)
#     BOM = models.ForeignKey(BOM, on_delete=models.CASCADE)
#     Material = models.ForeignKey(Material, on_delete=models.PROTECT)
#     _order   = models.SmallIntegerField('순서', default=0, null=True)
#     Amount = models.FloatField('소요량')
#     Description	= models.CharField('비고', max_length=500, null=True)
#     Portion = models.FloatField('배합비%', null=True)
#     DesignAmount = models.FloatField('설계소요량', null=True)
#     LossPro = models.FloatField('로스율%', null=True)
#     AutoConsuYN	= models.CharField('자동투입YN', max_length=1, null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'bom_comp'
#         verbose_name = 'BOM구성'
#         unique_together = [
#             ['BOM','Material'],
#         ]
#         index_together = [
#             ['Material'],
#         ]


# class BOMProcessComponent(models.Model):
#     id = models.AutoField(primary_key=True)
#     Product = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='ProducedBomProcess')
#     Process = models.ForeignKey(Process, on_delete=models.CASCADE)
#     Material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='ConsumedBomProcess')
#     Amount = models.FloatField('소요량', null=True)
#     BOM = models.ForeignKey(BOM, on_delete=models.DO_NOTHING, null=True)
#     # Routing = models.ForeignKey(Routing, on_delete=models.CASCADE, null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'bom_proc_comp'
#         verbose_name = 'BOM공정구성'
#         # unique_together = [
#         #     ['BOM', 'Process','Material', 'Routing'],
#         # ]
#         # index_together = [
#         #     ['Product', 'Process'],
#         #     ['Routing', 'BOM'], # routing field가 없어서 에러 발생하는 것
#         # ]