from pydantic import BaseModel, Field


# properties required during user creation
class RoleVMCreate(BaseModel):
    display: str
    code: str
    description: str
    reference: str


class RoleVMUpdate(RoleVMCreate):
    roleId: int


class RoleVMDropdown(BaseModel):
    RoleId: int = Field(alias="value")
    ShortName: str = Field(alias="text")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class RoleVM(BaseModel):
    RoleId: int = Field(alias="roleId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    DataLabReference: str = Field(alias="reference")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
