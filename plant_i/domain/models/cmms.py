from tarfile import NUL
from django.db import models
from domain.models.definition import Equipment, Material, Site, Unit
from domain.models.user import Depart
from django.contrib.auth.models import User
from domain.services.date import DateUtil
from datetime import datetime

class CmJobClass(models.Model):
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
        


