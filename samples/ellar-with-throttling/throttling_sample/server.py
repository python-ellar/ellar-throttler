
from ellar.app import AppFactory
from ellar.openapi import OpenAPIDocumentBuilder, OpenAPIDocumentModule, SwaggerUI

from .module import AppModule
from .simple_guard import SimpleGuard


app = AppFactory.create_from_app_module(AppModule, global_guards=[SimpleGuard])

docs = OpenAPIDocumentBuilder().build_document(app)
OpenAPIDocumentModule.setup(app=app, document=docs, docs_ui=[SwaggerUI()])
