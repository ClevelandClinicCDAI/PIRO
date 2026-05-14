from sqlalchemy import text
from sqlalchemy.orm import Session
from db.dict2Class import dict2Class


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


def get_synoptic_tnm_facets(protocol: str, db: Session):
    sql = text(
        "WITH ProtocolCases AS ( "
        "    SELECT DISTINCT CaseId "
        "    FROM [CaseCommentSynopticReportData] "
        "    WHERE [Level] = 1 AND [Value] = :protocol "
        ") "
        "SELECT [Key], [Value], COUNT(DISTINCT CaseId) AS case_count "
        "FROM [CaseCommentSynopticReportData] "
        "WHERE CaseId IN (SELECT CaseId FROM ProtocolCases) "
        "  AND [Level] != 1 "
        "  AND ([Key] LIKE '%pT category%' OR [Key] LIKE '%pN category%' OR [Key] LIKE '%pM category%') "
        "  AND [Value] IS NOT NULL AND LEN(TRIM([Value])) > 0 "
        "GROUP BY [Key], [Value] "
        "ORDER BY [Key], [Value]"
    ).bindparams(protocol=protocol)
    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class({"key": row[0], "value": row[1], "case_count": row[2]})
        result.append(item)
    return result
