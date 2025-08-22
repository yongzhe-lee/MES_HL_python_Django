import requests, json

from domain.services.date import DateUtil
from domain.services.sql import DbUtil
from domain.services.logging import LogWriter
from configurations import settings

class SapInterfaceService():

    token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJITCBLbGVtb3ZlIiwic3ViIjoiRUFJIiwiY2xpZW50SWQiOiIxNzQwMzg3MzEyMDAwMDEyNTA2IiwiY2xpZW50SVBzIjoiMTAuMjI2LjIzNi4zMjsgMTAuMjI2LjIzNi4zMDsgMTAuMjI2LjIzNi4zMSIsImlhdCI6MTc0MDYyMTA3Mn0.1oNwV640nxAwpWWglIWrpa9-LF2uNgXFpB6uOYKD7G0";

    url = ""

    # main : 219.253.223.111 sub : 219.253.223.84
    main_host= "219.253.223.111"
    headers = {}
    
    service_id = "rfc.production.mhe.korea"
    #service_id = "rfc.development.mhe.korea"

    resource = '/api/1.0/service/channel/jco'

    def __init__(self):
        self.token = settings.IF_EAI_TOKEN
        self.headers = {
            "Content-Type":"application/json",
            "Authorization": f"Bearer {self.token}"
        }

        self.url = f"https://{self.main_host}{self.resource}"

        return

    def get_sap_material(self, dt_start, dt_end, mig_flag='N', user=None):

        rfc_fuction ='ZPP_SMF_INTERFACE_001'

        data = {
            "jcoImportParameter" :{
                "function" : rfc_fuction,
                "headerParameters" : {
                    "I_SDATE": dt_start,
                    "I_EDATE": dt_end,
                    "I_MIG" : mig_flag
                },
            },
            "serviceId": self.service_id,
            "commandId": "retrieveTable"
        }

        param_data = json.dumps(data)

        contents=None
        log_start = DateUtil.get_current_datetime()
        success_yn = 'Y'

        try:
            
            response = requests.post(self.url, headers=self.headers, data=param_data, verify=False)
            
            if response.status_code != 200:
                success_yn = 'N'
                contents = response.text
                raise Exception(f"Error: {response.status_code} - {response.text}")

            return response.json()
        except Exception as ex:
            success_yn = 'N'
            raise ex
        finally:
            log_end = DateUtil.get_current_datetime()
            LogWriter.add_interface_log("sap_material", "service EAI", param_data, success_yn, log_start, log_end, contents=contents, user=user)


    def get_sap_bom_db_list():
        sql= '''
        select 
        id, stab_werks, stab_matnr, stab_revlv, stab_bmeng, stab_idnrk, stab_mnglg, stab_meins, stab_stufe, stab_datuv, stab_datab, stab_aennr, stab_bklas, stab_bkbez
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
        from if_sap_bom
        '''
        items = DbUtil.get_rows(sql)
        return items


    def get_sap_bom(self, base_date, materials=[], user=None):

        rfc_fuction ='ZPP_SMF_INTERFACE_002'

        mtab = []
        for m in materials:
            mtab.append({"MATNR": m})

        data = {
            "jcoImportParameter" :{
                "function" : rfc_fuction,
                "headerParameters" : {
                    "I_DATUV": base_date,
                },
                "tableParameters": {
                    "MTAB" : mtab
                }
            },
            "serviceId": self.service_id,
            "commandId": "retrieveTable"
        }
        
        param = json.dumps(data)

        contents = None
        success_yn = 'Y'
        log_start = DateUtil.get_current_datetime()

        try:
            response = requests.post(self.url, headers=self.headers, data=param, verify=False)
            if response.status_code != 200:
                success_yn = 'N'
                contents = response.text
                raise Exception(f"Error: {response.status_code} - {response.text}")

            return response.json()

        except Exception as ex:
            success_yn = 'N'
            raise ex
        finally:
            log_end = DateUtil.get_current_datetime()
            LogWriter.add_interface_log("sap_bom", "service EAI", param, success_yn, log_start, log_end, contents=contents, user=user)


    def get_sap_material_stock(self, materials=[], user=None):

        rfc_fuction ='ZPP_SMF_INTERFACE_003'

        mtab = []
        for m in materials:
            mtab.append({"MATNR": m})

        data = {
            "jcoImportParameter" :{
                "function" : rfc_fuction,
                "tableParameters": {
                    "MTAB" : mtab
                }
            },
            "serviceId": self.service_id,
            "commandId": "retrieveTable"
        }

        param = json.dumps(data)

        contents = None
        log_start = DateUtil.get_current_datetime()
        success_yn = 'Y'

        try:
            response = requests.post(self.url, headers=self.headers, data=param, verify=False)
            if response.status_code != 200:
                contents = response.text
                raise Exception(f"Error: {response.status_code} - {response.text}")

            return response.json()

        except Exception as ex:
            success_yn = 'N'
            raise ex
        finally:
            log_end = DateUtil.get_current_datetime()
            LogWriter.add_interface_log("sap_stock", "service EAI", param, success_yn, log_start, log_end, contents, user)



    def get_sap_input_number_list(self, rnd_num):

        sql = '''
        select 
        id, stab_mblnr, stab_zeile, stab_matnr, stab_maktx, stab_menge, stab_abqty, stab_meins, rnd_num
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        from if_sap_pcb_ran
        where rnd_num = %(rnd_num)s
        order by stab_mblnr
        '''

        items = DbUtil.get_rows(sql, {"rnd_num" : rnd_num})

        return items



    def get_sap_input_number_by_random(self, random_numbers=[], user=None):

        rfc_fuction ='ZPP_SMF_INTERFACE_004'

        mtab = []
        for rm in random_numbers:
            mtab.append({"ABKNR": rm})

        data = {
            "jcoImportParameter" :{
                "function" : rfc_fuction,
                "tableParameters" : {
                    "MTAB": mtab,
                },
            },
            "serviceId": self.service_id,
            "commandId": "retrieveTable"
        }
        
        param = json.dumps(data)

        contents = None
        log_start = DateUtil.get_current_datetime()
        success_yn = 'Y'
        try:
            response = requests.post(self.url, headers=self.headers, data=param, verify=False)
            if response.status_code != 200:
                contents = response.text
                raise Exception(f"Error: {response.status_code} - {response.text}")

            return response.json()
        except Exception as ex:
            success_yn = 'N'
            raise ex;
        finally:
            log_end = DateUtil.get_current_datetime()
            LogWriter.add_interface_log("sap_rand", "service EAI", param, success_yn, log_start, log_end, contents, user)


#print("----------------------------------------------------------------\r\n")
#service = SapInterfaceService()
#result = service.get_sap_material('20250101', '20250131', "N")
#print(result)

#print("----------------------------------------------------------------\r\n")

# D10.003-007
#result2 = service.get_sap_bom('20250314', ['D10.003-007'])
#print(result2)

#print("----------------------------------------------------------------\r\n")
# D10.003-007
#result3 = service.get_sap_material_stock(['D10.031-04'])
#print(result3)

#print("----------------------------------------------------------------\r\n")
# aDG24
#result4 = service.get_sap_input_number_by_random(['aBPYK'])
#print(result4)
