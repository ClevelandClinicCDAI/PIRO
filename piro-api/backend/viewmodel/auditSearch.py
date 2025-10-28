from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, root_validator
from core.search_util import filter_str_object
from core.string_util import StringUtil


class AuditSearchVM(BaseModel):
    AuditTrailSearchId: int = Field(alias="id")
    SearchQuery: str = Field(alias="search")
    SearchDisplay: str = Field(alias="display")
    SearchUrl: str = Field(alias="url")
    AdvancedQuery: Optional[str] = Field(alias="advsearch")
    MRN: Optional[str] = Field(alias="mrn")
    AdvancedDisplay: Optional[str] = Field(alias="advdisplay")
    TotalHits: int = Field(alias="count")
    CreateDate: datetime = Field(alias="createOn")

    @root_validator
    def transform(cls, values):
        if values is None:
            return
        if "AdvancedQuery" in values:
            input = values["AdvancedQuery"]
            if input is not None and StringUtil.isNotBlank(input):
                display = filter_str_object(input)
                values["AdvancedDisplay"] = display
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
