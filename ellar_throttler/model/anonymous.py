import typing as t

from ellar.common import IExecutionContext

from .base import BaseThrottler


class AnonymousThrottler(BaseThrottler):
    def __init__(
        self,
        name: str = "anon",
        *,
        ttl: int,
        limit: int,
        ignore_user_agents: t.Optional[t.List[str]] = None,
        header_prefix: str = "X-RateLimit",
    ):
        super().__init__(
            ttl=ttl,
            limit=limit,
            ignore_user_agents=ignore_user_agents,
            header_prefix=header_prefix,
            name=name,
        )

    def skip_if(self, context: IExecutionContext) -> bool:
        if context.user.is_authenticated:
            return True
        return False
