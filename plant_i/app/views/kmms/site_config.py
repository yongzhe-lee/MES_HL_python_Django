from django.db import transaction
from domain.models.cmms import CmSiteConfig, CmSites
from domain.services.common import CommonUtil
from domain.services.kmms.site_config import CmSiteConfigService
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.services.date import DateUtil

def site_config(context):
    '''
    /api/kmms/site_config
    '''
    items = []
    gparam = context.gparam;
    posparam = context.posparam
    action = gparam.get('action', 'read')
    request = context.request
    user = request.user

    site_config_Service = CmSiteConfigService()

    if action=='read':
        Site = gparam.get('Site', None)  
        if not Site:
            return {'success': False, 'message': 'Site ID가 제공되지 않았습니다.'}

        items = site_config_Service.read(Site)

    elif action=='updateProcOpts':
        try:
            site_id = posparam.get('Site')
            if not site_id:
                return {'success': False, 'message': 'Site ID가 제공되지 않았습니다.'}

            ProcOpts = posparam.get('ProcOpts')

            # update_or_create: site_id로 CmSiteConfig 객체를 찾아서 업데이트하거나, 없으면 새로 생성합니다.
            # 이를 통해 "matching query does not exist" 오류를 해결합니다.
            CmSiteConfig.objects.update_or_create(
                Site_id=site_id,
                defaults={
                    'ProcOpts': ProcOpts,
                }
            )

        except Exception as e:
            return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'}
        
        return {'success': True, 'message': '프로세스 정보가 저장되었습니다.'}

    elif action=='updateScheOpts':
        try:
            site_id = posparam.get('Site')
            if not site_id:
                return {'success': False, 'message': 'Site ID가 제공되지 않았습니다.'}

            ScheOpts = posparam.get('ScheOpts')

            # update_or_create: site_id로 CmSiteConfig 객체를 찾아서 업데이트하거나, 없으면 새로 생성합니다.
            # 이를 통해 "matching query does not exist" 오류를 해결합니다.
            CmSiteConfig.objects.update_or_create(
                Site_id=site_id,
                defaults={              
                    'ScheOpts': ScheOpts,
                }
            )

        except Exception as e:
            return {'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'}
        
        return {'success': True, 'message': '프로세스 정보가 저장되었습니다.'}

    return items