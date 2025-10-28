from typing import Annotated

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_nuid
from db.repository.commentType import (
    create_new_commentType,
    delete_commentType,
    get_commentType,
    list_commentType,
    list_commentType_active,
    update_commentType,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.commentType import (
    CommentTypeVM,
    CommentTypeVMCreate,
    CommentTypeVMUpdate,
)

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=CommentTypeVM,
)
async def create_commentType(
    commentType: CommentTypeVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_commentType(
        input=commentType, user=current_user, db=db
    )
    return result


@router.post(
    "/update",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=CommentTypeVM,
)
async def update__commentType(
    commentType: CommentTypeVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = update_commentType(input=commentType, user=current_user, db=db)
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[CommentTypeVM],
)
async def read_commentType_all(db: Session = Depends(get_db)):
    commentTypes = list_commentType(db=db)
    return paginate(commentTypes)


@router.get(
    "/active",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[CommentTypeVM],
)
async def read_commentType_all_active(db: Session = Depends(get_db)):
    commentTypes = list_commentType_active(db=db)
    return paginate(commentTypes)


@router.get(
    "/get/{commentTypeId}",
    dependencies=[Depends(JWTBearer())],
    response_model=CommentTypeVM,
)
async def get(commentTypeId: int, db: Session = Depends(get_db)):
    commentType = get_commentType(commentTypeId=commentTypeId, db=db)
    return commentType


@router.delete(
    "/delete/{commentTypeId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=CommentTypeVM,
)
async def delete(commentTypeId: int, db: Session = Depends(get_db)):
    commentType = delete_commentType(commentTypeId=commentTypeId, db=db)
    return commentType
