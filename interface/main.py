from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import routers as v1_routers
from infrastructure.config import configs
from infrastructure.container import Container


class AppCreator:
    _instance = None

    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url=f"{configs.API}/openapi.json",
            version="0.0.1",
        )

        # set db and container
        self.container = Container()
        self.db = self.container.db()
        # self.db.create_database()

        # set cors
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # set routes
        @self.app.get("/")
        def root():
            return "Service is working"

        self.app.include_router(v1_routers, prefix=configs.PREFIX)
        add_pagination(self.app)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppCreator, cls).__new__(cls)
        return cls._instance


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container
