from pydantic import BaseModel, Field
from typing import Optional


# properties required during user creation
class SpecimenSourceVMCreate(BaseModel):
    display: str
    code: str
    description: str
    score: Optional[float]
    reference: str


class SpecimenSourceVMUpdate(SpecimenSourceVMCreate):
    specimenSourceId: int


class SpecimenSourceVM(BaseModel):
    SpecimenSourceId: int = Field(alias="specimenSourceId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    RCPScore: Optional[float] = Field(alias="score")
    DataLabReference: str = Field(alias="reference")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
