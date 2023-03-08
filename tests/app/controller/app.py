from ellar.common import Controller, get

from ellar_throttler import skip_throttle, throttle

from .service import AppService


@Controller("/")
@throttle(limit=2, ttl=10)
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    async def test(self):
        return self.app_service.success()

    @get("/ignored")
    @skip_throttle()
    async def ignored(self):
        return self.app_service.ignored()
