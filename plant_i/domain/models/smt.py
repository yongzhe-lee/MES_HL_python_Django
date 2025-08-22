from tabnanny import verbose
from django.db import models
from domain.services.date import DateUtil
from django.contrib.auth.models import User
from domain.models.definition import Material, Equipment
from domain.models.cmms import CmEquipment

###################################################################
class ReflowProfile(models.Model):
    '''
    리플로우 프로파일
    '''
    id = models.AutoField(primary_key=True, db_comment="리플로우 프로파일 ID")
    Material = models.ForeignKey(Material, on_delete=models.DO_NOTHING, db_comment="품목 ID (참조키)", db_column="mat_pk")
    DataDate = models.DateTimeField('기준일시', db_column="data_date")
    Direction = models.CharField( max_length=50, null=True, db_comment="direction top/bottom", db_column="direction")
    FanLevel = models.IntegerField('FanLevel', null=True, db_comment="Fan Level", db_column="fan_level")
    MaxTemp = models.DecimalField('Max temp', decimal_places=3, max_digits=10, null=True, db_column="max_temp", db_comment="max temp")
    PreHeating = models.DecimalField('PreHeating', decimal_places=3, max_digits=10, null=True, db_column="pre_heating", db_comment="Pre Heating")
    DeltaCoolingTemp = models.DecimalField('Delta Cooling Temp', decimal_places=3, max_digits=10, null=True, db_column="delta_cooling_temp", db_comment="Delta Temp")
    AboveSecond = models.IntegerField('AboveSecond', null=True, db_comment="Above Second", db_column="above_second")
    FluxDwell = models.IntegerField('flux_dwell', null=True, db_comment="flux_dwell", db_column="flux_dwell")
    DeltaPeakTemp= models.DecimalField('DeltaPeakTemp', decimal_places=3, max_digits=10, null=True, db_column="delta_peak_temp", db_comment="Delta Peak Temp")
    OxygenConcentrationRatio = models.DecimalField('Oxygen Concentration ratio', decimal_places=3, max_digits=10, null=True, db_column="oxy_concen_ratio", db_comment="Oxygen Concentration ratio")
    CBSPositions = models.IntegerField('CBS Positions', null=True, db_comment="CBS Positions", db_column="cbs_positions")
    Acceptable = models.CharField('Acceptable', max_length=1, null=True, db_comment="Acceptable", db_column="acceptable")
    Description = models.TextField('비고', null=True)

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

    class Meta():
        db_table = 'reflow_profile'
        verbose_name = '리플로우 프로파일'
        db_table_comment = '리플로우 프로파일 관리 테이블'


class MonthlyTermResult(models.Model):
    id = models.AutoField(primary_key=True, db_comment="솔더점도체크 ID")
    data_year = models.IntegerField('년', db_column="data_year", db_comment="년")
    data_month = models.IntegerField('월', db_column="data_month", db_comment="월")
    data_group = models.CharField('데이터그룹', max_length=50, db_column="data_group", null=True, db_comment="데이터 그룹")
    confirmer = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_comment="팀장확인자 ID (참조키)", db_column="confirmer_id", null=True)
    confirm_yn = models.CharField('확인여부', max_length=1, default='N', db_column="confirm_yn", db_comment="확인 여부")
    confirm_date = models.DateTimeField('확인일시', db_column="confirm_date", null=True, db_comment="확인 일시")
    Description = models.TextField('비고', null=True) 

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

    class Meta():
        db_table = 'mon_term_result'
        verbose_name = '월별점검확인결과'
        db_table_comment = '솔더월별점검확인결과'

        unique_together  = [
            ['data_year', 'data_month']
        ]


class SolderViscosityCheckResult(models.Model):
    '''
    솔더점도체크결과
    '''
    id = models.AutoField(primary_key=True, db_comment="솔더점도체크 ID")
    DataDate = models.DateField('작업일', db_column="data_date")    
    StorageTemperature = models.CharField('보관규격체크', max_length=50, null=True, db_comment="Storage Temperature", db_column="storage_temp")
    AgitationCondition = models.CharField('교반조건체크', max_length=50, null=True, db_comment="Agitation Condition", db_column="agi_cond")
    CleanCheck = models.CharField('세척확인', max_length=50, null=True, db_comment="Clean Check", db_column="clean_check")

    Worker = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_comment="작업자 ID (참조키)", db_column="worker_id", null=True, related_name="visco_worker_user")
    Admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_comment="관리자 ID (참조키)", db_column="admin_id", null=True, related_name="visco_admin_user")
    TeamLeader = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_comment="팀장 ID (참조키)", db_column="team_leader_id", null=True, related_name="visco_teamleader_user")
    Description = models.TextField('비고', null=True)

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

    class Meta():
        db_table = 'visco_chk_result'
        verbose_name = '솔더점도체크결과'
        db_table_comment = '솔더점도체크결과 테이블'

        unique_together  = [
            ['DataDate']
        ]

class SolderViscosityCheckItem(models.Model):
    id = models.AutoField(primary_key=True, db_comment="솔더점도체크아이템 ID")
    DataDate = models.DateField('작업일', db_column="data_date")

    Material = models.ForeignKey(Material, on_delete=models.DO_NOTHING, db_comment="품목 ID (참조키)", db_column="mat_pk", null=True)
    mat_cd = models.CharField('mat_cd', max_length=100, null=True, db_comment="품목 코드", db_column="mat_cd")
    lot_no = models.CharField('lot_no', max_length=50, null=True, db_comment="Lot No", db_column="lot_no")
    serial_no = models.CharField('serial_no', max_length=50, null=True, db_comment="Lot No", db_column="serial_no")
    InDate = models.CharField('입고일자', null=True, max_length=10, db_comment="입고일자", db_column="in_date")
    ExpirationDate = models.CharField('만료일자', max_length=10, null=True, db_comment="만료일자", db_column="exp_date")
    RefrigeratorInDate = models.CharField("냉장고입고일자",  max_length=20, db_comment="냉장고입고일자", db_column="refr_in_date", null=True)
    viscometer = models.CharField('viscometer', max_length=50, null=True, db_comment="viscometer", db_column="viscometer")    
    ViscosityValue = models.DecimalField('점도값', decimal_places=3, max_digits=10, null=True, db_column="visc_value", db_comment="Viscosity Value")

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


    class Meta():
        db_table = 'visco_chk_item'
        verbose_name = '솔더점도체크항목결과'
        db_table_comment = '솔더점도체크항목결과테이블'



class TensionCheckResult(models.Model):
    '''
    텐션체크
    '''
    id = models.AutoField(primary_key=True, db_comment="텐션체크 ID")
    line_cd = models.CharField('라인코드', max_length=20)
    DataDate = models.DateTimeField('측정일', db_column="data_date")
    Barcode = models.CharField('Barcode', max_length=500, null=True, db_comment="Barcode", db_column="barcode")
    #prod_plan_pk = models.IntegerField("생산계획번호", null=True, db_comment="생산계획번호", db_column='prod_plan_pk')
    TensionValue1 = models.DecimalField('TensionValue1', decimal_places=2, max_digits=10, null=True, db_column="tension_value1", db_comment="Tension Value 1")
    TensionValue2 = models.DecimalField('TensionValue2', decimal_places=2, max_digits=10, null=True, db_column="tension_value2", db_comment="Tension Value 2")
    TensionValue3 = models.DecimalField('TensionValue3', decimal_places=2, max_digits=10, null=True, db_column="tension_value3", db_comment="Tension Value 3")
    TensionValue4 = models.DecimalField('TensionValue4', decimal_places=2, max_digits=10, null=True, db_column="tension_value4", db_comment="Tension Value 4")
    TensionValue5 = models.DecimalField('TensionValue5', decimal_places=2, max_digits=10, null=True, db_column="tension_value5", db_comment="Tension Value 5")
    Result = models.CharField('Result', max_length=50, null=True, db_comment="Result")
    Worker = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_comment="작업자 ID (참조키)", db_column="worker_id", null=True)
    DefectReason = models.TextField('불량사유', null=True, db_comment="Defect Reason", db_column="defect_reason")

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'ten_chk_result'
        verbose_name = '텐션체크결과'
        db_table_comment = 'SMT텐션체크결과'
        indexes = [ 
            models.Index(fields=['DataDate',"line_cd"], name='idx_tenchkresultdatadatalinecd')
        ]


class MounterInstace(models.Model):
    '''
    마운터 설비의  HEAD, FEEDER, PRV 까지는 kmms에 등록하고 , 정비부품은 
    '''
    id = models.AutoField(primary_key=True, db_comment="마운터정보관리PK")
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    equ_type = models.CharField(db_comment="마운터설비데이터구분,", max_length=20, db_column="equ_type", default='head') # head, feeder, prv
    head_type = models.CharField(db_comment="헤드타입", max_length=20, db_column="head_type", null=True, blank=True) # CPP, C&P20P, TWIN
    sn = models.CharField(db_comment="마운터하위설비시리얼번호", max_length=200, db_column="sn")
    manufacturer = models.CharField(db_comment="제조사", max_length=100, db_column="manufacturer", null=True, blank=True) # ASM, FUJI
    registered_dt = models.DateField(db_comment="등록일시", db_column="registered_dt", null=True, blank=True)
    retired_dt = models.DateField(db_comment="폐기일시", db_column="retired_dt", null=True, blank=True)
    description = models.CharField(db_comment="설명", max_length=500, db_column="description", null=True, blank=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)

    def set_audit(self, user : User):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return


    class Meta():
        db_table = 'mnt_instance'
        verbose_name = '마운터하위설비정보'
        db_table_comment = '마운터하위설비정보'

        unique_together  = [
            ['CmEquipment', 'sn']
        ]

    class MounterUseageHistory(models.Model):
        '''
        마운터 사용이력
        '''
        id = models.AutoField(primary_key=True, db_comment="마운터사용이력PK")
        Parent = models.ForeignKey('MounterInstace', models.DO_NOTHING, related_name="parent_mounter_instance_useage",  db_column='parent_id', db_comment='마운터설비PK', null=True)
        Instace = models.ForeignKey('MounterInstace', models.DO_NOTHING, related_name="mounter_instance_useage", db_column='instance_id', db_comment='마운터설비PK')
        mounted_at  = models.DateField(db_comment="사용일시", db_column="mounted_at", null=True, blank=True)
        unmouned_at = models.DateField(db_comment="사용종료일시", db_column="unmouned_at", null=True, blank=True)
        description = models.CharField(db_comment="사용종료설명", max_length=2000, db_column="description", null=True, blank=True)

        _status = models.CharField('_status', max_length=10, null=True)
        _created    = models.DateTimeField('_created', auto_now_add=True)
        _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
        _creater_id = models.IntegerField('_creater_id', null=True)
        _modifier_id = models.IntegerField('_modifier_id', null=True)

        def set_audit(self, user : User):
            if self._creater_id is None:
                self._creater_id = user.id
            self._modifier_id = user.id
            self._modified = DateUtil.get_current_datetime()
            return


        class Meta:
            db_table = 'mnt_use_history'
            verbose_name = '마운터사용이력'
            db_table_comment = '마운터사용이력'