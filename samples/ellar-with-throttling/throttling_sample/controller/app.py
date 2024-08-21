from ellar.common import Controller, get

from ellar_throttler import Throttle, SkipThrottle

from .service import AppService


@Controller("/")
@Throttle(annon={"limit": 2, "ttl": 10})
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    async def test(self, use_auth: bool):
        return self.app_service.success(use_auth)

    @get("/ignored")
    @SkipThrottle()
    async def ignored(self, use_auth: bool):
        return self.app_service.ignored(use_auth)
