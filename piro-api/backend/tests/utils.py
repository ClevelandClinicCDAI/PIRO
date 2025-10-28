import json
from datetime import date
from importlib import import_module
from itertools import repeat
from typing import Type

import polars as pd
from crud.crud import insert_data_rows
from dateutil.parser import parse as date_parse
from db.base_class import Base
from logger import logger
from sqlalchemy import engine, select
from sqlalchemy.orm import Session
from tests.consts import BASE_DIR, file_name_model_dict


def generate_rows_to_db(model_factory, batch_size: int = 25):
    """
    This function generates data from a provided factory_boy SQLAFactory
    instance and writes the results to a database's connection via a provided
    session instance. This helps to automate the data generation process to
    use randomized data and store the results in a RDBMS solution. Args:
    model_factory:
    session_obj:

    Returns: None

    """

    model_name = model_factory._meta.model.__tablename__
    session = model_factory._meta.sqlalchemy_session

    db_url = model_factory._meta.sqlalchemy_session.bind.url

    logger.info(f"Session Obj URL for {model_name} is: {db_url}")
    rows = model_factory.build_batch(batch_size)
    session.add_all(rows)
    try:
        session.commit()
        logger.info("Successfully written rows to db!")
    except Exception as e:
        logger.debug("Commit failed. See logs.")
        logger.error(f"{type(e), e, e.args}")
        session.rollback()

    # return model_factory.create_batch(batch_size)


def get_json_from_query(model: Type[Base], engine_obj: engine):
    """
    This function queries a database for a provided SQLA data model and then
    converts the payload into JSON via Pandas. This provides a performant
    data conversion solution necessary for generating data fixture files.
    Args:
        model: SQLA Data Model instance
        engine_obj: SQLA Engine

    Returns: dict

    """
    stmnt = select(model)
    with engine_obj.connect() as conn:
        df = pd.read_database(str(stmnt), conn)

    return df.to_dicts()


def create_fixture(model: Type[Base], engine_obj: engine):
    """
    The primary utility function that pulls data from the RDBMS solution set,
    converts the SQL payload into a python dictionary, and then writes the
    associated JSON contents to a .json file. The SQLA model instance will
    have it's tablename used for create the filename, and the files will be
    timestamped in the filename as well. Args: model: engine_obj:

    Args:
        model: SQLA Data Model instance
        engine_obj: SQLA engine

    Returns: None

    """
    model_name = model.__tablename__.lower()
    file_name = f"{model_name}_{date.today()}_data_fixtures.json"
    with open(file_name, "w") as f:
        f.write(
            json.dumps(
                get_json_from_query(model=model, engine_obj=engine_obj),
                indent=4,
                sort_keys=True,
                default=str,
            )
        )


def populate_tables(db: Session):
    def get_model_import(model_name: str):
        model_loc = f"db.models.{model_name}"
        imported_mod = import_module(model_loc)
        model = getattr(imported_mod, model_name)

        return model

    models = list(
        map(
            get_model_import,
            list(file_name_model_dict.values()),
        )
    )
    json_dir = BASE_DIR / "backend" / "tests" / "fixtures"
    logger.info(
        f"Files in directory: "
        f"{list(filter(lambda x: x.is_file(), json_dir.rglob('*.json')))}"
    )
    logger.info(json_dir)
    data_files = list(
        map(
            lambda x: list(json_dir.glob(f"{x}_*.json"))[0],
            list(x.lower() for x in file_name_model_dict.values()),
        )
    )

    data = list(
        map(lambda file_inst: json.loads(file_inst.open().read()), data_files)
    )
    list(map(data_to_sql, data, models, repeat(db)))


def data_to_sql(data_rows: list[dict], model: type[Base], db: Session):
    def _check_date_time(val: str):
        try:
            date_obj = date_parse(val)
            return date_obj
        except Exception:
            return val

    data_rows = list(
        map(
            lambda row: {k: _check_date_time(v) for k, v in row.items()},
            data_rows,
        )
    )
    rows = list(map(lambda row: model(**row), data_rows))

    success, rows = insert_data_rows(data_rows=rows, session_inst=db)

    logger.info(f"Status for write job of data rows: {success}")

    return rows
