from db.models.SearchRequestStatus import SearchRequestStatus
from exception.data_exception import DataException
from sqlalchemy.orm import Session


def SearchRequestStatus_get_id(code: str, db: Session):
    searchRequestStatus = (
        db.query(SearchRequestStatus)
        .filter(SearchRequestStatus.Code == code)
        .filter(SearchRequestStatus.IsActive == True)  # noqa
        .first()
    )

    if searchRequestStatus is None:
        raise DataException("SearchRequestStatus does not exist for %s" % code)
    return searchRequestStatus.SearchRequestStatusId
