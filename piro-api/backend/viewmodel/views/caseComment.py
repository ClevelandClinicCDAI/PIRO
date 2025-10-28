from core.string_util import StringUtil
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional


class CaseCommentInputVM(BaseModel):
    caseid: int


class CaseCommentVM(BaseModel):
    Id: str = Field(alias="id")
    CaseId: int = Field(alias="caseid")
    CommentType: str = Field(alias="type")
    CommentText: str = Field(alias="text")
    SourceCommentType: str = Field(alias="sourcetype")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True

    @root_validator
    def transform(cls, values):
        if values is None:
            return

        if "CommentText" in values:
            input = values["CommentText"]

            if input is not None and StringUtil.isNotBlank(input):
                # remove additional occurances of {\\rtf1
                if input.startswith("{\\rtf1"):
                    input = input.replace("{\\rtf1", "")
                    input = "{\\rtf1" + input

                    values["CommentText"] = input
        return values


class CaseCommentSynopticVM(BaseModel):
    Id: int = Field(alias="id")
    SynopticId: int = Field(alias="synopticId")
    Name: str = Field(alias="name")
    DataType: str = Field(alias="dataType")
    ContextName: str = Field(alias="context")
    ContexHierarchy: str = Field(alias="hierarchy")
    ValueLine: str = Field(alias="vaueLine")
    Level1: str = Field(alias="level1")
    Level2: str = Field(alias="level2")
    Level3: str = Field(alias="level3")
    Level4: str = Field(alias="level4")
    Level5: str = Field(alias="level5")
    Level6: str = Field(alias="level6")
    ElementName: str = Field(alias="elementName")
    ElementValue: str = Field(alias="elementValue")
    ElementComment: str = Field(alias="elementComment")
    CommentLine: int = Field(alias="commentLine")

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseCommentSynopticReportVM(BaseModel):
    id: int
    level: int
    isSection: bool
    text: str
    value: str
    comment: str
    hierarchy: str
    subtext: Optional[str] = ""
    subtext2: Optional[str]

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class CaseCommentSynopticReport:
    def __init__(
        self,
        id,
        level,
        isSection,
        text,
        subtext,
        subtext2,
        value,
        comment,
        hierarchy,
    ):
        self.id = id
        self.level = level
        self.isSection = isSection
        self.text = text
        self.subtext = subtext
        self.subtext2 = subtext2
        self.value = value
        self.comment = comment
        self.hierarchy = hierarchy


class CaseSynopticVM(BaseModel):
    synoptic: List[CaseCommentSynopticVM]
    patient: List[CaseCommentSynopticVM]
    report: List[CaseCommentSynopticReportVM]
    parsed: bool = False
