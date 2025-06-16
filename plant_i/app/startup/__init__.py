
import os, atexit, json
from django.apps import AppConfig
from .mqtt import MQTTApplication
from configurations import settings
from datetime import datetime
# 파일 락(lock file) 또는 OS-level mutex로 프로세스 중복 방지
#lock_file_path = os.path.join(tempfile.gettempdir(), 'planti_web_app.lock')
lock_file_path = "C:\\devprojects\\planti_web_app.lock"


def mark_running(start_position):    
    timestamp = datetime.now().timestamp()

    #print(f"call mark_running....{lock_file_path}")
    dic_data = {"timestamp" : timestamp, "pid" : os.getpid(), "start_position" : start_position}
    json_data = json.dumps(dic_data)
    with open(lock_file_path, 'w') as f:
        f.write(json_data)

    # 종료시 호출되는 메서드를 등록했으나, 실제 호출되지 않음
    atexit.register(on_exit)

def is_already_running():
    exist_flag =  os.path.exists(lock_file_path)
    if not exist_flag:
        return exist_flag
    try:
        with open(lock_file_path, 'r') as f:
            data = f.read()
            dic_data =json.loads(data)

            now_timestamp = datetime.now().timestamp()
            old_timestamp = dic_data.get('timestamp', 0)

            sec = now_timestamp-old_timestamp
            if(sec>15):
                print(f"diff seconds :  {sec}")
                return False
            else:
                mark_running("is_already_running")
                return True

    except Exception as ex:
        print(ex)
        raise ex


    return os.path.exists(lock_file_path)

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
            
        if settings.MAIN_APP_RUN:
            #print("마이그레이션금지==> settings.MAIN_APP_RUN : ", settings.MAIN_APP_RUN)
            if is_already_running():
                print("#########already_running###########")
                return

            mark_running("MainAppConfig.ready")

            mqtt_application = MQTTApplication()
            mqtt_application.ready()

        return