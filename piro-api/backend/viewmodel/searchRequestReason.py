from pydantic import BaseModel, Field


class SearchRequestReasonVMDropdown(BaseModel):
    SearchRequestReasonId: int = Field(alias="value")
    ShortName: str = Field(alias="text")
    Code: str = Field(alias="code")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
