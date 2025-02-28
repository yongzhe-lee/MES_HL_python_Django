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
    stab_atype = models.CharField('품목유형코드', max_length=15, null=True)
    stab_bkbez = models.CharField('품목유형명', max_length=15, null=True)
    stab_zctime = models.DecimalField('C/T', max_digits=5, decimal_places=1, null=True)
    stab_price = models.DecimalField('자재마스터단가', max_digits=11, decimal_places=2, null=True)
    stab_peinh = models.DecimalField('가격단위', max_digits=5, decimal_places=0, null=True)

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
        db_table = 'if_sap_pcb_ran'
        verbose_name = 'PCB난수별입고번호'
        unique_together = [
          
        ]




class IFMesLine(models.Model):

    '''
    line_cd	varchar(20)	라인코드
    line_nm	varchar(200)	라인명
    '''

    id = models.AutoField(primary_key=True)
    line_cd = models.CharField('라인코드', max_length=20)
    line_nm = models.CharField('라인명', max_length=200)

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
        db_table = 'if_mes_line'
        verbose_name = 'MES 라인정보 인터페이스'
        unique_together = [
          
        ]

class IFMesProcess(models.Model):
    '''
    proc_cd	varchar(20)	공정코드
    proc_nm	varchar(200)	공정명

    '''
    id = models.AutoField(primary_key=True)
    proc_cd = models.CharField('공정코드', max_length=20)
    proc_nm = models.CharField('공정명', max_length=200)


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
        db_table = 'if_mes_proc'
        verbose_name = 'MES 공정정보 인터페이스'
        unique_together = [
          
        ]


class IFMesEquipment(models.Model):
    '''
    equ_cd	varchar(20)	설비코드
    equ_nm	varchar(200)	설비명
    line_cd	varchar(20)	라인코드

    '''
    id = models.AutoField(primary_key=True)
    equ_cd = models.CharField('설비코드', max_length=20)
    equ_nm = models.CharField('설비명', max_length=200)
    line_cd = models.CharField('라인코드', max_length=20)

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
        db_table = 'if_mes_equ'
        verbose_name = 'MES 설비정보 인터페이스'
        unique_together = [
          
        ]

class IFMesProductionPlan(models.Model):
    '''
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
        db_table = 'if_mes_prod_plan'
        verbose_name = 'MES 생산계획 인터페이스'
        unique_together = [
          
        ]



class IFMesProductionResult(models.Model):
    '''
    sn	varchar(100)	시리얼번호
    c_sn	varchar(100)	변경시리얼번호
    mat_cd	varchar(20)	품목코드
    equ_cd	varchar(20)	설비코드
    line_cd	varchar(20)	라인코드
    proc_cd	varchar(20)	실적공정코드
    wo_num	varchar(30	작업지시번호
    bom_ver	varchar(5)	BOM버전
    status	varchar(1)	상태
    mes_dt	date	MES일시
    array_num	varchar(20)	배열번호
    pcb_cn	varchar(20)	PCB 번호

    '''
    id = models.BigAutoField(primary_key=True)
    sn = models.CharField('시리얼번호', max_length=100)
    c_sn = models.CharField('변경시리얼번호', max_length=100)
    mat_cd = models.CharField('품목코드', max_length=20)
    equ_cd = models.CharField('설비코드', max_length=20)
    line_cd = models.CharField('라인코드', max_length=20)
    proc_cd = models.CharField('실적공정코드', max_length=20)
    wo_num = models.CharField('작업지시번호', max_length=30)
    bom_ver = models.CharField('BOM버전', max_length=5)
    status = models.CharField('상태', max_length=1)
    mes_dt = models.DateField('MES일시')
    array_num = models.CharField('배열번호', max_length=20)
    pcb_cn = models.CharField('PCB 번호', max_length=20)


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
        db_table = 'if_mes_prod_result'
        verbose_name = 'MES 생산이력 인터페이스'
        unique_together = [
          
        ]


class IFMesEquipmentTestResult(models.Model):
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
    sn = models.CharField('시리얼번호', max_length=100)
    c_sn = models.CharField('변경시리얼번호', max_length=100)
    test_item_cd = models.CharField('검사항목코드', max_length=20)
    test_item_val = models.CharField('항목값', max_length=20)
    min_val = models.CharField('관리기준하한', max_length=20)
    max_val = models.CharField('관리기준상한', max_length=20)
    unit = models.CharField('단위', max_length=5)
    status = models.CharField('상태', max_length=5)
    pcb_cn = models.CharField('PCB 번호', max_length=20)
    equ_cd = models.CharField('설비코드', max_length=20)
    mat_cd = models.CharField('품목코드', max_length=20)
    mes_dt = models.DateField('MES일시')
    proc_cd = models.CharField('실적공정코드', max_length=20)
        

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
        db_table = 'if_equ_test_result'
        verbose_name = 'MES 설비측정데이터 인터페이스'
        unique_together = [
          
        ]

class IFQmsDefect(models.Model):
    '''
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
    id = models.BigAutoField(primary_key=True)
    qis_pk = models.IntegerField('QIS부적합테이블 PK')
    a_date = models.DateField('분석일자')
    o_date = models.DateField('발생일자')
    w_shift = models.CharField('근무조', max_length=10)
    step_class = models.CharField('단계', max_length=20)
    line_cd = models.CharField('라인코드', max_length=20)
    mat_cd = models.CharField('품목코드', max_length=50)
    serial_no = models.CharField('시리얼번호', max_length=50)
    hlk_part_no = models.CharField('파트번호', max_length=50)
    de_proc_cd = models.CharField('검출공정', max_length=20)
    oc_prod_cd = models.CharField('발생공정', max_length=20)
    imput_cate = models.CharField('귀책구분', max_length=50)
    defect_qty = models.DecimalField('불량수량', max_digits=13, decimal_places=3)
    defect_type1 = models.CharField('불량유형1', max_length=50)
    defect_type2 = models.CharField('불량유형2', max_length=50)
    worker_name = models.CharField('생산라인작업자', max_length=50)
    remark = models.CharField('REMARK(내용)', max_length=2000)
    init_result = models.CharField('초기분석결과', max_length=2000)
    complete_date = models.DateField('최종결론')
    final_result = models.CharField('최종결론내용', max_length=2000)
    

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
        db_table = 'if_qms_defect'
        verbose_name = 'MES 설비측정데이터 인터페이스'
        unique_together = [
          
        ]


class IFVanLotHostory(models.Model):
    '''
    VAN 입고식별번호	van_pk
    구매오더	po_number
    SAP자재전표(입고번호)	sap_recv_num
    검사유무	test_type
    판정결과	judg_result
    품목코드	mat_cd
    품목내역	mat_detail
    저장위치	loc_cd
    공급업체코드	supp_cd
    공급업체명	supp_nm
    단위	unit
    입고수량	input_qty
    LOT No	lot_no
    입고일자	recv_date
    입고시간	recv_time
    검사판정일자	ju_date
    검사판정시간	ju_time
    '''
    id = models.BigAutoField(primary_key=True)
    van_pk = models.CharField('VAN 입고식별번호', max_length=20)
    po_number = models.CharField('구매오더', max_length=20)
    sap_recv_num = models.CharField('SAP자재전표(입고번호)', max_length=20)
    test_type = models.CharField('검사유무', max_length=20)
    judg_result = models.CharField('판정결과', max_length=20)
    mat_cd = models.CharField('품목코드', max_length=20)
    mat_detail = models.CharField('품목내역', max_length=200)
    sap_loc_cd = models.CharField('저장위치', max_length=20)
    supp_cd = models.CharField('공급업체코드', max_length=20)
    supp_nm = models.CharField('공급업체명', max_length=200)
    unit = models.CharField('단위', max_length=20)
    input_qty = models.DecimalField('입고수량', max_digits=13, decimal_places=3)
    lot_no = models.CharField('LOT No', max_length=20)
    recv_date = models.DateField('입고일자')
    recv_time = models.TimeField('입고시간')
    ju_date = models.DateField('검사판정일자')
    ju_time = models.TimeField('검사판정시간')
    

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
        db_table = 'if_van_lot_history'
        verbose_name = 'VAN 입고별 LOT발행이력'
        unique_together = [
        ]


class IFVanReceivingInspectionResult(models.Model):
    '''
    van 검사고유식별번호	van_pk
    데이터 상태	status
    합격	is_pass
    불량	is_defect
    4M	is_4m
    DEV	is_dev
    제품그룹	prod_grp
    품목코드	mat_cd
    품목내역	mat_detail
    공장	factory
    LOT no	lot_no
    LOT size	lot_size
    수입검사코드	incom_test_cd
    검사수량	test_qty
    입고수량	input_qty
    입고여부	input_status
    주기단계	stage
    '''

    id = models.BigAutoField(primary_key=True)
    van_pk = models.CharField('van 검사고유식별번호', max_length=20)
    status = models.CharField('데이터 상태', max_length=20)
    is_pass = models.CharField('합격', max_length=20)
    is_defect = models.CharField('불량', max_length=20)
    is_4m = models.CharField('4M', max_length=20)
    is_dev = models.CharField('DEV', max_length=20)
    prod_grp = models.CharField('제품그룹', max_length=20)
    mat_cd = models.CharField('품목코드', max_length=20)
    mat_detail = models.CharField('품목내역', max_length=200)
    factory = models.CharField('공장', max_length=20)
    lot_no = models.CharField('LOT no', max_length=20)
    lot_size = models.CharField('LOT size', max_length=20)
    incom_test_cd = models.CharField('수입검사코드', max_length=20)
    test_qty = models.DecimalField('검사수량', max_digits=13, decimal_places=3)
    input_qty = models.DecimalField('입고수량', max_digits=13, decimal_places=3)
    input_status = models.CharField('입고여부', max_length=20)
    stage = models.CharField('주기단계', max_length=20)


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
        db_table = 'if_recv_inst_result'
        verbose_name = 'VAN PCB 수입검사결과 인터페이스'
        unique_together = [
        ]


class if_log(models.Model):

    id = models.BigAutoField(primary_key=True)
    task = models.CharField('인터페이스업무데이터구분', max_length=50, null =True)
    method = models.CharField('인터페이스방법', max_length=50, null =True)
    contents = models.TextField('인터페이스내용', null =True)
    equ_cd = models.CharField('설비코드', max_length=20, null =True)
    mat_cd = models.CharField('품목코드', max_length=50, null =True)
    rev_no = models.CharField('REVISION번호', max_length=2, null =True)
    is_success  = models.CharField(' success yn', max_length=1, default="Y")
    log_date = models.DateTimeField('로그일시', auto_now_add=True)

    class Meta():
        db_table = 'if_log'
        verbose_name = '인터페이스 이력 로그'
        unique_together = [
        ]

