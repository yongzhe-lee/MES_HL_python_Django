import json, time, threading
import paho.mqtt.client as mqtt
from configurations import settings

###############################################################################
# PORT : MQTT 1883, WEBSOCKET 9001
###############################################################################

class FacadeMQTTClient(object):

    __MQTT_CONNECTION_MESSAGE = {
        0 : 'success, connection accepted ',
        1 : 'connection refused, bad protocol ',
        2 : 'refused, client-id error ',
        3 : 'refused, service unavailable',
        4 : 'refused, bad username or password ',
        5 : 'refused, not authorized'
    }

    __mqtt_client__ = None
    __initialized = False
    __mqtt_thread = None
    __dic_topic_handler = {}

    @classmethod
    def initialize(cls, host, port, username=None, password=None):

        if cls.__initialized:
            raise Exception('FacadeMQTTClient.initialize duplicated')

        # 클라이언트 아이디를 지정한다(반드시)
        cls.__mqtt_client__ = mqtt.Client()
        #cls.__mqtt_client__ = mqtt.Client(client_id='mes21_mes_api', clean_session=False)

        cls.__mqtt_client__.on_connect = cls.on_connect
        cls.__mqtt_client__.on_message = cls.on_message
        cls.__mqtt_client__.on_disconnect = cls.on_disconnect

        if username:
            cls.__mqtt_client__.username_pw_set(username=username, password=password)

        try:
            ack = cls.__mqtt_client__.connect(host, port, 60)
            if ack !=0:
                message = cls.__MQTT_CONNECTION_MESSAGE.get(ack)
                print(message)
                raise Exception(message)

        except Exception as ex:
            message = 'cannot connect mqtt server'
            print(message)
            assert()

        # 접속이 끊어 졌다거 다시 연결시에 재 구독 할수 있도록 함        
        cls.__mqtt_thread = threading.Thread(target = cls.__mqtt_client__.loop_forever)
        cls.__mqtt_thread.start()

        cls.__initialized = True
        return

    @classmethod
    def set_topic_handler(cls, topic, handler):
        cls.__dic_topic_handler[topic] = handler
        return

    @classmethod
    def apply_topic_handler(cls):
        for topic,v in cls.__dic_topic_handler.items():
            cls.__mqtt_client__.subscribe(topic, qos=2)

        return

    @classmethod
    def subscribe(cls, topic, handler):
        cls.__dic_topic_handler[topic] = handler
        cls.__mqtt_client__.subscribe(topic, qos=2)
        return

    #added by choi : 2025/08/18
    @classmethod
    def unsubscribe_all(cls):
        if cls.__mqtt_client__:
            for t in list(cls.__dic_topic_handler.keys()):                
                cls.__mqtt_client__.unsubscribe(t)
            # 핸들러도 제거
            for t in list(cls.__dic_topic_handler.keys()):   
                del cls.__dic_topic_handler[t]

    @classmethod
    def on_message(cls, client, userdata, msg):

        topic = msg.topic
        payload = msg.payload
        #print('on_message - topic :', topic, ',  payload :', payload)

        try:
            if topic in cls.__dic_topic_handler:
                cls.__dic_topic_handler[topic](topic, payload)
            else:
                print('topic error :', topic)

        except Exception as ex:
            # collection or tracking 호출후에 exception 발생이 되어도 무시
            print(ex)

        return

    @classmethod
    def on_connect(cls, client, userdata, flags, rc):
        # The callback for when the client receives a CONNACK response from the server.
        message = '@@@@@@@@@@@@@@@@@@@@ MQTT Server {} on_connect @@@@@@@@@@@@@@@@@@@@'.format(client._host)
        print(message)
        # 접속이 끊어 졌다거 다시 연결시에 재 구독 할수 있도록 함
        for topic, handler in cls.__dic_topic_handler.items():
            cls.__mqtt_client__.subscribe(topic) 

        return

    @classmethod
    def on_disconnect(cls, client, userdata, rc):
        print('#################### on_disconnect #######################')
        return

    @classmethod
    def reconnect(cls):
        return cls.__mqtt_client__.reconnect()

    @classmethod
    def publish(cls, topic, payload, qos=2, retain=False):
        result = cls.__mqtt_client__.publish(topic, payload=payload, qos=qos, retain=retain)
        return result



class SystemEventService(object):

    def __init__(self):
        pass

    def job_start_event_publish(self, jobres):
        
        work_order_number = jobres.WorkOrderNumber
        equipment = jobres.Equipment
        material = jobres.Material

        dic_data={
            'event_type': 'job_start',
            'work_order_number' : work_order_number,
            'equipment_name' : equipment.Name,
            'material_name' : material.Name
        }
        topic = settings.TOPIC_SYSTEM_EVENT
        payload = json.dumps(dic_data)
        result = FacadeMQTTClient.publish(topic, payload, 2, False)
        return result
