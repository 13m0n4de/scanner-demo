from fastapi import APIRouter

from app.api import scans

api_router = APIRouter()
api_router.include_router(scans.router, tags=["scans"])
