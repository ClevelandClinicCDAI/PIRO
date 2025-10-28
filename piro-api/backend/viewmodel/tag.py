from pydantic import BaseModel, Field


# properties required during user creation
class TagVMCreate(BaseModel):
    name: str
    description: str


class TagVMDropdown(BaseModel):
    TagId: int = Field(alias="value")
    Name: str = Field(alias="text")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class TagVM(BaseModel):
    TagId: int = Field(alias="tagid")
    Name: str = Field(alias="name")
    Description: str = Field(alias="description")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
