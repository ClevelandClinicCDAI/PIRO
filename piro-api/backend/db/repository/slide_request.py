from datetime import datetime

from core.constants import Constants
from db.models.SlideRequest import SlideRequest
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload
from viewmodel.slide_request import SlideRequestCreateVM, SlideRoomNotesUpdateVM


def create_slide_request(
    input: SlideRequestCreateVM, user_id: int, user: str, db: Session
):
    request = SlideRequest(
        AccessionNumber=input.accessionNumber.strip(),
        Notes=input.notes.strip() if input.notes else None,
        UrgencyStatus=input.urgencyStatus,
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
    return query.order_by(asc(SlideRequest.CreateDate)).all()


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

    if request.Status == Constants.SlideRequestStatus.COMPLETED.value:
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

    if request.Status == Constants.SlideRequestStatus.NIF.value:
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
