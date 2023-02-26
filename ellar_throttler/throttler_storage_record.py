import dataclasses


@dataclasses.dataclass
class ThrottlerStorageRecord:
    #  Amount of requests done by a specific user (partially based on IP).
    total_hits: int
    #  Amount of seconds when the `total_hits` should expire.
    time_to_expire: int
