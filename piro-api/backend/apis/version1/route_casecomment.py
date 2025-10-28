from typing import Annotated, List
from core.security_util import SecurityUtil
from core.auth_bearer import JWTBearer
from db.repository.caseComment import (
    comment_copath,
    comment_epic,
    comment_text,
)
from db.repository.caseCommentSynoptic import (
    synoptic_patient,
    synoptic_text,
    synoptic_report,
)
from db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from viewmodel.views.caseComment import (
    CaseCommentSynopticReport,
    CaseCommentVM,
    CaseSynopticVM,
)
from core.security_user import get_current_user_role

router = APIRouter()


@router.get(
    "/text/{caseId}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[CaseCommentVM],
)
async def get_text(
    caseId: int,
    current_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    comments = comment_text(caseId=caseId, db=db)
    SecurityUtil.comment_text(comments, current_role)
    return comments


@router.get(
    "/epic/{caseId}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[CaseCommentVM],
)
async def get_epic(
    caseId: int,
    current_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    comments = comment_epic(caseId=caseId, db=db)
    SecurityUtil.comment_text(comments, current_role)
    return comments


@router.get(
    "/copath/{caseId}",
    dependencies=[Depends(JWTBearer())],
    response_model=List[CaseCommentVM],
)
async def get_copath(
    caseId: int,
    current_role: Annotated[str, Depends(get_current_user_role)],
    db: Session = Depends(get_db),
):
    comments = comment_copath(caseId=caseId, db=db)
    SecurityUtil.comment_text(comments, current_role)
    return comments


@router.get(
    "/synoptic/{synopticId}",
    dependencies=[Depends(JWTBearer())],
    response_model=CaseSynopticVM,
)
async def get_synoptic(synopticId: int, db: Session = Depends(get_db)):
    commentsSynoptic = synoptic_text(synopticId=synopticId, db=db)
    commentsPatient = synoptic_patient(synopticId=synopticId, db=db)
    level1: str = (
        "-" if len(commentsSynoptic) == 0 else commentsSynoptic[0].Level1
    )
    commentsSynopticCount = len(
        [x for x in commentsSynoptic if x.Level1 == level1]
    )
    # isLevel1: bool = (
    #     False if commentsSynopticCount == len(commentsSynoptic) else True
    # )

    level2: str = (
        "-" if len(commentsSynoptic) == 0 else commentsSynoptic[0].Level2
    )
    commentsSynopticCount = len(
        [x for x in commentsSynoptic if x.Level2 == level2]
    )
    isLevel2: bool = (
        False if commentsSynopticCount == len(commentsSynoptic) else True
    )

    level3: str = (
        "-" if len(commentsSynoptic) == 0 else commentsSynoptic[0].Level3
    )
    commentsSynopticCount = len(
        [x for x in commentsSynoptic if x.Level3 == level3]
    )
    isLevel3: bool = (
        False if commentsSynopticCount == len(commentsSynoptic) else True
    )
    report = []
    level1 = ""
    level2 = ""
    level3 = ""
    level4: str = ""
    level5: str = ""
    for data in commentsSynoptic:
        item = CaseCommentSynopticReport(0, 0, False, "", "", "", "", "", "")
        if isLevel2:
            if data.Level2 != level2:
                item.isSection = True
                item.level = 1
                item.text = data.Level2
                item.subtext = data.Level3
                # item.subtext2 = data.Level4
            elif data.Level3 != level3:
                item.isSection = False
                item.level = 2
                item.text = data.Level3
                item.subtext = data.Level4
            elif data.Level4 != level4:
                item.isSection = False
                item.level = 3
                item.text = data.Level4
                item.subtext = data.Level5
            elif data.Level5 != level5:
                item.isSection = False
                item.level = 4
                item.text = data.Level5
                item.subtext = data.Level6
                item.value = data.ElementValue
                item.comment = data.ElementComment
            else:
                item.isSection = False
                item.level = 5
                item.text = data.Level6
                item.value = data.ElementValue
                item.comment = data.ElementComment
        elif isLevel3:
            if data.Level3 != level3:
                item.isSection = True
                item.level = 1
                item.text = data.Level3
                item.subtext = data.Level4
                # item.subtext2 = data.Level5
            elif data.Level4 != level4:
                item.isSection = False
                item.level = 2
                item.text = data.Level4
                item.subtext = data.Level5
            elif data.Level5 != level5:
                item.isSection = False
                item.level = 3
                item.text = data.Level5
                item.subtext = data.Level6
                item.value = data.ElementValue
                item.comment = data.ElementComment
            else:
                item.isSection = False
                item.level = 4
                item.text = data.Level6
                item.value = data.ElementValue
                item.comment = data.ElementComment

        level1 = data.Level1
        level2 = data.Level2
        level3 = data.Level3
        level4 = data.Level4
        level5 = data.Level5

        item.id = data.Id
        item.hierarchy = data.ContexHierarchy
        report.append(item)

    return {
        "synoptic": commentsSynoptic,
        "patient": commentsPatient,
        "report": report,
    }


@router.get(
    "/synopticreport/{synopticId}",
    dependencies=[Depends(JWTBearer())],
    response_model=CaseSynopticVM,
)
async def get_synoptic_report(synopticId: int, db: Session = Depends(get_db)):
    commentsSynoptic = synoptic_report(synopticId=synopticId, db=db)
    # commentsPatient = synoptic_patient(synopticId=synopticId, db=db)

    report = []

    for data in commentsSynoptic:
        item = CaseCommentSynopticReport(0, 0, False, "", "", "", "", "", "")
        item.isSection = data.Level == 1 or data.Level == 2
        item.level = data.Level
        item.text = data.Key
        item.subtext = data.Level6
        item.value = data.Value
        item.comment = data.ElementValue
        item.id = data.TextId

        report.append(item)

    return {"synoptic": [], "patient": [], "report": report, "parsed": True}
