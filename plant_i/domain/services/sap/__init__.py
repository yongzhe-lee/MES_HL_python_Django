import requests, json
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

        body = json.dumps(data)
        print(body + "\r\n")

        response = requests.post(self.url, headers=self.headers, data=body, verify=False)

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


'''
print("----------------------------------------------------------------\r\n")
service = SapInterfaceService()
result = service.get_sap_material('20250101', '20250131', "N")
print(result)
#f = open("sap_mat.txt", 'w')
#f.write(result)
#f.close()



print("----------------------------------------------------------------\r\n")

result2 = service.get_sap_bom('20250312', ['D10.031-04'])
print(result2)

print("----------------------------------------------------------------\r\n")
result3 = service.get_sap_material_stock(['H00.002-76'])
print(result3)

print("----------------------------------------------------------------\r\n")
result4 = service.get_sap_input_number_by_random(['aDG24'])
print(result4)
'''
