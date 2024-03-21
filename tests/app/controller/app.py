from ellar.common import Controller, get

from ellar_throttler import SkipThrottle, Throttle

from .service import AppService


@Controller("/")
@Throttle(annon={"limit": 2, "ttl": 10})
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    async def test(self):
        return self.app_service.success()

    @get("/ignored")
    @SkipThrottle()
    async def ignored(self):
        return self.app_service.ignored()
