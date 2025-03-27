
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
            dic_result = sap_service.get_sap_input_number_by_random([rnd_num])
            items = dic_result['rs']["tables"]["STAB"]
            result["data"] = items

        elif action =="sap_van_report_by_pcb_rnd_num":
             rnd_num = gparam.get('rnd_num')

             sap_req_result = sap_service.get_sap_input_number_by_random([rnd_num])

             if not sap_req_result['rs'] :
                 result['success'] = False
                 result["message"] = 'PCB난수번호 SAP조회결과 없음'
                 return result

             sap_items = sap_req_result['rs']["tables"]["STAB"]

             reports = []
             items = []
             for item in sap_items:
                 sap_input_number = item["MBLNR"]
                 seq_no = item["ZEILE"]

                 print(f'sap_input_number:{sap_input_number}, seq_no : {seq_no}')
                 dic_result = van_service.get_van_test_result(sap_input_number, seq_no)
                 van_items = dic_result['rs']
                 print("van van_items" , van_items)

                 van_service.save_if_van_data(rnd_num, van_items, user)
                 report_data = van_service.get_van_report_data(rnd_num, sap_input_number)

                 for r in report_data['reports']:
                     reports.append(r)
                 for t in report_data['items']:
                     items.append(t)
                  
             result['success'] = True
             result['reports'] = reports
             result['items'] = items

             
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