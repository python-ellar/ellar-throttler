from ellar.common import Controller, get

from .service import AppService


@Controller("/default")
class DefaultController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    def get_default(self):
        return self.app_service.success()
