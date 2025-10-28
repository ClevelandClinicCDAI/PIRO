import importlib

from core.config import settings
from dateutil.parser import parse as date_parse
from db.base_class import Base
from logger import logger
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session, selectinload

db_url = settings.DATABASE

dialect = "postgresql" if "postgres" in db_url else "sqlite"

upsert = importlib.import_module(f"sqlalchemy.dialects.{dialect}").insert


def get_results_from_query(query, session):
    results = session.execute(query)
    try:
        results = results.one_or_none()
    except MultipleResultsFound:
        results = session.execute(query)
        results = results.first()

    return results


def get_one_or_create(
    session_inst: Session,
    model: type[Base],
    create_method_kwargs: dict = None,
    select_in: bool = False,
    m2m_field: str | None = None,
    **kwargs,
):
    def _get_entry(sqlmodel, **key_args):
        stmnt = select(sqlmodel).filter_by(**key_args)
        results = get_results_from_query(query=stmnt, session=session_inst)

        if results:
            if select_in and m2m_field:
                stmnt = stmnt.options(
                    selectinload(getattr(sqlmodel, m2m_field))
                )
                results = get_results_from_query(
                    query=stmnt, session=session_inst
                )
            return results, True
        else:
            return results, False

    results, exists = _get_entry(model, **kwargs)
    if results:
        return results, exists
    else:
        kwargs.update(create_method_kwargs or {})
        created = model()
        [setattr(created, k, v) for k, v in kwargs.items()]
        session_inst.add(created)
        session_inst.commit()
        return created, False


def write_row(data_row, session_inst: Session):
    try:
        session_inst.add(data_row)
        session_inst.commit()

        return True, data_row
    except Exception as e:
        session_inst.rollback()
        logger.error(
            f"Writing data row to table failed. See error message: "
            f"{type(e), e, e.args}"
        )

        return False, None


def insert_data_rows(data_rows, session_inst: Session):
    try:
        session_inst.add_all(data_rows)
        session_inst.commit()

        return True, data_rows

    except Exception as e:
        logger.error(
            f"Writing data rows to table failed. See error message: "
            f"{type(e), e, e.args}"
        )
        logger.info(
            "Attempting to write individual entries. This can be a "
            "bit taxing, so please consider your payload to the DB"
        )

        session_inst.rollback()
        processed_rows, failed_rows = [], []
        for row in data_rows:
            success, processed_row = write_row(row, session_inst=session_inst)
            if not success:
                failed_rows.append(row)
            else:
                processed_rows.append(row)

        if processed_rows:
            status = True
        else:
            status = (False,)
        return status, {"success": processed_rows, "failed": failed_rows}


def get_row(
    id_str: str | int,
    session_inst: Session,
    model: type[Base],
    pk_field: str = "id",
):
    stmnt = select(model).where(getattr(model, pk_field) == id_str)
    results = session_inst.execute(stmnt)

    row = results.scalar_one_or_none()

    if not row:
        success = False
    else:
        success = True

    return success, row


def get_rows(
    session_inst: Session,
    model: type[Base],
    page_size: int = 100,
    page: int = 1,
    **kwargs,
):
    stmnt = select(model).offset(page - 1).limit(page_size)
    if kwargs:
        if ["date" in x for x in kwargs] and any(
            x in y for y in kwargs for x in ("lte", "gte")
        ):
            date_keys = [x for x in kwargs.keys() if "date" in x]
            for key in date_keys:
                if "lte" in key:
                    model_key = key.replace("__lte", "")
                    date_val = kwargs.pop(key)
                    if isinstance(date_val, str):
                        date_val = date_parse(date_val)
                    stmnt = stmnt.where(getattr(model, model_key) < date_val)
                elif "gte" in key:
                    model_key = key.replace("__gte", "")
                    logger.info(model_key)
                    date_val = kwargs.pop(key)
                    if isinstance(date_val, str):
                        date_val = date_parse(date_val)
                    stmnt = stmnt.where(getattr(model, model_key) > date_val)
                else:
                    date_val = kwargs.pop(key)
                    if isinstance(date_val, str):
                        date_val = date_parse(date_val)
                    stmnt = stmnt.where(getattr(model, key) == date_val)
        elif "date" in kwargs:
            date_keys = [x for x in kwargs.keys() if "date" in x]
            for key in date_keys:
                stmnt = stmnt.where(getattr(model, key) == kwargs.pop(key))
        sort_desc, sort_field = (
            kwargs.pop(x) for x in ("sort_desc", "sort_field")
        )
        if all([sort_desc, sort_field]):
            stmnt = stmnt.order_by(getattr(model, sort_field).desc())
        else:
            stmnt = stmnt.order_by(getattr(model, sort_field))
        stmnt = stmnt.filter_by(**kwargs)
    _result = session_inst.execute(stmnt)

    results = _result.all()

    logger.debug(type(results))

    success = True if len(results) > 0 else False

    return success, results


def get_rows_within_id_list(
    id_str_list: list[str | int],
    session_inst: Session,
    model: type[Base],
    pk_field: str = "id",
):
    stmnt = select(model).where(getattr(model, pk_field).in_(id_str_list))
    results = session_inst.execute(stmnt)

    if results:
        success = True
    else:
        success = False

    return success, results


def delete_row(
    id_str: str | int,
    session_inst: Session,
    model: type[Base],
    pk_field: str = "id",
):
    success = False
    stmnt = select(model).where(getattr(model, pk_field) == id_str)
    results = session_inst.execute(stmnt)

    row = results.one_or_none()

    if not row:
        pass
    else:
        try:
            session_inst.delete(row)
            session_inst.commit()
            success = True
        except Exception as e:
            logger.error(
                f"Failed to delete data row. Please see error messages here: "
                f"{type(e), e, e.args}"
            )
            session_inst.rollback()

    return success


def bulk_upsert_mappings(
    payload: list,
    session_inst: Session,
    model: type[Base],
    pk_field: str = "id",
):
    try:
        stmnt = upsert(model).values(payload)
        stmnt = stmnt.on_conflict_do_update(
            index_elements=[getattr(model, pk_field)],
            set_={k: getattr(stmnt.excluded, k) for k in payload[0].keys()},
        )
        session_inst.execute(stmnt)

        session_inst.commit()

        return True

    except Exception as e:
        logger.error(
            f"Failed to upsert values to DB. Please see error: "
            f"{type(e), e, e.args}"
        )
        return False
