from django.db import models
from domain.services.date import DateUtil
from .system import space_check
from django.contrib.postgres.fields import JSONField


class DsMaster(models.Model):
    id = models.AutoField(primary_key=True, db_comment='모델 마스터 PK') # verbose_name = '모델마스터번호'. char일 가능성. 그럼 유니크 키도 모델마스터 번호가 될 수도.
    Name = models.CharField('모델명', max_length=50, db_comment='모델 마스터 명')
    Type = models.CharField('모델유형', max_length=50, null=True, db_comment='모델마스터 유형')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')
    _creater_nm = models.CharField('작성자명', max_length=10, null=True, db_comment='생성자 이름')
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True, db_comment='수정자 이름')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'ds_master'
        verbose_name = '모델마스터'
        unique_together  = [
            ['Name'],
        ]


class DsModel(models.Model):
    id = models.AutoField(primary_key=True, db_comment='모델 PK')
    Name = models.CharField('모델명', max_length=50, db_comment='모델명')
    Description = models.TextField('비고', null=True, db_comment='비고')
    Type = models.CharField('모델유형', max_length=50, null=True, db_comment='모델 유형')
    # SourceName = models.CharField('데이터출처', max_length=50, null=True) # 설계 변경
    Version = models.CharField('버전', max_length=50, null=True, default='1', db_comment='모델 버전')
    # FilePath = models.CharField('모델파일경로', max_length=500, null=True)
    DsMaster = models.ForeignKey(DsMaster, verbose_name='모델마스터번호', on_delete=models.DO_NOTHING, null=True, db_comment='모델마스터 PK(FK)') # 신규추가

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')
    _creater_nm = models.CharField('작성자명', max_length=10, null=True, db_comment='생성자 이름')
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True, db_comment='수정자 이름')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta():
        db_table = 'ds_model'
        verbose_name = '모델'
        index_together = [
            ['_created', 'Name', 'Type'],
            ['Name', '_created'],
            ['Type', '_created'],
        ]


class DsModelColumn(models.Model):
    id = models.AutoField(primary_key=True, db_comment='모델 학습 데이터 변수(태그) PK')
    DsModel = models.ForeignKey(DsModel, verbose_name='모델id', on_delete=models.DO_NOTHING, null=True, db_comment='모델 PK(FK)') # 신규추가
    VarIndex = models.IntegerField('변수순서', db_comment='변수(태그) 순서')
    VarName = models.CharField('변수명', max_length=100, db_comment='변수(태그) 명')
    VarType = models.CharField('변수유형', max_length=20, db_comment='변수(태그) 유형')
    DataCount = models.IntegerField('데이터개수', null=True, db_comment='변수(태그) 데이터 개수')
    MissingCount = models.IntegerField('결측치개수', null=True, db_comment='변수(태그) 데이터 결측치 개수')
    CategoryCount = models.IntegerField('범주개수', null=True, db_comment='변수(태그) 데이터 내 범주 개수')
    Mean = models.FloatField('평균', null=True, db_comment='변수(태그) 데이터 평균')
    Std = models.FloatField('표준편차', null=True, db_comment='변수(태그) 데이터 표준편차')
    Q1 = models.FloatField('Q1', null=True, db_comment='변수(태그) 데이터 Q1')
    Q2 = models.FloatField('Q2', null=True, db_comment='변수(태그) 데이터 Q2')
    Q3 = models.FloatField('Q3', null=True, db_comment='변수(태그) 데이터 Q3')
    MissingValProcess = models.CharField('결측치처리', max_length=50, null=True, db_comment='결측치 처리 방법')
    DropOutLow = models.FloatField('제거할이상치하한', null=True, db_comment='제거 기준 이상치 하한')
    DropOutUpper = models.FloatField('제거할이상치상한', null=True, db_comment='제거 기준 이상치 상한')
    X = models.SmallIntegerField('X변수Y(1)', null=True, db_comment='X변수 여부')
    Y = models.SmallIntegerField('Y변수Y(1)', null=True, db_comment='Y변수 여부')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')
    _creater_nm = models.CharField('작성자명', max_length=10, null=True, db_comment='생성자 이름')
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True, db_comment='수정자 이름')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'ds_model_col'
        verbose_name = '모델태그'
        index_together = [
            ['DsModel','VarIndex'],
        ]
        unique_together = [
            ['DsModel','VarName'],
        ]


class DsModelData(models.Model):
    ''' 모델학습데이터
    '''
    id = models.AutoField(primary_key=True, db_comment='모델 학습 데이터 로우(ROW) PK')
    DsModel = models.ForeignKey(DsModel, verbose_name='모델id', on_delete=models.DO_NOTHING, null=True, db_comment='모델 PK(FK)') # 신규추가
    RowIndex = models.IntegerField('로우인덱스', db_comment='ROW 데이터 index')
    Code = models.CharField('속성코드', max_length=50, db_comment='ROW 데이터 변수(태그) 명')
    Type = models.CharField('속성유형', max_length=50, null=True, db_comment='ROW 데이터 변수(태그) 유형')
    Char1 = models.CharField('문자값1', max_length=200, null=True, db_comment='ROW 데이터 값(char)')
    Number1 =  models.FloatField('수치값1', null=True, db_comment='ROW 데이터 값(float)')
    Date1 = models.DateTimeField('일시값1', null=True, db_comment='ROW 데이터 값(date)')   # 캐릭터로 감당 가능하지 않나 싶지만 우선 유지
    Text1 = models.TextField('텍스트값1', null=True, db_comment='ROW 데이터 값(text)')     # 캐릭터로 감당 가능하지 않나 싶지만 우선 유지
 
    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')
    _creater_nm = models.CharField('작성자명', max_length=10, null=True, db_comment='생성자 이름')
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True, db_comment='수정자 이름')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'ds_model_data'
        verbose_name = '모델학습데이터'
        unique_together = [
            ('DsModel', 'RowIndex', 'Code'),
        ]


class DsTagCorrelation(models.Model):
    id = models.AutoField(primary_key=True, db_comment='모델 구성 변수(태그) 간 상관관계 PK')
    DsModel = models.ForeignKey(DsModel, verbose_name='모델id', on_delete=models.DO_NOTHING, null=True, db_comment='모델 PK(FK)') # 신규추가
    XVarName = models.CharField('X변수', max_length=100, db_comment='모델 독립변수')
    YVarName = models.CharField('Y변수', max_length=100, db_comment='모델 종속변수')
    r = models.FloatField('R값', null=True, db_comment='모델 결정계수(설명력)')
    MultiLinearCoef = models.FloatField('다항회귀계수', null=True, db_comment='다항회귀계수(가중치)')
    RegressionEquation = models.CharField('회귀식', max_length=100, null=True, db_comment='모델 회귀식')
    AlgorithmType = models.CharField('알고리즘종류', max_length=100, null=True, db_comment='모델링에 사용된 알고리즘')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')
    _creater_nm = models.CharField('작성자명', max_length=10, null=True, db_comment='생성자 이름')
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True, db_comment='수정자 이름')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'ds_tag_corr'
        verbose_name = '모델태그상관관계'


# class LpProblem(models.Model):
#     id = models.AutoField(primary_key=True)
#     Name = models.CharField('제목', max_length=50)
#     Description = models.TextField('비고', null=True)
#     Type = models.CharField('구분', max_length=50, null=True)
#     MinMax = models.CharField('MinMax', max_length=3, default='min')
#     ObjectiveEquation = models.CharField('목적식', max_length=2000, null=True)
#     SolvedState = models.IntegerField('풀이상태', null=True)
#     Solved = models.FloatField('풀이값', null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modified', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'lp_prob'
#         verbose_name = 'LP문제'
#         index_together = [
#             ['_created', 'Name', 'Type'],
#         ]


# class LpVariable(models.Model):
#     id = models.AutoField(primary_key=True)
#     LpProblem = models.ForeignKey(LpProblem, verbose_name='분석데이터id', on_delete=models.PROTECT)
#     VarIndex = models.IntegerField('변수순서')
#     VarName = models.CharField('변수명', max_length=100)
#     Type = models.CharField('구분', max_length=50, null=True)
#     Description = models.TextField('설명', null=True)
#     LBound = models.FloatField('하한값', null=True)
#     UBound = models.FloatField('상한값', null=True)
#     Solved = models.FloatField('풀이값', null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modified', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'lp_var'
#         verbose_name = 'LP변수'
#         unique_together = [
#             ['LpProblem','VarIndex'],
#             ['LpProblem','VarName'],
#         ]


# class LpObjectiveCoef(models.Model):
#     id = models.AutoField(primary_key=True)
#     LpProblem = models.ForeignKey(LpProblem, verbose_name='분석데이터id', on_delete=models.PROTECT)
#     VarIndex = models.IntegerField('변수순서')
#     CoefValue = models.FloatField('계수값', null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modified', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'lp_obj_coef'
#         verbose_name = 'LP목적식계수'
#         unique_together = [
#             ['LpProblem','VarIndex'],
#         ]


# class LpConstraint(models.Model):
#     id = models.AutoField(primary_key=True)
#     LpProblem = models.ForeignKey(LpProblem, verbose_name='분석데이터id', on_delete=models.PROTECT)
#     Name = models.CharField('제약명', max_length=100, null=True)
#     Operator = models.CharField('연산자', max_length=2)
#     RightValue = models.FloatField('비교상수')    
#     ConstraintEquation = models.CharField('제약식', max_length=2000, null=True)
#     Solved = models.FloatField('풀이값', null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modified', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'lp_constr'
#         verbose_name = 'LP제약식'


# class LpConstraintCoef(models.Model):
#     id = models.AutoField(primary_key=True)
#     LpConstraint = models.ForeignKey(LpConstraint, verbose_name='Lp제약식id', on_delete=models.PROTECT)
#     VarIndex = models.IntegerField('변수순서')
#     CoefValue = models.FloatField('계수값', null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modified', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'lp_constr_coef'
#         verbose_name = 'LP목적식계수'
#         unique_together = [
#             ['LpConstraint','VarIndex'],
#         ]
        
# class LearningLog(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     Type= models.CharField('로그유형', max_length=20, null=True)
#     Message = models.TextField('메시지', null=True)
#     StartTime = models.DateTimeField('시작시간', null=True)
#     EndTime = models.DateTimeField('종료시간', null=True)

#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modified', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)

#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#         self._modifier_id = user.id
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta():
#         db_table = 'learning_log'
#         verbose_name = '모델학습로그'
#         index_together = [
#             ['_created'],
#             ['StartTime'],
#             ['EndTime'],
#         ]