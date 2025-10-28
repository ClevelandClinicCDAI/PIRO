from pydantic import BaseModel, Field


# properties required during user creation
class CommentTypeVMCreate(BaseModel):
    display: str
    code: str
    description: str
    reference: str
    etlSource: str


class CommentTypeVMUpdate(CommentTypeVMCreate):
    commentTypeId: int


class CommentTypeVM(BaseModel):
    CommentTypeId: int = Field(alias="commentTypeId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    DataLabReference: str = Field(alias="reference")
    ETLSource: str = Field(alias="etlSource")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
