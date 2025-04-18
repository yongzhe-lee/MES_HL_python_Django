from django.apps import AppConfig

from .mqtt import MQTTApplication
from configurations import settings


class MainAppConfig(AppConfig):
    name = 'app.startup'
    def ready(self):

        from domain.services.logging import LogWriter
        print("settings.MAIN_APP_RUN : ", settings.MAIN_APP_RUN)

        if settings.MAIN_APP_RUN:
            mqtt_application = MQTTApplication()
            mqtt_application.ready()


        return


    