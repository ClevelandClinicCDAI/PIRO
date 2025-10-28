from datetime import datetime
from core.constants import Constants
from core.config import Settings
from core.email import Email
from db.dict2Class import dict2Class
from db.models.Search import Search
from db.models.SearchRequest import SearchRequest
from db.models.SearchRequestReason import SearchRequestReason
from db.models.SearchRequestStatus import SearchRequestStatus
from db.models.User import User
from db.repository.lookup import SearchRequestStatus_get_id
from db.repository.searchRequestDataField import (
    addupdate_searchRequestDataFields,
)
from db.views.VSearchRequest import VSearchRequest
from exception.data_exception import DataException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, aliased
from viewmodel.searchRequest import (
    SearchRequestApprovalCommentVM,
    SearchRequestVMCreate,
)
from jinja2 import Template
from logger import logger


def create_new_searchRequest(
    input: SearchRequestVMCreate, user: str, userId: int, db: Session
):

    submitId = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.SUBMIT.name), db=db
    )

    searchRequest = SearchRequest(
        RequesterId=userId,
        SearchId=input.searchId,
        SearchRequestReasonId=input.reasonId,
        SearchRequestStatusId=submitId,
        RequestName=input.name,
        FromDate=input.dateFrom,
        ToDate=input.dateTo,
        IRB=input.irb,
        IsPediatric=input.isPediatric,
        RequestDocumentFile=input.fileData,
        RequestDocumentName=input.fileName,
        RequestDocumentSize=input.fileSize,
        RequestDocumentType=input.fileType,
        RequestDocumentExtension=input.fileExtension,
        RequestComment=input.comment,
        ResultDocumentFile=None,
        ResultDocumentName=None,
        ResultDocumentSize=None,
        ApprovedById=None,
        ApprovedDate=None,
        ApprovalComment=None,
        IsActive=True,
        CreateBy=user,
    )
    db.add(searchRequest)
    db.commit()
    db.refresh(searchRequest)
    addupdate_searchRequestDataFields(
        searchRequstId=searchRequest.SearchRequestId,
        dataFields=input.selectedFields,
        user=user,
        db=db,
    )
    try:
        email_searchRequest(
            searchRequestId=searchRequest.SearchRequestId, db=db
        )
    except Exception as exc:
        logger.error(
            f"Email delivery error - {searchRequest.SearchRequestId} 500 Internal Server Error "
            f"<{str(exc)} : {exc.args}>"
        )
    return searchRequest.SearchRequestId


def email_searchRequest(searchRequestId: int, db: Session):
    if Settings.DATAREQUEST_EMAIL_ENABLE == "True":
        search_request = get_searchRequest(
            searchRequestId=searchRequestId, db=db
        )
        f = open(
            Settings.DATAREQUEST_EMAIL_Template_DIRECTORY
            + Settings.DATAREQUEST_EMAIL_Template_FILE,
            "r",
        )
        html = f.read()

        body_template = Template(html, autoescape=True)
        html_transform = body_template.render(search_request.__dict__)

        subject = Settings.DATAREQUEST_EMAIL_SUBJECT
        subject_template = Template(subject, autoescape=True)
        subject_transform = subject_template.render(search_request.__dict__)

        to_adress = Settings.DATAREQUEST_EMAIL_TO
        cc_adress = Settings.DATAREQUEST_EMAIL_CC

        email_obj = Email(subject=subject_transform, html_body=html_transform)
        email_obj.send(to=to_adress, cc=cc_adress, bcc=None)


def update_approvalComment(
    input: SearchRequestApprovalCommentVM, user: str, db: Session
):
    search = (
        db.query(SearchRequest)
        .filter(SearchRequest.SearchRequestId == input.searchRequestId)
        .first()
    )
    if search is not None:
        search.ApprovalComment = input.approvalComment
        search.UpdatedBy = user
        db.commit()
    else:
        raise DataException("SearchRequest does not exist")
    return search


def update_searchRequest_status(
    searchRequestId: int,
    searchRequestStatusId: int,
    approval_user_id: int,
    user: str,
    db: Session,
):
    search = (
        db.query(SearchRequest)
        .filter(SearchRequest.SearchRequestId == searchRequestId)
        .first()
    )
    if search is not None:
        search.SearchRequestStatusId = searchRequestStatusId
        search.IsActive = True
        search.UpdatedBy = user
        if approval_user_id is not None:
            search.ApprovedById = approval_user_id
            search.ApprovedDate = datetime.now()
        db.commit()
    else:
        raise DataException("SearchRequest does not exist")
    return search


def list_searchRequest(
    statusId: int, userId: int, searchRequestId: int, db: Session
):
    queries = [SearchRequestStatus.IsActive == True]  # noqa
    if statusId != 0:
        queries.append(SearchRequestStatus.SearchRequestStatusId == statusId)
    if searchRequestId != 0:
        queries.append(SearchRequest.SearchRequestId == searchRequestId)
    if userId != 0:
        queries.append(SearchRequest.RequesterId == userId)
    result = []

    Reviewer = aliased(User)
    Approver = aliased(User)

    data = (
        db.query(
            SearchRequest, Search, SearchRequestStatus, Reviewer, Approver
        )
        .join(SearchRequest, SearchRequest.SearchId == Search.SearchId)
        .join(
            SearchRequestStatus,
            SearchRequest.SearchRequestStatusId
            == SearchRequestStatus.SearchRequestStatusId,
        )
        .join(Reviewer, SearchRequest.RequesterId == Reviewer.UserId)
        .join(
            Approver,
            SearchRequest.ApprovedById == Approver.UserId,
            isouter=True,
        )
        .filter(*queries)
        .order_by(desc(SearchRequest.SearchRequestId))
        .all()
    )

    for (
        searchRequest,
        search,
        searchRequestStatus,
        requester,
        approver,
    ) in data:
        item = dict2Class(
            {
                "SearchRequestId": searchRequest.SearchRequestId,
                "RequesterId": searchRequest.RequesterId,
                "Requester": requester.NUID,
                "SearchId": searchRequest.SearchId,
                "SearchRequestReasonId": searchRequest.SearchRequestReasonId,
                "SearchName": search.Name,
                "RequestName": searchRequest.RequestName,
                "FromDate": searchRequest.FromDate,
                "ToDate": searchRequest.ToDate,
                "IRB": searchRequest.IRB,
                "IsPediatric": searchRequest.IsPediatric,
                "RequestComment": searchRequest.RequestComment,
                "SearchRequestStatusId": searchRequest.SearchRequestStatusId,
                "RequestDocumentFile": searchRequest.RequestDocumentFile,
                "RequestDocumentName": searchRequest.RequestDocumentName,
                "RequestDocumentSize": searchRequest.RequestDocumentSize,
                "RequestDocumentType": searchRequest.RequestDocumentType,
                "RequestDocumentExtension": searchRequest.RequestDocumentExtension,  # noqa E5011
                "ResultDocumentFile": searchRequest.ResultDocumentFile,
                "ResultDocumentName": searchRequest.ResultDocumentName,
                "ResultDocumentSize": searchRequest.ResultDocumentSize,
                "ApprovedById": searchRequest.ApprovedById,
                "ApprovedBy": "" if approver is None else approver.NUID,
                "ApprovedDate": searchRequest.ApprovedDate,
                "IsActive": searchRequest.IsActive,
                "CreateDate": searchRequest.CreateDate,
                "SearchRequestStatus": searchRequestStatus.ShortName,
            }
        )
        result.append(item)
    return result


def list_searchRequest_display(
    statusId: int, userId: int, searchRequestId: int, db: Session
):
    queries = [VSearchRequest.IsActive == True]  # noqa
    if statusId != 0:
        queries.append(VSearchRequest.SearchRequestStatusId == statusId)
    if searchRequestId != 0:
        queries.append(VSearchRequest.SearchRequestId == searchRequestId)
    if userId != 0:
        queries.append(VSearchRequest.RequesterId == userId)
    result = []

    data = (
        db.query(VSearchRequest)
        .filter(*queries)
        .order_by(desc(VSearchRequest.SearchRequestId))
        .all()
    )

    for searchRequest in data:
        item = dict2Class(
            {
                "SearchRequestId": searchRequest.SearchRequestId,
                "SearchId": searchRequest.SearchId,
                "RequesterId": searchRequest.RequesterId,
                "RequestName": searchRequest.RequestName,
                "SearchRequestStatusId": searchRequest.SearchRequestStatusId,
                "SearchRequestReasonId": searchRequest.SearchRequestReasonId,
                "SearchRequestReason": searchRequest.SearchRequestReason,
                "SearchRequestReasonCode": searchRequest.SearchRequestReasonCode,  # noqa E5011
                "FromDate": searchRequest.FromDate,
                "ToDate": searchRequest.ToDate,
                "IRB": searchRequest.IRB,
                "IsPediatric": searchRequest.IsPediatric,
                "RequestDocumentExtension": searchRequest.RequestDocumentExtension,  # noqa E5011
                "RequestComment": searchRequest.RequestComment,
                "ApprovedDate": searchRequest.ApprovedDate,
                "ClosedDate": searchRequest.UpdateDate,
                "SubmitDate": searchRequest.CreateDate,
                "ApprovalComment": searchRequest.ApprovalComment,
                "IsActive": searchRequest.IsActive,
                "SearchName": searchRequest.SearchName,
                "SearchRequestStatus": searchRequest.SearchRequestStatus,
                "RequestedBy": searchRequest.RequestedBy,
                "ApprovedBy": searchRequest.ApprovedBy,
            }
        )
        result.append(item)
    return result


def get_searchRequest(searchRequestId: int, db: Session):
    data = list_searchRequest_display(0, 0, searchRequestId, db)

    for item in data:
        return item
    raise DataException("SearchRequest does not exist")


def get_searchRequest_all(searchRequestId: int, db: Session):
    data = list_searchRequest(0, 0, searchRequestId, db)

    for item in data:
        return item
    raise DataException("SearchRequest does not exist")


def delete_searchRequest(searchRequestId: int, db: Session):
    searchRequest = (
        db.query(SearchRequest)
        .filter(SearchRequest.SearchRequestId == searchRequestId)
        .filter(SearchRequest.IsActive == True)  # noqa
        .first()
    )
    if searchRequest is not None:
        searchRequest.IsActive = False
        db.commit()
    else:
        raise DataException("SearchRequest does not exist")
    return searchRequest


def list_reasons_active(db: Session):
    search = (
        db.query(SearchRequestReason)
        .filter(SearchRequestReason.IsActive == True)  # noqa
        .order_by(asc(SearchRequestReason.ShortName))
        .all()
    )
    return search
