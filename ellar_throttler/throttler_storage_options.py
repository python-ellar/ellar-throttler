import dataclasses


@dataclasses.dataclass
class ThrottlerStorageOption:
    total_hits: int
    expires_at: float
