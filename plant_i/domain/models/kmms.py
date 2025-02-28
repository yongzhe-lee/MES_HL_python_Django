from tarfile import NUL
from django.db import models
from domain.models.definition import Equipment, Material, Site, Unit
from domain.models.user import Depart
from django.contrib.auth.models import User
from domain.services.date import DateUtil

# 25.01.02 김하늘 추가(PM에서만 사용하는 업체) 모델 생성 보류(db에서만 테스트)
# class Supplier(models.Model):
#     '''
#     공급업체
#     '''
#     supplier_pk = models.AutoField(primary_key=True, db_column='supplier_pk')
#     Code = models.CharField('공급업체코드', db_column='supplier_cd', max_length=50)
#     Name = models.CharField('공급업체명', db_column='supplier_nm', max_length=100)
#     CEOName = models.CharField('대표자명', db_column='ceo_nm', max_length=80, null=True)
#     MainContactName = models.CharField('담당자1 이름', db_column='charger_nm', max_length=100, null=True)
#     MainContactPhone = models.CharField('담당자1 연락처', db_column='charger_tel', max_length=20, null=True)
#     SubContactName = models.CharField('담당자2 이름', db_column='charger2_nm', max_length=100, null=True)
#     SubContactPhone = models.CharField('담당자2 연락처', db_column='charger2_tel', max_length=20, null=True)
#     CompanyType = models.CharField('업체구분', db_column='comp_type', max_length=20, null=True)
#     BusinessCategory = models.CharField('업종', db_column='business_class_nm', max_length=200)
#     Description = models.CharField('비고', db_column='supplier_dsc', max_length=2000, null=True)
#     Nation = models.CharField('국가', db_column='nation', max_length=30, null=True)
#     Local = models.CharField('지역', db_column='local', max_length=30, null=True)
#     ZipCode = models.CharField('우편번호', db_column='zip_code', max_length=30, null=True)
#     Address1 = models.CharField('주소1', db_column='address1', max_length=200, null=True)
#     Address2 = models.CharField('주소2', db_column='address2', max_length=200, null=True)
#     Phone = models.CharField('전화번호', db_column='phone', max_length=30, null=True)
#     Fax = models.CharField('팩스번호', db_column='fax', max_length=30, null=True)
#     Homepage = models.CharField('홈페이지', db_column='homepage', max_length=100, null=True)
#     Email = models.CharField('이메일주소', db_column='email_addr', max_length=100, null=True)
#     Site = models.ForeignKey('Site', on_delete=models.DO_NOTHING, null=True, verbose_name='사이트')
#     UseYN = models.CharField('사용여부', db_column='use_yn', max_length=1, default='Y')
#     DeleteYN = models.CharField('삭제여부', db_column='del_yn', max_length=1, default='N')
    
#     _status = models.CharField('_status', max_length=10, null=True)
#     _created    = models.DateTimeField('_created', auto_now_add=True)
#     _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
#     _creater_id = models.IntegerField('_creater_id', null=True)
#     _modifier_id = models.IntegerField('_modifier_id', null=True)
#     _creater_nm = models.CharField('작성자명', max_length=10, null=True)
#     _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
#     def set_audit(self, user):
#         if self._creater_id is None:
#             self._creater_id = user.id
#             self._creater_nm = user.userprofile.Name
#         self._modifier_id = user.id
#         self._modifier_nm = user.userprofile.Name
#         self._modified = DateUtil.get_current_datetime()
#         return

#     class Meta:
#         db_table = 'supplier'
#         verbose_name = '공급업체'
#         unique_together = [
#             ['Code', 'Site']
#         ]        


class JobClass(models.Model):
    '''
    직종
    '''
    job_class_pk = models.AutoField(primary_key=True, db_column='job_class_pk')
    Code = models.CharField('직종코드', db_column='cd', max_length=20)
    Name = models.CharField('직종명', db_column='nm', max_length=100)
    WageCost = models.DecimalField('인건비단가', db_column='wage_cost', max_digits=10, decimal_places=3,null=True)
    UseYN = models.CharField('사용여부', db_column='use_yn', max_length=1, default='Y')
    DeleteYN = models.CharField('삭제여부', db_column='del_yn', max_length=1, default='N')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)

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
        unique_together = [
            ['Code']
        ]



class PreventiveMaintenace(models.Model):
    '''
    PM마스터
    '''
    pm_pk  = models.AutoField(primary_key=True, db_column='pm_pk')
    pm_no = models.CharField('PM번호', db_column='pm_no', max_length=20)
    Name = models.CharField('PM명', db_column='pm_name', max_length=100)
    PMSortNo = models.SmallIntegerField("PM번호소팅", db_column='pm_sort_no', null=True)
    Equipment = models.ForeignKey(Equipment, db_column='equ_id', on_delete=models.DO_NOTHING)
    Depart =  models.ForeignKey(Depart, db_column='dept_id', on_delete=models.DO_NOTHING)
    PMUser = models.ForeignKey(User, db_column='pm_user_id',  on_delete=models.DO_NOTHING)
    CycleType = models.CharField('주기단위', db_column='cycle_type' , max_length=100, null=True)
    CyclePerNumber = models.IntegerField('PM주기별번호', db_column='per_number', null=True)
    ScheduleStartDate = models.DateField('주기시작일', db_column='sch_start_dt', null=True)
    FirstWorkDate = models.DateField('최초PM생성일', db_column='first_work_dt', null=True)
    LasttWorkDate = models.DateField('최종PM생성일', db_column='last_work_dt', null=True)
    NexttCheckDate = models.DateField('다음주기일', db_column='next_chk_date', null=True)
    WorkText = models.CharField('작업지침', db_column='work_text', max_length=2000)
    WorkExpectHour = models.IntegerField('정비예상시간', db_column='work_expect_hr', null=True)
    PMType = models.CharField('PM유형', db_column='pm_type', max_length=20)
    UseYN = models.CharField('사용여부', db_column='use_yn', default='Y')
    DeleteYN = models.CharField('삭제여부', db_column='del_yn', default='N')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
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
        unique_together = [
            ['pm_no'],
            ['Name'],
        ]

class PMWorker(models.Model):
    '''
    PM작업자 
    '''
    id = models.AutoField(primary_key=True)
    PreventiveMaintenace = models.ForeignKey(PreventiveMaintenace, db_column='pm_pk', on_delete=models.DO_NOTHING)
    JobClass = models.ForeignKey(JobClass, db_column='job_class_pk', on_delete=models.DO_NOTHING)
    WorkHour = models.DecimalField('작업시간', db_column='work_hr', max_digits=7, decimal_places=2, null=True)
    DisplayOrder = models.SmallIntegerField('표시순서', db_column='disp_order', null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'pm_worker'
        verbose_name = 'PM인력'
        index_together = [
            ['PreventiveMaintenace']
        ]



class PMMaterial(models.Model):
    '''
    PM소요자재
    '''

    id = models.AutoField(primary_key=True)
    PreventiveMaintenace = models.ForeignKey(PreventiveMaintenace, db_column='pm_pk', on_delete=models.DO_NOTHING)
    Material = models.ForeignKey(Material, db_column='mat_pk', on_delete=models.DO_NOTHING)
    Amount = models.DecimalField('소요량', db_column='amt', max_digits=13, decimal_places=3)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'pm_mat'
        verbose_name = 'PM자재'
        unique_together = [
            ['PreventiveMaintenace','Material']
        ]
        index_together = [
            ['PreventiveMaintenace']
        ]



class CheckMaster(models.Model):
    '''
    점검마스터
    '''
    check_pk  = models.AutoField(primary_key=True, db_column='chk_pk')
    check_no = models.CharField('점검번호', db_column='chk_no', max_length=20)
    CheckName = models.CharField('점검명', db_column='chk_name', max_length=100)
    Depart =  models.ForeignKey(Depart, verbose_name='점검부서', db_column='dept_id', on_delete=models.DO_NOTHING, null=True)
    CheckUser = models.ForeignKey(User, verbose_name='점검담당자' ,db_column='chk_user_id',  on_delete=models.DO_NOTHING, null=True)
    CheckYN = models.CharField('점검여부', db_column='chk_yn', max_length=1, default='N')
    CycleType = models.CharField('주기유형', db_column='cycle_type' , max_length=100, null=True)
    CyclePerNumber = models.IntegerField('점검주기별번호', db_column='per_number', null=True)
    ScheduleStartDate = models.DateField('주기시작일', db_column='sch_start_dt', null=True)
    FirstWorkDate = models.DateField('최초점검생성일', db_column='first_work_dt', null=True)
    LasttWorkDate = models.DateField('최종점검생성일', db_column='last_work_dt', null=True)
    NexttCheckDate = models.DateField('다음주기일', db_column='next_chk_date', null=True)
    WorkText = models.CharField('작업지침', db_column='work_text', max_length=2000)
    WorkExpectHour = models.IntegerField('정비예상시간', db_column='work_expect_hr', null=True)
    CheckType = models.CharField('점검유형', db_column='check_type', max_length=20)
    UseYN = models.CharField('사용여부', db_column='use_yn', default='Y')
    DeleteYN = models.CharField('삭제여부', db_column='del_yn', default='N')

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
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

        index_together = [
            ['check_no']
        ]

class CheckEquip(models.Model):
    '''
    점검별 설비
    '''
    chk_mast_pk = models.OneToOneField(CheckMaster, primary_key=True, db_column='chk_mast_pk', on_delete=models.DO_NOTHING, help_text="점검 마스터 기본키 (CheckMaster와 1:1 관계)")
    Equipment = models.ForeignKey(Equipment, db_column='equip_pk', on_delete=models.DO_NOTHING,help_text="설비 기본키 (Equipment와 N:1 관계)")

    class Meta:
        db_table = 'chk_equip'
        verbose_name = '점검별 설비'
        verbose_name_plural = '점검별 설비 매칭테이블'

class CheckItem(models.Model):
    '''
    점검항목
    '''
    check_item_pk  = models.AutoField(primary_key=True, db_column='check_item_pk')
    CheckMaster = models.ForeignKey(CheckMaster, verbose_name='점검마스터', db_column='chk_pk', on_delete=models.DO_NOTHING)
    ItemIndex = models.SmallIntegerField('점검항목순번', db_column='item_index')
    ItemName = models.CharField('점검항목명', db_column='item_name', max_length=100)
    LCL = models.DecimalField('하한값', db_column='lcl', max_digits=13, decimal_places=3, null=True)
    UCL = models.DecimalField('상한값', db_column='ucl', max_digits=13, decimal_places=3, null=True)
    Unit = models.ForeignKey(Unit, verbose_name='단위', db_column='unit_id', on_delete=models.DO_NOTHING, null=True)
    Method = models.CharField('점검방법', db_column='method', max_length=100, null=True)
    Guide = models.CharField('점검가이드', db_column='guide', max_length=2000, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
            self._creater_nm = user.userprofile.Name
        self._modifier_id = user.id
        self._modifier_nm = user.userprofile.Name
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta():
        db_table = 'chk_item'
        verbose_name = '점검항목'
        index_together = [
            ['CheckMaster']
        ]


class CheckSchedule(models.Model):
    '''
    점검일정
    '''
    check_sch_pk = models.AutoField(primary_key=True, db_column='chk_sch_pk')
    check_sch_no = models.IntegerField('점검일정번호', db_column='chk_sch_no')
    CheckMaster = models.ForeignKey(CheckMaster, verbose_name='점검마스터', db_column='chk_pk', on_delete=models.DO_NOTHING)
    Depart =  models.ForeignKey(Depart, verbose_name='점검부서', db_column='dept_id', on_delete=models.DO_NOTHING, null=True)
    CheckScheduleDate = models.DateField('점검예정일', db_column='chk_sch_dt')
    CheckStatus = models.CharField('점검상태', db_column='chk_status', max_length=1, default='N')
    CheckUser = models.ForeignKey(User, db_column='chk_user_id', verbose_name='점검담당자', on_delete=models.DO_NOTHING, null=True)
    CheckDate = models.DateField('점검일', db_column='chk_dt', null=True)
    FileGroupCode = models.CharField('파일그룹코드', db_column='file_grp_cd', max_length=20, null=True)
    CheckRequestType = models.CharField('점검생성유형', db_column='chk_req_type', max_length=20, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
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
        verbose_name = '점검일정'

        unique_together = [
            ['check_sch_no']
        ]

class CheckScheduleItem(models.Model):
    '''
    점검일정별 항목
    '''
    id = models.AutoField(primary_key=True)
    CheckSchedule = models.ForeignKey(CheckSchedule, verbose_name='점검일정', db_column='chk_sch_pk', on_delete=models.DO_NOTHING)
    CheckItem = models.ForeignKey(CheckItem, verbose_name='점검항목', db_column='chk_item_pk', on_delete=models.DO_NOTHING)
    ItemName = models.CharField('점검항목명', db_column='item_name', max_length=100)
    ItemIndex = models.SmallIntegerField('점검항목순번', db_column='item_index')
    LCL = models.DecimalField('하한값', db_column='lcl', max_digits=13, decimal_places=3, null=True)
    UCL = models.DecimalField('상한값', db_column='ucl', max_digits=13, decimal_places=3, null=True)
    Unit = models.ForeignKey(Unit, verbose_name='단위', db_column='unit_id', on_delete=models.DO_NOTHING, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
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
        verbose_name = '점검일정'

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
    check_result_pk = models.AutoField(primary_key=True, db_column='chk_rslt_pk')
    CheckSchedule = models.ForeignKey(CheckSchedule, verbose_name='점검일정', db_column='chk_sch_pk', on_delete=models.DO_NOTHING)
    Equipment = models.ForeignKey(Equipment, verbose_name='설비', db_column='equ_id', on_delete=models.DO_NOTHING)
    Result = models.CharField('결과', db_column='result', max_length=1, null=True)
    Description = models.CharField('비고', db_column='description', max_length=2000, null=True)

    CheckRequestType = models.CharField('점검생성유형', db_column='chk_req_type', max_length=20, null=True)
    CheckItemTotal = models.SmallIntegerField('점검항목총수', db_column='chk_item_tot', null=True)
    AbnormalItemCount = models.SmallIntegerField('이상항목수', db_column='abn_item_cnt', null=True)
    FileGroupCode = models.CharField('파일그룹코드', db_column='file_grp_cd', max_length=20, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)
    
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
    id = models.AutoField(primary_key=True)
    CheckResult = models.ForeignKey(CheckResult, verbose_name='점검결과', db_column='chk_rslt_pk', on_delete=models.DO_NOTHING)
    CheckSchedule = models.ForeignKey(CheckSchedule, verbose_name='점검일정', db_column='chk_sch_pk', on_delete=models.DO_NOTHING)
    CheckItem = models.ForeignKey(CheckItem, verbose_name='점검항목', db_column='chk_item_pk', on_delete=models.DO_NOTHING)
    Result = models.CharField('결과', db_column='result', max_length=1, null=True)
    Description = models.CharField('비고', db_column='description', max_length=2000, null=True)
    CheckUser = models.ForeignKey(User, db_column='chk_user_id', verbose_name='점검담당자', on_delete=models.DO_NOTHING, null=True)
    CheckDate = models.DateField('점검일', db_column='chk_dt', null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True)
    _modified   = models.DateTimeField('_modfied', auto_now=True, null=True)
    _creater_id = models.IntegerField('_creater_id', null=True)
    _modifier_id = models.IntegerField('_modifier_id', null=True)
    _creater_nm = models.CharField('작성자명', max_length=10, null=True)
    _modifier_nm = models.CharField('변경자명', max_length=10, null=True)

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
    
    작업지시PK	work_order_pk				NUMERIC	9		
    작업지시서번호	work_order_no				VARCHAR	40		
    작업 상태	wo_status				VARCHAR	20		
    작업제목	work_title				VARCHAR	200		
    설비PK	equ_id				NUMERIC	7		
    작업유형	wo_type				VARCHAR	20		
    보전유형	maint_type_cd				VARCHAR	20		'CM'
    요청부서PK	req_dept_pk				NUMERIC	5		
    요청내역	req_info			Additional	CLOB			
    요청내역사진파일코드	req_info_img_grp_cd			Additional	VARCHAR	50		
    희망일	want_dt			Additional	DATE			
    고장일시	breakdown_dt				DATE			
    고장시간	breakdown_hr				NUMERIC	10	2	
    현상코드	problem_cd				VARCHAR	8		
    원인코드	cause_cd				VARCHAR	8		
    조치코드	remedy_cd				VARCHAR	8		
    계획시작일	plan_start_dt				DATE			
    계획완료일	plan_end_dt				DATE			
    작업시작일시	start_dt				DATE			
    작업종료일시	end_dt				DATE			
    작업부서PK	dept_pk				NUMERIC	5		
    작업담당자PK	work_charger_pk				NUMERIC	5		
    작업내역	work_text				CLOB			
    작업내역사진파일코드	work_text_img_grp_cd			Additional	VARCHAR	50		
    작업소싱 코드	work_src_cd				VARCHAR	20		'WS01'
    총작업비용	tot_cost				NUMERIC	10		
    자재비	mtrl_cost				NUMERIC	10		
    인건비	labor_cost				NUMERIC	10		
    외주비	outside_cost				NUMERIC	10		
    기타비용	etc_cost				NUMERIC	10		
    점검결과PK	chk_rslt_pk				NUMERIC	9		
    PM ID	pm_pk				NUMERIC	7		
    PM의뢰유형	pm_req_type			Additional	CHAR	1		'A'
    작업지시번호소팅용	work_order_sort				INTEGER			
    점검WO 여부	rqst_insp_yn				CHAR	1		'N'
    일보WO 여부	rqst_dpr_yn				CHAR	1		'N'
    결재라인	appr_line				VARCHAR	50		
    다음결재라인	appr_line_next				VARCHAR	10		
    작업결재정보PK	work_order_approval_pk				NUMERIC	9		
    첨부파일그룹코드	wo_file_grp_cd			Additional	VARCHAR	50		
    AUDIT				Pseudo				
    데이터상태	_status				VARCHAR	10		
    생성일시	_created				TIMESTAMP			now()
    생성자ID	_creater_id				INTEGER			SYSDATE
    생성자명	_creater_nm				VARCHAR	50		
    변경일시	_modified				TIMESTAMP			
    변경자ID	_modifier_id				INTEGER			
    변경자명	_modifier_nm				VARCHAR	50		
    점검항목PK	chk_item_pk				NUMERIC	9		

    '''
    work_order_pk = models.AutoField(primary_key=True, db_column='work_order_pk')
    work_order_no = models.CharField('작업지시서번호', db_column='work_order_no', max_length=40)
    wo_status = models.CharField('작업상태', db_column='wo_status', max_length=20)
    work_title = models.CharField('작업제목', db_column='work_title', max_length=200)
    Equipment = models.ForeignKey(Equipment, db_column='equ_id', on_delete=models.DO_NOTHING)
    wo_type = models.CharField('작업유형', db_column='wo_type', max_length=20, null=True)
    MaintenanceTypeCode = models.CharField('보전유형', db_column='maint_type_cd', max_length=20, default='CM', null=True)
    RequestDepart = models.ForeignKey(Depart, verbose_name='요청부서', db_column='req_dept_id', on_delete=models.DO_NOTHING, null=True, related_name='workorder_request_depart')
    RequestInfo = models.TextField('요청내역', db_column='req_info', null=True)
    RequestFileGroupCode = models.CharField('요청내역사진파일코드', db_column='req_file_grp_cd', max_length=50, null=True)
    WantDate = models.DateField('희망일', db_column='want_dt', null=True)
    BreakdownDate = models.DateField('고장일시', db_column='breakdown_dt', null=True)
    BreakdownHour = models.DecimalField('고장시간', db_column='breakdown_hr', max_digits=10, decimal_places=2, null=True)
    ProblemCode = models.CharField('현상코드', db_column='problem_cd', max_length=8, null=True)
    CauseCode = models.CharField('원인코드', db_column='cause_cd', max_length=8, null=True)
    RemedyCode = models.CharField('조치코드', db_column='remedy_cd', max_length=8, null=True)
    plan_start_dt = models.DateField('계획시작일', db_column='plan_start_dt', null=True)
    plan_end_dt = models.DateField('계획완료일', db_column='plan_end_dt', null=True)
    start_dt = models.DateField('작업시작일시', db_column='start_dt', null=True)
    end_dt = models.DateField('작업종료일시', db_column='end_dt', null=True)
    WorkDepart = models.ForeignKey(Depart, verbose_name='작업부서', db_column='work_dept_id', on_delete=models.DO_NOTHING, null=True, related_name='workorder_work_depart')
    WorkCharger = models.ForeignKey(User, verbose_name='작업담당자', db_column='work_charger_id', on_delete=models.DO_NOTHING, null=True)
    WorkText = models.TextField('작업내역', db_column='work_text', null=True)
    WorkFileGroupCoded = models.CharField('작업내역사진파일코드', db_column='work_file_grp_cd', max_length=50, null=True)
    WorkSourcingCode = models.CharField('작업소싱 코드', db_column='work_src_cd', max_length=20, default='WS01' , null=True)
    TotalCost = models.DecimalField('총작업비용', db_column='tot_cost', max_digits=10, decimal_places=2, null=True)
    MaterialCost = models.DecimalField('자재비', db_column='mtrl_cost', max_digits=10, decimal_places=2, null=True)
    LaborCost = models.DecimalField('인건비', db_column='labor_cost', max_digits=10, decimal_places=2, null=True)
    OutSourcingCost = models.DecimalField('외주비', db_column='outsourcing_cost', max_digits=10, decimal_places=2, null=True)
    EtcCost = models.DecimalField('기타비용', db_column='etc_cost', max_digits=10, decimal_places=2, null=True)
    PreventiveMaintenace = models.ForeignKey(PreventiveMaintenace, verbose_name='PM ID', db_column='pm_pk', on_delete=models.DO_NOTHING, null=True)
    PMRequestType = models.CharField('PM의뢰유형', db_column='pm_req_type', max_length=1, default='A')
    RorkOrderSort = models.IntegerField('작업지시번호소팅용', db_column='work_order_sort', null=True)
    rqst_insp_yn = models.CharField('점검WO 여부', db_column='rqst_insp_yn', max_length=1, default='N')
    rqst_dpr_yn = models.CharField('일보WO 여부', db_column='rqst_dpr_yn', max_length=1, default='N')
    WorkFileGroupCode = models.CharField('첨부파일그룹코드', db_column='wo_file_grp_cd', max_length=50, null=True)
    CheckResult = models.ForeignKey(CheckResult, verbose_name='점검결과', db_column='chk_result_pk', on_delete=models.DO_NOTHING, null=True)

    #appr_line = models.CharField('결재라인', db_column='appr_line', max_length=50, null=True)
    #appr_line_next = models.CharField('다음결재라인', db_column='appr_line_next', max_length=10, null=True)
    #approval_id = models.IntegerField('작업결재정보PK', db_column='approval_id', null=True)

    _status = models.CharField('_status', max_length=10)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modified', auto_now=True)
    _creater_id = models.IntegerField('_creater_id')
    _modifier_id = models.IntegerField('_modifier_id')
    _creater_nm = models.CharField('_creater_nm', max_length=50)
    _modifier_nm = models.CharField('_modifier_nm', max_length=50)


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
        verbose_name = '작업지시'
        unique_together = [
            ['work_order_no']
        ]
        index_together = [
            ['Equipment']
        ]