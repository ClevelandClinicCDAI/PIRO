from pydantic import BaseModel, Field
from typing import List


class AuditReportVM(BaseModel):
    Labels: List[str] = Field(alias="labels")
    SearchData: List[int] = Field(alias="search")
    CaseData: List[int] = Field(alias="case")
    SearchLabel: List[int] = Field(
        alias="searchlabel", default="# of Search Requests"
    )
    CaseLabel: List[int] = Field(alias="caselabel", default="# of Cases")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
