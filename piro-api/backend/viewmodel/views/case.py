from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CaseInputVM(BaseModel):
    caseid: int


class CaseVM(BaseModel):
    CaseId: int = Field(alias="caseid")
    RefRequisitionKey: Optional[str] = Field(alias="reqkey")
    SpecimenYear: int = Field(alias="specimenyear")
    CaseNumber: Optional[str] = Field(alias="casenumber", default="")
    AccessionDate: Optional[datetime] = Field(
        alias="accessiondate", exclude=False
    )
    ReceiveDate: Optional[datetime] = Field(alias="receivedate", exclude=False)
    OverdueDate: Optional[datetime] = Field(alias="overduedate", exclude=False)
    CollectionDate: Optional[datetime] = Field(
        alias="collectiondate", exclude=False
    )
    SignoutDate: Optional[datetime] = Field(alias="signoutdate", exclude=False)
    PatientName: Optional[str] = Field(alias="name", exclude=False)
    PatientDOB: Optional[datetime] = Field(alias="dob", exclude=False)
    PatientEpi: Optional[str] = Field(alias="epi", exclude=False)
    PatientMrn: Optional[str] = Field(alias="mrn", exclude=False)
    PatientLanguage: Optional[str] = Field(alias="language", exclude=False)
    PatientEthnicity: Optional[str] = Field(alias="ethnicity", exclude=False)
    PatientGender: Optional[str] = Field(alias="gender")
    PatientDeathDate: Optional[datetime] = Field(
        alias="deceasedate", exclude=False
    )
    PatientIsDeceased: Optional[bool] = Field(
        alias="isdeceased", exclude=False
    )
    PatientRace: Optional[str] = Field(alias="race", exclude=False)
    PatientCity: Optional[str] = Field(alias="city", exclude=False)
    PatientState: Optional[str] = Field(alias="state", exclude=False)
    PatientCountry: Optional[str] = Field(alias="country", exclude=False)
    Hospital: Optional[str] = Field(alias="hospital")
    Region: Optional[str] = Field(alias="region")
    CaseStatus: Optional[str] = Field(alias="status")
    CaseType: Optional[str] = Field(alias="casetype")
    CaseTypeCategory: Optional[str] = Field(alias="casetypecategory")
    ReviewType: Optional[str] = Field(alias="reviewtype")
    Specialty: Optional[str] = Field(alias="speciality")
    SpecialtyCode: Optional[str] = Field(alias="specialitycode")
    SpecialtyCategory: Optional[str] = Field(alias="specialitycategory")
    CasePatientAge: Optional[str] = Field(alias="agerange")
    CasePatientAgeYears: Optional[int] = Field(alias="age")
    AnnotationMalignant: Optional[str] = Field(alias="annotationmalignant")
    IsEpicMigrated: Optional[bool] = Field(alias="ismigrated")
    IsEpic: bool = Field(alias="isepic")
    IsCopath: bool = Field(alias="iscopath")
    CreateDate: Optional[datetime] = Field(alias="createdon")
    UpdateDate: Optional[datetime] = Field(alias="updatedon")
    IsConcentriq: bool = Field(alias="isconcentriq")
    CaseConcentriqId: Optional[int] = Field(alias="concentriqid")
    CaseConcentriqUrl: Optional[str] = Field(alias="concentriqurl")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseCommentVM(BaseModel):
    Id: int = Field(alias="id")
    CaseId: int = Field(alias="caseid")
    CommentTypeId: int = Field(alias="commenttypeid")
    CommentType: str = Field(alias="commenttype")
    CommentCount: int = Field(alias="count")
    CommentText: str = Field(alias="comment")
    CreateDate: datetime = Field(alias="createdon")
    UpdateDate: str = Field(alias="updatedon")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseStaffVM(BaseModel):
    CaseStaffId: int = Field(alias="casestaffid")
    CaseId: int = Field(alias="caseid")
    StaffId: int = Field(alias="staffid")
    FullName: str = Field(alias="name")
    UserId: str = Field(alias="userid")
    StartDate: str = Field(alias="startdate")
    EndDate: str = Field(alias="enddate")
    CreateDate: datetime = Field(alias="createdon")
    UpdateDate: str = Field(alias="updatedon")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseInterpreteVM(BaseModel):
    InterpreterId: int = Field(alias="interpreterid")
    CaseId: int = Field(alias="caseid")
    Interpreter: str = Field(alias="name")
    ProcedureCategory: str = Field(alias="category")
    CreateDate: datetime = Field(alias="createdon")
    UpdateDate: str = Field(alias="updatedon")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseSynopticSpecimenVM(BaseModel):
    CaseId: int = Field(alias="caseId")
    SpecimenId: int = Field(alias="specimenId")
    SynopticId: int = Field(alias="synopticId")
    SpecimenNum: str = Field(alias="specimen")
    SpecimenList: str = Field(alias="specimenlist")
    RecordCreateDate: datetime = Field(alias="recordDate")
    IsSpecimenLevel: bool = Field(alias="isSpecimenLevel")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseSynopticSpecimenGroupVM(BaseModel):
    SynopticId: str = Field(alias="synopticId")
    IsSpecimenLevel: bool = Field(alias="isSpecimenLevel")
    SpecimenNum: str = Field(alias="specimenGrp")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseSynopticTextVM(BaseModel):
    CaseId: int = Field(alias="caseId")
    SpecimenId: int = Field(alias="specimenId")
    SynopticId: int = Field(alias="synopticId")
    Specimen: str = Field(alias="specimen")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class ResultVM(BaseModel):
    case: CaseVM
    # caseComments: List[CaseCommentVM]
    caseStaffs: List[CaseStaffVM]
    interpreters: List[CaseInterpreteVM]
    specimens: List[CaseSynopticSpecimenVM]
    specimensGroup: List[CaseSynopticSpecimenGroupVM]
    attrExcludes: List[str]
