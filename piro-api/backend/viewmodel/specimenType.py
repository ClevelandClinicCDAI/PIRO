from pydantic import BaseModel, Field


# properties required during user creation
class SpecimenTypeVMCreate(BaseModel):
    display: str
    code: str
    description: str
    reference: str
    category: str


class SpecimenTypeVMUpdate(SpecimenTypeVMCreate):
    specimenTypeId: int


class SpecimenTypeVM(BaseModel):
    SpecimenTypeId: int = Field(alias="specimenTypeId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    DataLabReference: str = Field(alias="reference")
    # Category: str = Field(alias='category')
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
