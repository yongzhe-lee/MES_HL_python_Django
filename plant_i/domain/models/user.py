from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.contrib.auth.models import User
from domain.services.date import DateUtil
from .system import Site


class Depart(models.Model):
    id = models.AutoField('부서번호', primary_key=True)
    Code = models.CharField('부서코드', max_length=50, blank=False, null=False)
    Name = models.CharField('부서명', max_length=100, blank=False, null=False)
    UpDept_id = models.IntegerField('상위부서번호', blank=True, null=True)  # 외래 키 관계 설정 가능
    UpDeptCode = models.CharField('상위부서코드', max_length=50, blank=True, null=True)
    ReqDivCode = models.CharField('의뢰구분코드', max_length=20, blank=True, null=True)
    LabYN = models.CharField('실험실여부', max_length=1, default='N', blank=True, null=True)
    MfgYN = models.CharField('제조부서여부', max_length=1, default='N', blank=True, null=True)
    RoleNo = models.IntegerField('권한번호', blank=True, null=True)
    UseYN = models.CharField('사용여부', max_length=1, default='Y', blank=False, null=False)
    DelYN = models.CharField('삭제여부', max_length=1, default='N', blank=False, null=False)
    ApplyYN = models.CharField('적용여부', max_length=1, default='N', blank=True, null=True)
    Site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, null=True)
    
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
        db_table = 'dept'
        verbose_name = '부서'
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
