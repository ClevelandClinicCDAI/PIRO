from pydantic import BaseModel, Field


# properties required during user creation
class UserVMCreate(BaseModel):
    nuid: str
    firstName: str
    lastName: str
    roleId: int


class UserVMUpdate(UserVMCreate):
    userId: int


class UserVMUpdateProfile(BaseModel):
    firstName: str
    lastName: str


class UserVM(BaseModel):
    UserId: int = Field(alias="userId")
    NUID: str = Field(alias="nuid")
    FirstName: str = Field(alias="firstName")
    LastName: str = Field(alias="lastName")
    Role: str = Field(alias="role")
    # RoleId: int = Field(alias="roleId")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class UserAuthVM(BaseModel):
    Role: str = Field(alias="role")
    IsAuth: bool = Field(alias="isauth")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class UserDetailsVM(BaseModel):
    Name: str = Field(alias="name")
    Nuid: str = Field(alias="nuid")
    Role: str = Field(alias="role")
    IsAuth: bool = Field(alias="isauth")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
