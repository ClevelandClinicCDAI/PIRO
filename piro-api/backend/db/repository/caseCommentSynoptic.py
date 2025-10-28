from db.models.CaseCommentSynopticSpecimen import CaseCommentSynopticSpecimen
from db.models.CaseCommentSynopticText import CaseCommentSynopticText
from sqlalchemy import asc, text
from sqlalchemy.orm import Session
from db.dict2Class import dict2Class


def synoptic_specimen(caseId: int, db: Session):
    specimens = (
        db.query(CaseCommentSynopticSpecimen)
        .filter(CaseCommentSynopticSpecimen.CaseId == caseId)
        .order_by(asc(CaseCommentSynopticSpecimen.SpecimenNum))
        .all()
    )
    return specimens


def synoptic_text(synopticId: int, db: Session):
    comments = (
        db.query(CaseCommentSynopticText)
        .filter(CaseCommentSynopticText.SynopticId == synopticId)
        .filter(CaseCommentSynopticText.ContextName == "SYNOPTIC")
        .order_by(
            asc(CaseCommentSynopticText.CommentSequence),
            asc(CaseCommentSynopticText.ContexHierarchy),
        )
        .all()
    )
    return comments


def synoptic_patient(synopticId: int, db: Session):
    comments = (
        db.query(CaseCommentSynopticText)
        .filter(CaseCommentSynopticText.SynopticId == synopticId)
        .filter(CaseCommentSynopticText.ContextName == "PATIENT")
        .order_by(
            asc(CaseCommentSynopticText.CommentSequence),
            asc(CaseCommentSynopticText.ContexHierarchy),
        )
        .all()
    )
    return comments


def synoptic_specimen_group(caseId: int, db: Session):
    sql = text(
        "Select SpecimenNum, IsSpecimenLevel, STRING_AGG(SynopticId,',') WITHIN GROUP ( ORDER BY SynopticId DESC)  AS SynopticId from ( "
        + "SELECT SynopticId, IsSpecimenLevel, STRING_AGG(SpecimenNum,',')  WITHIN GROUP ( ORDER BY SpecimenNum ASC)  AS "
        + "SpecimenNum FROM [dbo].[CaseCommentSynopticSpecimen] "
        + f"Where CaseId = {caseId} "
        + "GROUP BY SynopticId, IsSpecimenLevel ) Syn "
        + "GROUP BY SpecimenNum, IsSpecimenLevel "
    )

    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class(
            {
                "SpecimenNum": row[0],
                "IsSpecimenLevel": row[1],
                "SynopticId": row[2],
            }
        )
        result.append(item)
    return result


def synoptic_report(synopticId: int, db: Session):
    sql = text(
        "EXEC [dbo].[P_CaseCommentSynopticReport]  @SynopticId = "
        + f"{synopticId}"
    )
    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class(
            {
                "SynopticId": row[0],
                "CaseId": row[1],
                "CaseNumber": row[2],
                "Level": row[3],
                "Key": row[4],
                "Value": row[5],
                "TextId": row[6],
                "CommentId": row[7],
                "Level1": row[8],
                "Level2": row[9],
                "Level3": row[10],
                "Level4": row[11],
                "Level5": row[12],
                "Level6": row[13],
                "ElementValue": row[14],
                "Comment": row[15],
                "CommentSequence": row[16],
                "NewCommentSequence": row[17],
            }
        )
        result.append(item)
    return result
