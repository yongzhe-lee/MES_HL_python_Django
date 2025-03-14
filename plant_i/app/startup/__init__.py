import importlib
import json, threading, time
from datetime import datetime

from django.apps import AppConfig
from configurations import settings
from .mqtt import MQTTApplication
#from domain.application.daily import daily_closing


class MainAppConfig(AppConfig):
    name = 'app.startup'

    def ready(self):

        from domain.services.logging import LogWriter
        print("settings.MAIN_APP_RUN : ", settings.MAIN_APP_RUN)

        if settings.MAIN_APP_RUN:
            mqtt_application = MQTTApplication()
            mqtt_application.ready()



            #logging_thread = threading.Thread(target=LogWriter.do_send_sf_log)
            #logging_thread.start()
            # 추가로 가동할 APP가 있으면 아래 추가
            #daily_closing(self)
            #from domain.services.mobile.task import ThermometerAlaramTask
            #task = ThermometerAlaramTask()
            #thermo_thread = threading.Thread(target=task.do_alaram_check)
            #thermo_thread.start()
            #from domain.services.kpc import KpcKpiService
            #kpc_kpi_service = KpcKpiService()
            #kpi_thread = threading.Thread(target= kpc_kpi_service.do_send_kpi_log)
            #kpi_thread.start()

        return


    