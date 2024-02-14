import hashlib
import typing as t

from ellar.common import GuardCanActivate, IExecutionContext, Response
from ellar.core.connection import HTTPConnection
from ellar.core.services import Reflector
from ellar.di import injectable
from ellar.utils import get_name

from .constants import THROTTLER_LIMIT, THROTTLER_SKIP, THROTTLER_TTL
from .exception import ThrottledException
from .interfaces import IThrottlerStorage
from .throttler_module_options import ThrottlerModuleOptions


@injectable()
class ThrottlerGuard(GuardCanActivate):
    header_prefix = "X-RateLimit"

    def __init__(
        self,
        storage_service: IThrottlerStorage,
        reflector: Reflector,
        options: ThrottlerModuleOptions,
    ) -> None:
        self.storage_service = storage_service
        self.reflector = reflector
        self.options = options

    async def can_activate(self, context: IExecutionContext) -> bool:
        handler = context.get_handler()
        class_ref = context.get_class()

        # Return early if the current route should be skipped.
        # or self.options.skipIf?.(context)

        if self.reflector.get_all_and_override(THROTTLER_SKIP, handler, class_ref) or (
            self.options.skip_if and self.options.skip_if(context)
        ):
            return True

        # Return early when we have no limit or ttl data.
        route_or_class_limit = self.reflector.get_all_and_override(
            THROTTLER_LIMIT, handler, class_ref
        )
        route_or_class_ttl = self.reflector.get_all_and_override(
            THROTTLER_TTL, handler, class_ref
        )

        # Check if specific limits are set at class or route level, otherwise use global options.
        limit = route_or_class_limit or self.options.limit
        ttl = route_or_class_ttl or self.options.ttl
        return await self.handle_request(context, limit, ttl)

    @classmethod
    def get_request_response(
        cls, context: IExecutionContext
    ) -> t.Tuple[HTTPConnection, Response]:
        connection_host = context.switch_to_http_connection()
        return connection_host.get_client(), connection_host.get_response()

    def get_tracker(self, connection: HTTPConnection) -> str:
        if connection.client:
            return connection.client.host

        return t.cast(str, connection.scope["server"][0])

    def generate_key(self, context: IExecutionContext, suffix: str) -> str:
        prefix = f"{get_name(context.get_class())}-{get_name(context.get_handler())}"
        return hashlib.md5(f"{prefix}-{suffix}".encode("utf8")).hexdigest()

    async def handle_request(
        self, context: IExecutionContext, limit: int, ttl: int
    ) -> bool:
        connection, response = self.get_request_response(context)

        tracker = self.get_tracker(connection)
        key = self.generate_key(context, tracker)
        result = await self.storage_service.increment(key, ttl)

        # Throw an error when the user reached their limit.
        if result.total_hits > limit:
            raise ThrottledException(wait=result.time_to_expire)

        response.headers[f"{self.header_prefix}-Limit"] = str(limit)
        response.headers[f"{self.header_prefix}-Remaining"] = str(
            max(0, limit - result.total_hits)
        )
        response.headers[f"{self.header_prefix}-Reset"] = str(result.time_to_expire)

        return True
