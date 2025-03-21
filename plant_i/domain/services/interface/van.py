import requests
from domain.models.interface import IFVanInterface, VanItemResult, VanReport
from domain.services.sql import DbUtil

class VanInterfaceService():

    token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJITCBLbGVtb3ZlIiwic3ViIjoiRUFJIiwiY2xpZW50SWQiOiIxNzQwMzg3MzEyMDAwMDEyNTA2IiwiY2xpZW50SVBzIjoiMTAuMjI2LjIzNi4zMjsgMTAuMjI2LjIzNi4zMDsgMTAuMjI2LjIzNi4zMSIsImlhdCI6MTc0MDYyMTA3Mn0.1oNwV640nxAwpWWglIWrpa9-LF2uNgXFpB6uOYKD7G0";
    main_host= "219.253.223.111"
    sub_host = "219.253.223.84"
    service_id = "van.development";
    command_id = "retrieveVanInspectReport";

    def __init__(self):
        pass

    def get_van_report_data(self, rnd_num, sap_input_number):

        result = {'success' : True}
        dic_param = {'sap_input_number' : sap_input_number, 'rnd_num': rnd_num}

        sql_report ='''
        select 
        id, report_number, inv_number, inv_seq, sap_gr_number, sap_gr_seq
        , mold, material_number, material_name, vendor_code, vendor_name, 
        material_revision, ecn_no, check_date, check_user_name
        , lot_no, lot_size, devision_no, fm_no, gr_date
        ,confirm_date, result_value, remark, aql_sample_count, defect_rate, passing_count, defect_count, sample_check_count
        , rnd_num
        , "_status", "_created", "_modified", "_creater_id", "_modifier_id"
        , to_char(_created, 'yyyy-mm-dd hh24:mi:ss') as created
        from van_report where 1=1
        '''
        if rnd_num: 
            sql_report+='''
            and rnd_num = %(rnd_num)s
            '''

        if sap_input_number:
            sql_report+='''
            and sap_gr_number = %(sap_input_number)s
            '''
        reports = DbUtil.get_rows(sql_report, dic_param)
        result['reports'] = reports


        sql_item= '''
        SELECT vir.id, vir.report_id
        , vir.seq, vir.spec_seq, vir.ins_text, vir.specification, vir.unit
        , vir.upper_limit, vir.lower_limit, vir.upper_limit_check, vir.lower_limit_check
        , vir.x1, vir.x10, vir.x2, vir.x3, vir.x4, vir.x5, vir.x6, vir.x7, vir.x8, vir.x9, vir.x_avg, vir.r_val, vir.pass_fail
        , vir.input_value, vir.input_value_text
        , vir."_status", vir."_created", vir."_modified", vir."_creater_id", vir."_modifier_id"
        , to_char(vir._created, 'yyyy-mm-dd hh24:mi:ss') as created
        from van_item_result vir
        inner join van_report vr on vr.id = vir.report_id
        where 1=1
        '''
        if rnd_num: 
            sql_item+='''
            and vr.rnd_num = %(rnd_num)s
            '''

        if sap_input_number:
            sql_item+='''
            vr.sap_gr_number = %(sap_input_number)s
            '''

        items = DbUtil.get_rows(sql_item, dic_param)
        result['items'] = items

        return result


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

    def save_if_van_data(rnd_num, items, user):

        dic_report = {}
        for item in items:
            van_report = None
            van_query = VanReport.objects.filter(report_number=item["REPORT_NUMBER"])
            count = van_query.count()

            if_van = IFVanInterface()
            if_van.rnd_num = rnd_num
            if_van.report_number = item["REPORT_NUMBER"]
            if_van.inv_number = item["INV_NUMBER"]
            if_van.inv_seq = item["INV_SEQ"]
            if_van.sap_gr_number = item["SAP_GR_NUMBER"]
            if_van.sap_gr_seq = item["SAP_GR_SEQ"]
            if_van.mold = item["MOLD"]
            if_van.material_number = item["MATERIAL_NUMBER"]
            if_van.material_name = item["MATERIAL_NAME"]
            if_van.vendor_code = item["VENDOR_CODE"]
            if_van.vendor_name = item["VENDOR_NAME"] 
            if_van.material_revision = item["MATERIAL_REVISION"]
            if_van.ecn_no = item["ECN_NO"]
            if_van.check_date = item["CHECK_DATE"]
            if_van.check_user_name = item["CHECK_USER_NAME"]
            if_van.lot_no = item["LOT_NO"]
            if_van.lot_size = item["LOT_SIZE"]
            if_van.devision_no = item["DEVISION_NO"]
            if_van.fm_no = item["FM_NO"]
            if_van.gr_date = item["GR_DATE"]
            if_van.confirm_date = item["CONFIRM_DATE"]
            if_van.result_value = item["RESULT_VALUE"]
            if_van.remark = item["REMARK"]
            if  item["AQL_SAMPLE_COUNT"]:
                if_van.aql_sample_count =  item["AQL_SAMPLE_COUNT"]
            if item["DEFECT_RATE"]:
                if_van.defect_rate = item["DEFECT_RATE"]
            if item["PASSING_COUNT"]:
                if_van.passing_count = item["PASSING_COUNT"]
            if item["DEFECT_COUNT"]:
                if_van.defect_count = item["DEFECT_COUNT"]
            if item["SAMPLE_CHECK_COUNT"]:
                if_van.sample_check_count = item["SAMPLE_CHECK_COUNT"]


            if if_van.report_number in dic_report:
                van_report = dic_report[if_van.report_number]
            else:
                van_query = VanReport.objects.filter(report_number=if_van.report_number)
                count = van_query.count()

                if count==0:
                    van_report = VanReport()
                    van_report.rnd_num = rnd_num
                    van_report.report_number = if_van.report_number
                    van_report.inv_number = if_van.inv_number
                    van_report.inv_seq = if_van.inv_seq
                    van_report.sap_gr_number = if_van.sap_gr_number
                    van_report.sap_gr_seq = if_van.sap_gr_seq
                    van_report.mold = if_van.mold
                    van_report.material_number = if_van.material_number
                    van_report.material_name = if_van.material_name
                    van_report.vendor_code = if_van.vendor_code
                    van_report.vendor_name = if_van.vendor_name
                    van_report.material_revision = if_van.material_revision
                    van_report.ecn_no = if_van.ecn_no
                    van_report.check_date = if_van.check_date
                    van_report.check_user_name = if_van.check_user_name
                    van_report.lot_no = if_van.lot_no
                    van_report.lot_size = if_van.lot_size
                    van_report.devision_no = if_van.devision_no
                    van_report.fm_no = if_van.fm_no
                    van_report.gr_date = if_van.gr_date
                    van_report.confirm_date = if_van.confirm_date
                    van_report.result_value = if_van.result_value
                    van_report.remark = if_van.remark
                    van_report.aql_sample_count = if_van.aql_sample_count
                    van_report.defect_rate = if_van.defect_rate
                    van_report.passing_count = if_van.passing_count
                    van_report.defect_count = if_van.defect_count
                    van_report.sample_check_count = if_van.sample_check_count
                    van_report.set_audit(user)
                    van_report.save()

                else:
                    van_report = van_query.first()


                dic_report[if_van.report_number] = van_report
            #########################################################
            if_van.seq = item["SEQ"]
            if_van.ins_text = item["INS_TEXT"]
            if_van.spec_seq = item["SPEC_SEQ"]
            if_van.specification = item["SPECIFICATION"]

            if item["UPPER_LIMIT"]:
                if_van.upper_limit = item["UPPER_LIMIT"]
            if item["LOWER_LIMIT"]:
                if_van.lower_limit = item["LOWER_LIMIT"]

            if_van.unit = item["UNIT"]
            if_van.machine_type = item["MACHINE_TYPE"]
            if_van.machine_type_text = item["MACHINE_TYPE_TEXT"]
            if_van.x1 = item["X1"]
            if_van.x2 = item["X2"]
            if_van.x3 = item["X3"]
            if_van.x4 = item["X4"]
            if_van.x5 = item["X5"]
            if_van.x6 = item["X6"]
            if_van.x7 = item["X7"]
            if_van.x8 = item["X8"]
            if_van.x9 = item["X9"]
            if_van.x10 = item["X10"]
            if_van.x_avg = item["X_AVG"]
            if_van.r_val = item["R_VAL"]
            if_van.pass_fail = item["PASS_FAIL"]
            if_van.input_value = item["INPUT_VALUE"]
            if_van.input_value_text = item["INPUT_VALUE_TEXT"]
            if_van.upper_limit_check = item["UPPER_LIMIT_CHECK"]
            if_van.lower_limit_check = item["LOWER_LIMIT_CHECK"]            
            if_van.set_audit(user)
            if_van.save()


            # 아이템시작
            van_item_result = None
            item_query = VanItemResult.objects.filter(VanReport=van_report, seq=item["SEQ"],  spec_seq=item["SPEC_SEQ"])
            item_count = item_query.count()
            if item_count>0:
                van_item_result = item_query.first()
            else:
                van_item_result = VanItemResult(VanReport = van_report)
                van_item_result.seq = item["SEQ"]
                van_item_result.ins_text = item["INS_TEXT"]
                van_item_result.spec_seq = item["SPEC_SEQ"]
                van_item_result.specification = item["SPECIFICATION"]
                van_item_result.upper_limit =if_van.upper_limit
                van_item_result.lower_limit = if_van.lower_limit
                van_item_result.unit = item["UNIT"]
                van_item_result.machine_type = item["MACHINE_TYPE"]
                van_item_result.machine_type_text = item["MACHINE_TYPE_TEXT"]
                van_item_result.x1 = item["X1"]
                van_item_result.x2 = item["X2"]
                van_item_result.x3 = item["X3"]
                van_item_result.x4 = item["X4"]
                van_item_result.x5 = item["X5"]
                van_item_result.x6 = item["X6"]
                van_item_result.x7 = item["X7"]
                van_item_result.x8 = item["X8"]
                van_item_result.x9 = item["X9"]
                van_item_result.x10 = item["X10"]
                van_item_result.x_avg = item["X_AVG"]
                van_item_result.r_val = item["R_VAL"]
                van_item_result.pass_fail = item["PASS_FAIL"]
                van_item_result.input_value = item["INPUT_VALUE"]
                van_item_result.input_value_text = item["INPUT_VALUE_TEXT"]
                van_item_result.upper_limit_check = item["UPPER_LIMIT_CHECK"]
                van_item_result.lower_limit_check = item["LOWER_LIMIT_CHECK"]
                van_item_result.set_audit(user)

                van_item_result.save()

'''
service = VanInterfaceService()
result = service.get_van_test_result('5000822215', '0001')
#5000822215 / 0001  내자
#5000822217 / 0001  외자
print(result)
'''


