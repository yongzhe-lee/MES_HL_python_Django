import json, threading, importlib
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


        '''
        (1, 'hpc1.load', 'HPC#1 매거진로더', '은일', now(), now(), 1, 1, '', '', 1),
(2, 'hpc1.flash' , 'HPC#1플래쉬프로그램입력', '코어솔루션', now(), now(), 1, 1, 'PCU111001', '', 1),
(3, 'hpc1.ict' , 'HPC#1 ICT', '코어솔루션', now(), now(), 1, 1, '', 'PCU112001', 1),
(4, 'hpc1.coatload', 'HPC#1 PCB코팅로더', 'CJT', now(), now(), 1, 1, '', '', 1),
(5, 'hpc1.coating1', 'HPC#1 Conformal코팅1', '', now(), now(), 1, 1, '', '', 1),
(6, 'hpc1.coating2', 'HPC#1 Conformal코팅2', '', now(), now(), 1, 1, '', '', 1),
(7, 'hpc1.coatvision', 'HPC#1 PCB코팅비젼', '', now(), now(), 1, 1, '', '', 1),
(8, 'hpc1.pcbrev', 'HPC#1 PCB반전', 'CJT', now(), now(), 1, 1, '', '', 1),
(9, 'hpc1.curr', 'HPC#1 코팅경화Curing', 'YJE', now(), now(), 1, 1, '', '', 1),
(10, 'hpc1.frobackload', 'HPC#1 프론트백로더', 'CJT', now(), now(), 1, 1, '', '', 1),
(11, 'hpc1.uh.load', 'HPC#1 Upper 하우징 로딩', 'CJT', now(), now(), 1, 1, '', '', 1),
(12, 'hpc1.tim', 'HPC#1 TIM도포', 'CJT', now(), now(), 1, 1, '', '', 1),
(13, 'hpc1.lh.load', 'HPC#1 Lower하우징로딩', 'CJT', now(), now(), 1, 1, '', '',1),
(14, 'hpc1.scrwt', 'HPC#1 스크류체결', 'CJT', now(), now(), 1, 1, '', '',1),
(15, 'hpc1.scrwt.height', 'HPC#1 스크류높이체크', 'CJT', now(), now(), 1, 1, '', '',1),
(16, 'hpc1.fclip', 'HPC#1 Fan&Clip Fan조립', 'CJT', now(), now(), 1, 1, '', '', 1),
(17, 'hpc1.fclip.height', 'HPC#1 Fan&Clip 높이체크', 'CJT', now(), now(), 1, 1, '', '', 1),
(18, 'hpc1.fclip.clip', 'HPC#1 Fan&Clip 클립', 'CJT', now(), now(), 1, 1, '', '', 1),
(19, 'hpc1.eol1', 'HPC#1 EOL1', '일신', now(), now(), 1, 1, '', '', 1),
(20, 'hpc1.eol2', 'HPC#1 EOL2', '일신', now(), now(), 1, 1, '', '', 1),
(21, 'hpc1.pinchk', 'HPC#1 Pin검사', 'CJT', now(), now(), 1, 1, '', '', 1),
(22, 'hpc1.labeling', 'HPC#1 Pin검사 라벨링', 'CJT', now(), now(), 1, 1, '', '', 1),
(23, 'hpc1.brackassm', 'HPC#1 브라켓조립', 'CJT', now(), now(), 1, 1, '', '', 1),
(24, 'hpc1.brackassm.height', 'HPC#1 브라켓높이', 'CJT', now(), now(), 1, 1, '', '', 1)

        '''


        dic_rst_topic = {
            'RST_hpc1.load' : ConrolPCResultMessageHandler.handler,
            'RST_hpc1.ict' : ConrolPCResultMessageHandler.handler,
            'RST_hpc1.coatload1' : ConrolPCResultMessageHandler.handler,
            'RST_hpc1.coatload2' : ConrolPCResultMessageHandler.handler,
        }


        '''
        PCU111001	PCU#1 Flash
        PCU112001	PCU#1 ICT
        PCU113001	PCU#1 Coating Vision#1
        PCU114001	PCU#1 Coating Vision#2
        PCU121001	PCU#1 Housing & PCB Assembly
        PCU122001	PCU#1 Cover Screw
        PCU123001	PCU#1 Cover Screw Height
        PCU124001	PCU#1 Fan Assembly
        PCU125001	PCU#1 Fan Screw
        PCU126001	PCU#1 Fan Screw Height
        PCU127001	PCU#1 Clip Wire Assembly
        PCU131001	PCU#1 EOL Test#1
        PCU131002	PCU#1 EOL Test#2
        PCU132001	PCU#1 Pin Check
        PCU133001	PCU#1 Labeling
        PCU134001	PCU#1 Bracket Assembly
        PCU135001	PCU#1 Bracket Assembly Check
        PCU151001	PCU#1 Tim Dispensing Vision


        SMT#4 설비코드

        '''



        FacadeMQTTClient.apply_topic_handler()

        return

class ConrolPCResultMessageHandler():
    def __init__(self):
        pass

    @classmethod
    def handler(cls, payload):
        dic_payload = json.loads(payload)

        equ_cd = dic_payload.get('equ_cd', None)
        mat_cd = dic_payload.get('mat_cd', None)
        rev_no = dic_payload.get('rev_no', None)

        try:
            print("aa")
        except Exception as ex:
            print(ex)

        return



class DeviceMessageHandler():

    @classmethod
    def initialize(cls):
        print("DeviceMessageHandler.initialize")
        return

    @classmethod
    def device_data_handler(cls, payload):
        '''
        클레무브에서 사용할지 검토필요
        설비별 DT 상태 업데이트 용으로 사용할 떄 설비별 TOPIC으로 분리해서 처리할 필요 있음
        '''


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
    def device_event_handler(cls, payload):
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

