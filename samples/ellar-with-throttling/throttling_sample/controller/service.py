from ellar.di import injectable


@injectable()
class AppService:
    def success(self, use_auth: bool):
        message = "success"
        if use_auth:
            message += " for Authenticated user"
        return {message: True}

    def ignored(self, use_auth: bool):
        message = "ignored"
        if use_auth:
            message += " for Authenticated user"
        return {message: True}
