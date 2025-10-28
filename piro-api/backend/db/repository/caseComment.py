from core.constants import Constants
from db.views.VCaseCommentCopath import VCaseCommentCopath
from db.views.VCaseCommentEpic import VCaseCommentEpic
from db.views.VCaseCommentText import VCaseCommentText
from sqlalchemy import asc
from sqlalchemy.orm import Session


def comment_copath(caseId: int, db: Session):
    comments = (
        db.query(VCaseCommentCopath)
        .filter(VCaseCommentCopath.CaseId == caseId)
        .order_by(asc(VCaseCommentCopath.CommentType))
        .all()
    )
    return comments


def comment_epic(caseId: int, db: Session):
    comments = (
        db.query(VCaseCommentEpic)
        .filter(VCaseCommentEpic.CaseId == caseId)
        .order_by(asc(VCaseCommentEpic.CommentType))
        .all()
    )
    return comments


def comment_text(caseId: int, db: Session):
    comments = (
        db.query(VCaseCommentText)
        .filter(VCaseCommentText.CaseId == caseId)
        .order_by(asc(VCaseCommentText.CommentType))
        .all()
    )
    return comments


def comment_final_epic(caseId: int, db: Session):
    comment = (
        db.query(VCaseCommentEpic)
        .filter(VCaseCommentEpic.CaseId == caseId)
        .filter(
            # VCaseCommentEpic.SourceCommentType == Constants.CommentTypeFinalDiagnosis
            (
                VCaseCommentEpic.SourceCommentType
                == Constants.CommentTypeFinalDiagnosis
            )
            | (
                VCaseCommentEpic.SourceCommentType
                == Constants.CommentTypeFlowCytometry
            )
        )
        .first()
    )
    return "" if comment is None else comment.CommentText


def comment_final_copath(caseId: int, db: Session):
    comment = (
        db.query(VCaseCommentCopath)
        .filter(VCaseCommentCopath.CaseId == caseId)
        .filter(
            VCaseCommentCopath.SourceCommentType
            == Constants.CommentTypeFinalCoPath
        )
        .first()
    )
    return "" if comment is None else comment.CommentText
