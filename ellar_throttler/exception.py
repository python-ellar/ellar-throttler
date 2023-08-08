import math
import typing as t

from ellar.common import APIException
from starlette import status


class ThrottledException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Request was throttled."
    extra_detail_singular = "Expected available in {wait} second."
    extra_detail_plural = "Expected available in {wait} seconds."

    def __init__(
        self, wait: t.Optional[float] = None, detail: t.Optional[t.Any] = None
    ) -> None:
        if detail is None:
            detail = self.default_detail
        if wait is not None:
            wait = math.ceil(wait)
            detail = " ".join(
                (
                    detail,
                    self.extra_detail_singular.format(wait=wait)
                    if wait < 1
                    else self.extra_detail_plural.format(wait=wait),
                )
            )
        headers = {"Retry-After": "%d" % float(wait or 0.0)}
        super().__init__(detail=detail, headers=headers)
