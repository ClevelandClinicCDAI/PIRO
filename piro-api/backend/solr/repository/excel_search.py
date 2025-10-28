# If on Python 2.X

import json
from datetime import date
from typing import List
from urllib.parse import parse_qs, urlparse

from core.config import Settings
from db.repository.search import get_search
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from pytest import Session
from solr.models.document import document
from solr.repository.piro import search_Q
from viewmodel.solr.search import SearchFilterVM
from pysolr import Solr
from core.search_util import filter_str_object


def get_search_data(
    searchId: int,
    fromDate: date,
    toDate: date,
    reasonCode: str,
    db: Session,
    solr: Solr,
    fields: str,
):
    search = get_search(searchId, db=db)
    advsearch = ""
    if search.AdvancedQuery is not None and search.AdvancedQuery != "":
        advsearch = filter_str_object(search.AdvancedQuery)
    query = search.SearchQuery
    parsed_url = urlparse(query)
    parsed_q = parse_qs(parsed_url.query)
    json_object = json.loads(parsed_q["searchFilter"][0])
    filters = []
    for item in json_object:
        # obj = SearchFilterVM
        # obj.category = obj['category']
        # obj.field = obj['field']
        # obj.search = obj['search']
        # obj.andcondition = obj['andcondition']
        obj = SearchFilterVM.parse_obj(item)

        filters.append(obj)

    # Add dates filter
    if fromDate is not None and toDate is not None:
        filters.append(
            SearchFilterVM(
                field="collectiondate",
                search=f'[{fromDate.strftime("%Y-%m-%d")}T00:00:00Z TO'
                f' {toDate.strftime("%Y-%m-%d")}T00:00:00Z]',
                category="collectiondate",
                andcondition=True,
                displaysingular="",
            )
        )
    elif fromDate is not None and toDate is None:
        filters.append(
            SearchFilterVM(
                field="collectiondate",
                search=f'[{fromDate.strftime("%Y-%m-%d")}T00:00:00Z TO NOW]',
                category="collectiondate",
                andcondition=True,
                displaysingular="",
            )
        )

    # Add deceased filter
    if reasonCode == "DEC":
        filters.append(
            SearchFilterVM(
                field="isdeceased",
                search="Deceased",
                category="isdeceased",
                andcondition=True,
                displaysingular="",
            )
        )

    docs = search_Q(
        input_arr=filters,
        input_adv=advsearch,
        mrn=search.MRN,
        sortBy="",
        sortOrder="",
        page=1,
        count=Settings.EXCEL_Output_Records,
        db=db,
        solr=solr,
        finalRtf=False,
        fields=fields,
    )
    return list(docs["items"])


def create_excel(searchId: int, data: List[document], fields: []):
    wb = Workbook()
    wb = load_workbook(
        f"{Settings.EXCEL_Template_DIRECTORY}{Settings.EXCEL_SEARCH_REQUEST_Template_FILE}"
    )
    ws1 = wb["Data"]

    offset_row = 0
    offset_col = 0
    col = 1
    row = 1
    for field in fields:
        ws1.cell(row, col + offset_col, field.DataFieldDisplayName)
        col = col + 1

    row = 2
    for rowData in data:
        col = 1
        rowDic = rowData.__dict__
        for field in fields:
            if field.DataFieldSolrField in rowDic:
                if rowDic[field.DataFieldSolrField] is None:
                    ws1.cell(
                        row + offset_row,
                        col + offset_col,
                        ILLEGAL_CHARACTERS_RE.sub(r"", ""),
                    )
                else:
                    # delimiter1 = "   ||||   "
                    # delimiter2 = "||--||"
                    str_data = ILLEGAL_CHARACTERS_RE.sub(
                        r"", str(rowDic[field.DataFieldSolrField])
                    )
                    str_data = str_data.replace("   ||||   ", "\n\n")
                    str_data = str_data.replace("||--||", "\n\n")
                    if field.DataFieldSolrField == "final":
                        str_data = str_data.replace("-", "\n-")
                    ws1.cell(
                        row + offset_row,
                        col + offset_col,
                        str_data,
                    )
            else:
                ws1.cell(
                    row + offset_row,
                    col + offset_col,
                    ILLEGAL_CHARACTERS_RE.sub(r"", ""),
                )
            col = col + 1
        row += 1

    file = f"PIRO_{searchId}.xlsx"
    path = f"{Settings.EXCEL_Output_DIRECTORY}{file}"
    wb.save(path)
    return {"path": path, "file": file}
