from sqlalchemy import text
from sqlalchemy.orm import Session
from db.dict2Class import dict2Class
from db.models.Cohort import Cohort
from db.models.CohortCase import CohortCase
from core.constants import Constants
from airflow.cohort_api import trigger_cohort_job


def get_synoptic_protocols(db: Session):
    sql = text(
        "SELECT [Value] AS protocol, COUNT(DISTINCT CaseId) AS case_count "
        "FROM [CaseCommentSynopticReportData] "
        "WHERE [Level] = 1 AND [Value] IS NOT NULL AND LEN(TRIM([Value])) > 0 "
        "GROUP BY [Value] "
        "HAVING COUNT(DISTINCT CaseId) >= 50 "
        "ORDER BY [Value]"
    )
    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class({"protocol": row[0], "case_count": row[1]})
        result.append(item)
    return result


def _build_filtered_cte(protocol: str, filters: list, params: dict):
    """
    Returns (full_cte_sql, case_source_name).
    Mutates params with all needed bind parameters.
    """
    params["protocol"] = protocol

    filter_cte_sql = ""
    for i, f in enumerate(filters):
        key_param = f"fkey{i}"
        val_param = f"fval{i}"
        params[key_param] = f["key"]
        params[val_param] = f["value"]
        filter_cte_sql += (
            f", Filter{i} AS ("
            f"  SELECT DISTINCT CaseId FROM [CaseCommentSynopticReportData]"
            f"  WHERE CaseId IN (SELECT CaseId FROM ProtocolCases)"
            f"  AND [Key] = :{key_param} AND [Value] = :{val_param}"
            f")"
        )

    if filters:
        parts = ["SELECT CaseId FROM ProtocolCases"] + [
            f"SELECT CaseId FROM Filter{i}" for i in range(len(filters))
        ]
        filter_cte_sql += ", FilteredCases AS (" + " INTERSECT ".join(parts) + ")"
        case_source = "FilteredCases"
    else:
        case_source = "ProtocolCases"

    base_cte = (
        "WITH ProtocolCases AS ("
        "  SELECT DISTINCT CaseId FROM [CaseCommentSynopticReportData]"
        "  WHERE [Level] = 1 AND [Value] = :protocol"
        ")"
    )
    return base_cte + filter_cte_sql, case_source


def get_synoptic_tnm_facets(protocol: str, filters: list, db: Session):
    """
    Return {items, total_cases} for pT/pN/pM categories, filtered by active selections.
    """
    params: dict = {}
    cte_sql, case_source = _build_filtered_cte(protocol, filters, params)

    facet_sql = text(
        cte_sql
        + " SELECT [Key], [Value], COUNT(DISTINCT CaseId) AS case_count"
        " FROM [CaseCommentSynopticReportData]"
        f" WHERE CaseId IN (SELECT CaseId FROM {case_source})"
        "   AND [Level] != 1"
        "   AND ([Key] LIKE '%pT category%' OR [Key] LIKE '%pN category%' OR [Key] LIKE '%pM category%')"
        "   AND [Value] IS NOT NULL AND LEN(TRIM([Value])) > 0"
        " GROUP BY [Key], [Value]"
        " ORDER BY [Key], [Value]"
    ).bindparams(**params)

    count_params: dict = {}
    count_cte_sql, count_source = _build_filtered_cte(protocol, filters, count_params)
    count_sql = text(
        count_cte_sql
        + f" SELECT COUNT(*) FROM {count_source}"
    ).bindparams(**count_params)

    rs = db.execute(facet_sql)
    items = [
        dict2Class({"key": row[0], "value": row[1], "case_count": row[2]})
        for row in rs
    ]
    total_cases = db.execute(count_sql).scalar() or 0

    return {"items": items, "total_cases": total_cases}


def get_matching_cases(protocol: str, filters: list, db: Session):
    """Return list of (CaseId, CaseNumber) matching the protocol + filters."""
    params: dict = {}
    cte_sql, case_source = _build_filtered_cte(protocol, filters, params)

    sql = text(
        cte_sql
        + f" SELECT DISTINCT r.CaseId, r.CaseNumber"
        f" FROM [CaseCommentSynopticReportData] r"
        f" WHERE r.CaseId IN (SELECT CaseId FROM {case_source})"
        f"   AND r.CaseNumber IS NOT NULL"
    ).bindparams(**params)

    rs = db.execute(sql)
    return [(row[0], row[1]) for row in rs]


def create_synoptic_cohort(
    protocol: str,
    filters: list,
    name: str,
    desc: str,
    user_id: int,
    user: str,
    db: Session,
):
    cases = get_matching_cases(protocol, filters, db)
    if not cases:
        return None

    cohort = Cohort(
        Name=name,
        Description=desc,
        Disease=protocol,
        IsFacetDisplay=True,
        UserId=user_id,
        IsActive=True,
        LoadType=Constants.CohortTypeCase,
        IsSolrUpdated=False,
        CreateBy=user,
    )
    db.add(cohort)
    db.commit()
    db.refresh(cohort)

    objects = [
        CohortCase(
            CohortPatientId=None,
            CohortId=cohort.CohortId,
            PatientId=None,
            CaseNumber=case_number,
            CaseId=case_id,
            IsActive=True,
            LoadType=Constants.CohortTypeCase,
            IsSolrUpdated=False,
            CreateBy=user,
        )
        for case_id, case_number in cases
    ]
    db.bulk_save_objects(objects)
    db.commit()

    trigger_cohort_job(cohortId=cohort.CohortId)

    return cohort.CohortId
