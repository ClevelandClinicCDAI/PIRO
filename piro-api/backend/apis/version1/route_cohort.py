from typing import Annotated, List

# from db.repository.auditTrailSearchRequest import create_audit_search_request

from core.auth_bearer import JWTBearer
from core.constants import Constants
from core.security_user import get_current_user_id, get_current_user_nuid
from db.repository.cohort import (
    create_new_cohort,
    get_cohort_data,
    delete_cohort,
    update_cohort,
    get_user_cohorts,
    list_cohort,
)
from db.repository.cohortPatient import (
    create_new_cohortpatient_excel,
    create_new_cohortcase_excel,
    get_cohortpatients,
    delete_cohortpatient,
    process_cohortpatient,
    process_cohortpatient_case,
)
from db.repository.cohortcase import (
    delete_cohortcase,
    process_cohortcase,
    get_cohortcases,
)


from db.session import get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException
from fastapi.responses import FileResponse
from solr.repository.excel_cohort import (
    create_excel_patient_mrn,
    create_excel_patient_epi,
    create_excel_case,
    read_excel,
    create_mrn_template,
    create_case_template,
    create_eid_template,
)
from sqlalchemy.orm import Session
from viewmodel.cohort import CohortVMUpdate, CohortVM, CohortFacetVM
from airflow.cohort_api import trigger_cohort_job

router = APIRouter()


@router.post(
    "/create",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def create_cohort_file(
    # search_request: SearchRequestVMCreate,
    name: Annotated[str, Form()],
    desc: Annotated[str, Form()],
    disease: Annotated[str, Form()],
    cohortId: Annotated[str, Form()],
    display: Annotated[bool, Form()],
    dataType: Annotated[str, Form()],
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
    file=File(...),  # noqa B008
):
    if cohortId is None or cohortId == "":
        raise HTTPException(status_code=510, detail="cohortId is empty")

    if file:
        # Read the excel file and load the data
        cohort_request: CohortVMUpdate = CohortVMUpdate()
        cohort_request.name = name
        cohort_request.desc = desc
        cohort_request.cohortId = -1
        cohort_request.fileData = file.file.read()
        cohort_request.type = dataType
        cohort_data = read_excel(cohort_request)

    if cohortId == "-1":
        cohort_new = create_new_cohort(
            name=name,
            desc=desc,
            disease=disease,
            display=display,
            dataType=dataType,
            userId=current_user_id,
            user=current_user,
            db=db,
        )
        cohortId = cohort_new.CohortId
    else:
        cohort_new = update_cohort(
            cohortId=cohortId,
            name=name,
            desc=desc,
            disease=disease,
            display=display,
            userId=current_user_id,
            user=current_user,
            db=db,
        )
    if file:
        delete_cohortpatient(int(cohortId), db)
        delete_cohortcase(int(cohortId), db)

        if (
            dataType == Constants.CohortTypeMrn
            or dataType == Constants.CohortTypeEpi
        ):
            result = create_new_cohortpatient_excel(
                cohortId=int(cohortId),
                input=cohort_data,
                type=dataType,
                user=current_user,
                db=db,
            )
            if not result:
                return False
            result = process_cohortpatient(cohortId=int(cohortId), db=db)
            if not result:
                return False
            result = process_cohortpatient_case(cohortId=int(cohortId), db=db)
            if not result:
                return False
        elif dataType == Constants.CohortTypeCase:
            result = create_new_cohortcase_excel(
                cohortId=int(cohortId),
                input=cohort_data,
                user=current_user,
                db=db,
            )
            if not result:
                return False
            result = process_cohortcase(cohortId=int(cohortId), db=db)
            if not result:
                return False
        result = trigger_cohort_job(cohortId=cohortId)
        if not result:
            return False
    else:
        raise HTTPException(status_code=510, detail="File is empty")
    return True


@router.post(
    "/update",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def create_cohort_lite(
    # search_request: SearchRequestVMCreate,
    name: Annotated[str, Form()],
    desc: Annotated[str, Form()],
    disease: Annotated[str, Form()],
    cohortId: Annotated[str, Form()],
    display: Annotated[bool, Form()],
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    if cohortId is None or cohortId == "":
        raise HTTPException(status_code=510, detail="cohortId is empty")

    update_cohort(
        cohortId=cohortId,
        name=name,
        desc=desc,
        disease=disease,
        display=display,
        userId=current_user_id,
        user=current_user,
        db=db,
    )
    return True


@router.get(
    "/all",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
    response_model=List[CohortVM],
)
async def cohort_all(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    cohorts = get_user_cohorts(userId=current_user_id, db=db)
    return cohorts


@router.get(
    "/facetlist",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                    Constants.RoleSecurityAdmin,
                ]
            )
        )
    ],
    response_model=List[CohortFacetVM],
)
async def facet_list(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    cohorts = list_cohort(userId=current_user_id, db=db)
    return cohorts


@router.delete(
    "/delete/{cohortId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def delete(
    cohortId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    if delete_cohort(cohortId=cohortId, db=db):
        delete_cohortcase(cohortId=cohortId, db=db)
        delete_cohortpatient(cohortId=cohortId, db=db)
    return True


@router.get(
    "/export/{cohortId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def export(
    cohortId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    cohort = get_cohort_data(cohortId=cohortId, db=db)

    if cohort.dataType == Constants.CohortTypeMrn:
        data = get_cohortpatients(cohortId=cohortId, db=db)

        file = create_excel_patient_mrn(
            cohortId=cohortId, cohort=cohort, data=data
        )
    elif cohort.dataType == Constants.CohortTypeEpi:
        data = get_cohortpatients(cohortId=cohortId, db=db)

        file = create_excel_patient_epi(
            cohortId=cohortId, cohort=cohort, data=data
        )
    else:
        data = get_cohortcases(cohortId=cohortId, db=db)

        file = create_excel_case(cohortId=cohortId, cohort=cohort, data=data)
    headers = {"Content-Disposition": f'attachment; filename={file["file"]}'}
    if file["path"].endswith(".xlsx") is False:
        raise HTTPException(status_code=510, detail="File path is illegal")

    return FileResponse(file["path"], headers=headers)


@router.get(
    "/template/mrn",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def export_template_mrn(db: Session = Depends(get_db)):
    file = create_mrn_template()
    headers = {"Content-Disposition": f'attachment; filename={file["file"]}'}
    if file["path"].endswith(".xlsx") is False:
        raise HTTPException(status_code=510, detail="File path is illegal")

    return FileResponse(file["path"], headers=headers)


@router.get(
    "/template/case",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def export_template_case(db: Session = Depends(get_db)):
    file = create_case_template()
    headers = {"Content-Disposition": f'attachment; filename={file["file"]}'}
    if file["path"].endswith(".xlsx") is False:
        raise HTTPException(status_code=510, detail="File path is illegal")

    return FileResponse(file["path"], headers=headers)


@router.get(
    "/template/eid",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def export_template_eid(db: Session = Depends(get_db)):
    file = create_eid_template()
    headers = {"Content-Disposition": f'attachment; filename={file["file"]}'}
    if file["path"].endswith(".xlsx") is False:
        raise HTTPException(status_code=510, detail="File path is illegal")

    return FileResponse(file["path"], headers=headers)


@router.get(
    "/get/{cohortId}",
    dependencies=[
        Depends(
            JWTBearer(
                [
                    Constants.RoleAdmin,
                    Constants.RoleDemoAdmin,
                    Constants.RoleAnalyst,
                    Constants.RoleUser,
                ]
            )
        )
    ],
)
async def get(
    cohortId: int,
    current_user: Annotated[str, Depends(get_current_user_nuid)],
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    cohort = get_cohort_data(cohortId=cohortId, db=db)
    return cohort
