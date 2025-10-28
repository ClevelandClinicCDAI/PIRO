from pydantic import BaseModel, Field
from datetime import datetime


class AuditCaseAnnotationVMSearch(BaseModel):
    caseid: int
    configid: int


class AuditCaseAnnotationVM(BaseModel):
    AuditCaseAnnotationId: int = Field(alias="id")
    CaseAnnotationId: int = Field(alias="configid")
    AnnotationId: int = Field(alias="annotationid")
    CaseId: int = Field(alias="caseid")
    AnnotationConfigurationId: int = Field(alias="annotationConfigurationId")
    ModelName: str = Field(alias="model")
    AnnotationValue: str = Field(alias="value")
    CreateDate: datetime = Field(alias="created")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
