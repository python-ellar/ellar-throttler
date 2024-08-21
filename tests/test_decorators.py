from ellar.common import constants
from ellar.reflect import reflect

from ellar_throttler import SkipThrottle, Throttle, ThrottlerInterceptor
from ellar_throttler.constants import THROTTLER_LIMIT, THROTTLER_SKIP, THROTTLER_TTL


def test_throttle_defines_interceptor():
    @Throttle(intercept=True)
    def target():
        pass

    value = reflect.get_metadata(constants.ROUTE_INTERCEPTORS, target)
    assert value == [ThrottlerInterceptor]


def test_throttle_defines_extra_config_for_throttlers():
    @Throttle(tm1={"ttl": 40, "limit": 200}, tm2={"ttl": 50, "limit": 100})
    def target():
        pass

    tm1_ttl = reflect.get_metadata(f"{THROTTLER_TTL}-tm1", target)
    tm1_limit = reflect.get_metadata(f"{THROTTLER_LIMIT}-tm1", target)
    assert f"{tm1_limit}/{tm1_ttl}" == "200/40"

    tm2_ttl = reflect.get_metadata(f"{THROTTLER_TTL}-tm2", target)
    tm2_limit = reflect.get_metadata(f"{THROTTLER_LIMIT}-tm2", target)

    assert f"{tm2_limit}/{tm2_ttl}" == "100/50"

    value = reflect.get_metadata(constants.ROUTE_INTERCEPTORS, target)

    assert value is None


def test_throttle_does_not_add_interceptor():
    @Throttle()
    def target():
        pass

    value = reflect.get_metadata(constants.ROUTE_INTERCEPTORS, target)

    assert value is None


def test_skip_skip_throttle():
    @SkipThrottle()
    def target():
        pass

    value = reflect.get_metadata(THROTTLER_SKIP, target)
    assert value is True


def test_skip_throttle_by_throttler_name():
    @SkipThrottle(tm1=True, tm2=True)
    def target():
        pass

    tm1_value = reflect.get_metadata(f"{THROTTLER_SKIP}-tm1", target)
    tm2_value = reflect.get_metadata(f"{THROTTLER_SKIP}-tm2", target)

    assert tm1_value == tm2_value is True
