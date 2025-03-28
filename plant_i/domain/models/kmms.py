from tarfile import NUL
from django.db import models
from domain.models.definition import Equipment, Material, Site, Unit
from domain.models.user import Depart
from django.contrib.auth.models import User
from domain.services.date import DateUtil
from datetime import datetime

class JobClass(models.Model):
    '''
    직종
    '''
    job_class_pk = models.AutoField(primary_key=True, db_column='job_class_pk', db_comment='직종 PK')
    Code = models.CharField('직종코드', db_column='cd', max_length=20, db_comment='직종 코드')
    Name = models.CharField('직종명', db_column='nm', max_length=100, db_comment='직종 이름')
    WageCost = models.DecimalField('인건비단가', db_column='wage_cost', max_digits=10, decimal_places=3, null=True, db_comment='인건비 단가')
    UseYN = models.CharField('사용여부', db_column='use_yn', max_length=1, default='Y', db_comment='사용 여부')
    DeleteYN = models.CharField('삭제여부', db_column='del_yn', max_length=1, default='N', db_comment='삭제 여부')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'job_class'
        verbose_name = '직종'
        db_table_comment = '직종 정보'
        unique_together = [
            ['Code']
        ]        
        
class Project(models.Model):
    '''
    프로젝트
    '''
    proj_pk = models.AutoField(primary_key=True, db_column='proj_pk', db_comment='프로젝트 PK')
    proj_cd = models.CharField('프로젝트코드', db_column='proj_cd', max_length=30, db_comment='프로젝트코드')
    proj_nm = models.CharField('프로젝트명', db_column='proj_nm', max_length=200, db_comment='프로젝트명')
    plan_start_dt = models.DateField('계획 시작일', db_column='plan_start_dt', db_comment='계획 시작일')
    plan_end_dt = models.DateField('계획 마감일', db_column='plan_end_dt', db_comment='계획 마감일')
    manager_id = models.CharField('담당자PK', db_column='manager_id', max_length=20, db_comment='담당자PK')
    proj_purpose = models.CharField('설명', db_column='proj_purpose', max_length=400, db_comment='설명')
    proj_tot_cost = models.IntegerField('중요성', db_column='proj_tot_cost', db_comment='중요성')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created    = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정일시')
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'project'
        verbose_name = '프로젝트'
        db_table_comment = '프로젝트 정보'
        unique_together = [
            ['proj_cd']
        ]

class PreventiveMaintenance(models.Model):
    '''
    PM마스터
    '''
    pm_pk = models.AutoField(primary_key=True, db_comment='예방보전 PK')
    pm_no = models.CharField('PM번호', db_column='pm_no', max_length=20, db_comment='예방보전 번호')
    Name = models.CharField('PM명', db_column='pm_nm', max_length=100, db_comment='예방보전 명')
    PMSortNo = models.SmallIntegerField('PM번호순번', db_column='pm_sort_no', null=True, db_comment='예방보전 번호순번')
    Equipment = models.ForeignKey(Equipment, db_column='equip_pk', on_delete=models.DO_NOTHING, db_comment='설비 ID')
    Depart = models.ForeignKey(Depart, db_column='dept_pk', on_delete=models.DO_NOTHING, db_comment='부서 ID')
    PMUser = models.ForeignKey(User, db_column='pm_user_pk', on_delete=models.DO_NOTHING, db_comment='예방보전 담당자 ID')
    CycleType = models.CharField('주기단위', db_column='cycle_type', max_length=100, null=True, db_comment='주기단위')
    CyclePerNumber = models.IntegerField('PM주기별번호', db_column='per_number', null=True, db_comment='예방보전 주기별번호')
    ScheduleStartDate = models.DateField('주기시작일', db_column='sched_start_dt', null=True, db_comment='주기시작일')
    FirstWorkDate = models.DateField('최초PM생성일', db_column='first_work_dt', null=True, db_comment='최초 예방보전 생성일')
    LastWorkDate = models.DateField('최종PM생성일', db_column='last_work_dt', null=True, db_comment='최종 예방보전 생성일')
    NextCheckDate = models.DateField('다음주기일', db_column='next_chk_date', null=True, db_comment='다음 주기일')
    WorkText = models.CharField('작업지침', db_column='work_text', max_length=2000, db_comment='작업지침')
    WorkExpectHour = models.IntegerField('정비예상시간', db_column='work_expect_hr', null=True, db_comment='정비 예상시간')
    PMType = models.CharField('PM유형', db_column='pm_type', max_length=20, db_comment='예방보전 유형')
    UseYN = models.CharField('사용여부', db_column='use_yn', default='Y', db_comment='사용 여부')
    DeleteYN = models.CharField('삭제여부', db_column='del_yn', default='N', db_comment='삭제 여부')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created    = models.DateTimeField('_created', auto_now_add=True, db_comment='생성일시')
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정일시')
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
        db_table = 'pm'
        verbose_name = 'PM마스터'
        db_table_comment = 'PM마스터 정보'
        unique_together = [
            ['pm_no'],
            ['Name'],
        ]

class PMWorker(models.Model):
    '''
    PM작업자 
    '''
    id = models.AutoField(primary_key=True, db_comment='PM작업자 PK')
    PreventiveMaintenance = models.ForeignKey(PreventiveMaintenance, db_column='pm_pk', on_delete=models.DO_NOTHING, db_comment='예방보전 PK')
    JobClass = models.ForeignKey(JobClass, db_column='job_class_pk', on_delete=models.DO_NOTHING, db_comment='직종 PK')
    WorkHour = models.DecimalField('작업시간', db_column='work_hr', max_digits=7, decimal_places=2, null=True, db_comment='작업 시간')
    DisplayOrder = models.SmallIntegerField('표시순서', db_column='disp_order', null=True, db_comment='표시 순서')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'pm_labor'
        verbose_name = 'PM인력'
        db_table_comment = 'PM작업자 정보'
        index_together = [
            ['PreventiveMaintenance']
        ]

class PMMaterial(models.Model):
    '''
    PM소요자재
    '''
    id = models.AutoField(primary_key=True, db_comment='PM소요자재 PK')
    PreventiveMaintenance = models.ForeignKey(PreventiveMaintenance, db_column='pm_pk', on_delete=models.DO_NOTHING, db_comment='예방보전 PK')
    Material = models.ForeignKey(Material, db_column='mat_pk', on_delete=models.DO_NOTHING, db_comment='자재 PK')
    Amount = models.DecimalField('소요량', db_column='amt', max_digits=13, decimal_places=3, db_comment='소요량')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'pm_mtrl'
        verbose_name = 'PM자재'
        db_table_comment = 'PM소요자재 정보'
        unique_together = [
            ['PreventiveMaintenance','Material']
        ]
        index_together = [
            ['PreventiveMaintenance']
        ]

class CheckMaster(models.Model):
    '''
    점검마스터
    '''
    check_pk = models.AutoField(primary_key=True, db_column='chk_pk', db_comment='점검 PK')
    check_no = models.CharField('점검번호', db_column='chk_no', max_length=20, db_comment='점검 번호')
    CheckName = models.CharField('점검명', db_column='chk_name', max_length=100, db_comment='점검 이름')
    Depart = models.ForeignKey(Depart, verbose_name='점검부서', db_column='dept_pk', on_delete=models.DO_NOTHING, null=True, db_comment='점검 부서 ID')
    CheckUser = models.ForeignKey(User, verbose_name='점검담당자', db_column='chk_user_id', on_delete=models.DO_NOTHING, null=True, db_comment='점검 담당자 ID')
    CheckYN = models.CharField('점검여부', db_column='chk_yn', max_length=1, default='N', db_comment='점검 여부')
    CycleType = models.CharField('주기유형', db_column='cycle_type', max_length=100, null=True, db_comment='주기 유형')
    CyclePerNumber = models.IntegerField('점검주기별번호', db_column='per_number', null=True, db_comment='점검 주기별 번호')
    ScheduleStartDate = models.DateField('주기시작일', db_column='sched_start_dt', null=True, db_comment='주기 시작일')
    FirstWorkDate = models.DateField('최초점검생성일', db_column='first_work_dt', null=True, db_comment='최초 점검 생성일')
    LasttWorkDate = models.DateField('최종점검생성일', db_column='last_work_dt', null=True, db_comment='최종 점검 생성일')
    NexttCheckDate = models.DateField('다음주기일', db_column='next_chk_date', null=True, db_comment='다음 주기일')
    WorkText = models.CharField('작업지침', db_column='work_text', max_length=2000, db_comment='작업 지침')
    WorkExpectHour = models.IntegerField('정비예상시간', db_column='work_expect_hr', null=True, db_comment='정비 예상시간')
    CheckType = models.CharField('점검유형', db_column='check_type', max_length=20, db_comment='점검 유형')
    UseYN = models.CharField('사용여부', db_column='use_yn', default='Y', db_comment='사용 여부')
    DeleteYN = models.CharField('삭제여부', db_column='del_yn', default='N', db_comment='삭제 여부')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'chk_mst'
        verbose_name = '점검마스터'
        db_table_comment = '점검마스터 정보'
        index_together = [
            ['check_no']
        ]

class CheckEquip(models.Model):
    '''
    점검별 설비
    '''
    chk_mast_pk = models.OneToOneField(CheckMaster, primary_key=True, db_column='chk_mast_pk', on_delete=models.DO_NOTHING, db_comment="점검마스터 기본키")
    Equipment = models.ForeignKey(Equipment, db_column='equip_pk', on_delete=models.DO_NOTHING,db_comment="설비기본키")

    class Meta:
        db_table = 'chk_equip'
        verbose_name = '점검별 설비'
        db_table_comment = '점검별 설비 매칭테이블'

class CheckItem(models.Model):
    '''
    점검항목
    '''
    Check_item_pk = models.AutoField(primary_key=True, db_column='check_item_pk', db_comment='점검항목 기본키')
    CheckMaster = models.ForeignKey(CheckMaster, verbose_name='점검마스터', db_column='chk_pk', on_delete=models.DO_NOTHING, db_comment='점검 마스터(FK)')
    ItemIndex = models.SmallIntegerField('점검항목순번', db_column='item_index', db_comment='점검 항목 순번')
    ItemName = models.CharField('점검항목명', db_column='item_name', max_length=100, db_comment='점검 항목명')
    LCL = models.DecimalField('하한값', db_column='lcl', max_digits=13, decimal_places=3, null=True, db_comment='점검 항목 하한값')
    UCL = models.DecimalField('상한값', db_column='ucl', max_digits=13, decimal_places=3, null=True, db_comment='점검 항목 상한값')
    Unit = models.ForeignKey(Unit, verbose_name='단위', db_column='unit_id', on_delete=models.DO_NOTHING, null=True, db_comment='단위 ID (FK)')
    Method = models.CharField('점검방법', db_column='method', max_length=100, null=True, db_comment='점검 방법')
    Guide = models.CharField('점검가이드', db_column='guide', max_length=2000, null=True, db_comment='점검 가이드')
    
    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='데이터 생성일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='데이터 수정일시')
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

    class Meta:
        db_table = 'chk_item'
        verbose_name = '점검항목'
        db_table_comment = '점검항목'

class CheckSchedule(models.Model):
    '''
    점검일정
    '''
    check_sch_pk = models.AutoField(primary_key=True, db_column='chk_sch_pk', db_comment='점검일정PK')
    check_sch_no = models.IntegerField('점검일정번호', db_column='chk_sch_no', db_comment='점검일정번호')
    CheckMaster = models.ForeignKey(CheckMaster, verbose_name='점검마스터', db_column='chk_mast_pk', on_delete=models.DO_NOTHING, db_comment='점검마스터PK')
    Depart = models.ForeignKey(Depart, verbose_name='점검부서', db_column='dept_pk', on_delete=models.DO_NOTHING, null=True, db_comment='점검부서')
    CheckScheduleDate = models.DateField('점검예정일', db_column='chk_sch_dt', db_comment='점검예정일')
    CheckStatus = models.CharField('점검상태', db_column='chk_status', max_length=1, default='N', db_comment='점검상태')
    CheckUser = models.ForeignKey(User, db_column='chk_user_id', verbose_name='점검담당자', on_delete=models.DO_NOTHING, null=True, db_comment='점검담당자')
    CheckDate = models.DateField('점검일', db_column='chk_dt', null=True, db_comment='점검일')
    FileGroupCode = models.CharField('파일그룹코드', db_column='file_grp_cd', max_length=20, null=True, db_comment='파일그룹코드')
    CheckRequestType = models.CharField('점검생성유형', db_column='chk_req_type', max_length=20, null=True, db_comment='점검생성유형')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'chk_sch'
        db_table_comment = '점검 일정'
        verbose_name = '점검일정'

        unique_together = [
            ['check_sch_no']
        ]

class CheckScheduleItem(models.Model):
    '''
    점검일정별 항목
    '''
    id = models.AutoField(primary_key=True, db_comment='점검일정별 항목 PK')
    CheckSchedule = models.ForeignKey(CheckSchedule, verbose_name='점검일정', db_column='chk_sch_pk', on_delete=models.DO_NOTHING, db_comment='점검일정PK')
    CheckItem = models.ForeignKey(CheckItem, verbose_name='점검항목', db_column='chk_item_pk', on_delete=models.DO_NOTHING, db_comment='점검항목PK')
    ItemName = models.CharField('점검항목명', db_column='chk_item_nm', max_length=200, db_comment='점검항목명')
    ItemIndex = models.SmallIntegerField('점검항목순번', db_column='item_idx', db_comment='순번')
    LCL = models.CharField('LCL', db_column='lcl', max_length=30, null=True, db_comment='하한값')
    UCL = models.CharField('UCL', db_column='ucl', max_length=30, null=True, db_comment='상한값')
    Unit = models.ForeignKey(Unit, verbose_name='단위', db_column='chk_item_unit_pk', on_delete=models.DO_NOTHING, null=True, db_comment='단위')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'chk_sch_item'
        db_table_comment = '점검 일정별 항목'
        verbose_name = '점검일정별 항목'

        unique_together = [
            ['CheckSchedule', 'CheckItem']
        ]

        index_together = [
            ['CheckSchedule']
        ]

class CheckResult(models.Model):
    '''
    점검결과
    '''
    check_result_pk = models.AutoField(primary_key=True, db_column='chk_rslt_pk', db_comment='점검결과PK')
    CheckSchedule = models.ForeignKey(CheckSchedule, verbose_name='점검일정', db_column='chk_sch_pk', on_delete=models.DO_NOTHING, db_comment='점검일정PK')
    Equipment = models.ForeignKey(Equipment, verbose_name='설비', db_column='equip_pk', on_delete=models.DO_NOTHING, db_comment='설비PK')
    Result = models.CharField('결과', db_column='result', max_length=1, null=True, db_comment='점검결과 (정상/이상)')
    Description = models.CharField('비고', db_column='description', max_length=2000, null=True, db_comment='비고')

    CheckRequestType = models.CharField('점검생성유형', db_column='chk_req_type', max_length=20, null=True, db_comment='점검생성유형')
    CheckItemTotal = models.SmallIntegerField('점검항목총수', db_column='chk_item_tot', null=True, db_comment='점검항목 총 개수')
    AbnormalItemCount = models.SmallIntegerField('이상항목수', db_column='abn_item_cnt', null=True, db_comment='이상 점검 항목 수')
    FileGroupCode = models.CharField('파일그룹코드', db_column='file_grp_cd', max_length=20, null=True, db_comment='첨부 파일 그룹 코드')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'chk_result'
        db_table_comment = '점검 결과'
        verbose_name = '점검결과'

        index_together = [
            ['CheckSchedule', 'Equipment'],
            ['CheckSchedule'],
            ['Equipment']
        ]

class CheckResultItem(models.Model):
    '''
    점검결과별 항목결과
    '''
    id = models.AutoField(primary_key=True, db_comment='점검결과별 항목결과 PK')
    CheckResult = models.ForeignKey(CheckResult, verbose_name='점검결과', db_column='chk_rslt_pk', on_delete=models.DO_NOTHING, db_comment='점검결과PK')
    CheckSchedule = models.ForeignKey(CheckSchedule, verbose_name='점검일정', db_column='chk_sch_pk', on_delete=models.DO_NOTHING, db_comment='점검일정PK')
    CheckItem = models.ForeignKey(CheckItem, verbose_name='점검항목', db_column='chk_item_pk', on_delete=models.DO_NOTHING, db_comment='점검항목PK')
    Result = models.CharField('결과', db_column='result', max_length=1, null=True, db_comment='점검결과 (정상/이상)')
    Description = models.CharField('비고', db_column='description', max_length=2000, null=True, db_comment='비고')
    CheckUser = models.ForeignKey(User, db_column='chk_user_id', verbose_name='점검담당자', on_delete=models.DO_NOTHING, null=True, db_comment='점검 담당자')
    CheckDate = models.DateField('점검일', db_column='chk_dt', null=True, db_comment='점검일')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modfied', auto_now=True, null=True, db_comment='수정 일시')
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
        db_table = 'chk_item_result'
        db_table_comment = '점검 결과별 항목 결과'
        verbose_name = '점검결과별 항목결과'

        index_together = [
            ['CheckResult', 'CheckSchedule'],
        ]
        unique_together = [
            ['CheckSchedule', 'CheckItem']
        ]

class WorkOrder(models.Model):
    '''
    작업지시
    '''
    work_order_pk = models.AutoField(primary_key=True, db_column='work_order_pk', db_comment='작업지시 PK')
    work_order_no = models.CharField('작업지시서번호', db_column='work_order_no', max_length=40, db_comment='작업지시서 번호')
    wo_status = models.CharField('작업상태', db_column='wo_status', max_length=20, db_comment='작업 상태')
    work_title = models.CharField('작업제목', db_column='work_title', max_length=200, db_comment='작업 제목')
    Equipment = models.ForeignKey(Equipment, db_column='equip_pk', on_delete=models.DO_NOTHING, db_comment='설비 ID')
    wo_type = models.CharField('작업유형', db_column='wo_type', max_length=20, null=True, db_comment='작업 유형')
    MaintenanceTypeCode = models.CharField('보전유형', db_column='maint_type_cd', max_length=20, default='CM', null=True, db_comment='보전 유형 코드')
    RequestDepart = models.ForeignKey(Depart, verbose_name='요청부서', db_column='req_dept_pk', on_delete=models.DO_NOTHING, null=True, related_name='workorder_request_depart', db_comment='요청 부서 ID')
    RequestInfo = models.TextField('요청내역', db_column='req_info', null=True, db_comment='요청 내역')
    RequestFileGroupCode = models.CharField('요청내역사진파일코드', db_column='req_file_grp_cd', max_length=50, null=True, db_comment='요청내역 사진파일 그룹코드')
    WantDate = models.DateField('희망일', db_column='want_dt', null=True, db_comment='작업 희망일')
    BreakdownDate = models.DateField('고장일시', db_column='breakdown_dt', null=True, db_comment='고장 발생일시')
    BreakdownHour = models.DecimalField('고장시간', db_column='breakdown_hr', max_digits=10, decimal_places=2, null=True, db_comment='고장 시간')
    ProblemCode = models.CharField('현상코드', db_column='problem_cd', max_length=8, null=True, db_comment='문제 현상 코드')
    CauseCode = models.CharField('원인코드', db_column='cause_cd', max_length=8, null=True, db_comment='원인 코드')
    RemedyCode = models.CharField('조치코드', db_column='remedy_cd', max_length=8, null=True, db_comment='조치 코드')
    plan_start_dt = models.DateField('계획시작일', db_column='plan_start_dt', null=True, db_comment='계획 시작일')
    plan_end_dt = models.DateField('계획완료일', db_column='plan_end_dt', null=True, db_comment='계획 완료일')
    start_dt = models.DateField('작업시작일시', db_column='start_dt', null=True, db_comment='작업 시작일시')
    end_dt = models.DateField('작업종료일시', db_column='end_dt', null=True, db_comment='작업 종료일시')
    WorkDepart = models.ForeignKey(Depart, verbose_name='작업부서PK', db_column='dept_pk', on_delete=models.DO_NOTHING, null=True, related_name='workorder_work_depart', db_comment='작업 부서 ID')
    WorkCharger = models.ForeignKey(User, verbose_name='작업담당자PK', db_column='work_charger_pk', on_delete=models.DO_NOTHING, null=True, db_comment='작업 담당자 ID')
    WorkText = models.TextField('작업내역', db_column='work_text', null=True, db_comment='작업 내역')
    WorkFileGroupCode = models.CharField('작업내역사진파일코드', db_column='work_file_grp_cd', max_length=50, null=True, db_comment='작업내역 사진파일 그룹코드')
    WorkSourcingCode = models.CharField('작업소싱 코드', db_column='work_src_cd', max_length=20, default='WS01', null=True, db_comment='작업 소싱 코드')
    TotalCost = models.DecimalField('총작업비용', db_column='tot_cost', max_digits=10, decimal_places=2, null=True, db_comment='총 작업비용')
    MaterialCost = models.DecimalField('자재비', db_column='mtrl_cost', max_digits=10, decimal_places=2, null=True, db_comment='자재 비용')
    LaborCost = models.DecimalField('인건비', db_column='labor_cost', max_digits=10, decimal_places=2, null=True, db_comment='인건비')
    OutSourcingCost = models.DecimalField('외주비', db_column='outsourcing_cost', max_digits=10, decimal_places=2, null=True, db_comment='외주 비용')
    EtcCost = models.DecimalField('기타비용', db_column='etc_cost', max_digits=10, decimal_places=2, null=True, db_comment='기타 비용')
    PreventiveMaintenance = models.ForeignKey(PreventiveMaintenance, verbose_name='PM ID', db_column='pm_pk', on_delete=models.DO_NOTHING, null=True, db_comment='예방정비 ID')
    PMRequestType = models.CharField('PM의뢰유형', db_column='pm_req_type', max_length=1, default='A', db_comment='예방정비 의뢰유형')
    WorkOrderSort = models.IntegerField('작업지시번호소팅용', db_column='work_order_sort', null=True, db_comment='작업지시 번호 정렬용')
    rqst_insp_yn = models.CharField('점검WO 여부', db_column='rqst_insp_yn', max_length=1, default='N', db_comment='점검 작업지시 여부')
    rqst_dpr_yn = models.CharField('일보WO 여부', db_column='rqst_dpr_yn', max_length=1, default='N', db_comment='일보 작업지시 여부')
    WorkFileGroupCode = models.CharField('첨부파일그룹코드', db_column='wo_file_grp_cd', max_length=50, null=True, db_comment='첨부파일 그룹코드')
    CheckResult = models.ForeignKey(CheckResult, verbose_name='점검결과', db_column='chk_rslt_pk', on_delete=models.DO_NOTHING, null=True, db_comment='점검결과 ID')
    site_id = models.IntegerField('사이트ID', db_column='site_id', null=True, db_comment='사이트 ID')
    WorkOrderApproval = models.ForeignKey('WorkOrderApproval', db_column='work_order_approval_pk', on_delete=models.DO_NOTHING, db_comment='작업결재정보PK', null=True)
    
    # 새로운 필드 추가
    appr_line = models.CharField('결재라인', db_column='appr_line', max_length=50, null=True, default='', db_comment='결재라인')
    appr_line_next = models.CharField('다음결재라인', db_column='appr_line_next', max_length=10, null=True, default='', db_comment='다음결재라인')
    proj_cd = models.CharField('프로젝트코드', db_column='proj_cd', max_length=30, null=True, db_comment='프로젝트 코드')

    _status = models.CharField('_status', max_length=10, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment='수정 일시')
    _creater_id = models.IntegerField('_creater_id', db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment='수정자 ID')
    _creater_nm = models.CharField('_creater_nm', max_length=50, null=True, db_comment='생성자 이름')
    _modifier_nm = models.CharField('_modifier_nm', max_length=50, null=True, db_comment='수정자 이름')

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'work_order'
        db_table_comment = '작업지시 정보'
        verbose_name = '작업지시'
        unique_together = [
            ['work_order_no']
        ]
        index_together = [
            ['Equipment']
        ]

class WorkOrderApproval(models.Model):
    '''
    작업지시 결재 정보
    '''
    work_order_approval_pk = models.AutoField(primary_key=True, db_column='work_order_approval_pk', db_comment='작업결재정보 PK')    
    rqst_user_pk = models.SmallIntegerField('요청자PK', db_column='rqst_user_pk', null=True, db_comment='요청자 PK')
    rqst_user_nm = models.CharField('요청자명', db_column='rqst_user_nm', max_length=50, null=True, db_comment='요청자 이름')
    rqst_dt = models.DateTimeField('요청일시', db_column='rqst_dt', null=True, db_comment='요청 일시')
    accept_user_pk = models.SmallIntegerField('접수자PK', db_column='accept_user_pk', null=True, db_comment='접수자 PK')
    accept_user_nm = models.CharField('접수자명', db_column='accept_user_nm', max_length=50, null=True, db_comment='접수자 이름')
    accept_dt = models.DateTimeField('접수일시', db_column='accept_dt', null=True, db_comment='접수 일시')
    appr_user_pk = models.SmallIntegerField('승인자PK', db_column='appr_user_pk', null=True, db_comment='승인자 PK')
    appr_user_nm = models.CharField('승인자명', db_column='appr_user_nm', max_length=50, null=True, db_comment='승인자 이름')
    appr_dt = models.DateTimeField('승인일시', db_column='appr_dt', null=True, db_comment='승인 일시')
    cancel_user_pk = models.SmallIntegerField('취소자PK', db_column='cancel_user_pk', null=True, db_comment='취소자 PK')
    cancel_user_nm = models.CharField('취소자명', db_column='cancel_user_nm', max_length=50, null=True, db_comment='취소자 이름')
    cancel_dt = models.DateTimeField('취소일시', db_column='cancel_dt', null=True, db_comment='취소 일시')
    cancel_reason = models.CharField('취소사유', db_column='cancel_reason', max_length=500, null=True, db_comment='취소 사유')
    reject_user_pk = models.SmallIntegerField('반려자PK', db_column='reject_user_pk', null=True, db_comment='반려자 PK')
    reject_user_nm = models.CharField('반려자명', db_column='reject_user_nm', max_length=50, null=True, db_comment='반려자 이름')
    reject_dt = models.DateTimeField('반려일시', db_column='reject_dt', null=True, db_comment='반려 일시')
    reject_reason = models.CharField('반려사유', db_column='reject_reason', max_length=500, null=True, db_comment='반려 사유')
    wo_status = models.CharField('작업상태', db_column='wo_status', max_length=20, default='DRAFT', db_comment='작업 상태')
    reg_user_pk = models.SmallIntegerField('등록자PK', db_column='reg_user_pk', null=True, db_comment='등록자 PK')
    reg_user_nm = models.CharField('등록자명', db_column='reg_user_nm', max_length=100, null=True, db_comment='등록자 이름')
    reg_dt = models.DateTimeField('등록일시', db_column='reg_dt', auto_now_add=True, db_comment='등록 일시')
    finish_user_pk = models.SmallIntegerField('완료자PK', db_column='finish_user_pk', null=True, db_comment='완료자 PK')
    finish_user_nm = models.CharField('완료자명', db_column='finish_user_nm', max_length=50, null=True, db_comment='완료자 이름')
    finish_dt = models.DateTimeField('완료일시', db_column='finish_dt', null=True, db_comment='완료 일시')
    work_finish_user_pk = models.SmallIntegerField('작업완료자PK', db_column='work_finish_user_pk', null=True, db_comment='작업 완료자 PK')
    work_finish_user_nm = models.CharField('작업완료자명', db_column='work_finish_user_nm', max_length=50, null=True, db_comment='작업 완료자 이름')
    work_finish_dt = models.DateTimeField('작업완료일시', db_column='work_finish_dt', null=True, db_comment='작업 완료 일시')

    _status = models.CharField('_status', max_length=10, null=True, db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modified', null=True, db_comment='수정 일시')
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
        db_table = 'work_order_approval'
        db_table_comment = '작업 결재정보'
        verbose_name = '작업지시 결재'

class WorkOrderMaterial(models.Model):
    '''
    작업 자재
    '''
    id = models.BigAutoField(primary_key=True)
    work_order = models.ForeignKey('WorkOrder', db_column='work_order_pk', on_delete=models.DO_NOTHING, db_comment='작업지시 PK')
    material = models.ForeignKey('Material', db_column='mtrl_pk', on_delete=models.DO_NOTHING, db_comment='자재 PK')
    unit_price = models.DecimalField('단가', db_column='unit_price', max_digits=9, decimal_places=0, db_comment='단가')
    loc_cd = models.CharField('위치코드', db_column='loc_cd', null=True,max_length=30, db_comment='위치 코드')
    own_dept_cd = models.CharField('소유부서코드', null=True,db_column='own_dept_cd', max_length=20, db_comment='소유 부서 코드')
    ab_grade = models.CharField('등급', db_column='ab_grade',null=True, max_length=10, db_comment='A/B 등급')
    plan_amt = models.SmallIntegerField('계획수량', null=True,db_column='plan_amt', db_comment='계획 수량')
    a_amt = models.SmallIntegerField('A등급 사용량', null=True,db_column='a_amt', db_comment='A등급 사용량')
    b_amt = models.SmallIntegerField('B등급 사용량', null=True,db_column='b_amt', db_comment='B등급 사용량')
    
    _status = models.CharField('_status', max_length=10, null=True,db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _modified = models.DateTimeField('_modified', null=True,auto_now=True, db_comment='수정 일시')
    _creater_id = models.IntegerField('_creater_id', null=True,db_comment='생성자 ID')
    _modifier_id = models.IntegerField('_modifier_id', null=True,db_comment='수정자 ID')
    _creater_nm = models.CharField('_creater_nm', null=True,max_length=50, db_comment='생성자 이름')
    _modifier_nm = models.CharField('_modifier_nm', null=True, max_length=50, db_comment='수정자 이름')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return
    
    class Meta:
        db_table = 'wo_mtrl'
        db_table_comment = '작업 자재'
        verbose_name = '작업 자재'

class WorkOrderHistory(models.Model):
    '''
    작업지시 이력
    '''
    id = models.BigAutoField(primary_key=True)
    work_order = models.ForeignKey('WorkOrder', db_column='work_order_pk', on_delete=models.DO_NOTHING, db_comment='작업지시 PK')
    before_status = models.CharField('이전 상태', db_column='before_status', max_length=20, db_comment='이전 작업 상태')
    after_status = models.CharField('변경 후 상태', db_column='after_status', max_length=20, null=True, db_comment='변경 후 작업 상태')
    change_ts = models.DateTimeField('변경 일시', db_column='change_ts', auto_now_add=True, db_comment='변경 일시')
    changer_pk = models.SmallIntegerField('변경자 PK', db_column='changer_pk', db_comment='변경자 PK')
    changer_nm = models.CharField('변경자 이름', db_column='changer_nm', max_length=100, db_comment='변경자 이름')
    change_reason = models.CharField('변경 사유', db_column='change_reason', max_length=500, null=True, db_comment='변경 사유')
    
    class Meta:
        db_table = 'work_order_hist'
        db_table_comment = '작업지시 이력'
        verbose_name = '작업지시 이력'

class WorkOrderLabor(models.Model):
    '''
    작업 인력
    '''
    id = models.AutoField(primary_key=True, db_comment='작업인력시PK')
    WorkOrder = models.ForeignKey('WorkOrder', db_column='work_order_pk', on_delete=models.DO_NOTHING, db_comment='작업지시PK')
    Equipment = models.ForeignKey('Equipment', db_column='equip_pk', null=True,on_delete=models.DO_NOTHING, db_comment='작업PK')
    JobClass = models.ForeignKey('JobClass', db_column='job_class_pk', null=True,on_delete=models.DO_NOTHING, db_comment='직종PK')
    LaborPrice = models.BigIntegerField('노임단가', db_column='labor_price', null=True,db_comment='노임단가')
    WorkerCount = models.IntegerField('인원수', db_column='worker_nos', default=1, null=True,db_comment='인원수')
    WorkHour = models.DecimalField('예상시간', db_column='work_hr', max_digits=7, null=True,decimal_places=2, db_comment='예상시간')
    RealWorkHour = models.DecimalField('실작업시간', db_column='real_work_hr', max_digits=7, null=True,decimal_places=2, db_comment='실작업시간')
    LaborDescription = models.CharField('비고', db_column='labor_dsc', max_length=100, null=True,db_comment='비고')

    class Meta:
        db_table = 'wo_labor'
        verbose_name = '작업 인력'
        db_table_comment = '작업 인력'

class FaultLocation(models.Model):
    '''
    작업 고정부위
    '''
    WorkOrder = models.ForeignKey('WorkOrder', db_column='work_order_pk', on_delete=models.DO_NOTHING, db_comment='작업지시PK')
    FaultLocationCode = models.CharField('고장개소 코드', db_column='fault_loc_cd', max_length=20, db_comment='고장개소 코드')
    FaultLocationDescription = models.CharField('고장개소 상세설명', db_column='fault_loc_desc', max_length=100, null=True, db_comment='고장개소 상세설명')
    CauseCode = models.CharField('원인 코드', db_column='cause_cd', max_length=8, db_comment='원인 코드')
    
    _status = models.CharField('_status', max_length=10, null=True,db_comment='데이터 상태')
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment='생성 일시')
    _creater_id = models.IntegerField('_creater_id', null=True,db_comment='생성자 ID')
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        
        return

    class Meta:
        db_table = 'wo_fault_loc'
        verbose_name = '작업 고정부위'
        db_table_comment = '작업 고정부위'



