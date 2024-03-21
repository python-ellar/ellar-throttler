import typing as t

from ellar.common import IExecutionContext, Serializer

from ellar_throttler.interfaces import IThrottleModel


class ThrottlerModuleOptions(Serializer):
    throttlers: t.List[IThrottleModel]

    # A string which overrides the default throttler error message
    error_message: t.Optional[str] = None

    # An array of regular expressions of user-agents to ignore when it comes to throttling requests
    ignore_user_agents: t.List[str] = []

    # A factory method to determine if throttling should be skipped.
    # This can be based on the incoming context.
    skip_if: t.Optional[t.Callable[[IExecutionContext], bool]] = None
