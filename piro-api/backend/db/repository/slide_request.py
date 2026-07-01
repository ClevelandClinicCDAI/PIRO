from datetime import datetime

from core.config import Settings
from core.constants import Constants
from core.email import Email
from db.models.SlideRequest import SlideRequest
from exception.data_exception import DataException
from logger import logger
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload
from viewmodel.slide_request import (
    SlideRequestCreateVM,
    SlideRoomNotesUpdateVM,
    derive_slide_request_case_type,
)


def _send_slide_request_completed_email(request: SlideRequest):
    if not Settings.EMAIL_SMTP_SERVER or not Settings.EMAIL_FROM:
        logger.warning(
            "Slide request completion email skipped for request %s because email settings are not configured.",
            request.SlideRequestId,
        )
        return

    requester = request.Requester
    requester_nuid = getattr(requester, "NUID", None)
    if not requester_nuid:
        logger.warning(
            "Slide request completion email skipped for request %s because the requester NUID is missing.",
            request.SlideRequestId,
        )
        return

    recipient = f"{requester_nuid}@ccf.org"
    subject = f"PIRO: Slide request completed - {request.AccessionNumber}"
    html_body = f"""
    <html>
      <body>
        <p>Your slide request has been completed.</p>
        <p><strong>Accession Number:</strong> {request.AccessionNumber}</p>
        <p>You can review the request in PIRO for any slide room notes.</p>
      </body>
    </html>
    """

    email_obj = Email(subject=subject, html_body=html_body)
    email_obj.send(to=recipient, cc=None, bcc=None)


def create_slide_request(
    input: SlideRequestCreateVM, user_id: int, user: str, db: Session
):
    request = SlideRequest(
        AccessionNumber=input.accessionNumber.strip(),
        CaseType=derive_slide_request_case_type(input.accessionNumber).value,
        Notes=input.requesterNotes.strip() if input.requesterNotes else None,
        EPath=bool(input.ePath),
        UrgencyStatus=input.urgencyStatus,
        Reason=input.reason,
        RequesterId=user_id,
        Status=Constants.SlideRequestStatus.PENDING.value,
        CreateBy=user,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def list_slide_requests(
    db: Session,
    statuses: list[str] | None = None,
    requester_id: int | None = None,
    case_type: Constants.SlideRequestCaseType | None = None,
    order_by_completed_desc: bool = False,
    limit: int | None = None,
):
    query = (
        db.query(SlideRequest)
        .options(joinedload(SlideRequest.Requester))
        .options(joinedload(SlideRequest.CompletedBy))
        .options(joinedload(SlideRequest.InProcessBy))
    )
    if statuses:
        query = query.filter(SlideRequest.Status.in_(statuses))
    if requester_id:
        query = query.filter(SlideRequest.RequesterId == requester_id)
    if case_type:
        query = query.filter(SlideRequest.CaseType == case_type.value)
    if order_by_completed_desc:
        query = query.order_by(
            desc(SlideRequest.CompletedDate),
            desc(SlideRequest.CreateDate),
            desc(SlideRequest.SlideRequestId),
        )
    else:
        query = query.order_by(asc(SlideRequest.CreateDate))

    if limit is not None:
        query = query.limit(limit)

    return query.all()


def complete_slide_request(
    request_id: int, user_id: int, user: str, db: Session
):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None:
        raise DataException("Slide request does not exist")

    if request.Status in (
        Constants.SlideRequestStatus.COMPLETED.value,
        Constants.SlideRequestStatus.CANCELED.value,
    ):
        return request

    completed_at = datetime.now().replace(tzinfo=None)
    request.Status = Constants.SlideRequestStatus.COMPLETED.value
    request.CompletedById = user_id
    if request.InProcessById is None:
        request.InProcessById = user_id
    request.CompletedDate = completed_at
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    try:
        _send_slide_request_completed_email(request)
    except Exception as exc:
        logger.error(
            "Slide request completion email failed for request %s <%s : %s>",
            request.SlideRequestId,
            str(exc),
            exc.args,
        )
    return request


def hold_slide_request(request_id: int, user: str, db: Session):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None:
        raise DataException("Slide request does not exist")

    if request.Status in (
        Constants.SlideRequestStatus.COMPLETED.value,
        Constants.SlideRequestStatus.NIF.value,
        Constants.SlideRequestStatus.CANCELED.value,
        Constants.SlideRequestStatus.HOLDING.value,
    ):
        return request

    request.Status = Constants.SlideRequestStatus.HOLDING.value
    request.CompletedById = None
    request.InProcessById = None
    request.CompletedDate = None
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    return request


def take_slide_request(request_id: int, user_id: int, user: str, db: Session):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None:
        raise DataException("Slide request does not exist")

    if request.Status in (
        Constants.SlideRequestStatus.COMPLETED.value,
        Constants.SlideRequestStatus.NIF.value,
        Constants.SlideRequestStatus.CANCELED.value,
        Constants.SlideRequestStatus.IN_PROCESS.value,
    ):
        return request

    request.Status = Constants.SlideRequestStatus.IN_PROCESS.value
    request.InProcessById = user_id
    request.CompletedById = None
    request.CompletedDate = None
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    return request


def mark_slide_request_nif(
    request_id: int, user_id: int, user: str, db: Session
):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None:
        raise DataException("Slide request does not exist")

    if request.Status in (
        Constants.SlideRequestStatus.NIF.value,
        Constants.SlideRequestStatus.CANCELED.value,
    ):
        return request

    completed_at = datetime.now().replace(tzinfo=None)
    request.Status = Constants.SlideRequestStatus.NIF.value
    request.CompletedById = user_id
    if request.InProcessById is None:
        request.InProcessById = user_id
    request.CompletedDate = completed_at
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    return request


def reset_slide_request(request_id: int, user: str, db: Session):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None:
        raise DataException("Slide request does not exist")

    if request.Status == Constants.SlideRequestStatus.PENDING.value:
        return request

    request.Status = Constants.SlideRequestStatus.PENDING.value
    request.CompletedById = None
    request.InProcessById = None
    request.CompletedDate = None
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    return request


def cancel_slide_request(
    request_id: int, user_id: int, user: str, db: Session
):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None or request.RequesterId != user_id:
        raise DataException("Slide request does not exist")
    if request.Status == Constants.SlideRequestStatus.CANCELED.value:
        return request
    if request.Status in (
        Constants.SlideRequestStatus.COMPLETED.value,
        Constants.SlideRequestStatus.NIF.value,
    ):
        return request

    canceled_at = datetime.now().replace(tzinfo=None)
    request.Status = Constants.SlideRequestStatus.CANCELED.value
    request.CompletedById = user_id
    request.CompletedDate = canceled_at
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    return request


def update_slide_room_notes(
    request_id: int,
    input: SlideRoomNotesUpdateVM,
    user: str,
    db: Session,
):
    request = (
        db.query(SlideRequest)
        .filter(SlideRequest.SlideRequestId == request_id)
        .first()
    )
    if request is None:
        raise DataException("Slide request does not exist")

    request.SlideRoomNotes = input.slideRoomNotes
    request.UpdateBy = user
    db.commit()
    db.refresh(request)
    return request
