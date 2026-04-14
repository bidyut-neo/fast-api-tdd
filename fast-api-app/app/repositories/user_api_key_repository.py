from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user_api_key import UserApiKey
from typing import List, Optional
import secrets

class UserApiKeyRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_api_key(self) -> str:
        return secrets.token_urlsafe(32)

    def create(self, user_id: int, api_key: Optional[str] = None) -> UserApiKey:
        if api_key is None:
            api_key = self.generate_api_key()
        db_key = UserApiKey(user_id=user_id, api_key=api_key)
        self.db.add(db_key)
        self.db.commit()
        self.db.refresh(db_key)
        return db_key

    def get_by_api_key(self, api_key: str) -> Optional[UserApiKey]:
        return self.db.query(UserApiKey).filter(UserApiKey.api_key == api_key).first()

    def get_by_user_id(self, user_id: int) -> List[UserApiKey]:
        return self.db.query(UserApiKey).filter(UserApiKey.user_id == user_id).all()

    def delete_by_api_key(self, api_key: str) -> bool:
        db_key = self.get_by_api_key(api_key)
        if db_key:
            self.db.delete(db_key)
            self.db.commit()
            return True
        return False

    def delete_by_user_id(self, user_id: int) -> int:
        deleted = self.db.query(UserApiKey).filter(UserApiKey.user_id == user_id).delete()
        self.db.commit()
        return deleted

    def exists(self, api_key: str) -> bool:
        return self.db.query(UserApiKey).filter(UserApiKey.api_key == api_key).count() > 0