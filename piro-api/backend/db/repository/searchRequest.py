from datetime import datetime
from core.constants import Constants
from core.config import Settings
from core.email import Email
from db.dict2Class import dict2Class
from db.models.Search import Search
from db.models.SearchRequest import SearchRequest
from db.models.SearchRequestReason import SearchRequestReason
from db.models.SearchRequestStatus import SearchRequestStatus
from db.models.ExtractionQueue import ExtractionQueue
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
    if bool(input.searchId) == bool(input.extractionSessionId):
        raise DataException(
            "Exactly one of searchId or extractionSessionId must be provided"
        )

    submitId = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.SUBMIT.name), db=db
    )

    searchRequest = SearchRequest(
        RequesterId=userId,
        SearchId=input.searchId,
        ExtractionSessionId=input.extractionSessionId,
        IsLlmAssisted=input.extractionSessionId is not None,
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


def email_extraction_run_completed(run_id: int, status: str, db: Session):
    """Notify the user who approved and started an LLM-assisted extraction run
    once it finishes (whether successfully or not).

    Only fires for runs tied to a SearchRequest (i.e. started via the
    Data Requests inbox's "Start Extraction" action) — not for ad-hoc
    validation/preview runs triggered from the Schema Builder by whoever
    designed the extraction schema.
    """
    if Settings.DATAREQUEST_EMAIL_ENABLE != "True":
        return

    searchRequest = (
        db.query(SearchRequest)
        .filter(SearchRequest.ExtractionRunId == run_id)
        .filter(SearchRequest.IsActive == True)  # noqa
        .first()
    )
    if searchRequest is None or searchRequest.ApprovedById is None:
        return

    approver = (
        db.query(User).filter(User.UserId == searchRequest.ApprovedById).first()
    )
    if approver is None or not approver.NUID:
        logger.warning(
            "Extraction completion email skipped for run %s because the "
            "approving user's NUID is missing.",
            run_id,
        )
        return

    recipient = f"{approver.NUID}@ccf.org"
    status_label = {
        "completed": "completed successfully",
        "completed_with_errors": "completed with some errors",
        "failed": "failed",
    }.get(status, status)

    subject = f"PIRO: Data extraction {status_label} - {searchRequest.RequestName}"
    html_body = f"""
    <html>
      <body>
        <p>The LLM-assisted extraction for your approved data request has {status_label}.</p>
        <p><strong>Request Name:</strong> {searchRequest.RequestName}</p>
        <p>You can review the results in the PIRO Data Requests inbox.</p>
      </body>
    </html>
    """

    email_obj = Email(subject=subject, html_body=html_body)
    email_obj.send(to=recipient, cc=None, bcc=None)


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
        .join(SearchRequest, SearchRequest.SearchId == Search.SearchId, isouter=True)
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
                "ExtractionSessionId": searchRequest.ExtractionSessionId,
                "IsLlmAssisted": searchRequest.IsLlmAssisted,
                "SearchRequestReasonId": searchRequest.SearchRequestReasonId,
                "SearchName": search.Name if search else None,
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
        case_count = None
        if searchRequest.IsLlmAssisted and searchRequest.ExtractionSessionId:
            case_count = (
                db.query(ExtractionQueue)
                .filter(ExtractionQueue.ExtractionSessionId == searchRequest.ExtractionSessionId)
                .count()
            )
        item = dict2Class(
            {
                "SearchRequestId": searchRequest.SearchRequestId,
                "SearchId": searchRequest.SearchId,
                "ExtractionSessionId": searchRequest.ExtractionSessionId,
                "ExtractionRunId": searchRequest.ExtractionRunId,
                "IsLlmAssisted": searchRequest.IsLlmAssisted,
                "ExtractionStatus": searchRequest.ExtractionStatus,
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
                "CaseCount": case_count,
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


def start_extraction_for_searchRequest(searchRequestId: int, user: str, db: Session):
    """Prepare a new ExtractionRun for an approved, LLM-assisted SearchRequest.

    Returns (searchRequest, run, case_ids, role-agnostic schema_json) so the
    caller (route layer) can schedule the actual background extraction job.
    Raises DataException on invalid state.
    """
    from db.repository.extraction import create_run, get_queue, reclaim_stale_run
    from db.models.ExtractionSession import ExtractionSession

    searchRequest = (
        db.query(SearchRequest)
        .filter(SearchRequest.SearchRequestId == searchRequestId)
        .filter(SearchRequest.IsActive == True)  # noqa
        .first()
    )
    if searchRequest is None:
        raise DataException("SearchRequest does not exist")
    if not searchRequest.IsLlmAssisted or searchRequest.ExtractionSessionId is None:
        raise DataException("SearchRequest is not LLM-assisted")

    approveId = SearchRequestStatus_get_id(
        code=str(Constants.SearchRequestStatus.APPROVE.name), db=db
    )
    if searchRequest.SearchRequestStatusId != approveId:
        raise DataException("SearchRequest must be approved before extraction can start")

    session = (
        db.query(ExtractionSession)
        .filter(ExtractionSession.ExtractionSessionId == searchRequest.ExtractionSessionId)
        .first()
    )
    if session is None or not session.SchemaJson:
        raise DataException("Extraction schema is not defined for this request")

    queue = get_queue(searchRequest.ExtractionSessionId, db)
    if not queue:
        raise DataException("Extraction schema has no queued cases")

    latest = reclaim_stale_run(searchRequest.ExtractionSessionId, db)
    if latest and latest.Status in ("pending", "running"):
        raise DataException(
            f"A run is already {latest.Status}. Wait for it to finish before starting another."
        )

    from core.config import settings

    run = create_run(
        session_id=searchRequest.ExtractionSessionId,
        schema_json=session.SchemaJson,
        llm_provider=settings.LLM_PROVIDER or "ollama",
        llm_model=settings.LLM_MODEL or "llama3.2",
        user=user,
        db=db,
        run_type="full",
    )

    searchRequest.ExtractionRunId = run.ExtractionRunId
    db.commit()

    case_ids = [q.CaseId for q in queue]
    return searchRequest, run, case_ids


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
