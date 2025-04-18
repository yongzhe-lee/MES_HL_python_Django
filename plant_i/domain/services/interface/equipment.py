import json
import dateutil
from domain.models.interface import IFEquipmentResult, IFEquipmentResultItem
from domain.services.logging import LogWriter
from domain.models.definition import EquipAlarmHistory

class IFEquipmentResultService():
    def __init__(self):
        pass

    def rst_equipment_topic_handler(self, topic, payload):
        """
        MQTT에서 수신한 payload를 처리하는 핸들러
        :param payload: MQTT에서 수신한 payload
        :return: None
        """
        print(topic, payload)
        dic_payload = json.loads(payload)
        state = dic_payload.get('state', None)
        sn = dic_payload.get('sn', None)
        equ_cd = dic_payload.get('stationID', None)
        mat_cd = dic_payload.get('PartNr', None)
        bom_ver = dic_payload.get('bom_ver', None)
        m_status = dic_payload.get('M_status', None)
        str_data_date = dic_payload.get('data_date', None)
        data_date = dateutil.parser.parse(str_data_date)

        is_mounter = False
        module_no = ""
        # mounter case 반영필요
        if equ_cd =='smt4.mnt':
            is_mounter = True


        equ_result = IFEquipmentResult()
        equ_result.sn = sn
        equ_result.sn_items = dic_payload.get('sn_items', [])        

        equ_result.state = state
        equ_result.equ_cd = equ_cd
        equ_result.mat_cd = mat_cd  
        equ_result.bom_ver = bom_ver
        equ_result.data_date = data_date


        try:

            is_alarm = dic_payload.get('alarm', False)
            if is_alarm=="1" or is_alarm=="Y":
                is_alarm = True

            alarm_items = dic_payload.get("alarm_items", [])
            equ_result.alarm_items = alarm_items
            equ_result.is_alarm = is_alarm
            equ_result.save()



            arr_cd = dic_payload.get('test_item_cd', [])
            arr_val = dic_payload.get('test_item_val', [])
            arr_min = dic_payload.get('test_item_min', [])
            arr_max = dic_payload.get('test_item_max', [])
            arr_unit = dic_payload.get('test_item_unit', [])
            arr_failcode = dic_payload.get('failcode', [])

            idx=0
            for item_cd in arr_cd:
                result_item = IFEquipmentResultItem()
                result_item.equ_result = equ_result
                result_item.test_item_cd = item_cd
                result_item.test_item_val = arr_val[idx]
                result_item.test_item_min = arr_min[idx]
                result_item.test_item_max = arr_max[idx]
                result_item.test_item_unit = arr_unit[idx]
                result_item.test_item_failcode = arr_failcode[idx]
                result_item.save()

                idx = idx+1


            if is_alarm:
                for alarm_item in alarm_items:
                    equip_alarm_history = EquipAlarmHistory()
                    equip_alarm_history.alarm_code = alarm_item.get("alarm_code", "")
                    equip_alarm_history.alarm_desc = alarm_item.get("alarm_desc", "")
                    equip_alarm_history.alarm_time = data_date
                    equip_alarm_history.save()

        except Exception as ex:
            source  = f"IFEquipmentResultService.rst_equipment_topic_handler - topic :{topic}"
            LogWriter.add_dblog("error", source, ex)
        return
