from django.db import models
from domain.services.date import DateUtil
from .system import space_check
from django.contrib.postgres.fields import JSONField


class DsData(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField('제목', max_length=50)
    Parent = models.ForeignKey('self', verbose_name='부모id', related_name='Children', on_delete=models.PROTECT, null=True)
    Description = models.TextField('비고', null=True)
    Type = models.CharField('구분', max_length=50, null=True)
    SourceName = models.CharField('데이터출처', max_length=50, null=True)
    DcData = JSONField('컬럼별데이터dictionarydata', null=True)
    DcText = models.TextField('컬럼별데이터', null=True)

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
        db_table = 'ds_data'
        verbose_name = '분석데이터'
        index_together = [
            ['_created', 'Name', 'Type'],
            ['Name', '_created'],
            ['Type', '_created'],
        ]


class DsColumn(models.Model):
    id = models.AutoField(primary_key=True)
    DsData = models.ForeignKey(DsData, verbose_name='분석데이터id', on_delete=models.PROTECT)
    VarIndex = models.IntegerField('변수순서')
    VarName = models.CharField('변수명', max_length=100)
    #VarType = models.CharField('변수유형', max_length=20)
    DataCount = models.IntegerField('데이터개수', null=True)
    MissingCount = models.IntegerField('결측치개수', null=True)
    CategoryCount = models.IntegerField('범주개수', null=True)
    Mean = models.FloatField('평균', null=True)
    Std = models.FloatField('표준편차', null=True)
    Q1 = models.FloatField('Q1', null=True)
    Q2 = models.FloatField('Q2', null=True)
    Q3 = models.FloatField('Q3', null=True)
    MissingValProcess = models.CharField('결측치처리', max_length=50, null=True)
    DropOutLow = models.FloatField('제거할이상치하한', null=True)
    DropOutUpper = models.FloatField('제거할이상치상한', null=True)
    X = models.SmallIntegerField('X변수Y(1)', null=True)
    Y = models.SmallIntegerField('Y변수Y(1)', null=True)

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
        db_table = 'ds_col'
        verbose_name = '데이터변수'
        index_together = [
            ['DsData','VarIndex'],
        ]
        unique_together = [
            ['DsData','VarName'],
        ]


class DsDataTable(models.Model):
    ''' 분석데이터결과
    '''
    id = models.AutoField(primary_key=True)
    DsData = models.ForeignKey(DsData, verbose_name='분석데이터id', on_delete=models.PROTECT)
    RowIndex = models.IntegerField('로인덱스')
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
        db_table = 'ds_data_table'
        verbose_name = '분석데이터결과'
        unique_together = [
            ('DsData', 'RowIndex', 'Code'),
        ]


class DsVarCorrelation(models.Model):
    id = models.AutoField(primary_key=True)
    DsData = models.ForeignKey(DsData, verbose_name='분석데이터id', on_delete=models.PROTECT)
    XVarName = models.CharField('X변수', max_length=100)
    YVarName = models.CharField('Y변수', max_length=100)
    r = models.FloatField('R값', null=True)
    MultiLinearCoef = models.FloatField('다항회귀계수', null=True)
    RegressionEquation = models.CharField('회귀식', max_length=100, null=True)

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
        db_table = 'ds_var_corr'
        verbose_name = '데이터변수'


class LpProblem(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField('제목', max_length=50)
    Description = models.TextField('비고', null=True)
    Type = models.CharField('구분', max_length=50, null=True)
    MinMax = models.CharField('MinMax', max_length=3, default='min')
    ObjectiveEquation = models.CharField('목적식', max_length=2000, null=True)
    SolvedState = models.IntegerField('풀이상태', null=True)
    Solved = models.FloatField('풀이값', null=True)

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
        db_table = 'lp_prob'
        verbose_name = 'LP문제'
        index_together = [
            ['_created', 'Name', 'Type'],
        ]


class LpVariable(models.Model):
    id = models.AutoField(primary_key=True)
    LpProblem = models.ForeignKey(LpProblem, verbose_name='분석데이터id', on_delete=models.PROTECT)
    VarIndex = models.IntegerField('변수순서')
    VarName = models.CharField('변수명', max_length=100)
    Type = models.CharField('구분', max_length=50, null=True)
    Description = models.TextField('설명', null=True)
    LBound = models.FloatField('하한값', null=True)
    UBound = models.FloatField('상한값', null=True)
    Solved = models.FloatField('풀이값', null=True)

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
        db_table = 'lp_var'
        verbose_name = 'LP변수'
        unique_together = [
            ['LpProblem','VarIndex'],
            ['LpProblem','VarName'],
        ]


class LpObjectiveCoef(models.Model):
    id = models.AutoField(primary_key=True)
    LpProblem = models.ForeignKey(LpProblem, verbose_name='분석데이터id', on_delete=models.PROTECT)
    VarIndex = models.IntegerField('변수순서')
    CoefValue = models.FloatField('계수값', null=True)

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
        db_table = 'lp_obj_coef'
        verbose_name = 'LP목적식계수'
        unique_together = [
            ['LpProblem','VarIndex'],
        ]


class LpConstraint(models.Model):
    id = models.AutoField(primary_key=True)
    LpProblem = models.ForeignKey(LpProblem, verbose_name='분석데이터id', on_delete=models.PROTECT)
    Name = models.CharField('제약명', max_length=100, null=True)
    Operator = models.CharField('연산자', max_length=2)
    RightValue = models.FloatField('비교상수')    
    ConstraintEquation = models.CharField('제약식', max_length=2000, null=True)
    Solved = models.FloatField('풀이값', null=True)

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
        db_table = 'lp_constr'
        verbose_name = 'LP제약식'


class LpConstraintCoef(models.Model):
    id = models.AutoField(primary_key=True)
    LpConstraint = models.ForeignKey(LpConstraint, verbose_name='Lp제약식id', on_delete=models.PROTECT)
    VarIndex = models.IntegerField('변수순서')
    CoefValue = models.FloatField('계수값', null=True)

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
        db_table = 'lp_constr_coef'
        verbose_name = 'LP목적식계수'
        unique_together = [
            ['LpConstraint','VarIndex'],
        ]
        
class LearningLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    Type= models.CharField('로그유형', max_length=20, null=True)
    Message = models.TextField('메시지', null=True)
    StartTime = models.DateTimeField('시작시간', null=True)
    EndTime = models.DateTimeField('종료시간', null=True)

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
        db_table = 'learning_log'
        verbose_name = '모델학습로그'
        index_together = [
            ['_created'],
            ['StartTime'],
            ['EndTime'],
        ]