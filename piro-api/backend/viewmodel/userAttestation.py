from pydantic import BaseModel, Field
from datetime import datetime

# properties required during user creation


class UserAttestationVM(BaseModel):
    TextAttest: str = Field(alias="textAttest")
    IsAttest: bool = Field(alias="isAttest")
    RequireAttest: bool = Field(alias="requireAttest")
    AttestationEnable: bool = Field(alias="enabled")
    CreateDate: datetime = Field(alias="created")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
