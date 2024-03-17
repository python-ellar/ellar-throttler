from ellar.common import Controller, get

from ellar_throttler import Throttle

from .service import AppService


@Throttle(annon={"limit": 2, "ttl": 10})  # overriding annon[throttler] config
@Controller("/limit")
class LimitController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    def get_throttled(self):
        return self.app_service.success()

    @Throttle(annon={"limit": 5, "ttl": 10})  # overriding annon[throttler] config
    @get("/higher")
    def get_higher(self):
        return self.app_service.success()

    @get("/shorter")
    @Throttle(
        annon={"limit": 3, "ttl": 5}, user={"limit": 3, "ttl": 3}
    )  # overriding annon and user throttler config
    def get_shorter(self):
        return self.app_service.success()

    @get("/shorter-2")
    @Throttle(
        annon={"limit": 2, "ttl": 5}, user={"limit": 2, "ttl": 3}
    )  # overriding annon and user throttler config
    def get_shorter_2(self):
        return self.app_service.success()
