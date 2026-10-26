"""Case sets keep explicit IDs; saved searches remain editable search criteria."""

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException
from sqlalchemy import column, func, inspect, insert, literal, select, table, text
from sqlalchemy.exc import IntegrityError

from core.search_util import filter_str_object
from core.constants import Constants
from core.exception_util import PIROException
from core.security_util import SecurityUtil
from db.models.CaseSet import CaseSet, CaseSetCase, CaseSetSpecimen
from db.models.Cohort import Cohort
from db.models.CohortCase import CohortCase
from db.models.Search import Search
from db.models.User import User
from solr.repository.piro import build_query, read_result
from viewmodel.case_set import CaseSetDocumentVM
from viewmodel.solr.search import SearchFilterVM

CAPTURE_BATCH = 500
OPERATIONS_SCHEMA_ERROR = (
    "Case set operations need a database update. "
    "Please contact your PIRO administrator."
)
CART_SCHEMA_ERROR = (
    "Creating a case set from the cart needs a database update. Ask your PIRO "
    "administrator to run 20261021_EnableCaseSetCart.sql."
)
OPERATION_LABELS = {
    "UNION": "Union",
    "INTERSECTION": "Intersection",
    "DIFFERENCE": "A minus B",
    "SYMMETRIC_DIFFERENCE": "Symmetric difference",
}

# Query only the clinical columns used here. The legacy Specimen ORM includes
# columns absent from the current SQL Server schema (e.g. FormatNumber).
SPECIMENS = table(
    "Specimen",
    column("SpecimenId"),
    column("CaseId"),
    column("SpecimenNumber"),
    column("IsActive"),
)
SPECIALTIES = table("Specialty", column("SpecialtyCategory"), column("IsActive"))
SHARING_SCHEMA_ERROR = (
    "Teaching sets need a database update. Ask your PIRO administrator to run "
    "20261021_EnableTeachingSets.sql."
)
SPECIMEN_SCHEMA_ERROR = (
    "Specimen selection needs a database update. Ask your PIRO administrator to run "
    "20261015_AddCaseSetSpecimens.sql."
)


def require_schema(db):
    schema = inspect(db.connection())
    for model in (CaseSet, CaseSetCase):
        if not schema.has_table(model.__tablename__):
            raise HTTPException(
                503,
                "Case sets are not available yet. Please contact your PIRO administrator to complete setup.",
            )
        actual = {c["name"] for c in schema.get_columns(model.__tablename__)}
        if model is CaseSet and not {"IsPublic", "SpecialtyCategory"}.issubset(actual):
            raise HTTPException(503, SHARING_SCHEMA_ERROR)
        if not set(model.__table__.columns.keys()).issubset(actual):
            raise HTTPException(
                503,
                "Case sets need a database update. Please contact your PIRO administrator.",
            )


def owned(set_id, owner_id, db, lock=False):
    query = db.query(CaseSet).filter(
        CaseSet.CaseSetId == set_id, CaseSet.OwnerId == owner_id
    )
    if lock:
        query = query.with_hint(
            CaseSet, "WITH (UPDLOCK, HOLDLOCK)", dialect_name="mssql"
        ).with_for_update()
    item = query.populate_existing().first()
    if item is None:
        raise HTTPException(404, "Case set not found.")
    return item


def counts(set_id, db):
    result = dict(
        db.query(CaseSetCase.ReviewState, func.count())
        .filter(CaseSetCase.CaseSetId == set_id)
        .group_by(CaseSetCase.ReviewState)
        .all()
    )
    return {
        "total": sum(result.values()),
        "unreviewed": result.get("UNREVIEWED", 0),
        "included": result.get("INCLUDED", 0),
        "excluded": result.get("EXCLUDED", 0),
    }


def utc(value):
    # SQL Server DATETIME stores these UTC timestamps without an offset.
    return value.replace(tzinfo=timezone.utc) if value is not None else None


def summary(item, db):
    return {
        "caseSetId": item.CaseSetId,
        "name": item.Name,
        "description": item.Description,
        "sourceType": item.SourceType,
        "sourceId": item.SourceId,
        "sourceName": item.SourceName,
        "archived": item.Archived,
        "isPublic": item.IsPublic,
        "specialtyCategory": item.SpecialtyCategory,
        "revision": item.Revision,
        "createdAt": utc(item.CreatedAt),
        "updatedAt": utc(item.UpdatedAt),
        "captureState": item.CaptureState,
        "captureCursor": item.CaptureCursor,
        "captureExpected": item.CaptureExpected,
        "captureSeen": item.CaptureSeen,
        "captureFinishedAt": utc(item.CaptureFinishedAt),
        "captureError": item.CaptureError,
        "lastCaseId": item.LastCaseId,
        "reviewFilter": item.ReviewFilter,
        **counts(item.CaseSetId, db),
    }


def specialty_categories(db):
    schema = inspect(db.connection())
    if not schema.has_table("Specialty") or not {
        "SpecialtyCategory",
        "IsActive",
    }.issubset({c["name"] for c in schema.get_columns("Specialty")}):
        raise HTTPException(
            503,
            "Specialty categories are not available. Contact your PIRO administrator.",
        )
    rows = db.execute(
        select(SPECIALTIES.c.SpecialtyCategory)
        .where(SPECIALTIES.c.IsActive == 1)
        .distinct()
    ).all()
    categories = {}
    for (value,) in rows:
        category = (value or "").strip()
        if category:
            categories.setdefault(category.casefold(), category)
    return sorted(categories.values(), key=str.casefold)


def share(set_id, owner_id, payload, db):
    try:
        item = owned(set_id, owner_id, db, lock=True)
        category = payload.specialtyCategory or None
        if payload.isPublic:
            if item.Archived or item.CaptureState != "READY":
                raise HTTPException(
                    409,
                    "Complete capture and restore this set before making it public.",
                )
            available = {value.casefold(): value for value in specialty_categories(db)}
            if not category or category.casefold() not in available:
                raise HTTPException(
                    422,
                    "Choose an available specialty category before making this set public.",
                )
            category = available[category.casefold()]
        else:
            # Unpublishing must remain possible if the category is retired.
            category = item.SpecialtyCategory
        same = item.IsPublic == payload.isPublic and item.SpecialtyCategory == category
        if item.Revision != payload.revision:
            if item.Revision == payload.revision + 1 and same:
                return summary(item, db)
            raise HTTPException(
                409,
                "This set changed in another session. Reload before saving sharing settings.",
            )
        if not same:
            item.IsPublic = payload.isPublic
            item.SpecialtyCategory = category
            item.Revision += 1
            item.UpdatedAt = datetime.utcnow()
        db.commit()
        return summary(item, db)
    except Exception:
        db.rollback()
        raise


def teaching_query(db):
    return db.query(CaseSet).filter(
        CaseSet.IsPublic == True,
        CaseSet.Archived == False,  # noqa: E712
        CaseSet.CaptureState == "READY",
    )


def teaching_set(set_id, db):
    item = teaching_query(db).filter(CaseSet.CaseSetId == set_id).first()
    if item is None:
        raise HTTPException(404, "Teaching set not found or no longer public.")
    return item


def teaching_summary(item, db):
    creator = (
        db.query(User.FirstName, User.LastName)
        .filter(User.UserId == item.OwnerId)
        .first()
    )
    creator_name = (
        " ".join(part.strip() for part in creator if part and part.strip())
        if creator
        else ""
    )
    total = (
        db.query(func.count())
        .select_from(CaseSetCase)
        .filter(
            CaseSetCase.CaseSetId == item.CaseSetId,
            CaseSetCase.ReviewState != "EXCLUDED",
        )
        .scalar()
    )
    return {
        "caseSetId": item.CaseSetId,
        "name": item.Name,
        "description": item.Description,
        "specialtyCategory": item.SpecialtyCategory,
        "creatorName": creator_name or "Unknown user",
        "total": total,
        "createdAt": utc(item.CreatedAt),
        "updatedAt": utc(item.UpdatedAt),
    }


def teaching_sets(category, page, size, db):
    query = teaching_query(db)
    categories = [
        value
        for (value,) in query.with_entities(CaseSet.SpecialtyCategory)
        .distinct()
        .order_by(CaseSet.SpecialtyCategory)
        .all()
        if value
    ]
    if category:
        query = query.filter(CaseSet.SpecialtyCategory == category)
    total = query.count()
    page = max(1, min(page, (total + size - 1) // size))
    rows = (
        query.order_by(CaseSet.Name, CaseSet.CaseSetId)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return {
        "items": [teaching_summary(item, db) for item in rows],
        "total": total,
        "page": page,
        "size": size,
        "categories": categories,
    }


def teaching_members(set_id, page, size, role, attest, db, solr):
    item = teaching_set(set_id, db)
    query = db.query(CaseSetCase).filter(
        CaseSetCase.CaseSetId == set_id, CaseSetCase.ReviewState != "EXCLUDED"
    )
    total = query.count()
    page = max(1, min(page, (total + size - 1) // size))
    rows = (
        query.order_by(CaseSetCase.Ordinal).offset((page - 1) * size).limit(size).all()
    )
    # Every signed-in role can browse. Roles without search privileges receive
    # the ordinary USER mask, never SecurityUtil's unrecognized-role fallback.
    if role not in (
        Constants.RoleAdmin,
        Constants.RoleDemoAdmin,
        Constants.RoleAnalyst,
        Constants.RoleUser,
        Constants.RoleSecurityAdmin,
    ):
        role, attest = Constants.RoleUser, False
    documents = case_documents(rows, role, attest, db, solr)
    return {
        "items": [
            {
                "caseId": row.CaseId,
                "ordinal": (page - 1) * size + index,
                "summary": documents.get(row.CaseId),
                "unavailable": row.CaseId not in documents,
            }
            for index, row in enumerate(rows, 1)
        ],
        "total": total,
        "page": page,
        "size": size,
        "set": teaching_summary(item, db),
    }


def sources(owner_id, db):
    searches = (
        db.query(Search)
        .filter(Search.UserId == owner_id, Search.IsActive == True)
        .order_by(Search.Name)
        .all()
    )  # noqa: E712
    cohorts = (
        db.query(Cohort)
        .filter(Cohort.UserId == owner_id, Cohort.IsActive == True)
        .order_by(Cohort.Name)
        .all()
    )  # noqa: E712
    return {
        "searches": [{"id": s.SearchId, "name": s.Name} for s in searches],
        "cohorts": [{"id": c.CohortId, "name": c.Name} for c in cohorts],
    }


def saved_query(source, db):
    try:
        # Saved SearchQuery is a search URL, not a list of case IDs.
        params = parse_qs(urlparse(source.SearchQuery).query)
        raw = json.loads(params["searchFilter"][0])
        if not isinstance(raw, list):
            raise ValueError("Expected search filters")
        filters = [SearchFilterVM.parse_obj(item) for item in raw]
        advanced = json.loads(source.AdvancedQuery or "{}")
        advanced_query = filter_str_object(source.AdvancedQuery) if advanced else ""
        query = build_query(filters, db)
        if advanced_query:
            query = f"({query}) AND ({advanced_query})"
        if source.MRN:
            query = f"({query}) AND (mrn:{source.MRN})"
        return json.dumps(
            {
                "query": query,
                "now": int(time.time() * 1000),
                "searchQuery": source.SearchQuery,
                "advancedQuery": advanced,
                "mrn": source.MRN,
            }
        )
    except (ValueError, KeyError, TypeError, AttributeError, PIROException) as error:
        raise HTTPException(
            422,
            "This saved search has invalid criteria. Load and save the search again before capturing it.",
        ) from error


def create(owner_id, payload, db):
    creation_key = str(payload.operationId)
    fingerprint = hashlib.sha256(
        payload.json(exclude={"operationId"}, sort_keys=True).encode()
    ).hexdigest()
    existing = (
        db.query(CaseSet)
        .filter(CaseSet.OwnerId == owner_id, CaseSet.CreationKey == creation_key)
        .first()
    )
    if existing:
        if existing.CreationHash != fingerprint:
            raise HTTPException(
                409, "This creation request was already used for another set."
            )
        return summary(existing, db)
    model = Search if payload.sourceType == "SAVED_SEARCH" else Cohort
    source_key = model.SearchId if model is Search else model.CohortId
    source = (
        db.query(model)
        .filter(
            source_key == payload.sourceId,
            model.UserId == owner_id,
            model.IsActive == True,
        )
        .first()
    )  # noqa: E712
    if source is None:
        raise HTTPException(404, "Source not found.")
    query = saved_query(source, db) if model is Search else "{}"
    item = CaseSet(
        OwnerId=owner_id,
        Name=payload.name,
        Description=payload.description,
        SourceType=payload.sourceType,
        SourceId=payload.sourceId,
        SourceName=source.Name,
        SourceQuery=query,
        CreationKey=creation_key,
        CreationHash=fingerprint,
    )
    try:
        db.add(item)
        db.flush()
        if model is Cohort:
            members = (
                select(CohortCase.CaseId)
                .where(
                    CohortCase.CohortId == source.CohortId,
                    CohortCase.IsActive == True,  # noqa: E712
                )
                .with_hint(CohortCase, "WITH (HOLDLOCK)", dialect_name="mssql")
            )
            unresolved = db.execute(
                members.where(
                    (CohortCase.CaseId.is_(None)) | (CohortCase.CaseId <= 0)
                ).limit(1)
            ).first()
            if unresolved:
                raise HTTPException(
                    409,
                    "Resolve the unmatched cases in this cohort before capturing a case set.",
                )
            distinct_ids = members.distinct().subquery()
            db.execute(
                insert(CaseSetCase).from_select(
                    ["CaseSetId", "CaseId", "Ordinal", "ReviewState", "Revision"],
                    select(
                        literal(item.CaseSetId),
                        distinct_ids.c.CaseId,
                        func.row_number().over(order_by=distinct_ids.c.CaseId),
                        literal("UNREVIEWED"),
                        literal(0),
                    ),
                )
            )
            item.CaptureExpected = counts(item.CaseSetId, db)["total"]
            item.CaptureSeen = item.CaptureExpected
            item.CaptureState = "READY"
            item.CaptureFinishedAt = datetime.utcnow()
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(CaseSet)
            .filter(CaseSet.OwnerId == owner_id, CaseSet.CreationKey == creation_key)
            .first()
        )
        if existing and existing.CreationHash == fingerprint:
            return summary(existing, db)
        if existing:
            raise HTTPException(
                409, "This creation request was already used for another set."
            )
        raise
    except Exception:
        db.rollback()
        raise
    return summary(item, db)


def require_source_schema(db, source_type, message):
    if db.bind.dialect.name == "mssql":
        # SQLAlchemy's SQL Server dialect does not implement check reflection.
        constraint = db.execute(
            text(
                "SELECT definition FROM sys.check_constraints "
                "WHERE parent_object_id = OBJECT_ID(N'dbo.CaseSet') "
                "AND name = N'CK_CaseSet_Source' AND is_disabled = 0"
            )
        ).first()
        if constraint is not None and constraint.definition is None:
            # DML permissions expose the constraint, but its definition is NULL
            # without VIEW DEFINITION. This is unknown, not a missing migration.
            # The real INSERT still enforces it; creation handlers translate an
            # old SourceType constraint's rejection after rolling back.
            return
        definition = constraint.definition if constraint is not None else None
    else:
        constraints = inspect(db.connection()).get_check_constraints("CaseSet")
        definition = next(
            (c["sqltext"] for c in constraints if c["name"] == "CK_CaseSet_Source"),
            None,
        )
    if not definition or f"'{source_type}'" not in definition.upper():
        raise HTTPException(503, message)


def require_operations_schema(db):
    require_source_schema(db, "OPERATION", OPERATIONS_SCHEMA_ERROR)


def operation_sources(owner_id, db):
    require_operations_schema(db)
    return addition_targets(owner_id, db)


def addition_targets(owner_id, db):
    items = (
        db.query(CaseSet.CaseSetId, CaseSet.Name)
        .filter(
            CaseSet.OwnerId == owner_id,
            CaseSet.Archived == False,  # noqa: E712
            CaseSet.CaptureState == "READY",
        )
        .order_by(CaseSet.Name, CaseSet.CaseSetId)
        .all()
    )
    return [{"id": item.CaseSetId, "name": item.Name} for item in items]


def validate_cart_cases(case_ids, solr):
    """Validate all additions before writing, using the same index as search."""
    for offset in range(0, len(case_ids), CAPTURE_BATCH):
        batch = case_ids[offset : offset + CAPTURE_BATCH]
        try:
            result = solr.search(
                "caseid:(" + " OR ".join(map(str, batch)) + ")",
                fl="caseid",
                rows=len(batch),
            )
            if result.raw_response.get("responseHeader", {}).get("partialResults"):
                raise ValueError("Incomplete search response")
            found = {int(doc["caseid"]) for doc in result}
        except Exception as error:
            raise HTTPException(
                503,
                "Cases could not be checked. Your cart has been kept; please retry.",
            ) from error
        if set(batch) != found:
            missing = ", ".join(map(str, sorted(set(batch) - found)))
            raise HTTPException(
                422,
                f"Some cases are no longer available (case IDs: {missing}). "
                "Remove them from the cart and retry. No cases were added.",
            )


def append_case_ids(item, case_ids, db):
    ordinal = (
        db.query(func.max(CaseSetCase.Ordinal))
        .filter_by(CaseSetId=item.CaseSetId)
        .scalar()
        or 0
    )
    db.add_all(
        [
            CaseSetCase(
                CaseSetId=item.CaseSetId,
                CaseId=case_id,
                Ordinal=ordinal + index,
                ReviewState="UNREVIEWED",
            )
            for index, case_id in enumerate(case_ids, 1)
        ]
    )
    db.flush()


def create_from_cart(owner_id, payload, db, solr):
    creation_key = str(payload.operationId)
    case_ids = list(dict.fromkeys(payload.caseIds))
    fingerprint = hashlib.sha256(
        payload.json(exclude={"operationId"}, sort_keys=True).encode()
    ).hexdigest()

    def existing_result():
        existing = (
            db.query(CaseSet)
            .filter_by(OwnerId=owner_id, CreationKey=creation_key)
            .first()
        )
        if existing and existing.CreationHash != fingerprint:
            raise HTTPException(
                409, "This creation request was already used for another set."
            )
        return existing

    try:
        existing = existing_result()
        if existing:
            return summary(existing, db)
        require_source_schema(db, "MANUAL", CART_SCHEMA_ERROR)
        validate_cart_cases(case_ids, solr)
        item = CaseSet(
            OwnerId=owner_id,
            Name=payload.name,
            Description=payload.description,
            SourceType="MANUAL",
            SourceId=0,
            SourceName="Search cart",
            SourceQuery=json.dumps({"caseIds": case_ids}),
            CreationKey=creation_key,
            CreationHash=fingerprint,
            CaptureState="READY",
            CaptureExpected=len(case_ids),
            CaptureSeen=len(case_ids),
            CaptureFinishedAt=datetime.utcnow(),
        )
        db.add(item)
        db.flush()
        append_case_ids(item, case_ids, db)
        db.commit()
        return summary(item, db)
    except IntegrityError as error:
        db.rollback()
        existing = existing_result()
        if existing:
            return summary(existing, db)
        if db.bind.dialect.name == "mssql" and "CK_CaseSet_Source" in str(error.orig):
            raise HTTPException(503, CART_SCHEMA_ERROR) from error
        raise
    except Exception:
        db.rollback()
        raise


def add_cases(set_id, owner_id, payload, db, solr):
    try:
        item = owned(set_id, owner_id, db, lock=True)
        require_review(item)
        case_ids = list(dict.fromkeys(payload.caseIds))
        existing = {
            case_id
            for (case_id,) in db.query(CaseSetCase.CaseId)
            .filter(CaseSetCase.CaseSetId == set_id, CaseSetCase.CaseId.in_(case_ids))
            .all()
        }
        additions = [case_id for case_id in case_ids if case_id not in existing]
        validate_cart_cases(additions, solr)
        if additions:
            append_case_ids(item, additions, db)
            item.Revision += 1
            item.UpdatedAt = datetime.utcnow()
            db.flush()
        result = {
            "set": summary(item, db),
            "added": len(additions),
            "alreadyPresent": len(existing),
        }
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def operation_operands(owner_id, payload, db):
    # Reviews and archive/edit also lock the parent. Always lock both in ID order
    # so reversed operands cannot deadlock and membership remains stable until commit.
    items = {
        set_id: owned(set_id, owner_id, db, lock=True)
        for set_id in sorted({payload.leftSetId, payload.rightSetId})
    }
    for item in items.values():
        if item.Archived or item.CaptureState != "READY":
            raise HTTPException(
                409,
                "Choose completed, active case sets before performing an operation.",
            )
    return items[payload.leftSetId], items[payload.rightSetId]


def operation_ids(payload):
    def ids(set_id):
        query = select(CaseSetCase.CaseId).where(CaseSetCase.CaseSetId == set_id)
        return query.where(
            CaseSetCase.ReviewState == "INCLUDED"
            if payload.membership == "INCLUDED_ONLY"
            else CaseSetCase.ReviewState != "EXCLUDED"
        )

    left, right = ids(payload.leftSetId), ids(payload.rightSetId)
    if payload.operation == "UNION":
        result = left.union(right)
    elif payload.operation == "INTERSECTION":
        result = left.intersect(right)
    elif payload.operation == "DIFFERENCE":
        result = left.except_(right)
    else:
        # Derived tables keep nested set expressions portable to SQL Server/SQLite.
        either = left.union(right).subquery()
        both = left.intersect(right).subquery()
        result = select(either.c.CaseId).except_(select(both.c.CaseId))
    return result.subquery()


def operand_summary(item, membership, db):
    totals = counts(item.CaseSetId, db)
    return {
        "id": item.CaseSetId,
        "name": item.Name,
        "revision": item.Revision,
        "eligible": totals["included"]
        + (totals["unreviewed"] if membership == "NOT_EXCLUDED" else 0),
        **totals,
    }


def preview_operation(owner_id, payload, db):
    require_operations_schema(db)
    try:
        left, right = operation_operands(owner_id, payload, db)
        result = {
            "left": operand_summary(left, payload.membership, db),
            "right": operand_summary(right, payload.membership, db),
            "operation": payload.operation,
            "membership": payload.membership,
            "total": db.execute(
                select(func.count()).select_from(operation_ids(payload))
            ).scalar_one(),
        }
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def create_operation(owner_id, payload, db):
    require_operations_schema(db)
    creation_key = str(payload.operationId)
    fingerprint = hashlib.sha256(
        payload.json(exclude={"operationId"}, sort_keys=True).encode()
    ).hexdigest()

    def existing_result():
        existing = (
            db.query(CaseSet)
            .filter(CaseSet.OwnerId == owner_id, CaseSet.CreationKey == creation_key)
            .first()
        )
        if existing and existing.CreationHash != fingerprint:
            raise HTTPException(
                409, "This creation request was already used for another set."
            )
        return existing

    try:
        existing = existing_result()
        if existing:
            return summary(existing, db)
        left, right = operation_operands(owner_id, payload, db)
        # Another identical request may have finished while waiting for these locks.
        existing = existing_result()
        if existing:
            return summary(existing, db)
        if (
            left.Revision != payload.leftRevision
            or right.Revision != payload.rightRevision
        ):
            raise HTTPException(
                409,
                "A source set changed since the preview. Preview the operation again before saving.",
            )
        provenance = {
            "operation": payload.operation,
            "membership": payload.membership,
            "left": operand_summary(left, payload.membership, db),
            "right": operand_summary(right, payload.membership, db),
        }
        item = CaseSet(
            OwnerId=owner_id,
            Name=payload.name,
            Description=payload.description,
            SourceType="OPERATION",
            SourceId=left.CaseSetId,
            SourceName=f"{OPERATION_LABELS[payload.operation]}: {left.Name}; {right.Name}",
            SourceQuery=json.dumps(provenance),
            CreationKey=creation_key,
            CreationHash=fingerprint,
            CaptureState="READY",
            CaptureFinishedAt=datetime.utcnow(),
        )
        db.add(item)
        db.flush()
        result_ids = operation_ids(payload)
        db.execute(
            insert(CaseSetCase).from_select(
                ["CaseSetId", "CaseId", "Ordinal", "ReviewState", "Revision"],
                select(
                    literal(item.CaseSetId),
                    result_ids.c.CaseId,
                    func.row_number().over(order_by=result_ids.c.CaseId),
                    literal("UNREVIEWED"),
                    literal(0),
                ),
            )
        )
        item.CaptureExpected = counts(item.CaseSetId, db)["total"]
        item.CaptureSeen = item.CaptureExpected
        db.commit()
        return summary(item, db)
    except IntegrityError as error:
        db.rollback()
        existing = existing_result()
        if existing:
            return summary(existing, db)
        if db.bind.dialect.name == "mssql" and "CK_CaseSet_Source" in str(error.orig):
            # The API account may not be allowed to inspect the old constraint.
            # Report a confirmed schema mismatch without leaving a partial set.
            raise HTTPException(503, OPERATIONS_SCHEMA_ERROR) from error
        raise
    except Exception:
        db.rollback()
        raise


def capture(set_id, owner_id, cursor, db, solr):
    item = owned(set_id, owner_id, db, lock=True)
    if item.Archived:
        raise HTTPException(409, "Restore this set before continuing capture.")
    if item.CaptureState == "READY" or item.CaptureCursor != cursor:
        return summary(item, db)
    try:
        snapshot = json.loads(item.SourceQuery)
        results = solr.search(
            snapshot["query"],
            fl="id,caseid",
            sort="caseid asc,id asc",
            cursorMark=cursor,
            rows=CAPTURE_BATCH,
            NOW=snapshot["now"],
        )
        next_cursor = results.raw_response.get("nextCursorMark")
        if not next_cursor or results.raw_response.get("responseHeader", {}).get(
            "partialResults"
        ):
            raise ValueError("Incomplete search response")
        docs = list(results)
        ids = [int(doc["caseid"]) for doc in docs]
        if any(case_id <= 0 for case_id in ids):
            raise ValueError("Invalid case identifier")
        seen = item.CaptureSeen + len(docs)
        if item.CaptureExpected is not None and results.hits != item.CaptureExpected:
            raise ValueError("Search results changed during capture")
        if next_cursor == cursor and (docs or seen != results.hits):
            raise ValueError("Search capture ended before all results were received")
        existing_ids = {
            r[0]
            for r in db.query(CaseSetCase.CaseId)
            .filter(CaseSetCase.CaseSetId == set_id, CaseSetCase.CaseId.in_(ids))
            .all()
        }
        ordinal = (
            db.query(func.max(CaseSetCase.Ordinal))
            .filter(CaseSetCase.CaseSetId == set_id)
            .scalar()
            or 0
        )
        additions = []
        for case_id in ids:
            if case_id not in existing_ids:
                ordinal += 1
                additions.append(
                    {"CaseSetId": set_id, "CaseId": case_id, "Ordinal": ordinal}
                )
                existing_ids.add(case_id)
        if additions:
            db.execute(insert(CaseSetCase), additions)
        item.CaptureExpected = results.hits
        item.CaptureSeen = seen
        item.CaptureCursor = next_cursor
        item.CaptureError = ""
        item.CaptureState = "READY" if next_cursor == cursor else "CAPTURING"
        item.UpdatedAt = datetime.utcnow()
        if item.CaptureState == "READY":
            item.CaptureFinishedAt = datetime.utcnow()
        db.commit()
    except Exception:
        db.rollback()
        item = owned(set_id, owner_id, db, lock=True)
        # Another request may have completed this same batch while we retried.
        if item.CaptureCursor == cursor and item.CaptureState != "READY":
            item.CaptureState = "FAILED"
            item.CaptureError = "Capture could not finish. Retry, or create a new set if the search results have changed."
            db.commit()
    return summary(item, db)


def list_sets(owner_id, archived, page, size, db):
    query = db.query(CaseSet).filter(
        CaseSet.OwnerId == owner_id, CaseSet.Archived == archived
    )
    return {
        "items": [
            summary(item, db)
            for item in query.order_by(CaseSet.CaseSetId.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        ],
        "total": query.count(),
    }


def edit(set_id, owner_id, payload, db):
    item = owned(set_id, owner_id, db, lock=True)
    if item.Revision != payload.revision:
        raise HTTPException(
            409, "This set changed in another session. Reload before saving."
        )
    item.Name, item.Description, item.Archived = (
        payload.name,
        payload.description,
        payload.archived,
    )
    item.Revision += 1
    item.UpdatedAt = datetime.utcnow()
    db.commit()
    return summary(item, db)


def delete_set(set_id, owner_id, revision, db):
    try:
        item = owned(set_id, owner_id, db, lock=True)
        if item.Revision != revision:
            raise HTTPException(
                409, "This set changed in another session. Reload before deleting."
            )
        # The parent lock serializes deletion with capture, review and operations.
        # Support installations both before and after the specimen migration.
        if inspect(db.connection()).has_table(CaseSetSpecimen.__tablename__):
            db.query(CaseSetSpecimen).filter(
                CaseSetSpecimen.CaseSetId == set_id
            ).delete(synchronize_session=False)
        # Remove only this set's memberships first to satisfy the existing FK.
        db.query(CaseSetCase).filter(CaseSetCase.CaseSetId == set_id).delete(
            synchronize_session=False
        )
        db.delete(item)
        db.commit()
    except Exception:
        db.rollback()
        raise


def require_review(item):
    if item.Archived or item.CaptureState != "READY":
        raise HTTPException(
            409, "Complete capture and restore the set before reviewing cases."
        )


def decide(set_id, case_id, owner_id, payload, db):
    item = owned(set_id, owner_id, db, lock=True)
    require_review(item)
    member = db.get(CaseSetCase, (set_id, case_id), populate_existing=True)
    if member is None:
        raise HTTPException(404, "Case is not in this set.")
    if member.Revision != payload.revision:
        # A retry after a lost response can acknowledge the already-saved decision.
        if (
            member.Revision == payload.revision + 1
            and member.ReviewState == payload.state
        ):
            return {"set": summary(item, db), "member": member_summary(member)}
        raise HTTPException(
            409, "This case changed in another session. Reload before reviewing it."
        )
    member.ReviewState = payload.state
    member.ReviewedAt = None if payload.state == "UNREVIEWED" else datetime.utcnow()
    member.ReviewerId = None if payload.state == "UNREVIEWED" else owner_id
    member.Revision += 1
    item.LastCaseId = case_id
    item.Revision += 1
    item.UpdatedAt = datetime.utcnow()
    db.commit()
    return {"set": summary(item, db), "member": member_summary(member)}


def position(set_id, owner_id, payload, db):
    item = owned(set_id, owner_id, db, lock=True)
    require_review(item)
    if (
        payload.caseId is not None
        and db.get(CaseSetCase, (set_id, payload.caseId)) is None
    ):
        raise HTTPException(404, "Case is not in this set.")
    item.LastCaseId, item.ReviewFilter = payload.caseId, payload.filter
    db.commit()
    return {"caseId": item.LastCaseId, "filter": item.ReviewFilter}


def member_summary(member):
    return {
        "caseId": member.CaseId,
        "ordinal": member.Ordinal,
        "state": member.ReviewState,
        "reviewedAt": utc(member.ReviewedAt),
        "revision": member.Revision,
    }


def require_specimen_schema(db):
    schema = inspect(db.connection())
    name = CaseSetSpecimen.__tablename__
    if not schema.has_table(name) or not set(
        CaseSetSpecimen.__table__.columns.keys()
    ).issubset({c["name"] for c in schema.get_columns(name)}):
        raise HTTPException(503, SPECIMEN_SCHEMA_ERROR)


def specimen_part(number, specimen_id):
    # SpecimenNumber normally contains the accession followed by a part letter.
    # Never return the accession here, including to demo users. Unknown formats
    # keep an explicit ID label instead of assigning an invented part letter.
    match = re.search(r"(?:^|[\s.\-])([A-Za-z]+)\s*$", number or "")
    return match.group(1).upper() if match else f"Specimen {specimen_id}"


def specimen_records(set_id, case_id, db):
    active = {
        row.SpecimenId: row.SpecimenNumber
        for row in db.execute(
            select(SPECIMENS.c.SpecimenId, SPECIMENS.c.SpecimenNumber).where(
                SPECIMENS.c.CaseId == case_id, SPECIMENS.c.IsActive == 1
            )
        ).all()
    }
    selected = {
        row.SpecimenId: row
        for row in db.query(CaseSetSpecimen)
        .filter_by(CaseSetId=set_id, CaseId=case_id)
        .all()
    }
    return active, selected


def specimen_response(item, member, active, selected, db):
    choices = [
        {
            "specimenId": specimen_id,
            "part": specimen_part(
                active.get(specimen_id, saved.SpecimenNumber if saved else ""),
                specimen_id,
            ),
            "selected": specimen_id in selected,
            "available": specimen_id in active,
        }
        for specimen_id, saved in {**dict.fromkeys(active), **selected}.items()
    ]
    choices.sort(
        key=lambda choice: (len(choice["part"]), choice["part"], choice["specimenId"])
    )
    return {
        "specimens": choices,
        "member": member_summary(member),
        "set": summary(item, db),
    }


def specimen_member(set_id, case_id, owner_id, db):
    item = owned(set_id, owner_id, db, lock=True)
    require_review(item)
    member = db.get(CaseSetCase, (set_id, case_id), populate_existing=True)
    if member is None:
        raise HTTPException(404, "Case is not in this set.")
    require_specimen_schema(db)
    return item, member


def specimens(set_id, case_id, owner_id, db):
    item, member = specimen_member(set_id, case_id, owner_id, db)
    active, selected = specimen_records(set_id, case_id, db)
    return specimen_response(item, member, active, selected, db)


def select_specimens(set_id, case_id, owner_id, payload, db):
    try:
        item, member = specimen_member(set_id, case_id, owner_id, db)
        active, selected = specimen_records(set_id, case_id, db)
        requested = set(payload.specimenIds)
        if member.Revision != payload.revision:
            if member.Revision == payload.revision + 1 and requested == set(selected):
                return specimen_response(item, member, active, selected, db)
            raise HTTPException(
                409,
                "This case changed in another session. Reload before selecting specimens.",
            )
        # Previously selected unavailable specimens may be retained or removed.
        # New selections must be active specimens belonging to this exact case.
        if requested - set(active) - set(selected):
            raise HTTPException(
                422,
                "Select only available specimens belonging to this case. Reload the specimen list.",
            )
        if requested != set(selected):
            for specimen_id in set(selected) - requested:
                db.delete(selected[specimen_id])
            now = datetime.utcnow()
            for specimen_id in requested - set(selected):
                db.add(
                    CaseSetSpecimen(
                        CaseSetId=set_id,
                        CaseId=case_id,
                        SpecimenId=specimen_id,
                        SpecimenNumber=active[specimen_id],
                        SelectedBy=owner_id,
                        SelectedAt=now,
                    )
                )
            member.Revision += 1
            item.Revision += 1
            item.UpdatedAt = now
            db.flush()
            active, selected = specimen_records(set_id, case_id, db)
        response = specimen_response(item, member, active, selected, db)
        db.commit()
        return response
    except Exception:
        db.rollback()
        raise


def case_documents(rows, role, attest, db, solr):
    documents = {}
    if rows:
        ids = " OR ".join(str(r.CaseId) for r in rows)
        try:
            results = solr.search(f"caseid:({ids})", rows=len(rows), fl="*")
            for raw in results:
                doc = read_result(raw, db)
                doc.age = doc.age or 0
                doc.hospital = doc.hospital or ""
                SecurityUtil.search(doc, role, attest)
                if SecurityUtil.is_demo_admin(role):
                    # Expanded report sections follow the case-detail masking rules.
                    for field in ("gross", "synoptic"):
                        value = getattr(doc, field, None) or ""
                        setattr(
                            doc,
                            field,
                            SecurityUtil.mask_case(SecurityUtil.mask_date(value)),
                        )
                documents[int(raw["caseid"])] = CaseSetDocumentVM.from_orm(doc).dict()
        except Exception as error:
            raise HTTPException(
                502,
                "Case summaries could not be loaded. Please retry.",
            ) from error
    return documents


def members(
    set_id, owner_id, review_filter, page, size, resume, role, attest, db, solr
):
    item = owned(set_id, owner_id, db)
    require_review(item)
    if resume:
        review_filter = item.ReviewFilter
    query = db.query(CaseSetCase).filter(CaseSetCase.CaseSetId == set_id)
    if review_filter != "ALL":
        query = query.filter(CaseSetCase.ReviewState == review_filter)
    total = query.count()
    if resume and item.LastCaseId is not None:
        last = db.get(CaseSetCase, (set_id, item.LastCaseId))
        if last:
            before = query.filter(CaseSetCase.Ordinal < last.Ordinal).count()
            page = before // size + 1
    page = max(1, min(page, (total + size - 1) // size))
    rows = (
        query.order_by(CaseSetCase.Ordinal).offset((page - 1) * size).limit(size).all()
    )
    documents = case_documents(rows, role, attest, db, solr)
    return {
        "items": [
            {
                **member_summary(r),
                "summary": documents.get(r.CaseId),
                "unavailable": r.CaseId not in documents,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "size": size,
        "filter": review_filter,
        "set": summary(item, db),
    }
