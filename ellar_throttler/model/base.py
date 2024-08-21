import hashlib
import typing as t
from abc import ABC

from ellar.common import IExecutionContext
from ellar.core import HTTPConnection
from ellar.utils import get_name
from starlette.responses import Response

from ellar_throttler.exception import ThrottledException
from ellar_throttler.interfaces import IThrottleModel, IThrottlerStorage


class BaseThrottler(IThrottleModel, ABC):
    __slots__ = (
        "_name",
        "_ttl",
        "_limit",
        "_ignore_user_agents",
        "header_prefix",
    )

    def __init__(
        self,
        name: str,
        *,
        ttl: int,
        limit: int,
        ignore_user_agents: t.Optional[t.List[str]] = None,
        header_prefix: str = "X-RateLimit",
    ) -> None:
        self._name = name
        self._ttl = ttl
        self._limit = limit
        self._ignore_user_agents = ignore_user_agents or []
        self.header_prefix = header_prefix

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def ttl(self) -> int:
        return self._ttl

    @property
    def name(self) -> str:
        return self._name

    @property
    def ignore_user_agents(self) -> t.List[str]:
        return self._ignore_user_agents

    async def get_tracker_identity(self, connection: HTTPConnection) -> str:
        if connection.client:  # pragma: no cover
            return connection.client.host

        return t.cast(str, connection.scope["server"][0])

    def make_key(self, context: IExecutionContext, suffix: str) -> str:
        prefix = f"{get_name(context.get_class())}-{get_name(context.get_handler())}-{self.name}"
        return hashlib.md5(f"{prefix}-{suffix}".encode("utf8")).hexdigest()

    @classmethod
    def get_request_response(
        cls, context: IExecutionContext
    ) -> t.Tuple[HTTPConnection, t.Optional[Response]]:
        connection_host = context.switch_to_http_connection()
        return connection_host.get_client(), connection_host.get_response()

    async def allow_request(
        self,
        context: IExecutionContext,
        *,
        storage_service: IThrottlerStorage,
        ttl: int,
        limit: int,
        error_message: t.Optional[str] = None,
    ) -> bool:
        connection, response = self.get_request_response(context)

        tracker = await self.get_tracker_identity(connection)

        key = self.make_key(context, tracker)
        result = await storage_service.increment(key, ttl)

        # Throw an error when the user reached their limit.
        if result.total_hits > limit:
            # Format error message if it has `{wait}` tag
            error_message_ = (
                str(error_message).format(wait=result.time_to_expire)
                if error_message
                else error_message
            )

            raise ThrottledException(
                self.name, wait=result.time_to_expire, detail=error_message_
            )

        if response:
            response.headers[f"{self.header_prefix}-Limit-{self.name}"] = str(limit)
            response.headers[f"{self.header_prefix}-Remaining-{self.name}"] = str(
                max(0, limit - result.total_hits)
            )
            response.headers[f"{self.header_prefix}-Reset-{self.name}"] = str(
                result.time_to_expire
            )

        return True

    def __str__(self) -> str:
        def _format_rate(seconds: int) -> str:
            if 1 <= seconds < 60:
                return f"{seconds % 1}day(s)"
            elif 60 <= seconds < 3600:
                return f"{seconds % 60}min(s)"
            elif 3600 <= seconds < 86400:
                return f"{seconds % 3600}hour(s)"
            else:
                return f"{seconds % 86400}day(s)"

        return f"<{self.__class__.__name__} name={self.name} rate={self.limit}/{_format_rate(self.ttl)} ignoreAgents={self.ignore_user_agents}>"
