from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from typing import List, Optional
from fastapi import HTTPException, status

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user: UserCreate, hashed_password: str) -> UserResponse:
        # Check if username already exists
        existing_user = self.repository.get_by_username(user.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username {user.username} already exists"
            )
        
        db_user = self.repository.create(user, hashed_password)
        return UserResponse.from_orm(db_user)

    def get_user(self, user_id: int) -> UserResponse:
        db_user = self.repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return UserResponse.from_orm(db_user)

    def get_user_by_username(self, username: str):
        return self.repository.get_by_username(username)

    def get_all_users(self) -> List[UserResponse]:
        db_users = self.repository.get_all()
        return [UserResponse.from_orm(user) for user in db_users]

    def update_user(self, user_id: int, **kwargs) -> UserResponse:
        db_user = self.repository.update(user_id, **kwargs)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return UserResponse.from_orm(db_user)

    def delete_user(self, user_id: int) -> None:
        success = self.repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )