from db.models.SearchRequestStatus import SearchRequestStatus
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.searchRequestStatus import (
    SearchRequestStatusVMCreate,
    SearchRequestStatusVMUpdate,
)


def create_new_searchRequestStatus(
    input: SearchRequestStatusVMCreate, user: str, db: Session
):
    searchRequestStatus = SearchRequestStatus(
        ShortName=input.display,
        Code=input.code,
        Description=input.description,
        IsActive=True,
        CreateBy=user,
    )
    db.add(searchRequestStatus)
    db.commit()
    db.refresh(searchRequestStatus)
    return searchRequestStatus


def update_searchRequestStatus(
    input: SearchRequestStatusVMUpdate, user: str, db: Session
):
    searchRequestStatus = (
        db.query(SearchRequestStatus)
        .filter(
            SearchRequestStatus.SearchRequestStatusId == input.searchRequestStatusId
        )
        .first()
    )
    if searchRequestStatus is not None:
        searchRequestStatus.ShortName = input.display
        searchRequestStatus.Code = input.code
        searchRequestStatus.Description = input.description
        searchRequestStatus.IsActive = True
        db.commit()
    else:
        raise DataException("SearchRequestStatus does not exist")
    return searchRequestStatus


def list_searchRequestStatus(db: Session):
    searchRequestStatus = (
        db.query(SearchRequestStatus).order_by(asc(SearchRequestStatus.ShortName)).all()
    )
    return searchRequestStatus


def list_searchRequestStatus_active(db: Session):
    searchRequestStatus = (
        db.query(SearchRequestStatus)
        .filter(SearchRequestStatus.IsActive == True)  # noqa
        .order_by(asc(SearchRequestStatus.ShortName))
        .all()
    )  # noqa
    return searchRequestStatus


def get_searchRequestStatus(searchRequestStatusId: int, db: Session):
    searchRequestStatus = (
        db.query(SearchRequestStatus)
        .filter(SearchRequestStatus.SearchRequestStatusId == searchRequestStatusId)
        .first()
    )
    if searchRequestStatus is None:
        raise DataException("SearchRequestStatus does not exist")
    return searchRequestStatus


def delete_searchRequestStatus(searchRequestStatusId: int, db: Session):
    searchRequestStatus = (
        db.query(SearchRequestStatus)
        .filter(SearchRequestStatus.SearchRequestStatusId == searchRequestStatusId)
        .filter(SearchRequestStatus.IsActive == True)  # noqa
        .first()
    )  # noqa
    if searchRequestStatus is not None:
        searchRequestStatus.IsActive = False
        db.commit()
    else:
        raise DataException("SearchRequestStatus does not exist")
    return searchRequestStatus
