from datetime import datetime
from typing import Any, List, Optional

from core.config import Settings
from core.string_util import StringUtil
from logger import logger
from pydantic import BaseModel, Field, root_validator
from striprtf.striprtf import rtf_to_text


# properties required during user creation
class SearchFilterVM(BaseModel):
    field: str
    search: str
    category: str
    andcondition: bool
    displaysingular: Optional[str]


class AdvSearchInputVM(BaseModel):
    advfields: Optional[str]


class AdvSearchVM(BaseModel):
    result: bool
    filter: Optional[str]
    message: Optional[str]


class SearchInputVM(BaseModel):
    advfields: Optional[str]
    mrn: Optional[str]
    fields: Optional[List[SearchFilterVM]]
    url: str
    sortby: str
    sortorder: str
    page: int
    cohortIds: Optional[List[int]]


class SearchDocumentBaseVM(BaseModel):
    def ParseComment(nodeInput: str, nodeOutput: str, values: Any):
        delimiter1 = "   ||||   "
        delimiter2 = "||--||"
        delimiter3 = "  "
        charLimit = 1000
        texts = []
        commentCount = values[nodeInput + "count"]
        try:
            if nodeInput in values:
                input = values[nodeInput]
                if input is not None and StringUtil.isNotBlank(input):
                    if commentCount > 1:
                        if delimiter1 in input:
                            texts = input.split(delimiter1)
                        elif delimiter2 in input:
                            texts = input.split(delimiter2)
                        elif delimiter3 in input:
                            texts = input.split(delimiter3)
                    else:
                        texts.append(input)
                    li = []
                    for text in texts:
                        try:
                            if nodeInput == "final":
                                if not text.startswith("{\\rtf1"):
                                    if len(text) > charLimit:
                                        text = text[0:charLimit] + "    ....."
                                else:
                                    # remove additional occurances of {\\rtf1
                                    text = text.replace("{\\rtf1", "")
                                    text = "{\\rtf1" + text
                            else:
                                if text.startswith("{\\rtf1"):
                                    text = rtf_to_text(text)

                                if len(text) > charLimit:
                                    text = text[0:charLimit] + "    ....."
                            li.append(text)
                        except Exception as e:
                            logger.error(
                                f"Error parsing comment. See error "
                                f"messaging: {type(e), e, e.args}"
                            )
                            li.append("Comment did not load. Error occurred.")
                    values[nodeOutput] = li
        except Exception as e:
            logger.error(f"Please see errors: {type(e), e, e.args}")
            values[nodeOutput] = []


class SearchDocumentVM(SearchDocumentBaseVM):
    collectiondate: Optional[datetime] = Field(exclude=True)
    gender: str = ""
    age: int
    epi: str = ""
    casetypecategory: str = ""
    specimenyear: str = ""
    procedurecategory: Optional[str] = ""
    signoutdate: Optional[str] = Field(exclude=False)
    receivedate: Optional[str] = Field(exclude=False)
    language: str = ""
    specimennumber: Optional[str] = Field(exclude=True)
    specimennumbers: Optional[List[str]] = []
    casenumber: str = ""
    hospital: str = ""
    accessiondate: Optional[datetime] = Field(exclude=False)
    ethnicity: str = ""
    annotationmalignant: str = ""
    ismalignant: bool = False
    importdate: Optional[datetime]
    interpreter: str = Field(exclude=True)
    interpreters: Optional[List[str]] = []
    staffname: str = Field(exclude=True)
    staffnames: Optional[List[str]] = []
    isdeceased: Optional[bool] = Field(exclude=False)
    dob: Optional[datetime] = Field(exclude=False)
    caseid: str = ""
    final: Optional[str] = Field(exclude=True)
    finaltexts: Optional[List[str]] = []
    gross: Optional[str] = Field(exclude=True)
    grosstexts: Optional[List[str]] = Field(exclude=True)
    addend: Optional[str] = Field(exclude=True)
    addendtexts: Optional[List[str]] = []
    comment: Optional[str] = Field(exclude=True)
    commenttexts: Optional[List[str]] = []
    microscopic: Optional[str] = Field(exclude=True)
    microscopictexts: Optional[List[str]] = []
    intraop: Optional[str] = Field(exclude=True)
    intraoptexts: Optional[List[str]] = []
    resident: Optional[str] = Field(exclude=True)
    residenttexts: Optional[List[str]] = []
    synoptic: Optional[str] = Field(exclude=True)
    synoptictexts: Optional[List[str]] = []
    patientname: Optional[str] = Field(exclude=False)
    patientdeathdate: Optional[datetime]
    race: str = ""
    specialty: str = ""
    mrn: str = ""
    casetype: str = ""
    overduedate: Optional[datetime] = Field(exclude=False)
    casestatus: str = ""
    region: str = ""
    specialtycode: str = ""
    addendcount: int = 0
    grosscount: int = 0
    commentcount: int = 0
    intraopcount: int = 0
    finalcount: int = 0
    synopticcount: int = 0
    residentcount: int = 0
    microscopiccount: int = 0
    isepic: bool = False
    isepicmigrated: bool = False
    iscopath: bool = False
    isconcentriq: bool = False
    concentriqid: int = 0
    concentriqurl: str = ""

    @root_validator
    def transform(cls, values):
        if values is None:
            return
        SearchDocumentBaseVM.ParseComment("gross", "grosstexts", values)
        SearchDocumentBaseVM.ParseComment("final", "finaltexts", values)
        SearchDocumentBaseVM.ParseComment("addend", "addendtexts", values)
        SearchDocumentBaseVM.ParseComment("comment", "commenttexts", values)
        SearchDocumentBaseVM.ParseComment(
            "microscopic",
            "microscopictexts",
            values,
        )
        SearchDocumentBaseVM.ParseComment("intraop", "intraoptexts", values)
        SearchDocumentBaseVM.ParseComment("resident", "residenttexts", values)
        SearchDocumentBaseVM.ParseComment("synoptic", "synoptictexts", values)

        if "staffname" in values:
            input = values["staffname"]
            if input is not None and StringUtil.isNotBlank(input):
                li = list(input.split(" | "))
                values["staffnames"] = li

        if "interpreter" in values:
            input = values["interpreter"]
            if input is not None and StringUtil.isNotBlank(input):
                li = list(input.split(" | "))
                values["interpreters"] = li

        if "specimennumber" in values:
            input = values["specimennumber"]
            if input is not None and StringUtil.isNotBlank(input):
                li = list(input.split(" | "))
                values["specimennumbers"] = li

        if "annotationmalignant" in values:
            input = values["annotationmalignant"]
            if input.lower() == "positive":
                values["ismalignant"] = True

        return values

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True


class SearchOutputVM(BaseModel):
    items: List[SearchDocumentVM]
    total: int
    pages: int
    page: int
    size: int = Settings.RECORDS_PER_PAGE

    class Config:  # to convert non dict obj to json
        orm_mode = True
        allow_population_by_field_name = True
