from fastapi import APIRouter

from app.api import scan

api_router = APIRouter()
api_router.include_router(scan.router, tags=["scan"])
