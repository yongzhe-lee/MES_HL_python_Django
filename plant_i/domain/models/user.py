from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.contrib.auth.models import User
from domain.services.date import DateUtil
from .system import Factory, Site


class Depart(models.Model):
    id = models.AutoField('부서번호', primary_key=True, db_comment="부서 고유 번호")
    Code = models.CharField('부서코드', max_length=50, blank=False, null=False, db_comment="부서를 식별하는 코드")
    Name = models.CharField('부서명', max_length=100, blank=False, null=False, db_comment="부서의 이름")
    UpDept_id = models.IntegerField('상위부서번호', blank=True, null=True, db_comment="상위 부서의 고유 번호")
    UpDeptCode = models.CharField('상위부서코드', max_length=50, blank=True, null=True, db_comment="상위 부서를 식별하는 코드")
    ReqDivCode = models.CharField('의뢰구분코드', max_length=20, blank=True, null=True, db_comment="의뢰 구분 코드")
    LabYN = models.CharField('실험실여부', max_length=1, default='N', blank=True, null=True, db_comment="실험실 여부 (Y/N)")
    MfgYN = models.CharField('제조부서여부', max_length=1, default='N', blank=True, null=True, db_comment="제조 부서 여부 (Y/N)")
    RoleNo = models.IntegerField('권한번호', blank=True, null=True, db_comment="권한 번호")
    UseYN = models.CharField('사용여부', max_length=1, default='Y', blank=False, null=False, db_comment="사용 여부 (Y/N)")
    DelYN = models.CharField('삭제여부', max_length=1, default='N', blank=False, null=False, db_comment="삭제 여부 (Y/N)")
    ApplyYN = models.CharField('적용여부', max_length=1, default='N', blank=True, null=True, db_comment="적용 여부 (Y/N)")
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True, db_comment="소속된 사이트 정보")
    Factory = models.ForeignKey(Factory, on_delete=models.DO_NOTHING, null=True, db_comment="소속된 공장")

    _status = models.CharField('_status', max_length=10, null=True, db_comment="상태 값")
    _created = models.DateTimeField('_created', auto_now_add=True, db_comment="데이터 생성 일시")
    _modified = models.DateTimeField('_modified', auto_now=True, null=True, db_comment="데이터 수정 일시")
    _creater_id = models.IntegerField('_creater_id', null=True, db_comment="데이터 생성자 ID")
    _modifier_id = models.IntegerField('_modifier_id', null=True, db_comment="데이터 수정자 ID")

    def set_audit(self, user):
        if self._creater_id is None:
            self._creater_id = user.id
        self._modifier_id = user.id
        self._modified = DateUtil.get_current_datetime()
        return

    class Meta:
        db_table = 'dept'
        verbose_name = '부서'
        db_table_comment = "부서 정보를 관리하는 테이블"
        unique_together = [
            ['Code'],
            ['Name'],
        ]

class UserGroup(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    Code = models.CharField('코드', max_length=50)
    Name = models.CharField('사용자그룹명', max_length=100, default='None')
    Disabled = models.BooleanField('사용안함', null=True, default=False)
    Description	= models.CharField('비고', max_length=500, null=True)
    ShiftYn	= models.CharField('교대조여부', max_length=1, null=True)
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True)
    Factory = models.ForeignKey(Factory, on_delete=models.DO_NOTHING, null=True, db_comment="소속된 공장")

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
        db_table = 'user_group'
        verbose_name = '사용자그룹'
        verbose_name_plural = 'User Groups'
        default_related_name = 'UserGroup'

        unique_together = [
            ['Code'],
        ]

class UserProfile(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    UserGroup = models.ForeignKey(UserGroup, on_delete=models.DO_NOTHING, null=True)
    password_changed = models.DateTimeField('패스워드변경일', null=True)
    lang_code =  models.CharField('사용언어코드', max_length=30, default='ko-KR')
    token = models.CharField(max_length=512, null=True)
    Name = models.CharField('사용자명', max_length=100, null=True)
    Depart = models.ForeignKey(Depart, on_delete=models.DO_NOTHING, null=True)
    job_class_pk = models.IntegerField('직무등급id', null=True) # CmJobClass

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
        db_table = 'user_profile'
        verbose_name = '사용자프로필'

        index_together = [
            ['UserGroup'],
        ]

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):

    if created:
        UserProfile.objects.create(User=instance)
    instance.userprofile.save()

    return

class UserGroupMenu(models.Model):
    id = models.AutoField(primary_key=True)
    UserGroup = models.ForeignKey(UserGroup, on_delete=models.DO_NOTHING, null=True)
    MenuCode = models.CharField('메뉴코드', max_length=50, null=False)
    AuthCode = models.CharField('권한코드', max_length=10, null=False)

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
        db_table = 'user_group_menu'
        verbose_name = '사용자그룹메뉴'

        unique_together = [
            ['MenuCode', 'UserGroup'],
        ]
        index_together = [
            ['UserGroup'],
        ]
        
class UserGroupUser(models.Model):
    id = models.AutoField(primary_key=True)
    UserGroup_id = models.IntegerField('사용자그룹id', blank=False, null=False)  # 외래 키 관계 설정 가능
    User_id = models.IntegerField('사용자id', blank=False, null=False)  # 외래 키 관계 설정 가능

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
        db_table = 'user_group_user'
        verbose_name = '사용자그룹별사용자'
        unique_together = (('UserGroup_id', 'User_id'),)  # 복합 기본 키 설정
