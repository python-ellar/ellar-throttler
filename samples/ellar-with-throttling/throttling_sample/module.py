from ellar.common import Module

from ellar_throttler import AnonymousThrottler, ThrottlerModule, UserThrottler

from .controller.module import ControllerModule


@Module(
    modules=(
        ControllerModule,
        ThrottlerModule.setup(
            throttlers=[
                AnonymousThrottler(name="annon", limit=5, ttl=60),
                UserThrottler(limit=100, ttl=60),
                # AnonymousThrottler(name='burst', limit=6, ttl=6),
                # AnonymousThrottler(name='sustained', limit=100, ttl=144)
            ]
        ),
    )
)
class AppModule:
    pass
