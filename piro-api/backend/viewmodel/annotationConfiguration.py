from pydantic import BaseModel, Field


class AnnotationConfigurationVM(BaseModel):
    AnnotationConfigurationId: int = Field(alias="annotationConfigurationId")
    AnnotationMetric: str = Field(alias="metric")
    DisplayText: str = Field(alias="display")
    UIModel: str = Field(alias="property")
    RowIndex: int = Field(alias="row")
    ColumnIndex: int = Field(alias="column")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
