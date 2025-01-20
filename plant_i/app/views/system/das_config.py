
from domain.models.definition import DASServer, DASConfig
from domain.services.das.config import DASConfigService
from domain.services.logging import LogWriter

def das_config(context):
    '/api/das/config'

    items = []
    gparam = context.gparam
    posparam = context.posparam
    action = gparam.get('action')
    dasconfig_service = DASConfigService()

    try:

        if action=='read':
            server = gparam.get('server')
            equipment = gparam.get('equipment')
            items = dasconfig_service.get_das_config_list(server, equipment)
        elif action=='detail':
            id= gparam.get('id')
            items = dasconfig_service.get_das_config_detail(id)

        elif action=='save':
            print(posparam)
            id = posparam.get('id')
        
            dasconfig =  None
            if id:
                dasconfig = DASConfig.objects.get(id=id)
            else:
                dasconfig =  DASConfig()

            is_active = posparam.get('is_active', 'N')

            dasconfig.Server_id =  posparam.get('Server_id')
            dasconfig.Equipment_id =  posparam.get('Equipment_id')
            dasconfig.Name =  posparam.get('Name')
            dasconfig.Description =  posparam.get('Description')
            dasconfig.Configuration =  posparam.get('Configuration')
            dasconfig.ConfigFileName =  posparam.get('ConfigFileName')
            dasconfig.Handler =  posparam.get('Handler')
            dasconfig.DeviceType =  posparam.get('DeviceType')
            dasconfig.Topic =  posparam.get('Topic')
            dasconfig.is_active = is_active

            dasconfig.save()
            items = {'id': id}

        elif action == 'delete':
            id = posparam.get('id')
            if id:
                DASConfig.objects.filter(id = id).first().delete()
                items = {'success' : True}

    except Exception as ex:
        source = '/api/das/config, action:{} '.format(action)
        LogWriter.add_dblog('error',source, ex)
        if action == 'delete':
            err_msg = LogWriter.delete_err_message(ex)
            items = {'success':False, 'message': err_msg}
            return items
        else:
            items = {}
            items['success'] = False
            if not items.get('message'):
                items['message'] = str(ex)
            return items
        #raise ex


    return items
