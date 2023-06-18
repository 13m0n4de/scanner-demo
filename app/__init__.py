from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

from dramatiq_dashboard import DashboardApp

from app.config import CONFIG
from app.api import api_router
from app.actors import broker

API_CONFIG = CONFIG["api"]
DASHBOARD_CONFIG = CONFIG["dashboard"]


def create_app() -> FastAPI:
    app = FastAPI(
        version=API_CONFIG["version"],
        title=API_CONFIG["title"],
        description=API_CONFIG["description"],
        docs_url=API_CONFIG["docs_url"],
    )
    register_cors(app)
    register_routers(app)

    dashboard = DashboardApp(broker=broker, prefix=DASHBOARD_CONFIG["url"])
    app.mount(DASHBOARD_CONFIG["url"], WSGIMiddleware(dashboard))

    return app


def register_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI) -> None:
    app.include_router(api_router)
