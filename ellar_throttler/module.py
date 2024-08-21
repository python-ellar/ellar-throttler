import functools
import typing as t

from ellar.cache import CacheModule
from ellar.common import IExecutionContext, IModuleSetup, Module
from ellar.common.exceptions import ImproperConfiguration
from ellar.core import Config, ModuleSetup
from ellar.core.modules import DynamicModule, ModuleBase, ModuleRefBase
from ellar.di import ProviderConfig

from ellar_throttler.interfaces import IThrottleModel, IThrottlerStorage
from ellar_throttler.throttler_module_options import ThrottlerModuleOptions
from ellar_throttler.throttler_service import (
    CacheThrottlerStorageService,
    ThrottlerStorageService,
)


class _Config(t.TypedDict):
    throttlers: t.Optional[t.List[IThrottleModel]]
    storage: t.Union[t.Type, t.Type[IThrottlerStorage], t.Any, None]
    error_message: t.Optional[str]
    ignore_user_agents: t.Optional[t.List[str]]
    skip_if: t.Optional[t.Callable[[IExecutionContext], bool]]


@Module(name="ThrottlerModule", exports=[IThrottlerStorage, ThrottlerModuleOptions])
class ThrottlerModule(ModuleBase, IModuleSetup):
    @classmethod
    def post_build(cls, module_ref: "ModuleRefBase") -> None:
        storage = module_ref.providers.get(IThrottlerStorage)
        if storage.use_class and (  # type:ignore[union-attr]
            storage.use_class == CacheThrottlerStorageService  # type:ignore[union-attr]
            or issubclass(storage.use_class, CacheThrottlerStorageService)  # type:ignore[union-attr]
        ):
            try:
                module_ref.tree_manager.add_module_dependency(cls, CacheModule)
            except ValueError:
                raise ImproperConfiguration(
                    f"Using {CacheThrottlerStorageService} as storage type requires {CacheModule} setup. "
                    f"See https://python-ellar.github.io/ellar/security/rate-limit/"
                ) from None

    @classmethod
    def setup(
        cls,
        throttlers: t.Optional[t.List[IThrottleModel]] = None,
        storage: t.Union[t.Type, t.Type[IThrottlerStorage], t.Any, None] = None,
        error_message: t.Optional[str] = None,
        ignore_user_agents: t.Optional[t.List[str]] = None,
        skip_if: t.Optional[t.Callable[[IExecutionContext], bool]] = None,
    ) -> DynamicModule:
        """
        Sets up ThrottlingModule
        :param throttlers: List of Throttling Models
        :param storage: Throttling Caching Service. Default: ThrottlerStorageService
        :param error_message: a string which overrides the default throttler error message
        :param ignore_user_agents: an array of regular expressions of user-agents to ignore when it comes to throttling requests
        :param skip_if: A factory method to determine if throttling should be skipped before running any throttler model.
        :return: DynamicModule
        """

        return cls.__setup_module(
            options=ThrottlerModuleOptions(
                throttlers=throttlers or [],
                error_message=error_message,
                ignore_user_agents=ignore_user_agents or [],
                skip_if=skip_if,
            ),
            storage=storage,
        )

    @classmethod
    def register_setup(cls, **override_config: t.Any) -> ModuleSetup:
        """
        Register Module to be configured through `ELLAR_THROTTLER_CONFIG` variable in Application Config
        """
        return ModuleSetup(
            cls,
            inject=[Config],
            factory=functools.partial(
                cls.__register_setup_factory,
                override_config=override_config,
            ),
        )

    @staticmethod
    def __register_setup_factory(
        module_ref: ModuleRefBase,
        config: Config,
        override_config: t.Dict[str, t.Any],
    ) -> DynamicModule:
        if config.get("ELLAR_THROTTLER_CONFIG") and isinstance(
            config.ELLAR_THROTTLER_CONFIG, dict
        ):
            defined_config = dict(config.ELLAR_THROTTLER_CONFIG)
            defined_config.update(override_config)

            storage = defined_config.pop("storage")

            schema = ThrottlerModuleOptions.model_validate(
                defined_config, from_attributes=True
            )
            module = t.cast(t.Type[ThrottlerModule], module_ref.module)
            return module.__setup_module(schema, storage)
        raise RuntimeError(
            "Could not find `ELLAR_THROTTLER_CONFIG` in application config."
        )

    @classmethod
    def __setup_module(
        cls,
        options: ThrottlerModuleOptions,
        storage: t.Union[t.Type, t.Type[IThrottlerStorage], t.Any, None] = None,
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
                    use_value=options,
                ),
            ],
        )
