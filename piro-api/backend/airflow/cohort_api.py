import json
import requests
from pathlib import Path

from logger import logger
from core.config import Settings
from airflow.general import get_certificate_path_airflow, get_airflow_api_token


def trigger_cohort_job(cohortId: int) -> bool:
    """Calls the Airflow API to execute an Airflow DAG to load Cohort
    data into Solr."""

    logger.info("trigger_cohort_job-Start")

    certPath: Path = get_certificate_path_airflow()

    load_url: str | None = Settings.AIRFLOW_DAG_COHORT_LOADER_URL

    # Derive the base URL from the full DAG trigger URL
    # e.g. https://<host>/api/v2/dags/solr_cohort_load/dagRuns
    # base_url = https://<host>
    if not load_url:
        logger.error("Unable to get Airflow load URL.")
        return False
    base_url: str = load_url.split("/api/")[0]

    token: str | None = get_airflow_api_token(base_url, str(certPath))
    if not token:
        logger.error("Unable to get an Airflow API auth token.")
        return False

    headers: dict = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    load_data: dict = {
        "logical_date": None,
        "conf": {"cohortId": f"{cohortId}"},
    }
    load_response: requests.Response = requests.post(
        load_url,
        data=json.dumps(load_data),
        headers=headers,
        verify=str(certPath),
    )

    if load_response.status_code not in (
        200,
        201,
    ):  # May return 201 on success
        logger.error("Failed to trigger an Airflow DAG via the API:")
        logger.error(f"load_response: {load_response}")
        logger.error(
            f"load_response Status: {load_response.status_code}, Reason: {load_response.reason}"  # noqa:E501
        )
        return False

    logger.info("trigger_cohort_job-End")
    return True
