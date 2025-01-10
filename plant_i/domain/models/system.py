from model_utils import Choices

from django.db import models
from django.contrib.auth.models import User
from domain.services.date import DateUtil

from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy


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

#     #('department',          ugettext_lazy('Department')), # 부서
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
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=75)
    Code = models.CharField(max_length=10, blank=True, null=True)

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
    
    class Meta:
        db_table = 'site'
        verbose_name = '사이트'


class Factory(models.Model):
    id  = models.AutoField(primary_key=True)
    Code = models.CharField('공장코드', max_length=50)
    Name = models.CharField('공장명', max_length=100, null=True)
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True)
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
        db_table = 'factory'
        verbose_name = '공장'
        unique_together = [
            ['Site'],
            ['Code'],
            ['Name'],
        ]


class Unit(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=90)
    Code = models.CharField(max_length=30, blank=True, null=True)
    Remark = models.CharField(max_length=300, blank=True, null=True)
    DispOrder = models.IntegerField(blank=True, null=True)
    UseYn = models.CharField(max_length=1, default='Y')
    DelYn = models.CharField(max_length=1, default='N')

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

    class Meta:
        db_table = 'unit'
        verbose_name = '단위'


class SystemLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    Type= models.CharField('로그유형', max_length=20, null=True)
    Source= models.CharField('소스', max_length=100, null=True)
    Message = models.TextField('메시지', null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)

    class Meta():
        db_table = 'sys_log'
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
    id = models.AutoField(primary_key=True)
    CodeType = models.CharField('코드유형', max_length=30)
    Code = models.CharField('코드', max_length=30)
    Value = models.CharField('디코드값', max_length=30)
    Description	= models.CharField('설명', max_length=500, null=True)
    _ordering   = models.IntegerField('_순서',default=0, null=True)

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
        db_table = 'sys_code'
        verbose_name = '시스템코드'
        unique_together = [
            ['CodeType', 'Code'],
        ]
        index_together = [
            ['CodeType', 'Code', 'Value'],
        ]

class LabelCode(models.Model):
    id = models.AutoField(primary_key=True)
    ModuleName = models.CharField('화면명', max_length=100)
    TemplateKey = models.CharField('템플릿명', max_length=100)
    LabelCode = models.CharField('라벨코드', max_length=200)
    Description	= models.CharField('설명', max_length=200, null=True)
    
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
        db_table = 'label_code'
        verbose_name = '라벨코드'
        unique_together = [
            ['ModuleName', 'TemplateKey', 'LabelCode'],
        ]

class LabelCodeLanguage(models.Model):
    id = models.AutoField(primary_key=True)
    LabelCode = models.ForeignKey(LabelCode, on_delete=models.DO_NOTHING)
    LangCode = models.CharField('언어코드', max_length=30)
    DispText = models.CharField('표시문자', max_length=500)
    
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
        db_table = 'label_code_lang'
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
    MenuCode = models.CharField('메뉴코드', primary_key=True, max_length=50)
    MenuName = models.CharField('메뉴명', max_length=50)
    MenuFolder = models.ForeignKey(MenuFolder, on_delete=models.DO_NOTHING, null=True)    
    IconCSS = models.CharField('아이콘스타일', max_length=50, null=True)
    Url = models.CharField('Url', max_length=100, null=True)
    Popup = models.CharField('화면PopupYN', max_length=1, null=True, default='N')
    _order = models.IntegerField('순서', default=0, null=True)

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
        db_table = 'menu_item'
        verbose_name = '메뉴항목'
        #index_together = [
        #    ['MenuFolder'],
        #]

class Bookmark(models.Model):
    id = models.AutoField(primary_key=True)
    User = models.ForeignKey(User, on_delete=models.CASCADE)    
    MenuItem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, db_column='MenuCode')
    _created    = models.DateTimeField('_created', auto_now_add=True)

    class Meta():
        db_table = 'bookmark'
        verbose_name = '바로가기메뉴'
        unique_together = [
            ['User', 'MenuItem'],
        ]

class StoryboardItem(models.Model):
    id = models.AutoField(primary_key=True)
    MenuCode = models.CharField('메뉴코드', max_length=50)
    Duration = models.SmallIntegerField('전환시간(초)')
    #MenuCode = models.CharField( max_length=30, default='default')
    BoardType = models.CharField('타입', max_length=30, default='menu')
    ParameterData = models.CharField('파라미터데이터',max_length=100, null=True)
    Url = models.CharField('URL',max_length=200, null=True)
    
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
        db_table = 'storyboard_item'
        verbose_name = '스토리보드항목'

class DocumentForm(models.Model):
    id = models.AutoField(primary_key=True)
    FormType = models.CharField('문서유형', max_length=20,)
    FormGroup = models.CharField('양식종류', max_length=20,)
    FormName = models.CharField('양식명', max_length=200,)
    Content = models.TextField('내용', null=True, )
    Description	= models.CharField('설명', max_length=500, null=True)
    State = models.CharField('상태', max_length=20, null=True)
    StartDate = models.DateTimeField('적용시작일', null=True)
    EndDate = models.DateTimeField('적용종료일', null=True)
    
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
        db_table = 'doc_form'
        verbose_name = '문서양식'
        index_together = [
            ['FormType'],
        ]

class DocumentResult(models.Model):
    id  = models.AutoField(primary_key=True)
    DocumentForm = models.ForeignKey(DocumentForm, on_delete=models.PROTECT)
    DocumentDate = models.DateField('일자')
    DocumentName = models.CharField('문서명', max_length=200)
    Content	= models.TextField('내용', null=True)
    Description	= models.CharField('설명', max_length=2000, null=True)
    Number1 = models.FloatField('수치값1', null=True)
    Number2 = models.FloatField('수치값2', null=True)
    Number3 = models.FloatField('수치값3', null=True)
    Text1 = models.CharField('문자값1', max_length=2000, null=True)
    Text2 = models.CharField('문자값2', max_length=2000, null=True)
    Text3 = models.CharField('문자값3', max_length=2000, null=True)

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
        db_table = 'doc_result'
        verbose_name = '문서결과'
        index_together = [
            ['DocumentForm', 'DocumentDate'],
            ['DocumentDate'],
        ]

class AttachMaster(models.Model):
    id = models.AutoField(primary_key=True)
    TableName = models.CharField('테이블명', max_length=50)
    AttachName = models.CharField('첨부명', max_length=50)
    Description	= models.CharField('설명', max_length=500, null=True)
    FilePath = models.CharField('파일경로', max_length=500, null=True)

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
        db_table = 'attach_master'
        verbose_name = '첨부파일정의'
        index_together = [
            ['TableName'],
        ]

class AttachFile(models.Model):
    id = models.AutoField(primary_key=True)
    TableName = models.CharField('테이블명', max_length=50)
    DataPk = models.IntegerField('데이터pk')
    AttachName = models.CharField('첨부명', max_length=50) # 데이터의 업무 구분
    FileIndex = models.IntegerField('파일인덱스')
    FileName = models.CharField('파일명', max_length=100) # 사용자의 업로드한 파일명
    PhysicFileName = models.CharField('물리파일명', max_length=100) # 물리적인 저장파일명
    ExtName = models.CharField('확장자', max_length=10, null=True)
    FilePath = models.CharField('파일경로', max_length=500, null=True)
    FileSize = models.IntegerField('파일사이즈', null=True)
    
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
        db_table = 'attach_file'
        verbose_name = '첨부파일'
        #unique_together = [
        #    ['DataPk', 'TableName', 'AttachName', 'FileIndex'],
        #]
        index_together = [
            ['DataPk', 'TableName'],
        ]

class Board(models.Model):
    id  = models.AutoField(primary_key=True)    
    #BoardGroup = models.ForeignKey(BoardGroup, on_delete=models.CASCADE, null=False)
    BoardGroup = models.CharField('게시판명', max_length=50)
    WriteDateTime = models.DateTimeField('작성일', null=True)
    Title = models.CharField('제목', max_length=100)
    Content = models.TextField('내용', null=True)
    NoticeYN = models.CharField('공지글', max_length=1)
    NoticeEndDate = models.DateField('공지종료일', null=True)
    
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
        db_table = 'board'
        verbose_name = '게시판'
        index_together = [
            ['BoardGroup', 'WriteDateTime'],
            ['BoardGroup', 'NoticeYN', 'NoticeEndDate'],
        ]

class BoardReply(models.Model):
    id = models.AutoField(primary_key=True)    
    Board = models.ForeignKey(Board, on_delete=models.CASCADE, null=False)
    Reply = models.CharField('댓글', max_length=500)
    
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
        db_table = 'board_reply'
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
    id = models.BigAutoField(primary_key=True)
    MenuCode = models.CharField('메뉴코드', max_length = 50)
    User = models.ForeignKey(User, on_delete=models.CASCADE)

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
        db_table = 'menu_use_log'
        verbose_name = '메뉴사용로그'
        index_together = [
            ['_created'],
            ['User', '_created'],
            ['MenuCode', '_created'],
            ['User', 'MenuCode', '_created'],
        ]

class LoginLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    Type= models.CharField('로그인/아웃 구분', max_length=50)
    User = models.ForeignKey(User, on_delete=models.DO_NOTHING)    
    IPAddress = models.GenericIPAddressField('IP주소', null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    class Meta():
        db_table = 'login_log'
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


