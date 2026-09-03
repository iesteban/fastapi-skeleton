from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import User


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService:
    @staticmethod
    def create_user(db: Session, username: str, email: str) -> User:
        # Business rule: usernames must not collide (case-insensitive)
        if db.query(User).filter(func.lower(User.username) == username.lower()).first():
            raise UserAlreadyExistsError(f"Username '{username}' is already taken.")

        if db.query(User).filter(func.lower(User.email) == email.lower()).first():
            raise UserAlreadyExistsError(f"Email '{email}' is already registered.")

        user = User(username=username, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found.")
        return user
