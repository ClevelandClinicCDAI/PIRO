from pydantic import BaseModel, Field


# properties required during user creation
class EthnicityVMCreate(BaseModel):
    display: str
    code: str
    description: str
    reference: str


class EthnicityVMUpdate(EthnicityVMCreate):
    ethnicityId: int


class EthnicityVM(BaseModel):
    EthnicityId: int = Field(alias="ethnicityId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    DataLabReference: str = Field(alias="reference")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
