from ellar.app import AppFactory

from ellar_throttler import ThrottlerGuard

from .module import AppModule

app = AppFactory.create_from_app_module(AppModule, global_guards=[ThrottlerGuard])
