from app.schemas import UserProfile


class UserService:
    @staticmethod
    def get_current_user() -> UserProfile:
        return UserProfile(
            user_id='anonymous',
            email='anonymous@localhost',
            full_name='Anonymous User',
            persona='developer',
            subscription_plan='free',
            created_at='2026-01-01T00:00:00Z',
        )
