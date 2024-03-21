from ellar.common import Module

from ellar_throttler import AnonymousThrottler, ThrottlerModule

from .controller.module import ControllerModule


@Module(
    modules=(
        ControllerModule,
        ThrottlerModule.setup(
            throttlers=[AnonymousThrottler(name="annon", limit=5, ttl=60)]
        ),
    )
)
class AppModule:
    pass
