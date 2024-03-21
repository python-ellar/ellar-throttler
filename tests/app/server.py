from ellar.app import AppFactory

from ellar_throttler import ThrottlerInterceptor

from .module import AppModule
from .simple_guard import SimpleGuard

app = AppFactory.create_from_app_module(AppModule, global_guards=[SimpleGuard])
app.use_global_interceptors(ThrottlerInterceptor)
