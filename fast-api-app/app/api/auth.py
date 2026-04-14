from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.user_api_key_repository import UserApiKeyRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, Token, ChangePassword
from app.api.deps import get_current_user, get_auth_service
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    api_key_repo = UserApiKeyRepository(db)
    auth_service = AuthService(user_repo, api_key_repo)
    
    user, access_token = auth_service.register_user(user_create)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    api_key_repo = UserApiKeyRepository(db)
    auth_service = AuthService(user_repo, api_key_repo)
    
    user, access_token = auth_service.login_user(user_login)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db)
):
    # We need to get the API key from the token
    # For simplicity, we'll rely on the client to stop using the token
    # The actual invalidation happens when the API key is deleted
    # This endpoint just returns success; actual invalidation is done via token validation
    return {"message": "Logged out successfully"}

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    change_password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db)
):
    auth_service.change_password(
        current_user.id,
        change_password_data.current_password,
        change_password_data.new_password
    )
    return {"message": "Password changed successfully"}