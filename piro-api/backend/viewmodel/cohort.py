from pydantic import BaseModel, Field
from typing import Optional


# properties required during user creation
class CohortDataVM:
    cohortId: int
    data: str
    firstName: str
    lastName: str


class CohortVMUpdate:
    cohortId: int
    name: str
    desc: str
    type: str
    fileData: Optional[bytes]


class CohortVMDropdown(BaseModel):
    CohortId: int = Field(alias="value")
    Name: str = Field(alias="text")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CohortVM(BaseModel):
    CohortId: int = Field(alias="cohortId")
    Name: str = Field(alias="name")
    Description: str = Field(alias="desc")
    Disease: str = Field(alias="disease")
    IsActive: bool = Field(alias="active")
    IsFacetDisplay: bool = Field(alias="display")
    PatientCountTotal: Optional[int] = Field(alias="patientCount")
    PatientCountMatched: Optional[int] = Field(alias="matched")
    PatientCountUnMatched: Optional[int] = Field(alias="unmatched")
    CaseCount: Optional[int] = Field(alias="caseCount")
    Type: str = Field(alias="type")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CohortFacetVM(BaseModel):
    CohortId: int = Field(alias="value")
    Name: str = Field(alias="name")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CohortDetailsVM:
    cohortId: int
    name: str
    desc: str
    disease: str
    display: bool
    dataType: str
    patientCount: Optional[int]
    matched: Optional[int]
    unmatched: Optional[int]
    caseCount: Optional[int]
    caseCountMatched: Optional[int]
