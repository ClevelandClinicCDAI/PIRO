from db.models.Tag import Tag
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.tag import TagVMCreate


def create_new_tag(input: TagVMCreate, userId: int, user: str, db: Session):
    tag = Tag(
        UserId=userId,
        Description=input.description,
        Name=input.name,
        IsActive=True,
        CreateBy=user,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def list_tag_active(userId: int, db: Session):
    tags = (
        db.query(Tag)
        .filter(Tag.IsActive == True)  # noqa
        .filter(Tag.UserId == userId)
        .order_by(asc(Tag.Name))
        .all()
    )  # noqa
    return tags


def get_tag(tagId: int, db: Session):
    tag = db.query(Tag).filter(Tag.TagId == tagId).first()
    if tag is None:
        raise DataException("Tag does not exist")
    return tag


def delete_tag(tagId: int, db: Session):
    tag = (
        db.query(Tag)
        .filter(Tag.TagId == tagId)
        .filter(Tag.IsActive == True)  # noqa
        .first()
    )  # noqa
    if tag is not None:
        tag.IsActive = False
        db.commit()
    else:
        raise DataException("Tag does not exist")
    return tag
