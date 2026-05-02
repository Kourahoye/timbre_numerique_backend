from django.apps import AppConfig


class TimbreConfig(AppConfig):
    name = 'timbre'

    def ready(self):
        import timbre.signals   