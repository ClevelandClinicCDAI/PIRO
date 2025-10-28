from pydantic import BaseModel, Field


class AIVoteVM(BaseModel):
    AnnotationConfigurationId: int = Field(alias="annotationConfigurationId")
    Case: str = Field(alias="case")
    Comment: str = Field(alias="comment")
    Feedback: int = Field(alias="feedback")


class AIReviewVM(BaseModel):
    AnnotationConfigurationId: int = Field(alias="annotationConfigurationId")
    Case: str = Field(alias="case")


class AIVoteMarkReviewedVM(BaseModel):
    CaseAnnotationId: int = Field(alias="caseannotationid")
