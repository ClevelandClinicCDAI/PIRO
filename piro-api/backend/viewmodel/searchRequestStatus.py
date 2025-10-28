from pydantic import BaseModel, Field


# properties required during user creation
class SearchRequestStatusVMCreate(BaseModel):
    display: str
    code: str
    description: str


class SearchRequestStatusVMUpdate(SearchRequestStatusVMCreate):
    searchRequestStatusId: int


class SearchRequestStatusVMDropdown(BaseModel):
    SearchRequestStatusId: int = Field(alias="value")
    ShortName: str = Field(alias="text")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class SearchRequestStatusVM(BaseModel):
    SearchRequestStatusId: int = Field(alias="searchRequestStatusId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
