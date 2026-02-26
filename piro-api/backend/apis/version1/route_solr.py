from timeit import default_timer as timer
from typing import Annotated, List
from core.auth_bearer import JWTBearer
from core.config import settings
from core.security_user import (
    get_current_user_id,
    get_current_user_nuid,
    get_current_user_role,
    get_current_user_attest,
)
from db.repository.auditTrailSearch import create_audit_search
from db.session import get_db, get_solr
from fastapi import APIRouter, Depends
from pysolr import Solr
from pytest import Session
from solr.repository.piro import (
    build_query_display,
    facet_get,
    get_Index_Date,
    search_Q,
    search_total,
    suggest_get,
)
from viewmodel.solr.facet import FacetVM
from viewmodel.solr.keyvalue import SuggestVM
from viewmodel.solr.search import (
    SearchInputVM,
    SearchOutputVM,
    AdvSearchInputVM,
    AdvSearchVM,
)
from core.security_util import SecurityUtil
from core.search_util import filter_str_object
from core.exception_util import PIROException
from viewmodel.solr.facet import FacetData

router = APIRouter()


@router.post(
    "/validateadvsearch",
    dependencies=[Depends(JWTBearer())],
    response_model=AdvSearchVM,
)
async def validateadvsearch(
    input_val: AdvSearchInputVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_userid: Annotated[str, Depends(get_current_user_id)],
    current_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
    solr: Solr = Depends(get_solr),
):
    adv_filter = ""
    try:
        if input_val.advfields == "{}" or input_val.advfields == "":
            return {"result": False, "filter": adv_filter}

        adv_filter = filter_str_object(input_val.advfields)
        return {"result": True, "filter": adv_filter}
    except PIROException as error:
        return {"result": False, "message": str(error)}


@router.post(
    "/search",
    dependencies=[Depends(JWTBearer())],
    response_model=SearchOutputVM,
)
async def search_solr(
    input_val: SearchInputVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_userid: Annotated[str, Depends(get_current_user_id)],
    current_role: Annotated[str, Depends(get_current_user_role)],
    current_is_attest: Annotated[bool, Depends(get_current_user_attest)],
    db: Session = Depends(get_db),
    solr: Solr = Depends(get_solr),
):
    """Primary search route.  Queries Solr."""

    start = timer()
    adv_filter = filter_str_object(input_val.advfields)
    docs = search_Q(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        sortBy=input_val.sortby,
        sortOrder=input_val.sortorder,
        page=input_val.page,
        count=0,
        db=db,
        solr=solr,
        finalRtf=True,
    )
    end = timer()

    # Save  Audit data
    create_audit_search(
        userId=current_userid,
        user=current_user,
        searchQuery=docs["query"],
        searchDisplay=build_query_display(input_arr=input_val.fields),
        searchUrl=input_val.url,
        advQuery=input_val.advfields,
        mrn=input_val.mrn,
        caseIds=docs["caseIds"],
        total=docs["total"],
        exeuteTime=(end - start),
        db=db,
    )
    for doc in docs["items"]:
        SecurityUtil.search(doc, current_role, current_is_attest)

    return docs


@router.get("/lastdataupdated")
async def last_data_updated(
    solr: Solr = Depends(get_solr),
):
    index_date = get_Index_Date(solr=solr)

    return index_date


@router.post(
    "/suggestcomment",
    dependencies=[Depends(JWTBearer())],
    response_model=List[SuggestVM],
)
async def suggest_comment_solr(
    input_val: str,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
):
    terms = await suggest_get(
        input_val=input_val,
        suggest=settings.SOLR_SUGGEST_COMMENT,
        suggester=settings.SOLR_SUGGESTER_COMMENT,
    )
    return terms


@router.post(
    "/suggeststaff",
    dependencies=[Depends(JWTBearer())],
    response_model=List[SuggestVM],
)
async def suggest_staff_solr(
    input_val: str,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
):
    terms = await suggest_get(
        input_val=input_val,
        suggest=settings.SOLR_SUGGEST_STAFF,
        suggester=settings.SOLR_SUGGESTER_STAFF,
    )
    return terms


@router.post(
    "/suggestcase",
    dependencies=[Depends(JWTBearer())],
    response_model=List[SuggestVM],
)
async def suggest_case_solr(
    input_val: str,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
):
    terms = await suggest_get(
        input_val=input_val,
        suggest=settings.SOLR_SUGGEST_CASE,
        suggester=settings.SOLR_SUGGESTER_CASE,
    )
    return terms


@router.post(
    "/facet", dependencies=[Depends(JWTBearer())], response_model=FacetVM
)
async def search_facet(
    input_val: SearchInputVM,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    solr: Solr = Depends(get_solr),
    db: Session = Depends(get_db),
):  # noqa:E501
    adv_filter = filter_str_object(input_val.advfields)
    facetMalignant = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="annotationmalignant",
        solr=solr,
        db=db,
    )
    facetGender = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="gender",
        solr=solr,
        db=db,
    )
    facetRegion = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="region",
        solr=solr,
        db=db,
    )
    facetCaseTypeCategory = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="casetypecategory",
        solr=solr,
        db=db,
    )
    facetReviewType = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="reviewtype",
        solr=solr,
        db=db,
    )
    specialty = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="specialty",
        solr=solr,
        db=db,
    )
    mrn = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="mrn",
        solr=solr,
        db=db,
        recordlimit=5,
        minCount=1,
    )
    patientname = facet_get(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        facet="patientname",
        solr=solr,
        db=db,
        recordlimit=5,
        minCount=1,
    )  # noqa:E501
    filterTotal = search_total(
        input_arr=input_val.fields,
        input_adv=adv_filter,
        mrn=input_val.mrn,
        solr=solr,
        db=db,
    )

    # cohort counts
    cohortData: List[FacetData] = []
    if input_val.cohortIds is not None:
        for cohortId in input_val.cohortIds:
            filterTotalCohort = search_total(
                input_arr=input_val.fields,
                input_adv=adv_filter,
                mrn=input_val.mrn,
                solr=solr,
                db=db,
                cohortId=cohortId,
            )
            cohortData.append(FacetData(key=cohortId, val=filterTotalCohort))

    return {
        "annotationmalignant": facetMalignant,
        "gender": facetGender,
        "region": facetRegion,
        "casetypecategory": facetCaseTypeCategory,
        "reviewtype": facetReviewType,
        "specialty": specialty,
        "mrn": mrn,
        "patientname": patientname,
        "filterTotal": filterTotal,
        "cohorts": cohortData,
    }


@router.get("/filterdata", dependencies=[Depends(JWTBearer())])
async def filter_details():
    data = [
        {
            "name": "All Text Fields",
            "type": "text",
            # "value": "final;comment;addend;microscopic",
            "value": "final;comment;addend",
            "show": "true",
            "placeholder": "Search text across all comment fields",
            "color": "#A52A2A",
        },
        {
            "name": "Final Diagnosis",
            "type": "text",
            "value": "final",
            "show": "true",
            "color": "#E1C16E",
        },
        {
            "name": "Diagnostic Comment",
            "type": "text",
            "value": "comment",
            "show": "true",
            "color": "#DAA06D",
        },
        {
            "name": "Addendum",
            "type": "text",
            "value": "addend",
            "show": "true",
        },
        {
            "name": "Synoptic Report",
            "type": "text",
            "value": "synoptic",
            "show": "true",
            "color": "#800020",
        },
        {
            "name": "Intraoperative Diagnosis",
            "type": "text",
            "value": "intraop",
            "show": "true",
            "color": "#E97451",
        },
        {
            "name": "Gross Description",
            "type": "text",
            "value": "gross",
            "show": "true",
            "color": "#6E260E",
        },
        {
            "name": "Resident Details",
            "type": "text",
            "value": "resident",
            "show": "true",
            "color": "#C19A6B",
        },
        {
            "name": "Clinical Details",
            "type": "text",
            "value": "clinical",
            "show": "true",
            "color": "#954535",
        },
        # {
        #     "name": "Microscopic Description",
        #     "type": "text",
        #     "value": "microscopic",
        #     "show": "true",
        #     "color": "#6B8E23",
        # },
        {
            "name": "Pathologist",
            "type": "suggest",
            "value": "staffname",
            "show": "true",
            "color": "#966919",
        },
        {
            "name": "Collection Date",
            "type": "daterange",
            "value": "collectiondate",
            "show": "true",
            "color": "#C4A484",
        },
        {
            "name": "Patient MRN",
            "type": "text",
            "value": "mrn",
            "show": "true",
            "placeholder": "Search patient MRN",
            "color": "#6F4E37",
        },
        {
            "name": "Case Number",
            "type": "suggest",
            "value": "casenumber",
            "show": "true",
            "placeholder": "Select case or Include * for partial search, "
            "e.g. SW-10*",
            "color": "#CD7F32",
        },
        {
            "name": "Related Cases by Case Number",
            "type": "suggest",
            "value": "patcasenumber",
            "show": "true",
            "placeholder": "Select case , "
            "e.g. C22-037763. Fetches all the cases for patient.",
            "color": "#CD7032",
        },
        {
            "name": "Cohort",
            "type": "category",
            "value": "cohort",
            "show": "true",
            "color": "#84A484",
        },
        {
            "name": "Patient Age",
            "type": "category",
            "options": [
                {"name": "0-30", "value": "0-30"},
                {"name": "31-40", "value": "31-40"},
                {"name": "41-50", "value": "41-50"},
                {"name": "51-60", "value": "51-60"},
                {"name": "61-70", "value": "61-70"},
                {"name": "Other", "value": "Other"},
            ],
            "value": "casepatientage",
            "show": "false",
            "color": "#7B3F00",
        },
        {
            "name": "Patient Age",
            "type": "slider",
            "value": "casepatientageyears",
            "show": "false",
            "color": "#D27D2D",
        },
        {
            "name": "Patient Gender",
            "type": "category",
            "options": [
                {"name": "Female", "value": "Female"},
                {"name": "Male", "value": "Male"},
            ],
            "value": "gender",
            "show": "false",
            "color": "#834333",
        },
        {
            "name": "Annotation Malignant",
            "type": "category",
            "options": [
                {"name": "Positive", "value": "Positive"},
                {"name": "Negative", "value": "Negative"},
            ],
            "value": "annotationmalignant",
            "show": "false",
            "color": "#534333",
        },
        {
            "name": "Case Type",
            "type": "category",
            "options": [
                {"name": "Autopsy", "value": "Autopsy"},
                {"name": "Bone marrow", "value": "Bone marrow"},
                {"name": "Cytology", "value": "Cytology"},
                {"name": "Surgical Pathology", "value": "Surgical Pathology"},
                {"name": "Flow Cytometry", "value": "Flow Cytometry"},
            ],
            "value": "casetypecategory",
            "show": "false",
            "color": "#CD7F32",
        },
        {
            "name": "Consultation Type",
            "type": "category",
            "options": [
                {"name": "Routine case", "value": "Routine"},
                {"name": "Consulting", "value": "Consult"},
                {"name": "Outside Review", "value": "Outside Review"},
            ],
            "value": "reviewtype",
            "show": "false",
            "color": "#988558",
        },
        {
            "name": "Region",
            "type": "category",
            "options": [
                {"name": "Akron", "value": "Akron"},
                {"name": "Florida", "value": "Florida"},
                {"name": "Indian River", "value": "Indian River"},
                {"name": "Mercy", "value": "Mercy"},
                {"name": "NE Ohio", "value": "NE Ohio"},
                {"name": "Ohio", "value": "Ohio"},
                {"name": "Other", "value": "Other"},
            ],
            "value": "region",
            "show": "false",
            "color": "#C19A6B",
        },
        {
            "name": "Specialty",
            "type": "category",
            "options": [
                {"name": "1 Derm", "value": "1 Derm"},
                {"name": "2 Derm", "value": "2 Derm"},
                {"name": "3 Derm", "value": "3 Derm"},
                {"name": "Breast Biopsy", "value": "Breast Biopsy"},
                {"name": "Breast Large", "value": "Breast Large"},
                {"name": "Cardiac", "value": "Cardiac"},
                {"name": "Consult", "value": "Consult"},
                {"name": "Cyto Non-Gyn", "value": "Cyto Non-Gyn"},
                {"name": "Eye", "value": "Eye"},
                {
                    "name": "Foreign Body/Hardware",
                    "value": "Foreign Body/Hardware",
                },
                {"name": "GI Large", "value": "GI Large"},
                {"name": "GI Small", "value": "GI Small"},
                {"name": "GU ePath", "value": "GU ePath"},
                {"name": "GU Large", "value": "GU Large"},
                {"name": "GU Small", "value": "GU Small"},
                {"name": "GYN Biopsy", "value": "GYN Biopsy"},
                {"name": "GYN Large", "value": "GYN Large"},
                {"name": "GYN Placenta/POC", "value": "GYN Placenta/POC"},
                {"name": "Head & Neck 1", "value": "Head & Neck 1"},
                {"name": "Head & Neck 2", "value": "Head & Neck 2"},
                {"name": "Hematology", "value": "Hematology"},
                {"name": "Hepatobiliary", "value": "Hepatobiliary"},
                {"name": "JMCKENNEY", "value": "JMCKENNEY"},
                {"name": "Lymphoma 1", "value": "Lymphoma 1"},
                {"name": "Lymphoma 2", "value": "Lymphoma 2"},
                {"name": "Medical Kidney", "value": "Medical Kidney"},
                {"name": "Neuro 1", "value": "Neuro 1"},
                {"name": "Neuro 2", "value": "Neuro 2"},
                {"name": "Oral/Maxillofacial", "value": "Oral/Maxillofacial"},
                {"name": "Orthopedic", "value": "Orthopedic"},
                {"name": "Other", "value": "Other"},
                {"name": "Pulmonary Biopsy", "value": "Pulmonary Biopsy"},
                {"name": "Pulmonary Large", "value": "Pulmonary Large"},
                {"name": "Reference GI", "value": "Reference GI"},
                {"name": "Soft Tissue", "value": "Soft Tissue"},
            ],
            "value": "specialty",
            "show": "false",
            "color": "#A95C68",
        },
        {
            "name": "Concentriq",
            "type": "category",
            "options": [
                {"name": "Yes", "value": "Concentriq(Yes)"},
                {"name": "No", "value": "Concentriq(No)"},
            ],
            "value": "isconcentriq",
            "show": "false",
            "color": "#333F83",
        },
    ]
    return data


@router.get("/filteradvanceddata", dependencies=[Depends(JWTBearer())])
async def filter_advanced_details():
    # "collectionDate": {"name": 'Collection Date', "type": 'date', "operators": ['=', '<=', '>=']},
    data = {
        "mrn": {
            "name": "MRN #",
            "type": "string",
            "operators": ["="],
        },
        "casenumber": {
            "name": "Case Number",
            "type": "string",
            "operators": ["="],
        },
        "final": {
            "name": "Final Diagnosis",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "comment": {
            "name": "Diagnostic Comment",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "addend": {
            "name": "Addendum",
            "type": "string",
            "operators": ["contains", "not"],
        },
        # "microscopic": {
        #     "name": "Microscopic Description",
        #     "type": "string",
        #     "operators": ["contains", "not"],
        # },
        "synoptic": {
            "name": "Synoptic Report",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "intraop": {
            "name": "Intraoperative Diagnosis",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "gross": {
            "name": "Gross Description",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "resident": {
            "name": "Resident Details",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "clinical": {
            "name": "Clinical Details",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "pathologist": {
            "name": "Pathologist",
            "type": "string",
            "operators": ["contains", "not"],
        },
        "collectiondate": {
            "name": "Collection Date",
            "type": "date",
            "operators": ["=", "!=", ">=", "=<"],
        },
        "casepatientageyears": {
            "name": "Patient Age",
            "type": "number",
            "operators": ["=", "!=", ">=", "=<"],
        },
        "gender": {
            "name": "Patient Gender",
            "type": "category",
            "options": [
                {"name": "Male", "value": "Male"},
                {"name": "Female", "value": "Female"},
            ],
            "operators": ["in", "not in", "=", "!="],
        },
        "annotationmalignant": {
            "name": "Annotation Malignant",
            "type": "category",
            "options": [
                {"name": "Positive", "value": "Positive"},
                {"name": "Negative", "value": "Negative"},
            ],
            "operators": ["in", "not in", "=", "!="],
        },
        "casetypecategory": {
            "name": "Case Type",
            "type": "category",
            "options": [
                {"name": "Autopsy", "value": "Autopsy"},
                {"name": "Bone marrow", "value": "Bone marrow"},
                {"name": "Surgical Pathology", "value": "Surgical Pathology"},
                {"name": "Cytology", "value": "Cytology"},
            ],
            "operators": ["in", "not in", "=", "!="],
        },
        "reviewtype": {
            "name": "Consultation Type",
            "type": "category",
            "options": [
                {"name": "Routine case", "value": "Routine"},
                {"name": "Consulting", "value": "Consult"},
                {"name": "Outside Review", "value": "Outside Review"},
            ],
            "operators": ["in", "not in", "=", "!="],
        },
        "region": {
            "name": "Region",
            "type": "category",
            "options": [
                {"name": "Akron", "value": "Akron"},
                {"name": "Florida", "value": "Florida"},
                {"name": "Indian River", "value": "Indian River"},
                {"name": "Mercy", "value": "Mercy"},
                {"name": "NE Ohio", "value": "NE Ohio"},
                {"name": "Ohio", "value": "Ohio"},
                {"name": "Other", "value": "Other"},
            ],
            "operators": ["in", "not in", "=", "!="],
        },
        "specialty": {
            "name": "Specialty",
            "type": "category",
            "options": [
                {"name": "1 Derm", "value": "1 Derm"},
                {"name": "2 Derm", "value": "2 Derm"},
                {"name": "3 Derm", "value": "3 Derm"},
                {"name": "Breast Biopsy", "value": "Breast Biopsy"},
                {"name": "Breast Large", "value": "Breast Large"},
                {"name": "Cardiac", "value": "Cardiac"},
                {"name": "Consult", "value": "Consult"},
                {"name": "Cyto Non-Gyn", "value": "Cyto Non-Gyn"},
                {"name": "Eye", "value": "Eye"},
                {
                    "name": "Foreign Body/Hardware",
                    "value": "Foreign Body/Hardware",
                },
                {"name": "GI Large", "value": "GI Large"},
                {"name": "GI Small", "value": "GI Small"},
                {"name": "GU ePath", "value": "GU ePath"},
                {"name": "GU Large", "value": "GU Large"},
                {"name": "GU Small", "value": "GU Small"},
                {"name": "GYN Biopsy", "value": "GYN Biopsy"},
                {"name": "GYN Large", "value": "GYN Large"},
                {"name": "GYN Placenta/POC", "value": "GYN Placenta/POC"},
                {"name": "Head & Neck 1", "value": "Head & Neck 1"},
                {"name": "Head & Neck 2", "value": "Head & Neck 2"},
                {"name": "Hematology", "value": "Hematology"},
                {"name": "Hepatobiliary", "value": "Hepatobiliary"},
                {"name": "JMCKENNEY", "value": "JMCKENNEY"},
                {"name": "Lymphoma 1", "value": "Lymphoma 1"},
                {"name": "Lymphoma 2", "value": "Lymphoma 2"},
                {"name": "Medical Kidney", "value": "Medical Kidney"},
                {"name": "Neuro 1", "value": "Neuro 1"},
                {"name": "Neuro 2", "value": "Neuro 2"},
                {"name": "Oral/Maxillofacial", "value": "Oral/Maxillofacial"},
                {"name": "Orthopedic", "value": "Orthopedic"},
                {"name": "Other", "value": "Other"},
                {"name": "Pulmonary Biopsy", "value": "Pulmonary Biopsy"},
                {"name": "Pulmonary Large", "value": "Pulmonary Large"},
                {"name": "Reference GI", "value": "Reference GI"},
                {"name": "Soft Tissue", "value": "Soft Tissue"},
            ],
            "operators": ["in", "not in", "=", "!="],
        },
        "isconcentriq": {
            "name": "Is Concentriq",
            "type": "category",
            "options": [
                {"name": "Yes", "value": "true"},
                {"name": "No", "value": "false"},
            ],
            "operators": ["="],
        },
    }
    return data
