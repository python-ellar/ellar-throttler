<p align="center">
  <a href="#" target="blank"><img src="https://python-ellar.github.io/ellar/img/EllarLogoB.png" width="200" alt="Ellar Logo" /></a>
</p>

<p align="center">Ellar - Python ASGI web framework for building fast, efficient, and scalable RESTful APIs and server-side applications.</p>

![Test](https://github.com/python-ellar/ellar-throttler/actions/workflows/test_full.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/python-ellar/ellar-throttler)
[![PyPI version](https://badge.fury.io/py/ellar-throttler.svg)](https://badge.fury.io/py/ellar-throttler)
[![PyPI version](https://img.shields.io/pypi/v/ellar-throttler.svg)](https://pypi.python.org/pypi/ellar-throttler)
[![PyPI version](https://img.shields.io/pypi/pyversions/ellar-throttler.svg)](https://pypi.python.org/pypi/ellar-throttler)

## Introduction
A rate limit module for Ellar

## Installation
```shell
$(venv) pip install ellar-throttler
```

## Configure ThrottlerModule
We need to set up the `ThrottlerModule` to be able for configuring throttling mechanisms for the entire application.

```python
from ellar.common import Module
from ellar_throttler import AnonymousThrottler, ThrottlerModule, UserThrottler


@Module(
    modules=(
        ThrottlerModule.setup(
            throttlers=[
                AnonymousThrottler(limit=100, ttl=60*5), # 100 requests per 5mins
                UserThrottler(limit=1000, ttl=60*60*24) # 1000 requests per day
            ]
        ),
    )
)
class AppModule:
    pass
```

## Applying Throttling to Controllers

```python
from ellar.common import Controller, get
from ellar_throttler import Throttle, AnonymousThrottler, UserThrottler
from ellar.di import injectable


@injectable()
class AppService:
    def success(self, use_auth: bool):
        message = "success"
        if use_auth:
            message += " for Authenticated user"
        return {message: True}

    def ignored(self, use_auth: bool):
        message = "ignored"
        if use_auth:
            message += " for Authenticated user"
        return {message: True}


@Throttle(intercept=True)
@Controller("/limit")
class LimitController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @get()
    def get_throttled(self, use_auth: bool):
        return self.app_service.success(use_auth)

    @get("/shorter")
    @Throttle(anon={"limit": 3, "ttl": 5}, user={"limit": 3, "ttl": 3}) # overriding anon and user throttler config
    def get_shorter(self, use_auth: bool):
        return self.app_service.success(use_auth)

    @get("/shorter-inline-throttling")
    @Throttle(AnonymousThrottler(ttl=5, limit=3), UserThrottler(ttl=3, limit=3)) # overriding global throttling options
    def get_shorter_inline_version(self, use_auth: bool):
        return self.app_service.success(use_auth)
```

## References
- [Documentation](https://python-ellar.github.io/ellar/techniques/rate-limit)

## License
Ellar is [MIT licensed](LICENSE).
