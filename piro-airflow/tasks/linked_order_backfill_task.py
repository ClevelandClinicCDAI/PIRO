from airflow.sdk import task
from tasks.loaders.linked_order_backfill_loader import (
    LinkedOrderBackfillLoader,
)


@task
def linked_order_backfill_task():
    loader = LinkedOrderBackfillLoader()
    loader.load()
    loader.close_db_connections()
