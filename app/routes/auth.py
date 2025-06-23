from fastapi import APIRouter
from appwrite.exception import AppwriteException
from app.game.models.pydantic import (
    SuccessResponse,
)

router = APIRouter(tags=["auth"])

