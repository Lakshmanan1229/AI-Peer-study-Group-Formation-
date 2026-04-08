from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.groups import router as groups_router
from app.routers.feedback import router as feedback_router
from app.routers.recommendations import router as recommendations_router
from app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "students_router",
    "groups_router",
    "feedback_router",
    "recommendations_router",
    "admin_router",
]
