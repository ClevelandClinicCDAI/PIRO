from db.models.CommentType import CommentType
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.commentType import CommentTypeVMCreate, CommentTypeVMUpdate


def create_new_commentType(input: CommentTypeVMCreate, user: str, db: Session):
    commentType = CommentType(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        DataLabReference=input.reference,
        ETLSource=input.etlSource,
        IsActive=True,
        CreateBy=user,
    )
    db.add(commentType)
    db.commit()
    db.refresh(commentType)
    return commentType


def update_commentType(input: CommentTypeVMUpdate, user: str, db: Session):
    commentType = (
        db.query(CommentType)
        .filter(CommentType.CommentTypeId == input.commentTypeId)
        .first()
    )
    if commentType is not None:
        commentType.ShortName = input.display
        commentType.Code = input.code
        commentType.Description = input.description
        commentType.DataLabReference = input.reference
        commentType.ETLSource = input.etlSource
        commentType.IsActive = True
        commentType.UpdatedBy = user
        db.commit()
    else:
        raise DataException("CommentType does not exist")
    return commentType


def list_commentType(db: Session):
    commentType = (
        db.query(CommentType).order_by(asc(CommentType.ShortName)).all()
    )
    return commentType


def list_commentType_active(db: Session):
    commentType = (
        db.query(CommentType)
        .filter(CommentType.IsActive == True)  # noqa
        .order_by(asc(CommentType.ShortName))
        .all()
    )  # noqa
    return commentType


def get_commentType(commentTypeId: int, db: Session):
    commentType = (
        db.query(CommentType)
        .filter(CommentType.CommentTypeId == commentTypeId)
        .first()
    )
    if commentType is None:
        raise DataException("CommentType does not exist")
    return commentType


def delete_commentType(commentTypeId: int, db: Session):
    commentType = (
        db.query(CommentType)
        .filter(CommentType.CommentTypeId == commentTypeId)
        .filter(CommentType.IsActive == True)  # noqa
        .first()
    )  # noqa
    if commentType is not None:
        commentType.IsActive = False
        db.commit()
    else:
        raise DataException("CommentType does not exist")
    return commentType
