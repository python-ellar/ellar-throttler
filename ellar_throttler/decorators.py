import typing as t

from ellar.reflect import reflect

from .constants import THROTTLER_LIMIT, THROTTLER_SKIP, THROTTLER_TTL


def _set_throttler_metadata(target: t.Callable, limit: int, ttl: int) -> None:
    reflect.define_metadata(THROTTLER_TTL, ttl, target)
    reflect.define_metadata(THROTTLER_LIMIT, limit, target)


def throttle(*, limit: int = 20, ttl: int = 60) -> t.Callable:
    """
    Adds metadata to the target which will be handled by the ThrottlerGuard to
    handle incoming requests based on the given metadata.

    Usage:
    Use on controllers or individual route functions

    @throttle(limit=20, ttl=300)
    class ControllerSample:
        @throttle(limit=20, ttl=300)
        async def index(self):
            ...

    :param limit: Guard Type or Instance
    :param ttl: Guard Type or Instance
    :return: Callable
    """

    def decorator(func: t.Callable) -> t.Callable:
        _set_throttler_metadata(func, limit=limit, ttl=ttl)
        return func

    return decorator


def skip_throttle(skip: bool = True) -> t.Callable:
    """
    Adds metadata to the target which will be handled by the ThrottlerGuard
    whether to skip throttling for this context.

    Usage:
    Use on controllers or individual route functions

    @throttle(limit=20, ttl=300)
    class ControllerSample:
        @skip_throttle()
        async def index(self):
            ...

        @skip_throttle(false)
        async def create(self):
            ...

    :param skip:
    :return:
    """

    def decorator(func: t.Callable) -> t.Callable:
        reflect.define_metadata(THROTTLER_SKIP, skip, func)
        return func

    return decorator
