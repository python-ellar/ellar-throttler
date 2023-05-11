from ellar.common import Serializer


class ThrottlerStorageRecord(Serializer):
    #  Amount of requests done by a specific user (partially based on IP).
    total_hits: int
    #  Amount of seconds when the `total_hits` should expire.
    time_to_expire: int
