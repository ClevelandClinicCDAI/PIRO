from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLoginVM(BaseModel):
    username: str
    password: str
    islog: bool


class OAuthLoginVM(BaseModel):
    """Request body for /token when AUTH_MODE=OAUTH.

    The client (SPA) completes authorization-code + PKCE against the IdP
    on its own, then posts the resulting id_token here so the API can
    verify it and mint a PIRO session JWT.
    """

    id_token: str
    islog: bool


class LogoutResponseVM(BaseModel):
    """Response body for POST /logout.

    ``end_session_url`` is populated with the IdP's RP-initiated logout
    endpoint when running under AUTH_MODE=OAUTH; the SPA can optionally
    redirect the browser there to end the shared IdP session (SLO).
    Under AUTH_MODE=LDAP the field is ``None`` and the client is
    expected to discard its PIRO JWT locally.
    """

    end_session_url: Optional[str]
