from pydantic import BaseModel, Field


class KeyValueData(BaseModel):
    key: str
    val: int
    type: str


class SuggestVM(BaseModel):
    Value: str = Field(alias="value")
    Name: str = Field(alias="name")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
