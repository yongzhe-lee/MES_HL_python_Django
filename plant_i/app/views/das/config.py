import os, json
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from domain.models.definition import DASConfig, DASServer, Equipment
from domain.services.system import SystemService

def config(context):
    '''
    /api/das/config?action=das_config&equ_id=1
    '''

    gparam = context.gparam
    action = gparam.get('action', 'read')
    user = context.request.user
    result = {'success' : True}

    dic_filepath = {}
    dic_filepath["1"] = "01_hpc1.load.json"
    dic_filepath["2"] = "02_hpc1.flash.json"
    dic_filepath["3"] = "03_hpc1.ict.json"
    dic_filepath["4"] = "04_hpc1.coatload.json"
    dic_filepath["5"] = "05_hpc1.pcbrev.json"
    dic_filepath["6"] = "06_hpc1.curing.json"
    dic_filepath["7"] = "07_hpc1.frobackload.json"
    dic_filepath["8"] = "08_hpc1.uh.load.json"
    dic_filepath["9"] = "09_hpc1.tim.json"
    dic_filepath["10"] = "10_hpc1.lh.load.json"
    dic_filepath["11"] = "11_hpc1.scrwt.json"
    dic_filepath["12"] = "12_hpc1.fclip.json"
    dic_filepath["13"] = "13_hpc1.eol.json"
    dic_filepath["15"] = "15_hpc1.pinchk.json"
    dic_filepath["16"] = "16_hpc1.brackassm.json"
    dic_filepath["17"] = "17_smt3.load.json"
    dic_filepath["18"] = "18_smt3.unload.json"

    try:
        if action == 'das_config':

            equ_id = gparam.get('equ_id')
            equipment = Equipment.objects.get(id=equ_id)
            curr_dir = os.getcwd()
            config_path = curr_dir + '/domain/_sql/das_config/'
            filepath = config_path + dic_filepath[equ_id]

            with open(filepath, 'r', encoding="utf8") as f:
                filedata = f.read()

            data = json.loads(filedata)
            dic_result = data["result"]
            items = dic_result['items']
            item = items[0]
            configuration = json.dumps(item, ensure_ascii=False)

            server_id = 1
            device_type = "melsec_tcp"
            if equipment.id>16:
                server_id =2
                device_type = "mewtocol_tcp"


            queryset = DASConfig.objects.filter(id = equ_id)
            if queryset.exists():
                queryset.update(Configuration = configuration)
            else:
                das_config = DASConfig()
                das_config.Name = equipment.Name +  '수집설정'
                das_config.Description= equipment.Name +  '수집설정'
                das_config.Configuration = configuration
                das_config.Server_id = server_id
                das_config.Equipment_id = equipment.id
                das_config.DeviceType = device_type
                das_config.is_active = 'Y'
                das_config.set_audit(user)
                das_config.save()


    except Exception as ex:
        result['success'] = False
        result["message"] = str(ex)

    return result