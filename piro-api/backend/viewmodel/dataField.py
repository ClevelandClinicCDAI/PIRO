from pydantic import BaseModel, Field


# properties required during user creation
class DataFieldVMCreate(BaseModel):
    display: str
    code: str
    solrfield: str
    sequence: int
    categoryid: int


class DataFieldVMUpdate(DataFieldVMCreate):
    datafieldId: int


class DataFieldCategoryVMDropdown(BaseModel):
    DataFieldCategoryId: int = Field(alias="categoryid")
    DisplayName: str = Field(alias="display")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class DataFieldVM(BaseModel):
    DataFieldId: int = Field(alias="datafieldId")
    DisplayName: str = Field(alias="display")
    Code: str = Field(alias="code")
    SolrField: str = Field(alias="solrfield")
    Sequence: int = Field(alias="sequence")
    Category: str = Field(alias="category")
    CategoryId: int = Field(alias="categoryid")
    IsActive: bool = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
