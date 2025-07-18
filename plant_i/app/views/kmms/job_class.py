from django.db import transaction
from django.db.backends.utils import logger
from domain.models.cmms import CmJobClass
from domain.services.common import CommonUtil
from domain.services.sql import DbUtil
from domain.services.kmms.pm_master import PMService
from domain.services.logging import LogWriter
from domain.services.date import DateUtil
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

def job_class(context):
    '''
    /api/kmms/job_class
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user

    pm_master_service = PMService()

    if action=='read': 
        items = pm_master_service.get_job_class_list()

    elif action=='save':
        # 데이터 저장 로직  
        job_class_pk = posparam.get('job_class_pk')
        jc = None

        try:
            if job_class_pk:        
                jc = CmJobClass.objects.filter(id=job_class_pk).first()
                if not jc:
                    return JsonResponse({
                        'result': False,
                        'message': f"PM with pk {id} does not exist."
                    })

            else:
                jc = CmJobClass()

                # 자동으로 코드 생성
                max_code = getMaxCode()  # ✅ self 제거하고 직접 호출
          
            
            # 데이터 저장
            jc.JobClassCode = max_code
            jc.JobClassName = posparam.get('occuName')     
            jc.WageCost = CommonUtil.try_int(posparam.get('maintenanceTime'))
            jc.UseYn = 'Y'
            jc.DelYn = 'N'
            jc.InsertTs = timezone.now()
            jc.InserterId = user.id
            jc.save()

            items = {'success': True, 'id': jc.job_class_pk}

        except Exception as ex:
            source = 'api/kmms/job_class, action:{}'.format(action)
            LogWriter.add_dblog('error', source, ex)
            raise ex

    return items
    
# ✅ self 없이 독립적으로 사용할 수 있도록 정적 메서드로 변경
@staticmethod
def getMaxCode():
    try:
        max_code = ""
        sql = """
            SELECT coalesce(MAX(job_class_cd), 'JC00') as max FROM cm_job_class
        """
        max_code = DbUtil.get_rows(sql)[0]['max']
        new_code = 'JC' + str(int(max_code[2:]) + 1).zfill(2)

        return new_code  # ✅ 'JC01' 그대로 반환
    except Exception as e:
        logger.error(f"Error in getMaxCode: {str(e)}")
        return '0'
    
