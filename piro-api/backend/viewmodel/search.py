from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, root_validator


# properties required during user creation
class SearchVMCreate(BaseModel):
    name: str
    description: str
    query: str
    advfields: Optional[str]
    mrn: Optional[str]


class SearchVMUpdate(SearchVMCreate):
    searchId: int


class SearchVMDropdown(BaseModel):
    SearchId: int = Field(alias="value")
    Name: str = Field(alias="text")
    CreateDate: datetime = Field(alias="createOn")

    @root_validator
    def transform_data(cls, values):
        if "CreateDate" in values:
            dat = values["CreateDate"]
            if dat is not None:
                values["Name"] = (
                    f"({dat.strftime('%m-%d-%Y')}) {values['Name']}"
                )
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class SearchVM(BaseModel):
    SearchId: int = Field(alias="searchId")
    UserId: int = Field(alias="userId")
    Name: str = Field(alias="name")
    RequesterFirstName: Optional[str] = Field(alias="firstname")
    RequesterLastName: Optional[str] = Field(alias="lastname")
    Description: str = Field(alias="description")
    SearchQuery: str = Field(alias="query")
    AdvancedQuery: Optional[str] = Field(alias="advsearch")
    MRN: Optional[str] = Field(alias="mrn")
    Display: Optional[str] = Field(alias="display")
    IsActive: bool = Field(alias="active")
    CreateDate: datetime = Field(alias="createOn")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
