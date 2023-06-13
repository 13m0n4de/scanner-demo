from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_app_config
from app.api import api_router


API_CONFIG = get_app_config()['api']


def create_app() -> FastAPI:
    app = FastAPI(
        version=API_CONFIG['version'],
        title=API_CONFIG['title'],
        description=API_CONFIG['description'],
        docs_url=API_CONFIG['docs_url']
    )
    register_cors(app)
    register_routers(app)
    return app


def register_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )


def register_routers(app: FastAPI) -> None:
    app.include_router(api_router)

