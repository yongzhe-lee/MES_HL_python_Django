import requests, json

from domain.services.sql import DbUtil

#from domain.services.logging import LogWriter
#from configurations import settings

class SapInterfaceService():

    token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJITCBLbGVtb3ZlIiwic3ViIjoiRUFJIiwiY2xpZW50SWQiOiIxNzQwMzg3MzEyMDAwMDEyNTA2IiwiY2xpZW50SVBzIjoiMTAuMjI2LjIzNi4zMjsgMTAuMjI2LjIzNi4zMDsgMTAuMjI2LjIzNi4zMSIsImlhdCI6MTc0MDYyMTA3Mn0.1oNwV640nxAwpWWglIWrpa9-LF2uNgXFpB6uOYKD7G0";

    url = ""
    main_host= "219.253.223.111"
    sub_host = "219.253.223.84"
    headers = {}
    
    #service_id = "rfc.production.mhe.korea"
    service_id = "rfc.development.mhe.korea"
    resource = '/api/1.0/service/channel/jco'

    def __init__(self):
        #self.token = settings.IF_EAI_TOKEN
        self.headers = {
            "Content-Type":"application/json",
            "Authorization": f"Bearer {self.token}"
        }

        self.url = f"https://{self.main_host}{self.resource}"

        return

    def get_sap_material(self, dt_start, dt_end, mig_flag='N'):

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
        print(param_data + "\r\n")

        #LogWriter.add_interface_log("sap_material", "EAI", contents=param_data)
        response = requests.post(self.url, headers=self.headers, data=param_data, verify=False)
        return response.json()


    def get_sap_bom(self, base_date, materials=[]):

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

        body = json.dumps(data)
        print(body + "\r\n")
        response = requests.post(self.url, headers=self.headers, data=body, verify=False)
        return response.json()

    def get_sap_material_stock(self, materials=[]):

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

        body = json.dumps(data)
        print(body + "\r\n")
        response = requests.post(self.url, headers=self.headers, data=body, verify=False)
        return response.json()


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



    def get_sap_input_number_by_random(self, random_numbers=[]):

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

        body = json.dumps(data)
        print(body + "\r\n")
        response = requests.post(self.url, headers=self.headers, data=body, verify=False)
        return response.json()


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
