from ellar.di import injectable
from ellar.common import GuardCanActivate, IExecutionContext, Identity


@injectable
class SimpleGuard(GuardCanActivate):
    async def can_activate(self, context: IExecutionContext) -> bool:
        if context.switch_to_http_connection().get_client().query_params.get('use_auth') == 'true':
            context.user = Identity(id=2, username='ellar', first_name='python', last_name='framework')
        return True
