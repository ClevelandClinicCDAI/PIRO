from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.email import Email
from core.security_user import get_current_user_nuid
from db.repository.user import list_user_active
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException
from logger import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter()

_ADMIN_ROLES = [Constants.RoleAdmin, Constants.RoleDemoAdmin]


class EmailUsersPayload(BaseModel):
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1, max_length=100)


@router.post(
    "/send",
    dependencies=[Depends(JWTBearer(_ADMIN_ROLES))],
)
async def send_email_to_all_users(
    payload: EmailUsersPayload,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    users = list_user_active(db=db)
    if not users:
        raise HTTPException(status_code=400, detail="No active users found.")

    domain = payload.domain.lstrip("@")
    recipients = ",".join(f"{u.NUID}@{domain}" for u in users)

    html_body = payload.body.replace("\n", "<br>")
    html_body = f"<html><body>{html_body}</body></html>"

    try:
        email = Email(subject=payload.subject, html_body=html_body)
        email.send(to=recipients, cc=None, bcc=None)
    except Exception as exc:
        logger.error("Email Users send failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to send emails.")

    return {"status": True, "recipientCount": len(users)}
