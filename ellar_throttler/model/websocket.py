import typing as t

from ellar.common import IExecutionContext
from ellar.core import HTTPConnection
from starlette.responses import Response

from .base import BaseThrottler


class WebsocketThrottler(BaseThrottler):
    @classmethod
    def get_request_response(
        cls, context: IExecutionContext
    ) -> t.Tuple[HTTPConnection, t.Optional[Response]]:
        connection_host = context.switch_to_http_connection()
        return connection_host.get_client(), None

    def skip_if(self, context: IExecutionContext) -> bool:
        # Check if a request type is websocket
        scope, _, _ = context.get_args()
        if scope["type"] != "websocket":  # pragma: no cover
            return True

        return False

    async def get_tracker_identity(self, connection: HTTPConnection) -> str:
        if connection.user and connection.user.is_authenticated:
            ident = connection.user.get("id", connection.user.get("sub"))
            return f"WebsocketUserIdentifiedAs[{ident}]"
        else:
            return await super().get_tracker_identity(connection)
