from fastapi import APIRouter
from app.api.routes.match import router as match_router
from app.api.routes.crowd import router as crowd_router
from app.api.routes.incidents import router as incident_router
from app.api.routes.operations import router as ops_router
from app.api.routes.assistant import router as assistant_router
from app.api.routes.accessibility import router as accessibility_router

api_router = APIRouter(prefix="/api")

api_router.include_router(match_router)
api_router.include_router(crowd_router)
api_router.include_router(incident_router)
api_router.include_router(ops_router)
api_router.include_router(assistant_router)
api_router.include_router(accessibility_router)
