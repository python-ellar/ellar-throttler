from ellar.common import Module
from ellar.core import ModuleBase
from ellar.di import ProviderConfig

from ellar_throttler.interfaces import IThrottlerStorage
from ellar_throttler.throttler_service import CacheThrottlerStorageService


@Module(
    providers=[
        ProviderConfig(IThrottlerStorage, use_class=CacheThrottlerStorageService)
    ]
)
class ThrottlerModule(ModuleBase):
    pass
