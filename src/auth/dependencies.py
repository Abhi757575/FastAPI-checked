from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission
)
from src.db.main import get_session
from src.db.redis import token_in_blocklist
from .service import UserService
from .utils import decode_token


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self,
        request: Request
    ) -> dict:

        credentials: HTTPAuthorizationCredentials | None = (
            await super().__call__(request)
        )

        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code"
            )

        token = credentials.credentials

        token_data = decode_token(token)

        if not self.token_valid(token_data):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )

        blocked = await token_in_blocklist(token_data["jti"])

        if blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please login again"
                }
            )

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token_data: Any) -> bool:
        return token_data is not None

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError(
            "Please override this method in child classes"
        )


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:

        if token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )


class RefreshTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:

        if not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )


# Create instances
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()


async def get_current_user(
    token_details: dict = Depends(access_token_bearer),
    session: AsyncSession = Depends(get_session)
):

    user_email = token_details["user"]["email"]

    user = await UserService.get_user_by_email(
        user_email,
        session
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


class RoleChecker:

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user=Depends(get_current_user)
    ) -> Any:

        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
        #only here custom error modelling is used, rest need to be updated to use custom errors as well