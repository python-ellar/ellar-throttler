import typing as t

from ellar.common import IExecutionContext
from ellar.core import HTTPConnection

from .base import BaseThrottler


class UserThrottler(BaseThrottler):
    def __init__(
        self,
        name: str = "user",
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
        return False

    async def get_tracker_identity(self, connection: HTTPConnection) -> str:
        if connection.user and connection.user.is_authenticated:
            ident = connection.user.get("id", connection.user.get("sub"))
            return f"UserIdentifiedAs[{ident}]"
        else:
            return await super().get_tracker_identity(connection)
