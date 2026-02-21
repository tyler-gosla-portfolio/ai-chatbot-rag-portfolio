from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as docs_router
from app.api.v1.chats import router as chats_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(docs_router)
router.include_router(chats_router)
