from typing import Annotated, List

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.searchRequestDataField import (
    addupdate_searchRequestDataFields,
    list_dataField,
    list_searchRequestDataField,
    delete_searchRequestDataField,
)
from db.repository.auditTrailSearchRequest import create_audit_search_request
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.serarchRequestDataField import (
    DataFieldMasterVM,
    SearchRequestDataFieldsVMUpdate,
    SearchRequestDataFieldVM,
)

router = APIRouter()


@router.post(
    "/update",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                    Constants.RoleDemoAdmin,
                ]
            )
        )
    ],
    response_model=bool,
)
async def update_searchRequestDataField(
    input: SearchRequestDataFieldsVMUpdate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    addupdate_searchRequestDataFields(
        searchRequstId=input.searchrequestId,
        dataFields=input.dataFields,
        user=current_user,
        db=db,
    )

    create_audit_search_request(
        userId=current_user_id,
        user=current_user,
        searchRequestId=input.searchrequestId,
        action=Constants.SearchRequestAction.UPDATE.name,
        db=db,
    )

    return True


@router.get(
    "/getdatafields",
    dependencies=[Depends(JWTBearer())],
    response_model=DataFieldMasterVM,
)
async def getdatafields(db: Session = Depends(get_db)):
    searchRequestDataFields = list_dataField(db=db)
    return searchRequestDataFields


@router.get(
    "/get/{searchRequestId}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[SearchRequestDataFieldVM],
)
async def get(searchRequestId: int, db: Session = Depends(get_db)):
    if searchRequestId == -1:
        searchRequestDataFields = list_dataField(db=db)
    else:
        searchRequestDataFields = list_searchRequestDataField(
            searchRequestId=searchRequestId, db=db
        )
    return searchRequestDataFields


@router.delete(
    "/delete/{searchRequestDataFieldId}",
    dependencies=[
        Depends(JWTBearer([Constants.RoleAdmin, Constants.RoleDemoAdmin]))
    ],
    response_model=bool,
)
async def delete(searchRequestDataFieldId: int, db: Session = Depends(get_db)):
    delete_searchRequestDataField(
        searchRequestDataFieldId == searchRequestDataFieldId, db=db
    )
    return True
