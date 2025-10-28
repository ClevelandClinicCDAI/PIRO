import json
import hmac
import hashlib
from fastapi import HTTPException
from db.session import get_db
from fastapi import Request, APIRouter, Depends, status
from pytest import Session
from viewmodel.views.case import ResultVM
from logger import logger
from core.config import Settings


router = APIRouter()


@router.post("/create", dependencies=[], response_model=ResultVM)
async def concentriq_create(
    request: Request,
    db: Session = Depends(get_db),
):
    timestamp = request.headers.get("webhook-timestamp")
    received_signature = request.headers.get("webhook-signature")

    if not timestamp or not received_signature:
        logger.error(
            "Conentriq create error - concentriq_create 400 Internal Server Error "
            "Missing signature headers."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature headers.",
        )

    if not Settings.CONCENTRIQ_WEBHOOK_SECRET:
        logger.error(
            "Conentriq create error - concentriq_create 501 Internal Server Error "
            "CONCENTRIQ_WEBHOOK_SECRET not set."
        )
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="CONCENTRIQ_WEBHOOK_SECRET not set.",
        )

    payload = await request.json()
    logger.info(f"concentriq_create, payload from Concentriq is " f"{payload}")
    computed_signature = get_signature(
        timestamp, payload, Settings.CONCENTRIQ_WEBHOOK_SECRET
    )
    logger.info(f"received_signature " f"{received_signature}")
    logger.info(f"computed_signature " f"{computed_signature}")
    if received_signature != computed_signature:
        logger.error(
            "Conentriq create error - concentriq_create 401 Internal Server Error "
            "Invalid webhook token."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token.",
        )
    try:
        logger.info(
            f"concentriq_create, payload from Concentriq is " f"{payload}"
        )
    except Exception as exc:
        logger.error(
            f"Concentriq create error - concentriq_create 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return True


def get_signature(timestamp, body, signing_secret):
    """Generate HMAC SHA256 signature for the webhook payload."""
    data_string = json.dumps(
        body, separators=(",", ":")
    )  # Compact JSON, similar to JS JSON.stringify
    payload = f"{timestamp}.{data_string}"
    signature = hmac.new(
        signing_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return signature


@router.post("/delete", dependencies=[], response_model=ResultVM)
async def concentriq_delete(
    request: Request,
    db: Session = Depends(get_db),
):
    timestamp = request.headers.get("webhook-timestamp")
    received_signature = request.headers.get("webhook-signature")

    if not timestamp or not received_signature:
        logger.error(
            "Conentriq create error - concentriq_delete 400 Internal Server Error "
            "Missing signature headers."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature headers.",
        )
    payload = await request.json()
    logger.info(f"concentriq_delete, payload from Concentriq is " f"{payload}")
    computed_signature = get_signature(
        timestamp, payload, Settings.CONCENTRIQ_WEBHOOK_SECRET
    )
    if received_signature != computed_signature:
        logger.error(
            "Conentriq create error - concentriq_delete 401 Internal Server Error "
            "Invalid webhook token."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token.",
        )
    try:
        logger.info(
            f"concentriq_delete, payload from Concentriq is " f"{payload}"
        )
    except Exception as exc:
        logger.error(
            f"Conentriq create error - concentriq_delete 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return True


@router.post("/update", dependencies=[], response_model=ResultVM)
async def concentriq_update(
    request: Request,
    db: Session = Depends(get_db),
):
    timestamp = request.headers.get("webhook-timestamp")
    received_signature = request.headers.get("webhook-signature")

    if not timestamp or not received_signature:
        logger.error(
            "Conentriq create error - concentriq_update 400 Internal Server Error "
            "Missing signature headers."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature headers.",
        )
    payload = await request.json()
    logger.info(f"concentriq_update, payload from Concentriq is " f"{payload}")
    computed_signature = get_signature(
        timestamp, payload, Settings.CONCENTRIQ_WEBHOOK_SECRET
    )
    if received_signature != computed_signature:
        logger.error(
            "Conentriq create error - concentriq_update 401 Internal Server Error "
            "Invalid webhook token."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token.",
        )
    try:
        logger.info(
            f"concentriq_update, payload from Concentriq is " f"{payload}"
        )
    except Exception as exc:
        logger.error(
            f"Conentriq create error - concentriq_update 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return True
