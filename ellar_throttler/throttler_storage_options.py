from ellar.serializer import Serializer


class ThrottlerStorageOption(Serializer):
    total_hits: int
    expires_at: float
