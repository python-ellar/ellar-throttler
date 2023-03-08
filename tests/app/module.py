from ellar.common import Module

from .controller.module import ControllerModule


@Module(modules=(ControllerModule,))
class AppModule:
    pass
