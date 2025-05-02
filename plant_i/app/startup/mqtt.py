
import json, threading,time, importlib
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder

from configurations import settings
from domain.services.mqtt import FacadeMQTTClient


###############################################################################
# topic 
#    device_data
#    device_event
###############################################################################

class MQTTApplication():

    ###########################################################################
    def ready(self):

        # MQTT client 초기화
        if settings.MOSQUITTO_USERNAME:
            FacadeMQTTClient.initialize(settings.MOSQUITTO_HOST, settings.MOSQUITTO_MQTT_PORT, settings.MOSQUITTO_USERNAME, settings.MOSQUITTO_PASSWORD)
        else:
            FacadeMQTTClient.initialize(settings.MOSQUITTO_HOST, settings.MOSQUITTO_MQTT_PORT)

        # Device 메시지 핸들러 초기화
        DeviceMessageHandler.initialize()

        # 설비별 topic handler 등록, topic handler는 각 설비별로 다르게 구현되어야 함

        FacadeMQTTClient.set_topic_handler(settings.TOPIC_DEVICE_DATA, DeviceMessageHandler.device_data_handler)
        FacadeMQTTClient.set_topic_handler(settings.TOPIC_DEVICE_EVENT, DeviceMessageHandler.device_event_handler)


        plant_topic_thread = threading.Thread(target=self.mapping_equipment_topic_handler)
        plant_topic_thread.start()

        return

    def mapping_equipment_topic_handler(self):

        print("mapping_equipment_topic_handler ready...")
        # 10초간 대기, 어플리케이션이 시작되고 django ORM이 초기화될 때까지 대기
        time.sleep(10)
        print("mapping_equipment_topic_handler starting...")

        from domain.services.interface.equipment import IFEquipmentResultService
        if_equ_rst_servide = IFEquipmentResultService()
        arr_equ_cd = [
           "hpc1.load","hpc1.flash","hpc1.ict",
           "hpc1.coatload","hpc1.coating1","hpc1.coating2","hpc1.coatvision",
           "hpc1.pcbrev","hpc1.curr",
           "hpc1.frobackload","hpc1.uh.load",
           "hpc1.tim","hpc1.tim.assy",
           "hpc1.lh.load",
           "hpc1.scrwt","hpc1.scrwt.height",
           "hpc1.fclip","hpc1.fclip.height","hpc1.fclip.clip", "hpc1.fclip.screw",
           "hpc1.eol1","hpc1.eol2",
           "hpc1.pinchk","hpc1.labeling","hpc1.brackassm","hpc1.brackassm.height",
           "smt4.loader","smt4.laserrmarking","smt4.sp1","smt4.sp2","smt4.spi","smt4.mnt","smt4.pre-aoi","smt4.reflow","smt4.aoi","smt4.aoireview","smt4.unloader","hpc1.packing"
        ]

        for equ_cd in arr_equ_cd:
            rst_topic = "rst_" + equ_cd
            FacadeMQTTClient.set_topic_handler(rst_topic, if_equ_rst_servide.rst_equipment_topic_handler)




        FacadeMQTTClient.apply_topic_handler()
        print("mapping_equipment_topic_handler finish...")
        return


class DeviceMessageHandler():

    @classmethod
    def initialize(cls):
        print("DeviceMessageHandler.initialize")
        return

    @classmethod
    def device_data_handler(cls, topic, payload):
        '''
        클레무브에서 사용할지 검토필요
        설비별 DT 상태 업데이트 용으로 사용할 떄 설비별 TOPIC으로 분리해서 처리할 필요 있음
        '''
        print(topic)

        from domain.models.definition import DASConfig

        dic_payload = json.loads(payload)
        device_id = dic_payload.get('device', None)
        queryset = DASConfig.objects.filter(id=device_id)
        if len(queryset)==0:
            return

        try:
            das_config = queryset[0]
            handler = das_config.Handler
            config_filename = das_config.ConfigFileName

            # config 파일명을 이용할 것인지 여부 고민, 커스터마이징의 경우 고민
            module = importlib.import_module('domain.services.das.protocol')
            handler_func = getattr(module, handler, None)
            if handler_func:
                locals = handler_func(dic_payload, das_config)
                #success = result.get('success', False)
                equipment = das_config.Equipment
                dic_pub = {
                    'type':'notify',
                    'target':'device',
                    'action': 'read',
                    'equipment' : {'pk':equipment.id, 'name': equipment.Name},
                    'device': {'pk':das_config.id,'name': das_config.Name },
                    'locals': locals
                }
                pub_payload = json.dumps(dic_pub, cls=DjangoJSONEncoder, ensure_ascii=False)
                FacadeMQTTClient.publish(settings.TOPIC_HMI_DATA, pub_payload)

        except Exception as ex:
            print(ex);

        return

    @classmethod
    def device_event_handler(cls, topic, payload):
        '''
        parms = {
            'type': 'notify', 
            'target': 'device', 
            'action': 'error', 
            'device': 223, 
            'date': '2019-11-27T12:23:59.332+09:00', 
            'message': 'RequestModbusData.error - device_id : 223, host: 192.168.0.57'
        }
        '''

        from domain.models.definition import DASConfig
        print(topic)

        dic_payload = json.loads(payload)
        device_id = dic_payload.get('device', None)
        action = dic_payload.get('action', None)
        message = dic_payload.get('message', None)
        date = dic_payload.get('date', None)

        status = ''
        if action=='error':
            status = 'F'

        dic_result = {
            'success':True,
            'message':message,
            'status': status,
            'date' :date
        }

        if device_id:
            das_config = DASConfig.objects.get(id=device_id) 
            equipment = das_config.Equipment
            dic_pub = {
                'type':'notify',
                'target':'device',
                'action':action,
                'equipment' : { 'pk':equipment.id, 'name': equipment.Name },
                'device' : { 'pk':das_config.id,'name': das_config.Name },
                'locals': dic_result
            }
            pub_payload = json.dumps(dic_pub, cls=DjangoJSONEncoder, ensure_ascii=False)
            FacadeMQTTClient.publish(settings.TOPIC_HMI_DATA, pub_payload)

        return

