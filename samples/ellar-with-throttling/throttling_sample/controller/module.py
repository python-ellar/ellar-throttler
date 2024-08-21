from ellar.common import Module

from .app import AppController
from .default import DefaultController
from .limit import LimitController
from .service import AppService


@Module(
    controllers=(DefaultController, LimitController, AppController),
    providers=[AppService],
)
class ControllerModule:
    pass
