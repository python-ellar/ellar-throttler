import typing as t

from ellar.common import IExecutionContext, IModuleSetup, Module
from ellar.core.modules import DynamicModule, ModuleBase
from ellar.di import ProviderConfig

from ellar_throttler.interfaces import IThrottlerStorage
from ellar_throttler.throttler_module_options import ThrottlerModuleOptions
from ellar_throttler.throttler_service import ThrottlerStorageService


@Module()
class ThrottlerModule(ModuleBase, IModuleSetup):
    @classmethod
    def setup(
        cls,
        ttl: int,
        limit: int,
        storage: t.Union[t.Type, t.Any, None] = None,
        skip_if: t.Optional[t.Callable[[IExecutionContext], bool]] = None,
    ) -> DynamicModule:
        if storage and isinstance(storage, IThrottlerStorage):
            _provider = ProviderConfig(IThrottlerStorage, use_value=storage)
        elif storage:
            _provider = ProviderConfig(IThrottlerStorage, use_class=storage)
        else:
            _provider = ProviderConfig(
                IThrottlerStorage, use_class=ThrottlerStorageService
            )

        return DynamicModule(
            cls,
            providers=[
                _provider,
                ProviderConfig(
                    ThrottlerModuleOptions,
                    use_value=ThrottlerModuleOptions(
                        limit=limit,
                        ttl=ttl,
                        skip_if=skip_if,
                    ),
                ),
            ],
        )
