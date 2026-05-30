from fastapi import APIRouter
from app.schemas import UserProfile
from app.services.user_service import UserService

router = APIRouter(prefix='/api/users', tags=['users'])

@router.get('/me', response_model=UserProfile, summary='Get current user profile')
def get_current_user() -> UserProfile:
    return UserService.get_current_user()
