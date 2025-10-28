from typing import List
from db.models.Search import Search
from db.models.User import User
from exception.data_exception import DataException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from viewmodel.search import SearchVMCreate, SearchVMUpdate
from viewmodel.solr.search import SearchFilterVM
from urllib.parse import parse_qs, urlparse
import json
from solr.repository.piro import build_query_display
from db.dict2Class import dict2Class


def create_new_search(
    input: SearchVMCreate, user: str, userId: int, db: Session
):
    search = Search(
        UserId=userId,
        Name=input.name,
        Description=input.description,
        SearchQuery=input.query,
        AdvancedQuery=input.advfields,
        MRN=input.mrn,
        IsActive=True,
        CreateBy=user,
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


def update_search(input: SearchVMUpdate, user: str, db: Session):
    search = db.query(Search).filter(Search.SearchId == input.searchId).first()
    if search is not None:
        search.Name = input.name
        search.Description = input.description
        search.SearchQuery = input.query
        search.MRN = input.mrn
        search.IsActive = True
        search.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Search does not exist")
    return search


def list_search(db: Session, userId: int):
    search = (
        db.query(Search)
        .filter(Search.UserId == userId)
        .order_by(asc(Search.Name))
        .all()
    )
    return search


def list_search_active(db: Session, userId: int):
    search = (
        db.query(Search)
        .filter(Search.UserId == userId)
        .filter(Search.IsActive == True)  # noqa
        .order_by(desc(Search.SearchId))
        .all()
    )
    return search


def get_search(searchId: int, db: Session):
    search = db.query(Search).filter(Search.SearchId == searchId).first()
    if search is None:
        raise DataException("Search does not exist")
    return search


def get_search_display(searchId: int, db: Session):
    data = (
        db.query(Search, User)
        .join(Search, Search.UserId == User.UserId)
        .filter(Search.SearchId == searchId)
        .all()
    )
    if data is None:
        raise DataException("Search does not exist")
    item = {}
    for search, requester in data:
        query = search.SearchQuery
        parsed_url = urlparse(query)
        parsed_q = parse_qs(parsed_url.query)
        json_object = json.loads(parsed_q["searchFilter"][0])
        filters: List[SearchFilterVM] = []
        for json_item in json_object:
            filter = SearchFilterVM(
                field=json_item["field"],
                search=json_item["search"],
                category=json_item["category"],
                andcondition=json_item["andcondition"],
                displaysingular=(
                    json_item["displaysingular"]
                    if "displaysingular" in json_item
                    else ""
                ),
            )
            filters.append(filter)

        display = build_query_display(input_arr=filters)
        item = dict2Class(
            {
                "SearchId": search.SearchId,
                "UserId": search.UserId,
                "RequesterFirstName": requester.FirstName,
                "RequesterLastName": requester.LastName,
                "SearchQuery": search.SearchQuery,
                "Name": search.Name,
                "Description": search.Description,
                "SearchName": search.SearchQuery,
                "Display": display,
                "IsActive": search.IsActive,
                "CreateDate": search.CreateDate,
            }
        )
    return item


def delete_search(searchId: int, db: Session):
    search = (
        db.query(Search)
        .filter(Search.SearchId == searchId)
        .filter(Search.IsActive == True)  # noqa
        .first()
    )
    if search is not None:
        search.IsActive = False
        db.commit()
    else:
        raise DataException("Search does not exist")
    return search
