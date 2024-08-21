import typing as t

from ellar.common import EllarInterceptor, IExecutionContext
from ellar.core.services import Reflector
from ellar.di import injectable

from .constants import INLINE_THROTTLERS, THROTTLER_LIMIT, THROTTLER_SKIP, THROTTLER_TTL
from .interfaces import IThrottlerStorage
from .throttler_module_options import ThrottlerModuleOptions


@injectable()
class ThrottlerInterceptor(EllarInterceptor):
    def __init__(
        self,
        storage_service: IThrottlerStorage,
        reflector: Reflector,
        options: ThrottlerModuleOptions,
    ) -> None:
        self.storage_service = storage_service
        self.reflector = reflector
        self.options = options

    async def intercept(
        self, context: IExecutionContext, next_interceptor: t.Callable[..., t.Coroutine]
    ) -> t.Any:
        handler = context.get_handler()
        class_ref = context.get_class()

        connection = context.switch_to_http_connection().get_client()
        user_agent = connection.headers.get("User-Agent")

        if await self.should_skip(context):
            return await next_interceptor()

        # Return early if the current route should be skipped.
        if self.reflector.get_all_and_override(THROTTLER_SKIP, handler, class_ref):
            return await next_interceptor()

        inline_throttlers = (
            self.reflector.get_all_and_override(INLINE_THROTTLERS, handler, class_ref)
            or []
        )
        throttlers = inline_throttlers or self.options.throttlers

        for throttler in throttlers:
            # Continue if throttler was skipped
            skip_route_throttle = self.reflector.get_all_and_override(
                f"{THROTTLER_SKIP}-{throttler.name}", handler, class_ref
            )
            if skip_route_throttle:
                continue

            # Continue if a throttler model says skip otherwise
            if throttler.skip_if(context):
                continue

            # Check if throttler should ignore user agent
            _ignore_user_agents = (
                self.options.ignore_user_agents or throttler.ignore_user_agents
            )
            if user_agent in _ignore_user_agents:
                continue

            # Return early when we have no limit or ttl data.
            route_or_class_limit = self.reflector.get_all_and_override(
                f"{THROTTLER_LIMIT}-{throttler.name}", handler, class_ref
            )
            route_or_class_ttl = self.reflector.get_all_and_override(
                f"{THROTTLER_TTL}-{throttler.name}", handler, class_ref
            )

            # Check if specific limits are set at class or route level, otherwise use global options.
            limit = route_or_class_limit or throttler.limit
            ttl = route_or_class_ttl or throttler.ttl

            await throttler.allow_request(
                context,
                storage_service=self.storage_service,
                limit=limit,
                ttl=ttl,
                error_message=self.options.error_message,
            )

        return await next_interceptor()

    async def should_skip(self, context: IExecutionContext) -> bool:
        if self.options.skip_if:
            return self.options.skip_if(context)
        return False
