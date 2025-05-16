from tabnanny import verbose
from django.db import models
from domain.services.date import DateUtil


class IFSapMaterial(models.Model):
    '''
    STAB_WERKS	CHAR(4)	플랜트
    STAB_MATNR	CHAR(18)	자재
    STAB_MAKTX	CHAR(40)	품명
    STAB_GROES	CHAR(32)	규격
    STAB_MATKL	CHAR(9)	자재그룹
    STAB_MTART	CHAR(15)	자재유형
    STAB_MEINS	CHAR(4)	기본단위
    STAB_ATYPE	CHAR(15)	품목유형
    '''
    id  = models.AutoField(primary_key=True)

    stab_werks = models.CharField('플랜트', max_length=4, null=True)
    stab_matnr = models.CharField('자재', max_length=18, null=True)
    stab_maktx = models.CharField('품명', max_length=40, null=True)
    stab_groes = models.CharField('규격', max_length=32, null=True)
    stab_matkl = models.CharField('자재그룹', max_length=9, null=True)
    stab_mtart = models.CharField('자재유형', max_length=15, null=True)
    stab_meins = models.CharField('기본단위', max_length=4, null=True)
    stab_bklas = models.CharField('품목유형코드', max_length=15, null=True)
    stab_bkbez = models.CharField('품목유형명', max_length=25, null=True)
    stab_zctime = models.DecimalField('C/T', max_digits=5, decimal_places=1, null=True)
    stab_price = models.DecimalField('자재마스터단가', max_digits=11, decimal_places=2, null=True)
    stab_peinh = models.DecimalField('가격단위', max_digits=5, decimal_places=0, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_sap_mat'
        verbose_name = 'sap 품목정보 인터페이스'
        unique_together = [
          
        ]

class IFSapBOM(models.Model):

   
    id  = models.AutoField(primary_key=True)
    stab_werks = models.CharField('플랜트', max_length=4)
    stab_matnr = models.CharField('상위자재', max_length=18)
    stab_revlv = models.CharField('REVISION번호', max_length=2, null=True)
    stab_bmeng = models.DecimalField('기준수량', max_digits=13, decimal_places=3)
    stab_idnrk = models.CharField('구성부품코드', max_length=18)
    stab_mnglg = models.DecimalField('구성부품수량', max_digits=13, decimal_places=3)
    stab_meins = models.CharField('단위', max_length=4)
    stab_stufe = models.CharField('BOM레벨', max_length=5)
    stab_datuv = models.CharField('효력시작일', max_length=8)
    stab_datab = models.CharField('효력종료일', max_length=8)
    stab_aennr = models.CharField('ECN번호', max_length=12, null=True)
    stab_bklas = models.CharField('품목유형코드', max_length=4, null=True)
    stab_bkbez = models.CharField('품목유형명', max_length=25, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_sap_bom'
        verbose_name = 'sap bom 인터페이스'
        unique_together = [
          
        ]

class IFSapMaterialStock(models.Model):

    '''
    STAB-WERKS	char(4)	플랜트
    STAB_MATNR	char(18)	자재
    STAB-MAKTX	char(40)	품명
    STAB-LGORT	char(4)	저장위치
    STAB-LABST	decimal(13.3)	가용재고
    STAB-INSME	decimal(13.3)	품질재고
    STAB-SPEME	decimal(13.3)	보류재고
    STAB-MEINS	char(4)	단위
    '''
    id = models.AutoField(primary_key=True)
    stab_werks = models.CharField('플랜트', max_length=4)
    stab_matnr = models.CharField('자재', max_length=18)
    stab_maktx = models.CharField('품명', max_length=40)
    stab_lgort = models.CharField('저장위치', max_length=4)
    stab_lgobe = models.CharField('저장위치', max_length=16, null=True)
    stab_labst = models.DecimalField('가용재고', max_digits=13, decimal_places=3, null=True)
    stab_insme = models.DecimalField('품질재고', max_digits=13, decimal_places=3, null=True)
    stab_speme = models.DecimalField('보류재고', max_digits=13, decimal_places=3, null=True)
    stab_mslbq = models.DecimalField('외주재고', max_digits=13, decimal_places=3, null=True)
    stab_mkolq = models.DecimalField('벤더 Consignment', max_digits=13, decimal_places=3, null=True)
    stab_mskuq = models.DecimalField('고객  Consignment', max_digits=13, decimal_places=3, null=True)
    stab_meins = models.CharField('단위', max_length=4)
    stab_bklas = models.CharField('품목유형코드', max_length=4,  null=True)
    stab_bkbez = models.CharField('품목유형명', max_length=25, null=True)
    data_date = models.DateTimeField('기준일시')
    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_sap_mat_stock'
        verbose_name = 'sap 품목별 현재고 인터페이스'
        unique_together = [
          
        ]

class IFSapPcbRandomNumber(models.Model):
    id = models.AutoField(primary_key=True)
    stab_mblnr = models.CharField('입고번호', max_length=10)
    stab_zeile = models.CharField('아이템번호', max_length=4)
    stab_matnr = models.CharField('자재번호', max_length=18)
    stab_maktx = models.CharField('품명', max_length=40)
    stab_menge = models.DecimalField('입고수량', max_digits=13, decimal_places=3)
    stab_abqty = models.DecimalField('난수별수량', max_digits=13, decimal_places=3)
    stab_meins = models.CharField('단위', max_length=4)
    rnd_num = models.CharField('난수번호', max_length=10, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_sap_pcb_ran'
        verbose_name = 'PCB난수별입고번호'
        unique_together = [
          
        ]

class IFMesLine(models.Model):
    '''
    사용하지 않음, 삭제예정
    line_cd	varchar(20)	라인코드
    line_nm	varchar(200)	라인명
    '''

    id = models.AutoField(primary_key=True)
    line_cd = models.CharField('라인코드', max_length=20)
    line_nm = models.CharField('라인명', max_length=200)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_mes_line'
        verbose_name = 'MES 라인정보 인터페이스'
        unique_together = [
          
        ]

class IFMesProcess(models.Model):
    '''
    사용하지 않음 삭제예정
    proc_cd	varchar(20)	공정코드
    proc_nm	varchar(200)	공정명

    '''
    id = models.AutoField(primary_key=True)
    proc_cd = models.CharField('공정코드', max_length=20)
    proc_nm = models.CharField('공정명', max_length=200)


    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_mes_proc'
        verbose_name = 'MES 공정정보 인터페이스'
        unique_together = [
          
        ]

class IFMesEquipment(models.Model):
    '''
    사용하지 않음, 삭제예정
    equ_cd	varchar(20)	설비코드
    equ_nm	varchar(200)	설비명
    line_cd	varchar(20)	라인코드
    '''
    id = models.AutoField(primary_key=True)
    equ_cd = models.CharField('설비코드', max_length=20)
    equ_nm = models.CharField('설비명', max_length=200)
    line_cd = models.CharField('라인코드', max_length=20)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_mes_equ'
        verbose_name = 'MES 설비정보 인터페이스'
        unique_together = [
          
        ]

class IFMesProductionPlan(models.Model):
    '''
    생산계획
    plan_date	date	계획일
    line_cd	varchar(20)	라인코드
    order	int	순서
    mat_cd	varchar(20)	품목코드
    plan_qty	decimal(13,3)	계획수량
    description	varchar(2000)	비고

    '''
    id = models.AutoField(primary_key=True)
    plan_date = models.DateField('계획일')
    line_cd = models.CharField('라인코드', max_length=20)
    order = models.IntegerField('순서')
    mat_cd = models.CharField('품목코드', max_length=20)
    plan_qty = models.DecimalField('계획수량', max_digits=13, decimal_places=3)
    description = models.CharField('비고', max_length=2000)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_mes_prod_plan'
        verbose_name = 'MES 생산계획 인터페이스'
        unique_together = [
          
        ]

class IFEquipmentResult(models.Model):
    '''
    제어PC 설비데이터
    '''
    id = models.BigAutoField(primary_key=True)
    equ_cd = models.CharField('StationID', max_length=100, null=True) # plant_i 설비코드
    data_date = models.DateTimeField('생성일시')
    sn = models.CharField('대표시리얼번호', max_length=100, null=True)
    sn_new = models.CharField('변경시리얼번호', max_length=100, null=True) # 하우징 PCB Assembly 에서만 들어온다
    sn_items = models.JSONField('다중시리얼번호', null=True) # SMT#4 에서만 들어온다
    pcb_cn = models.CharField('PCB 번호', max_length=100, null=True) # 레이저마킹에서만 들어온다
    pcb_input = models.DateTimeField('pcb_input', null=True) #smt 전용
    pcb_size = models.CharField('pcb size', max_length=100, null=True) #smt 전용
    pcb_ww = models.CharField('pcb ww', max_length=100, null=True) #smt 전용(레이저마킹)
    pcb_array = models.CharField('pcb_array', max_length=100, null=True) #smt 전용
    state =  models.CharField('생산결과', max_length=5, null=True)  # 합부여부
    # light =  models.JSONField('경광등정보', null=True) DT전용
    # light_items = models.JSONField('경광등정보', null=True) # 마운터전용 ==> DT전용
    m_status = models.JSONField('설비가동상태정보', null=True) # 설비상태 {"status" : "run", "start_dt": "", "end_dt": ""}
    mat_cd = models.CharField('PartNr', max_length=100, null=True) # 품목코드
    mat_desc = models.CharField('PartDesc', max_length=100, null=True) # SAP에 등록되어 있는 품목설명    
    #mes_equ_cd = models.CharField('StationNo', max_length=100, null=True)
    bom_ver = models.CharField('bom_ver', max_length=100, null=True)
    is_alarm = models.BooleanField('is_alarm', default=False, null=True)
    alarm_items = models.JSONField('알람목록', null=True)  #[{"alarm_cd" : "", "":""} ]
    flow_meter_items = models.JSONField('유량계정보', null=True) # 마운터전용 {"flow_meter1":1, "flow_meter2":2}
    module_no = models.CharField('module_no', max_length=100, null=True) # 마운터전용
    dummy1 = models.CharField('dummy1', max_length=100, null=True)
    dummy2 = models.CharField('dummy2', max_length=100, null=True)    
    _created = models.DateTimeField('_created', auto_now=True)

    class Meta():
        db_table = 'if_equ_result'
        verbose_name = 'MES 설비생산데이터 인터페이스'
        unique_together = [
            ["equ_cd", "data_date","sn"]
        ] 

class IFEquipmentResultItem(models.Model):
    '''
    설비측정데이터 인터페이스
    sn	varchar(100)	시리얼번호
    c_sn	varchar(100)	변경시리얼번호
    test_item_cd	varchar(20)	검사항목코드
    test_item_val	varchar(20)	항목값
    min_val	varchar(20)	관리기준하한
    max_val	varchar(20)	관리기준상한
    unit	varchar(5)	단위
    status	varchar(5)	상태
    pcb_cn	varchar(20)	PCB 번호
    equ_cd	varchar(20)	설비코드
    mat_cd	varchar(20)	품목코드
    mes_dt	date	MES일시
    proc_cd	varchar(20)	실적공정코드
    '''
    id = models.BigAutoField(primary_key=True)
    EquipmentResult = models.ForeignKey(IFEquipmentResult, on_delete=models.CASCADE, null=True, db_column="rst_id")
    test_item_cd = models.CharField('검사항목코드', max_length=100)
    test_item_val = models.CharField('항목값', max_length=500, null=True)
    min_val = models.CharField('관리기준하한', max_length=500, null=True)
    max_val = models.CharField('관리기준상한', max_length=500, null=True)
    unit = models.CharField('단위', max_length=20, null=True)
    failcode = models.CharField('failcode', max_length=2000, null=True)
    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    

    class Meta():
        db_table = 'if_equ_result_item'
        verbose_name = 'MES 설비측정데이터 인터페이스'
        unique_together = [
          ["EquipmentResult", "test_item_cd"]
        ]

class IFEquipemntDefectItems(models.Model):
    '''
    결함코드
    결함명
    컴포넌트명(포지션)
    부품번호
    '''

    id = models.BigAutoField(primary_key=True)
    EquipmentResult = models.ForeignKey(IFEquipmentResult, on_delete=models.CASCADE, null=True, db_column="rst_id")
    defect_cd = models.CharField('결함코드', max_length=20, null=True)
    defect_nm = models.CharField('결함명', max_length=100, null=True)
    component_nm = models.CharField('컴포넌트명(포지션)', max_length=100, null=True)
    part_no = models.CharField('부품번호', max_length=100, null=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modfied', auto_now=True)

    class Meta():
        db_table = 'if_equ_defect_item'
        verbose_name = 'MES 설비부적합데이터 인터페이스'
        unique_together = [
            ["EquipmentResult", "defect_cd"]
        ]

class IFMounterPickupRate(models.Model):
    id = models.BigAutoField(primary_key=True)
    job = models.CharField("job", max_length=200, null=True)
    equ_cd = models.CharField('설비코드', max_length=50, null=True)
    machine = models.CharField('머신코드', max_length=50, null=True)
    position = models.CharField('포지션', max_length=50, null=True)
    partNumber = models.CharField('부품번호', max_length=50, null=True)
    fidl = models.CharField('FIDL', max_length=50, null=True)
    pickup = models.IntegerField('픽업수', null=True)
    no_pickup = models.IntegerField('픽업실패수', null=True)
    usage = models.IntegerField('사용횟수', null=True)
    reject = models.IntegerField('리젝수', null=True)
    error = models.IntegerField('에러수', null=True)
    dislodge = models.IntegerField('이탈수', null=True)
    rescan = models.IntegerField('리스캔수', null=True)
    lcr = models.IntegerField('LCR수', null=True)
    pickup_ratio = models.DecimalField('픽업비율', max_digits=5, decimal_places=2, null=True)
    reject_ratio = models.DecimalField('리젝비율', max_digits=5, decimal_places=2, null=True)
    error_ratio = models.DecimalField('에러비율', max_digits=5, decimal_places=2, null=True)
    dislodge_ratio = models.DecimalField('이탈비율', max_digits=5, decimal_places=2, null=True)
    success_ratio = models.DecimalField('성공비율', max_digits=5, decimal_places=2, null=True)

    data_date = models.DateTimeField('생성일시')
    _status = models.CharField('_status', max_length=10, null=True)
    _created = models.DateTimeField('_created', auto_now_add=True)
    _modified = models.DateTimeField('_modfied', auto_now=True)

    class Meta():
        db_table = 'if_mnt_pickup_rate'
        verbose_name = 'mouter pickup rate'
        unique_together = [
            ["machine", "position","data_date"]
        ]

class IFQmsDefect(models.Model):
    '''
    DB to DB로 변경되었습니다.

    qis_pk	int	QIS부적합테이블 PK
    a_date	date	분석일자
    o_date	date	발생일자
    w_shift	varchar(10)	근무조
    step_class	varchar(20)	단계
    line_cd	varchar(20)	라인코드
    mat_cd	varchar(50)	품목코드
    serial_no	varchar(50)	시리얼번호
    hlk_part_no	varchar(50)	파트번호
    de_proc_cd	varchar(20)	검출공정
    oc_prod_cd	varchar(20)	발생공정
    imput_cate	varchar(50)	귀책구분
    defect_qty	decimal(13,3)	불량수량
    defect_type1	varchar(50)	불량유형1
    defect_type2	varchar(50)	불량유형2
    worker_name	varchar(50)	생산라인작업자
    remark	varchar(2000)	REMARK(내용)
    init_result	varchar(2000)	초기분석결과
    complete_date	date	최종결론
    final_result	varchar(2000)	최종결론내용

    '''
   #id = models.BigAutoField(primary_key=True)
    qis_pk = models.IntegerField('QIS부적합테이블 PK', primary_key=True)
    a_date = models.DateField('분석일자', null=True)
    o_date = models.DateField('발생일자', null=True)
    w_shift = models.CharField('근무조', max_length=10, null=True)
    step_class = models.CharField('단계', max_length=20, null=True)
    line_cd = models.CharField('라인코드', max_length=20, null=True)
    mat_cd = models.CharField('품목코드', max_length=50, null=True)
    serial_no = models.CharField('시리얼번호', max_length=50, null=True)
    hlk_part_no = models.CharField('파트번호', max_length=50, null=True)
    de_proc_cd = models.CharField('검출공정', max_length=50, null=True)
    oc_prod_cd = models.CharField('발생공정', max_length=50, null=True)
    imput_cate = models.CharField('귀책구분', max_length=50, null=True)
    defect_qty = models.DecimalField('불량수량', max_digits=13, decimal_places=3, null=True)
    defect_type1 = models.CharField('불량유형1', max_length=50, null=True)
    defect_type2 = models.CharField('불량유형2', max_length=50, null=True)
    worker_name = models.CharField('생산라인작업자', max_length=50, null=True)
    remark = models.CharField('REMARK(내용)', max_length=2000, null=True)
    init_result = models.CharField('초기분석결과', max_length=2000, null=True)
    complete_date = models.DateField('최종결론', null=True)
    final_result = models.CharField('최종결론', max_length=2000, null=True)    
    final_remark = models.CharField('최종결론내용', max_length=2000, null=True)   

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_qms_defect'
        verbose_name = 'MES 설비측정데이터 인터페이스'
        unique_together = [
          
        ]

class IFVanInterface(models.Model):

    id = models.BigAutoField(primary_key=True)
    rnd_num = models.CharField('난수번호', max_length=10, null=True)
    #헤더시작
    report_number = models.CharField("성적서번호", max_length=20, null=True )
    inv_number = models.CharField("거래명세서번호", max_length=20, null=True )
    inv_seq = models.CharField("거래명세서아이템항번", max_length=6, null=True )
    sap_gr_number = models.CharField("SAP입고번호", max_length=20, null=True )
    sap_gr_seq = models.CharField("sap_gr_seq", max_length=10, null=True )
    mold = models.CharField("금형차수", max_length=1, null=True )
    material_number = models.CharField("자재코드", max_length=50, null=True )
    material_name = models.CharField("자재명", max_length=500, null=True )
    vendor_code = models.CharField("업체코드", max_length=20, null=True )
    vendor_name = models.CharField("업체명", max_length=500, null=True )
    material_revision = models.CharField("자재리비전", max_length=10, null=True )
    ecn_no = models.CharField("ecn_no", max_length=20, null=True )
    check_date = models.CharField("검사일자", max_length=8, null=True )
    check_user_name = models.CharField("검사자", max_length=50, null=True )
    lot_no = models.CharField("lot_no", max_length=10, null=True )
    lot_size  = models.CharField("lot_size", max_length=18, null=True )
    devision_no = models.CharField("devision_no", max_length=50, null=True )
    fm_no = models.CharField("4M no", max_length=100, null=True )
    gr_date = models.CharField("입고일자", max_length=8, null=True )
    confirm_date = models.CharField("판정일자", max_length=8, null=True )
    result_value = models.CharField("판정결과", max_length=20, null=True )
    remark = models.CharField("remark", max_length=1000, null=True )
    aql_sample_count = models.DecimalField("AQL 외관검사샘플링수", null=True, max_digits=18, decimal_places=0, blank=True)
    defect_rate = models.CharField("불량률기준", max_length=50, null=True )
    passing_count= models.CharField("AC합격판정개수", max_length=50, null=True )
    defect_count = models.CharField("RE불량판정개수", max_length=50, null=True )
    #defect_rate = models.DecimalField("불량률기준", max_digits=18, decimal_places=2, null=True, blank=True)
    #passing_count = models.DecimalField("AC합격판정개수", null=True, max_digits=18, decimal_places=0, blank=True)
    #defect_count =  models.DecimalField("RE불량판정개수", null=True, max_digits=18, decimal_places=0, blank=True)
    sample_check_count=  models.DecimalField("AQL치수검사수량", null=True, max_digits=18, decimal_places=0, blank=True)

    # 아이템 시작
    seq =  models.IntegerField("seq", null=True, blank=True)
    ins_text = models.CharField("ins_text", max_length=100, null=True )
    spec_seq =  models.CharField("specification", max_length=7, null=True )
    specification  = models.CharField("specification", max_length=500, null=True )
    #upper_limit = models.DecimalField("upper_limit", max_digits=18, decimal_places=5, null=True, blank=True)
    #lower_limit = models.DecimalField("lower_limit", max_digits=18, decimal_places=5, null=True, blank=True)
    upper_limit = models.CharField("upper_limit", max_length=20, null=True )
    lower_limit = models.CharField("lower_limit", max_length=20, null=True )

    unit = models.CharField("unit", max_length=20, null=True )
    machine_type = models.CharField("machine_type", max_length=20, null=True )
    machine_type_text = models.CharField("machine_type_text", max_length=100, null=True )

    x1 = models.CharField("x1", max_length=20, null=True)
    x2 = models.CharField("x2", max_length=20, null=True)
    x3 = models.CharField("x3", max_length=20, null=True)
    x4 = models.CharField("x4", max_length=20, null=True)
    x5 = models.CharField("x5", max_length=20, null=True)
    x6 = models.CharField("x6", max_length=20, null=True)
    x7 = models.CharField("x7", max_length=20, null=True)
    x8 = models.CharField("x8", max_length=20, null=True)
    x9 = models.CharField("x9", max_length=20, null=True)
    x10 = models.CharField("x10", max_length=20, null=True)

    x_avg  = models.CharField("x_avg", max_length=20, null=True )
    r_val = models.CharField("r_val", max_length=20, null=True )
    pass_fail = models.CharField("pass_fail", max_length=20, null=True )
    input_value= models.CharField("input_value", max_length=4, null=True )
    input_value_text = models.CharField("input_value_text", max_length=100, null=True )
    upper_limit_check = models.CharField("upper_limit_check", max_length=5, null=True )
    lower_limit_check = models.CharField("lower_limit_check", max_length=5, null=True )  

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'if_van'
        verbose_name = 'VAN PCB 수입검사결과 인터페이스'
        unique_together = [
        ]

class VanReport(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    rnd_num = models.CharField('난수번호', max_length=10, null=True)
    #헤더시작
    report_number = models.CharField("성적서번호", max_length=20, null=True )
    inv_number = models.CharField("거래명세서번호", max_length=20, null=True )
    inv_seq = models.CharField("거래명세서아이템항번", max_length=6, null=True )
    sap_gr_number = models.CharField("SAP입고번호", max_length=20, null=True )
    sap_gr_seq = models.CharField("sap_gr_seq", max_length=10, null=True )
    mold = models.CharField("금형차수", max_length=1, null=True )
    material_number = models.CharField("자재코드", max_length=50, null=True )
    material_name = models.CharField("자재명", max_length=500, null=True )
    vendor_code = models.CharField("업체코드", max_length=20, null=True )
    vendor_name = models.CharField("업체명", max_length=500, null=True )
    material_revision = models.CharField("자재리비전", max_length=10, null=True )
    ecn_no = models.CharField("ecn_no", max_length=20, null=True )
    check_date = models.CharField("검사일자", max_length=8, null=True )
    check_user_name = models.CharField("검사자", max_length=50, null=True )
    lot_no = models.CharField("lot_no", max_length=10, null=True )
    lot_size  = models.CharField("lot_size", max_length=18, null=True )
    devision_no = models.CharField("devision_no", max_length=50, null=True )
    fm_no = models.CharField("4M no", max_length=100, null=True )
    gr_date = models.CharField("입고일자", max_length=8, null=True )
    confirm_date = models.CharField("판정일자", max_length=8, null=True )
    result_value = models.CharField("판정결과", max_length=20, null=True )
    remark = models.CharField("remark", max_length=1000, null=True )
    aql_sample_count = models.DecimalField("AQL 외관검사샘플링수", null=True, max_digits=18, decimal_places=0, blank=True)

    defect_rate = models.CharField("defect_rate", max_length=50, null=True )
    passing_count= models.CharField("passing_count", max_length=50, null=True )
    defect_count = models.CharField("defect_count", max_length=50, null=True )
    #defect_rate = models.DecimalField("불량률기준", max_digits=18, decimal_places=2, null=True, blank=True)
    #passing_count = models.DecimalField("AC합격판정개수", null=True, max_digits=18, decimal_places=0, blank=True)
    #defect_count =  models.DecimalField("RE불량판정개수", null=True, max_digits=18, decimal_places=0, blank=True)
    sample_check_count=  models.DecimalField("AQL치수검사수량", null=True, max_digits=18, decimal_places=0, blank=True)

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'van_report'
        verbose_name = 'VAN PCB 성적서'
        unique_together = [
        ]

class VanItemResult(models.Model):
    id = models.BigAutoField(primary_key=True)
    VanReport = models.ForeignKey(VanReport, db_column='report_id', on_delete=models.DO_NOTHING, db_comment="VAN성적서id")
    seq =  models.IntegerField("seq", null=True, blank=True)
    ins_text = models.CharField("ins_text", max_length=100, null=True )
    spec_seq =  models.CharField("specification", max_length=7, null=True )
    specification  = models.CharField("specification", max_length=500, null=True )
    #upper_limit = models.DecimalField("upper_limit", max_digits=18, decimal_places=5, null=True, blank=True)
    #lower_limit = models.DecimalField("lower_limit", max_digits=18, decimal_places=5, null=True, blank=True)
    upper_limit = models.CharField("upper_limit", max_length=20, null=True )
    lower_limit = models.CharField("lower_limit", max_length=20, null=True )

    unit = models.CharField("unit", max_length=20, null=True )
    machine_type = models.CharField("machine_type", max_length=20, null=True )
    machine_type_text = models.CharField("machine_type_text", max_length=100, null=True )

    x1 = models.CharField("x1", max_length=20, null=True)
    x2 = models.CharField("x2", max_length=20, null=True)
    x3 = models.CharField("x3", max_length=20, null=True)
    x4 = models.CharField("x4", max_length=20, null=True)
    x5 = models.CharField("x5", max_length=20, null=True)
    x6 = models.CharField("x6", max_length=20, null=True)
    x7 = models.CharField("x7", max_length=20, null=True)
    x8 = models.CharField("x8", max_length=20, null=True)
    x9 = models.CharField("x9", max_length=20, null=True)
    x10 = models.CharField("x10", max_length=20, null=True)

    x_avg  = models.CharField("x_avg", max_length=20, null=True )
    r_val = models.CharField("r_val", max_length=20, null=True )
    pass_fail = models.CharField("pass_fail", max_length=20, null=True )
    input_value= models.CharField("input_value", max_length=4, null=True )
    input_value_text = models.CharField("input_value_text", max_length=100, null=True )
    upper_limit_check = models.CharField("upper_limit_check", max_length=5, null=True )
    lower_limit_check = models.CharField("lower_limit_check", max_length=5, null=True )  

    _status = models.CharField('_status', max_length=10, null=True)
    _created    = models.DateTimeField('_created', auto_now_add=True, null=True)
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
        db_table = 'van_item_result'
        verbose_name = 'VAN PCB 성적서항목결과'
        unique_together = [
        ]

class IFLog(models.Model):

    id = models.BigAutoField(primary_key=True)
    task = models.CharField('인터페이스업무데이터구분', max_length=50, null =True)
    method = models.CharField('인터페이스방법', max_length=50, null =True)
    contents = models.TextField('인터페이스내용', null =True)
    equ_cd = models.CharField('설비코드', max_length=20, null =True)
    mat_cd = models.CharField('품목코드', max_length=50, null =True)
    rev_no = models.CharField('REVISION번호', max_length=2, null =True)
    is_success  = models.CharField(' success yn', max_length=1, default="Y")
    log_date = models.DateTimeField('로그일시', auto_now_add=True)
    _creater_id = models.IntegerField('_creater_id', null=True)

    class Meta():
        db_table = 'if_log'
        verbose_name = '인터페이스 이력 로그'
        unique_together = [
        ]

