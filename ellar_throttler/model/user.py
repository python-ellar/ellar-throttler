import typing as t

from ellar.core import HTTPConnection

from .http import HTTPThrottler


class UserThrottler(HTTPThrottler):
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

    async def get_tracker_identity(self, connection: HTTPConnection) -> str:
        if connection.user and connection.user.is_authenticated:
            ident = connection.user.get("id", connection.user.get("sub"))
            return f"UserIdentifiedAs[{ident}]"
        else:
            return await super().get_tracker_identity(connection)
