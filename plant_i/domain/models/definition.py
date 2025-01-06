from tabnanny import verbose
from django.db import models
from domain.services.date import DateUtil
from .system import space_check, Site, Factory, Unit
from .user import Depart


class Line(models.Model):
    id  = models.AutoField(primary_key=True)
    Code = models.CharField('라인코드', max_length=50)
    Name = models.CharField('라인명', max_length=100, null=True)
    Description	= models.CharField('설명', max_length=500, null=True)
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
        db_table = 'line'
        verbose_name = '라인'
        unique_together = [
            ['Code'],
            ['Name'],
        ]

class Process(models.Model):
    id  = models.AutoField(primary_key=True)
    Code = models.CharField('공정코드', max_length=50)
    Name = models.CharField('공정명', max_length=100, null=True)
    ProcessType = models.CharField('공정유형', max_length=100, null=True)
    Description	= models.CharField('설명', max_length=500, null=True)

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
        db_table = 'process'
        verbose_name = '공정'
        unique_together = [
            ['Code'],
            ['Name'],
        ]

class Shift(models.Model):
    id  = models.AutoField(primary_key=True)
    Code = models.CharField('근무조코드', max_length=30)
    Name = models.CharField('근무조명', max_length=30)
    StartTime = models.CharField('시작시간', max_length=5, null=True)   #hh24:mm
    EndTime = models.CharField('종료시간', max_length=5, null=True)     #hh24:mm
    Description	= models.CharField('설명', max_length=500, null=True)
    
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
        db_table = 'shift'
        verbose_name = '근무조'
        unique_together = [
            ['Code'],
        ]
        


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=75)
    Code = models.CharField(max_length=50, blank=True, null=True)
    Email = models.CharField(max_length=50, blank=True, null=True)
    TelNo = models.CharField(max_length=30, blank=True, null=True)
    Address = models.CharField(db_column='addr', max_length=1000, blank=True, null=True)
    BusinessDesc = models.CharField(max_length=150, blank=True, null=True)
    CustomerYn = models.CharField(max_length=1)
    SupplierYn = models.CharField(max_length=1)
    Remark = models.CharField(max_length=300, blank=True, null=True)
    UseYn = models.CharField(max_length=1, default='Y')
    DelYn = models.CharField(max_length=1, default='N')
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, blank=True, null=True)
    UserText1 = models.CharField(max_length=200, blank=True, null=True)
    UserText2 = models.CharField(max_length=200, blank=True, null=True)
    UserText3 = models.CharField(max_length=200, blank=True, null=True)
    UserText4 = models.CharField(max_length=200, blank=True, null=True)
    UserText5 = models.CharField(max_length=200, blank=True, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'company'
        verbose_name = '업체'
  
        
class Cycle(models.Model):
    id = models.AutoField(primary_key=True)
    Type = models.CharField(max_length=50)
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=400, blank=True, null=True)
    StartDate = models.DateField(null=True)
    StartTime = models.CharField(max_length=20, blank=True, null=True)
    Remark = models.CharField(max_length=500, blank=True, null=True)
    UseYn = models.CharField(max_length=1, default='Y')
    DelYn = models.CharField(max_length=1, default='N')
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True)
    HolidayYn = models.CharField(max_length=1, default='N')

    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'cycle'
        verbose_name = '주기'
        
        
class DocumentFolder(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Code = models.CharField(max_length=50, blank=True, null=True)
    UpDocFold_id = models.IntegerField(blank=True, null=True) # 외래 키 관계 설정 가능
    DispOrder = models.IntegerField(blank=True, null=True)
    UseYn = models.CharField(max_length=1, default='Y')
    DelYn = models.CharField(max_length=1, default='N')
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'doc_fold'
        verbose_name = '문서폴더'
        
class Docuemnt(models.Model):
    id = models.AutoField(primary_key=True)
    DocumentFolder = models.ForeignKey(DocumentFolder, on_delete=models.PROTECT)
    Code = models.CharField(max_length=100)
    Title = models.CharField(max_length=300, null=True)
    Content = models.CharField(max_length=4000, null=True)
    Version = models.IntegerField()
    DelYn = models.CharField(max_length=1, default='N')

    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'doc'
        verbose_name = '문서'

        
class Holiday(models.Model):
    id = models.AutoField(primary_key=True)
    Date = models.DateField()
    UseYn = models.CharField(max_length=1, default='Y')
    FixedYn = models.CharField(max_length=1, default='N')
    Remark = models.CharField(max_length=300, blank=True, null=True)
    DelYn = models.CharField(max_length=1, default='N')
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'holiday'
        verbose_name = '공휴일'
        
class CustCol(models.Model):
    id = models.AutoField(primary_key=True)
    TableName = models.CharField(max_length=50, null=True)
    Name = models.CharField(max_length=50, null=True)
    DataType = models.CharField(max_length=50, null=True)
    DataFormat = models.CharField(max_length=50, null=True)
    CodeGrpName = models.CharField(max_length=1, null=True)
    UseYn = models.CharField(max_length=1, default='Y')
    RequiredYn = models.CharField(max_length=1, default='N')
    DispOrder = models.IntegerField(blank=True, null=True)
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'cust_col'
        verbose_name = '사용자 정의 컬럼'



class CodeGroup(models.Model):
    id = models.AutoField('코드그룹번호', primary_key=True)
    Code = models.CharField('코드그룹코드', max_length=50, blank=False, null=False)
    Name = models.CharField('코드그룹명', max_length=100, blank=True, null=True)
    SystemYn = models.CharField('시스템여부', max_length=1, blank=False, null=False)
    Remark = models.CharField('비고', max_length=500, blank=True, null=True)
    UseYn = models.CharField('사용여부', max_length=1, default='Y', blank=False, null=False)
    DelYn = models.CharField('삭제여부', max_length=1, default='N', blank=True, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'code_group'
        verbose_name = '코드그룹'
        
class Code(models.Model):
    id = models.AutoField('코드번호', primary_key=True)
    #CodeGroup = models.ForeignKey(CodeGroup, on_delete=models.DO_NOTHING, null=True)
    CodeGroupCode = models.CharField('코드그룹코드', max_length=50, blank=True, null=True)
    Code = models.CharField('코드', max_length=50, blank=False, null=False)
    Name = models.CharField('코드명', max_length=100, blank=False, null=False)
    Attr1 = models.CharField('속성1', max_length=100, blank=True, null=True)
    Attr2 = models.CharField('속성2', max_length=100, blank=True, null=True)
    Attr3 = models.CharField('속성3', max_length=100, blank=True, null=True)
    Remark = models.CharField('비고', max_length=500, blank=True, null=True)
    DispOrder = models.IntegerField('표시순서', blank=True, null=True)
    UseYn = models.CharField('사용여부', max_length=1, default='Y', blank=False, null=False)
    DelYn = models.CharField('삭제여부', max_length=1, default='N', blank=True, null=True)
    
    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'code'
        verbose_name = '코드'


class EquipmentGroup(models.Model):
    id = models.AutoField(primary_key=True)
    Code = models.CharField('설비그룹코드', max_length=50, validators=[space_check],)
    Name = models.CharField('설비그룹명', max_length=100, default='None')
    EquipmentType = models.CharField('설비유형', max_length=50, default='manufacturing')
    Description	= models.CharField('설명', max_length=500, null=True)

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
        db_table = 'equ_grp'
        verbose_name = '설비그룹'
        unique_together = [
            ['Code'],
            ['Name'],
        ]


class Equipment(models.Model): #, part1_fields.ElementLevelType):
    id  = models.AutoField(primary_key=True)
    Code = models.CharField('설비코드', max_length=50, validators=[space_check])
    Line = models.ForeignKey(Line, db_column='line_id', on_delete=models.DO_NOTHING, null=True) # 신규추가
    MESCode = models.CharField('MES설비코드', max_length=50, null =True) # 신규추가
    SAPCode = models.CharField('SAP설비코드', max_length=50, null =True) # 신규추가
    Name = models.CharField('설비명', max_length=100)
    EquipmentGroup = models.ForeignKey(EquipmentGroup, on_delete=models.DO_NOTHING, null=True)
    Description	= models.CharField('설명', max_length=500, null=True)
    Maker = models.CharField('제조사', max_length=50, null=True)# 제작업체
    Model = models.CharField('모델', max_length=50, null=True)
    Standard = models.CharField('규격', max_length=50, null=True)
    Usage = models.CharField('용도', max_length=50, null=True)
    ManageNumber = models.CharField('관리번호', max_length=50, null=True)
    SerialNumber = models.CharField('시리얼넘버', max_length=50, null=True)
    Depart = models.ForeignKey(Depart, null=True, on_delete=models.DO_NOTHING) 

    ProductionYear = models.SmallIntegerField('제작연도', null=True)
    AssetYN = models.CharField('자산성여부', max_length=1, null=True)
    DurableYears = models.SmallIntegerField('내용연수', null=True)
    PowerWatt = models.FloatField('소비전력(W)', null=True)    
    Voltage = models.CharField('사용전압', null=True, max_length=50)    
    Manager = models.CharField('관리책임자', max_length=100, null=True)
    SupplierName = models.CharField('공급업체', max_length=50, null=True)
    PurchaseDate = models.DateField('구매일', null=True)
    PurchaseCost = models.FloatField('구매가', null=True)   
    ServiceCharger = models.CharField('서비스담당자', max_length=100, null=True) 
    ASTelNumber = models.CharField('AS전화번호', null=True, max_length=50)
    AttentionRemark = models.CharField('주의사항', null=True, max_length=2000)    
    Inputdate = models.CharField('입고일', null=True, max_length=12)
    InstallDate    = models.DateField('설치일', null=True)
    DisposalDate    = models.DateField('폐기일', null=True)
    DisposalReason = models.CharField('폐기사유', max_length=100, null=True) 
    OperationRateYN = models.CharField('가동률표시YN', max_length=1, null=True) 
    Status = models.CharField('설비상태', max_length=10, null=True, default='normal')


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
        db_table = 'equ'
        verbose_name = '설비'
        verbose_name_plural = 'Equipments'
        default_related_name = 'Equipments'

        unique_together = [
            ['Code'],
            ['Name'],
        ]
        #index_together = [
        #    ('WorkCenter'),
        #]


#class EquipmentProperty(AbstractAuditModel):
#    id          = models.AutoField(primary_key=True)
#    Code = models.CharField('Code', max_length=50, validators=[space_check])
#    Name = models.CharField('Name', max_length=100, default='None')
#    Owner = models.ForeignKey(Equipment, on_delete=models.CASCADE)
#    Parent = models.ForeignKey('self', verbose_name='Parent', related_name='Children', on_delete=models.CASCADE, null=True)
#    Value = models.TextField('Value', null=True, db_column='Value')
#    class Meta():
#        db_table = 'equ_pro'
#        verbose_name = '사용자그룹'
#        unique_together = [
#            ('Owner', 'Code','Parent'),
#            ('Owner', 'Name','Parent')
#        ]
   


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
    tag_name = models.CharField('태그명', max_length=50)
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
    id  = models.AutoField(primary_key=True)
    Factory = models.ForeignKey(Factory, on_delete=models.DO_NOTHING)
    Code = models.CharField('품목코드', max_length=50, validators=[space_check])
    Name = models.CharField('품목명', max_length=100)
    Standard = models.CharField('규격', max_length=1000)
    ItemGroup = models.CharField('자재그룹', max_length=9, null=True)
    ItemType = models.CharField('자재유형', max_length=15, null=True)
    BasicUnit = models.CharField('기본단위', max_length=3, null=True)
    ItemType = models.CharField('품목유형', max_length=15, null=True)
    CycleTime = models.DecimalField('c/t', decimal_places=3, max_digits=10, null=True)
    in_price = models.DecimalField('입고금액',decimal_places=3, max_digits=10, null=True)
    out_price = models.DecimalField('출고금액', decimal_places=3, max_digits=10, null=True)

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
        db_table = 'material'
        verbose_name = '품목정보'
        unique_together  = [
            ['Code'],
            ['Name'],
        ]
 

'''
데이터수집의 복잡성으로 주석처리함

class EquipAlarm(models.Model):    
    alarm_code = models.CharField('알람코드', db_column='equ_alarm_cd' , max_length=50, primary_key=True, null=False)
    Equipment = models.ForeignKey(Equipment, db_column='Equipment_id', on_delete=models.DO_NOTHING)    
    Name = models.CharField('알람명', db_column='alarm_nm' , max_length=100)
    AlarmNumber = models.CharField('알람식별번호', db_column='alarm_num' ,max_length=50, null=True)    
    Detail = models.TextField('알람상세', db_column='alarm_detail', null=True)

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
        db_table = 'equ_alarm'
        verbose_name = '설비알람정보'
        index_together = [ 
            ['Equipment']
        ]

class EquipAlarmHistory(models.Model):
    id  = models.BigAutoField(primary_key=True)
    alarm_code =  models.CharField('알람코드', db_column='equ_alarm_cd' , max_length=50)
    Detail = models.TextField('알람추가내용', db_column='detail', null=True)
    DataDate = models.DateTimeField('발생일시')

    class Meta():
        db_table = 'equ_alarm_hist'
        verbose_name = '설비알람이력'
        index_together = [ 
            ['alarm_code','DataDate'],
            ['DataDate'],
        ]
'''