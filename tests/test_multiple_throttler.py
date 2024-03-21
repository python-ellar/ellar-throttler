import time

from app.controller.module import ControllerModule
from app.simple_guard import SimpleGuard
from ellar.testing import Test

from ellar_throttler import (
    AnonymousThrottler,
    ThrottlerInterceptor,
    ThrottlerModule,
    UserThrottler,
)

test_module_mixed = Test.create_test_module(
    modules=(
        ThrottlerModule.setup(
            throttlers=[
                AnonymousThrottler(limit=5, ttl=30),
                UserThrottler(limit=50, ttl=120),
            ]
        ),
        ControllerModule,
    ),
    global_guards=[SimpleGuard],
)

test_module_mixed.create_application().use_global_interceptors(ThrottlerInterceptor)


def test_all_registered_throttlers():
    _client = test_module_mixed.get_test_client()

    res = _client.get("/")

    assert res.status_code == 200
    assert res.json() == {"success": True}

    assert res.headers["x-ratelimit-limit-anon"] == "5"
    assert res.headers["x-ratelimit-remaining-anon"] == "4"
    assert res.headers["x-ratelimit-reset-anon"] == "29"

    assert res.headers["x-ratelimit-limit-user"] == "50"
    assert res.headers["x-ratelimit-remaining-user"] == "49"
    assert res.headers["x-ratelimit-reset-user"] == "119"


def test_anonymous_throttler_breaks():
    _client = test_module_mixed.get_test_client()

    for _ in range(6):
        res = _client.get("/")

    assert res.status_code == 429

    assert res.headers["retry-after-anon"] == "29"


def test_user_throttler_breaks():
    _client = test_module_mixed.get_test_client()

    for _ in range(51):
        res = _client.get("/?use_auth=true")

    assert res.status_code == 429

    assert res.headers["retry-after-user"] == "119"


def test_sustained_burst():
    test_module = Test.create_test_module(
        modules=(
            ThrottlerModule.setup(
                throttlers=[
                    AnonymousThrottler(name="burst", limit=6, ttl=6),
                    AnonymousThrottler(name="sustained", limit=100, ttl=144),
                ]
            ),
            ControllerModule,
        )
    )
    test_module.create_application().use_global_interceptors(ThrottlerInterceptor)

    _client = test_module.get_test_client()

    for _ in range(7):
        res = _client.get("/")
        time.sleep(0.5)  # quick restart

    assert res.status_code == 429

    time.sleep(2)  # quick restart
    res = _client.get("/")

    for _ in range(5):
        res = _client.get("/")

    assert res.headers["x-ratelimit-limit-sustained"] == "100"
    assert res.headers["x-ratelimit-remaining-sustained"] == "88"
    assert res.headers["x-ratelimit-reset-sustained"] == "138"
