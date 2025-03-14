import requests

class VanInterfaceService():

    token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJITCBLbGVtb3ZlIiwic3ViIjoiRUFJIiwiY2xpZW50SWQiOiIxNzQwMzg3MzEyMDAwMDEyNTA2IiwiY2xpZW50SVBzIjoiMTAuMjI2LjIzNi4zMjsgMTAuMjI2LjIzNi4zMDsgMTAuMjI2LjIzNi4zMSIsImlhdCI6MTc0MDYyMTA3Mn0.1oNwV640nxAwpWWglIWrpa9-LF2uNgXFpB6uOYKD7G0";
    main_host= "219.253.223.111"
    sub_host = "219.253.223.84"
    service_id = "van.development";
    command_id = "retrieveVanInspectReport";

    def __init__(self):
        pass


    def get_van_test_result(self, input_num, seq_no ):

        url = f"https://{self.main_host}/api/1.0/service/channel";
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        data = {
            "serviceId": self.service_id,
            "commandId": self.command_id,
            "sapGrNumber": input_num,
            "sapGrSeq": seq_no
        }
        
        query_string  = "&".join([f"{key}={value}" for key, value in data.items()])
        url = url + "?" + query_string

        response = requests.post(url, headers=headers, params=data, verify=False)
        return response.json()


'''
service = VanInterfaceService()
result = service.get_van_test_result('5000822215', '0001')
#5000822215 / 0001  내자
#5000822217 / 0001  외자
print(result)
'''


