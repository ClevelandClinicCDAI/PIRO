import pathlib
import tempfile
from datetime import datetime
from typing import Annotated, List

from db.repository.auditTrailSearchRequest import create_audit_search_request

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.lookup import SearchRequestStatus_get_id
from db.repository.searchRequest import (
    create_new_searchRequest,
    delete_searchRequest,
    get_searchRequest,
    get_searchRequest_all,
    list_reasons_active,
    list_searchRequest_display,
    update_approvalComment,
    update_searchRequest_status,
)
from db.session import get_db, get_solr
from pysolr import Solr
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi_pagination import Page, paginate
from solr.repository.excel_search import create_excel, get_search_data
from sqlalchemy.orm import Session
from viewmodel.searchRequest import (
    SearchRequestApprovalCommentVM,
    SearchRequestDisplayVM,
    SearchRequestVM,
    SearchRequestVMCreate,
)
from db.repository.searchRequestDataField import list_searchRequestDataField
from viewmodel.searchRequestReason import SearchRequestReasonVMDropdown
from logger import logger

router = APIRouter()


@router.post(
    "/createrequest",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def create_searchRequest(
    # search_request: SearchRequestVMCreate,
    name: Annotated[str, Form()],
    comment: Annotated[str, Form()],
    reasonId: Annotated[str, Form()],
    searchId: Annotated[str, Form()],
    dateFrom: Annotated[str, Form()],
    dateTo: Annotated[str, Form()],
    irb: Annotated[str, Form()],
    isPediatric: Annotated[bool, Form()],
    selectedFields: Annotated[str, Form()],
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    file: UploadFile = File(...),  # noqa B008
):
    if not file:
        raise HTTPException(status_code=510, detail="File is empty")
    file_extension = pathlib.Path(file.filename).suffix

    date_from = datetime.strptime(dateFrom, "%Y-%m-%d %H:%M:%S")
    date_to = datetime.strptime(dateTo, "%Y-%m-%d %H:%M:%S")
    selectedFieldArr = [int(x) for x in selectedFields.split(",")]

    search_request: SearchRequestVMCreate = SearchRequestVMCreate(
        name=name,
        searchId=searchId,
        reasonId=reasonId,
        comment=comment,
        fileData=file.file.read(),
        dateFrom=date_from,
        dateTo=date_to,
        irb=irb,
        isPediatric=isPediatric,
        fileType=file.content_type,
        fileSize=file.size,
        fileName=file.filename,
        fileExtension=file_extension,
        selectedFields=selectedFieldArr,
    )

    searchRequestId = create_new_searchRequest(
        input=search_request,
        user=current_user,
        userId=int(current_user_id),
        db=db,
    )

    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.SUBMIT.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return True


@router.post(
    "/createrequestlite",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def create_searchRequestLite(
    # search_request: SearchRequestVMCreate,
    name: Annotated[str, Form()],
    comment: Annotated[str, Form()],
    reasonId: Annotated[str, Form()],
    searchId: Annotated[str, Form()],
    dateFrom: Annotated[str, Form()],
    dateTo: Annotated[str, Form()],
    selectedFields: Annotated[str, Form()],
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    date_from = datetime.strptime(dateFrom, "%Y-%m-%d %H:%M:%S")
    date_to = datetime.strptime(dateTo, "%Y-%m-%d %H:%M:%S")

    selectedFieldArr = [int(x) for x in selectedFields.split(",")]

    search_request: SearchRequestVMCreate = SearchRequestVMCreate(
        name=name,
        searchId=searchId,
        reasonId=reasonId,
        comment=comment,
        fileData=None,
        dateFrom=date_from,
        dateTo=date_to,
        fileType=None,
        fileSize=None,
        fileName=None,
        fileExtension=None,
        selectedFields=selectedFieldArr,
    )

    searchRequestId = create_new_searchRequest(
        input=search_request,
        user=current_user,
        userId=int(current_user_id),
        db=db,
    )

    try:
        # statusId = SearchRequestStatus_get_id(
        #     code=str(Constants.SearchRequestStatus.SUBMIT.name), db=db
        # )
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.SUBMIT.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return True


@router.post(
    "/create",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
    response_model=SearchRequestVM,
)
async def create(
    searchRequest: SearchRequestVMCreate,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    searchRequestId = create_new_searchRequest(
        input=searchRequest,
        user=current_user,
        userId=int(current_user_id),
        db=db,
    )
    try:
        # statusId = SearchRequestStatus_get_id(
        #     code=str(Constants.SearchRequestStatus.SUBMIT.name), db=db
        # )
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.SUBMIT.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return searchRequestId


@router.post(
    "/approvalcomment",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
)
async def update__searchRequest(
    searchRequest: SearchRequestApprovalCommentVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    db: Session = Depends(get_db),
):
    update_approvalComment(input=searchRequest, user=current_user, db=db)
    return True


@router.post(
    "/approve/{searchRequestId}",
    dependencies=[Depends(JWTBearer())],
)
async def approve_search_request(
    searchRequestId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.APPROVE.name), db=db
    )
    result = update_searchRequest_status(
        searchRequestId=searchRequestId,
        searchRequestStatusId=submit_status_id,
        approval_user_id=current_user_id,
        user=current_user,
        db=db,
    )

    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.APPROVE.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return result


@router.post("/deny/{searchRequestId}", dependencies=[Depends(JWTBearer())])
async def deny_search_request(
    searchRequestId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.DENY.name), db=db
    )
    result = update_searchRequest_status(
        searchRequestId=searchRequestId,
        searchRequestStatusId=submit_status_id,
        approval_user_id=current_user_id,
        user=current_user,
        db=db,
    )
    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.DENY.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return result


@router.post("/close/{searchRequestId}", dependencies=[Depends(JWTBearer())])
async def close(
    searchRequestId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.CLOSE.name), db=db
    )
    result = update_searchRequest_status(
        searchRequestId=searchRequestId,
        searchRequestStatusId=submit_status_id,
        approval_user_id=None,
        user=current_user,
        db=db,
    )
    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.CLOSE.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return result


@router.get(
    "/all",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestDisplayVM],
)
async def read_searchRequest_all(db: Session = Depends(get_db)):
    search_requests = list_searchRequest_display(
        statusId=0, userId=0, searchRequestId=0, db=db
    )
    return paginate(search_requests)


@router.get(
    "/allsubmit",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestDisplayVM],
)
async def read_searchRequest_all_submit(db: Session = Depends(get_db)):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.SUBMIT.name), db=db
    )
    search_requests = list_searchRequest_display(
        statusId=submit_status_id, userId=0, searchRequestId=0, db=db
    )
    return paginate(search_requests)


@router.get(
    "/mysubmit",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestDisplayVM],
)
async def read_searchRequest_my_submit(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.SUBMIT.name), db=db
    )
    search_requests = list_searchRequest_display(
        statusId=submit_status_id,
        userId=int(current_user_id),
        searchRequestId=0,
        db=db,
    )
    return paginate(search_requests)


@router.get(
    "/getall/{status}",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestDisplayVM],
)
async def read_searchRequest_status(
    status: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    submit_status_id = SearchRequestStatus_get_id(code=status, db=db)
    search_requests = list_searchRequest_display(
        statusId=submit_status_id,
        # userId=int(current_user_id),
        userId=0,
        searchRequestId=0,
        db=db,
    )
    return paginate(search_requests)


@router.get(
    "/allapproved",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestDisplayVM],
)
async def read_searchRequest_all_approved(db: Session = Depends(get_db)):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.APPROVE.name), db=db
    )
    search_requests = list_searchRequest_display(
        statusId=submit_status_id, userId=0, searchRequestId=0, db=db
    )
    return paginate(search_requests)


@router.get(
    "/alldeny",
    dependencies=[Depends(JWTBearer())],
    response_model=Page[SearchRequestDisplayVM],
)
async def read_searchRequest_all_deny(db: Session = Depends(get_db)):
    submit_status_id = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.DENY.name), db=db
    )
    search_requests = list_searchRequest_display(
        statusId=submit_status_id, userId=0, searchRequestId=0, db=db
    )
    return paginate(search_requests)


@router.get(
    "/get/{searchRequestId}",
    dependencies=[Depends(JWTBearer())],
    response_model=SearchRequestDisplayVM,
)
async def get(searchRequestId: int, db: Session = Depends(get_db)):
    search_request = get_searchRequest(searchRequestId=searchRequestId, db=db)
    return search_request


@router.delete(
    "/delete/{searchRequestId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
)
async def delete(
    searchRequestId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    delete_searchRequest(searchRequestId=searchRequestId, db=db)
    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.DELETE.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return True


@router.get(
    "/export/{searchRequestId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
)
async def export(
    searchRequestId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    solr: Solr = Depends(get_solr),
):
    search_request = get_searchRequest(searchRequestId=searchRequestId, db=db)
    searchRequestDataFields = list_searchRequestDataField(
        searchRequestId=searchRequestId, db=db
    )
    searchRequestDataFields = [
        x for x in searchRequestDataFields if x.IsSelected == True  # noqa
    ]
    fields: str = ",".join(
        str(x.DataFieldSolrField) for x in searchRequestDataFields
    )
    data = get_search_data(
        search_request.SearchId,
        fromDate=search_request.FromDate,
        toDate=search_request.ToDate,
        reasonCode=search_request.SearchRequestReasonCode,
        db=db,
        solr=solr,
        fields=fields,
    )
    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.EXPORT.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    file = create_excel(
        searchId=search_request.SearchId,
        data=data,
        fields=searchRequestDataFields,
    )
    headers = {"Content-Disposition": f'attachment; filename={file["file"]}'}

    if file["path"].endswith(".xlsx") is False:
        raise HTTPException(status_code=510, detail="File path is illegal")
    return FileResponse(file["path"], headers=headers)


@router.get(
    "/download/{searchRequestId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                ]
            )
        )
    ],
)
async def download(
    searchRequestId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    search_request = get_searchRequest_all(
        searchRequestId=searchRequestId, db=db
    )
    try:
        create_audit_search_request(
            userId=current_user_id,
            user=current_user,
            searchRequestId=searchRequestId,
            action=Constants.SearchRequestAction.DOWNLOAD.name,
            db=db,
        )
    except Exception as exc:
        logger.error(
            f"Search request audit error - create_audit_search_request 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )

    # https://stackoverflow.com/questions/55873174/how-do-i-return-an-image-in-fastapi
    with tempfile.NamedTemporaryFile(
        mode="w+b",
        prefix=search_request.RequestDocumentName,
        suffix=search_request.RequestDocumentExtension,
        delete=False,
    ) as FOUT:
        FOUT.write(search_request.RequestDocumentFile)
    return FileResponse(
        FOUT.name,
        media_type=search_request.RequestDocumentType,
    )


@router.get(
    "/reasondropdown",
    dependencies=[Depends(JWTBearer())],
    response_model=List[SearchRequestReasonVMDropdown],
)
async def get_reason_dropdown(db: Session = Depends(get_db)):
    reasons = list_reasons_active(db=db)
    return reasons
