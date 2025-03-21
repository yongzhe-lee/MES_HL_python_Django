
import os, json

from domain.services.sql import DbUtil
from domain.services.interface.van import VanInterfaceService
from domain.services.interface.sap import SapInterfaceService
#from domain.models.interface import IFVanInterface, VanItemResult, VanReport

def van(context):
    '''
    /api/interface/van?action=local_migration
    '''
    gparam = context.gparam
    posparam = context.posparam
    request = context.request
    user = request.user
    action = gparam.get('action')
    result = {'success' : True, 'message' : ''}

    sap_service = SapInterfaceService()
    van_service = VanInterfaceService()

    try:

        if action=="read":

            rnd_num = gparam.get('rnd_num')
            sap_input_number = gparam.get('sap_input_number')

            result = van_service.get_van_report_data(rnd_num, sap_input_number)

        elif action=="request_sap_input_number":
            
            rnd_num = gparam.get('rnd_num')

            dic_result = sap_service.get_sap_input_number([rnd_num])
            data = dic_result['rs']["tables"]["STAB"]
            result["data"] = data

        elif action =="sap_van_report_by_pcb_rnd_num":
             rnd_num = gparam.get('rnd_num')
             dic_result = sap_service.get_sap_input_number([rnd_num])
             data = dic_result['rs']["tables"]["STAB"]

             if len(data)==0:
                 result['success'] = False
                 result["message"] = 'PCB난수번호 SAP조회결과 없음'
                 return result

             sap_input_number = data["MBLNR"]
             seq_no = data["ZEILE"]


             dic_result = van_service.get_van_test_result(sap_input_number, seq_no)
             items = dic_result['rs']
             count = van_service.save_if_van_data(rnd_num, items, user)

             result = van_service.get_van_report_data(rnd_num, sap_input_number)

        elif action=="local_migration":
            curr_dir = os.getcwd()
            filepath = curr_dir + '/domain/_sql/if/van.json'

            with open(filepath, 'r', encoding="utf8") as f:
                filedata = f.read()

            dic_result = json.loads(filedata)
            items = dic_result['rs']
            van_service.save_if_van_data(items, user)


    except Exception as ex:
        result["success"] = False
        result["message"] = str(ex)

    return result