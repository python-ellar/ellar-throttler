import typing as t

from ellar.common import IExecutionContext, Serializer


class ThrottlerModuleOptions(Serializer):
    # The amount of requests that are allowed within the ttl's time window.
    limit: int

    #  The amount of seconds of how many requests are allowed within this time.
    ttl: int

    # A factory method to determine if throttling should be skipped.
    # This can be based on the incoming context.
    skip_if: t.Optional[t.Callable[[IExecutionContext], bool]] = None
