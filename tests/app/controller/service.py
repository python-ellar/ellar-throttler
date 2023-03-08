from ellar.di import injectable


@injectable()
class AppService:
    def success(self):
        return {"success": True}

    def ignored(self):
        return {"ignored": True}
