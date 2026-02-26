from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# properties required during user creation
class SearchRequestVMCreate(BaseModel):
    name: str
    searchId: int
    reasonId: int
    irb: Optional[str]
    isPediatric: Optional[bool]
    comment: str
    fileData: Optional[bytes]
    dateTo: Optional[datetime] = None
    dateFrom: Optional[datetime] = None
    fileType: Optional[str]
    fileName: Optional[str]
    fileSize: Optional[int]
    selectedFields: Optional[list[int]]
    fileExtension: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class SearchRequestVMUpdate(SearchRequestVMCreate):
    searchRequestId: int
    searchRequestStatusId: int


class SearchRequestApprovalCommentVM(BaseModel):
    searchRequestId: int
    approvalComment: str


class SearchRequestVM(BaseModel):
    SearchRequestId: int = Field(alias="searchRequestId")
    SearchId: int = Field(alias="searchId")
    RequesterId: int = Field(alias="requesterId")
    SearchRequestStatusId: int = Field(alias="statusId")
    SearchRequestReasonId: int = Field(alias="reasonId")
    Requester: Optional[str] = Field(alias="requester")
    SearchName: Optional[str] = Field(alias="search")
    RequestName: Optional[str] = Field(alias="name")
    FromDate: Optional[datetime] = Field(alias="fromDate")
    ToDate: Optional[datetime] = Field(alias="toDate")
    IRB: Optional[str] = Field(alias="irb")
    IsPediatric: Optional[bool] = Field(alias="isPediatric")
    RequestComment: Optional[str] = Field(alias="comment")
    RequestDocumentFile: Optional[str] = Field(alias="fileName")
    RequestDocumentName: Optional[str] = Field(alias="fileData")
    RequestDocumentSize: Optional[str] = Field(alias="fileSize")
    RequestComment: Optional[str] = Field(alias="comment")
    ResultDocumentFile: Optional[str] = Field(alias="resultfileName")
    ResultDocumentName: Optional[str] = Field(alias="resultfileData")
    ResultDocumentSize: Optional[str] = Field(alias="resultSize")
    ApprovedById: Optional[int] = Field(alias="approvedById")
    ApprovedBy: Optional[str] = Field(alias="approvedBy")
    ApprovedDate: Optional[datetime] = Field(alias="approvedDate")
    ApprovalComment: Optional[str] = Field(alias="approvalComment")
    IsActive: bool = Field(alias="active")
    CreateDate: datetime = Field(alias="createOn")
    SearchRequestStatus: Optional[str] = Field(alias="status")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class SearchRequestDisplayVM(BaseModel):
    SearchRequestId: int = Field(alias="searchRequestId")
    SearchId: int = Field(alias="searchId")
    RequesterId: int = Field(alias="requesterId")
    SearchRequestReasonId: Optional[int] = Field(alias="reasonId")
    SearchRequestReason: Optional[str] = Field(alias="reason")
    SearchRequestReasonCode: Optional[str] = Field(alias="reasonCode")
    SearchRequestStatusId: int = Field(alias="statusId")
    RequestName: Optional[str] = Field(alias="name")
    FromDate: Optional[datetime] = Field(alias="fromDate")
    ToDate: Optional[datetime] = Field(alias="toDate")
    IRB: Optional[str] = Field(alias="irb")
    IsPediatric: Optional[bool] = Field(alias="isPediatric")
    RequestDocumentExtension: Optional[str] = Field(alias="fileExtn")
    RequestComment: Optional[str] = Field(alias="comment")
    ApprovedDate: Optional[datetime] = Field(alias="approvedDate")
    ClosedDate: Optional[datetime] = Field(alias="closedDate")
    SubmitDate: Optional[datetime] = Field(alias="submitDate")
    ApprovalComment: Optional[str] = Field(alias="approvalComment")
    IsActive: bool = Field(alias="active")
    Requester: Optional[str] = Field(alias="requester")
    SearchName: Optional[str] = Field(alias="search")
    SearchName: Optional[str] = Field(alias="searchName")
    SearchRequestStatus: Optional[str] = Field(alias="searchRequestStatus")
    RequestedBy: Optional[str] = Field(alias="requestedBy")
    ApprovedBy: Optional[str] = Field(alias="approvedBy")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
