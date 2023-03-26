from ellar.common import Module

from ellar_throttler import ThrottlerModule

from .app import AppController
from .default import DefaultController
from .limit import LimitController
from .service import AppService


@Module(
    modules=[ThrottlerModule.setup(limit=5, ttl=60)],
    controllers=(DefaultController, LimitController, AppController),
    providers=[AppService],
)
class ControllerModule:
    pass
