from pydantic import BaseModel, Field
from typing import List, Optional


# properties required during user creation
class SearchRequestDataFieldVMCreate(BaseModel):
    searchrequestId: int
    datafieldId: int
    selected: bool


class SearchRequestDataFieldVMUpdate(SearchRequestDataFieldVMCreate):
    searchrequestdatafieldId: int


class SearchRequestDataFieldsVMUpdate(BaseModel):
    searchrequestId: int
    dataFields: List[int]


class DataFieldVM(BaseModel):
    DataFieldId: Optional[int] = Field(alias="datafieldId")
    DataFieldDisplayName: Optional[str] = Field(alias="display")
    DataFieldCode: Optional[str] = Field(alias="code")
    DataFieldSolrField: Optional[str] = Field(alias="solrfield")
    DataFieldSequence: Optional[int] = Field(alias="sequence")
    DataFieldCategorySequence: Optional[int] = Field(alias="categorysequence")
    DataFieldCategoryId: Optional[int] = Field(alias="categoryid")
    DataFieldCategoryDisplayName: Optional[str] = Field(
        alias="categorydisplay"
    )
    DataFieldCategoryCode: Optional[str] = Field(alias="categorycode")
    DataFieldIsActive: Optional[bool] = Field(alias="active")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class DataFieldCategoryVM(BaseModel):
    DataFieldCategoryId: Optional[int] = Field(alias="categoryid")
    DataFieldCategoryDisplayName: Optional[str] = Field(
        alias="categorydisplay"
    )
    DataFieldCategoryCode: Optional[str] = Field(alias="categorycode")
    DataFieldCategorySequence: Optional[int] = Field(alias="categorysequence")
    DataFieldIsActive: Optional[bool] = Field(alias="active")
    Count: Optional[int] = Field(alias="count", default=0)
    DataFields: List[List[DataFieldVM]] = Field(alias="fields")
    FieldPartition: Optional[int] = Field(alias="fieldpartition", default=1)

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class DataFieldMasterVM(BaseModel):
    DataFieldCategories: List[DataFieldCategoryVM] = Field(alias="categories")
    DataFields: List[DataFieldVM] = Field(alias="fields")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class SearchRequestDataFieldVM(DataFieldVM):
    SearchRequestDataFieldId: Optional[int] = Field(
        alias="searchrequestdatafieldId", default=-1
    )
    SearchRequestId: Optional[int] = Field(alias="searchrequestId", default=-1)
    IsSelected: Optional[bool] = Field(alias="selected")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
