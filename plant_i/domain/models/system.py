from model_utils import Choices

from django.db import models
from django.contrib.auth.models import User
from domain.services.date import DateUtil

from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy
from django.utils import timezone  # timezone 모듈 추가


# ELEMENT_LEVEL_CHOICES = Choices(
#     ('enterprise',          ugettext_lazy('Enterprise')),
#     ('site',                ugettext_lazy('Site')),
#     ('area',                ugettext_lazy('Area')),

#     ('workcenter',          ugettext_lazy('Work Center')),      # routing
#     ('workunit',            ugettext_lazy('Work Unit')),        # workcenter  => segment, jobresponset, materialactual

#     ('storagezone',         ugettext_lazy('Storage Zone')),
#     ('storageunit',         ugettext_lazy('Storage Unit')),
        
#     #('productionunit',      ugettext_lazy('Production Unit')),
#     #('processcell',         ugettext_lazy('Process Cell')),
#     #('unit',                ugettext_lazy('Unit')),

#     ('productionline',      ugettext_lazy('Production Line')),
#     ('workcell',            ugettext_lazy('Workcell')),

#     ('equipmentmodule',     ugettext_lazy('Equipment Module')),
#     ('controlmodule',       ugettext_lazy('Control Module')),

#     #('dept',          ugettext_lazy('Department')), # 부서
#     #('group',               _('Group')), # 반
#     ('route',               ugettext_lazy('Route')), # 공정/워크센터
#     ('routeunit',           ugettext_lazy('Route Unit')), # 공정/워크센터
#     ('other',               ugettext_lazy('Other')), # 
# )


def space_check(value):
    if ' ' in value:
        raise ValidationError('Do not allow spaces.', params={'value': value})
    return


# 24.10.24 김하늘 추가(mes에서는 해당 테이블로 따로 빼서 관리를 했던것 같다) 
# 24.10.25 제거
# class AbstractAuditModel(models.Model):
#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)
    
#     class Meta:
#         abstract = True

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

class Site(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    Name = models.CharField(max_length=75, db_comment="사이트 이름")
    Code = models.CharField(max_length=10, blank=True, null=True, db_comment="사이트 코드")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'site'
        db_table_comment = "사이트 정보를 저장하는 테이블"
        verbose_name = '사이트'

class Factory(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    Code = models.CharField('공장코드', max_length=50, db_comment="공장의 고유 코드")
    Name = models.CharField('공장명', max_length=100, null=True, db_comment="공장명 (nullable)")
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True, db_comment="연결된 사이트 ID")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'factory'
        db_table_comment = "공장 정보를 저장하는 테이블"
        verbose_name = '공장'

class Unit(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    Name = models.CharField(max_length=90, db_comment="단위 이름")
    Code = models.CharField(max_length=30, blank=True, null=True, db_comment="단위 코드 (nullable)")
    Remark = models.CharField(max_length=300, blank=True, null=True, db_comment="비고 (nullable)")
    DispOrder = models.IntegerField(blank=True, null=True, db_comment="표시 순서 (nullable)")
    UseYn = models.CharField(max_length=1, default='Y', db_comment="사용 여부 (Y: 사용, N: 미사용)")
    DelYn = models.CharField(max_length=1, default='N', db_comment="삭제 여부 (Y: 삭제, N: 유지)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'unit'
        db_table_comment = "단위 정보를 저장하는 테이블"
        verbose_name = '단위'

class SystemLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="기본 키")
    Type = models.CharField('로그유형', max_length=20, null=True, db_comment="로그 유형 (예: ERROR, INFO, DEBUG)")
    Source = models.CharField('소스', max_length=100, null=True, db_comment="로그 발생 소스")
    Message = models.TextField('메시지', null=True, db_comment="로그 메시지")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="로그 생성 시간")

    class Meta:
        db_table = 'sys_log'
        db_table_comment = "시스템 로그 정보를 저장하는 테이블"
        verbose_name = '시스템로그'
        index_together = [
            ['_created'],
            ['Type', '_created'],
            ['Source', '_created'],
        ]

    @classmethod
    def add_log(cls, logtype, source, message=None):
        message = str(message)
        syslog = cls.objects.create(Type=logtype, Source=source, Message=message)
        return syslog

class SystemCode(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    CodeType = models.CharField('코드유형', max_length=30, db_comment="코드 유형 (예: 시스템 설정, 사용자 권한)")
    Code = models.CharField('코드', max_length=30, db_comment="코드 값 (예: ACTIVE, INACTIVE)")
    Value = models.CharField('디코드값', max_length=30, db_comment="코드의 실제 의미 (예: 활성화, 비활성화)")
    Description = models.CharField('설명', max_length=500, null=True, db_comment="코드에 대한 설명 (nullable)")
    _ordering = models.IntegerField('_순서', default=0, null=True, db_comment="표시 순서 (nullable)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'sys_code'
        db_table_comment = "시스템 코드 정보를 저장하는 테이블"
        verbose_name = '시스템코드'
        unique_together = [
            ['CodeType', 'Code'],
        ]
        index_together = [
            ['CodeType', 'Code', 'Value'],
        ]

class LabelCode(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    ModuleName = models.CharField('화면명', max_length=100, db_comment="해당 라벨이 사용되는 화면명")
    TemplateKey = models.CharField('템플릿명', max_length=100, db_comment="템플릿 키 (예: UI 구성 요소)")
    LabelCode = models.CharField('라벨코드', max_length=200, db_comment="라벨의 고유 코드")
    Description = models.CharField('설명', max_length=200, null=True, db_comment="라벨에 대한 설명 (nullable)")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'label_code'
        db_table_comment = "라벨 코드 정보를 저장하는 테이블"
        verbose_name = '라벨코드'
        unique_together = [
            ['ModuleName', 'TemplateKey', 'LabelCode'],
        ]

class LabelCodeLanguage(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    LabelCode = models.ForeignKey(LabelCode, on_delete=models.DO_NOTHING, db_comment="라벨 코드 참조")
    LangCode = models.CharField('언어코드', max_length=30, db_comment="언어 코드 (예: ko, en, zh)")
    DispText = models.CharField('표시문자', max_length=500, db_comment="해당 언어로 표시될 문자")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'label_code_lang'
        db_table_comment = "라벨 다국어 설정 정보를 저장하는 테이블"
        verbose_name = '라벨다국어설정'
        unique_together = [
            ['LabelCode', 'LangCode'],
        ]
        index_together = [
            ['LabelCode', 'LangCode', 'DispText'],
        ]

class MenuFolder(models.Model):
    id = models.AutoField(primary_key=True)
    FolderName = models.CharField('폴더명', max_length=50)
    IconCSS = models.CharField('아이콘스타일', max_length=50, null=True)
    Parent = models.ForeignKey('self', verbose_name='부모폴더', related_name='Children', on_delete=models.CASCADE, null=True)
    _order = models.IntegerField('순서',default=0, null=True)

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
        db_table = 'menu_folder'
        verbose_name = '메뉴폴더'
        index_together = [
            ['Parent'],
        ]

class MenuItem(models.Model):
    MenuCode = models.CharField('메뉴코드', primary_key=True, max_length=50, db_comment="메뉴 코드 (기본 키)")
    MenuName = models.CharField('메뉴명', max_length=50, db_comment="메뉴 이름")
    MenuFolder = models.ForeignKey(
        MenuFolder, on_delete=models.DO_NOTHING, null=True, db_comment="소속된 메뉴 폴더 ID (nullable)"
    )    
    IconCSS = models.CharField('아이콘스타일', max_length=50, null=True, db_comment="아이콘 스타일 (CSS 클래스명)")
    Url = models.CharField('Url', max_length=100, null=True, db_comment="메뉴 URL (nullable)")
    Popup = models.CharField('화면PopupYN', max_length=1, null=True, default='N', db_comment="팝업 여부 (Y: 팝업, N: 일반 화면)")
    _order = models.IntegerField('순서', default=0, null=True, db_comment="메뉴 정렬 순서")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'menu_item'
        db_table_comment = "메뉴 항목 정보를 저장하는 테이블"
        verbose_name = '메뉴항목'
        # index_together = [
        #     ['MenuFolder'],
        # ]

class Bookmark(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    User = models.ForeignKey(User, on_delete=models.CASCADE, db_comment="사용자 ID (해당 북마크의 소유자)")
    MenuItem = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, db_column='MenuCode', db_comment="북마크된 메뉴 항목 코드"
    )
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="북마크 생성 날짜")

    class Meta:
        db_table = 'bookmark'
        db_table_comment = "사용자별 바로가기 메뉴 정보를 저장하는 테이블"
        verbose_name = '바로가기메뉴'
        unique_together = [
            ['User', 'MenuItem'],
        ]

class StoryboardItem(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    MenuCode = models.CharField('메뉴코드', max_length=50, db_comment="연결된 메뉴 코드")
    Duration = models.SmallIntegerField('전환시간(초)', db_comment="화면 전환 시간 (초 단위)")
    BoardType = models.CharField('타입', max_length=30, default='menu', db_comment="스토리보드 타입 (예: menu, image, video)")
    ParameterData = models.CharField('파라미터데이터', max_length=100, null=True, db_comment="추가 파라미터 데이터 (nullable)")
    Url = models.CharField('URL', max_length=200, null=True, db_comment="연결된 URL (nullable)")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'storyboard_item'
        db_table_comment = "스토리보드 항목 정보를 저장하는 테이블"
        verbose_name = '스토리보드항목'

class DocumentForm(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    FormType = models.CharField('문서유형', max_length=20, db_comment="문서의 유형 (예: 계약서, 보고서)")
    FormGroup = models.CharField('양식종류', max_length=20, db_comment="양식의 종류 (예: 일반, 기밀)")
    FormName = models.CharField('양식명', max_length=200, db_comment="문서 양식의 이름")
    Content = models.TextField('내용', null=True, db_comment="문서의 내용 (nullable)")
    Description = models.CharField('설명', max_length=500, null=True, db_comment="문서 설명 (nullable)")
    State = models.CharField('상태', max_length=20, null=True, db_comment="문서 상태 (예: 활성, 비활성)")
    StartDate = models.DateTimeField('적용시작일', null=True, db_comment="문서 양식의 적용 시작일")
    EndDate = models.DateTimeField('적용종료일', null=True, db_comment="문서 양식의 적용 종료일")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'doc_form'
        db_table_comment = "문서 양식 정보를 저장하는 테이블"
        verbose_name = '문서양식'
        index_together = [
            ['FormType'],
        ]

class DocumentResult(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    DocumentForm = models.ForeignKey(
        DocumentForm, on_delete=models.PROTECT, db_comment="연결된 문서 양식 ID"
    )
    DocumentDate = models.DateField('일자', db_comment="문서 작성 또는 적용 일자")
    DocumentName = models.CharField('문서명', max_length=200, db_comment="문서 이름")
    Content = models.TextField('내용', null=True, db_comment="문서의 본문 내용 (nullable)")
    Description = models.CharField('설명', max_length=2000, null=True, db_comment="문서 설명 (nullable)")
    Number1 = models.FloatField('수치값1', null=True, db_comment="수치 값 1 (nullable)")
    Number2 = models.FloatField('수치값2', null=True, db_comment="수치 값 2 (nullable)")
    Number3 = models.FloatField('수치값3', null=True, db_comment="수치 값 3 (nullable)")
    Text1 = models.CharField('문자값1', max_length=2000, null=True, db_comment="문자 값 1 (nullable)")
    Text2 = models.CharField('문자값2', max_length=2000, null=True, db_comment="문자 값 2 (nullable)")
    Text3 = models.CharField('문자값3', max_length=2000, null=True, db_comment="문자 값 3 (nullable)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'doc_result'
        db_table_comment = "문서 결과 정보를 저장하는 테이블"
        verbose_name = '문서결과'
        index_together = [
            ['DocumentForm', 'DocumentDate'],
            ['DocumentDate'],
        ]
'''
class AttachMaster(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    TableName = models.CharField('테이블명', max_length=50, db_comment="첨부 파일이 연관된 테이블 이름")
    AttachName = models.CharField('첨부명', max_length=50, db_comment="첨부 파일의 이름")
    Description = models.CharField('설명', max_length=500, null=True, db_comment="첨부 파일 설명 (nullable)")
    FilePath = models.CharField('파일경로', max_length=500, null=True, db_comment="첨부 파일 저장 경로 (nullable)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'attach_master'
        db_table_comment = "첨부 파일 정의 정보를 저장하는 테이블"
        verbose_name = '첨부파일정의'
        index_together = [
            ['TableName'],
        ]
'''

class AttachFile(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")
    TableName = models.CharField('테이블명', max_length=50, db_comment="첨부 파일이 연관된 테이블 이름")
    DataPk = models.IntegerField('데이터pk', db_comment="해당 테이블의 데이터 기본 키")
    AttachName = models.CharField('첨부명', max_length=50, db_comment="업무 구분을 위한 첨부 이름")
    FileIndex = models.IntegerField('파일인덱스', db_comment="파일의 순서 또는 인덱스")
    FileName = models.CharField('파일명', max_length=100, db_comment="사용자가 업로드한 원본 파일명")
    PhysicFileName = models.CharField('물리파일명', max_length=100, db_comment="저장된 물리적인 파일명")
    ExtName = models.CharField('확장자', max_length=10, null=True, db_comment="파일 확장자 (nullable)")
    FilePath = models.CharField('파일경로', max_length=500, null=True, db_comment="파일이 저장된 경로 (nullable)")
    FileSize = models.IntegerField('파일사이즈', null=True, db_comment="파일 크기 (nullable, 단위: byte)")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'attach_file'
        db_table_comment = "첨부 파일 정보를 저장하는 테이블"
        verbose_name = '첨부파일'
        # unique_together = [
        #     ['DataPk', 'TableName', 'AttachName', 'FileIndex'],
        # ]
        index_together = [
            ['DataPk', 'TableName'],
        ]

class Board(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")    
    BoardGroup = models.CharField('게시판명', max_length=50, db_comment="게시판 그룹 이름 (예: 공지사항, 자유게시판)")
    WriteDateTime = models.DateTimeField('작성일', null=True, db_comment="게시글 작성일")
    Title = models.CharField('제목', max_length=100, db_comment="게시글 제목")
    Content = models.TextField('내용', null=True, db_comment="게시글 내용 (nullable)")
    NoticeYN = models.CharField('공지글', max_length=1, db_comment="공지 여부 (Y: 공지, N: 일반글)")
    NoticeEndDate = models.DateField('공지종료일', null=True, db_comment="공지 종료일 (nullable)")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'board'
        db_table_comment = "게시판 정보를 저장하는 테이블"
        verbose_name = '게시판'
        index_together = [
            ['BoardGroup', 'WriteDateTime'],
            ['BoardGroup', 'NoticeYN', 'NoticeEndDate'],
        ]

class BoardReply(models.Model):
    id = models.AutoField(primary_key=True, db_comment="기본 키")    
    Board = models.ForeignKey(
        Board, on_delete=models.CASCADE, null=False, db_comment="댓글이 속한 게시글 ID"
    )
    Reply = models.CharField('댓글', max_length=500, db_comment="댓글 내용")
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="댓글 생성 날짜")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="댓글 수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="댓글 작성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="댓글 수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'board_reply'
        db_table_comment = "게시판 댓글 정보를 저장하는 테이블"
        verbose_name = '게시판댓글'
        index_together = [
            ['Board'],
        ]

class WorkCalendar(models.Model):
    '''워크센터별 근무일, 출근(근무)시간 설정
    '''
    id = models.AutoField(primary_key=True)
    DataDate = models.DateField('일자')
    StartTime = models.TimeField('근무시작시간', null=True)
    EndTime = models.TimeField('근무종료시간', null=True)
    WorkHr =  models.FloatField('실근무시간', null=True)
    HolidayYN = models.CharField('휴일YN', max_length=1, default='N',  null=True)
    DataPk = models.IntegerField('데이터pk', null=True)
    TableName = models.CharField('테이블명', max_length=50, null=True)

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
        db_table = 'work_calendar'
        verbose_name = '작업달력'
        unique_together = [
            ['DataDate', 'DataPk', 'TableName'],
        ]
        index_together = [
            ['DataPk', 'TableName', 'DataDate'],
        ]

class Calendar(models.Model):
    ''' 일정, 회의 등을 등록
    '''
    id = models.AutoField(primary_key=True)
    DataDate = models.DateField('일자')
    StartTime = models.TimeField('시작시간', null=True)
    EndTime = models.TimeField('종료시간', null=True)
    Title =  models.CharField('제목', max_length=100)
    Color = models.CharField('색깔', max_length=100, null=True)
    Description = models.CharField('설명', max_length=500, null=True)

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
        db_table = 'calendar'
        verbose_name = '일정달력'
        index_together = [
            ['DataDate'],
            ['Title', 'DataDate'],
        ]

class PropertyMaster(models.Model):
    id = models.AutoField(primary_key=True)
    TableName = models.CharField('테이블명', max_length=50)
    Code = models.CharField('속성코드', max_length=50)
    Type = models.CharField('속성유형', max_length=50, null=True)
    Description	= models.CharField('속성설명', max_length=500, null=True)
    
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
        db_table = 'prop_master'
        verbose_name = '속성정의'
        unique_together = [
            ('TableName', 'Code'),
        ]

class PropertyData(models.Model):
    ''' 공통속성데이터
    '''
    id = models.AutoField(primary_key=True)
    DataPk = models.IntegerField('데이터pk')
    TableName = models.CharField('테이블명', max_length=50)
    Code = models.CharField('속성코드', max_length=50)
    Type = models.CharField('속성유형', max_length=50, null=True)
    Char1 = models.CharField('문자값1', max_length=200, null=True)
    Number1 =  models.FloatField('수치값1', null=True)
    Date1 = models.DateTimeField('일시값1', null=True)
    Text1 = models.TextField('텍스트값1', null=True)
    
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
        db_table = 'prop_data'
        verbose_name = '속성데이터'
        unique_together = [
            ('DataPk', 'TableName', 'Code'),
        ]

class SystemOption(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField('코드', max_length=50)
    Value = models.TextField('값', null=True)
    Description = models.CharField('설명', max_length=500, null=True)
    
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
        db_table = 'sys_option'
        verbose_name = '시스템옵션'
        unique_together = [
            ['Code'],
        ]

class ActionMaster(models.Model):
    id          = models.AutoField(primary_key=True)
    TableName = models.CharField('테이블명', max_length=50)
    Code = models.CharField('액션코드', max_length=50)
    Type = models.CharField('액션유형', max_length=50, null=True)
    Description	= models.CharField('액션설명', max_length=500, null=True)

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
        db_table = 'action_master'
        verbose_name = '액션정의'
        unique_together = [
            ('TableName', 'Code'),
        ]


class ActionData(models.Model):
    ''' 공통액션데이터. 행위, 행위자, 행위시간을 저장
    '''
    id = models.AutoField(primary_key=True)
    DataPk = models.IntegerField('데이터pk')
    TableName = models.CharField('테이블명', max_length=50)
    Code = models.CharField('액션코드', max_length=50)
    Type = models.CharField('액션유형', max_length=50, null=True)
    ActorPk = models.IntegerField('행위자', null=True)
    ActionDateTime = models.DateTimeField('행위일시', auto_now_add=True)
    Description = models.CharField('비고', max_length=500, null=True)
    
    ActorTableName = models.CharField('행위자테이블명', max_length=50, null=True)
    ActorName = models.CharField('행위자명', max_length=50, null=True)
    Char1 = models.CharField('문자1', max_length=200, null=True)
    Char2 = models.CharField('문자2', max_length=200, null=True)
    Char3 = models.CharField('문자3', max_length=200, null=True)
    StartDate = models.DateField('시작일', null=True) 
    EndDate = models.DateField('마침일', null=True) 
    DataPk2 = models.IntegerField('데이터2pk', null=True)
    TableName2 = models.CharField('테이블2명', max_length=50, null=True)

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
        db_table = 'action_data'
        verbose_name = '액션데이터'
        index_together = [
            ['DataPk', 'TableName', 'ActionDateTime'],
            ['DataPk2', 'TableName2'],
        ]


class RelationData(models.Model):
    ''' 공통관계데이터. 만능 다대다테이블
    '''
    id = models.AutoField(primary_key=True)
    DataPk1 = models.IntegerField('데이터1pk')
    TableName1 = models.CharField('테이블1명', max_length=50)
    DataPk2 = models.IntegerField('데이터2pk')
    TableName2 = models.CharField('테이블2명', max_length=50)
    RelationName = models.CharField('관계명', max_length=50)
    Char1 = models.CharField('문자값1', max_length=200, null=True)
    Number1 =  models.FloatField('수치값1', null=True)
    Date1 = models.DateTimeField('일시값1', null=True)
    Text1 = models.TextField('텍스트값1', null=True)    
    StartDate = models.DateField('적용시작일', null=True)
    EndDate = models.DateField('적용종료일', null=True)
    _order   = models.IntegerField('순서',default=0, null=True)

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
        db_table = 'rela_data'
        verbose_name = '관계데이터'
        unique_together = [
            ['DataPk1', 'TableName1', 'DataPk2', 'TableName2', 'RelationName'],
        ]
        index_together = [
            ['DataPk1', 'TableName1', 'TableName2'],
            ['DataPk2', 'TableName2', 'TableName1'],
        ]


class RelationCodeData(models.Model):
    ''' 공통관계데이터. 만능 다대다테이블. 테이블1은 user_code 혹은 sys_code 
    '''
    id = models.AutoField(primary_key=True)
    Code1 = models.CharField('코드값1', max_length=50)
    TableName1 = models.CharField('테이블1명', max_length=50)
    DataPk2 = models.IntegerField('데이터2pk')
    TableName2 = models.CharField('테이블2명', max_length=50)
    RelationName = models.CharField('관계명', max_length=50)
    Char1 = models.CharField('문자값1', max_length=200, null=True)
    Number1 =  models.FloatField('수치값1', null=True)
    Date1 = models.DateTimeField('일시값1', null=True)
    Text1 = models.TextField('텍스트값1', null=True)    
    StartDate = models.DateField('적용시작일', null=True)
    EndDate = models.DateField('적용종료일', null=True)
    _order   = models.IntegerField('순서',default=0, null=True)

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
        db_table = 'rela_code_data'
        verbose_name = '관계코드데이터'
        unique_together = [
            ['Code1', 'TableName1', 'DataPk2', 'TableName2', 'RelationName'],
        ]
        index_together = [
            ['Code1', 'TableName1', 'TableName2'],
            ['DataPk2', 'TableName2', 'TableName1'],
        ]


class Relation3Data(models.Model):
    ''' 공통관계데이터 3관계. 만능 다대다테이블
    '''
    id = models.AutoField(primary_key=True)
    DataPk1 = models.IntegerField('데이터1pk')
    TableName1 = models.CharField('테이블1명', max_length=50)
    DataPk2 = models.IntegerField('데이터2pk')
    TableName2 = models.CharField('테이블2명', max_length=50)
    DataPk3 = models.IntegerField('데이터3pk')
    TableName3 = models.CharField('테이블3명', max_length=50)
    RelationName = models.CharField('관계명', max_length=50)
    Char1 = models.CharField('문자값1', max_length=200, null=True)
    Number1 =  models.FloatField('수치값1', null=True)
    Date1 = models.DateTimeField('일시값1', null=True)
    Text1 = models.TextField('텍스트값1', null=True)    
    StartDate = models.DateField('적용시작일', null=True)
    EndDate = models.DateField('적용종료일', null=True)
    _order   = models.IntegerField('순서',default=0, null=True)

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
        db_table = 'rela3_data'
        verbose_name = '관계3데이터'
        unique_together = [
            ['DataPk1', 'TableName1', 'DataPk2', 'TableName2', 'DataPk3', 'TableName3', 'RelationName'],
        ]
        index_together = [
            ['DataPk1', 'TableName1', 'TableName2'],
            ['DataPk2', 'TableName2', 'TableName1'],
        ]


class MenuUseLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="기본 키")
    MenuCode = models.CharField('메뉴코드', max_length=50, db_comment="사용한 메뉴의 코드")
    User = models.ForeignKey(User, on_delete=models.CASCADE, db_comment="사용자 ID (해당 메뉴를 사용한 사용자)")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="데이터 상태")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="로그 생성 날짜 (메뉴 사용 시간)")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="수정 날짜")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="생성한 사용자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="수정한 사용자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'menu_use_log'
        db_table_comment = "사용자가 메뉴를 사용한 기록을 저장하는 테이블"
        verbose_name = '메뉴사용로그'
        index_together = [
            ['_created'],
            ['User', '_created'],
            ['MenuCode', '_created'],
            ['User', 'MenuCode', '_created'],
        ]

class LoginLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="기본 키")
    Type = models.CharField('로그인/아웃 구분', max_length=50, db_comment="로그인 또는 로그아웃 구분 (예: LOGIN, LOGOUT)")
    User = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_comment="사용자 ID (로그인한 사용자)")
    IPAddress = models.GenericIPAddressField('IP주소', null=True, db_comment="로그인 시 사용한 IP 주소 (nullable)")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="로그인/로그아웃 발생 시각")

    class Meta:
        db_table = 'login_log'
        db_table_comment = "사용자의 로그인 및 로그아웃 기록을 저장하는 테이블"
        verbose_name = '로그인로그'
        index_together = [
            ['_created'],
            ['User', '_created'],
            ['IPAddress', '_created'],
        ]

class SFLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    logDt  = models.DateTimeField('로그일시', auto_now_add=True)
    useSe = models.CharField('사용구분(접속/종료/변경/조회)', max_length=20)
    sysUser	= models.IntegerField('사용자id')
    conectIp=models.CharField('IP주소', max_length=50)
    dataUsgqty	= models.IntegerField('사용량')
    SendYN = models.CharField('송신YN', max_length=1, default='N')

    class Meta():
        db_table = 'sf_log'
        verbose_name = '스마트팩토리전송로그'

        index_together = [
            ['logDt'],
            #['SendYN'],
            ['SendYN', 'logDt'],
            ['sysUser', 'logDt'],
            ['conectIp', 'logDt'],
        ]

class ErrorLog(models.Model):
    error_log_pk = models.BigAutoField(primary_key=True, db_comment="기본 키")
    error_log_type = models.CharField('오류 유형', max_length=50, db_comment="오류 유형 (예: ERROR, WARNING, INFO)")
    error_log_title = models.CharField('오류 제목', max_length=200, db_comment="오류 제목")
    error_log_desc = models.TextField('오류 설명', db_comment="오류 상세 내용")
    insert_ts = models.DateTimeField('생성 시간', auto_now_add=True, db_comment="로그 생성 시간")

    class Meta:
        db_table = 'error_log'
        db_table_comment = "오류 로그 정보를 저장하는 테이블"
        verbose_name = '오류 로그'
        index_together = [
            ['insert_ts'],
            ['error_log_type', 'insert_ts']
        ]
    
    @classmethod
    def add_log(cls, log_type, title, description):
        return cls.objects.create(
            error_log_type=log_type,
            error_log_title=title,
            error_log_desc=description
        )

class DebugLog(models.Model):
    debug_log_pk = models.BigAutoField(primary_key=True, db_comment="기본 키")
    log_time = models.DateTimeField('로그 시간', auto_now_add=True, db_comment="로그 생성 시간")
    message = models.TextField('로그 메시지', db_comment="로그 상세 내용")

    class Meta:
        db_table = 'debug_log'
        db_table_comment = "디버그 로그 정보를 저장하는 테이블"
        verbose_name = '디버그 로그'
        indexes = [
            models.Index(fields=['log_time'], name='idx_debug_log_time'),
        ]
    
    @classmethod
    def add_log(cls, message):
        return cls.objects.create(message=message)


