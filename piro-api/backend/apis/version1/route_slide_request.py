from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.slide_request import (
    cancel_slide_request,
    complete_slide_request,
    create_slide_request,
    hold_slide_request,
    take_slide_request,
    list_slide_requests,
    mark_slide_request_nif,
    reset_slide_request,
    update_slide_room_notes,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.slide_request import (
    SlideRequestCreateVM,
    SlideRequestVM,
    SlideRoomNotesUpdateVM,
    to_slide_request_vm,
)

router = APIRouter()

_REQUEST_ROLES = [
    Constants.RoleAdmin,
    Constants.RoleDemoAdmin,
    Constants.RoleAnalyst,
    Constants.RoleUser,
]

_QUEUE_ROLES = [
    Constants.RoleAdmin,
    Constants.RoleDemoAdmin,
    Constants.RoleSlideRoom,
]


@router.post(
    "",
    dependencies=[Depends(JWTBearer(_REQUEST_ROLES))],
    response_model=SlideRequestVM,
)
async def create_slide_request_endpoint(
    payload: SlideRequestCreateVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    request = create_slide_request(
        input=payload,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.get(
    "",
    dependencies=[Depends(JWTBearer(_REQUEST_ROLES))],
    response_model=List[SlideRequestVM],
)
async def list_my_slide_requests(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    requests = list_slide_requests(
        db=db, requester_id=int(current_user_id)
    )
    return [to_slide_request_vm(item) for item in requests]


@router.get(
    "/pending",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=List[SlideRequestVM],
)
async def list_pending_slide_requests(
    db: Session = Depends(get_db),
):
    requests = list_slide_requests(
        db=db, statuses=[Constants.SlideRequestStatus.PENDING.value]
    )
    return [to_slide_request_vm(item) for item in requests]


@router.get(
    "/holding",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=List[SlideRequestVM],
)
async def list_holding_slide_requests(
    db: Session = Depends(get_db),
):
    requests = list_slide_requests(
        db=db, statuses=[Constants.SlideRequestStatus.HOLDING.value]
    )
    return [to_slide_request_vm(item) for item in requests]


@router.get(
    "/in-process",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=List[SlideRequestVM],
)
async def list_in_process_slide_requests(
    db: Session = Depends(get_db),
):
    requests = list_slide_requests(
        db=db, statuses=[Constants.SlideRequestStatus.IN_PROCESS.value]
    )
    return [to_slide_request_vm(item) for item in requests]


@router.get(
    "/completed",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=List[SlideRequestVM],
)
async def list_completed_slide_requests(
    db: Session = Depends(get_db),
):
    requests = list_slide_requests(
        db=db,
        statuses=[
            Constants.SlideRequestStatus.COMPLETED.value,
            Constants.SlideRequestStatus.NIF.value,
            Constants.SlideRequestStatus.CANCELED.value,
        ],
    )
    return [to_slide_request_vm(item) for item in requests]


@router.post(
    "/{request_id}/complete",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=SlideRequestVM,
)
async def complete_slide_request_endpoint(
    request_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    request = complete_slide_request(
        request_id=request_id,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.post(
    "/{request_id}/hold",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=SlideRequestVM,
)
async def hold_slide_request_endpoint(
    request_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    request = hold_slide_request(
        request_id=request_id,
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.post(
    "/{request_id}/in-process",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=SlideRequestVM,
)
async def take_slide_request_endpoint(
    request_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    request = take_slide_request(
        request_id=request_id,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.post(
    "/{request_id}/nif",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=SlideRequestVM,
)
async def mark_slide_request_nif_endpoint(
    request_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    request = mark_slide_request_nif(
        request_id=request_id,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.post(
    "/{request_id}/reset",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=SlideRequestVM,
)
async def reset_slide_request_endpoint(
    request_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    request = reset_slide_request(
        request_id=request_id,
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.post(
    "/{request_id}/cancel",
    dependencies=[Depends(JWTBearer(_REQUEST_ROLES))],
    response_model=SlideRequestVM,
)
async def cancel_slide_request_endpoint(
    request_id: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    request = cancel_slide_request(
        request_id=request_id,
        user_id=int(current_user_id),
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)


@router.post(
    "/{request_id}/notes",
    dependencies=[Depends(JWTBearer(_QUEUE_ROLES))],
    response_model=SlideRequestVM,
)
async def update_slide_room_notes_endpoint(
    request_id: int,
    payload: SlideRoomNotesUpdateVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    request = update_slide_room_notes(
        request_id=request_id,
        input=payload,
        user=current_user,
        db=db,
    )
    return to_slide_request_vm(request)
