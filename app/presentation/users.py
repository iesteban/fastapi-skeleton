from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session
import re

from ..business import UserService
from ..business.users import UserAlreadyExistsError, UserNotFoundError
from ..database import get_db

users_router = APIRouter()


# Presentation-layer validation: field types, formats, and lengths
class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    display_name: str | None = None

    @field_validator("username", mode="after")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username must be alphanumeric with underscores only.")
        return value



class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


@users_router.post("/", response_model=UserResponse, status_code=201)
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, username=payload.username, email=payload.email)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return user


@users_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = UserService.get_user(db, user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return user
