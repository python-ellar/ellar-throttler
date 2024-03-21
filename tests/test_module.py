import pytest
from app.controller.module import ControllerModule
from ellar.cache import CacheModule
from ellar.cache.backends.local_cache import LocalMemCacheBackend
from ellar.testing import Test

from ellar_throttler import (
    AnonymousThrottler,
    CacheThrottlerStorageService,
    ThrottlerInterceptor,
    ThrottlerModule,
)


def test_module_register_setup():
    tm = Test.create_test_module(
        modules=(
            ThrottlerModule.register_setup(ignore_user_agents=["api-edx"]),
            ControllerModule,
            CacheModule.setup(default=LocalMemCacheBackend()),
        ),
        config_module={
            "ELLAR_THROTTLER_CONFIG": {
                "throttlers": [AnonymousThrottler(limit=5, ttl=100)],
                "storage": CacheThrottlerStorageService,
            }
        },
    )
    tm.create_application().use_global_interceptors(ThrottlerInterceptor)

    _client = tm.get_test_client()

    for _ in range(6):
        res = _client.get("/limit/")
    assert res.status_code == 429
    assert "Request was throttled. Expected available in" in res.json()["detail"]
    assert "retry-after-anon" in res.headers


def test_module_register_setup_fails():
    tm = Test.create_test_module(
        modules=(
            ThrottlerModule.register_setup(ignore_user_agents=["api-edx"]),
            ControllerModule,
            CacheModule.setup(default=LocalMemCacheBackend()),
        ),
    )
    with pytest.raises(RuntimeError):
        tm.create_application().use_global_interceptors(ThrottlerInterceptor)
