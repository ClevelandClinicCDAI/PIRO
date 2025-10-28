from datetime import date

from pydantic import BaseModel, Field


class ETL_LogVM(BaseModel):
    Id: int = Field(alias="id")
    TableName: str = Field(alias="tablename")
    ToBeInsertRecordCount: str = Field(alias="insertcount")
    InsertRecordCount: str = Field(alias="insertedcount")
    TobeUpdateRecordCount: str = Field(alias="updatecount")
    UpdateRecordCount: str = Field(alias="updatedcount")
    IsSuccess: bool = Field(alias="success")
    ErrorMessage: str = Field(alias="message")
    CreatedDate: date = Field(alias="createdon")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
