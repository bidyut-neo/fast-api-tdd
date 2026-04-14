from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from typing import List, Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserCreate, hashed_password: str) -> User:
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        db_user = self.get_by_id(user_id)
        if db_user:
            for key, value in kwargs.items():
                setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        db_user = self.get_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False