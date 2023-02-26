import typing as t
from abc import ABC, abstractmethod

from ..throttler_storage_options import ThrottlerStorageOption
from ..throttler_storage_record import ThrottlerStorageRecord


class IThrottlerStorage(ABC):
    @property
    @abstractmethod
    def storage(self) -> t.Dict[str, ThrottlerStorageOption]:
        """
        The internal storage with all the request records.
        The key is a hashed key based on the current context and IP.
        :return:
        """

    @abstractmethod
    async def increment(self, key: str, ttl: int) -> ThrottlerStorageRecord:
        """
        Increment the amount of requests for a given record. The record will
        automatically be removed from the storage once its TTL has been reached.
        :param key:
        :param ttl:
        :return:
        """
