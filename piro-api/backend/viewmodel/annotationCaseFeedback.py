from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AnnotationCaseFeedbackVMCreate(BaseModel):
    annotationCaseFeedbackId: Optional[int]
    annotationConfigurationId: Optional[int]
    caseid: Optional[int]
    feedback: Optional[int]
    comment: Optional[str]


class AnnotationCaseFeedbackVMSearch(BaseModel):
    annotationConfigurationId: Optional[int]
    caseid: Optional[int]
    casenum: Optional[str]
    pending: Optional[bool]
    feedback: Optional[int]


class AnnotationCaseFeedbackVM(BaseModel):
    AnnotationCaseFeedbackId: int = Field(alias="id")
    AnnotationConfigurationId: int = Field(alias="configid")
    CaseId: int = Field(alias="caseid")
    CaseNumber: str = Field(alias="casenum")
    Feedback: int = Field(alias="feedback")
    IsReviewed: bool = Field(alias="reviewed")
    Comment: str = Field(alias="comment")
    AnnotationConfigurationName: str = Field(
        alias="annotationConfigurationName"
    )
    UserName: Optional[str] = Field(alias="user")
    CreateDate: datetime = Field(alias="created")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class AnnotationCaseFeedbackDataVM(BaseModel):
    PostiveVoteCount: int = Field(alias="postiveVoteCount")
    NegativeVoteCount: int = Field(alias="negativeVoteCount")
    MyVote: int = Field(alias="myVote")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
