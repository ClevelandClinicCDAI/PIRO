from pydantic import BaseModel, Field


# properties required during user creation
class TagCaseVMCreate(BaseModel):
    caseid: int
    tagid: int


class TagCaseVM(BaseModel):
    TagCaseId: int = Field(alias="tagcaseid")
    TagId: int = Field(alias="tagid")
    CaseId: int = Field(alias="caseid")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class TagCaseDisplayVM(BaseModel):
    TagCaseId: int = Field(alias="tagcaseid")
    TagId: int = Field(alias="tagid")
    CaseId: int = Field(alias="caseid")
    UserId: int = Field(alias="userid")
    TagName: str = Field(alias="tag")
    TagDesc: str = Field(alias="desc")
    CaseNumber: str = Field(alias="case")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
