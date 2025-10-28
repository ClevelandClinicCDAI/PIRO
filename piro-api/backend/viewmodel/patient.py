from pydantic import BaseModel, Field


# properties required during user creation


class PatientVM(BaseModel):
    PatientId: int = Field(alias="patientid")
    MRN: str = Field(alias="mrn")
    EpiId: str = Field(alias="epi")
    FirstName: str = Field(alias="firstname")
    LastName: str = Field(alias="lastname")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
