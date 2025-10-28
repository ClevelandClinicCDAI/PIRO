from db.dict2Class import dict2Class
from db.models.Case import Case
from db.models.Tag import Tag
from db.models.TagCase import TagCase
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.tagCase import TagCaseVMCreate


def create_new_tagcase(input: TagCaseVMCreate, user: str, db: Session):
    tagcase = TagCase(
        TagId=input.tagid, CaseId=input.caseid, IsActive=True, CreateBy=user
    )
    db.add(tagcase)
    db.commit()
    db.refresh(tagcase)
    return tagcase


def list_tagcase_active(caseId: int, userId: int, db: Session):
    tagcases = []
    data = (
        db.query(TagCase, Tag, Case)
        .join(Tag, TagCase.TagId == Tag.TagId)
        .join(Case, TagCase.CaseId == Case.CaseId)
        .filter(TagCase.IsActive == True)  # noqa
        .filter(Tag.UserId == userId)
        .filter(TagCase.CaseId == caseId)
        .order_by(asc(Tag.Name))
        .order_by(asc(Case.CaseNumber))
        .all()
    )  # noqa
    for tagCase, tag, case in data:
        result = dict2Class(
            {
                "TagCaseId": tagCase.TagCaseId,
                "TagId": tag.TagId,
                "CaseId": tagCase.CaseId,
                "UserId": tag.UserId,
                "TagName": tag.Name,
                "TagDesc": tag.Description,
                "CaseNumber": case.CaseNumber,
                "IsActive": tagCase.IsActive,
            }
        )
        tagcases.append(result)
    return tagcases


def list_tagname_active(caseId: int, userId: int, db: Session):
    tags = []
    data = (
        db.query(TagCase, Tag)
        .join(Tag, TagCase.TagId == Tag.TagId)
        .filter(TagCase.CaseId == caseId)
        .filter(TagCase.IsActive == True)  # noqa
        .filter(Tag.UserId == userId)
        .order_by(asc(Tag.Name))
        .all()
    )  # noqa
    for _tagCase, tag in data:
        tags.append(tag.Name)
    list_set = set(tags)
    return list(list_set)


def delete_tagcase(tagCaseId: int, db: Session):
    tagcase = (
        db.query(TagCase)
        .filter(TagCase.TagCaseId == tagCaseId)
        .filter(Tag.IsActive == True)  # noqa
        .first()
    )  # noqa
    if tagcase is not None:
        tagcase.IsActive = False
        db.commit()
    else:
        raise DataException("Tag Case does not exist")
    return tagcase
