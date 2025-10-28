from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.tagCase import (
    create_new_tagcase,
    delete_tagcase,
    list_tagcase_active,
    list_tagname_active,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.tagCase import TagCaseDisplayVM, TagCaseVM, TagCaseVMCreate

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=TagCaseVM,
)
async def create_tagcase(
    tagCase: TagCaseVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    result = create_new_tagcase(input=tagCase, user=current_user, db=db)
    return result


@router.get(
    "/all/{caseId}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[TagCaseDisplayVM],
)
async def read_tagCase_all(
    caseId: int,
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    tagCases = list_tagcase_active(caseId=caseId, userId=current_userid, db=db)
    return tagCases


@router.get(
    "/tags/{caseId}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[str],
)
async def read_tagcases_all(
    caseId: int,
    current_userid: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    tagCases = list_tagname_active(caseId=caseId, userId=current_userid, db=db)
    return tagCases


@router.delete(
    "/delete/{tagCaseId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=TagCaseVM,
)
async def delete(tagCaseId: int, db: Session = Depends(get_db)):
    tagCase = delete_tagcase(tagCaseId=tagCaseId, db=db)
    return tagCase
