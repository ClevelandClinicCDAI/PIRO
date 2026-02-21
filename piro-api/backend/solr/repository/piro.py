# If on Python 2.X

import math
from typing import List

# import time
import aiohttp
from core.config import settings
from core.string_util import StringUtil
from db.repository.caseComment import comment_final_copath, comment_final_epic
from logger import logger
from pysolr import Solr
from solr.models.document import document
from sqlalchemy.orm import Session
from viewmodel.solr.search import SearchFilterVM
from db.repository.case import get_mrn_casenumber


def build_query(input_arr: List[SearchFilterVM], db: Session):
    def get_category(element):
        return element.category

    input_arr.sort(key=get_category)
    categoryLst: List[str] = []
    # get the list of the distinct category
    for item in input_arr:
        if item.category not in categoryLst:
            categoryLst.append(item.category)

    catValue: str = ""

    def func(SearchFilterVM):
        if SearchFilterVM.category == catValue:
            return True
        else:
            return False

    qand: str = ""
    for item in categoryLst:
        catValue = item
        dataList = filter(func, input_arr)
        qor: str = ""
        for d in dataList:
            field = str(dict(d)["field"])
            val = str(dict(d)["search"])
            if field == "isdeceased" and val == "NA":
                continue
            elif field == "cohort":
                val = f"{{!join from=caseid to=caseid fromIndex=PIROCohort}}cohortid:{val}"
            elif field == "isdeceased" and val == "Deceased":
                val = "1"
            elif field == "isdeceased" and val == "Alive":
                val = "0"
            elif field == "isconcentriq" and val == "NA":
                continue
            elif field == "isconcentriq" and val == "Concentriq(Yes)":
                val = "1"
            elif field == "isconcentriq" and val == "Concentriq(No)":
                val = "0"
            elif field == "patcasenumber":
                field = "mrn"
                # val = "56521208"
                # start_time = time.time()
                casemrn = get_mrn_casenumber(val, db)
                if casemrn is None:
                    val = "0"
                else:
                    val = casemrn
                # process_time = (time.time() - start_time) * 1000
                # formatted_process_time = f"{process_time:.2f}"

            if StringUtil.isNotBlank(field):
                if ";" in field:
                    fields = field.split(";")
                    innerSplitQ = []
                    for f in fields:
                        if "date" in f:
                            innerSplitQ.append(f"{f}:{val}")
                        elif "years" in f:
                            innerSplitQ.append(f"{f}:{val}")
                        elif "casenumber" in f:
                            innerSplitQ.append(f"{f}:{val}")
                        elif "staffname" in f:
                            innerSplitQ.append(f"{'pathologist'}:{val}")
                        elif "cohort" in field:
                            innerSplitQ = f"{val}"
                        else:
                            innerSplitQ.append(f'{f}:"{val}"')
                    innerQ = " OR ".join(innerSplitQ)
                else:
                    if "date" in field:
                        innerQ = f"{field}:{val}"
                    elif "years" in field:
                        innerQ = f"{field}:{val}"
                    elif "casenumber" in field:
                        innerQ = f"{field}:{val}"
                    elif "staffname" in field:
                        innerQ = f"{'pathologist'}:{val}"
                    elif "cohort" in field:
                        innerQ = f"{val}"
                    else:
                        innerQ = f'{field}:"{val}"'
                if qor == "":
                    qor = innerQ
                else:
                    qor = f"{qor} OR {innerQ}"

        if qand == "" and qor != "":
            qand = f"({qor})"
        elif qor != "":
            qand = f"{qand} AND ({qor})"
    # qand = qand + " AND {!join from=caseid to=caseid fromIndex=PIROCohort}cohortid:5"

    if qand == "":
        return "*:*"
    else:
        return qand


def build_query_display(input_arr: List[SearchFilterVM]):
    def get_category(element):
        return element.category

    input_arr.sort(key=get_category)

    categoryLst: List[str] = []
    # get the list of the distinct category
    for item in input_arr:
        if item.category not in categoryLst:
            categoryLst.append(item.category)

    catValue: str = ""

    def func(SearchFilterVM):
        if SearchFilterVM.category == catValue:
            return True
        else:
            return False

    qand: str = ""
    for item in categoryLst:
        catValue = item
        dataList = filter(func, input_arr)
        qor: str = ""
        for d in dataList:
            field = str(dict(d)["field"])
            displaysingular = ""
            if "displaysingular" in dict(d):
                displaysingular = str(dict(d)["displaysingular"])
            val = str(dict(d)["search"])
            if StringUtil.isNotBlank(field):
                if ";" in field and displaysingular != "1":
                    fields = field.split(";")
                    innerSplitQ = []
                    for f in fields:
                        if "date" in f:
                            valDate: str = val.replace("T00:00:00Z", "")
                            innerSplitQ.append(f"##{valDate}$$")
                        else:
                            innerSplitQ.append(f"##{val}$$")
                    innerQ = " OR ".join(innerSplitQ)
                else:
                    if "date" in field:
                        valDate = val.replace("T00:00:00Z", "")
                        innerQ = f"##{valDate}$$"
                    # elif "isdeceased" in field:
                    #     if val == "1":
                    #         innerQ = f"##Deceased$$"
                    #     elif val == "0":
                    #         innerQ = f"##Alive$$"
                    else:
                        innerQ = f"##{val}$$"
                if qor == "":
                    qor = innerQ
                else:
                    qor = f"{qor} OR {innerQ}"

        if qand == "" and qor != "":
            qand = f"({qor})"
        elif qor != "":
            qand = f"{qand}  AND  ({qor})"
    if qand == "":
        return "*:*"
    else:
        return qand


# ##Search function to execute the filter criteria on SOLR
def search_Q(
    input_arr: List[SearchFilterVM],
    input_adv: str,
    mrn: str,
    sortBy: str,
    sortOrder: str,
    page: int,
    count: int,
    db: Session,
    solr: Solr,
    finalRtf: bool = False,
    fields: str = "*",
):
    qand = build_query(input_arr, db)
    if input_adv is not None and input_adv != "":
        qand = f"{qand} AND {input_adv}"

    if mrn is not None and mrn != "":
        qand = f"{qand} AND (mrn:{mrn})"

    if page > 0:
        page = page - 1

    solr_query_params = {
        "start": (page * settings.RECORDS_PER_PAGE),
        "rows": settings.RECORDS_PER_PAGE if count == 0 else count,
    }

    sortStr = ""
    if StringUtil.isNotBlank(sortBy):
        sortStr = f"{sortBy} {sortOrder}"
    results = solr.search(qand, sort=sortStr, fl=fields, **solr_query_params)

    docs: List[document] = []
    caseIds: List[int] = []
    for result in results:
        # docs.append(read_result(result, db=db))
        doc = read_result(result, db=db)
        if "caseid" in result:
            caseIds.append(int(result["caseid"]))
        if finalRtf:
            # Fetch RTF for Final Diagnosis
            if "final" in result:
                if doc.isepic:
                    final = comment_final_epic(int(result["caseid"]), db=db)
                    if final != "":
                        doc.final = final
                        doc.finalcount = 1
                elif doc.iscopath:
                    final = comment_final_copath(int(result["caseid"]), db=db)
                    if final != "":
                        doc.final = final
                        doc.finalcount = 1

                    # result['final'] = comment_final_copath(int(
                    # result['caseid']), db=db)
                    # result['finalcount'] = 1
        docs.append(doc)
    return {
        "items": docs,
        "total": results.hits,
        "page": page,
        "pages": math.floor(results.hits / settings.RECORDS_PER_PAGE),
        "query": qand,
        "caseIds": caseIds,
    }


def search_total(
    input_arr: List[SearchFilterVM],
    input_adv: str,
    mrn: str,
    solr: Solr,
    db: Session,
    cohortId: int = 0,
):
    qand = build_query(input_arr, db)

    if input_adv is not None and input_adv != "":
        qand = f"{qand} AND {input_adv}"

    if mrn is not None and mrn != "":
        qand = f"{qand} AND (mrn:{mrn})"

    if cohortId != 0:
        qand = f"({qand}) AND {{!join from=caseid to=caseid fromIndex=PIROCohort}}cohortid:{cohortId}"

    solr_query_params = {
        "start": 0,
        "rows": 0,
        # 'hl': 'true',
        # 'hl.fl': 'body',
        # 'hl.fragsize': 10,
        # 'hl.snippets': 3,
        # 'df': 'gross',
    }
    results = solr.search(qand, fl="id", **solr_query_params)
    return results.hits


def read_result(result: any, db: Session):
    """
    Search function to read the search results and transform it to a document

    Args:
        result:
        db:

    Returns:
    """
    # object
    doc = document()
    if "collectiondate" in result:
        doc.collectiondate = result["collectiondate"]
    else:
        doc.collectiondate = None
    if "gender" in result:
        doc.gender = result["gender"]
        match doc.gender:
            case "Male":
                doc.gender = "M"
            case "Female":
                doc.gender = "F"
            case _:
                doc.gender = "-"

    if "casepatientageyears" in result:
        doc.age = result["casepatientageyears"]
        doc.casepatientageyears = result["casepatientageyears"]
    else:
        doc.age = ""
        doc.casepatientageyears = ""
    if "epi" in result:
        doc.epi = result["epi"]
    else:
        doc.epi = ""
    if "casetypecategory" in result:
        doc.casetypecategory = result["casetypecategory"]
    if "specimenyear" in result:
        doc.specimenyear = result["specimenyear"]
    if "procedurecategory" in result:
        doc.procedurecategory = result["procedurecategory"]
    else:
        doc.procedurecategory = None
    if "signoutdate" in result:
        doc.signoutdate = result["signoutdate"]
    else:
        doc.signoutdate = None
    if "receivedate" in result:
        doc.receivedate = result["receivedate"]
    else:
        doc.receivedate = None
    if "language" in result:
        doc.language = result["language"]
    if "specimennumber" in result:
        doc.specimennumber = result["specimennumber"]
    if "casenumber" in result:
        doc.casenumber = result["casenumber"]
    if "hospital" in result:
        doc.hospital = result["hospital"]
    else:
        doc.hospital = None
    if "accessiondate" in result:
        doc.accessiondate = result["accessiondate"]
    else:
        doc.accessiondate = None
    if "ethnicity" in result:
        doc.ethnicity = result["ethnicity"]
    if "importdate" in result:
        doc.importdate = result["importdate"]
    if "interpreter" in result:
        doc.interpreter = result["interpreter"]
    else:
        doc.interpreter = ""
    if "pathologist" in result:
        doc.staffname = result["pathologist"]
        doc.pathologist = result["pathologist"]
    else:
        doc.staffname = ""
    if "isdeceased" in result:
        doc.isdeceased = result["isdeceased"]
    if "dob" in result:
        doc.dob = result["dob"]
    if "caseid" in result:
        doc.caseid = result["caseid"]
    if "gross" in result:
        doc.gross = result["gross"]
    else:
        doc.gross = ""
    if "comment" in result:
        doc.comment = result["comment"]
    else:
        doc.comment = ""
    if "microscopic" in result:
        doc.microscopic = result["microscopic"]
    else:
        doc.microscopic = ""
    if "addend" in result:
        doc.addend = result["addend"]
    else:
        doc.addend = ""
    if "resident" in result:
        doc.resident = result["resident"]
    else:
        doc.resident = ""
    if "synoptic" in result:
        doc.synoptic = result["synoptic"]
    else:
        doc.synoptic = ""
    if "intraop" in result:
        doc.intraop = result["intraop"]
    else:
        doc.intraop = ""
    if "clinical" in result:
        doc.clinical = result["clinical"]
    else:
        doc.clinical = ""
    if "clinicalcount" in result:
        doc.clinicalcount = result["clinicalcount"]
    else:
        doc.clinicalcount = ""
    if "patientname" in result:
        doc.patientname = result["patientname"]
    else:
        doc.patientname = ""
    if "deathdate" in result:
        doc.patientdeathdate = result["deathdate"]
        doc.deathdate = result["deathdate"]
    else:
        doc.patientdeathdate = None
        doc.deathdate = None
    if "race" in result:
        doc.race = result["race"]
    if "specialty" in result:
        doc.specialty = result["specialty"]
    if "mrn" in result:
        doc.mrn = result["mrn"]
    if "casetype" in result:
        doc.casetype = result["casetype"]
    if "overduedate" in result:
        doc.overduedate = result["overduedate"]
    else:
        doc.overduedate = None
    if "casestatus" in result:
        doc.casestatus = result["casestatus"]
    if "region" in result:
        doc.region = result["region"]
    if "specialtycode" in result:
        doc.specialtycode = result["specialtycode"]

    if "addendcount" in result:
        doc.addendcount = result["addendcount"]
    else:
        doc.addendcount = 0
    if "grosscount" in result:
        doc.grosscount = result["grosscount"]
    else:
        doc.grosscount = 0
    if "commentcount" in result:
        doc.commentcount = result["commentcount"]
    else:
        doc.commentcount = 0
    if "microscopiccount" in result:
        doc.microscopiccount = result["microscopiccount"]
    else:
        doc.microscopiccount = 0
    if "intraopcount" in result:
        doc.intraopcount = result["intraopcount"]
    else:
        doc.intraopcount = 0
    if "finalcount" in result:
        doc.finalcount = result["finalcount"]
    else:
        doc.finalcount = 0
    if "synopticcount" in result:
        doc.synopticcount = result["synopticcount"]
    else:
        doc.synopticcount = 0
    if "residentcount" in result:
        doc.residentcount = result["residentcount"]
    else:
        doc.residentcount = 0
    if "isepic" in result:
        doc.isepic = result["isepic"]
    if "isepicmigrated" in result:
        doc.isepicmigrated = result["isepicmigrated"]
    if "iscopath" in result:
        doc.iscopath = result["iscopath"]

    if "final" in result:
        doc.final = result["final"]
    else:
        doc.final = ""

    if "annotationmalignant" in result:
        doc.annotationmalignant = result["annotationmalignant"]
    else:
        doc.annotationmalignant = ""

    if "reviewtype" in result:
        doc.reviewtype = result["reviewtype"]
    else:
        doc.reviewtype = ""
    if "specialtycategory" in result:
        doc.specialtycategory = result["specialtycategory"]

    if "isconcentriq" in result:
        doc.isconcentriq = result["isconcentriq"]

    if "concentriqid" in result:
        doc.concentriqid = result["concentriqid"]
        doc.concentriqurl = (
            f'{settings.CONCENTRIQ_URL}{result["concentriqid"]}'
        )
    return doc


# Search function to execute the search criteria and execute just for the
# facet data. This will not return any data
def facet_get(
    input_arr: List[SearchFilterVM],
    input_adv: str,
    mrn: str,
    facet: str,
    solr: Solr,
    db: Session,
    recordlimit: int = 0,
    minCount: int = 0,
):  # noqa:E501
    solr_query_params = {
        "start": 0,
        "rows": 0,
        "facet": "on",
        "facet.field": facet,
        "facet.limit": 60 if recordlimit == 0 else recordlimit,
        "facet.mincount": 0 if minCount == 0 else minCount,
    }
    qand = build_query(input_arr, db)

    if input_adv is not None and input_adv != "":
        qand = f"{qand} AND {input_adv}"

    if mrn is not None and mrn != "":
        qand = f"{qand} AND (mrn:{mrn})"

    results = solr.search(qand, fl="*", **solr_query_params)
    return results.facets


# ##Search function to execute the suggest endpoint for comments, Staff, Case
async def suggest_get(input_val: str, suggest: str, suggester: str):
    result: any
    try:
        auth = aiohttp.BasicAuth(
            login=settings.SOLR_USER_NAME,
            password=settings.SOLR_USER_PASSWORD,
            encoding="utf-8",
        )
        async with aiohttp.ClientSession(auth=auth) as session:
            suggest_url = f"{settings.SOLR_URL}/{suggest}{input_val}"
            async with session.get(url=suggest_url, verify_ssl=False) as resp:
                result = await resp.json()
                terms = result["suggest"][suggester][input_val]["suggestions"]
                suggest = list()
                for term in terms:
                    if "term" in term:
                        suggest.append(
                            {
                                "name": str(term["term"]),
                                "value": str(term["term"]),
                            }
                        )
                return suggest
    except Exception as e:
        logger.error(e)
        return []


def get_Index_Date(solr: Solr):
    solr_query_params = {"start": 0, "rows": 1, "sort": "createdate desc"}
    results = solr.search("*:*", fl="createdate", **solr_query_params)
    for result in results:
        return result["createdate"]
