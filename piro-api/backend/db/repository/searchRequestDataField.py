from core.list_util import split_list_group
from db.dict2Class import dict2Class
from db.models.SearchRequestDataField import SearchRequestDataField
from db.models.DataField import DataField
from db.models.DataFieldCategory import DataFieldCategory
from exception.data_exception import DataException
from sqlalchemy import asc
from sqlalchemy.orm import Session
from viewmodel.serarchRequestDataField import SearchRequestDataFieldVMUpdate
from typing import List


def create_all_searchRequestDataField(
    searchRequstId: int,
    input: List[SearchRequestDataFieldVMUpdate],
    user: str,
    db: Session,
):

    def search_input(data: SearchRequestDataFieldVMUpdate, dataFieldId: int):
        if data.datafieldId == dataFieldId:
            return data
        else:
            return None

    searchRequestDataFields = list_searchRequestDataField(
        searchRequestId=searchRequstId
    )
    if searchRequestDataFields is None or len(searchRequestDataFields) == 0:
        datFields = list_dataField(db=db)
    else:
        datFields = list_searchRequestDataField(
            searchRequstId=searchRequstId, db=db
        )

    for data in datFields:  # noqa
        inputData = filter(search_input, input)
        if input is None:
            input = SearchRequestDataFieldVMUpdate()
            input.selected = False
            input.searchrequestdatafieldId = -1
            input.datafieldId = input.datafieldId
            input.searchrequestId = searchRequstId
        addupdate_searchRequestDataField(
            input=inputData, user=user, isCommit=False, db=db
        )
    db.commit()


def addupdate_searchRequestDataField(
    input: SearchRequestDataFieldVMUpdate,
    user: str,
    isCommit: bool,
    db: Session,
):
    searchRequestDataField = (
        db.query(SearchRequestDataField)
        .filter(
            SearchRequestDataField.SearchRequestDataFieldId
            == input.searchrequestdatafieldId
        )
        # .filter(SearchRequestDataField.SearchRequestId == input.searchrequestId)
        .filter(SearchRequestDataField.IsActive == True)  # noqa
        .first()
    )
    if searchRequestDataField is not None:
        searchRequestDataField.DataFieldId = input.datafieldId
        searchRequestDataField.IsSelected = input.selected
        searchRequestDataField.IsActive = True
        searchRequestDataField.UpdatedBy = user
    else:
        searchRequestDataField = SearchRequestDataField(
            SearchrequestId=input.searchrequestId,
            DataFieldId=input.datafieldId,
            IsSelected=input.selected,
            IsActive=True,
            CreateBy=user,
        )
        db.add(searchRequestDataField)
    if isCommit:
        db.commit()
    return searchRequestDataField


def addupdate_searchRequestDataFields(
    searchRequstId: int, dataFields: list[int], user: str, db: Session
):
    searchRequestDataFields = (
        db.query(SearchRequestDataField)
        .filter(SearchRequestDataField.SearchRequestId == searchRequstId)
        .filter(SearchRequestDataField.IsActive == True)
        .all()
    )  # noqa

    for searchRequestDataFieldUpdate in searchRequestDataFields:
        if searchRequestDataFieldUpdate.DataFieldId in dataFields:
            searchRequestDataFieldUpdate.IsSelected = True
            searchRequestDataFieldUpdate.UpdateBy = user
        else:
            searchRequestDataFieldUpdate.IsSelected = False
            searchRequestDataFieldUpdate.UpdateBy = user

    for searchRequestDataFieldadd in dataFields:
        inputData = [
            i
            for i in searchRequestDataFields
            if i.DataFieldId == searchRequestDataFieldadd
        ]
        if inputData is None or len(inputData) == 0:
            searchRequestDataField = SearchRequestDataField(
                SearchRequestId=searchRequstId,
                DataFieldId=searchRequestDataFieldadd,
                IsSelected=True,
                IsActive=True,
                CreateBy=user,
            )
            db.add(searchRequestDataField)
    db.commit()
    return True


def list_searchRequestDataField(searchRequestId: int, db: Session):
    queries = [SearchRequestDataField.IsActive == True]  # noqa
    queries.append(SearchRequestDataField.SearchRequestId == searchRequestId)
    # queries.append(SearchRequestDataField.IsSelected == True)  # noqa
    result = []
    data = (
        db.query(SearchRequestDataField, DataField, DataFieldCategory)
        .join(
            DataField,
            SearchRequestDataField.DataFieldId == DataField.DataFieldId,
        )
        .join(
            DataFieldCategory,
            DataField.DataFieldCategoryId
            == DataFieldCategory.DataFieldCategoryId,
        )
        .filter(*queries)
        .order_by(asc(DataField.Sequence), asc(DataFieldCategory.Sequence))
        .all()
    )

    for searchRequestDataField, dataField, dataFieldCategory in data:
        item = dict2Class(
            {
                "SearchRequestDataField": searchRequestDataField.SearchRequestDataFieldId,
                "SearchRequestId": searchRequestDataField.SearchRequestId,
                "IsSelected": searchRequestDataField.IsSelected,
                "IsActive": searchRequestDataField.IsActive,
                "DataFieldId": dataField.DataFieldId,
                "DataFieldDisplayName": dataField.DisplayName,
                "DataFieldSolrField": dataField.SolrField,
                "DataFieldCode": dataField.Code,
                "DataFieldSequence": dataField.Sequence,
                "DataFieldIsActive": dataField.IsActive,
                "DataFieldCategoryId": dataFieldCategory.DataFieldCategoryId,
                "DataFieldCategoryDisplayName": dataFieldCategory.DisplayName,
                "DataFieldCategoryCode": dataFieldCategory.Code,
                "DataFieldCategorySequence": dataFieldCategory.Sequence,
                "DataFieldCategoryIsActive": dataFieldCategory.IsActive,
            }
        )
        result.append(item)
    return result


def list_dataField(db: Session):
    queries = [DataField.IsActive == True]  # noqa
    datafields = []
    data = (
        db.query(DataField, DataFieldCategory)
        .join(
            DataFieldCategory,
            DataField.DataFieldCategoryId
            == DataFieldCategory.DataFieldCategoryId,
        )
        .filter(*queries)
        .order_by(asc(DataField.Sequence), asc(DataField.DisplayName))
        .all()
    )
    for dataField, dataFieldCategory in data:
        item = dict2Class(
            {
                "DataFieldId": dataField.DataFieldId,
                "DataFieldDisplayName": dataField.DisplayName,
                "DataFieldSolrField": dataField.SolrField,
                "DataFieldCode": dataField.Code,
                "DataFieldSequence": dataField.Sequence,
                "DataFieldIsActive": dataField.IsActive,
                "DataFieldCategoryId": dataFieldCategory.DataFieldCategoryId,
                "DataFieldCategoryDisplayName": dataFieldCategory.DisplayName,
                "DataFieldCategoryCode": dataFieldCategory.Code,
                "DataFieldCategorySequence": dataFieldCategory.Sequence,
                "DataFieldCategoryIsActive": dataFieldCategory.IsActive,
            }
        )
        datafields.append(item)

    queries = [DataFieldCategory.IsActive == True]  # noqa
    datafieldCategories = []
    data = (
        db.query(DataFieldCategory)
        .filter(*queries)
        .order_by(
            asc(DataFieldCategory.Sequence), asc(DataFieldCategory.DisplayName)
        )
        .all()
    )
    for dataFieldCategory in data:
        # pattern = "N.*"
        fieldpartition: int = 3
        filtered_fields = [
            x
            for x in datafields
            if dataFieldCategory.DataFieldCategoryId == x.DataFieldCategoryId
        ]
        item = dict2Class(
            {
                "DataFieldCategoryId": dataFieldCategory.DataFieldCategoryId,
                "DataFieldCategoryDisplayName": dataFieldCategory.DisplayName,
                "DataFieldCategoryCode": dataFieldCategory.Code,
                "DataFieldCategorySequence": dataFieldCategory.Sequence,
                "DataFieldCategoryIsActive": dataFieldCategory.IsActive,
                "Count": len(filtered_fields),
                "DataFields": split_list_group(
                    filtered_fields, fieldpartition
                ),
                "FieldPartition": fieldpartition,
            }
        )
        datafieldCategories.append(item)

    return {
        "DataFieldCategories": datafieldCategories,
        "DataFields": datafields,
    }


def delete_searchRequestDataField(searchRequestDataFieldId: int, db: Session):
    searchRequestDataField = (
        db.query(SearchRequestDataField)
        .filter(
            SearchRequestDataField.SearchRequestDataFieldId
            == searchRequestDataFieldId
        )
        .filter(SearchRequestDataField.IsActive == True)
        .first()  # noqa
    )
    if searchRequestDataField is not None:
        searchRequestDataField.IsActive = False
        db.commit()
    else:
        raise DataException("SearchRequestDataField does not exist")
    return searchRequestDataField
