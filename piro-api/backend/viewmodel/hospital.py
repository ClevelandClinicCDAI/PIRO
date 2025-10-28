from pydantic import BaseModel, Field


# properties required during user creation
class HospitalVMCreate(BaseModel):
    # regionId: int
    display: str
    code: str
    description: str
    reference: str


class HospitalVMUpdate(HospitalVMCreate):
    hospitalId: int


class HospitalVM(BaseModel):
    HospitalId: int = Field(alias="hospitalId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    DataLabReference: str = Field(alias="reference")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
