import typing as t

from ellar.common import constants, set_metadata
from ellar.reflect import reflect

from .constants import THROTTLER_LIMIT, THROTTLER_SKIP, THROTTLER_TTL
from .throttler_interceptor import ThrottlerInterceptor


class _Config(t.TypedDict):
    # Overriding limit of specific throttler through scope
    limit: int
    #  Overriding ttl of specific throttler through scope
    ttl: int


def Throttle(*, apply_interceptor: bool = False, **kwargs: _Config) -> t.Callable:
    """
    Adds metadata to the target which will be handled by the ThrottlerGuard to
    handle incoming requests based on the given metadata.

    Usage:
    Use on controllers or individual route functions

    @Throttle(throttler_model_name={'limit':20, 'ttl':300})
    class ControllerSample:
        @Throttle('user', limit=20, ttl=300)
        async def index(self):
            ...

    :param apply_interceptor: Indicates whether to apply ThrottlerInterceptor
    :param kwargs: Throttler name used in setting up ThrottlerModule with overriding config
    :return: Callable
    """

    def decorator(func_: t.Callable) -> t.Callable:
        if isinstance(kwargs, dict):
            for k, v in kwargs.items():
                reflect.define_metadata(f"{THROTTLER_TTL}-{k}", v.get("ttl"), func_)
                reflect.define_metadata(f"{THROTTLER_LIMIT}-{k}", v.get("limit"), func_)

        if apply_interceptor:
            return set_metadata(constants.ROUTE_INTERCEPTORS, [ThrottlerInterceptor])(  # type:ignore[no-any-return]
                func_
            )

        return func_

    return decorator


def SkipThrottle(**throttler_names: bool) -> t.Callable:
    """
    Adds metadata to the target which will be handled by the ThrottlerInterceptor
    whether to skip throttling for this context.

    Usage:
    Use on controllers or individual route functions

    @Throttle(throttler_model_name={'limit':20, 'ttl':300})
    class ControllerSample:
        @SkipThrottle()
        async def index(self):
            This will skip all throttlers for the target

        @SkipThrottle(throttler_model_name=True)
        async def create(self):
            This will skip only `throttler_model_name` throttler and execute others for the target

    :param throttler_names: Throttler name used in setting up ThrottlerModule with overriding config
    :return: Callable
    """

    def decorator(func_: t.Callable) -> t.Callable:
        if throttler_names:
            for k, v in throttler_names.items():
                reflect.define_metadata(f"{THROTTLER_SKIP}-{k}", v, func_)
            return func_

        reflect.define_metadata(THROTTLER_SKIP, True, func_)
        return func_

    return decorator
