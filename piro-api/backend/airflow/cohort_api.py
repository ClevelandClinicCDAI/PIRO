import json
import requests
from logger import logger
from core.config import Settings
from airflow.general import get_certificate_path_airflow


# def trigger_cohort_job(
#     cohortId: int
# ):
def trigger_cohort_job(cohortId: int) -> bool:
    """Function to call the solr data loader."""
    _authentication_header = Settings.AIRFLOW_HEADER_AUTH
    logger.info("trigger_cohort_job-Start")
    headers = {
        "Authorization": f"Basic {_authentication_header}",
        "Content-Type": "application/json",
    }
    _load_url = Settings.AIRFLOW_DAG_COHORT_LOADER_URL
    logger.info("solr_delete_url-Start")

    load_data = {"conf": {"cohortId": f"{cohortId}"}}
    logger.info(load_data)
    certPath = get_certificate_path_airflow()
    logger.info(certPath)
    load_response = requests.post(
        _load_url, data=json.dumps(load_data), headers=headers, verify=certPath
    )

    # logger.info(f"load_response: {load_response}")

    if load_response.status_code != 200:
        logger.info(f"load_response: {load_response}")
        logger.info(
            f"load_response Status: {load_response.status_code}, Reason: {load_response.reason}"
        )
        # raise Exception(f"Error in Airlow Cohort API call: {load_response.status_code}, Reason: {load_response.reason}")
        return False
    # logger.info("trigger_cohort_job-End")
    return True
