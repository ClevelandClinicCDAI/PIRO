from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.tag import (
    create_new_tag,
    delete_tag,
    get_tag,
    list_tag_active,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from viewmodel.tag import TagVM, TagVMCreate, TagVMDropdown

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=TagVM,
)
async def create_tag(
    tag: TagVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    result = create_new_tag(
        input=tag, userId=current_userid, user=current_user, db=db
    )
    return result


@router.get(
    "/all", dependencies=[Depends(JWTBearer())], response_model=Page[TagVM]
)
async def read_tag_all(
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    tags = list_tag_active(userId=int(current_userid), db=db)
    return paginate(tags)


@router.get(
    "/dropdown",
    dependencies=[Depends(JWTBearer())],
    response_model=List[TagVMDropdown],
)
async def read_tag_dropdown(
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    tags = list_tag_active(userId=int(current_userid), db=db)
    return tags


@router.get(
    "/get/{tagId}", dependencies=[Depends(JWTBearer())], response_model=TagVM
)
async def get(tagId: int, db: Session = Depends(get_db)):
    tag = get_tag(tagId=tagId, db=db)
    return tag


@router.delete(
    "/delete/{tagId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=TagVM,
)
async def delete(tagId: int, db: Session = Depends(get_db)):
    tag = delete_tag(tagId=tagId, db=db)
    return tag
