from app.controller.module import ControllerModule
from app.simple_guard import SimpleGuard
from ellar.testing import Test

from ellar_throttler import (
    AnonymousThrottler,
    ThrottlerInterceptor,
    ThrottlerModule,
    UserThrottler,
)

test_module_anon = Test.create_test_module(
    modules=(
        ThrottlerModule.setup(throttlers=[AnonymousThrottler(limit=5, ttl=100)]),
        ControllerModule,
    ),
    global_guards=[SimpleGuard],
)
test_module_anon.create_application().use_global_interceptors(ThrottlerInterceptor)


def test_anonymous_throttler_skip_if():
    _client = test_module_anon.get_test_client()

    res = _client.get("/")

    assert res.status_code == 200
    assert res.json() == {"success": True}

    assert "x-ratelimit-limit-anon" in res.headers

    res = _client.get("/?use_auth=true")

    assert res.status_code == 200
    assert res.json() == {"success": True}

    assert "x-ratelimit-limit-anon" not in res.headers
    assert "x-ratelimit-remaining-anon" not in res.headers
    assert "x-ratelimit-reset-anon" not in res.headers


def test_ignore_user_agent():
    test_module = Test.create_test_module(
        modules=(
            ThrottlerModule.setup(
                throttlers=[
                    UserThrottler(limit=5, ttl=100, ignore_user_agents=["testclient"])
                ]
            ),
            ControllerModule,
        ),
    )
    test_module.create_application().use_global_interceptors(ThrottlerInterceptor)
    _client = test_module.get_test_client()

    res = _client.get("/")

    assert res.status_code == 200
    assert res.json() == {"success": True}

    assert "x-ratelimit-limit-anon" not in res.headers
    assert "x-ratelimit-remaining-anon" not in res.headers
    assert "x-ratelimit-reset-anon" not in res.headers


def test_model_with_different_header_prefix():
    test_module = Test.create_test_module(
        modules=(
            ThrottlerModule.setup(
                throttlers=[
                    UserThrottler(limit=5, ttl=100, header_prefix="X-Custom-Throttle")
                ]
            ),
            ControllerModule,
        ),
    )
    test_module.create_application().use_global_interceptors(ThrottlerInterceptor)
    _client = test_module.get_test_client()

    res = _client.get("/")

    assert res.status_code == 200
    assert res.json() == {"success": True}

    assert "x-custom-throttle-limit-user" in res.headers
    assert "x-custom-throttle-remaining-user" in res.headers
    assert "x-custom-throttle-reset-user" in res.headers
