from django.db import models
from domain.services.date import DateUtil

class ExtraSourceCode(models.Model):
    id = models.AutoField(primary_key=True)
    TaskName = models.CharField('업무명', max_length=50)
    AccessKey = models.CharField('키', max_length=50)
    Source = models.CharField('소스', max_length=2000, null=True)
    UseYN = models.CharField('사용유무', max_length=1, default='Y')
    Description	= models.CharField('설명', max_length=200, null=True)

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
        db_table = 'ext_src'
        verbose_name = '사용자정의소스코드'
        unique_together = [
            ['TaskName', 'AccessKey'],
        ]