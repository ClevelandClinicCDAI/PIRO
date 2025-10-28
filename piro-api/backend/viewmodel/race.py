from pydantic import BaseModel, Field


# properties required during user creation
class RaceVMCreate(BaseModel):
    display: str
    code: str
    description: str
    reference: str


class RaceVMUpdate(RaceVMCreate):
    raceId: int


class RaceVM(BaseModel):
    RaceId: int = Field(alias="raceId")
    ShortName: str = Field(alias="display")
    Code: str = Field(alias="code")
    Description: str = Field(alias="description")
    DataLabReference: str = Field(alias="reference")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
