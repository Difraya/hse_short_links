from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin, InvalidPasswordException
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy, BearerTransport
from fastapi_users.db import SQLAlchemyUserDatabase

from fastapi import Depends, Request
from typing import Optional, Union
import uuid

from models import Users
from schemas.auth import UserCreate
from db import get_user_db
from config import SECRET

# Транспорт — как клиент будет передавать токен
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# JWT-стратегия — как токен создаётся и валидируется
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# Сам backend (JWT)
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Менеджер пользователей
class UserManager(UUIDIDMixin, BaseUserManager[Users, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: Users, request: Optional[Request] = None):
        print(f"User {user.id} зарегистрирован.")

    async def on_after_forgot_password(self, user: Users, token: str, request: Optional[Request] = None):
        print(f"User {user.id} forgot password. Token: {token}")

    async def on_after_request_verify(self, user: Users, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Token: {token}")

    async def validate_password(self, password: str, user: Union[UserCreate, Users]) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(reason="Password must be at least 8 characters")
        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")

# Зависимость
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# Сам fastapi_users
fastapi_users = FastAPIUsers[Users, uuid.UUID](
    get_user_manager,
    [auth_backend],
)