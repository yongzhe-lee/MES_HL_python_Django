from django.apps import AppConfig

class MainAppConfig(AppConfig):
    name = 'app.startup'

    def ready(self):
        print("✅ 앱이 로드됨: MainAppConfig.ready() 실행됨")

        from configurations import settings
        if settings.MAIN_APP_RUN:
            print(f"settings.MAIN_APP_RUN: {settings.MAIN_APP_RUN}")
