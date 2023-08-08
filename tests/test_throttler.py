import time

import pytest
from app.controller.module import ControllerModule
from app.server import app
from ellar.cache import CacheModule
from ellar.cache.backends.local_cache import LocalMemCacheBackend
from ellar.testing import Test, TestClient

from ellar_throttler import (
    CacheThrottlerStorageService,
    ThrottlerGuard,
    ThrottlerModule,
    ThrottlerStorageService,
)

client = TestClient(app)


class TestAppController:
    """
    Tests for setting `@throttle()` at the method level and for ignore routes
    """

    def test_ignored(self):
        res = client.get("/ignored")
        assert res.status_code == 200
        assert res.json() == {"ignored": True}
        assert "x-ratelimit-limit" not in res.headers
        assert "x-ratelimit-remaining" not in res.headers
        assert "x-ratelimit-reset" not in res.headers

    def test_index(self):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json() == {"success": True}
        assert res.headers["x-ratelimit-limit"] == "2"
        assert res.headers["x-ratelimit-remaining"] == "1"
        assert res.headers["x-ratelimit-reset"] == "9"


class TestLimitController:
    """
    Tests for setting `@throttle()` at the class level and overriding at the method level
    """

    @pytest.mark.parametrize(
        "url, limit",
        [
            ("/limit/", 2),
            ("/limit/higher", 5),
        ],
    )
    def test_limit_index(self, url, limit):
        for i in range(limit):
            res = client.get(url)
            assert res.status_code == 200
            assert res.json() == {"success": True}

            assert res.headers["x-ratelimit-limit"] == str(limit)
            assert res.headers["x-ratelimit-remaining"] == str(limit - (i + 1))
            assert "x-ratelimit-reset" in res.headers

        res = client.get(url)
        assert res.status_code == 429
        assert "Request was throttled. Expected available in" in res.json()["detail"]
        assert "retry-after" in res.headers


class TestDefaultController:
    """ "
    Tests for setting throttle values at the `module_configure` level
    """

    def test_default_controller_index(self):
        res = client.get("/default/")
        assert res.status_code == 200
        assert res.json() == {"success": True}

        assert res.headers["x-ratelimit-limit"] == "5"
        assert res.headers["x-ratelimit-remaining"] == "4"
        assert "x-ratelimit-reset" in res.headers


class TestSkipIfConfigure:
    def test_skip_configure(self):
        test_module = Test.create_test_module(
            modules=(
                ThrottlerModule.setup(limit=5, ttl=100, skip_if=lambda ctx: True),
                ControllerModule,
            ),
            global_guards=[ThrottlerGuard],
        )

        _client = test_module.get_test_client()
        for _i in range(15):
            res = _client.get("/")

            assert res.status_code == 200
            assert res.json() == {"success": True}

            assert "x-ratelimit-limit" not in res.headers
            assert "x-ratelimit-remaining" not in res.headers
            assert "x-ratelimit-reset" not in res.headers


class TestThrottlerStorageServiceConfiguration:
    test_module_cache = Test.create_test_module(
        modules=(
            ThrottlerModule.setup(
                limit=5, ttl=100, storage=CacheThrottlerStorageService
            ),
            CacheModule.register_setup(),
            ControllerModule,
        ),
        global_guards=[ThrottlerGuard],
        config_module={"CACHES": {"default": LocalMemCacheBackend()}},
    )

    test_module_use_value = Test.create_test_module(
        modules=(
            ThrottlerModule.setup(limit=5, ttl=100, storage=ThrottlerStorageService()),
            ControllerModule,
        ),
        global_guards=[ThrottlerGuard],
    )

    def request_for_limit(self, app_client, url, limit):
        for i in range(limit):
            res = app_client.get(url)
            assert res.status_code == 200
            assert res.json() == {"success": True}

            assert res.headers["x-ratelimit-limit"] == str(limit)
            assert res.headers["x-ratelimit-remaining"] == str(limit - (i + 1))
            assert "x-ratelimit-reset" in res.headers

    @pytest.mark.parametrize("test_module", [test_module_cache, test_module_use_value])
    def test_limit_index(self, test_module):
        _client = test_module.get_test_client()

        for url, limit in [("/limit/", 2), ("/limit/higher", 5)]:
            self.request_for_limit(_client, url, limit)
            res = _client.get(url)
            assert res.status_code == 429
            assert (
                "Request was throttled. Expected available in" in res.json()["detail"]
            )
            assert "retry-after" in res.headers

    @pytest.mark.parametrize("test_module", [test_module_cache, test_module_use_value])
    def test_limit_get_shorter(self, test_module):
        _client = test_module.get_test_client()
        limit, url = (
            5,
            "/limit/shorter",
        )

        self.request_for_limit(_client, url, limit)

        res = _client.get(url)
        assert res.status_code == 429
        time.sleep(1)  # quick restart
        res = _client.get(url)
        assert res.headers["x-ratelimit-remaining"] == str(limit - 1)

    @pytest.mark.parametrize("test_module", [test_module_use_value])
    def test_limit_get_shorter_cache_clear(self, test_module):
        _client = test_module.get_test_client()
        limit, url = (
            5,
            "/limit/shorter-2",
        )

        self.request_for_limit(_client, url, limit)

        res = _client.get(url)
        assert res.status_code == 429
        time.sleep(2)  # quick restart
        res = _client.get(url)
        assert res.headers["x-ratelimit-remaining"] == str(limit - 1)
