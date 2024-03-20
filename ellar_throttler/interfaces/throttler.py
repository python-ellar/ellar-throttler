import typing as t
from abc import abstractmethod

from ellar.common import IExecutionContext
from ellar.core import HTTPConnection
from ellar.pydantic import as_pydantic_validator

from .throttler_storage import IThrottlerStorage


@as_pydantic_validator("__validate_throttler_type__", schema={"type": "object"})
class IThrottleModel:
    @classmethod
    def __validate_throttler_type__(
        cls, __input_value: t.Any, _: t.Any
    ) -> "IThrottleModel":
        if not isinstance(__input_value, cls):  # pragma: no cover
            raise ValueError(f"Invalid type. Expected type {cls} got {__input_value}")

        return __input_value

    @property
    @abstractmethod
    def limit(self) -> int:
        """The amount of requests that are allowed within the ttl's time window."""

    @property
    @abstractmethod
    def ttl(self) -> int:
        """The amount of seconds of how many requests are allowed within this time."""

    @property
    @abstractmethod
    def name(self) -> str:
        """the name for internal tracking of which throttler set is being used"""

    @property
    @abstractmethod
    def ignore_user_agents(self) -> t.List[str]:
        """An array of regular expressions of user-agents to ignore when it comes to throttling requests"""

    @abstractmethod
    def skip_if(self, context: IExecutionContext) -> bool:
        """
        A factory method to determine if throttling should be skipped.
        This can be based on the incoming context.
        :param context: IExecutionContext
        :return: Boolean
        """

    @abstractmethod
    async def get_tracker_identity(self, connection: HTTPConnection) -> str:
        """
        A factory method to determine if throttling should be skipped.
        This can be based on the incoming context.
        :param connection: HTTPConnection
        :return: String
        """

    @abstractmethod
    def make_key(self, context: IExecutionContext, suffix: str) -> str:
        """
        A function that takes in the IExecutionContext, the tracker string and the throttler name as a string and
        returns a string to override the final key which will be used to store the rate limit value.
        This overrides the default logic of the make_key_function method.
        :param context: IExecutionContext
        :param suffix: String
        :return:
        """

    @abstractmethod
    async def allow_request(
        self,
        context: IExecutionContext,
        *,
        storage_service: IThrottlerStorage,
        ttl: int,
        limit: int,
        error_message: t.Optional[str] = None,
    ) -> bool:
        """
        Checks if request should be throttled.
        :param context: IExecutionContext
        :param storage_service: Storage Service Instance
        :param ttl: amount of seconds of how many requests are allowed within this time.
        :param limit: The Number of requests that are allowed within the ttl's time window
        :param error_message: An array of regular expressions of user agents to ignore when it comes to throttling requests
        :return:
        """
