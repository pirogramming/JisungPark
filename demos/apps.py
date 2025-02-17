from django.apps import AppConfig


class DemosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'demos'

    def ready(self):
        import demos.signals  # 시그널 등록