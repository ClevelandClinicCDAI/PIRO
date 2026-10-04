"""Inspect or synchronize the catalog using local Compose connection settings."""

import argparse
import os
from pathlib import Path

import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from tasks.loaders.concentriq_catalog import iter_catalog_batches
from tasks.loaders.concentriq_case_loader import ConcentriqCaseLoader
from tasks.utils.concentriq_setup import get_concentriq_db_engine, get_concentriq_case_page_size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--override", type=Path,
                        default=Path(__file__).resolve().parents[1] / "docker-compose.override.yml")
    parser.add_argument("--apply", action="store_true", help="Write the catalog to PIRO using deployed synchronization procedures")
    args = parser.parse_args()
    environment = yaml.safe_load(args.override.read_text())["services"]["api"]["environment"]
    for key, value in environment.items():
        if key.startswith(("POSTGRES_", "CONCENTRIQ_DB_", "CONCENTRIQ_CASE_")):
            os.environ[key] = str(value)
    if not args.apply:
        engine = get_concentriq_db_engine()
        try:
            count = sum(len(items) for items in iter_catalog_batches(engine, get_concentriq_case_page_size()))
            print(f"Concentriq cases with ready images: {count}. PIRO unchanged.")
        finally:
            engine.dispose()
        return

    server = environment["MSSQL_SERVER"]
    if "," in server:
        server, port = server.rsplit(",", 1)
    else:
        port = "1433"
    engine = create_engine(URL.create(
        "mssql+pymssql", username=environment["MSSQL_USER"],
        password=environment["MSSQL_PASSWORD"], host=server, port=int(port),
        database=environment["MSSQL_DB"]), hide_parameters=True)
    loader = ConcentriqCaseLoader(piro_engine=engine)
    try:
        if not loader.should_we_process_concentriq_data():
            raise ValueError("CaseDetails.Get.Enabled must be active and true in dbo.ConcentriqConfig")
        loader.get_concentriq_data()
    finally:
        loader.close_db_connection()


if __name__ == "__main__":
    main()
