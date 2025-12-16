from apis.version1 import (
    route_case,
    route_casecomment,
    route_commentType,
    route_cohort,
    route_ethnicity,
    route_etl_log,
    route_gender,
    route_hospital,
    route_patient,
    route_profile,
    route_race,
    route_region,
    route_role,
    route_slide_request,
    route_search,
    route_searchRequest,
    route_searchRequestStatus,
    route_solr,
    route_specimenSource,
    route_specimenType,
    route_tag,
    route_tagcase,
    route_token,
    route_user,
    route_report,
    route_searchRequestDataField,
    route_annotation,
    route_concentriq,
)
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(route_token.router, prefix="/token", tags=["Token"])
api_router.include_router(route_solr.router, prefix="/solr", tags=["Solr"])
api_router.include_router(
    route_profile.router, prefix="/profile", tags=["Profile"]
)
api_router.include_router(
    route_casecomment.router, prefix="/casecomment", tags=["Case Comments"]
)
api_router.include_router(
    route_case.router, prefix="/case", tags=["Case Info"]
)
api_router.include_router(route_tag.router, prefix="/tag", tags=["Tag"])
api_router.include_router(
    route_tagcase.router, prefix="/tagcase", tags=["Tag"]
)
api_router.include_router(
    route_search.router, prefix="/search", tags=["Search"]
)
api_router.include_router(
    route_searchRequestDataField.router,
    prefix="/searchrequestfield",
    tags=["Search Request Data Field"],
)
api_router.include_router(
    route_searchRequest.router,
    prefix="/searchrequest",
    tags=["Search Request"],
)
api_router.include_router(
    route_gender.router, prefix="/gender", tags=["Gender"]
)
api_router.include_router(route_user.router, prefix="/user", tags=["User"])
api_router.include_router(route_role.router, prefix="/role", tags=["Role"])
api_router.include_router(
    route_specimenType.router, prefix="/specimentype", tags=["Specimen Type"]
)
api_router.include_router(
    route_specimenSource.router,
    prefix="/specimensource",
    tags=["Specimen Sources"],
)
api_router.include_router(
    route_searchRequestStatus.router,
    prefix="/searchrequeststatus",
    tags=["Search Request Status"],
)
api_router.include_router(
    route_region.router, prefix="/region", tags=["Region"]
)
api_router.include_router(route_race.router, prefix="/race", tags=["Race"])

api_router.include_router(
    route_hospital.router, prefix="/hospital", tags=["Hospital"]
)
api_router.include_router(
    route_ethnicity.router, prefix="/ethnicity", tags=["Ethnicity"]
)
api_router.include_router(
    route_commentType.router, prefix="/commenttype", tags=["Comment Types"]
)
api_router.include_router(
    route_etl_log.router, prefix="/etllog", tags=["Etl Logs"]
)
api_router.include_router(
    route_report.router, prefix="/report", tags=["Reports"]
)
api_router.include_router(
    route_patient.router, prefix="/patient", tags=["Patients"]
)
api_router.include_router(
    route_cohort.router, prefix="/cohort", tags=["Cohorts"]
)
api_router.include_router(
    route_annotation.router, prefix="/annotation", tags=["Annotations"]
)
api_router.include_router(
    route_concentriq.router, prefix="/concentriq", tags=["Concentriq"]
)
api_router.include_router(
    route_slide_request.router,
    prefix="/sliderequest",
    tags=["Slide Requests"],
)
