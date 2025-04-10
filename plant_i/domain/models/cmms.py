from tarfile import NUL
from django.db import models
from domain.models.definition import Equipment, Material, Site, Unit
from domain.models.user import Depart
from django.contrib.auth.models import User
from domain.services.date import DateUtil
from datetime import datetime

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'HOST': DBMS_HOST,
#         'NAME': 'swing',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'PORT': 5432,
#         'OPTIONS': {
#             'options': '-c search_path=swing_admin'
#         }
#     }
# }

# python manage.py inspectdb > cmms.py

class CmAlarm(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='alarm_pk', db_comment='알람 PK')
    CmTag = models.ForeignKey('CmTag', models.DO_NOTHING, db_column='tag_pk', db_comment='태그 PK')
    AlarmDt = models.DateTimeField(db_column='alarm_dt', db_comment='알람일시')
    AlarmType = models.CharField(max_length=10, db_column='alarm_type', db_comment='알람유형')
    DataVal = models.FloatField(blank=True, null=True, db_column='data_val', db_comment='데이터값')
    StdVal = models.CharField(max_length=20, blank=True, null=True, db_column='std_val', db_comment='기준값')
    AlarmStatus = models.CharField(db_column='alarm_status', db_comment='알람상태')
    AlarmAck = models.CharField(blank=True, null=True, db_column='alarm_ack', db_comment='알람확인')
    ReturnDt = models.DateTimeField(blank=True, null=True, db_column='return_dt', db_comment='복귀일시')
    TagDataPk = models.BigIntegerField(blank=True, null=True, db_column='tag_data_pk', db_comment='태그데이터 PK')
    CmAlarmAction = models.ForeignKey('CmAlarmAction', models.DO_NOTHING, db_column='alarm_actn_pk', null=True, db_comment='알람조치 PK')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    UpdateDt = models.DateTimeField(auto_now_add=True, null=True, db_column='update_dt', db_comment='수정일시')

    class Meta:
        db_table = 'cm_alarm'
        db_table_comment = '알람'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return

class CmAlarmAction(models.Model):
    id = models.AutoField(primary_key=True, db_column='alarm_actn_pk', db_comment='알람조치 PK')
    ActnDt = models.DateTimeField(db_column='actn_dt', db_comment='조치일시')
    ActnUserId = models.CharField(max_length=20, db_column='actn_user_id', db_comment='조치자 ID')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    AlarmStatus = models.CharField(max_length=10, blank=True, null=True, db_column='alarm_status', db_comment='알람상태')
    AlarmCause = models.CharField(max_length=10, db_column='alarm_cause', db_comment='알람원인')
    ActnType = models.CharField(max_length=10, db_column='actn_type', db_comment='조치유형')
    ActnRemark = models.CharField(max_length=400, blank=True, null=True, db_column='actn_remark', db_comment='조치비고')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_alarm_actn'
        db_table_comment = '알람조치'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return

class CmAlarmBox(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='alarm_box_pk', db_comment='알람박스 PK')
    BoxGroupCode = models.CharField(max_length=15, db_column='box_group_cd', db_comment='박스그룹코드')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    BoxEquipName = models.CharField(max_length=30, db_column='box_equip_nm', db_comment='박스설비명')
    TopScale = models.DecimalField(max_digits=3, decimal_places=1, db_column='top_scale', db_comment='상단스케일')
    LeftScale = models.DecimalField(max_digits=3, decimal_places=1, db_column='left_scale', db_comment='좌측스케일')
    TopScaleFull = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, db_column='top_scale_full', db_comment='상단스케일전체')
    LeftScaleFull = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, db_column='left_scale_full', db_comment='좌측스케일전체')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_alarm_box'
        db_table_comment = '알람박스'
        unique_together = (('BoxGroupCode', 'CmEquipment'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return

class CmAlarmNotiGroup(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='alarm_noti_grp_pk', db_comment='알람알림그룹 PK')
    NotiGrpName = models.CharField(unique=True, max_length=50, db_column='noti_grp_nm', db_comment='알림그룹명')
    NotiGrpType = models.CharField(max_length=20, db_column='noti_grp_type', db_comment='알림그룹유형')
    MailSndYn = models.CharField(db_column='mail_snd_yn', db_comment='메일발송여부')
    SmsSndYn = models.CharField(db_column='sms_snd_yn', db_comment='SMS발송여부')
    MailTitle = models.CharField(max_length=50, blank=True, null=True, db_column='mail_title', db_comment='메일제목')
    MailContent = models.CharField(max_length=2000, blank=True, null=True, db_column='mail_content', db_comment='메일내용')
    MailSndrAddr = models.CharField(max_length=40, blank=True, null=True, db_column='mail_sndr_addr', db_comment='메일발신자주소')
    SmsContent = models.CharField(max_length=100, blank=True, null=True, db_column='sms_content', db_comment='SMS내용')
    SmsSndrNo = models.CharField(max_length=15, blank=True, null=True, db_column='sms_sndr_no', db_comment='SMS발신번호')
    Remark = models.CharField(max_length=200, blank=True, null=True, db_column='remark', db_comment='비고')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertDt = models.DateTimeField(auto_now_add=True, db_column='insert_dt', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateDt = models.DateTimeField(blank=True, null=True, db_column='update_dt', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_alarm_noti_grp'
        db_table_comment = '알람알림그룹'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAlarmNotiUser(models.Model):
    CmAlarmNotiGroup = models.ForeignKey('CmAlarmNotiGroup', models.DO_NOTHING, db_column='alarm_noti_grp_pk', db_comment='알람알림그룹 PK')
    UserPk = models.IntegerField(db_column='user_pk', db_comment='사용자 PK')
    NotiYn = models.CharField(db_column='noti_yn', db_comment='알림여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True,  null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_alarm_noti_user'
        db_table_comment = '알람알림사용자'
        unique_together = (('CmAlarmNotiGroup', 'UserPk'),)
    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnUserSsMtrl(models.Model):
    CmAlarmNotiGroup = models.ForeignKey('CmAlarmNotiGroup', models.DO_NOTHING, db_column='alarm_noti_grp_pk', db_comment='알람알림그룹 PK')
    UserPk = models.SmallIntegerField(db_column='user_pk', db_comment='사용자 PK')
    CmMaterial = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')

    class Meta:
        db_table = 'cm_an_user_ss_mtrl'
        db_table_comment = '알람알림사용자구독자재'

class CmAnotiMailHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_mail_hist_pk', db_comment='알림메일이력 PK')
    CmAlarmNotiGroup = models.ForeignKey('CmAlarmNotiGroup', models.DO_NOTHING, db_column='alarm_noti_grp_pk', db_comment='알람알림그룹 PK')
    MailTitle = models.CharField(max_length=100, blank=True, null=True, db_column='mail_title', db_comment='메일제목')
    MailContent = models.TextField(blank=True, null=True, db_column='mail_content', db_comment='메일내용')
    MailSndrAddr = models.CharField(max_length=40, db_column='mail_sndr_addr', db_comment='메일발신자주소')
    MailRcvrAddr = models.CharField(max_length=40, db_column='mail_rcvr_addr', db_comment='메일수신자주소')
    MailRcvrId = models.CharField(max_length=20, blank=True, null=True, db_column='mail_rcvr_id', db_comment='메일수신자 ID')
    ResultType = models.CharField(db_column='result_type', db_comment='결과유형')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    SendTs = models.DateTimeField(blank=True, null=True, db_column='send_ts', db_comment='발송일시')
    SendRmk = models.CharField(max_length=200, blank=True, null=True, db_column='send_rmk', db_comment='발송비고')
    ErrorCnt = models.SmallIntegerField(db_column='error_cnt', db_comment='에러건수')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_mail_hist'
        db_table_comment = '알림메일이력'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnotiSmsHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_sms_hist_pk', db_comment='알림SMS이력 PK')
    CmAlarmNotiGroup = models.ForeignKey('CmAlarmNotiGroup', models.DO_NOTHING, db_column='alarm_noti_grp_pk', db_comment='알람알림그룹 PK')
    SmsContent = models.CharField(max_length=150, db_column='sms_content', db_comment='SMS내용')
    SmsSndrNo = models.CharField(max_length=15, db_column='sms_sndr_no', db_comment='SMS발신번호')
    SmsRcvrNo = models.CharField(max_length=15, db_column='sms_rcvr_no', db_comment='SMS수신번호')
    SmsRcvrId = models.CharField(max_length=30, blank=True, null=True, db_column='sms_rcvr_id', db_comment='SMS수신자 ID')
    ResultType = models.CharField(db_column='result_type', db_comment='결과유형')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    SendTs = models.DateTimeField(blank=True, null=True, db_column='send_ts', db_comment='발송일시')
    SendRmk = models.CharField(max_length=200, blank=True, null=True, db_column='send_rmk', db_comment='발송비고')
    ErrorCnt = models.SmallIntegerField(db_column='error_cnt', db_comment='에러건수')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_sms_hist'
        db_table_comment = '알림SMS이력'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAttachFile(models.Model):
    id = models.AutoField(primary_key=True, db_column='file_pk', db_comment='파일 PK')
    CmAttachFileGroup = models.ForeignKey('CmAttachFileGroup', models.DO_NOTHING, db_column='file_grp_cd', db_comment='파일그룹코드')
    FileOrgName = models.CharField(max_length=300, db_column='file_org_nm', db_comment='원본파일명')
    FileStreName = models.CharField(max_length=300, blank=True, null=True, db_column='file_stre_nm', db_comment='저장파일명')
    FileExt = models.CharField(max_length=20, blank=True, null=True, db_column='file_ext', db_comment='파일확장자')
    FileSize = models.BigIntegerField(blank=True, null=True, db_column='file_size', db_comment='파일크기(Byte)')
    RootPath = models.CharField(max_length=300, blank=True, null=True, db_column='root_path', db_comment='루트경로')
    FileStreCours = models.CharField(max_length=300, blank=True, null=True, db_column='file_stre_cours', db_comment='저장경로')
    FileNote = models.CharField(max_length=100, blank=True, null=True, db_column='file_note', db_comment='파일설명')
    AttachType = models.CharField(max_length=20, blank=True, null=True, db_column='attach_type', db_comment='첨부타입')
    AttachPk = models.IntegerField(blank=True, null=True, db_column='attach_pk', db_comment='첨부대상 PK')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterPk = models.SmallIntegerField(blank=True, null=True, db_column='inserter_pk', db_comment='등록자 PK')

    class Meta:
        db_table = 'cm_attach_file'
        db_table_comment = '첨부파일'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAttachFileGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=50, db_column='attach_file_grp_cd', db_comment='첨부파일그룹코드')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    UseYn = models.CharField(blank=True, null=True, db_column='use_yn', db_comment='사용여부')

    class Meta:
        db_table = 'cm_attach_file_grp'
        db_table_comment = '첨부파일그룹'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmBaseCode(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='code_pk', db_comment='코드 PK')
    CmBaseCodeGroup = models.ForeignKey('CmBaseCodeGroup', models.DO_NOTHING, db_column='code_grp_cd', db_comment='코드그룹코드')
    CodeCd = models.CharField(max_length=50, db_column='code_cd', db_comment='코드')
    CodeName = models.CharField(max_length=100, db_column='code_nm', db_comment='코드명')
    CodeDsc = models.CharField(max_length=200, blank=True, null=True, db_column='code_dsc', db_comment='코드설명')
    GroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='grp_cd', db_comment='그룹코드')
    CodeNameEn = models.CharField(max_length=200, blank=True, null=True, db_column='code_nm_en', db_comment='코드명(영문)')
    CodeNameCh = models.CharField(max_length=200, blank=True, null=True, db_column='code_nm_ch', db_comment='코드명(중문)')
    CodeNameJp = models.CharField(max_length=200, blank=True, null=True, db_column='code_nm_jp', db_comment='코드명(일문)')
    DispOrder = models.SmallIntegerField(blank=True, null=True, db_column='disp_order', db_comment='표시순서')
    UseYn = models.CharField(blank=True, null=True, db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True,  null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')
    Attr1 = models.CharField(max_length=100, blank=True, null=True, db_column='attr1', db_comment='속성1')

    class Meta:
        db_table = 'cm_base_code'
        db_table_comment = '기준코드'
        unique_together = (('CmBaseCodeGroup', 'CodeCd'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmBaseCodeGroup(models.Model):
    CodeGroupCode = models.CharField(primary_key=True, max_length=40, db_column='code_grp_cd', db_comment='코드그룹코드')
    CodeGrpName = models.CharField(max_length=100, db_column='code_grp_nm', db_comment='코드그룹명')
    CodeGrpDsc = models.CharField(max_length=200, blank=True, null=True, db_column='code_grp_dsc', db_comment='코드그룹설명')
    EditYn = models.CharField(db_column='edit_yn', db_comment='편집가능여부')
    CodePkYn = models.CharField(blank=True, null=True, db_column='code_pk_yn', db_comment='PK여부')
    DispOrder = models.SmallIntegerField(blank=True, null=True, db_column='disp_order', db_comment='표시순서')

    class Meta:
        db_table = 'cm_base_code_grp'
        db_table_comment = '코드그룹'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmChkEquip(models.Model):
    CmEquipChkMaster = models.ForeignKey('CmEquipChkMaster', models.DO_NOTHING, db_column='chk_mast_pk', db_comment='설비점검마스터 PK')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')

    class Meta:
        db_table = 'cm_chk_equip'
        db_table_comment = '점검대상설비'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmChkItemTemplate(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='template_id', db_comment='템플릿 ID')
    ChkItem = models.CharField(max_length=200, db_column='chk_item', db_comment='점검항목')
    Unit = models.CharField(max_length=20, blank=True, null=True, db_column='unit', db_comment='단위')
    GroupCode = models.CharField(max_length=40, blank=True, null=True, db_column='group_code', db_comment='그룹코드')
    HashTag = models.CharField(max_length=100, blank=True, null=True, db_column='hash_tag', db_comment='해시태그')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_chk_item_template'
        db_table_comment = '점검항목 템플릿'
        unique_together = (('ChkItem', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmComBbs(models.Model):
    id = models.AutoField(primary_key=True, db_column='ntt_id', db_comment='게시글 ID')
    CmComBbsMaster = models.ForeignKey('CmComBbsMaster', models.DO_NOTHING, db_column='bbs_id', db_comment='게시판 ID')
    NttSj = models.CharField(max_length=2000, db_column='ntt_sj', db_comment='게시글 제목')
    NttCn = models.TextField(blank=True, null=True, db_column='ntt_cn', db_comment='게시글 내용')
    NttLev = models.IntegerField(blank=True, null=True, db_column='ntt_lev', db_comment='게시글 깊이')
    UpNttId = models.IntegerField(blank=True, null=True, db_column='up_ntt_id', db_comment='상위 게시글 ID')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    AnswerYn = models.CharField(db_column='answer_yn', db_comment='답변 여부')
    AnswerLc = models.IntegerField(blank=True, null=True, db_column='answer_lc', db_comment='답변 위치')
    DispOrder = models.IntegerField(blank=True, null=True, db_column='disp_order', db_comment='표시 순서')
    ReadCnt = models.IntegerField(blank=True, null=True, db_column='read_cnt', db_comment='조회수')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제 여부')
    NttStartDate = models.DateField(blank=True, null=True, db_column='ntt_start_date', db_comment='게시 시작일')
    NttEndDate = models.DateField(blank=True, null=True, db_column='ntt_end_date', db_comment='게시 종료일')
    NtcrUserId = models.CharField(max_length=50, db_column='ntcr_user_id', db_comment='작성자 ID')
    NtcrUserName = models.CharField(max_length=20, db_column='ntcr_user_nm', db_comment='작성자명')
    AtchFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='atch_file_grp_cd', db_comment='첨부파일 그룹코드')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_com_bbs'
        db_table_comment = '게시글'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmComBbsMaster(models.Model):
    id = models.CharField(primary_key=True, max_length=20, db_column='bbs_id', db_comment='게시판 ID')
    BbsName = models.CharField(max_length=255, db_column='bbs_nm', db_comment='게시판명')
    BbsIntrcn = models.CharField(max_length=4000, blank=True, null=True, db_column='bbs_intrcn', db_comment='게시판 소개')
    BbsTyCode = models.CharField(max_length=20, db_column='bbs_ty_cd', db_comment='게시판 유형 코드')
    BbsAttrbCode = models.CharField(max_length=20, db_column='bbs_attrb_cd', db_comment='게시판 속성 코드')
    ReplyPosblYn = models.CharField(blank=True, null=True, db_column='reply_posbl_yn', db_comment='답글 가능 여부')
    FileAtchPosblYn = models.CharField(db_column='file_atch_posbl_yn', db_comment='파일 첨부 가능 여부')
    AnswerYn = models.CharField(blank=True, null=True, db_column='answer_yn', db_comment='답변 사용 여부')
    AtchPosblFileNumber = models.IntegerField(db_column='atch_posbl_file_number', db_comment='첨부 가능 파일 개수')
    AtchPosblFileSize = models.IntegerField(blank=True, null=True, db_column='atch_posbl_file_size', db_comment='첨부 가능 파일 크기')
    UseYn = models.CharField(blank=True, null=True, db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_com_bbs_master'
        db_table_comment = '게시판 마스터'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmComComment(models.Model):
    id = models.AutoField(primary_key=True, db_column='cmmt_id', db_comment='댓글 ID')
    CmComBbs = models.ForeignKey('CmComBbs', models.DO_NOTHING, db_column='ntt_id', db_comment='게시글 ID')
    WrterUserId = models.CharField(max_length=20, db_column='wrter_user_id', db_comment='작성자 ID')
    WrterName = models.CharField(max_length=50, db_column='wrter_nm', db_comment='작성자명')
    Answer = models.CharField(max_length=200, db_column='answer', db_comment='댓글 내용')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_com_comment'
        db_table_comment = '게시판 댓글'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmCostCenter(models.Model):
    CcenterCode = models.CharField(primary_key=True, max_length=15, db_column='ccenter_cd', db_comment='코스트센터 코드')
    CcenterName = models.CharField(max_length=40, db_column='ccenter_nm', db_comment='코스트센터명')
    Remark = models.CharField(max_length=200, null=True, blank=True, db_column='remark', db_comment='비고')
    IsDeletable = models.CharField(max_length=1, null=True, blank=True, db_column='is_deletable', db_comment='완전삭제가능여부')
    UseYn = models.CharField(max_length=1, default='Y', db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자ID')
    InserterName = models.CharField(max_length=50, null=True, blank=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now=True, null=True, blank=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, null=True, blank=True, db_column='updater_id', db_comment='수정자ID')
    UpdaterName = models.CharField(max_length=50, null=True, blank=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_cost_center'
        db_table_comment = '코스트센터 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

    def __str__(self):
        return self.CcenterName

class CmDashBoardItem(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='dashboard_item_pk', db_comment='대시보드 항목 PK')
    DashboardItemCode = models.CharField(max_length=50, db_column='dashboard_item_cd', db_comment='대시보드 항목 코드')
    DashboardItemName = models.CharField(max_length=100, db_column='dashboard_item_nm', db_comment='대시보드 항목 명')
    DashboardItemUrl = models.CharField(max_length=300, blank=True, null=True, db_column='dashboard_item_url', db_comment='대시보드 항목 URL')
    DashboardItemDesc = models.CharField(max_length=500, blank=True, null=True, db_column='dashboard_item_desc', db_comment='대시보드 항목 설명')
    UseYn = models.CharField(blank=True, null=True, db_column='use_yn', db_comment='사용여부')

    class Meta:
        db_table = 'cm_dash_board_item'
        db_table_comment = '대시보드 항목'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmDept(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='dept_pk', db_comment='부서 PK')
    DeptCode = models.CharField(unique=True, max_length=20, db_column='dept_cd', db_comment='부서 코드')
    DeptName = models.CharField(max_length=100, db_column='dept_nm', db_comment='부서명')
    Parent = models.ForeignKey('self', models.DO_NOTHING, db_column='up_dept_pk', null=True, db_comment='상위 부서 PK')
    SiteId = models.CharField(max_length=20, blank=True, null=True, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    BusinessYn = models.CharField(db_column='business_yn', db_comment='사업부 여부')
    TeamYn = models.CharField(db_column='team_yn', db_comment='팀 여부')
    TpmYn = models.CharField(db_column='tpm_yn', db_comment='TPM 여부')
    TeamBusiYn = models.CharField(db_column='team_busi_yn', db_comment='팀 사업 여부')
    CcenterCode = models.CharField(max_length=30, blank=True, null=True, db_column='ccenter_cd', db_comment='코스트센터 코드')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')
    CostViewAuth = models.CharField(blank=True, null=True, db_column='cost_view_auth', db_comment='비용 보기 권한')

    class Meta:
        db_table = 'cm_dept'
        db_table_comment = '부서'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmDummyMonth(models.Model):
    VMonth = models.CharField(primary_key=True, max_length=2, db_column='v_month', db_comment='가상 월')

    class Meta:
        db_table = 'cm_dummy_month'
        db_table_comment = '가상 월 마스터'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipCategory(models.Model):
    EquipCategoryCode = models.CharField(max_length=2, primary_key=True, db_column='equip_category_id', db_comment='설비 카테고리 ID')
    EquipCategoryDesc = models.CharField(max_length=50, db_column='equip_category_desc', db_comment='설비 카테고리 이름')
    Remark = models.CharField(max_length=100, blank=True, null=True, db_column='remark', db_comment='비고')
    UseYn = models.CharField(max_length=1, db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_equip_category'
        db_table_comment = '설비 카테고리 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkItem(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='chk_item_pk', db_comment='점검항목 PK')
    CmEquipChkMaster = models.ForeignKey('CmEquipChkMaster', models.DO_NOTHING, db_column='chk_mast_pk', db_comment='점검마스터 PK')
    ItemIdx = models.SmallIntegerField(db_column='item_idx', db_comment='항목 순번')
    ChkItemName = models.CharField(max_length=200, db_column='chk_item_nm', db_comment='점검항목명')
    Lcl = models.CharField(max_length=30, blank=True, null=True, db_column='lcl', db_comment='하한값')
    Ucl = models.CharField(max_length=30, blank=True, null=True, db_column='ucl', db_comment='상한값')
    ChkItemUnitPk = models.SmallIntegerField(blank=True, null=True, db_column='chk_item_unit_pk', db_comment='단위 PK')
    Method = models.CharField(max_length=100, blank=True, null=True, db_column='method', db_comment='점검방법')
    Guide = models.CharField(max_length=150, blank=True, null=True, db_column='guide', db_comment='점검기준')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_equip_chk_item'
        db_table_comment = '설비 점검 항목'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkItemMst(models.Model):
    #ChkSchePk = models.BigIntegerField(primary_key=True, db_column='chk_sche_pk', db_comment='점검스케줄 PK')
    CmEquipChkSche = models.ForeignKey('CmEquipChkSche', models.DO_NOTHING, db_column='chk_sche_pk', db_comment='점검스케줄 PK')
    #ChkItemPk = models.BigIntegerField(db_column='chk_item_pk', db_comment='점검항목 PK')
    CmEquipChkItem = models.ForeignKey('CmEquipChkItem', models.DO_NOTHING, db_column='chk_item_pk', db_comment='점검항목 PK')
    ItemIdx = models.IntegerField(db_column='item_idx', db_comment='항목 인덱스')
    ChkItemName = models.CharField(max_length=100, db_column='chk_item_nm', db_comment='점검항목명')
    Lcl = models.CharField(max_length=30, blank=True, null=True, db_column='lcl', db_comment='하한값')
    Ucl = models.CharField(max_length=30, blank=True, null=True, db_column='ucl', db_comment='상한값')
    ChkItemUnitPk = models.SmallIntegerField(blank=True, null=True, db_column='chk_item_unit_pk', db_comment='단위 PK')

    class Meta:
        db_table = 'cm_equip_chk_item_mst'
        db_table_comment = '설비 점검 항목 마스터'
        unique_together = (('CmEquipChkSche', 'CmEquipChkItem'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkItemRslt(models.Model):
    CmEquipChkRslt = models.ForeignKey('CmEquipChkRslt', models.DO_NOTHING, db_column='chk_rslt_pk', db_comment='점검결과 PK')
    CmEquipChkItem = models.ForeignKey('CmEquipChkItem', models.DO_NOTHING, db_column='chk_item_pk', db_comment='점검항목 PK')
    CmEquipChkSche = models.ForeignKey('CmEquipChkSche', models.DO_NOTHING, db_column='chk_sche_pk', db_comment='점검스케줄 PK')
    ChkItemRslt = models.CharField(blank=True, null=True, db_column='chk_item_rslt', db_comment='점검항목 결과')
    ChkItemRsltDesc = models.CharField(max_length=1000, blank=True, null=True, db_column='chk_item_rslt_desc', db_comment='점검 결과 설명')
    ChkUserPk = models.IntegerField(db_column='chk_user_pk', null=True, db_comment='점검자 PK')
    ChkDt = models.DateTimeField(db_column='chk_dt', db_comment='점검일시')

    class Meta:
        db_table = 'cm_equip_chk_item_rslt'
        db_table_comment = '설비 점검 항목 결과'
        unique_together = (('CmEquipChkRslt', 'CmEquipChkItem'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkMaster(models.Model):
    id = models.AutoField(primary_key=True, db_column='chk_mast_pk', db_comment='점검마스터 PK')
    ChkMastNo = models.CharField(max_length=20, db_column='chk_mast_no', db_comment='점검마스터 번호')
    ChkMastName = models.CharField(max_length=100, db_column='chk_mast_nm', db_comment='점검마스터 명')
    DeptPk = models.SmallIntegerField(db_column='dept_pk', db_comment='부서 PK')
    ChkUserPk = models.IntegerField(blank=True, null=True, db_column='chk_user_pk', db_comment='점검자 PK')
    ChkYn = models.CharField(db_column='chk_yn', db_comment='점검 여부')
    CycleType = models.CharField(max_length=20, blank=True, null=True, db_column='cycle_type', db_comment='주기 유형')
    PerNumber = models.SmallIntegerField(blank=True, null=True, db_column='per_number', db_comment='주기 단위 수치')
    SchedStartDate = models.DateField(blank=True, null=True, db_column='sched_start_date', db_comment='점검 시작일')
    FirstChkDate = models.DateField(blank=True, null=True, db_column='first_chk_date', db_comment='최초 점검일')
    LastChkDate = models.DateField(blank=True, null=True, db_column='last_chk_date', db_comment='마지막 점검일')
    NextChkDate = models.DateField(blank=True, null=True, db_column='next_chk_date', db_comment='다음 점검일')
    WorkText = models.CharField(max_length=2000, blank=True, null=True, db_column='work_text', db_comment='작업 지시사항')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')
    DailyReportCode = models.CharField(max_length=50, blank=True, null=True, db_column='daily_report_cd', db_comment='일일보고 코드')
    DailyReportTypeCode = models.CharField(max_length=50, blank=True, null=True, db_column='daily_report_type_cd', db_comment='일일보고 유형 코드')

    class Meta:
        db_table = 'cm_equip_chk_mast'
        db_table_comment = '설비 점검 마스터'
        unique_together = (('ChkMastNo', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkRslt(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='chk_rslt_pk', db_comment='점검결과 PK')
    CmEquipChkSche = models.ForeignKey('CmEquipChkSche', models.DO_NOTHING, db_column='chk_sche_pk', db_comment='점검스케줄 PK')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    ChkReqType = models.CharField(blank=True, null=True, db_column='chk_req_type', db_comment='점검요청유형')
    ChkItemTot = models.SmallIntegerField(blank=True, null=True, db_column='chk_item_tot', db_comment='전체 점검항목 수')
    AbnItemCnt = models.SmallIntegerField(blank=True, null=True, db_column='abn_item_cnt', db_comment='이상 항목 수')
    ChkRslt = models.CharField(blank=True, null=True, db_column='chk_rslt', db_comment='점검결과')
    RsltDsc = models.CharField(max_length=500, blank=True, null=True, db_column='rslt_dsc', db_comment='결과 설명')
    ChkRsltFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='chk_rslt_file_grp_cd', db_comment='첨부파일 그룹코드')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_equip_chk_rslt'
        db_table_comment = '설비 점검 결과'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkSche(models.Model):
    id = models.AutoField(primary_key=True, db_column='chk_sche_pk', db_comment='점검스케줄 PK')
    ChkScheNo = models.BigIntegerField(db_column='chk_sche_no', db_comment='점검스케줄 번호')
    CmEquipChkMaster = models.ForeignKey('CmEquipChkMaster', models.DO_NOTHING, db_column='chk_mast_pk', db_comment='점검마스터 PK')
    DeptPk = models.SmallIntegerField(db_column='dept_pk', db_comment='부서 PK')
    ChkScheDt = models.DateField(db_column='chk_sche_dt', db_comment='점검예정일')
    ChkStatus = models.CharField(max_length=30, db_column='chk_status', db_comment='점검상태')
    ChkUserPk = models.SmallIntegerField(blank=True, null=True, db_column='chk_user_pk', db_comment='점검자 PK')
    ChkDt = models.DateField(blank=True, null=True, db_column='chk_dt', db_comment='실제 점검일')
    ChkScheFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='chk_sche_file_grp_cd', db_comment='첨부파일 그룹코드')
    ChkScheType = models.CharField(blank=True, null=True, db_column='chk_sche_type', db_comment='점검유형')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterNm = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_equip_chk_sche'
        db_table_comment = '설비 점검 스케줄'
        unique_together = (('ChkScheNo', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipChkScheSendLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id', db_comment='로그 ID')
    SendDt = models.DateTimeField(db_column='send_dt', db_comment='전송 일시')
    SendLog = models.TextField(db_column='send_log', db_comment='전송 로그')

    class Meta:
        db_table = 'cm_equip_chk_sche_send_log'
        db_table_comment = '설비 점검 스케줄 전송 로그'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipClassify(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='equip_class_pk', db_comment='설비분류 PK')
    EquipClassCode = models.CharField(max_length=20, db_column='equip_class_id', db_comment='설비분류 ID')
    EquipClassDesc = models.CharField(max_length=120, db_column='equip_class_desc', db_comment='설비분류 설명')
    HierarchyPath = models.CharField(max_length=50, db_column='hierarchy_path', db_comment='계층구조 경로')
    CategoryCode = models.CharField(max_length=2, blank=True, null=True, db_column='category_id', db_comment='카테고리ID')
    ParentCode = models.CharField(max_length=20, blank=True, null=True, db_column='parent_id', db_comment='상위클래스ID')
    ClassType = models.CharField(max_length=5, db_column='class_type', db_comment='클래스 타입')
    #Site = models.ForeignKey('CmSites', models.DO_NOTHING, db_column='site_id', db_comment='사이트ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(max_length=1, db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_equip_classify'
        db_table_comment = '설비분류 정보'
        unique_together = (('EquipClassCode', 'ParentCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipDeptHist(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='equip_dept_hist_pk', db_comment='설비관리부서 변경이력 PK')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', null=True, db_comment='설비 PK')
    EquipDeptBefore = models.CharField(max_length=200, db_column='equip_dept_bef', db_comment='변경전 관리부서')
    EquipDeptAfter = models.CharField(max_length=200, db_column='equip_dept_aft', db_comment='변경후 관리부서')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')

    class Meta:
        db_table = 'cm_equip_dept_hist'
        db_table_comment = '설비관리부서 변경이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipLocHist(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='equip_loc_hist_pk', db_comment='설비위치 변경이력 PK')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    EquipLocBefore = models.CharField(max_length=200, db_column='equip_loc_bef', db_comment='변경전 설비위치')
    EquipLocAfter = models.CharField(max_length=200, db_column='equip_loc_aft', db_comment='변경후 설비위치')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')

    class Meta:
        db_table = 'cm_equip_loc_hist'
        db_table_comment = '설비위치 변경이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipPartMtrl(models.Model):
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    CmMaterial = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    Amt = models.SmallIntegerField(null=True, blank=True, db_column='amt', db_comment='구성수량')
    CumulAmt = models.SmallIntegerField(null=True, blank=True, db_column='cumul_amt', db_comment='누적수량')
    UseYn = models.CharField(max_length=1, db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(max_length=1, db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(null=True, auto_now_add=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, null=True, blank=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, null=True, blank=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_equip_part_mtrl'
        db_table_comment = '설비부품자재 정보'
        unique_together = (('CmEquipment', 'CmMaterial'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipSpec(models.Model):
    id = models.AutoField(primary_key=True, db_column='equip_spec_pk', db_comment='설비사양 PK')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    EquipSpecName = models.CharField(max_length=60, db_column='equip_spec_nm', db_comment='사양명칭')
    EquipSpecUnit = models.CharField(max_length=20, blank=True, null=True, db_column='equip_spec_unit', db_comment='사양단위')
    EquipSpecValue = models.CharField(max_length=100, blank=True, null=True, db_column='equip_spec_value', db_comment='사양값')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_equip_spec'
        db_table_comment = '설비사양 정보'
        unique_together = (('CmEquipment', 'EquipSpecName'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmEquipment(models.Model):
    id = models.AutoField(primary_key=True, db_column='equip_pk', db_comment='설비 PK')
    EquipCode = models.CharField(max_length=20, db_column='equip_cd', db_comment='설비 코드')
    EquipName = models.CharField(max_length=200, db_column='equip_nm', db_comment='설비 명')
    CmEquipCategory = models.ForeignKey('CmEquipCategory', models.DO_NOTHING, db_column='equip_category_id', db_comment='설비 카테고리')
    Parent = models.ForeignKey('self', models.DO_NOTHING, db_column='up_equip_pk', blank=True, null=True, db_comment='상위설비 PK')
    CmLocation = models.ForeignKey('CmLocation', models.DO_NOTHING, db_column='loc_pk', db_comment='위치 PK')
    EquipStatus = models.CharField(max_length=20, db_column='equip_status', db_comment='설비 상태')
    SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    EquipClassPath = models.CharField(max_length=20, blank=True, null=True, db_column='equip_class_path', db_comment='설비 분류')
    EquipClassDesc = models.CharField(max_length=120, blank=True, null=True, db_column='equip_class_desc', db_comment='설비 분류 설명')
    DeptPk = models.SmallIntegerField(db_column='dept_pk', db_comment='관리부서 PK')
    AssetNos = models.CharField(max_length=500, blank=True, null=True, db_column='asset_nos', db_comment='자산 번호')
    MakeDt = models.DateField(blank=True, null=True, db_column='make_dt', db_comment='제조일')
    InstallDt = models.DateField(blank=True, null=True, db_column='install_dt', db_comment='설치일')
    WarrantyDt = models.DateField(blank=True, null=True, db_column='warranty_dt', db_comment='보증만료일')
    BuyCost = models.BigIntegerField(blank=True, null=True, db_column='buy_cost', db_comment='구매비용')
    MakerPk = models.SmallIntegerField(blank=True, null=True, db_column='maker_pk', db_comment='제조사 PK')
    ModelNumber = models.CharField(max_length=100, blank=True, null=True, db_column='model_number', db_comment='모델넘버')
    SerialNumber = models.CharField(max_length=100, blank=True, null=True, db_column='serial_number', db_comment='시리얼넘버')
    CmMaterial = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_pk', blank=True, null=True, db_comment='자재대상설비 PK')
    CmSupplier = models.ForeignKey('CmSupplier', models.DO_NOTHING, db_column='supplier_pk', blank=True, null=True, db_comment='공급업체 PK')
    PhotoFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='photo_file_grp_cd', db_comment='사진첨부파일그룹코드')
    DocFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='doc_file_grp_cd', db_comment='문서첨부파일코드')
    CmImportRank = models.ForeignKey('CmImportRank', models.DO_NOTHING, db_column='import_rank_pk', blank=True, null=True, db_comment='중요도등급 PK')
    EnvironEquipYn = models.CharField(max_length=1, db_column='environ_equip_yn', db_comment='환경설비여부')
    CcenterCode = models.CharField(max_length=30, blank=True, null=True, db_column='ccenter_cd', db_comment='Cost Center 코드')
    BreakdownDt = models.DateField(blank=True, null=True, db_column='breakdown_dt', db_comment='고장일시')
    DisposedType = models.CharField(max_length=10, blank=True, null=True, db_column='disposed_type', db_comment='불용처리타입')
    DisposedDate = models.DateField(blank=True, null=True, db_column='disposed_date', db_comment='불용처리일자')
    EquipDsc = models.CharField(max_length=2000, blank=True, null=True, db_column='equip_dsc', db_comment='비고')
    UseYn = models.CharField(max_length=1, db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(max_length=1, db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')
    ProcessCode = models.CharField(max_length=20, blank=True, null=True, db_column='process_cd', db_comment='프로세스 코드')
    SystemCode = models.CharField(max_length=20, blank=True, null=True, db_column='system_cd', db_comment='시스템 코드')
    FirstAssetStatus = models.CharField(max_length=20, blank=True, null=True, db_column='first_asset_status', db_comment='최초자산상태')

    class Meta:
        db_table = 'cm_equipment'
        db_table_comment = '설비 정보'
        unique_together = (('EquipCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmErrorLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='error_log_pk', db_comment='에러 로그 PK')
    ErrorLogType = models.CharField(max_length=50, db_column='error_log_type', db_comment='에러 로그 유형')
    ErrorLogTitle = models.CharField(max_length=200, db_column='error_log_title', db_comment='에러 제목')
    ErrorLogDesc = models.TextField(db_column='error_log_desc', db_comment='에러 설명')
    InsertTs = models.DateTimeField(db_column='insert_ts', db_comment='등록일시')

    class Meta:
        db_table = 'cm_error_log'
        db_table_comment = '에러 로그'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmExSupplier(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='ex_supplier_pk', db_comment='외부업체 PK')
    ExSupplierCode = models.CharField(max_length=50, db_column='ex_supplier_cd', db_comment='외부업체 코드')
    ExSupplierName = models.CharField(max_length=200, db_column='ex_supplier_nm', db_comment='외부업체명')
    CeoName = models.CharField(max_length=80, blank=True, null=True, db_column='ceo_nm', db_comment='대표자명')
    ChargerName = models.CharField(max_length=80, blank=True, null=True, db_column='charger_nm', db_comment='담당자명')
    BusinessClassName = models.CharField(max_length=200, blank=True, null=True, db_column='business_class_nm', db_comment='업종')
    ExSupplierDsc = models.CharField(max_length=4000, blank=True, null=True, db_column='ex_supplier_dsc', db_comment='비고')
    Nation = models.CharField(max_length=50, blank=True, null=True, db_column='nation', db_comment='국가')
    ZipCode = models.CharField(max_length=6, blank=True, null=True, db_column='zip_code', db_comment='우편번호')
    Address1 = models.CharField(max_length=300, blank=True, null=True, db_column='address1', db_comment='주소1')
    Address2 = models.CharField(max_length=300, blank=True, null=True, db_column='address2', db_comment='주소2')
    Phone = models.CharField(max_length=100, blank=True, null=True, db_column='phone', db_comment='전화번호')
    Fax = models.CharField(blank=True, null=True, db_column='fax', db_comment='팩스')
    Homepage = models.CharField(max_length=100, blank=True, null=True, db_column='homepage', db_comment='홈페이지')
    EmailAddr = models.CharField(max_length=100, blank=True, null=True, db_column='email_addr', db_comment='이메일')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_ex_supplier'
        db_table_comment = '외부업체 정보'
        unique_together = (('ExSupplierCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmHelpFaq(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='help_faq_pk', db_comment='FAQ PK')
    FaqTitle = models.CharField(max_length=300, db_column='faq_title', db_comment='질문')
    FaqAnswer = models.TextField(blank=True, null=True, db_column='faq_answer', db_comment='답변')
    HashTag = models.CharField(max_length=400, blank=True, null=True, db_column='hash_tag', db_comment='해시태그')
    LangCode = models.CharField(max_length=20, blank=True, null=True, db_column='lang_cd', db_comment='언어코드')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_help_faq'
        db_table_comment = 'FAQ 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmHelpItem(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='help_item_pk', db_comment='헬프항목 PK')
    HelpItemName = models.CharField(max_length=100, db_column='help_item_nm', db_comment='헬프항목명')
    HelpItemConts = models.TextField(blank=True, null=True, db_column='help_item_conts', db_comment='헬프내용')
    HelpItemType = models.CharField(max_length=20, blank=True, null=True, db_column='help_item_type', db_comment='헬프유형')
    HelpItemClass = models.CharField(max_length=20, blank=True, null=True, db_column='help_item_class', db_comment='헬프분류')
    TableName = models.CharField(max_length=100, blank=True, null=True, db_column='table_nm', db_comment='테이블명')
    ColumnName = models.CharField(max_length=100, blank=True, null=True, db_column='column_nm', db_comment='컬럼명')
    LangCode = models.CharField(max_length=20, blank=True, null=True, db_column='lang_cd', db_comment='언어코드')
    HashTag = models.CharField(max_length=400, blank=True, null=True, db_column='hash_tag', db_comment='해시태그')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')

    class Meta:
        db_table = 'cm_help_item'
        db_table_comment = '헬프 항목 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmHolidayCustom(models.Model):
    NationCode = models.CharField(max_length=10, db_column='nation_cd', db_comment='국가코드')
    YearVal = models.CharField(max_length=4, db_column='year_val', db_comment='년도')
    MonthVal = models.CharField(max_length=2, db_column='month_val', db_comment='월')
    DayVal = models.CharField(max_length=2, db_column='day_val', db_comment='일')
    TypeVal = models.CharField(max_length=1, blank=True, null=True, db_column='type_val', db_comment='유형')
    NameVal = models.CharField(max_length=100, db_column='name_val', db_comment='휴일명')
    RepeatYn = models.CharField(db_column='repeat_yn', db_comment='반복여부')

    class Meta:
        db_table = 'cm_holiday_custom'
        db_table_comment = '사용자 정의 휴일'
        unique_together = (('NationCode', 'YearVal', 'MonthVal', 'DayVal'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmHolidayInfo(models.Model):
    NationCode = models.CharField(primary_key=True, max_length=10, db_column='nation_cd', db_comment='국가코드')
    YearVal = models.CharField(max_length=4, db_column='year_val', db_comment='년도')
    MonthVal = models.CharField(max_length=2, db_column='month_val', db_comment='월')
    DayVal = models.CharField(max_length=2, db_column='day_val', db_comment='일')
    TypeVal = models.CharField(max_length=1, blank=True, null=True, db_column='type_val', db_comment='유형')
    NameVal = models.CharField(max_length=100, db_column='name_val', db_comment='휴일명')

    class Meta:
        db_table = 'cm_holiday_info'
        db_table_comment = '국가별 공휴일 정보'
        unique_together = (('NationCode', 'YearVal', 'MonthVal', 'DayVal'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmI18N(models.Model):
    LangCode = models.CharField(primary_key=True, max_length=100, db_column='lang_code', db_comment='언어코드')
    LangDesc = models.CharField(max_length=200, blank=True, null=True, db_column='lang_desc', db_comment='언어설명')
    DefMsg = models.CharField(max_length=200, db_column='def_msg', db_comment='기본메시지')

    class Meta:
        db_table = 'cm_i18n'
        db_table_comment = '국제화 기본 메시지'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmI18NDtl(models.Model):
    LangType = models.CharField(max_length=5, db_column='lang_type', db_comment='언어유형')
    LangCode = models.CharField(max_length=100, db_column='lang_code', db_comment='언어코드')
    LangMsg = models.CharField(max_length=200, db_column='lang_msg', db_comment='언어메시지')

    class Meta:
        db_table = 'cm_i18n_dtl'
        db_table_comment = '국제화 다국어 메시지'
        unique_together = (('LangType', 'LangCode'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmI18NLang(models.Model):
    LangType = models.CharField(primary_key=True, max_length=5, db_column='lang_type', db_comment='언어유형')
    LangName = models.CharField(max_length=50, db_column='lang_name', db_comment='언어명')

    class Meta:
        db_table = 'cm_i18n_lang'
        db_table_comment = '국제화 언어 유형'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmIfErpAssetInfo(models.Model):
    AssetNo = models.CharField(primary_key=True, max_length=100, db_column='asset_no', db_comment='자산번호')
    AssetDesc = models.CharField(max_length=300, db_column='asset_desc', db_comment='자산명')
    AssetTypeName = models.CharField(max_length=300, blank=True, null=True, db_column='asset_type_nm', db_comment='자산유형명')
    FixAssetLdgrDesc = models.CharField(max_length=100, blank=True, null=True, db_column='fix_asset_ldgr_desc', db_comment='고정자산원장')
    Uom = models.CharField(max_length=10, blank=True, null=True, db_column='uom', db_comment='단위')
    AssetQnty = models.CharField(max_length=15, blank=True, null=True, db_column='asset_qnty', db_comment='수량')
    FixAssetMajCatName = models.CharField(max_length=300, blank=True, null=True, db_column='fix_asset_maj_cat_nm', db_comment='대분류')
    FixAssetMnCatName = models.CharField(max_length=300, blank=True, null=True, db_column='fix_asset_mn_cat_nm', db_comment='중분류')
    FixAssetSubCatName = models.CharField(max_length=300, blank=True, null=True, db_column='fix_asset_sub_cat_nm', db_comment='소분류')
    AuCode = models.CharField(max_length=30, blank=True, null=True, db_column='au_cd', db_comment='AU 코드')
    AuName = models.CharField(max_length=150, blank=True, null=True, db_column='au_nm', db_comment='AU 명칭')
    DeptCode = models.CharField(max_length=30, blank=True, null=True, db_column='dept_cd', db_comment='부서코드')
    DeptName = models.CharField(max_length=100, blank=True, null=True, db_column='dept_nm', db_comment='부서명')
    CmmsDeptCode = models.CharField(max_length=20, blank=True, null=True, db_column='cmms_dept_cd', db_comment='CMMS 부서코드')
    MstAttr1 = models.CharField(max_length=300, blank=True, null=True, db_column='mst_attr1', db_comment='기타속성')
    EmpNo = models.CharField(max_length=30, blank=True, null=True, db_column='emp_no', db_comment='사번')
    EmpName = models.CharField(max_length=100, blank=True, null=True, db_column='emp_nm', db_comment='사원명')
    AssetAcqDate = models.CharField(max_length=8, blank=True, null=True, db_column='asset_acq_date', db_comment='취득일자')
    OrigAcqCost = models.CharField(max_length=15, blank=True, null=True, db_column='orig_acq_cost', db_comment='취득원가')
    CurrntCostAmt = models.CharField(max_length=15, blank=True, null=True, db_column='currnt_cost_amt', db_comment='현재가치')
    DeprnAccuAmt = models.CharField(max_length=15, blank=True, null=True, db_column='deprn_accu_amt', db_comment='감가상각누계')
    ImpairAccuAmt = models.CharField(max_length=15, blank=True, null=True, db_column='impair_accu_amt', db_comment='손상누계액')
    NetAssetValue = models.CharField(max_length=15, blank=True, null=True, db_column='net_asset_value', db_comment='순자산가치')
    UpdtDt = models.CharField(max_length=14, blank=True, null=True, db_column='updt_dt', db_comment='업데이트일시')
    HidenYn = models.CharField(db_column='hiden_yn', db_comment='숨김여부')
    InsertDt = models.DateTimeField(db_column='insert_dt', db_comment='등록일시')
    UpdateDt = models.DateTimeField(blank=True, null=True, db_column='update_dt', db_comment='수정일시')

    class Meta:
        db_table = 'cm_if_erp_asset_info'
        db_table_comment = 'ERP 연계 자산정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmImportRank(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='import_rank_pk', db_comment='중요도등급 PK')
    ImportRankCode = models.CharField(max_length=10, unique=True, db_column='import_rank_cd', db_comment='중요도등급 코드')
    ImportRankDesc = models.CharField(max_length=400, blank=True, null=True, db_column='import_rank_desc', db_comment='설명')
    UseYn = models.CharField(max_length=1, blank=True, null=True, db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(max_length=1, blank=True, null=True, db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_import_rank'
        db_table_comment = '중요도등급 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmJobClass(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='job_class_pk', db_comment='직무등급 PK')
    JobClassCode = models.CharField(max_length=20, db_column='job_class_cd', db_comment='직무등급 코드')
    JobClassName = models.CharField(max_length=50, db_column='job_class_nm', db_comment='직무등급 명칭')
    WageCost = models.BigIntegerField(blank=True, null=True, db_column='wage_cost', db_comment='인건비')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_job_class'
        db_table_comment = '직무등급 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmLabelRptForm(models.Model):
    FormCode = models.CharField(primary_key=True, max_length=7, db_column='form_cd', db_comment='라벨양식 코드')
    FormName = models.CharField(max_length=30, db_column='form_nm', db_comment='라벨양식 명칭')
    FormKinds = models.CharField(max_length=6, db_column='form_kinds', db_comment='양식종류')
    SrcConts = models.CharField(max_length=6, db_column='src_conts', db_comment='출처내용')
    DefaultYn = models.CharField(db_column='default_yn', db_comment='기본 여부')
    ContsText = models.CharField(max_length=2000, blank=True, null=True, db_column='conts_text', db_comment='내용 텍스트')
    ContsFile = models.CharField(max_length=50, blank=True, null=True, db_column='conts_file', db_comment='내용 파일')
    Remark = models.CharField(max_length=50, blank=True, null=True, db_column='remark', db_comment='비고')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_label_rpt_form'
        db_table_comment = '라벨 출력 양식'
        unique_together = (('FormCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmLocMapMarker(models.Model):
    LocCode = models.CharField(primary_key=True, max_length=30, db_column='loc_cd', db_comment='위치 코드')
    MarkerType = models.CharField(db_column='marker_type', db_comment='마커 유형')
    MarkerInfo = models.TextField(db_column='marker_info', db_comment='마커 정보')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_loc_map_marker'
        db_table_comment = '위치 마커 정보'
        unique_together = (('LocCode', 'MarkerType'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmLocation(models.Model):
    LocPk = models.AutoField(primary_key=True, db_column='loc_pk', db_comment='로케이션 PK')
    LocName = models.CharField(max_length=100, db_column='loc_nm', db_comment='로케이션명')
    LocCode = models.CharField(max_length=30, db_column='loc_cd', db_comment='로케이션 코드')
    UpLocPk = models.ForeignKey('self', models.DO_NOTHING, db_column='up_loc_pk', null=True, blank=True, db_comment='상위 로케이션 PK')
    LocStatus = models.CharField(max_length=10, db_column='loc_status', db_comment='로케이션 상태')
    SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    PlantYn = models.CharField(max_length=1, db_column='plant_yn', default='N', null=True, blank=True, db_comment='공장 여부')
    BuildingYn = models.CharField(max_length=1, db_column='building_yn', default='N', null=True, blank=True, db_comment='건물 여부')
    SpshopYn = models.CharField(max_length=1, db_column='spshop_yn', default='N', null=True, blank=True, db_comment='특수공정 여부')
    Isa95Class = models.CharField(max_length=10, db_column='isa95_class', null=True, blank=True, db_comment='ISA-95 Class')
    MapDrawFileCd = models.CharField(max_length=50, db_column='map_draw_file_cd', null=True, blank=True, db_comment='도면 파일 코드')
    OutOrder = models.SmallIntegerField(db_column='out_order', default=99, db_comment='표시 순서')
    UseYn = models.CharField(max_length=1, db_column='use_yn', default='Y', null=True, blank=True, db_comment='사용 여부')
    DelYn = models.CharField(max_length=1, db_column='del_yn', default='N', null=True, blank=True, db_comment='삭제 여부')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자ID')
    InserterName = models.CharField(max_length=50, null=True, blank=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now=True, null=True, blank=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, null=True, blank=True, db_column='updater_id', db_comment='수정자ID')
    UpdaterName = models.CharField(max_length=50, null=True, blank=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_location'
        db_table_comment = '위치 정보'
        unique_together = (('LocCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
    def __str__(self):
        return self.LocName

class CmLoginsLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='logins_pk', db_comment='로그인이력 PK')
    LoginUserId = models.CharField(max_length=20, db_column='login_user_id', db_comment='로그인사용자 ID')
    EventTs = models.DateTimeField(db_column='event_ts', db_comment='이벤트일시')
    EventType = models.CharField(max_length=2, db_column='event_type', db_comment='이벤트유형')
    LoginReason = models.CharField(max_length=200, blank=True, null=True, db_column='login_reason', db_comment='로그인이유')
    LoginIp = models.CharField(max_length=46, db_column='login_ip', db_comment='로그인 IP')
    LoginUseragent = models.CharField(max_length=150, db_column='login_useragent', db_comment='로그인사용자에이전트')
    LoginUrl = models.CharField(max_length=100, db_column='login_url', db_comment='로그인 URL')
    LoginUuid = models.CharField(max_length=50, blank=True, null=True, db_column='login_uuid', db_comment='로그인 UUID')
    TokenRefreshTs = models.DateTimeField(blank=True, null=True, db_column='token_refresh_ts', db_comment='토큰갱신일시')
    SendYn = models.CharField(blank=True, null=True, db_column='send_yn', db_comment='발송여부')
    SendRslt = models.TextField(blank=True, null=True, db_column='send_rslt', db_comment='발송결과')

    class Meta:
        db_table = 'cm_logins_log'
        db_table_comment = '로그인이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmMaterial(models.Model):
    id = models.AutoField(primary_key=True, db_column='mtrl_pk', db_comment='자재 PK')
    MtrlCode = models.CharField(max_length=40, db_column='mtrl_cd', db_comment='자재 코드')
    MtrlName = models.CharField(max_length=150, db_column='mtrl_nm', db_comment='자재 명칭')
    MtrlClassCodePk = models.SmallIntegerField(db_column='mtrl_class_cd_pk', db_comment='자재분류 코드 PK')
    MtrlDsc = models.CharField(max_length=4000, blank=True, null=True, db_column='mtrl_dsc', db_comment='자재 설명')
    MakerPk = models.SmallIntegerField(blank=True, null=True, db_column='maker_pk', db_comment='제조사 PK')
    SafetyStockAmt = models.SmallIntegerField(db_column='safety_stock_amt', db_comment='안전재고수량')
    AmtUnitPk = models.SmallIntegerField(blank=True, null=True, db_column='amt_unit_pk', db_comment='수량 단위 PK')
    UnitPrice = models.BigIntegerField(blank=True, null=True, db_column='unit_price', db_comment='단가')
    UnitPriceDt = models.DateField(blank=True, null=True, db_column='unit_price_dt', db_comment='단가 기준일')
    CmSupplier = models.ForeignKey('CmSupplier', models.DO_NOTHING, db_column='supplier_pk', blank=True, null=True, db_comment='공급업체 PK')
    DeliveryDays = models.SmallIntegerField(blank=True, null=True, db_column='delivery_days', db_comment='납기일수')
    DeliveryType = models.CharField(blank=True, null=True, db_column='delivery_type', db_comment='납기유형')
    ErpMtrlCode = models.CharField(max_length=50, blank=True, null=True, db_column='erp_mtrl_cd', db_comment='ERP 자재코드')
    PhotoFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='photo_file_grp_cd', db_comment='사진 파일그룹 코드')
    AttachFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='attach_file_grp_cd', db_comment='첨부 파일그룹 코드')
    AllowAddBom = models.CharField(db_column='allow_add_bom', db_comment='BOM 추가 허용 여부')
    SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')
    MtrlBarcode = models.CharField(max_length=300, blank=True, null=True, db_column='mtrl_barcode', db_comment='자재 바코드')
    ConstructionPk = models.SmallIntegerField(blank=True, null=True, db_column='construction_pk', db_comment='공사 PK')
    EquipmentPk = models.SmallIntegerField(blank=True, null=True, db_column='equipment_pk', db_comment='설비 PK')
    CommonMtrlCode = models.CharField(max_length=40, blank=True, null=True, db_column='common_mtrl_cd', db_comment='공통 자재코드')

    class Meta:
        db_table = 'cm_material'
        db_table_comment = '자재 정보'
        unique_together = (('MtrlCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmMenu(models.Model):
    id = models.CharField(primary_key=True, max_length=10, db_column='menu_id', db_comment='메뉴 ID')
    MenuName = models.CharField(max_length=50, db_column='menu_nm', db_comment='메뉴 명')
    Parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True, db_column='up_menu', db_comment='상위 메뉴')
    CmProgram = models.ForeignKey('CmProgram', models.DO_NOTHING, blank=True, null=True, db_column='prog', db_comment='프로그램')
    MenuIcon = models.CharField(max_length=30, blank=True, null=True, db_column='menu_icon', db_comment='메뉴 아이콘')
    MobileYn = models.CharField(blank=True, null=True, db_column='mobile_yn', db_comment='모바일 여부')
    DispOrder = models.IntegerField(blank=True, null=True, db_column='disp_order', db_comment='표시 순서')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_menu'
        db_table_comment = '메뉴 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmMtrlInout(models.Model):
    id = models.AutoField(primary_key=True, db_column='mtrl_inout_pk', db_comment='자재 입출고 PK')
    CmMaterial = models.ForeignKey(CmMaterial, models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    OwnDeptCode = models.CharField(max_length=20, blank=True, null=True, db_column='own_dept_cd', db_comment='소유부서 코드')
    InoutLocCode = models.CharField(max_length=30, blank=True, null=True, db_column='inout_loc_cd', db_comment='입출고 위치코드')
    InoutDiv = models.CharField(max_length=30, db_column='inout_div', db_comment='입출고 구분')
    InoutType = models.CharField(max_length=5, db_column='inout_type', db_comment='입출고 유형')
    InoutUprice = models.BigIntegerField(blank=True, null=True, db_column='inout_uprice', db_comment='단가')
    InoutQty = models.SmallIntegerField(db_column='inout_qty', db_comment='입출고 수량')
    InoutDt = models.DateTimeField(db_column='inout_dt', db_comment='입출고 일시')
    AbGrade = models.CharField(max_length=10, db_column='ab_grade', db_comment='등급')
    LocCellAddr = models.CharField(max_length=5, db_column='loc_cell_addr', db_comment='위치 주소')
    StockedDt = models.DateField(blank=True, null=True, db_column='stocked_dt', db_comment='재고반영일')
    CmSupplier = models.ForeignKey('CmSupplier', models.DO_NOTHING, db_column='supplier_pk', blank=True, null=True, db_comment='공급업체 PK')
    WorkOrderPk = models.BigIntegerField(blank=True, null=True, db_column='work_order_pk', db_comment='작업지시 PK')
    CmPinvLoc = models.ForeignKey('CmPinvLoc', models.DO_NOTHING, db_column='pinv_loc_pk', blank=True, null=True, db_comment='실사위치 PK')
    MtrlRemark = models.CharField(max_length=4000, blank=True, null=True, db_column='mtrl_remark', db_comment='비고')
    InoutCxYn = models.CharField(blank=True, null=True, db_column='inout_cx_yn', db_comment='입출고 취소 여부')
    InoutCxDesc = models.CharField(max_length=400, blank=True, null=True, db_column='inout_cx_desc', db_comment='입출고 취소 설명')
    InoutCxDt = models.DateTimeField(blank=True, null=True, db_column='inout_cx_dt', db_comment='입출고 취소일시')
    InoutCxUserPk = models.SmallIntegerField(blank=True, null=True, db_column='inout_cx_user_pk', db_comment='입출고 취소 사용자')
    InputerPk = models.SmallIntegerField(blank=True, null=True, db_column='inputer_pk', db_comment='입력자 PK')
   # SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_mtrl_inout'
        db_table_comment = '자재 입출고 이력'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmMtrlSubstitute(models.Model):
    #MtrlPk = models.IntegerField(primary_key=True, db_column='mtrl_pk', db_comment='자재 PK')
    CmMaterial = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    #MtrlSubstitutePk = models.IntegerField(db_column='mtrl_substitute_pk', db_comment='대체 자재 PK')
    CmMaterialSubstitute = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_substitute_pk', db_comment='대체자재 PK',  related_name='CmMaterialSubstitute')
    OutOrdr = models.SmallIntegerField(blank=True, null=True, db_column='out_ordr', db_comment='정렬 순서')

    class Meta:
        db_table = 'cm_mtrl_substitute'
        db_table_comment = '자재 대체 정보'
        unique_together = (('CmMaterial', 'CmMaterialSubstitute'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmMttrMtbfInfo(models.Model):
    InfoYear = models.CharField(max_length=4, db_column='info_year', db_comment='년도')
    InfoType = models.CharField(max_length=4, db_column='info_type', db_comment='정보 타입')
    EquipCode = models.CharField(max_length=20, db_column='equip_cd', db_comment='설비 코드')
    MtVal = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, db_column='mt_val', db_comment='MT 또는 MTBF 값')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    DispOrdr = models.SmallIntegerField(blank=True, null=True, db_column='disp_ordr', db_comment='정렬 순서')

    class Meta:
        db_table = 'cm_mttr_mtbf_info'
        db_table_comment = 'MTTR/MTBF 기준 정보'
        unique_together = (('InfoYear', 'InfoType', 'EquipCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmOperationsLog(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='operations_pk', db_comment='작업이력 PK')
    UserId = models.CharField(max_length=20, db_column='user_id', db_comment='사용자 ID')
    ActionCode = models.CharField(max_length=8, db_column='action_cd', db_comment='작업 코드')
    ActionTs = models.DateTimeField(db_column='action_ts', db_comment='작업 일시')
    MenuId = models.CharField(max_length=10, db_column='menu_id', db_comment='메뉴 ID')
    MenuName = models.CharField(max_length=50, db_column='menu_nm', db_comment='메뉴 명')
    CodeCond = models.TextField(blank=True, null=True, db_column='code_cond', db_comment='조건 코드')
    DataSize = models.IntegerField(blank=True, null=True, db_column='data_size', db_comment='데이터 크기')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    SendYn = models.CharField(blank=True, null=True, db_column='send_yn', db_comment='발송 여부')
    SendRslt = models.TextField(blank=True, null=True, db_column='send_rslt', db_comment='발송 결과')

    class Meta:
        db_table = 'cm_operations_log'
        db_table_comment = '작업이력 로그'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPermission(models.Model):
    id = models.CharField(primary_key=True, max_length=10, db_column='permission_id', db_comment='권한 ID')
    PermissionName = models.CharField(max_length=40, db_column='permission_nm', db_comment='권한 이름')
    PermissionDsc = models.CharField(max_length=400, blank=True, null=True, db_column='permission_dsc', db_comment='권한 설명')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_permission'
        db_table_comment = '권한 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPinvLoc(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='pinv_loc_pk', db_comment='실사위치 PK')
    PinvLocTitle = models.CharField(max_length=200, db_column='pinv_loc_title', db_comment='실사명')
    PinvLocSdate = models.DateField(db_column='pinv_loc_sdate', db_comment='시작일')
    PinvLocEdate = models.DateField(db_column='pinv_loc_edate', db_comment='종료일')
    LocCode = models.CharField(max_length=30, db_column='loc_cd', db_comment='위치 코드')
    PinvLocStatus = models.CharField(max_length=10, db_column='pinv_loc_status', db_comment='상태')
    PinvLocDate = models.DateTimeField(blank=True, null=True, db_column='pinv_loc_date', db_comment='실사일시')
    PinvLocUserId = models.CharField(max_length=50, blank=True, null=True, db_column='pinv_loc_user_id', db_comment='실사자 ID')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    DelYn = models.CharField(blank=True, null=True, db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_pinv_loc'
        db_table_comment = '자재 실사 위치'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPinvLocMtrl(models.Model):
    CmPinvLoc = models.ForeignKey(CmPinvLoc, models.DO_NOTHING, db_column='pinv_loc_pk', db_comment='실사위치 PK')
    MtrlCode = models.CharField(max_length=40, db_column='mtrl_cd', db_comment='자재 코드')
    OwnDeptCode = models.CharField(max_length=20, blank=True, null=True, db_column='own_dept_cd', db_comment='소유 부서 코드')
    LocCode = models.CharField(max_length=30, db_column='loc_cd', db_comment='위치 코드')
    StockUprice = models.BigIntegerField(db_column='stock_uprice', db_comment='단가')
    AbGrade = models.CharField(max_length=10, db_column='ab_grade', db_comment='등급')
    LocCellAddr = models.CharField(max_length=5, db_column='loc_cell_addr', db_comment='셀 주소')
    StockedDt = models.DateField(db_column='stocked_dt', db_comment='재고 기준일')
    LastStockQty = models.SmallIntegerField(blank=True, null=True, db_column='last_stock_qty', db_comment='이전 재고 수량')
    SurveyStockQty = models.SmallIntegerField(blank=True, null=True, db_column='survey_stock_qty', db_comment='실사 수량')

    class Meta:
        db_table = 'cm_pinv_loc_mtrl'
        db_table_comment = '자재 실사 정보'
        unique_together = (('MtrlCode', 'CmPinvLoc', 'LocCode', 'StockUprice', 'AbGrade', 'LocCellAddr', 'StockedDt'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPm(models.Model):
    id = models.AutoField(primary_key=True, db_column='pm_pk', db_comment='PM PK')
    PmNo = models.CharField(db_column='pm_no', max_length=20, db_comment='PM 번호')
    PmName = models.CharField(db_column='pm_nm', max_length=100, db_comment='PM 명')
    PmNoSort = models.IntegerField(db_column='pm_no_sort', null=True, blank=True, db_comment='PM 번호 소팅')
    CmEquipment = models.ForeignKey(CmEquipment, models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    DeptPk = models.SmallIntegerField(db_column='dept_pk', null=True, blank=True, db_comment='작업부서 PK')
    PmUserPk = models.SmallIntegerField(db_column='pm_user_pk', null=True, blank=True, db_comment='작업담당자 PK')
    CycleType = models.CharField(db_column='cycle_type', max_length=20, null=True, blank=True, db_comment='주기단위 코드')
    PerNumber = models.SmallIntegerField(db_column='per_number', null=True, blank=True, db_comment='PM 주기')
    SchedStartDt = models.DateField(db_column='sched_start_dt', null=True, blank=True, db_comment='주기시작일')
    FirstWorkDt = models.DateField(db_column='first_work_dt', null=True, blank=True, db_comment='최초시작일')
    LastWorkDt = models.DateField(db_column='last_work_dt', null=True, blank=True, db_comment='최종PM생성일')
    NextChkDate = models.DateField(db_column='next_chk_date', null=True, blank=True, db_comment='다음점검주기생성기준일')
    WorkText = models.CharField(db_column='work_text', max_length=4000, null=True, blank=True, db_comment='작업지침')
    WorkExpectHr = models.SmallIntegerField(db_column='work_expect_hr', null=True, blank=True, db_comment='정비예상시간')
    PmType = models.CharField(db_column='pm_type', max_length=20, db_comment='PM 유형 코드')
    #SiteId = models.CharField(db_column='site_id', max_length=20, db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(db_column='use_yn', max_length=1, db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', max_length=1, db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(db_column='inserter_id', max_length=20, db_comment='등록자 ID')
    InserterName = models.CharField(db_column='inserter_nm', max_length=50, null=True, blank=True, db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, db_column='update_ts', null=True, blank=True, db_comment='수정일시')
    UpdaterId = models.CharField(db_column='updater_id', max_length=20, null=True, blank=True, db_comment='수정자 ID')
    UpdaterName = models.CharField(db_column='updater_nm', max_length=50, null=True, blank=True, db_comment='수정자명')

    class Meta:
        db_table = 'cm_pm'
        db_table_comment = '예방정비 정보'
        unique_together = (('PmNo', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPmLabor(models.Model):
    CmPm = models.ForeignKey(CmPm, models.DO_NOTHING, db_column='pm_pk', db_comment='PM PK')
    CmJobClass = models.ForeignKey(CmJobClass, models.DO_NOTHING, db_column='job_class_pk', db_comment='직종 PK')
    WorkHr = models.DecimalField(db_column='work_hr', max_digits=7, decimal_places=2, null=True, blank=True, db_comment='작업시간')
    DispOrdr = models.SmallIntegerField(db_column='disp_ordr', null=True, blank=True, db_comment='순번')

    class Meta:
        db_table = 'cm_pm_labor'
        db_table_comment = 'PM 인력 정보'
        unique_together = (('CmJobClass', 'CmPm'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPmMtrl(models.Model):
    CmPm = models.OneToOneField(CmPm, models.DO_NOTHING, db_column='pm_pk', db_comment='PM PK')
    CmMaterial = models.ForeignKey(CmMaterial, models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    Amt = models.SmallIntegerField(db_column='amt', default=0, db_comment='소요량')

    class Meta:
        db_table = 'cm_pm_mtrl'
        db_table_comment = 'PM 자재 정보'
        unique_together = (('CmPm', 'CmMaterial'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPmScheSendLog(models.Model):
    Id = models.BigAutoField(primary_key=True, db_column='id', db_comment='ID')
    SendDt = models.DateTimeField(db_column='send_dt', db_comment='발송일시')
    SendLog = models.TextField(db_column='send_log', db_comment='발송로그')

    class Meta:
        db_table = 'cm_pm_sche_send_log'
        db_table_comment = 'PM 스케줄 발송 로그'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmPopInfo(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='popup_pk', db_comment='팝업 PK')
    PopupTitle = models.CharField(max_length=200, db_column='popup_title', db_comment='팝업 제목')
    PopupType = models.CharField(db_column='popup_type', db_comment='팝업 유형')
    PopupConts = models.TextField(blank=True, null=True, db_column='popup_conts', db_comment='팝업 내용')
    FileUrl = models.CharField(max_length=300, blank=True, null=True, db_column='file_url', db_comment='파일 URL')
    PopupWidthLoc = models.CharField(max_length=20, blank=True, null=True, db_column='popup_width_loc', db_comment='가로 위치')
    PopupHeightLoc = models.CharField(max_length=20, blank=True, null=True, db_column='popup_height_loc', db_comment='세로 위치')
    PopupWidthSize = models.IntegerField(blank=True, null=True, db_column='popup_width_size', db_comment='가로 크기')
    PopupHeightSize = models.IntegerField(blank=True, null=True, db_column='popup_height_size', db_comment='세로 크기')
    StartDate = models.DateField(db_column='start_date', db_comment='시작일')
    EndDate = models.DateField(db_column='end_date', db_comment='종료일')
    StopViewYn = models.CharField(blank=True, null=True, db_column='stop_view_yn', db_comment='다시보지 않기 여부')
    NoticeYn = models.CharField(blank=True, null=True, db_column='notice_yn', db_comment='공지 여부')

    class Meta:
        db_table = 'cm_pop_info'
        db_table_comment = '팝업 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmProgram(models.Model):
    id = models.CharField(primary_key=True, max_length=5, db_column='prog_id', db_comment='프로그램 ID')
    ProgName = models.CharField(max_length=100, db_column='prog_nm', db_comment='프로그램 명')
    ProgPath = models.CharField(max_length=200, blank=True, null=True, db_column='prog_path', db_comment='프로그램 경로')
    ProgDesc = models.CharField(max_length=200, blank=True, null=True, db_column='prog_desc', db_comment='프로그램 설명')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용 여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제 여부')

    class Meta:
        db_table = 'cm_prog'
        db_table_comment = '프로그램 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmProject(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='proj_pk', db_comment='프로젝트 PK')
    ProjCode = models.CharField(max_length=30, unique=True, db_column='proj_cd', db_comment='프로젝트 코드')
    ProjName = models.CharField(max_length=200, db_column='proj_nm', db_comment='프로젝트 명')
    PlanStartDt = models.DateField(db_column='plan_start_dt', db_comment='계획 시작일')
    PlanEndDt = models.DateField(db_column='plan_end_dt', db_comment='계획 종료일')
    ManagerId = models.CharField(max_length=20, blank=True, null=True, db_column='manager_id', db_comment='담당자 ID')
    ProjPurpose = models.CharField(max_length=4000, blank=True, null=True, db_column='proj_purpose', db_comment='프로젝트 목적')
    ProjTotCost = models.IntegerField(blank=True, null=True, db_column='proj_tot_cost', db_comment='총 비용')
    Status = models.CharField(max_length=8, db_column='status', db_comment='상태')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_project'
        db_table_comment = '프로젝트 정보'
        unique_together = (('ProjCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmReliabCodes(models.Model):
    ReliabCode = models.CharField(max_length=8, db_column='reliab_cd', db_comment='신뢰도 코드')
    ReliabName = models.CharField(max_length=50, db_column='reliab_nm', db_comment='신뢰도 명')
    Types = models.CharField(db_column='types', db_comment='타입')
    Remark = models.CharField(max_length=100, blank=True, null=True, db_column='remark', db_comment='비고')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(db_column='use_yn', db_comment='사용 여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_reliab_codes'
        db_table_comment = '신뢰도 코드 정보'
        unique_together = (('ReliabCode', 'Types', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmRole(models.Model):
    RoleCode = models.CharField(primary_key=True, max_length=4, db_column='role_cd', db_comment='역할 코드')
    RoleName = models.CharField(max_length=40, db_column='role_nm', db_comment='역할 명')
    UserType = models.CharField(db_column='user_type', db_comment='사용자 유형')
    RoleDesc = models.CharField(max_length=100, blank=True, null=True, db_column='role_desc', db_comment='역할 설명')

    class Meta:
        db_table = 'cm_role'
        db_table_comment = '역할 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmRoleMenu(models.Model):
    RoleCode = models.CharField(max_length=4, db_column='role_cd', db_comment='역할 코드')
    CmMenu = models.ForeignKey('CmMenu', models.DO_NOTHING, db_column='menu_id', db_comment='메뉴 ID')
    ReadYn = models.CharField(db_column='read_yn', db_comment='읽기 권한 여부')
    WriteYn = models.CharField(db_column='write_yn', db_comment='쓰기 권한 여부')

    class Meta:
        db_table = 'cm_role_menu'
        db_table_comment = '역할별 메뉴 권한'
        unique_together = (('RoleCode', 'CmMenu'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmRolePermission(models.Model):
    RoleCode = models.CharField(max_length=4, db_column='role_cd', primary_key=True, db_comment='역할 코드')
    CmPermission = models.ForeignKey('CmPermission', models.DO_NOTHING, db_column='permission_id', db_comment='권한 ID')

    class Meta:
        db_table = 'cm_role_permission'
        db_table_comment = '역할별 권한 설정'
        unique_together = (('RoleCode', 'CmPermission'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmScheLog(models.Model):
    Id = models.BigAutoField(primary_key=True, db_column='id', db_comment='ID')
    SendDt = models.DateTimeField(db_column='send_dt', db_comment='발송일시')
    SendLog = models.TextField(db_column='send_log', db_comment='발송 로그')

    class Meta:
        db_table = 'cm_sche_log'
        db_table_comment = '스케줄 발송 로그'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmSiteConfig(models.Model):
    Site = models.OneToOneField('CmSites', models.DO_NOTHING, primary_key=True, db_column='site', db_comment='사이트 ID')
    ProcOpts = models.TextField(db_column='proc_opts', db_comment='처리 옵션')
    ScheOpts = models.TextField(blank=True, null=True, db_column='sche_opts', db_comment='스케줄 옵션')
    ExtOpts = models.TextField(blank=True, null=True, db_column='ext_opts', db_comment='확장 옵션')
    SvcOpts = models.TextField(blank=True, null=True, db_column='svc_opts', db_comment='서비스 옵션')
    UserPolicy = models.TextField(blank=True, null=True, db_column='user_policy', db_comment='사용자 정책')

    class Meta:
        db_table = 'cm_site_config'
        db_table_comment = '사이트별 설정 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmSites(models.Model):
    id = models.CharField(primary_key=True, max_length=20, db_column='site_id', db_comment='사이트 ID')
    SiteDesc = models.CharField(max_length=100, db_column='site_desc', db_comment='사이트 설명')
    SiteManager = models.CharField(max_length=20, blank=True, null=True, db_column='site_manager', db_comment='사이트 관리자')
    Status = models.CharField(db_column='status', db_comment='상태')
    CcuCount = models.SmallIntegerField(db_column='ccu_count', db_comment='CCU 수')
    MapDrawFileCode = models.CharField(max_length=50, blank=True, null=True, db_column='map_draw_file_cd', db_comment='맵 그리기 파일 코드')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_sites'
        db_table_comment = '사이트 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmStorLocAddr(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='stor_loc_addr_pk', db_comment='보관 위치 주소 PK')
    LocCode = models.CharField(max_length=30, db_column='loc_cd', db_comment='위치 코드')
    LocCellAddr = models.CharField(max_length=5, db_column='loc_cell_addr', db_comment='셀 주소')
    RackNo = models.CharField(max_length=2, db_column='rack_no', db_comment='랙 번호')
    LevelNo = models.CharField(max_length=2, db_column='level_no', db_comment='레벨 번호')
    ColNo = models.CharField(max_length=2, db_column='col_no', db_comment='열 번호')
    OutUnavailYn = models.CharField(db_column='out_unavail_yn', db_comment='출고 불가 여부')
    UseYn = models.CharField(blank=True, null=True, db_column='use_yn', db_comment='사용 여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_stor_loc_addr'
        db_table_comment = '보관 위치 주소 정보'
        unique_together = (('LocCode', 'LocCellAddr'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmSupplier(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='supplier_pk', db_comment='공급업체 PK')
    SupplierCode = models.CharField(max_length=50, db_column='supplier_cd', db_comment='공급업체 코드')
    SupplierName = models.CharField(max_length=200, db_column='supplier_nm', db_comment='공급업체명')
    CeoName = models.CharField(max_length=80, blank=True, null=True, db_column='ceo_nm', db_comment='대표자명')
    ChargerName = models.CharField(max_length=40, blank=True, null=True, db_column='charger_nm', db_comment='담당자명')
    ChargerTel = models.CharField(max_length=20, blank=True, null=True, db_column='charger_tel', db_comment='담당자 전화번호')
    Charger2Name = models.CharField(max_length=40, blank=True, null=True, db_column='charger2_nm', db_comment='보조담당자명')
    Charger2Tel = models.CharField(max_length=20, blank=True, null=True, db_column='charger2_tel', db_comment='보조담당자 전화번호')
    CompType = models.CharField(max_length=5, blank=True, null=True, db_column='comp_type', db_comment='기업유형')
    BusinessClassName = models.CharField(max_length=200, blank=True, null=True, db_column='business_class_nm', db_comment='업종명')
    SupplierDsc = models.CharField(max_length=4000, blank=True, null=True, db_column='supplier_dsc', db_comment='공급업체 설명')
    Nation = models.CharField(max_length=50, blank=True, null=True, db_column='nation', db_comment='국가')
    Local = models.CharField(max_length=30, blank=True, null=True, db_column='local', db_comment='지역')
    ZipCode = models.CharField(max_length=6, blank=True, null=True, db_column='zip_code', db_comment='우편번호')
    Address1 = models.CharField(max_length=300, blank=True, null=True, db_column='address1', db_comment='주소1')
    Address2 = models.CharField(max_length=300, blank=True, null=True, db_column='address2', db_comment='주소2')
    Phone = models.CharField(max_length=100, blank=True, null=True, db_column='phone', db_comment='전화번호')
    Fax = models.CharField(max_length=100, blank=True, null=True, db_column='fax', db_comment='팩스')
    Homepage = models.CharField(max_length=100, blank=True, null=True, db_column='homepage', db_comment='홈페이지')
    EmailAddr = models.CharField(max_length=100, blank=True, null=True, db_column='email_addr', db_comment='이메일 주소')
    SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_supplier'
        db_table_comment = '공급업체 정보'
        unique_together = (('SupplierCode', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmSysOpt(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='sys_opt_pk', db_comment='시스템옵션 PK')
    SysOpts = models.TextField(blank=True, null=True, db_column='sys_opts', db_comment='시스템 옵션')

    class Meta:
        db_table = 'cm_sys_opt'
        db_table_comment = '시스템 옵션 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmTag(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='tag_pk', db_comment='태그 PK')
    Tag = models.CharField(unique=True, max_length=100, db_column='tag', db_comment='태그명')
    TagDesc = models.CharField(max_length=200, blank=True, null=True, db_column='tag_desc', db_comment='태그 설명')
    CmEquipment = models.ForeignKey(CmEquipment, models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    CmTagMeasType = models.ForeignKey('CmTagMeasType', models.DO_NOTHING, db_column='tag_meas_type_pk', db_comment='측정유형 PK')
    MeasPoint = models.CharField(max_length=50, blank=True, null=True, db_column='meas_point', db_comment='측정지점')
    SrcSystem = models.CharField(max_length=4, db_column='src_system', db_comment='출처 시스템')
    SrcTag = models.CharField(max_length=100, db_column='src_tag', db_comment='출처 태그')
    SrcIpAddr = models.CharField(max_length=40, blank=True, null=True, db_column='src_ip_addr', db_comment='출처 IP 주소')
    MeasSensor = models.CharField(max_length=50, blank=True, null=True, db_column='meas_sensor', db_comment='센서')
    AlarmTrouble = models.CharField(max_length=100, blank=True, null=True, db_column='alarm_trouble', db_comment='알람 트러블')
    WarnLow = models.FloatField(blank=True, null=True, db_column='warn_low', db_comment='경고 하한')
    WarnHigh = models.FloatField(blank=True, null=True, db_column='warn_high', db_comment='경고 상한')
    DangerLow = models.FloatField(blank=True, null=True, db_column='danger_low', db_comment='위험 하한')
    DangerHigh = models.FloatField(blank=True, null=True, db_column='danger_high', db_comment='위험 상한')
    DecPlace = models.SmallIntegerField(blank=True, null=True, db_column='dec_place', db_comment='소수점 자리수')
    AlarmChkYn = models.CharField(blank=True, null=True, db_column='alarm_chk_yn', db_comment='알람 체크 여부')
    ChartGroupCode = models.CharField(max_length=3, blank=True, null=True, db_column='chart_grp_cd', db_comment='차트 그룹 코드')
    DataRes = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True, db_column='data_res', db_comment='데이터 해상도')
    DispOrder = models.SmallIntegerField(blank=True, null=True, db_column='disp_order', db_comment='표시 순서')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_tag'
        db_table_comment = '태그 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmTagData(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='tag_data_pk', db_comment='태그 데이터 PK')
    CmTag = models.ForeignKey(CmTag, models.DO_NOTHING, db_column='tag_pk', db_comment='태그 PK')
    DataDt = models.DateTimeField(db_column='data_dt', db_comment='데이터 시각')
    DataVal = models.FloatField(db_column='data_val', db_comment='데이터 값')
    DataId = models.CharField(max_length=30, blank=True, null=True, db_column='data_id', db_comment='데이터 식별자')

    class Meta:
        db_table = 'cm_tag_data'
        db_table_comment = '태그 실시간 데이터'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmTagMeasType(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='tag_meas_type_pk', db_comment='측정유형 PK')
    MeasTypeName = models.CharField(unique=True, max_length=50, db_column='meas_type_nm', db_comment='측정유형명')
    MeasUnit = models.CharField(max_length=10, db_column='meas_unit', db_comment='측정단위')
    AlarmDispType = models.CharField(max_length=2, db_column='alarm_disp_type', db_comment='알람 표시유형')
    DispOrder = models.SmallIntegerField(db_column='disp_order', db_comment='표시순서')
    UseYn = models.CharField(blank=True, null=True, db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_tag_meas_type'
        db_table_comment = '태그 측정유형'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmUserDashboard(models.Model):
    UserPk = models.IntegerField(db_column='user_pk', db_comment='사용자 PK')
    DashboardItemPk = models.SmallIntegerField(db_column='dashboard_item_pk', db_comment='대시보드 항목 PK')
    PosiX = models.IntegerField(blank=True, null=True, db_column='posi_x', db_comment='X 좌표')
    PosiY = models.IntegerField(blank=True, null=True, db_column='posi_y', db_comment='Y 좌표')
    DashboardCont = models.CharField(max_length=2000, blank=True, null=True, db_column='dashboard_cont', db_comment='대시보드 내용')

    class Meta:
        db_table = 'cm_user_dashboard'
        db_table_comment = '사용자 대시보드 설정'
        unique_together = (('UserPk', 'DashboardItemPk'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmUserFav(models.Model):
    UserPk = models.IntegerField(db_column='user_pk', db_comment='사용자 PK')
    CmMenu = models.ForeignKey(CmMenu, models.DO_NOTHING, db_comment='메뉴')
    DispOrdr = models.SmallIntegerField(null=True, db_column='disp_ordr', db_comment='표시순서')

    class Meta:
        db_table = 'cm_user_fav'
        db_table_comment = '사용자 즐겨찾기 메뉴'
        unique_together = (('UserPk', 'CmMenu'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmUserInfo(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='user_pk', db_comment='사용자 PK')
    UserName = models.CharField(max_length=60, db_column='user_nm', db_comment='사용자 이름')
    DeptPk = models.SmallIntegerField(db_column='dept_pk', db_comment='부서 PK')
    UserType = models.CharField(max_length=2, blank=True, null=True, db_column='user_type', db_comment='사용자 유형')
    LoginId = models.CharField(max_length=50, db_column='login_id', db_comment='로그인 ID')
    UserPassword = models.CharField(max_length=255, db_column='user_password', db_comment='비밀번호')
    AdminYn = models.CharField(db_column='admin_yn', db_comment='관리자 여부')
    UseLangCode = models.CharField(max_length=10, blank=True, null=True, db_column='use_lang_cd', db_comment='사용 언어 코드')
    #SiteId = models.CharField(max_length=20, blank=True, null=True, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    TempPasswordYn = models.CharField(blank=True, null=True, db_column='temp_password_yn', db_comment='임시 비밀번호 여부')
    UserMail = models.CharField(max_length=50, blank=True, null=True, db_column='user_mail', db_comment='이메일')
    UserPhone = models.CharField(max_length=20, blank=True, null=True, db_column='user_phone', db_comment='전화번호')
    JobClassPk = models.SmallIntegerField(blank=True, null=True, db_column='job_class_pk', db_comment='직종 PK')
    EmpNo = models.CharField(max_length=30, blank=True, null=True, db_column='emp_no', db_comment='사원번호')
    JobPos = models.CharField(max_length=25, blank=True, null=True, db_column='job_pos', db_comment='직급')
    LeaderYn = models.CharField(db_column='leader_yn', db_comment='리더 여부')
    Salt = models.CharField(max_length=100, blank=True, null=True, db_column='salt', db_comment='비밀번호 SALT')
    AllowLogin = models.CharField(db_column='allow_login', db_comment='로그인 허용 여부')
    SiteChangeYn = models.CharField(blank=True, null=True, db_column='site_change_yn', db_comment='사이트 변경 가능 여부')
    NotifyWoRejected = models.CharField(blank=True, null=True, db_column='notify_wo_rejected', db_comment='작업지시 반려 알림 여부')
    NotifyWoClosed = models.CharField(blank=True, null=True, db_column='notify_wo_closed', db_comment='작업지시 완료 알림 여부')
    NotifyWoAssigned = models.CharField(blank=True, null=True, db_column='notify_wo_assigned', db_comment='작업지시 배정 알림 여부')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용 여부')
    DelYn = models.CharField(db_column='del_yn', db_comment='삭제 여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_user_info'
        db_table_comment = '사용자 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmUserRole(models.Model):
    UserPk = models.IntegerField(db_column='user_pk', db_comment='사용자 PK')
    CmRole = models.ForeignKey('CmRole', models.DO_NOTHING, db_column='role_cd', db_comment='권한 코드')

    class Meta:
        db_table = 'cm_user_role'
        db_table_comment = '사용자 권한 매핑'
        unique_together = (('UserPk', 'CmRole'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmUserTokenStore(models.Model):
    Id = models.SmallAutoField(primary_key=True, db_column='id', db_comment='토큰 저장 PK')
    UserPk = models.SmallIntegerField(db_column='user_pk', db_comment='사용자 PK')
    RefreshToken = models.CharField(max_length=600, blank=True, null=True, db_column='refresh_token', db_comment='리프레시 토큰')
    LoginId = models.CharField(max_length=20, blank=True, null=True, db_column='login_id', db_comment='로그인 ID')
    IpAddr = models.CharField(max_length=40, blank=True, null=True, db_column='ip_addr', db_comment='IP 주소')
    ExpiredTime = models.CharField(max_length=50, blank=True, null=True, db_column='expired_time', db_comment='만료시간')
    UpdateTs = models.DateTimeField(auto_now_add=True, db_column='update_ts', db_comment='수정일시')
    AccessToken = models.CharField(max_length=500, blank=True, null=True, db_column='access_token', db_comment='엑세스 토큰')
    ExpiredRfsTime = models.CharField(max_length=50, blank=True, null=True, db_column='expired_rfs_time', db_comment='리프레시 만료시간')
    UserAgent = models.CharField(max_length=150, blank=True, null=True, db_column='user_agent', db_comment='사용자 에이전트')
    Uuid = models.CharField(max_length=50, blank=True, null=True, db_column='uuid', db_comment='UUID')
    AutoLogout = models.CharField(max_length=200, blank=True, null=True, db_column='auto_logout', db_comment='자동 로그아웃 여부')

    class Meta:
        db_table = 'cm_user_token_store'
        db_table_comment = '사용자 토큰 저장소'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmVDeptPk(models.Model):
    Max = models.SmallIntegerField(blank=True, null=True, db_column='max', db_comment='최대 부서 PK')

    class Meta:
        db_table = 'cm_v_dept_pk'
        db_table_comment = '부서 PK 뷰'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmWoFaultLoc(models.Model):
    CmWorkOrder = models.ForeignKey('CmWorkOrder', models.DO_NOTHING, db_column='work_order_pk', db_comment='작업지시 PK')
    FaultLocCode = models.CharField(max_length=20, db_column='fault_loc_cd', db_comment='고장위치 코드')
    FaultLocDesc = models.CharField(max_length=100, blank=True, null=True, db_column='fault_loc_desc', db_comment='고장위치 설명')
    CauseCode = models.CharField(max_length=8, db_column='cause_cd', db_comment='고장 원인 코드')
    InsertDt = models.DateTimeField(db_column='insert_dt', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')

    class Meta:
        db_table = 'cm_wo_fault_loc'
        db_table_comment = '작업지시 고장위치'
        unique_together = (('CmWorkOrder', 'FaultLocCode'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmWoLabor(models.Model):
    CmWorkOrder = models.ForeignKey('CmWorkOrder', models.DO_NOTHING, db_column='work_order_pk', db_comment='작업지시 PK')
    EmpPk = models.IntegerField(db_column='emp_pk', null=True, db_comment='사용자 PK')
    CmJobClass = models.ForeignKey(CmJobClass, models.DO_NOTHING, db_column='job_class_pk', blank=True, null=True, db_comment='직종 PK')
    LaborPrice = models.BigIntegerField(blank=True, null=True, db_column='labor_price', db_comment='노무비')
    WorkerNos = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True, db_column='worker_nos', db_comment='작업자 수')
    WorkHr = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, db_column='work_hr', db_comment='작업시간')
    RealWorkHr = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, db_column='real_work_hr', db_comment='실작업시간')
    LaborDsc = models.CharField(max_length=100, blank=True, null=True, db_column='labor_dsc', db_comment='비고')

    class Meta:
        db_table = 'cm_wo_labor'
        db_table_comment = '작업지시 인력'
        unique_together = (('CmWorkOrder', 'EmpPk', 'CmJobClass'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 

class CmWoMtrl(models.Model):
    CmWorkOrder = models.ForeignKey('CmWorkOrder', models.DO_NOTHING, db_column='work_order_pk', db_comment='작업지시 PK')
    CmMaterial = models.ForeignKey(CmMaterial, models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    UnitPrice = models.DecimalField(max_digits=9, decimal_places=0, db_column='unit_price', db_comment='단가')
    LocCode = models.CharField(max_length=30, blank=True, null=True, db_column='loc_cd', db_comment='위치코드')
    OwnDeptCode = models.CharField(max_length=20, blank=True, null=True, db_column='own_dept_cd', db_comment='소유부서코드')
    AbGrade = models.CharField(max_length=10, blank=True, null=True, db_column='ab_grade', db_comment='등급')
    PlanAmt = models.SmallIntegerField(blank=True, null=True, db_column='plan_amt', db_comment='계획수량')
    AAmt = models.SmallIntegerField(blank=True, null=True, db_column='a_amt', db_comment='소모수량 A')
    BAmt = models.SmallIntegerField(blank=True, null=True, db_column='b_amt', db_comment='소모수량 B')

    class Meta:
        db_table = 'cm_wo_mtrl'
        db_table_comment = '작업지시 자재'
        unique_together = (('CmWorkOrder', 'CmMaterial', 'UnitPrice', 'LocCode', 'OwnDeptCode', 'AbGrade'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmWorkOrder(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='work_order_pk', db_comment='작업지시 PK')
    WorkOrderNo = models.CharField(max_length=40, blank=True, null=True, db_column='work_order_no', db_comment='작업지시 번호')
    WoStatus = models.CharField(max_length=20, db_column='wo_status', db_comment='작업지시 상태')
    WorkTitle = models.CharField(max_length=200, db_column='work_title', db_comment='작업명')
    CmEquipment = models.ForeignKey(CmEquipment, models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    WoType = models.CharField(max_length=20, blank=True, null=True, db_column='wo_type', db_comment='작업유형')
    MaintTypeCode = models.CharField(max_length=20, blank=True, null=True, db_column='maint_type_cd', db_comment='보전유형 코드')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    ReqDeptBusiCode = models.CharField(max_length=20, blank=True, null=True, db_column='req_dept_busi_cd', db_comment='요청부서 사업코드')
    ReqDeptPk = models.SmallIntegerField(blank=True, null=True, db_column='req_dept_pk', db_comment='요청부서 PK')
    ReqInfo = models.TextField(blank=True, null=True, db_column='req_info', db_comment='요청내용')
    ReqInfoImgGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='req_info_img_grp_cd', db_comment='요청 이미지 그룹 코드')
    WantDt = models.DateTimeField(blank=True, null=True, db_column='want_dt', db_comment='요청일시')
    BreakdownDt = models.DateTimeField(blank=True, null=True, db_column='breakdown_dt', db_comment='고장일시')
    BreakdownMin = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='breakdown_min', db_comment='고장시간(분)')
    ProblemCode = models.CharField(max_length=8, blank=True, null=True, db_column='problem_cd', db_comment='문제 코드')
    CauseCode = models.CharField(max_length=8, blank=True, null=True, db_column='cause_cd', db_comment='원인 코드')
    RemedyCode = models.CharField(max_length=8, blank=True, null=True, db_column='remedy_cd', db_comment='조치 코드')
    PlanStartDt = models.DateField(blank=True, null=True, db_column='plan_start_dt', db_comment='계획 시작일')
    PlanEndDt = models.DateField(blank=True, null=True, db_column='plan_end_dt', db_comment='계획 종료일')
    StartDt = models.DateTimeField(blank=True, null=True, db_column='start_dt', db_comment='작업 시작일시')
    EndDt = models.DateTimeField(blank=True, null=True, db_column='end_dt', db_comment='작업 종료일시')
    DeptPk = models.SmallIntegerField(db_column='dept_pk', db_comment='작업부서 PK')
    WorkChargerPk = models.IntegerField(db_column='work_charger_pk', null=True, db_comment='작업 담당자 PK')
    WorkText = models.TextField(blank=True, null=True, db_column='work_text', db_comment='작업내용')
    WorkTextImgGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='work_text_img_grp_cd', db_comment='작업내용 이미지그룹코드')
    WorkSrcCode = models.CharField(max_length=20, blank=True, null=True, db_column='work_src_cd', db_comment='작업 소스 코드')
    TotCost = models.BigIntegerField(blank=True, null=True, db_column='tot_cost', db_comment='총 비용')
    MtrlCost = models.BigIntegerField(blank=True, null=True, db_column='mtrl_cost', db_comment='자재 비용')
    LaborCost = models.BigIntegerField(blank=True, null=True, db_column='labor_cost', db_comment='인력 비용')
    OutsideCost = models.BigIntegerField(blank=True, null=True, db_column='outside_cost', db_comment='외주 비용')
    EtcCost = models.BigIntegerField(blank=True, null=True, db_column='etc_cost', db_comment='기타 비용')
    ChkRsltPk = models.BigIntegerField(blank=True, null=True, db_column='chk_rslt_pk', db_comment='점검결과 PK')
    #PmPk = models.IntegerField(blank=True, null=True, db_column='pm_pk', db_comment='PM PK')
    CmPm = models.ForeignKey('CmPm', models.DO_NOTHING, null=True, db_column='pm_pk', db_comment='PM PK')

    PmReqType = models.CharField(db_column='pm_req_type', db_comment='PM 요청유형')
    ProjCode = models.CharField(db_column='proj_cd', blank=True, null=True, db_comment='프로젝트 코드')
    WorkOrderSort = models.BigIntegerField(blank=True, null=True, db_column='work_order_sort', db_comment='작업정렬순서')
    RqstInspYn = models.CharField(db_column='rqst_insp_yn', db_comment='검사요청 여부')
    RqstDprYn = models.CharField(db_column='rqst_dpr_yn', db_comment='DPR요청 여부')
    ApprLine = models.CharField(max_length=50, blank=True, null=True, db_column='appr_line', db_comment='결재라인')
    ApprLineNext = models.CharField(max_length=10, blank=True, null=True, db_column='appr_line_next', db_comment='다음 결재자')
    CmWorkOrderApproval = models.ForeignKey('CmWorkOrderApproval', models.DO_NOTHING, db_column='work_order_approval_pk', db_comment='작업지시 결재 PK')
    WoFileGroupCode = models.CharField(max_length=50, blank=True, null=True, db_column='wo_file_grp_cd', db_comment='파일 그룹 코드')
    IfSendYn = models.CharField(blank=True, null=True, db_column='if_send_yn', db_comment='IF 전송 여부')
    TempNo = models.CharField(max_length=100, blank=True, null=True, db_column='temp_no', db_comment='임시번호')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')
    CostType = models.CharField(max_length=20, blank=True, null=True, db_column='cost_type', db_comment='비용유형')
    QualityImpactYn = models.CharField(blank=True, null=True, db_column='quality_impact_yn', db_comment='품질영향 여부')

    class Meta:
        db_table = 'cm_work_order'
        db_table_comment = '작업지시 정보'
        unique_together = (('WorkOrderNo', 'Factory_id'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmWorkOrderApproval(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='work_order_approval_pk', db_comment='작업지시결재 PK')
    RqstUserPk = models.SmallIntegerField(blank=True, null=True, db_column='rqst_user_pk', db_comment='요청자 PK')
    RqstUserName = models.CharField(max_length=50, blank=True, null=True, db_column='rqst_user_nm', db_comment='요청자명')
    RqstDt = models.DateTimeField(blank=True, null=True, db_column='rqst_dt', db_comment='요청일시')
    AcceptUserPk = models.SmallIntegerField(blank=True, null=True, db_column='accept_user_pk', db_comment='접수자 PK')
    AcceptUserName = models.CharField(max_length=50, blank=True, null=True, db_column='accept_user_nm', db_comment='접수자명')
    AcceptDt = models.DateTimeField(blank=True, null=True, db_column='accept_dt', db_comment='접수일시')
    ApprUserPk = models.SmallIntegerField(blank=True, null=True, db_column='appr_user_pk', db_comment='결재자 PK')
    ApprUserName = models.CharField(max_length=50, blank=True, null=True, db_column='appr_user_nm', db_comment='결재자명')
    ApprDt = models.DateTimeField(blank=True, null=True, db_column='appr_dt', db_comment='결재일시')
    CancelUserPk = models.SmallIntegerField(blank=True, null=True, db_column='cancel_user_pk', db_comment='취소자 PK')
    CancelUserName = models.CharField(max_length=50, blank=True, null=True, db_column='cancel_user_nm', db_comment='취소자명')
    CancelDt = models.DateTimeField(blank=True, null=True, db_column='cancel_dt', db_comment='취소일시')
    CancelReason = models.CharField(max_length=500, blank=True, null=True, db_column='cancel_reason', db_comment='취소사유')
    RejectUserPk = models.SmallIntegerField(blank=True, null=True, db_column='reject_user_pk', db_comment='반려자 PK')
    RejectUserName = models.CharField(max_length=50, blank=True, null=True, db_column='reject_user_nm', db_comment='반려자명')
    RejectDt = models.DateTimeField(blank=True, null=True, db_column='reject_dt', db_comment='반려일시')
    RejectReason = models.CharField(max_length=500, blank=True, null=True, db_column='reject_reason', db_comment='반려사유')
    WoStatus = models.CharField(max_length=20, db_column='wo_status', db_comment='작업지시 상태')
    RegUserPk = models.SmallIntegerField(db_column='reg_user_pk', db_comment='등록자 PK')
    RegUserName = models.CharField(max_length=100, db_column='reg_user_nm', db_comment='등록자명')
    RegDt = models.DateTimeField(db_column='reg_dt', db_comment='등록일시')
    FinishUserPk = models.SmallIntegerField(blank=True, null=True, db_column='finish_user_pk', db_comment='완료자 PK')
    FinishUserName = models.CharField(max_length=50, blank=True, null=True, db_column='finish_user_nm', db_comment='완료자명')
    FinishDt = models.DateTimeField(blank=True, null=True, db_column='finish_dt', db_comment='완료일시')
    WorkFinishUserPk = models.SmallIntegerField(blank=True, null=True, db_column='work_finish_user_pk', db_comment='작업완료자 PK')
    WorkFinishUserName = models.CharField(max_length=50, blank=True, null=True, db_column='work_finish_user_nm', db_comment='작업완료자명')
    WorkFinishDt = models.DateTimeField(blank=True, null=True, db_column='work_finish_dt', db_comment='작업완료일시')

    class Meta:
        db_table = 'cm_work_order_approval'
        db_table_comment = '작업지시 결재 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmWorkOrderHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='work_order_hist_pk', db_comment='작업지시이력 PK')
    CmWorkOrder = models.ForeignKey(CmWorkOrder, models.DO_NOTHING, db_column='work_order_pk', db_comment='작업지시 PK')
    BeforeStatus = models.CharField(max_length=20, db_column='before_status', db_comment='이전상태')
    AfterStatus = models.CharField(max_length=20, blank=True, null=True, db_column='after_status', db_comment='이후상태')
    ChangeTs = models.DateTimeField(db_column='change_ts', db_comment='변경일시')
    ChangerPk = models.SmallIntegerField(db_column='changer_pk', db_comment='변경자 PK')
    ChangerName = models.CharField(max_length=100, db_column='changer_nm', db_comment='변경자명')
    ChangeReason = models.CharField(max_length=500, blank=True, null=True, db_column='change_reason', db_comment='변경사유')

    class Meta:
        db_table = 'cm_work_order_hist'
        db_table_comment = '작업지시 이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmWorkOrderSupplier(models.Model):
    CmWorkOrder = models.ForeignKey(CmWorkOrder, models.DO_NOTHING, db_column='work_order_pk', db_comment='작업지시 PK')
    CmExSupplier = models.ForeignKey(CmExSupplier, models.DO_NOTHING, db_column='ex_supplier_pk', db_comment='외부업체 PK')
    Cost = models.BigIntegerField(blank=True, null=True, db_column='cost', db_comment='외주비용')

    class Meta:
        db_table = 'cm_work_order_supplier'
        db_table_comment = '작업지시 외부업체 정보'
        unique_together = (('CmWorkOrder', 'CmExSupplier'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnotiTalkHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_talk_hist_pk', db_comment='알림톡이력 PK')
    CmAlarmNotiGroup = models.ForeignKey(CmAlarmNotiGroup, models.DO_NOTHING, db_column='alarm_noti_grp_pk', db_comment='알람알림그룹 PK')
    TalkContent = models.CharField(max_length=150, db_column='talk_content', db_comment='알림톡내용')
    TalkSndrNo = models.CharField(max_length=15, db_column='talk_sndr_no', db_comment='알림톡발신번호')
    TalkRcvrNo = models.CharField(max_length=15, db_column='talk_rcvr_no', db_comment='알림톡수신번호')
    TalkRcvrId = models.CharField(max_length=30, blank=True, null=True, db_column='talk_rcvr_id', db_comment='알림톡수신자 ID')
    ResultType = models.CharField(db_column='result_type', db_comment='결과유형')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    SendTs = models.DateTimeField(blank=True, null=True, db_column='send_ts', db_comment='발송일시')
    SendRmk = models.CharField(max_length=200, blank=True, null=True, db_column='send_rmk', db_comment='발송비고')
    ErrorCnt = models.SmallIntegerField(db_column='error_cnt', db_comment='에러건수')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_talk_hist'
        db_table_comment = '알림톡 이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnotiTalkTmpl(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_talk_tmpl_pk', db_comment='알림톡템플릿 PK')
    TmplName = models.CharField(max_length=50, db_column='tmpl_nm', db_comment='템플릿명')
    TmplContent = models.CharField(max_length=150, db_column='tmpl_content', db_comment='템플릿내용')
    TmplCode = models.CharField(max_length=20, db_column='tmpl_code', db_comment='템플릿코드')
    TmplType = models.CharField(db_column='tmpl_type', db_comment='템플릿유형')
    TmplStatus = models.CharField(db_column='tmpl_status', db_comment='템플릿상태')
    TmplRmk = models.CharField(max_length=200, blank=True, null=True, db_column='tmpl_rmk', db_comment='템플릿비고')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_talk_tmpl'
        db_table_comment = '알림톡 템플릿 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnotiTalkTmplVar(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_talk_tmpl_var_pk', db_comment='알림톡템플릿변수 PK')
    CmAnotiTalkTmpl = models.ForeignKey(CmAnotiTalkTmpl, models.DO_NOTHING, db_column='anoti_talk_tmpl_pk', db_comment='알림톡템플릿 PK')
    VarName = models.CharField(max_length=50, db_column='var_nm', db_comment='변수명')
    VarType = models.CharField(db_column='var_type', db_comment='변수유형')
    VarValue = models.CharField(max_length=100, blank=True, null=True, db_column='var_value', db_comment='변수값')
    VarRmk = models.CharField(max_length=200, blank=True, null=True, db_column='var_rmk', db_comment='변수비고')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_talk_tmpl_var'
        db_table_comment = '알림톡 템플릿 변수 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnotiTalkTmplVarVal(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_talk_tmpl_var_val_pk', db_comment='알림톡템플릿변수값 PK')
    CmAnotiTalkTmplVar = models.ForeignKey(CmAnotiTalkTmplVar, models.DO_NOTHING, db_column='anoti_talk_tmpl_var_pk', db_comment='알림톡템플릿변수 PK')
    VarVal = models.CharField(max_length=100, db_column='var_val', db_comment='변수값')
    VarValRmk = models.CharField(max_length=200, blank=True, null=True, db_column='var_val_rmk', db_comment='변수값비고')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_talk_tmpl_var_val'
        db_table_comment = '알림톡 템플릿 변수값 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAnotiTalkTmplVarValHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='anoti_talk_tmpl_var_val_hist_pk', db_comment='알림톡템플릿변수값이력 PK')
    CmAnotiTalkTmplVar = models.ForeignKey(CmAnotiTalkTmplVar, models.DO_NOTHING, db_column='anoti_talk_tmpl_var_pk', db_comment='알림톡템플릿변수 PK')
    VarVal = models.CharField(max_length=100, db_column='var_val', db_comment='변수값')
    VarValRmk = models.CharField(max_length=200, blank=True, null=True, db_column='var_val_rmk', db_comment='변수값비고')
    #SiteId = models.CharField(max_length=20, db_column='site_id', db_comment='사이트 ID')
    Factory_id = models.IntegerField(null=True, db_column='factory_pk',  db_comment="공장id")
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')

    class Meta:
        db_table = 'cm_anoti_talk_tmpl_var_val_hist'
        db_table_comment = '알림톡 템플릿 변수값 이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmArea(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='area_pk', db_comment='구역 PK')
    AreaCode = models.CharField(max_length=20, db_column='area_cd', db_comment='구역코드')
    AreaName = models.CharField(max_length=50, db_column='area_nm', db_comment='구역명')
    AreaType = models.CharField(max_length=20, db_column='area_type', db_comment='구역유형')
    AreaDesc = models.CharField(max_length=200, blank=True, null=True, db_column='area_desc', db_comment='구역설명')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_area'
        db_table_comment = '구역 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAreaEquip(models.Model):
    CmArea = models.ForeignKey(CmArea, models.DO_NOTHING, db_column='area_pk', db_comment='구역 PK')
    CmEquipment = models.ForeignKey('CmEquipment', models.DO_NOTHING, db_column='equip_pk', db_comment='설비 PK')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_area_equip'
        db_table_comment = '구역-설비 매핑 정보'
        unique_together = (('CmArea', 'CmEquipment'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAreaMtrl(models.Model):
    CmArea = models.ForeignKey(CmArea, models.DO_NOTHING, db_column='area_pk', db_comment='구역 PK')
    CmMaterial = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_area_mtrl'
        db_table_comment = '구역 자재 정보'
        unique_together = (('CmArea', 'CmMaterial'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmAreaUser(models.Model):
    CmArea = models.ForeignKey(CmArea, models.DO_NOTHING, db_column='area_pk', db_comment='구역 PK')
    UserPk = models.IntegerField(db_column='user_pk', db_comment='사용자 PK')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_area_user'
        db_table_comment = '구역 사용자 정보'
        unique_together = (('CmArea', 'UserPk'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmBomVer(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='bom_pk', db_comment='BOM PK')
    CmMaterial = models.ForeignKey('CmMaterial', models.DO_NOTHING, db_column='mtrl_pk', db_comment='자재 PK')
    BomVer = models.CharField(max_length=10, db_column='bom_ver', db_comment='BOM버전')
    BomDesc = models.CharField(max_length=200, blank=True, null=True, db_column='bom_desc', db_comment='BOM설명')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_bom_ver'
        db_table_comment = 'BOM 버전 정보'
        unique_together = (('CmMaterial', 'BomVer'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmCodeGroup(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='code_grp_pk', db_comment='코드그룹 PK')
    CodeGroupCode = models.CharField(max_length=20, unique=True, db_column='code_grp_cd', db_comment='코드그룹코드')
    CodeGrpName = models.CharField(max_length=50, db_column='code_grp_nm', db_comment='코드그룹명')
    CodeGrpDesc = models.CharField(max_length=200, blank=True, null=True, db_column='code_grp_desc', db_comment='코드그룹설명')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_code_grp'
        db_table_comment = '코드 그룹 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmCodeMst(models.Model):
    id = models.SmallAutoField(primary_key=True, db_column='code_pk', db_comment='코드 PK')
    CmCodeGroup = models.ForeignKey(CmCodeGroup, models.DO_NOTHING, db_column='code_grp_pk', db_comment='코드그룹 PK')
    CodeCode = models.CharField(max_length=20, db_column='code_cd', db_comment='코드')
    CodeName = models.CharField(max_length=50, db_column='code_nm', db_comment='코드명')
    CodeDesc = models.CharField(max_length=200, blank=True, null=True, db_column='code_desc', db_comment='코드설명')
    CodeSeq = models.SmallIntegerField(db_column='code_seq', db_comment='코드순서')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_code_mst'
        db_table_comment = '코드 마스터 정보'
        unique_together = (('CmCodeGroup', 'CodeCode'),)

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmCodeMstHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='code_hist_pk', db_comment='코드이력 PK')
    CmCodeMst = models.ForeignKey(CmCodeMst, models.DO_NOTHING, db_column='code_pk', db_comment='코드 PK')
    CmCodeGroup = models.ForeignKey(CmCodeGroup, models.DO_NOTHING, db_column='code_grp_pk', db_comment='코드그룹 PK')
    CodeCode = models.CharField(max_length=20, db_column='code_cd', db_comment='코드')
    CodeName = models.CharField(max_length=50, db_column='code_nm', db_comment='코드명')
    CodeDesc = models.CharField(max_length=200, blank=True, null=True, db_column='code_desc', db_comment='코드설명')
    CodeSeq = models.SmallIntegerField(db_column='code_seq', db_comment='코드순서')
    UseYn = models.CharField(db_column='use_yn', db_comment='사용여부')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_code_mst_hist'
        db_table_comment = '코드 마스터 이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
class CmCodeMstLangHist(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='code_lang_hist_pk', db_comment='코드언어이력 PK')
    CmCodeMst = models.ForeignKey(CmCodeMst, models.DO_NOTHING, db_column='code_pk', db_comment='코드 PK')
    LangCode = models.CharField(max_length=10, db_column='lang_cd', db_comment='언어코드')
    CodeName = models.CharField(max_length=50, db_column='code_nm', db_comment='코드명')
    CodeDesc = models.CharField(max_length=200, blank=True, null=True, db_column='code_desc', db_comment='코드설명')
    InsertTs = models.DateTimeField(auto_now_add=True, db_column='insert_ts', db_comment='등록일시')
    InserterId = models.CharField(max_length=20, db_column='inserter_id', db_comment='등록자 ID')
    InserterName = models.CharField(max_length=50, blank=True, null=True, db_column='inserter_nm', db_comment='등록자명')
    UpdateTs = models.DateTimeField(auto_now_add=True, null=True, db_column='update_ts', db_comment='수정일시')
    UpdaterId = models.CharField(max_length=20, blank=True, null=True, db_column='updater_id', db_comment='수정자 ID')
    UpdaterName = models.CharField(max_length=50, blank=True, null=True, db_column='updater_nm', db_comment='수정자명')

    class Meta:
        db_table = 'cm_code_mst_lang_hist'
        db_table_comment = '코드 언어 이력 정보'

    def set_audit(self, user):
        if self.InserterId is None:
            self.InserterId = user.id
            self.InserterName = user.username
        self.UpdaterId = user.id
        self.UpdaterName = user.username
        self.UpdateDt = DateUtil.get_current_datetime()
        return
 
