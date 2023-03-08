from ellar.common import Controller, get

from ellar_throttler import throttle

from .service import AppService


@throttle(limit=2, ttl=10)
@Controller("/limit")
class LimitController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    def get_throttled(self):
        return self.app_service.success()

    @throttle(limit=5, ttl=10)
    @get("/higher")
    def get_higher(self):
        return self.app_service.success()

    @get("/shorter")
    @throttle(limit=5, ttl=2)
    def get_shorter(self):
        return self.app_service.success()

    @get("/shorter-2")
    @throttle(limit=5, ttl=2)
    def get_shorter_2(self):
        return self.app_service.success()
