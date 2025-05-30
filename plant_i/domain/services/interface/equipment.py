
import json
from datetime import datetime

from domain.models.interface import IFEquipmentResult, IFEquipmentResultItem, IFEquipmentRecipe, IFEquipemntDefectItems
from domain.services.logging import LogWriter
from domain.models.definition import EquipAlarmHistory
from domain.services.date import DateUtil
class IFEquipmentResultService():
    def __init__(self):
        pass

    def rst_equipment_topic_handler(self, topic, payload):
        """
        MQTT에서 수신한 payload를 처리하는 핸들러
        :param payload: MQTT에서 수신한 payload
        :return: None
        """
        source  = f"IFEquipmentResultService.rst_equipment_topic_handler - topic :{topic}"

        now = DateUtil.get_current_datetime()

        print(topic, payload)
        dic_payload = None
        try:

            dic_payload = json.loads(payload)
        except Exception as ppex:
            LogWriter.add_dblog("error", source, ppex)

        state = dic_payload.get('state', None)
        sn = dic_payload.get('sn', None)
        sn_new = dic_payload.get('sn_new', None)
        sn_items = dic_payload.get('sn_items', [])
        equ_cd = dic_payload.get('stationID', None)
        if equ_cd is None:
            equ_cd = dic_payload.get('StationID', None)

        mat_cd = dic_payload.get('PartNr', None)
        mat_desc = dic_payload.get('PartDesc', None)
        bom_ver = dic_payload.get('bom_ver', None)
        m_status = dic_payload.get('M_status', None)
        str_data_date = dic_payload.get('data_date', None)
        data_date = None
        pcb_cn=dic_payload.get('pcb_cn', None)
        pcb_input = dic_payload.get('pcb_input', None)
        pcb_size=dic_payload.get('pcb_size', None)
        pcb_array=dic_payload.get('pcb_array', None)
        pcb_ww = dic_payload.get('pcb_ww', None)

        is_mounter = False
        module_no = ""
        # mounter case 반영필요
        if equ_cd =='smt4.mnt':
            is_mounter = True


        equ_result = IFEquipmentResult()
        equ_result.sn = sn
        equ_result.sn_new = sn_new
        equ_result.sn_items = sn_items
        equ_result.state = state
        equ_result.equ_cd = equ_cd
        equ_result.mat_cd = mat_cd  
        equ_result.mat_desc = mat_desc
        equ_result.bom_ver = bom_ver

        try:
            data_date = datetime.strptime(str_data_date,'%Y-%m-%dT%H:%M:%S%z')
            #data_date = dateutil.parser.parse(str_data_date)
        except Exception as ddex:
            LogWriter.add_dblog("error", source, ddex)

        equ_result.data_date = data_date
        equ_result.pcb_cn = pcb_cn
        equ_result.pcb_size = pcb_size
        equ_result.pcb_array = pcb_array
        equ_result.pcb_ww = pcb_ww

        if pcb_input:
            try:
                pcb_input = datetime.strptime(pcb_input,'%Y-%m-%dT%H:%M:%S%z')
                equ_result.pcb_input = pcb_input
            except Exception as eex:
                source = source + "- pcb_input format error : " + pcb_input
                LogWriter.add_dblog("error", source, eex)

        try:

            defect_items = dic_payload.get('defect_items', None)

            is_alarm = dic_payload.get('is_alarm', None)
            if is_alarm=="1" or is_alarm=="Y" or is_alarm=="true" or is_alarm==1 or is_alarm==True:
                is_alarm = True
            else:
                is_alarm = False


            alarm_items = dic_payload.get("alarm_items", [])
            equ_result.alarm_items = alarm_items
            equ_result.defect_items = defect_items
            equ_result.is_alarm = is_alarm
            equ_result.save()

            if defect_items:
                for dt in defect_items:
                    sn = dt.get('sn', None)
                    if_defect_item = IFEquipemntDefectItems()
                    if_defect_item.sn = sn
                    if_defect_item.EquipmentResult = equ_result
                    if_defect_item.defect_cd = dt.get('failure_type', None)
                    if_defect_item.defect_nm = dt.get('failure_cause', None)
                    if_defect_item.ComponentName = dt.get('comp_name', None)
                    if_defect_item.PartNumber = dt.get('comp_part_nr', None)
                    if_defect_item._created = now
                    if_defect_item.save()


            arr_cd = dic_payload.get('test_item_cd', [])
            arr_val = dic_payload.get('test_item_val', [])
            arr_min = dic_payload.get('min_val', [])
            arr_max = dic_payload.get('max_val', [])
            arr_unit = dic_payload.get('unit', [])
            arr_failcode = dic_payload.get('failcode', [])

            idx=0
            for item_cd in arr_cd:
                result_item = IFEquipmentResultItem()
                result_item.EquipmentResult = equ_result
                result_item.test_item_cd = item_cd
                result_item.test_item_val = arr_val[idx]
                result_item.min_val = arr_min[idx]
                result_item.max_val = arr_max[idx]
                result_item.unit = arr_unit[idx]
                result_item.failcode = arr_failcode[idx]
                result_item.save()

                idx = idx+1
            try:
                recipe_items = dic_payload.get("recipe_items", None)
                if recipe_items:
                    dic_flow_meter = recipe_items.get("flow_meter", None)
                    if dic_flow_meter:
                        if_recipe1 = IFEquipmentRecipe()
                        if_recipe1.EquipmentResult = equ_result
                        if_recipe1.GroupName="flow_meter"
                        if_recipe1.item_cd = "flow_meter1"
                        if_recipe1.item_val = dic_flow_meter.get("flow_meter1", None)
                        if_recipe1._created = now
                        if_recipe1.save()

                        if_recipe2 = IFEquipmentRecipe()
                        if_recipe2.EquipmentResult = equ_result
                        if_recipe2.GroupName="flow_meter"
                        if_recipe2.item_cd = "flow_meter2"
                        if_recipe2.item_val = dic_flow_meter.get("flow_meter2", None)
                        if_recipe2._created = now
                        if_recipe2.save()


                    screw_items = recipe_items.get("screw_items", None)
                    if screw_items:
                        item_cd = screw_items.get("item_cd", [])
                        item_val = screw_items.get("item_val", [])
                        idx = 0
                        for cd in item_cd:
                            if_recipe = IFEquipmentRecipe()
                            if_recipe.EquipmentResult = equ_result
                            if_recipe.GroupName="screw_items"
                            if_recipe.item_cd = cd
                            if_recipe.item_val = item_val[idx]
                            if_recipe._created = now
                            if_recipe.save()
                            idx = idx+1

            except Exception as rrrex:
                LogWriter.add_dblog("error", source + " recipe", rrrex)



            if is_alarm:
                for alarm_item in alarm_items:

                    equip_alarm_history = EquipAlarmHistory()
                    equip_alarm_history.equ_cd = equ_cd

                    alarm_code = alarm_item.get("alarm_code", "")
                    module_no = alarm_item.get("module_no", None)

                    if is_mounter:
                        alarm_code = f'{equ_cd}.alm.{alarm_code}'
                        if module_no:
                            equip_alarm_history.equ_cd =  f"{equ_cd}{module_no}"

                    # [{"onoff": 1, "end_dt": null, "start_dt": "2025-05-19T16:35:04+09:00", "alarm_msg": "Unable to locate the target object. (Additional)", "module_no": "15", "alarm_code": "8000D760", "part_number": "N20.004-00"}]
                    
                    
                    equip_alarm_history.alarm_code = alarm_code
                    equip_alarm_history.module_no = module_no
                    equip_alarm_history.details = alarm_item.get("alarm_msg", "")
                    equip_alarm_history.part_number = alarm_item.get("part_number", None)
                    onoff = alarm_item.get("onoff", None)
                    if onoff:
                        equip_alarm_history.onoff = str(onoff)

                    
                    str_start_dt = alarm_item.get("start_dt", None)
                    str_end_dt = alarm_item.get("end_dt", None)
                    
                    if str_start_dt:
                        try:
                            start_dt = datetime.strptime(str_start_dt,'%Y-%m-%dT%H:%M:%S%z')
                            equip_alarm_history.start_dt = start_dt
                        except Exception as sddex:
                            LogWriter.add_dblog("error", source, sddex)

                    if str_end_dt:
                        try:
                            end_dt = datetime.strptime(str_end_dt,'%Y-%m-%dT%H:%M:%S%z')
                            equip_alarm_history.end_dt = end_dt
                        except Exception as eddex:
                            LogWriter.add_dblog("error", source, eddex)

                    equip_alarm_history.rst_id = equ_result.id
                    equip_alarm_history.data_date = data_date
                    equip_alarm_history.save()
            
        except Exception as ex:
            LogWriter.add_dblog("error", source, ex)
        return
   
