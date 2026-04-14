import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.user_api_key_repository import UserApiKeyRepository
from app.schemas.user import UserCreate, UserLogin, Token, TokenData

class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        api_key_repository: UserApiKeyRepository
    ):
        self.user_repository = user_repository
        self.api_key_repository = api_key_repository
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "5"))

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, user_id: int, api_key: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "api_key": api_key,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret_key, algorithm=self.jwt_algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
            user_id = int(payload.get("sub"))
            api_key = payload.get("api_key")
            if user_id is None or api_key is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return TokenData(user_id=user_id, api_key=api_key)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def authenticate_user(self, username: str, password: str):
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def register_user(self, user_create: UserCreate) -> tuple:
        # Check if username exists
        existing = self.user_repository.get_by_username(user_create.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = self.hash_password(user_create.password)
        user = self.user_repository.create(user_create, hashed_password)
        
        # Generate API key for this user
        api_key = self.api_key_repository.create(user.id)
        
        # Create JWT token
        access_token = self.create_access_token(user.id, api_key.api_key)
        
        return user, access_token

    def login_user(self, user_login: UserLogin) -> tuple:
        user = self.authenticate_user(user_login.username, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Delete existing API keys for this user (single session)
        self.api_key_repository.delete_by_user_id(user.id)
        
        # Generate new API key
        api_key = self.api_key_repository.create(user.id)
        
        # Create JWT token
        access_token = self.create_access_token(user.id, api_key.api_key)
        
        return user, access_token

    def logout_user(self, api_key: str) -> bool:
        return self.api_key_repository.delete_by_api_key(api_key)

    def validate_token_and_get_user(self, token: str):
        token_data = self.decode_token(token)
        
        # Check if API key still exists
        if not self.api_key_repository.exists(token_data.api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalidated (logged out)"
            )
        
        user = self.user_repository.get_by_id(token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not self.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        new_hashed = self.hash_password(new_password)
        self.user_repository.update(user_id, hashed_password=new_hashed)
        
        # Invalidate all existing API keys (force logout from all devices)
        self.api_key_repository.delete_by_user_id(user_id)
        
        return True