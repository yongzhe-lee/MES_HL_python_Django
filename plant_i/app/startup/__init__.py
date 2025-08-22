
import os, atexit, json
from django.apps import AppConfig
#from .mqtt import MQTTApplication
#from .mqtt import MQTTApplication4DT
#from configurations import settings
from datetime import datetime
# 파일 락(lock file) 또는 OS-level mutex로 프로세스 중복 방지
#lock_file_path = os.path.join(tempfile.gettempdir(), 'planti_web_app.lock')
lock_file_path = "C:\\devprojects\\planti_web_app.lock"


def mark_running(start_position):    
    timestamp = datetime.now().timestamp()

    #print(f"call mark_running....{lock_file_path}")
    dic_data = {"timestamp" : timestamp, "pid" : os.getpid(), "start_position" : start_position}
    json_data = json.dumps(dic_data)

    try:
        with open(lock_file_path, 'w') as f:
            f.write(json_data)

        #종료시 호출되는 메서드를 등록했으나, 실제 호출되지 않음
        atexit.register(on_exit)

    except Exception as ex:
        print(ex)

    return


def is_already_running():
    exist_flag =  os.path.exists(lock_file_path)
    if not exist_flag:
        return exist_flag

    now_dt = datetime.now()
    try:
        dic_data = {}
        with open(lock_file_path, 'r') as f:
            data = f.read()
            dic_data =json.loads(data)

        now_timestamp = now_dt.timestamp()
        old_timestamp = dic_data.get('timestamp', 0)

        sec = now_timestamp-old_timestamp
        if(sec>1):
            print(f"diff seconds :  {sec}")
            return False
        else:
            mark_running("is_already_running")
            return True

    except Exception as ex:
        print(ex)


    return exist_flag

def on_exit():
    '''
    어플리케이션 종료시 실제로 호출되지 않음
    '''
    try:
        #print("call on_exit....")
        os.remove(lock_file_path)
    except FileNotFoundError:
        pass

class MainAppConfig(AppConfig):
    name = 'app.startup'
    def ready(self):
        #DT용 MQTT를 활성화함. 그때 그때 필요할때 구독하는게 좋은데 일단 있는 소스를 활용해서 받아 보자
        #MQTTApplication4DT().ready()
        return