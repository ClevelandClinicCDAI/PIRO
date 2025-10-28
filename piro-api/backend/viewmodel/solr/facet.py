import math
from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator


class FacetData(BaseModel):
    key: str
    val: int


class FacetBaseVM(BaseModel):
    facet_ranges: Optional[Any]
    facet_fields: Optional[Any] = Field(exclude=True)
    facets: List[FacetData] = []
    field: str = ""

    def transform(cls, values, facetdata):
        facets: List[FacetData] = []
        for index, item in enumerate(facetdata):
            if index % 2 == 0:
                facets.append(FacetData(key=item, val=0))
            else:
                res: int = index / 2
                facets[math.floor(res)].val = item

        values["facets"] = facets


class FacetMalignantVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "annotationmalignant"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetGenderVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "gender"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetRegionVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "region"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetCaseTypeVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "casetypecategory"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetSpecialtyVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "specialty"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetReviewTypeVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "reviewtype"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CasePatientAgeVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "casepatientage"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetMrnVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "mrn"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetPatientVM(FacetBaseVM):
    @root_validator
    def transform_data(cls, values):
        FacetBaseVM.field = "patientname"

        if "facet_fields" in values:
            dat = values["facet_fields"]
            FacetBaseVM.transform(cls, values, dat[FacetBaseVM.field])
        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class FacetVM(BaseModel):
    gender: FacetGenderVM
    region: FacetRegionVM
    annotationmalignant: FacetMalignantVM
    casetypecategory: FacetCaseTypeVM
    reviewtype: FacetReviewTypeVM
    specialty: FacetSpecialtyVM
    mrn: FacetMrnVM
    patientname: FacetPatientVM
    filterTotal: int
    cohorts: List[FacetData] = []
