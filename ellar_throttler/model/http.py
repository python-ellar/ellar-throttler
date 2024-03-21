from ellar.common import IExecutionContext

from .base import BaseThrottler


class HTTPThrottler(BaseThrottler):
    def skip_if(self, context: IExecutionContext) -> bool:
        # Check if a request type is http
        scope, _, _ = context.get_args()
        if scope["type"] != "http":  # pragma: no cover
            return True

        return False
