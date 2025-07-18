import requests

class MESInterfaceService():

    host = "http://localhost:8080"  # 웹서버내 다른 포트로 연결됨
    def __def__(self):
        pass

    def convert_to_array(self, dic_res):
        items = []
        if dic_res["success"]:
            rows = dic_res['data']
            for r in rows:
                row = {}
                for c in r:
                    name = c.get("Name")
                    value = c.get("Value")
                    row[name] = value
                items.append(row)
        return items


    def get_production_plan_all(self, fromDate:str, toDate:str, line:str, product:str):
        #ProductPlanAll
        url = f"{self.host}/api/mes/ProductPlanAll"
        param = {
            "fromDate" : fromDate, 
            "toDate" : toDate,
            "line" : line,
            "product" : product
        }

        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        return response.json()
        
        
    
    def get_production_plan_excel(self, fromDate:str, toDate:str, line:str, product:str):
        #ProductPlanExcel
        url = f"{self.host}/api/mes/ProductPlanExcel"
        param = {
            "fromDate" : fromDate, 
            "toDate" : toDate,
            "line" : line,
            "product" : product
        }
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_workorder_list(self, line):
        #WorkOrderList
        url = f"{self.host}/api/mes/WorkOrderList?line={line}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_active_workorder(self, equipment :str):
        #ActiveWorkOrder
        url = f"{self.host}/api/mes/ActiveWorkOrder"
        param = {"equipment" : equipment}
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_lot_history(self, inputLotId):
        #LotHistory
        url = f"{self.host}/api/mes/LotHistory"
        param = {"inputLotId" : inputLotId}
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_fpy_date(self, fromDate, toDate, line, team):
        #FpyData        
        url = f"{self.host}/api/mes/FpyData"
        param = {"fromDate":fromDate, "toDate" : toDate, "line" : line, "team":team}
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_oee_plant(self, fromDate, toDate):
        #OeePlant
        url = f"{self.host}/api/mes/OeePlant"
        param = {"fromDate" : fromDate, "toDate" : toDate}
        response = requests.get(url, param)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_oee_line_group(self, fromDate, toDate, bizType):
        #OeeLineGroup
        url = f"{self.host}/api/mes/OeeLineGroup"
        param = {"fromDate" : fromDate, "toDate" : toDate,  "bizType":bizType}
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()

    def get_oee_line_team(self, fromDate, toDate, team):
        #OeeLineTeam
        url = f"{self.host}/api/mes/OeeLineTeam"
        param = {"fromDate" : fromDate, "toDate" : toDate,  "team":team}
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()
    
    def get_oee_line_analysis(self, fromDate, toDate, line):
        #OeeLineAnalysis
        url = f"{self.host}/api/mes/OeeLineAnalysis"
        param = {"fromDate" : fromDate, "toDate" : toDate,  "line":line}
        response = requests.get(url, param)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response.json()


