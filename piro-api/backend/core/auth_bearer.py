from core.security_token import decode_access_token
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from logger import logger


class JWTBearer(HTTPBearer):
    def __init__(self, roles: str | None = None, auto_error: bool = False):
        if roles is None:
            roles = []
        self.allowed_roles = roles
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request
        )
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if len(self.allowed_roles) == 0:
                if not self.verify_jwt(credentials.credentials):
                    raise HTTPException(
                        status_code=403,
                        detail="Invalid token or expired token.",
                    )
            else:
                if not self.verify_jwt_role(credentials.credentials):
                    raise HTTPException(
                        status_code=403, detail="Access denied."
                    )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code."
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        try:
            payload = decode_access_token(jwtoken)
        except Exception as e:
            logger.error(
                f"Please see log for error messaging: " f"{type(e), e, e.args}"
            )
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid

    def verify_jwt_role(self, jwtoken: str) -> bool:
        try:
            payload = decode_access_token(jwtoken)
            if payload:
                for role in self.allowed_roles:
                    logger.info(f"payload from JWT token is " f"{payload}")
                    logger.info(self.allowed_roles)
                    if role == str(payload["role"].upper()):
                        return True
                return False
            else:
                return False
        except Exception as e:
            logger.error(
                f"Please see log for error messaging: " f"{type(e), e, e.args}"
            )
            return False
