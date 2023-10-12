from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from jose import jwt
from pydantic import ValidationError

from app.core.config import configs
from app.core.container import Container
from app.core.exceptions import AuthError
from app.core.security import ALGORITHM, JWTBearer
from app.model.user import User
from app.schema.auth_schema import Payload
from app.services.user_service import UserService


@inject
def get_current_user(
        token: str = Depends(JWTBearer()),
        service: UserService = Depends(Provide[Container.user_service]),
) -> User:
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=ALGORITHM)
        token_data = Payload(**payload)
    except (jwt.JWTError, ValidationError):
        raise AuthError(detail="Could not validate credentials")

    current_user = service.get_by_id(token_data.id)
    if not current_user:
        raise AuthError(detail="Lead not found")

    return current_user
