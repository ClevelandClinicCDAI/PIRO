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

    Within the same Key (e.g. pT category), multiple selected values are OR'd
    using an IN clause — cases matching ANY of those values are included.
    Between different Keys, groups are AND'd via INTERSECT — cases must satisfy
    at least one value from every selected Key group simultaneously.

    ProtocolData is joined once from the full table so all Filter CTEs work on
    the already-scoped small dataset.
    """
    params["protocol"] = protocol

    # Group filter values by key: {key: [val, val, ...]}
    key_groups: dict = {}
    for f in filters:
        key_groups.setdefault(f["key"], []).append(f["value"])

    filter_cte_sql = ""
    for gi, (key, values) in enumerate(key_groups.items()):
        key_param = f"fkey{gi}"
        params[key_param] = key
        val_params = []
        for vi, val in enumerate(values):
            vp = f"fval{gi}_{vi}"
            params[vp] = val
            val_params.append(f":{vp}")
        in_clause = ", ".join(val_params)
        filter_cte_sql += (
            f", FilterKey{gi} AS ("
            f"  SELECT DISTINCT CaseId FROM ProtocolData"
            f"  WHERE [Key] = :{key_param} AND [Value] IN ({in_clause})"
            f")"
        )

    if key_groups:
        parts = ["SELECT CaseId FROM ProtocolCases"] + [
            f"SELECT CaseId FROM FilterKey{gi}" for gi in range(len(key_groups))
        ]
        filter_cte_sql += ", FilteredCases AS (" + " INTERSECT ".join(parts) + ")"
        case_source = "FilteredCases"
    else:
        case_source = "ProtocolCases"

    base_cte = (
        "WITH ProtocolSynoptics AS ("
        "  SELECT DISTINCT SynopticId, CaseId FROM [CaseCommentSynopticReportData]"
        "  WHERE [Level] = 1 AND [Value] = :protocol"
        "),"
        " ProtocolCases AS ("
        "  SELECT DISTINCT CaseId FROM ProtocolSynoptics"
        "),"
        # Pre-filter data elements to this protocol's synoptics once via JOIN.
        # All subsequent CTEs reference ProtocolData instead of the full table.
        " ProtocolData AS ("
        "  SELECT d.SynopticId, d.CaseId, d.[Key], d.[Value]"
        "  FROM [CaseCommentSynopticReportData] d"
        "  INNER JOIN ProtocolSynoptics ps ON d.SynopticId = ps.SynopticId"
        "  WHERE d.[Level] != 1"
        "    AND d.[Value] IS NOT NULL AND LEN(TRIM(d.[Value])) > 0"
        ")"
    )
    return base_cte + filter_cte_sql, case_source


def get_synoptic_facets(protocol: str, filters: list, db: Session):
    """
    Return {items, total_cases, year_dist} for all categorical data elements.
    year_dist = [{year, case_count}] ordered by year.
    All three datasets share the same filtered case set.
    """
    params: dict = {}
    cte_sql, case_source = _build_filtered_cte(protocol, filters, params)

    # CategoricalKeys derived from ProtocolData (already scoped to this protocol)
    categorical_cte = (
        ", CategoricalKeys AS ("
        "  SELECT [Key]"
        "  FROM ProtocolData"
        "  GROUP BY [Key]"
        "  HAVING COUNT(DISTINCT [Value]) BETWEEN 2 AND 30"
        ")"
    )

    facet_sql = text(
        cte_sql
        + categorical_cte
        + " SELECT d.[Key], d.[Value], COUNT(DISTINCT d.CaseId) AS case_count"
        " FROM ProtocolData d"
        " JOIN CategoricalKeys ck ON d.[Key] = ck.[Key]"
        f" WHERE d.CaseId IN (SELECT CaseId FROM {case_source})"
        " GROUP BY d.[Key], d.[Value]"
        " HAVING COUNT(DISTINCT d.CaseId) > 10"
        " ORDER BY d.[Key], d.[Value]"
    ).bindparams(**params)

    count_params: dict = {}
    count_cte_sql, count_source = _build_filtered_cte(protocol, filters, count_params)
    count_sql = text(
        count_cte_sql
        + f" SELECT COUNT(*) FROM {count_source}"
    ).bindparams(**count_params)

    year_params: dict = {}
    year_cte_sql, year_source = _build_filtered_cte(protocol, filters, year_params)
    year_sql = text(
        year_cte_sql
        + " SELECT YEAR(c.AccessionDate) AS yr, COUNT(DISTINCT c.CaseId) AS case_count"
        " FROM [Case] c"
        f" WHERE c.CaseId IN (SELECT CaseId FROM {year_source})"
        "   AND c.AccessionDate IS NOT NULL"
        " GROUP BY YEAR(c.AccessionDate)"
        " ORDER BY yr"
    ).bindparams(**year_params)

    rs = db.execute(facet_sql)
    items = [
        dict2Class({"key": row[0], "value": row[1], "case_count": row[2]})
        for row in rs
    ]
    total_cases = db.execute(count_sql).scalar() or 0
    year_dist = [{"year": row[0], "case_count": row[1]} for row in db.execute(year_sql)]

    return {"items": items, "total_cases": total_cases, "year_dist": year_dist}


def get_matching_cases(protocol: str, filters: list, db: Session):
    """Return list of (CaseId, CaseNumber) matching the protocol + filters."""
    params: dict = {}
    cte_sql, case_source = _build_filtered_cte(protocol, filters, params)

    sql = text(
        cte_sql
        + " SELECT DISTINCT d.CaseId, d.CaseNumber"
        " FROM [CaseCommentSynopticReportData] d"
        " INNER JOIN ProtocolSynoptics ps ON d.SynopticId = ps.SynopticId"
        f" WHERE d.CaseId IN (SELECT CaseId FROM {case_source})"
        "   AND d.CaseNumber IS NOT NULL"
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
